import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from exam.models import Exam, Question, Answer
from django.conf import settings
 

@login_required
def interview_home(request):
    """
    Text-based interview home page with form submission handling
    """
    if request.method == 'POST':
        job_description = request.POST.get('job_description', '').strip()
        
        if not job_description:
            return render(request, "interview/home.html", {
                'error': 'Job description is required'
            })
        
        # Create new interview session
        from .models import InterviewSession
        resume_text = getattr(request.user.userprofile, 'resume_text', '') or ''
        
        session = InterviewSession.objects.create(
            user=request.user,
            job_description=job_description,
            resume_text=resume_text,
            total_questions=10
        )
        
        # Redirect to chat interface
        return redirect('interview_chat', session_id=str(session._id))
    
    return render(request, "interview/home.html")


@login_required
def interview_chat(request, session_id):
    """
    Minimal chat view to satisfy routing; renders chat template.
    """
    context = {
        "session_id": session_id,
    }
    return render(request, "interview/chat.html", context)


@login_required
def exam_loading(request):
    """
    Initiates the exam generation process using AI agents.
    """
    try:
        job_role = request.session.get("job_role")
        if not job_role:
            return redirect("exam_home")

        # Build user context for personalization
        resume_text = getattr(request.user.userprofile, 'resume_text', '') or ''
        # Collect past exam scores (latest 10)
        from .models import Exam as ExamModel
        past_scores = list(ExamModel.objects.filter(user=request.user).order_by('-created_at').values_list('score', flat=True)[:10])
        # Pull preferences and strengths/weaknesses from AgentMemory (if exists)
        from analysis.models import AgentMemory
        try:
            mem = AgentMemory.objects.get(user=request.user)
            preferences = mem.preferences or {}
            strengths = mem.strengths or []
            weaknesses = mem.weaknesses or []
        except AgentMemory.DoesNotExist:
            preferences = {}
            strengths = []
            weaknesses = []
        # Avoid repeating recent questions for this role (latest 50)
        from .models import Question as QModel
        recent_qs = list(QModel.objects.filter(exam__user=request.user, exam__job_role=job_role).order_by('-_id').values_list('text', flat=True)[:50])
        user_context = {
            'resume_text': resume_text,
            'past_scores': past_scores,
            'preferences': preferences,
            'strengths': strengths,
            'weaknesses': weaknesses
        }

        # Client-side Puter.js should generate questions; server no longer calls Gemini/Groq
        questions_data = { 'questions': [] }
        
        if not questions_data or 'questions' not in questions_data or not questions_data['questions']:
            return render(request, "exam/error.html", {"message": "Exam generation now runs client-side. Please use the updated UI to generate questions with Puter.js and retry."})

        # --- Sanitize and enforce option diversity/quality ---
        import difflib

        def is_generic(text: str) -> bool:
            if not isinstance(text, str):
                return True
            t = text.strip().lower()
            return (t == '' or
                    'all of the above' in t or
                    'none of the above' in t or
                    t in {'all', 'none', 'both', 'neither'})

        def options_are_diverse(opts):
            norm = [strip_label(o or '').lower() for o in opts]
            # Unique and non-empty
            if len(set(norm)) < len(norm):
                return False
            if any(len(o) < 2 for o in norm):
                return False
            # Avoid highly similar options
            for i in range(len(norm)):
                for j in range(i+1, len(norm)):
                    if difflib.SequenceMatcher(a=norm[i], b=norm[j]).ratio() > 0.85:
                        return False
            return True

        needed = 30
        attempts = 0
        max_attempts = 3
        accumulated = []

        def extract_good_questions(payload):
            out = []
            for q in payload.get('questions', []):
                qtext = q.get('question', '')
                if is_generic(qtext):
                    continue
                opts = (q.get('options') or q.get('choices') or q.get('answers') or [])
                if not isinstance(opts, list):
                    continue
                # Ensure 4 options
                while len(opts) < 4:
                    opts.append('')
                opts = [strip_label(x or '') for x in opts[:4]]
                if any(is_generic(o) for o in opts):
                    continue
                if not options_are_diverse(opts):
                    continue
                # Valid correct answer mapping
                correct_letter = normalize_correct_letter(opts, q.get('correct_answer'))
                if correct_letter not in {'A','B','C','D'}:
                    continue
                out.append({
                    'question': qtext,
                    'options': opts,
                    'correct_letter': correct_letter,
                    'explanation': q.get('explanation', ''),
                    'topic': q.get('topic') or None
                })
            return out

        # First batch
        accumulated.extend(extract_good_questions(questions_data))

        # If not enough, fetch more with updated avoidance
        while len(accumulated) < needed and attempts < max_attempts:
            attempts += 1
            more_avoid = recent_qs + [q['question'] for q in accumulated]
            more = ai_service.generate_exam_questions_for_user(
                user_context=user_context,
                avoidance_list=more_avoid,
                job_role=job_role,
                num_questions=needed - len(accumulated),
                difficulty="medium",
            )
            if not more or 'questions' not in more:
                break
            accumulated.extend(extract_good_questions(more))
            # Deduplicate by question text
            seen = set()
            dedup = []
            for q in accumulated:
                if q['question'] in seen:
                    continue
                seen.add(q['question'])
                dedup.append(q)
            accumulated = dedup
            
        if not accumulated:
            return render(request, "exam/error.html", {"message": "Could not generate high-quality unique questions. Please try again."})

        # Create the exam and questions in the database.
        exam = Exam.objects.create(
            user=request.user,
            job_role=job_role
        )

        # Store exam ID in session for navigation
        request.session['current_exam_id'] = str(exam._id)

        # Also avoid recent global questions for this role to reduce cross-user repetition
        from .models import Question as QGlobal
        global_recent = set(list(QGlobal.objects.filter(exam__job_role=job_role)
                                 .order_by('-_id').values_list('text', flat=True)[:200]))

        import re

        def strip_label(text: str) -> str:
            if not isinstance(text, str):
                return ''
            # Remove leading labels like "A.", "(A)", "A)" and extra spaces
            return re.sub(r"^[\s\(\[]?[A-Da-d][\)\].:\-\s]+\s*", "", text).strip()

        def normalize_correct_letter(options_list, correct_value):
            letters = ['A', 'B', 'C', 'D']
            # If already a proper letter
            if isinstance(correct_value, str):
                cv = correct_value.strip().upper()
                if cv in letters:
                    return cv
            # If numeric index
            try:
                idx = int(correct_value)
                if 0 <= idx < len(options_list):
                    return letters[idx]
            except Exception:
                pass
            # Match by option text
            if isinstance(correct_value, str):
                target = strip_label(correct_value).lower()
                for i, opt in enumerate(options_list):
                    if target == strip_label(opt or '').lower():
                        return letters[i]
            # Default
            return 'A'

        saved = 0
        for question_data in accumulated[:needed]:
            # Skip globally recent duplicates
            if question_data.get('question') in global_recent:
                continue
            topic = question_data.get("topic") or None
            options = question_data.get("options") or []
            correct_letter = question_data.get("correct_letter")
            question = Question.objects.create(
                exam=exam,
                text=question_data["question"],
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_option=correct_letter,
                explanation=question_data.get("explanation", ""),
                topic=topic
            )
            saved += 1

        if saved == 0:
            return render(request, "exam/error.html", {"message": "No unique questions could be generated. Please try again."})

        # Redirect to the first question.
        return redirect("exam_test", exam_id=str(exam._id), question_num=1)

    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error generating exam: {str(e)}"})

@login_required
def exam_test(request, exam_id, question_num):
    """
    Displays a single question for the exam (assessment style - one question per page).
    Handles form submission to record the answer and show feedback.
    """
    try:
        exam = get_object_or_404(Exam, _id=ObjectId(exam_id), user=request.user)
        questions = list(Question.objects.filter(exam=exam).order_by('_id'))
        
        if not questions:
            return render(request, "exam/error.html", {"message": "No questions found for this exam"})
        
        # Get the current question (1-indexed)
        current_question = questions[question_num - 1]
        
        # Get user's answer for this question
        try:
            user_answer = Answer.objects.get(question=current_question, user=request.user)
            selected_option = user_answer.selected_option
            is_correct = user_answer.is_correct
        except Answer.DoesNotExist:
            selected_option = None
            is_correct = None
        
        # Handle form submission
        if request.method == "POST":
            action = request.POST.get("action", "answer")
            
            if action == "answer":
                selected_option = request.POST.get("answer")
                if selected_option:
                    # Create or update the answer
                    Answer.objects.update_or_create(
                        question=current_question,
                        user=request.user,
                        defaults={
                            'selected_option': selected_option,
                            'is_correct': selected_option == current_question.correct_option
                        }
                    )
                    # Refresh the answer data
                    user_answer = Answer.objects.get(question=current_question, user=request.user)
                    selected_option = user_answer.selected_option
                    is_correct = user_answer.is_correct
            
            elif action == "next":
                # Move to next question or finish exam
                if question_num < len(questions):
                    return redirect("exam_test", exam_id=exam_id, question_num=question_num + 1)
                else:
                    return redirect("exam_result")
        
        # Calculate progress
        progress = (question_num / len(questions)) * 100
        
        context = {
            'question': current_question,
            'question_num': question_num,
            'total_questions': len(questions),
            'progress': progress,
            'exam': exam,
            'exam_id': exam_id,
            'selected_option': selected_option,
            'is_correct': is_correct,
            'show_feedback': selected_option is not None
        }
        
        return render(request, "exam/test.html", context)
        
    except (IndexError, ValueError) as e:
        return render(request, "exam/error.html", {"message": f"Invalid question number: {str(e)}"})
    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error loading question: {str(e)}"})

@login_required
def exam_result(request):
    """
    Displays the exam results with detailed feedback.
    """
    try:
        exam_id = request.session.get('current_exam_id')
        if not exam_id:
            return redirect("exam_home")
        
        exam = get_object_or_404(Exam, _id=ObjectId(exam_id))
        questions = Question.objects.filter(exam=exam).order_by('_id')
        
        # Get user's answers
        user_answers = {}
        for question in questions:
            try:
                answer = Answer.objects.get(question=question, user=request.user)
                user_answers[question._id] = answer
            except Answer.DoesNotExist:
                user_answers[question._id] = None
        
        # Calculate score
        correct_answers = sum(1 for answer in user_answers.values() 
                            if answer and answer.is_correct)
        total_questions = questions.count()
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Save the score to the exam record
        exam.score = int(score_percentage)
        exam.save()
        
        # Prepare question results for template
        question_results = []
        for question in questions:
            user_answer = user_answers.get(question._id)
            question_results.append({
                'question': question,
                'selected_option': user_answer.selected_option if user_answer else None,
                'correct_option': question.correct_option,
                'is_correct': user_answer.is_correct if user_answer else False
            })
        
        context = {
            'exam': exam,
            'questions': questions,
            'user_answers': user_answers,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'score_percentage': score_percentage,
            'percentage': score_percentage,
            'correct_count': correct_answers,
            'question_results': question_results
        }
        
        return render(request, "exam/result.html", context)
        
    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error loading results: {str(e)}"})

@login_required
def start_exam(request, exam_id):
    """
    Starts a specific exam by setting it in the session.
    """
    try:
        exam = get_object_or_404(Exam, _id=ObjectId(exam_id), user=request.user)
        request.session['current_exam_id'] = str(exam._id)
        return redirect("exam_test", exam_id=str(exam._id), question_num=1)
    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error starting exam: {str(e)}"})