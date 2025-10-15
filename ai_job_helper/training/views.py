import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TrainingSession, TrainingMessage
from analysis.models import AgentMemory

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

    # Provide agent memory context to the template (ATS score, exam scores)
    latest_ats_score = None
    recent_exam_scores = []
    try:
        from ats.models import ATSResult
        latest = ATSResult.objects.filter(user=request.user).order_by('-created_at').first()
        if latest:
            latest_ats_score = int(latest.final_score)
    except Exception:
        latest_ats_score = None
    try:
        from exam.models import Exam
        recent_exam_scores = list(Exam.objects.filter(user=request.user).order_by('-created_at').values_list('score', flat=True)[:5])
    except Exception:
        recent_exam_scores = []

    if request.method == "POST":
        role = request.POST.get("role", "user").strip() or "user"
        msg = request.POST.get("message", "")
        if msg:
            TrainingMessage.objects.create(session=session, role=role, content=msg)
            # Upsert session summary pointer in AgentMemory and update per-turn summary
            mem, _ = AgentMemory.objects.get_or_create(user=request.user)
            sessions = mem.sessions or []
            # find or create this session entry
            found = False
            for s in sessions:
                if s.get('id') == str(session._id):
                    found = True
                    # short rolling summary: last user message (truncated) and total turns
                    try:
                        total_msgs = session.messages.count()
                    except Exception:
                        total_msgs = 0
                    short = msg.strip().replace('\n', ' ')
                    if len(short) > 160:
                        short = short[:157] + '...'
                    s['summary'] = f"Last: {short} | Turns: {total_msgs}"
                    break
            if not found:
                sessions.append({
                    'type': 'training',
                    'id': str(session._id),
                    'started_at': str(session.created_at),
                    'ended_at': None,
                    'summary': (msg[:157] + '...') if len(msg) > 160 else msg,
                    'score': None,
                })
            # persist recent exam scores for completeness
            try:
                from exam.models import Exam
                mem.last_exam_scores = list(Exam.objects.filter(user=request.user).order_by('-created_at').values_list('score', flat=True)[:5])
            except Exception:
                pass
            mem.sessions = sessions
            mem.save()
        return redirect("training_chat", session_id=str(session._id))

    return render(request, "training/chat.html", {"session": session, "chat_messages": chat_messages, "latest_ats_score": latest_ats_score, "recent_exam_scores": recent_exam_scores})
