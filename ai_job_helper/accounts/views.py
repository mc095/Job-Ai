from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserProfileForm

# Import models
from exam.models import Exam
from ats.models import ATSResult
from analysis.models import AnalysisResult


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def home(request):
    user = request.user

    # Default stats
    stats = {
        "exam_score": "N/A",
        "ats_score": "N/A",
        "resume_score": "N/A",
    }

    # Exam score
    try:
        latest_exam = Exam.objects.filter(user=user).order_by('-created_at').first()
        if latest_exam and latest_exam.score is not None:
            stats["exam_score"] = str(latest_exam.score)  # raw score
    except Exception as e:
        print("Error fetching exam score:", e)

    # ATS score
    try:
        latest_ats = ATSResult.objects.filter(user=user).order_by('-created_at').first()
        if latest_ats and latest_ats.final_score is not None:
            stats["ats_score"] = f"{latest_ats.final_score:.1f}%"
    except Exception as e:
        print("Error fetching ATS score:", e)

    # Resume analysis score
    try:
        latest_analysis = AnalysisResult.objects.filter(user=user).order_by('-created_at').first()
        if latest_analysis and latest_analysis.score is not None:
            stats["resume_score"] = f"{latest_analysis.score:.1f}%"
    except Exception as e:
        print("Error fetching resume score:", e)

    services = [
        {"name": "Resume Builder", "url": "resume_home", "icon": "📄"},
        {"name": "Job Analysis", "url": "analysis_home", "icon": "📊"},
        {"name": "ATS Optimizer", "url": "ats_home", "icon": "⚡"},
        {"name": "Exam Prep", "url": "exam_home", "icon": "📝"},
        {"name": "Training", "url": "training_home", "icon": "📚"},
    ]

    return render(request, "home.html", {"services": services, "stats": stats})


@login_required
def profile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form})
