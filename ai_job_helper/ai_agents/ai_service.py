from .agno_agent import AgnoAgent
from .gemini_agent import GeminiAgent

class AIService:
    """Unified AI service that tries Agno first, then falls back to Gemini"""
    
    def __init__(self):
        self.agno_agent = AgnoAgent()
        self.gemini_agent = GeminiAgent()
    
    def generate_portfolio_content(self, user_data, template_type="creative"):
        """Generate portfolio content using AI agents"""
        # Try Agno first
        result = self.agno_agent.generate_portfolio_content(user_data, template_type)
        if result:
            return result
        
        # Fallback to Gemini
        return self.gemini_agent.generate_portfolio_content(user_data, template_type)
    
    def generate_exam_questions(self, job_role, num_questions=10):
        """Generate exam questions using AI agents - prioritize Gemini for accuracy"""
        # Try Gemini first for better accuracy
        result = self.gemini_agent.generate_exam_questions(job_role, num_questions)
        if result:
            print("✅ Using Gemini for exam questions")
            return result
        
        # Fallback to Agno
        print("⚠️ Falling back to Agno for exam questions")
        return self.agno_agent.generate_exam_questions(job_role, num_questions)
    
    def generate_interview_questions(self, job_description):
        """Generate interview questions using AI agents"""
        # Try Agno first
        result = self.agno_agent.generate_interview_questions(job_description)
        if result:
            return result
        
        # Fallback to Gemini
        return self.gemini_agent.generate_interview_questions(job_description)
    
    def analyze_resume(self, resume_text, job_description):
        """Analyze resume using AI agents"""
        # Try Agno first
        result = self.agno_agent.analyze_resume(resume_text, job_description)
        if result:
            return result
        
        # Fallback to Gemini
        return self.gemini_agent.analyze_resume(resume_text, job_description)
    
    def generate_ats_optimization(self, resume_text, job_description):
        """Generate ATS optimization using AI agents"""
        # Try Agno first
        result = self.agno_agent.generate_ats_optimization(resume_text, job_description)
        if result:
            return result
        
        # Fallback to Gemini
        return self.gemini_agent.generate_ats_optimization(resume_text, job_description)
