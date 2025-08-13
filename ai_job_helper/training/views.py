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
        # Create initial bot message
        initial_message = (
            f"Hello! I'm your AI career coach. I'll help you prepare for your job interview. "
            f"I've reviewed your resume and the job description. Would you like me to:\n\n"
            f"1. Analyze the key requirements of the position\n"
            f"2. Identify areas where your experience matches well\n"
            f"3. Suggest skills you might want to develop\n"
            f"4. Practice interview questions\n\n"
            f"What would you like to focus on first?"
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
    
    messages = session.messages.all().order_by("timestamp")

    if request.method == "POST":
        user_msg = request.POST.get("message")
        TrainingMessage.objects.create(session=session, role="user", content=user_msg)

        # Prepare conversation history
        history = [{"role": m.role, "content": m.content} for m in messages]
        history.append({"role": "user", "content": user_msg})

        # System prompt with resume & JD
        system_prompt = (
            f"You are a career coach chatbot. The user has this resume:\n\n{session.resume_text}\n\n"
            f"And is applying for this job:\n\n{session.job_description}\n\n"
            "Train the user for the interview, teach them relevant skills, explain concepts from the JD, "
            "and give external resource links for further learning. Keep it conversational."
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

        TrainingMessage.objects.create(session=session, role="bot", content=bot_reply)

        return redirect("training_chat", session_id=str(session._id))

    return render(request, "training/chat.html", {"session": session, "messages": messages})
