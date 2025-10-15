import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import InterviewSession, InterviewMessage
from analysis.models import AgentMemory
 

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

    chat_messages = session.messages.all().order_by("timestamp")

    if request.method == "POST" and not session.completed:
        candidate_answer = request.POST.get("answer")
        InterviewMessage.objects.create(session=session, role="candidate", content=candidate_answer)
        # Ensure session pointer in AgentMemory
        try:
            mem, _ = AgentMemory.objects.get_or_create(user=request.user)
            sessions = mem.sessions or []
            if not any(s.get('id') == str(session._id) for s in sessions):
                sessions.append({
                    'type': 'interview',
                    'id': str(session._id),
                    'started_at': str(session.created_at),
                    'ended_at': None,
                    'summary': '',
                    'score': None,
                })
                mem.sessions = sessions
                mem.save()
        except Exception:
            pass

        # Prepare conversation history
        history = [{"role": m.role, "content": m.content} for m in chat_messages]
        history.append({"role": "candidate", "content": candidate_answer})

        # Global application performance context
        try:
            from analysis.models import AgentMemory
            mem = AgentMemory.objects.get(user=request.user)
            strengths = ", ".join(mem.strengths or [])
            weaknesses = ", ".join(mem.weaknesses or [])
        except Exception:
            strengths = ""
            weaknesses = ""
        try:
            from exam.models import Exam
            past_scores = list(Exam.objects.filter(user=request.user).order_by('-created_at').values_list('score', flat=True)[:5])
        except Exception:
            past_scores = []
        system_context = (
            f"Global context — recent scores: {past_scores}; strengths: {strengths}; weaknesses: {weaknesses}. "
            f"Ask concise, specific questions only."
        )
        history.insert(0, {"role": "system", "content": system_context})

        # Check if the interview is over or if a new question is needed
        if session.current_question >= session.total_questions:
            # Finalize with deterministic summary (no server LLM)
            summary = "Thank you for completing the interview. We'll review your answers and get back to you."
            InterviewMessage.objects.create(session=session, role="interviewer", content=summary)
            session.performance_score = 0
            session.feedback_summary = summary
            session.completed = True
            # update AgentMemory session end
            try:
                mem = AgentMemory.objects.get(user=request.user)
                sessions = mem.sessions or []
                for s in sessions:
                    if s.get('id') == str(session._id):
                        s['ended_at'] = str(session.created_at)
                        s['summary'] = summary
                        s['score'] = session.performance_score
                mem.sessions = sessions
                mem.save()
            except Exception:
                pass
        else:
            # Generate a simple placeholder question (client-side Puter.js should drive real flow)
            next_q = f"Question {session.current_question + 1}: Please describe a recent challenge relevant to this role and how you solved it."
            if next_q and len(next_q) > 240:
                next_q = next_q[:237] + '...'
            InterviewMessage.objects.create(session=session, role="interviewer", content=next_q)
            session.current_question += 1

        session.save()
        return redirect("interview_chat", session_id=str(session._id))

    return render(request, "interview/chat.html", {
        "session": session,
        "chat_messages": chat_messages,
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
