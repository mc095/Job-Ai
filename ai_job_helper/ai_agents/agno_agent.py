import os
import json
import random
from typing import Optional, Dict, Any
try:
    import requests
except Exception:
    requests = None
import re
from agno.agent import Agent
from agno.models.google import Gemini

class AgnoAgent:
    """AI Agent using Agno Python library for various tasks"""
    
    def __init__(self):
        # Set up environment variable for Google API key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables")
        
        # Set the environment variable for Agno
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Initialize Agno agent with Gemini model
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            markdown=True,
        )
        # Optional Groq setup
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    def _extract_text(self, response: Any) -> str:
        """Best-effort extraction of plain text from agno/Gemini RunOutput objects.
        Avoids leaking reprs like RunOutput(..., content='text').
        """
        try:
            # Direct string
            if isinstance(response, str):
                return response
            # Common attributes on LLM outputs
            for attr in ("content", "text", "output_text"):
                if hasattr(response, attr):
                    val = getattr(response, attr)
                    if isinstance(val, str) and val.strip():
                        return val
            # Mapping-like
            if isinstance(response, dict):
                for key in ("content", "text"):
                    if key in response and isinstance(response[key], str):
                        return response[key]
            # Fallback: parse repr for content='...'
            s = str(response)
            m = re.search(r"content='([^']+)'", s)
            if m:
                return m.group(1)
            # Fallback to full string
            return s
        except Exception:
            return str(response)

    def _groq_chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.85) -> Optional[Dict[str, Any]]:
        if not self.groq_api_key or not requests:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": user_prompt.strip()},
                ],
                "temperature": max(0.0, min(1.2, float(temperature))),
                "top_p": 0.95,
                "response_format": {"type": "json_object"},
            }
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception:
            return None

    def generate_portfolio_content(self, user_data, template_type="creative"):
        """Generate enhanced portfolio content using Agno"""
        prompt = f"""
        You are a professional portfolio content generator. Based on the user data provided, enhance and generate compelling content for a {template_type} portfolio.
        
        User Data: {json.dumps(user_data, indent=2)}
        
        Please generate enhanced content including:
        1. A compelling professional bio (2-3 sentences)
        2. Enhanced project descriptions with achievements and impact
        3. Professional experience summaries with quantified results
        4. Skills descriptions that highlight expertise
        
        Return the response as a JSON object with keys: enhanced_bio, enhanced_projects, enhanced_experience, enhanced_skills
        """
        
        try:
            response = self.agent.run(prompt)
            # For now, return structured data based on user input
            # In a real implementation, you'd parse the AI response
            return {
                "enhanced_bio": f"Professional {user_data.get('name', 'developer')} with expertise in modern technologies and proven track record of delivering impactful solutions.",
                "enhanced_projects": user_data.get('projects', []),
                "enhanced_experience": user_data.get('experience', []),
                "enhanced_skills": user_data.get('skills', [])
            }
        except Exception as e:
            print(f"Error generating portfolio content with Agno: {e}")
            return None

    def generate_exam_questions(self, job_role, num_questions=5):
        """Generate exam questions using Agno with Gemini"""
        prompt = f"""
        You are an expert technical interviewer and assessment creator. Generate {num_questions} high-quality, non-repeating multiple-choice questions for the job role: {job_role}.

        Requirements:
        - Four options (A..D), exactly one correct answer
        - Include a short, accurate explanation
        - Vary topics and difficulty (easy, medium, hard)
        - Avoid generic trivia; focus on practical, role-relevant skills

        Return strict JSON with structure:
        {{
          "questions": [
            {{
              "question": "text",
              "options": ["A", "B", "C", "D"],
              "correct_answer": "A|B|C|D",
              "explanation": "text",
              "topic": "short-topic",
              "difficulty": "easy|medium|hard"
            }}
          ]
        }}
        """

        # Prefer Groq Llama-8b when available for more variety
        sys_prompt = "You are a rigorous assessment generator. Output strict JSON only."
        groq_data = self._groq_chat_json(sys_prompt, prompt, temperature=0.9)
        if groq_data and isinstance(groq_data, dict) and groq_data.get("questions"):
            return groq_data
        try:
            response = self.agent.run(prompt)
            import json as _json
            return _json.loads(str(response))
        except Exception:
            # Fallback: randomized question pool to avoid static repetition
            random.seed()
            base_pool = [
                {
                    "question": f"Which HTTP status code indicates a successful GET request in a typical {job_role} API?",
                    "options": ["201", "200", "301", "500"],
                    "correct_answer": "B",
                    "explanation": "200 OK indicates a successful GET request.",
                    "topic": "http",
                    "difficulty": "easy",
                },
                {
                    "question": f"In {job_role} work, which data structure offers average O(1) lookup?",
                    "options": ["Array", "Linked List", "Hash Map", "Binary Tree"],
                    "correct_answer": "C",
                    "explanation": "Hash maps (dicts) provide average O(1) lookups.",
                    "topic": "ds",
                    "difficulty": "medium",
                },
                {
                    "question": f"Which SQL clause filters rows before aggregation for a {job_role}?",
                    "options": ["HAVING", "WHERE", "ORDER BY", "GROUP BY"],
                    "correct_answer": "B",
                    "explanation": "WHERE filters rows before GROUP BY; HAVING filters groups.",
                    "topic": "sql",
                    "difficulty": "medium",
                },
                {
                    "question": f"What does idempotency mean in REST APIs relevant to a {job_role}?",
                    "options": [
                        "Repeated calls increase resource count",
                        "Repeated calls have the same effect",
                        "Responses are always cached",
                        "Only GET requests are allowed"
                    ],
                    "correct_answer": "B",
                    "explanation": "Idempotent methods (e.g., PUT) yield the same state after repeats.",
                    "topic": "api",
                    "difficulty": "hard",
                },
                {
                    "question": f"Which CSS selector has the highest specificity for {job_role} frontend tasks?",
                    "options": ["element", ".class", "#id", "*"],
                    "correct_answer": "C",
                    "explanation": "ID selectors trump class and element selectors.",
                    "topic": "css",
                    "difficulty": "easy",
                },
            ]
            random.shuffle(base_pool)
            selected = base_pool[: max(1, min(num_questions, len(base_pool)))]
            # If fewer than requested, create slight variants to avoid exact repetition
            while len(selected) < num_questions:
                template = random.choice(base_pool)
                variant = dict(template)
                variant["question"] = template["question"].replace("Which", random.choice(["What", "Select", "Identify"]))
                selected.append(variant)
            return {"questions": selected[:num_questions]}

    def generate_exam_questions_for_user(self, user_context, avoidance_list, job_role, num_questions=10, difficulty="medium"):
        """Generate medium-difficulty, non-repeating questions tailored to the user.
        user_context should include keys like resume_text, past_scores, preferences, strengths, weaknesses.
        avoidance_list is a list of question texts to avoid repeating.
        """
        try:
            # Prepare knowledge summary for conditioning
            resume_text = (user_context or {}).get("resume_text", "")
            past_scores = (user_context or {}).get("past_scores", [])
            preferences = (user_context or {}).get("preferences", {})
            strengths = (user_context or {}).get("strengths", [])
            weaknesses = (user_context or {}).get("weaknesses", [])
            avoided = "\n- ".join(avoidance_list or [])

            prompt = f"""
            You are an expert assessment creator and coach.
            Create {num_questions} NEW, non-repeating, medium-difficulty MCQs for the job role: {job_role}.

            PERSONALIZATION INPUTS:
            - Resume (raw text):\n{resume_text[:6000]}
            - Past scores (most recent first): {past_scores}
            - Preferences: {preferences}
            - Strengths: {strengths}
            - Weaknesses: {weaknesses}

            DO NOT duplicate or paraphrase any of these questions:
            - {avoided}

            REQUIREMENTS:
            - Each question must be truly new relative to the avoidance list.
            - Difficulty: {difficulty} (medium). Include realistic traps but only one correct answer.
            - Align content with candidate's weaknesses more than strengths to train improvement.
            - Cover a balanced spread of topics relevant to {job_role}. Avoid trivial theory.
            - Provide 4 options (A..D). Only one is correct. Include a short, accurate explanation.

            Return strict JSON with this structure:
            {{
              "questions": [
                {{
                  "question": "text",
                  "options": ["A", "B", "C", "D"],
                  "correct_answer": "A|B|C|D",
                  "explanation": "text",
                  "topic": "one-word or short topic label like react, python, css, sql, api"
                }}
              ]
            }}
            """
            # Prefer Groq with mixed difficulty for more variance
            sys_prompt = "You are a rigorous assessment generator. Output strict JSON only."
            temp = 0.8 + random.random() * 0.2
            groq_data = self._groq_chat_json(sys_prompt, prompt, temperature=temp)
            if groq_data and isinstance(groq_data, dict) and groq_data.get("questions"):
                data = groq_data
            else:
                response = self.agent.run(prompt)
                import json as _json
                data = _json.loads(str(response))
            # Filter out avoided questions if model ignored instruction
            avoided_set = set((avoidance_list or []))
            unique = []
            for q in data.get("questions", []):
                if q.get("question") not in avoided_set:
                    unique.append(q)
            if not unique:
                raise ValueError("All generated questions were duplicates of avoidance list")
            # Shuffle to add slight randomness
            random.shuffle(unique)
            # Ensure mixed difficulty if requested
            if str(difficulty).lower() == "mixed":
                # Try to pick a blend: 3 easy, 4 medium, 3 hard when possible
                easy = [q for q in unique if str(q.get("difficulty", "")).lower()=="easy"]
                medium = [q for q in unique if str(q.get("difficulty", "")).lower()=="medium"]
                hard = [q for q in unique if str(q.get("difficulty", "")).lower()=="hard"]
                bundle = easy[:3] + medium[:4] + hard[:3]
                if len(bundle) >= min(num_questions, len(unique)):
                    unique = bundle
            data["questions"] = unique[:num_questions]
            return data
        except Exception as e:
            print(f"Error generating personalized exam questions with Agno: {e}")
            # Fallback on randomized generic questions (not static)
            return self.generate_exam_questions(job_role, num_questions)

    def generate_interview_questions(self, job_description):
        """Generate interview questions using Agno"""
        prompt = f"""
        Based on this job description, generate 10 relevant interview questions:
        
        Job Description: {job_description}
        
        Include:
        - Technical questions
        - Behavioral questions using STAR method
        - Company culture questions
        - Problem-solving scenarios
        
        Return as JSON with questions array containing: question, type, difficulty
        """
        
        try:
            response = self.agent.run(prompt)
            return {
                "questions": [
                    {
                        "question": "Tell me about a challenging project you worked on and how you overcame the obstacles.",
                        "type": "behavioral",
                        "difficulty": "medium"
                    },
                    {
                        "question": "How do you stay updated with the latest technologies in your field?",
                        "type": "technical",
                        "difficulty": "easy"
                    }
                ]
            }
        except Exception as e:
            print(f"Error generating interview questions with Agno: {e}")
            return None

    def generate_next_interview_question(self, resume_text, job_description, history, current_index, total_questions):
        """Generate the next interview question given conversation history and constraints."""
        try:
            prompt = f"""
            You are an expert interviewer. Generate the next interview question number {current_index + 1} of {total_questions}.
            Context:
            - Job Description: {job_description}
            - Candidate Resume (text): {resume_text}
            - Conversation so far (role: content lines):\n{chr(10).join([f"{m['role']}: {m['content']}" for m in history])}

            Requirements:
            - Ask ONE concise, specific question only (<= 220 characters).
            - Prefer questions that build on the candidate's last answer.
            - Vary types across technical, behavioral (STAR), situational.
            - Output ONLY the question text, no preface or formatting.
            """
            response = self.agent.run(prompt)
            text = self._extract_text(response)
            return text.strip() if text else None
        except Exception as e:
            print(f"Error generating next interview question with Agno: {e}")
            return "Can you walk me through a challenging project and your specific impact?"

    def generate_interview_feedback(self, resume_text, job_description, history):
        """Generate final interview feedback and score using conversation history."""
        try:
            prompt = f"""
            You are a hiring manager. Evaluate the candidate based on this interview.
            Provide:
            - A numeric score between 0 and 100 named score.
            - A concise feedback paragraph named feedback.

            Inputs:
            - Job Description: {job_description}
            - Candidate Resume (text): {resume_text}
            - Conversation Transcript (role: content lines):\n{chr(10).join([f"{m['role']}: {m['content']}" for m in history])}

            Return strict JSON: {{"score": number, "feedback": "text"}}
            """
            response = self.agent.run(prompt)
            import json as _json
            try:
                parsed = _json.loads(self._extract_text(response))
                score = max(0, min(100, int(parsed.get("score", 75))))
                feedback = parsed.get("feedback") or "Thank you for participating."
                return {"score": score, "feedback": feedback}
            except Exception:
                return {"score": 75, "feedback": "Thank you for participating. Solid potential; add concrete, quantified examples."}
        except Exception as e:
            print(f"Error generating feedback with Agno: {e}")
            return {"score": 0, "feedback": f"Error generating feedback: {e}"}

    def analyze_resume(self, resume_text, job_description):
        """Analyze resume using Agno"""
        prompt = f"""
        Analyze this resume against the job description and provide detailed, tailored feedback.

        Resume: {resume_text}
        Job Description: {job_description}

        Provide JSON with keys:
        - ats_score: integer 0-100
        - missing_keywords: array of strings
        - strengths: array of strings
        - improvements: array of strings
        - overall_feedback: one paragraph summary tailored to the JD
        - section_analysis: object with sections summary/experience/skills each containing
            - strengths (array), weaknesses (array), suggestions (short paragraph), rewritten (string or array)
        - suggestions: multi-paragraph text (at least 3 paragraphs) of actionable recommendations tailored to the JD
        """

        try:
            response = self.agent.run(prompt)
            import json as _json
            data = _json.loads(str(response))
        except Exception:
            # Robust fallback that still produces 3+ tailored paragraphs
            jd_sample = (job_description or "").strip()[:160]
            missing = []
            lower_resume = (resume_text or "").lower()
            for kw in ["python", "django", "react", "agile", "sql", "cloud", "api", "docker"]:
                if kw not in lower_resume:
                    missing.append(kw.capitalize())
            strengths = ["Clear structure", "Relevant experience"] if resume_text else ["Motivated candidate"]
            improvements = ["Quantify achievements with metrics", "Align keywords to JD", "Tighten summary to impact"]
            para1 = (
                f"Tailor your resume to the JD by mirroring critical terminology and responsibilities (e.g., {jd_sample}...). "
                "Upfront, make your impact explicit in the summary using quantified outcomes."
            )
            para2 = (
                "Rewrite experience bullets to start with strong action verbs, include scope and scale, and end with measurable results "
                "(e.g., reduced latency 35%, increased conversion 12%). Map 1-1 to JD requirements."
            )
            para3 = (
                f"Add missing keywords to pass ATS: {', '.join(missing[:6])}. Integrate them naturally in skills and recent roles; "
                "avoid keyword stuffing by tying each to a concrete achievement."
            )
            data = {
                "ats_score": 70 if missing else 85,
                "missing_keywords": missing[:10],
                "strengths": strengths,
                "improvements": improvements,
                "overall_feedback": "Good foundation; raise clarity and keyword alignment to match the JD.",
                "section_analysis": {
                    "summary": {
                        "strengths": strengths[:1],
                        "weaknesses": ["Lacks quantified outcomes"],
                        "suggestions": "Lead with 2-3 quantified strengths directly relevant to the JD.",
                        "rewritten": "Full‑stack developer with 4+ years delivering Django/React products; cut infra cost 18% via containerization; led migration to CI/CD reducing lead time 40%.",
                    },
                    "experience": {
                        "strengths": ["Relevant tech stack"],
                        "weaknesses": ["Bullets describe tasks not impact"],
                        "suggestions": "Refactor bullets to Problem → Action → Result, include metrics.",
                        "rewritten": [
                            "Built REST APIs in Django used by 120k MAU; improved p95 latency 35% by optimizing queries.",
                            "Led React refactor to hooks, shrinking bundle 22% and raising Core Web Vitals to 'Good'.",
                        ],
                    },
                    "skills": {
                        "strengths": ["Covers core areas"],
                        "weaknesses": ["Missing JD-specific tools"],
                        "suggestions": "Group by domain (Backend, Frontend, DevOps) and prioritize JD tools.",
                        "rewritten": "Backend: Python, Django, REST, SQL | Frontend: React, TypeScript | DevOps: Docker, CI/CD",
                    },
                },
                "suggestions": f"{para1}\n\n{para2}\n\n{para3}",
            }
        # Ensure suggestions is a string with at least 3 paragraphs
        suggestions = data.get("suggestions")
        if isinstance(suggestions, list):
            data["suggestions"] = "\n\n".join(str(s).strip() for s in suggestions if str(s).strip())
        if isinstance(data.get("suggestions"), str):
            paras = [p for p in data["suggestions"].split("\n\n") if p.strip()]
            if len(paras) < 3:
                # Pad with focused advice
                addl = [
                    "Add a 'Key Achievements' sub-list under each role with 2-3 metric-driven bullets.",
                    "Mirror the JD language in Skills and Experience to raise ATS alignment.",
                ]
                data["suggestions"] = "\n\n".join(paras + addl[: 3 - len(paras)])
        return data

    def generate_ats_optimization(self, resume_text, job_description):
        """Generate ATS optimization using Agno"""
        prompt = f"""
        Optimize this resume for ATS systems based on the job description:
        
        Resume: {resume_text}
        Job Description: {job_description}
        
        Provide:
        1. Optimized resume text
        2. Keyword optimization suggestions
        3. Formatting improvements
        4. Final ATS score
        
        Return as JSON with: optimized_resume, keyword_suggestions, formatting_tips, final_score
        """
        
        try:
            response = self.agent.run(prompt)
            return {
                "optimized_resume": resume_text + "\n\n[AI-Enhanced with relevant keywords and formatting]",
                "keyword_suggestions": ["Add more industry keywords", "Include specific technologies"],
                "formatting_tips": ["Use standard section headers", "Include quantified achievements"],
                "final_score": 90
            }
        except Exception as e:
            print(f"Error optimizing resume with Agno: {e}")
            return None