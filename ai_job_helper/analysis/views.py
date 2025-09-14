# analysis/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ai_agents.ai_service import AIService

@login_required
def home(request):
    ai_suggestions = None
    rewritten_resume = None

    if request.method == "POST":
        job_description = request.POST.get("job_description", "").strip()
        resume_text = request.user.userprofile.resume_text.strip() if request.user.userprofile.resume_text else ""

        if not resume_text:
            ai_suggestions = "❌ No resume text found in your profile. Please update your profile first."
        elif not job_description:
            ai_suggestions = "❌ Please enter a job description."
        else:
            try:
                # Use AI service for resume analysis
                ai_service = AIService()
                analysis_result = ai_service.analyze_resume(resume_text, job_description)
                
                if analysis_result:
                    # Store the full analysis result for detailed display
                    ai_suggestions = analysis_result
                    rewritten_sections = analysis_result.get('rewritten_sections', {})
                    
                    # Combine rewritten sections into a full resume
                    if rewritten_sections:
                        rewritten_resume = f"""
{rewritten_sections.get('summary', '')}

EXPERIENCE:
{chr(10).join(rewritten_sections.get('experience', []))}

SKILLS:
{rewritten_sections.get('skills', '')}
"""
                else:
                    ai_suggestions = "❌ Failed to analyze resume. Please try again."
                    
            except Exception as e:
                ai_suggestions = f"❌ Error analyzing resume: {str(e)}"

    return render(request, "analysis/home.html", {
        "ai_suggestions": ai_suggestions,
        "rewritten_resume": rewritten_resume
    })
