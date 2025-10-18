# analysis/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
 

@login_required
def home(request):
    ai_suggestions = None
    rewritten_resume = None
    resume_text_ctx = request.user.userprofile.resume_text.strip() if getattr(request.user, 'userprofile', None) and request.user.userprofile.resume_text else ""

    if request.method == "POST":
        job_description = request.POST.get("job_description", "").strip()
        resume_text = request.user.userprofile.resume_text.strip() if request.user.userprofile.resume_text else ""

        if not resume_text:
            ai_suggestions = "❌ No resume text found in your profile. Please update your profile first."
        elif not job_description:
            ai_suggestions = "❌ Please enter a job description."
        else:
            # If client-side Puter.js included a result, show it raw
            puter_raw = request.POST.get("puter_result_analysis", "").strip()
            if puter_raw:
                ai_suggestions = puter_raw
            else:
                ai_suggestions = ""

    return render(request, "analysis/home.html", {
        "ai_suggestions": ai_suggestions,
        "rewritten_resume": rewritten_resume,
        "resume_text": resume_text_ctx,
    })
