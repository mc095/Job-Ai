import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Answer
from django.conf import settings
from ai_agents.ai_service import AIService
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
def home(request):
    """
    Renders the home page where the user can input a job role.
    Handles form submission to start the exam generation process.
    """
    if request.method == "POST":
        job_role = request.POST.get("job_role")
        request.session["job_role"] = job_role
        return redirect("exam_loading")
    return render(request, "exam/home.html")


@login_required
def exam_loading(request):
    """Generate exam with ONE API call - 30 unique, non-repetitive questions."""
    try:
        job_role = request.session.get("job_role")
        if not job_role:
            return redirect("exam_home")

        # Get recent questions to avoid repetition
        recent_questions = list(
            Question.objects.filter(
                exam__user=request.user,
                exam__job_role=job_role
            ).order_by('-_id').values_list('text', flat=True)[:50]
        )

        # ONE API call to generate 30 unique questions
        ai_service = AIService()
        data = ai_service.generate_exam_questions_for_user(
            user_context={},
            avoidance_list=recent_questions,
            job_role=job_role,
            num_questions=30,
            difficulty="medium",
        )
        
        questions = data.get('questions', [])
        if len(questions) < 20:
            return render(request, "exam/error.html", {"message": "Failed to generate enough exam questions. Please try again."})

        # Create exam
        exam = Exam.objects.create(user=request.user, job_role=job_role)
        request.session['current_exam_id'] = str(exam._id)

        # Save questions to database (up to 30)
        for q in questions[:30]:
            opts = q.get("options", ["","","",""])
            while len(opts) < 4:
                opts.append("")
            
            correct = q.get("correct_answer", "A")
            if isinstance(correct, int):
                correct = ['A','B','C','D'][correct] if 0 <= correct < 4 else 'A'
            else:
                correct = str(correct)[0].upper() if correct else 'A'

            Question.objects.create(
                exam=exam,
                text=q.get("question", ""),
                option_a=str(opts[0]),
                option_b=str(opts[1]),
                option_c=str(opts[2]),
                option_d=str(opts[3]),
                correct_option=correct,
                explanation=q.get("explanation", ""),
                topic=q.get("topic", job_role)
            )

        return redirect("exam_test", exam_id=str(exam._id), question_num=1)

    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error: {str(e)}"})

@login_required
@require_POST
def import_exam(request):
    """Accept client-generated questions JSON and create an exam.

    Expected JSON body:
    { "job_role": str, "questions": [ {question, options[4], correct_answer (A-D or text), explanation, topic} ] }
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    job_role = (data.get("job_role") or "").strip()
    items = data.get("questions") or []
    if not job_role or not isinstance(items, list):
        return JsonResponse({"ok": False, "error": "Missing job_role or questions"}, status=400)

    # Deduplicate and validate up to 30, fallback to 20
    seen = set()
    valid = []
    for q in items:
        qtext = (q.get("question") or "").strip()
        if not qtext:
            continue
        key = qtext.lower()
        if key in seen:
            continue
        options = q.get("options") or []
        if not isinstance(options, list):
            options = []
        while len(options) < 4:
            options.append("")
        options = [str(o or "") for o in options[:4]]
        corr = q.get("correct_answer")
        mapping = {0:'A',1:'B',2:'C',3:'D'}
        if isinstance(corr, int) and corr in mapping:
            correct_letter = mapping[corr]
        elif isinstance(corr, str):
            up = corr.strip().upper()
            if up in {'A','B','C','D'}:
                correct_letter = up
            else:
                match_idx = next((i for i, opt in enumerate(options) if opt.strip().lower() == corr.strip().lower()), 0)
                correct_letter = mapping.get(match_idx, 'A')
        else:
            correct_letter = 'A'
        valid.append({
            "question": qtext,
            "options": options,
            "correct": correct_letter,
            "explanation": q.get("explanation", ""),
            "topic": (q.get("topic") or None)
        })
        seen.add(key)

    target = 30 if len(valid) >= 30 else (20 if len(valid) >= 20 else 0)
    if target == 0:
        return JsonResponse({"ok": False, "error": "Insufficient unique questions"}, status=400)

    # Create exam and persist
    exam = Exam.objects.create(user=request.user, job_role=job_role)
    for q in valid[:target]:
        Question.objects.create(
            exam=exam,
            text=q["question"],
            option_a=q["options"][0],
            option_b=q["options"][1],
            option_c=q["options"][2],
            option_d=q["options"][3],
            correct_option=q["correct"],
            explanation=q.get("explanation", ""),
            topic=q.get("topic")
        )

    request.session['current_exam_id'] = str(exam._id)
    return JsonResponse({"ok": True, "redirect": 
        request.build_absolute_uri(
            redirect("exam_test", exam_id=str(exam._id), question_num=1).url
        )
    })

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
            'show_feedback': selected_option is not None,
            'explanation': current_question.explanation,  # Pass explanation for display
            'correct_option': current_question.correct_option
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
        return redirect("exam_test", question_num=1)
    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error starting exam: {str(e)}"})