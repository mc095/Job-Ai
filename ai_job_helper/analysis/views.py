# analysis/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from groq import Groq

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
            prompt = f"""
You are an expert resume reviewer.
The following is the candidate's resume:

{resume_text}

The following is the job description:

{job_description}

1. Analyze the resume against the job description.
2. Suggest clear, actionable improvements.
3. Rewrite the ENTIRE resume so it is optimized for this job description while keeping the tone professional.
Format your response as:

### Suggestions:
[bullet points]

### Rewritten Resume:
[full optimized resume text]
"""

            client = Groq()
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=1500,
                top_p=1,
                stream=False
            )

            ai_response = completion.choices[0].message.content  # ✅ Correct extraction

            # Optional: split into suggestions + rewritten resume
            if "### Rewritten Resume:" in ai_response:
                parts = ai_response.split("### Rewritten Resume:")
                ai_suggestions = parts[0].replace("### Suggestions:", "").strip()
                rewritten_resume = parts[1].strip()
            else:
                ai_suggestions = ai_response

    return render(request, "analysis/home.html", {
        "ai_suggestions": ai_suggestions,
        "rewritten_resume": rewritten_resume
    })
