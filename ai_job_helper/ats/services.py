import re
import json
from typing import List, Tuple, Dict
from django.conf import settings
from groq import Groq

# regex for tokens incl. tech like c++, c#, .net
_WORD = re.compile(r"[A-Za-z][A-Za-z\-\+\.#\d]{1,}")

def _normalize_token(w: str) -> str:
    wl = w.lower()
    wl = wl.replace('c++', 'cpp')
    wl = wl.replace('c#', 'csharp')
    return wl

def extract_keywords(text: str) -> List[str]:
    if not text:
        return []
    return [_normalize_token(w) for w in _WORD.findall(text)]

def real_ats_analysis(resume_text: str, jd_text: str) -> Dict:
    """
    REAL ATS Analysis - not just keyword matching!
    Analyzes actual ATS compatibility factors:
    1. Keyword density and placement
    2. Section completeness
    3. Format compatibility
    4. Skills matching
    5. Experience relevance
    """
    
    # Extract meaningful keywords (not just any words)
    technical_keywords = extract_technical_keywords(jd_text)
    soft_skills = extract_soft_skills(jd_text)
    experience_keywords = extract_experience_keywords(jd_text)
    
    # Analyze resume sections
    sections = analyze_resume_sections(resume_text)
    
    # Calculate real ATS scores
    keyword_score = calculate_keyword_score(resume_text, technical_keywords, soft_skills)
    section_score = calculate_section_score(sections)
    format_score = calculate_format_score(resume_text)
    experience_score = calculate_experience_relevance(resume_text, experience_keywords)
    
    # Weighted final score (real ATS systems use similar weighting)
    final_score = int(round(
        keyword_score * 0.4 +      # 40% - Keywords (most important for ATS)
        section_score * 0.25 +     # 25% - Complete sections
        format_score * 0.2 +       # 20% - ATS-friendly format
        experience_score * 0.15    # 15% - Relevant experience
    ))
    
    # Find missing critical keywords
    missing_keywords = find_missing_critical_keywords(resume_text, technical_keywords, soft_skills)
    
    return {
        'final_score': final_score,
        'keyword_score': keyword_score,
        'section_score': section_score,
        'format_score': format_score,
        'experience_score': experience_score,
        'missing_keywords': missing_keywords,
        'sections_analysis': sections,
        'technical_keywords_found': find_matching_keywords(resume_text, technical_keywords),
        'soft_skills_found': find_matching_keywords(resume_text, soft_skills)
    }

def extract_technical_keywords(jd_text: str) -> List[str]:
    """Extract technical skills and technologies from job description"""
    technical_patterns = [
        r'\b(?:Python|Java|JavaScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin)\b',
        r'\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
        r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
        r'\b(?:HTML|CSS|SASS|LESS|Bootstrap|Tailwind|jQuery)\b',
        r'\b(?:REST|API|GraphQL|Microservices|Agile|Scrum|DevOps)\b',
        r'\b(?:Machine Learning|AI|Data Science|Analytics|Tableau|Power BI)\b',
        r'\b(?:Linux|Unix|Windows|macOS|iOS|Android)\b'
    ]
    
    keywords = set()
    for pattern in technical_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        keywords.update([match.lower() for match in matches])
    
    return list(keywords)

def extract_soft_skills(jd_text: str) -> List[str]:
    """Extract soft skills from job description"""
    soft_skill_patterns = [
        r'\b(?:leadership|teamwork|communication|problem solving|analytical|creative)\b',
        r'\b(?:collaboration|time management|project management|mentoring|training)\b',
        r'\b(?:adaptability|flexibility|initiative|attention to detail|critical thinking)\b',
        r'\b(?:presentation|negotiation|customer service|client relations|stakeholder management)\b'
    ]
    
    keywords = set()
    for pattern in soft_skill_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        keywords.update([match.lower() for match in matches])
    
    return list(keywords)

def extract_experience_keywords(jd_text: str) -> List[str]:
    """Extract experience-related keywords"""
    experience_patterns = [
        r'\b(?:years?|experience|senior|junior|lead|principal|architect|engineer|developer|analyst)\b',
        r'\b(?:startup|enterprise|fintech|healthcare|e-commerce|SaaS|B2B|B2C)\b',
        r'\b(?:remote|hybrid|onsite|full-time|part-time|contract|freelance)\b'
    ]
    
    keywords = set()
    for pattern in experience_patterns:
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        keywords.update([match.lower() for match in matches])
    
    return list(keywords)

def analyze_resume_sections(resume_text: str) -> Dict:
    """Analyze completeness of resume sections"""
    sections = {
        'header': bool(re.search(r'(?:name|email|phone|linkedin)', resume_text, re.IGNORECASE)),
        'summary': bool(re.search(r'(?:summary|objective|profile|about)', resume_text, re.IGNORECASE)),
        'experience': bool(re.search(r'(?:experience|employment|work history|professional)', resume_text, re.IGNORECASE)),
        'education': bool(re.search(r'(?:education|degree|university|college|school)', resume_text, re.IGNORECASE)),
        'skills': bool(re.search(r'(?:skills|technical|technologies|competencies)', resume_text, re.IGNORECASE)),
        'projects': bool(re.search(r'(?:projects|portfolio|achievements)', resume_text, re.IGNORECASE))
    }
    
    return sections

def calculate_keyword_score(resume_text: str, technical_keywords: List[str], soft_skills: List[str]) -> int:
    """Calculate keyword matching score (0-100)"""
    if not technical_keywords and not soft_skills:
        return 50  # Default if no keywords found
    
    resume_lower = resume_text.lower()
    total_keywords = len(technical_keywords) + len(soft_skills)
    found_keywords = 0
    
    # Check technical keywords (weighted more heavily)
    for keyword in technical_keywords:
        if keyword in resume_lower:
            found_keywords += 1.5  # Technical keywords are more important
    
    # Check soft skills
    for skill in soft_skills:
        if skill in resume_lower:
            found_keywords += 1
    
    # Calculate percentage
    if total_keywords == 0:
        return 50
    
    score = int(round((found_keywords / (len(technical_keywords) * 1.5 + len(soft_skills))) * 100))
    return min(100, max(0, score))

def calculate_section_score(sections: Dict) -> int:
    """Calculate section completeness score (0-100)"""
    required_sections = ['header', 'experience', 'education', 'skills']
    optional_sections = ['summary', 'projects']
    
    required_score = sum(1 for section in required_sections if sections.get(section, False))
    optional_score = sum(1 for section in optional_sections if sections.get(section, False))
    
    # Weight required sections more heavily
    score = int(round((required_score * 2 + optional_score) / (len(required_sections) * 2 + len(optional_sections)) * 100))
    return min(100, max(0, score))

def calculate_format_score(resume_text: str) -> int:
    """Calculate ATS-friendly format score (0-100)"""
    score = 50  # Base score
    
    # Check for ATS-friendly elements
    if re.search(r'\b\d+%|\b\d+\+|\b\d+[kK]|\$\d+', resume_text):  # Quantified achievements
        score += 15
    
    if re.search(r'\b(?:developed|implemented|created|designed|managed|led|improved|optimized)', resume_text, re.IGNORECASE):  # Action verbs
        score += 15
    
    if len(resume_text.split('\n')) > 10:  # Proper formatting with line breaks
        score += 10
    
    if re.search(r'@\w+\.\w+', resume_text):  # Professional email
        score += 10
    
    return min(100, max(0, score))

def calculate_experience_relevance(resume_text: str, experience_keywords: List[str]) -> int:
    """Calculate experience relevance score (0-100)"""
    if not experience_keywords:
        return 50
    
    resume_lower = resume_text.lower()
    found_keywords = sum(1 for keyword in experience_keywords if keyword in resume_lower)
    
    score = int(round((found_keywords / len(experience_keywords)) * 100))
    return min(100, max(0, score))

def find_missing_critical_keywords(resume_text: str, technical_keywords: List[str], soft_skills: List[str]) -> List[str]:
    """Find missing critical keywords that should be added"""
    resume_lower = resume_text.lower()
    missing = []
    
    # Check technical keywords (prioritize these)
    for keyword in technical_keywords:
        if keyword not in resume_lower:
            missing.append(keyword)
    
    # Check soft skills (limit to most important ones)
    important_soft_skills = ['leadership', 'communication', 'problem solving', 'teamwork', 'analytical']
    for skill in important_soft_skills:
        if skill in soft_skills and skill not in resume_lower:
            missing.append(skill)
    
    return missing[:20]  # Limit to top 20 most important

def find_matching_keywords(resume_text: str, keywords: List[str]) -> List[str]:
    """Find which keywords are present in the resume"""
    resume_lower = resume_text.lower()
    return [keyword for keyword in keywords if keyword in resume_lower]

def baseline_overlap_score(resume_text: str, jd_text: str) -> Tuple[int, List[str]]:
    """Legacy function - now uses real ATS analysis"""
    analysis = real_ats_analysis(resume_text, jd_text)
    return analysis['final_score'], analysis['missing_keywords']

def call_groq_analysis(resume_text: str, job_description: str, rewrite: bool) -> Dict[str, str]:
    client = Groq(api_key=getattr(settings, "GROQ_API_KEY", None))

    rewrite_block = (
        "Also include a full optimized resume under a heading '### Optimized Resume:' "
        "that preserves truthful experience, avoids fabrications, and improves phrasing."
        if rewrite else
        "Do NOT include a rewritten resume."
    )

    prompt = f"""
You are an ATS and career expert. Compare the candidate's resume with the job description.

Return EXACTLY these sections (use these headings):
### ATS Score:
<single integer 0-100>

### Missing Keywords:
<comma-separated keywords (max 30)>

### Suggestions:
<6-10 bullet points>

{rewrite_block}
{resume_text}
{job_description}
"""

    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_completion_tokens=1200,
        top_p=1,
        stream=False
    )
    content = completion.choices[0].message.content

    # Parse sections
    llm_score = 0
    missing_keywords = ""
    suggestions = ""
    optimized_resume = ""

    m = re.search(r"###\s*ATS\s*Score:\s*(\d{1,3})", content, flags=re.I)
    if m:
        llm_score = int(m.group(1))
        llm_score = max(0, min(100, llm_score))

    m = re.search(r"###\s*Missing\s*Keywords:\s*(.+?)(?:\n###|\Z)", content, flags=re.I | re.S)
    if m:
        missing_keywords = m.group(1).strip()

    m = re.search(r"###\s*Suggestions:\s*(.+?)(?:\n###|\Z)", content, flags=re.I | re.S)
    if m:
        suggestions = m.group(1).strip()

    if rewrite:
        m = re.search(r"###\s*Optimized\s*Resume:\s*(.+)\Z", content, flags=re.I | re.S)
        if m:
            optimized_resume = m.group(1).strip()

    return {
        "llm_score": llm_score,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions,
        "optimized_resume": optimized_resume,
        "raw": content,
    }