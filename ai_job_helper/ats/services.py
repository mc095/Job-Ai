import re
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

def baseline_overlap_score(resume_text: str, jd_text: str) -> Tuple[int, List[str]]:
    """Very simple heuristic: overlap of keyword sets."""
    resume_tokens = set(extract_keywords(resume_text))
    jd_tokens = extract_keywords(jd_text)

    stop = {"and", "or", "with", "the", "a", "an", "to", "of", "in", "for", "on", "at", "by", "as"}
    jd_tokens = [w for w in jd_tokens if w not in stop and len(w) > 2]
    jd_set = set(jd_tokens)

    if not jd_set:
        return 0, []

    common = resume_tokens.intersection(jd_set)
    coverage = int(round(len(common) / len(jd_set) * 100))
    missing = sorted(list(jd_set - resume_tokens))[:50]

    return max(0, min(coverage, 100)), missing

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