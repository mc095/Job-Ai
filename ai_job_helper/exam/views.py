import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Answer
from django.conf import settings
from ai_agents.ai_service import AIService

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

        # Use AI service to generate personalized, non-repeating questions
        ai_service = AIService()
        questions_data = ai_service.generate_exam_questions_for_user(
            user_context=user_context,
            avoidance_list=recent_qs,
            job_role=job_role,
            num_questions=10,
            difficulty="mixed",
        )
        
        if not questions_data or 'questions' not in questions_data:
            return render(request, "exam/error.html", {"message": "Failed to generate exam questions"})

        # Create the exam and questions in the database.
        exam = Exam.objects.create(
            user=request.user,
            job_role=job_role
        )

        # Store exam ID in session for navigation
        request.session['current_exam_id'] = str(exam._id)

        for question_data in questions_data['questions']:
            topic = question_data.get("topic") or None
            question = Question.objects.create(
                exam=exam,
                text=question_data["question"],
                option_a=question_data["options"][0] if len(question_data["options"]) > 0 else "",
                option_b=question_data["options"][1] if len(question_data["options"]) > 1 else "",
                option_c=question_data["options"][2] if len(question_data["options"]) > 2 else "",
                option_d=question_data["options"][3] if len(question_data["options"]) > 3 else "",
                correct_option=question_data["correct_answer"],
                explanation=question_data.get("explanation", ""),
                topic=topic
            )

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
        return redirect("exam_test", question_num=1)
    except Exception as e:
        return render(request, "exam/error.html", {"message": f"Error starting exam: {str(e)}"})