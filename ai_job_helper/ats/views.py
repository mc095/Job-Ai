from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ATSForm
from .models import ATSResult
from .services import baseline_overlap_score, call_groq_analysis

@login_required
def home(request):
    context = {"result": None, "history": None, "form": ATSForm()}

    if request.method == "POST":
        form = ATSForm(request.POST)
        context["form"] = form

        if form.is_valid():
            jd = form.cleaned_data["job_description"].strip()
            rewrite = form.cleaned_data["rewrite_resume"]
            resume_text = getattr(request.user.userprofile, "resume_text", "") or ""

            if not resume_text:
                context["error"] = "No resume text found in your profile. Please paste your resume in Profile."
                return render(request, "ats/home.html", context)
            if not jd:
                context["error"] = "Please paste a job description."
                return render(request, "ats/home.html", context)

            # 1) Baseline heuristic
            base_score, missing_list = baseline_overlap_score(resume_text, jd)

            # 2) LLM refinement
            try:
                ai = call_groq_analysis(resume_text, jd, rewrite)
                # Fuse baseline & LLM score (simple average)
                final_score = int(round((base_score + (ai["llm_score"] or 0)) / 2))
                missing_keywords = ai["missing_keywords"] or ", ".join(missing_list)
                suggestions = ai["suggestions"] or "No suggestions generated."
                optimized_resume = ai["optimized_resume"] or ""
            except Exception as e:
                final_score = base_score
                missing_keywords = ", ".join(missing_list)
                suggestions = f"LLM error; showing baseline only. Error: {e}"
                optimized_resume = ""

            # 3) Persist result
            result = ATSResult.objects.create(
                user=request.user,
                job_description=jd,
                baseline_score=base_score,
                final_score=final_score,
                missing_keywords=missing_keywords,
                suggestions=suggestions,
                optimized_resume=optimized_resume
            )
            context["result"] = result

    # recent history
    context["history"] = ATSResult.objects.filter(user=request.user)[:10]
    return render(request, "ats/home.html", context)
