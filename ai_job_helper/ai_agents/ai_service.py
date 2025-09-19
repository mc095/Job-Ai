from .agno_agent import AgnoAgent

class AIService:
    """AI service powered by agno Agent using Gemini model."""
    
    def __init__(self):
        self.agno_agent = AgnoAgent()
    
    def generate_portfolio_content(self, user_data, template_type="creative"):
        """Generate portfolio content using agno (Gemini model)."""
        return self.agno_agent.generate_portfolio_content(user_data, template_type)
    
    def generate_exam_questions(self, job_role, num_questions=10):
        """Generate exam questions using agno (Gemini model)."""
        return self.agno_agent.generate_exam_questions(job_role, num_questions)

    def generate_exam_questions_for_user(self, user_context, avoidance_list, job_role, num_questions=10, difficulty="medium"):
        """Generate personalized, non-repeating exam questions for a user using agno (Gemini)."""
        return self.agno_agent.generate_exam_questions_for_user(
            user_context=user_context,
            avoidance_list=avoidance_list,
            job_role=job_role,
            num_questions=num_questions,
            difficulty=difficulty,
        )
    
    def generate_interview_questions(self, job_description):
        """Generate a bank of interview questions using agno (Gemini)."""
        return self.agno_agent.generate_interview_questions(job_description)

    def generate_next_interview_question(self, resume_text, job_description, history, current_index, total_questions):
        """Generate the next interview question using conversation context."""
        return self.agno_agent.generate_next_interview_question(
            resume_text=resume_text,
            job_description=job_description,
            history=history,
            current_index=current_index,
            total_questions=total_questions,
        )
    
    def analyze_resume(self, resume_text, job_description):
        """Analyze resume using agno (Gemini)."""
        return self.agno_agent.analyze_resume(resume_text, job_description)
    
    def generate_ats_optimization(self, resume_text, job_description):
        """Generate ATS optimization using agno (Gemini)."""
        return self.agno_agent.generate_ats_optimization(resume_text, job_description)

    def generate_interview_feedback(self, resume_text, job_description, history):
        """Generate final interview feedback and numeric score using conversation context."""
        return self.agno_agent.generate_interview_feedback(
            resume_text=resume_text,
            job_description=job_description,
            history=history,
        )
