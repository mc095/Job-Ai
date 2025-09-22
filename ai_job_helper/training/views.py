import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import TrainingSession, TrainingMessage

@login_required
def training_home(request):
    resume_text = request.user.userprofile.resume_text.strip() if request.user.userprofile.resume_text else ""

    if request.method == "POST":
        jd = request.POST.get("job_description")
        session = TrainingSession.objects.create(
            user=request.user,
            job_description=jd,
            resume_text=resume_text
        )
        # Create initial interviewer message
        initial_message = (
            "I'm the Interviewer. I reviewed your resume and the job description. "
            "We can start with: \n\n"
            "1) A quick review of key role requirements\n"
            "2) Mapping your experience to the JD\n"
            "3) Practice interview questions (technical/behavioral)\n\n"
            "Where would you like to begin?"
        )
        TrainingMessage.objects.create(session=session, role="bot", content=initial_message)
        return redirect("training_chat", session_id=str(session._id))

    return render(request, "training/home.html", {"resume": resume_text})


@login_required
def training_chat(request, session_id):
    try:
        session = TrainingSession.objects.get(_id=ObjectId(session_id), user=request.user)
    except (TrainingSession.DoesNotExist, ValueError):
        return render(request, "training/error.html", {"message": "Training session not found"})
    
    chat_messages = session.messages.all().order_by("timestamp")

    if request.method == "POST":
        user_msg = request.POST.get("message")
        TrainingMessage.objects.create(session=session, role="user", content=user_msg)

        # Prepare conversation history
        history = [{"role": m.role, "content": m.content} for m in chat_messages]
        history.append({"role": "user", "content": user_msg})

        # Global performance context and concise coaching
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

        # System prompt with resume & JD and global memory
        system_prompt = (
            f"You are an Interviewer coach. Be concise (<= 4 short sentences). Use bullets when helpful.\n\n"
            f"Global performance: scores {past_scores}; strengths: {strengths}; weaknesses: {weaknesses}.\n\n"
            f"Resume:\n{session.resume_text}\n\n"
            f"Job Description:\n{session.job_description}\n\n"
            f"Respond to the latest user message with targeted, actionable guidance."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": system_prompt + "\n\nConversation history:\n" +
                                    "\n".join([f"{m['role']}: {m['content']}" for m in history])
                        }
                    ]
                }
            ]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        data = r.json()

        bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
        if isinstance(bot_reply, str) and len(bot_reply) > 600:
            bot_reply = bot_reply[:597] + "..."

        TrainingMessage.objects.create(session=session, role="bot", content=bot_reply)

        return redirect("training_chat", session_id=str(session._id))

    return render(request, "training/chat.html", {"session": session, "chat_messages": chat_messages})
