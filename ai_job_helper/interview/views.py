import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import InterviewSession, InterviewMessage
from ai_agents.ai_service import AIService

@login_required
def interview_home(request):
    """
    Handles the interview home page, allowing a user to start a new session.
    It retrieves the user's resume and initializes a new interview session.
    """
    # Get user's resume if available
    resume_text = request.user.userprofile.resume_text.strip() if request.user.userprofile.resume_text else ""

    if request.method == "POST":
        jd = request.POST.get("job_description")
        session = InterviewSession.objects.create(
            user=request.user,
            job_description=jd,
            resume_text=resume_text
        )

        # Create initial interviewer message
        welcome_message = (
            "Hello! I will be conducting your interview today. "
            "I've reviewed your resume and the job description. "
            "I'll ask you a series of questions relevant to the position. "
            "Please take your time to provide detailed and specific answers. "
            "Are you ready to begin?"
        )
        InterviewMessage.objects.create(session=session, role="interviewer", content=welcome_message)

        # Redirect to the chat page, casting the ObjectId to a string
        return redirect("interview_chat", session_id=str(session._id))

    return render(request, "interview/home.html")


@login_required
def interview_chat(request, session_id):
    """
    Manages the interview chat interface, displaying messages and handling user responses.
    This view also triggers the LLM to generate new questions or final feedback.
    """
    try:
        session = InterviewSession.objects.get(_id=ObjectId(session_id), user=request.user)
    except (InterviewSession.DoesNotExist, ValueError):
        return render(request, "interview/error.html", {"message": "Interview session not found"})

    messages = session.messages.all().order_by("timestamp")

    if request.method == "POST" and not session.completed:
        candidate_answer = request.POST.get("answer")
        InterviewMessage.objects.create(session=session, role="candidate", content=candidate_answer)

        # Prepare conversation history
        history = [{"role": m.role, "content": m.content} for m in messages]
        history.append({"role": "candidate", "content": candidate_answer})

        # Check if the interview is over or if a new question is needed
        if session.current_question >= session.total_questions:
            # Generate and save final feedback using AI agent
            ai_service = AIService()
            feedback_data = ai_service.generate_interview_feedback(
                resume_text=session.resume_text,
                job_description=session.job_description,
                history=history,
            )
            if isinstance(feedback_data, dict):
                feedback_msg = f"SCORE: {feedback_data.get('score', 0)}\nFEEDBACK: {feedback_data.get('feedback', '')}"
                InterviewMessage.objects.create(session=session, role="interviewer", content=feedback_msg)
                session.performance_score = feedback_data.get('score', 0)
                session.feedback_summary = feedback_data.get('feedback', '')
                session.completed = True
            else:
                # Fallback behavior
                InterviewMessage.objects.create(session=session, role="interviewer", content=str(feedback_data))
                session.performance_score = 0
                session.feedback_summary = str(feedback_data)
                session.completed = True
        else:
            # Generate and save the next question using AI agent with context
            ai_service = AIService()
            next_q = ai_service.generate_next_interview_question(
                resume_text=session.resume_text,
                job_description=session.job_description,
                history=history,
                current_index=session.current_question,
                total_questions=session.total_questions,
            )
            InterviewMessage.objects.create(session=session, role="interviewer", content=next_q)
            session.current_question += 1

        session.save()
        return redirect("interview_chat", session_id=str(session._id))

    return render(request, "interview/chat.html", {
        "session": session,
        "messages": messages,
        "is_completed": session.completed
    })


def generate_interview_question(resume, jd, history):
    """Deprecated: retained for backward compatibility."""
    ai_service = AIService()
    data = ai_service.generate_interview_questions(jd)
    if data and 'questions' in data and data['questions']:
        current_q_num = len([m for m in history if m['role'] == 'interviewer']) - 1
        if 0 <= current_q_num < len(data['questions']):
            return data['questions'][current_q_num]['question']
    return "Can you tell me about a challenging project you worked on and how you overcame the obstacles?"
