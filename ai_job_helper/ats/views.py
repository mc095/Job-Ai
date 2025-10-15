from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import re
from .forms import ATSForm
from .models import ATSResult
from .services import real_ats_analysis, baseline_overlap_score
from analysis.models import AgentMemory

@login_required
def home(request):
    context = {"result": None, "history": None, "form": ATSForm()}

    # Expose resume_text for client-side scoring (Puter.js)
    try:
        resume_text_ctx = getattr(request.user.userprofile, "resume_text", "") or ""
    except Exception:
        resume_text_ctx = ""
    context["resume_text"] = resume_text_ctx

    if request.method == "POST":
        form = ATSForm(request.POST)
        context["form"] = form

        if form.is_valid():
            jd = form.cleaned_data["job_description"].strip()
            rewrite = form.cleaned_data["rewrite_resume"]
            resume_text = getattr(request.user.userprofile, "resume_text", "") or ""

            # keep in context for template JS usage
            context["resume_text"] = resume_text

            if not resume_text:
                context["error"] = "No resume text found in your profile. Please paste your resume in Profile."
                return render(request, "ats/home.html", context)
            if not jd:
                context["error"] = "Please paste a job description."
                return render(request, "ats/home.html", context)

            # 1) REAL ATS Analysis (baseline)
            real_analysis = real_ats_analysis(resume_text, jd)

            # 2) If client-side Puter.js result provided, parse and use it
            puter_raw = request.POST.get("puter_result", "").strip()
            llm_score = None
            parsed_missing = None
            parsed_suggestions = None
            parsed_optimized_resume = None
            if puter_raw:
                m = re.search(r"###\s*ATS\s*Score:\s*(\d{1,3})", puter_raw, flags=re.I)
                if m:
                    llm_score = max(0, min(100, int(m.group(1))))
                m = re.search(r"###\s*Missing\s*Keywords:\s*(.+?)(?:\n###|\Z)", puter_raw, flags=re.I | re.S)
                if m:
                    parsed_missing = m.group(1).strip()
                m = re.search(r"###\s*Suggestions:\s*(.+?)(?:\n###|\Z)", puter_raw, flags=re.I | re.S)
                if m:
                    parsed_suggestions = m.group(1).strip()
                m = re.search(r"###\s*Optimized\s*Resume(?:\s*\(.*?\))?:\s*(.+)\Z", puter_raw, flags=re.I | re.S)
                if m:
                    parsed_optimized_resume = m.group(1).strip()

            # 3) Build final values preferring Puter.js when present
            final_score = llm_score if llm_score is not None else real_analysis['final_score']
            missing_keywords = parsed_missing if parsed_missing is not None else ", ".join(real_analysis['missing_keywords'])
            suggestions = parsed_suggestions if parsed_suggestions is not None else generate_comprehensive_suggestions(real_analysis)
            optimized_resume = parsed_optimized_resume if parsed_optimized_resume is not None else ""

            # 4) No Gemini/Groq enrichment; rely on Puter.js or comprehensive real analysis only

            # 5) Persist result
            result = ATSResult.objects.create(
                user=request.user,
                job_description=jd,
                baseline_score=real_analysis['keyword_score'],  # Use keyword score as baseline
                final_score=final_score,
                missing_keywords=missing_keywords,
                suggestions=suggestions,
                optimized_resume=optimized_resume
            )
            context["result"] = result
            context["real_analysis"] = real_analysis  # Pass detailed analysis to template

            # Update AgentMemory with last ATS score
            try:
                mem, _ = AgentMemory.objects.get_or_create(user=request.user)
                mem.last_ats_score = final_score
                mem.save()
            except Exception:
                pass

    # recent history
    context["history"] = ATSResult.objects.filter(user=request.user)[:10]
    return render(request, "ats/home.html", context)

def generate_detailed_suggestions(real_analysis, ai_result):
    """Generate detailed suggestions combining real analysis with AI insights"""
    suggestions = []
    
    # Add comprehensive score-based suggestions with detailed explanations
    if real_analysis['keyword_score'] < 70:
        missing_keywords = real_analysis['missing_keywords'][:5]
        suggestions.append(f"🔑 CRITICAL KEYWORD OPTIMIZATION: Your keyword matching score is {real_analysis['keyword_score']}%, which is below the 70% threshold that most ATS systems require. To increase your chances of passing ATS screening, strategically incorporate these missing keywords: {', '.join(missing_keywords)}. Place them naturally in your experience descriptions, skills section, and summary. For example, if 'Python' is missing, add it to your technical skills and mention specific Python projects in your experience.")
    
    if real_analysis['section_score'] < 80:
        missing_sections = [section for section, present in real_analysis['sections_analysis'].items() if not present]
        if missing_sections:
            suggestions.append(f"📋 ESSENTIAL SECTIONS MISSING: Your resume is missing {', '.join(missing_sections)} section(s), which reduces your ATS compatibility score to {real_analysis['section_score']}%. ATS systems expect standard resume sections. Add a {missing_sections[0]} section with relevant content. For example, if 'projects' is missing, create a 'Projects' section highlighting 2-3 relevant projects with technologies used and results achieved.")
    
    if real_analysis['format_score'] < 70:
        suggestions.append(f"📄 FORMAT OPTIMIZATION NEEDED: Your format score is {real_analysis['format_score']}%. To improve ATS compatibility: 1) Add quantified achievements with numbers and percentages (e.g., 'Increased performance by 40%'), 2) Use strong action verbs (Developed, Implemented, Led, Optimized), 3) Ensure proper formatting with clear section headers, 4) Include a professional email address. These elements help ATS systems better parse and rank your resume.")
    
    if real_analysis['experience_score'] < 70:
        suggestions.append(f"💼 EXPERIENCE RELEVANCE: Your experience relevance score is {real_analysis['experience_score']}%. To improve: 1) Tailor your experience descriptions to match the job requirements, 2) Include industry-specific terminology from the job description, 3) Highlight relevant technologies and methodologies, 4) Quantify your achievements with specific metrics and results.")
    
    # Add AI-generated section-specific suggestions
    if ai_result.get('ats_improvements'):
        for section, improvements in ai_result['ats_improvements'].items():
            if improvements.get('suggestions'):
                suggestions.append(f"💡 {section.upper()} SECTION OPTIMIZATION: {improvements['suggestions']}")
    
    # Add overall strategy suggestions
    if real_analysis['final_score'] < 80:
        suggestions.append(f"🎯 OVERALL STRATEGY: Your current ATS score is {real_analysis['final_score']}%. To increase your chances of getting past ATS screening: 1) Prioritize adding missing keywords naturally throughout your resume, 2) Ensure all standard sections are present and well-formatted, 3) Include quantified achievements in your experience, 4) Use industry-standard terminology and action verbs, 5) Consider adding a projects section if you have relevant work to showcase.")
    
    return " | ".join(suggestions) if suggestions else "🎉 EXCELLENT ATS COMPATIBILITY: Your resume shows strong ATS compatibility with a score of {real_analysis['final_score']}%! Continue to refine by adding more quantified achievements and staying current with industry keywords."

def generate_comprehensive_suggestions(real_analysis):
    """Generate comprehensive suggestions based on real analysis"""
    suggestions = []
    
    # 1. CRITICAL KEYWORD OPTIMIZATION
    if real_analysis['keyword_score'] < 70:
        missing_keywords = real_analysis['missing_keywords'][:5]
        suggestions.append(f"🔑 CRITICAL KEYWORD OPTIMIZATION: Your keyword matching score is {real_analysis['keyword_score']}%, which is below the 70% threshold that most ATS systems require. To increase your chances of passing ATS screening, strategically incorporate these missing keywords: {', '.join(missing_keywords)}. Place them naturally in your experience descriptions, skills section, and summary. For example, if 'Python' is missing, add it to your technical skills and mention specific Python projects in your experience.")
    
    # 2. ESSENTIAL SECTIONS MISSING
    if real_analysis['section_score'] < 80:
        missing_sections = [section for section, present in real_analysis['sections_analysis'].items() if not present]
        if missing_sections:
            suggestions.append(f"📋 ESSENTIAL SECTIONS MISSING: Your resume is missing {', '.join(missing_sections)} section(s), which reduces your ATS compatibility score to {real_analysis['section_score']}%. ATS systems expect standard resume sections. Add a {missing_sections[0]} section with relevant content. For example, if 'projects' is missing, create a 'Projects' section highlighting 2-3 relevant projects with technologies used and results achieved.")
    
    # 3. FORMAT OPTIMIZATION NEEDED
    if real_analysis['format_score'] < 70:
        suggestions.append(f"📄 FORMAT OPTIMIZATION NEEDED: Your format score is {real_analysis['format_score']}%. To improve ATS compatibility: 1) Add quantified achievements with numbers and percentages (e.g., 'Increased performance by 40%'), 2) Use strong action verbs (Developed, Implemented, Led, Optimized), 3) Ensure proper formatting with clear section headers, 4) Include a professional email address. These elements help ATS systems better parse and rank your resume.")
    
    # 4. EXPERIENCE RELEVANCE
    if real_analysis['experience_score'] < 70:
        suggestions.append(f"💼 EXPERIENCE RELEVANCE: Your experience relevance score is {real_analysis['experience_score']}%. To improve: 1) Tailor your experience descriptions to match the job requirements, 2) Include industry-specific terminology from the job description, 3) Highlight relevant technologies and methodologies, 4) Quantify your achievements with specific metrics and results.")
    
    # 5. DETAILED KEYWORD STRATEGY
    if real_analysis['keyword_score'] < 80:
        suggestions.append(f"🎯 ADVANCED KEYWORD STRATEGY: Your keyword score is {real_analysis['keyword_score']}%. To maximize ATS compatibility: 1) Use exact keyword variations from the job description, 2) Include both technical skills (Python, React, SQL) and soft skills (Leadership, Communication), 3) Place keywords in multiple sections (summary, experience, skills), 4) Use industry-standard terminology and acronyms, 5) Include both full terms and abbreviations (e.g., 'Machine Learning' and 'ML')")
    
    # 6. QUANTIFIED ACHIEVEMENTS STRATEGY
    suggestions.append(f"📊 QUANTIFIED ACHIEVEMENTS STRATEGY: To boost your ATS score, add specific metrics throughout your resume: 1) Use numbers and percentages (e.g., 'Increased sales by 25%', 'Managed team of 8 developers'), 2) Include time-based achievements (e.g., 'Reduced processing time by 50% in 6 months'), 3) Add financial impact (e.g., 'Saved company $50K annually'), 4) Mention scale and scope (e.g., 'Led project serving 10,000+ users'), 5) Include specific technologies and tools used")
    
    # 7. ATS-FRIENDLY FORMATTING
    suggestions.append(f"📝 ATS-FRIENDLY FORMATTING: Ensure your resume passes ATS parsing: 1) Use standard section headers (EXPERIENCE, EDUCATION, SKILLS, PROJECTS), 2) Avoid graphics, tables, or complex formatting, 3) Use simple bullet points and clear fonts, 4) Include contact information at the top, 5) Save as .docx or .pdf format, 6) Use consistent date formats (MM/YYYY), 7) Avoid headers and footers")
    
    # 8. INDUSTRY-SPECIFIC OPTIMIZATION
    suggestions.append(f"🏭 INDUSTRY-SPECIFIC OPTIMIZATION: Tailor your resume for your target industry: 1) Research common keywords in your field, 2) Include relevant certifications and licenses, 3) Highlight industry-specific tools and technologies, 4) Use terminology that recruiters in your field expect, 5) Include relevant projects and achievements, 6) Mention industry standards and best practices you follow")
    
    # 9. EXPERIENCE SECTION ENHANCEMENT
    suggestions.append(f"💼 EXPERIENCE SECTION ENHANCEMENT: Make your experience stand out: 1) Start each bullet point with a strong action verb, 2) Focus on achievements rather than duties, 3) Use the STAR method (Situation, Task, Action, Result), 4) Include specific technologies and tools used, 5) Show progression and growth in your roles, 6) Quantify your impact with numbers and metrics")
    
    # 10. SKILLS SECTION OPTIMIZATION
    suggestions.append(f"🛠️ SKILLS SECTION OPTIMIZATION: Optimize your skills section for ATS: 1) Include both technical and soft skills, 2) Use exact keywords from the job description, 3) Organize skills by category (Technical Skills, Soft Skills, Tools), 4) Include proficiency levels when relevant, 5) Add industry-specific certifications, 6) Keep the list current and relevant")
    
    # 11. PROJECTS SECTION STRATEGY
    suggestions.append(f"🚀 PROJECTS SECTION STRATEGY: Showcase your work effectively: 1) Include 2-3 most relevant projects, 2) Describe the problem you solved and your solution, 3) Mention technologies, tools, and methodologies used, 4) Include quantifiable results and impact, 5) Add links to live demos or GitHub repositories, 6) Highlight projects that match the job requirements")
    
    # 12. OVERALL STRATEGY
    if real_analysis['final_score'] < 80:
        suggestions.append(f"🎯 OVERALL STRATEGY: Your current ATS score is {real_analysis['final_score']}%. To increase your chances of getting past ATS screening: 1) Prioritize adding missing keywords naturally throughout your resume, 2) Ensure all standard sections are present and well-formatted, 3) Include quantified achievements in your experience, 4) Use industry-standard terminology and action verbs, 5) Consider adding a projects section if you have relevant work to showcase, 6) Tailor your resume for each specific job application, 7) Get feedback from industry professionals")
    
    return " | ".join(suggestions) if suggestions else f"🎉 EXCELLENT ATS COMPATIBILITY: Your resume shows strong ATS compatibility with a score of {real_analysis['final_score']}%! Continue to refine by adding more quantified achievements and staying current with industry keywords."

def generate_fallback_suggestions(real_analysis):
    """Generate suggestions based on real analysis when AI fails"""
    return generate_comprehensive_suggestions(real_analysis)
