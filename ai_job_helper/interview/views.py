import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import InterviewSession, InterviewMessage

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

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
            # Generate and save final feedback
            feedback = generate_feedback(session, history)
            InterviewMessage.objects.create(session=session, role="interviewer", content=feedback)
            
            # Parse the feedback response for score and feedback text
            try:
                parts = feedback.split("FEEDBACK:", 1)
                score_part = parts[0].strip()
                feedback_part = parts[1].strip() if len(parts) > 1 else feedback
                
                # Extract score
                score = float(score_part.replace("SCORE:", "").strip())
                
                # Save score and feedback
                session.performance_score = score
                session.feedback_summary = feedback_part
                session.completed = True
            except Exception as e:
                print(f"Error parsing feedback: {str(e)}")
                session.completed = True
                # Set default values if parsing fails
                session.performance_score = 0
                session.feedback_summary = feedback
        else:
            # Generate and save the next question
            next_q = generate_interview_question(session.resume_text, session.job_description, history)
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
    """
    Helper function to call the Gemini API and generate a single interview question.
    """
    prompt = (
        f"You are an interviewer. You have the candidate's resume:\n\n{resume}\n\n"
        f"And the job description:\n\n{jd}\n\n"
        "Ask the next interview question based on the job and resume. "
        "Be specific, one question only, no feedback yet.\n\n"
        "Conversation so far:\n"
        + "\n".join([f"{m['role']}: {m['content']}" for m in history])
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}", headers=headers, data=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.RequestException, KeyError, IndexError) as e:
        return f"Error generating question: {str(e)}"


def generate_feedback(session, history):
    """
    Helper function to call the Gemini API and generate final interview feedback with score.
    """
    prompt = (
        f"You are an interviewer. You have the candidate's resume:\n\n{session.resume_text}\n\n"
        f"And the job description:\n\n{session.job_description}\n\n"
        "Review the entire interview and provide:\n"
        "1. A performance score (0-100)\n"
        "2. Detailed feedback on technical skills, communication, experience fit\n"
        "3. Areas for improvement\n"
        "4. Overall assessment\n\n"
        "Format your response exactly as:\n"
        "SCORE: [number]\n"
        "FEEDBACK: [your detailed feedback]\n\n"
        "Here is the entire interview conversation:\n"
        + "\n".join([f"{m['role']}: {m['content']}" for m in history])
        + "\n\nNow provide a detailed evaluation of the candidate's performance, including strengths, weaknesses, and improvement tips."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}", headers=headers, data=json.dumps(payload))
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.RequestException, KeyError, IndexError) as e:
        return f"Error generating feedback: {str(e)}"
