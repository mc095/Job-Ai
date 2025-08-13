# exam/services.py
import os
from typing import List, Annotated
from pydantic import BaseModel, Field, field_validator
from agno.agent import Agent
from agno.models.groq import Groq

class MCQ(BaseModel):
    question: str = Field(..., description="MCQ question text")
    options: Annotated[List[str], Field(min_length=4, max_length=4)]
    correct_index: int = Field(..., ge=0, le=3, description="Index of the correct option (0..3)")
    explanation: str = Field("", description="Why the answer is correct")

    @field_validator('question')
    @classmethod
    def no_empty_q(cls, v):
        if not v.strip():
            raise ValueError("question empty")
        return v

class MCQSet(BaseModel):
    role: str
    questions: Annotated[List[MCQ], Field(min_length=30, max_length=30)]

def generate_mcqs_for_role(job_role: str) -> MCQSet:
    """
    Returns a MCQSet with exactly 30 MCQs for the given job role.
    Requires GROQ_API_KEY in environment.
    """
    # You can choose any Groq chat model that supports instruction following well.
    # llama-3.1-8b-instant or mixtral-8x7b are good fast choices.
    model = Groq(id="llama-3.1-8b-instant")  # fast & cheap
    agent = Agent(
        model=model,
        description=(
            "You are an assessment generator. Create a 30-question MCQ exam for the given job role. "
            "Difficulty: beginner to intermediate, with a few advanced items. Ensure 4 options each."
        ),
        response_model=MCQSet,          # Pydantic schema forces structure
        parse_response=True,            # Convert to Pydantic
        use_json_mode=True              # Ask model to return JSON directly
    )

    prompt = f"""
Role: {job_role}

Generate a 30-question multiple-choice test tailored to the role above.
Rules:
- Each question must have exactly 4 concise options.
- 'correct_index' must be an integer 0..3.
- Prefer practical, real-world topics; avoid trick questions.
- Include an explanation.

Return only JSON conforming to the schema (MCQSet) with fields: role, questions[30].
"""
    res = agent.run(prompt, stream=False)  # returns MCQSet because of response_model
    return res  # already MCQSet