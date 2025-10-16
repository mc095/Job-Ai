import os
import json
from typing import Any, Dict, List, Optional


class AIService:
    """
    Gemini-backed AI service for generating exam questions.

    Method: generate_exam_questions_for_user returns:
    {
      "questions": [
        {
          "question": str,
          "options": [str, str, str, str],
          "correct_answer": str | int,  # letter A-D, index 0-3, or option text
          "explanation": Optional[str],
          "topic": Optional[str]
        }, ...
      ]
    }
    """

    def __init__(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable")

        self._client = None
        self._legacy_model = None
        self._model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

        # Prefer the new google.genai client when available
        try:
            from google import genai as genai_client  # type: ignore
            self._client = genai_client.Client(api_key=api_key)
        except Exception:
            self._client = None

        if self._client is None:
            try:
                import google.generativeai as genai_legacy  # type: ignore
                genai_legacy.configure(api_key=api_key)
                self._legacy_model = genai_legacy
            except Exception as exc:
                raise RuntimeError("No Gemini client available (google.genai / google-generativeai)") from exc

    def generate_exam_questions_for_user(
        self,
        *,
        user_context: Dict[str, Any],
        avoidance_list: Optional[List[str]],
        job_role: str,
        num_questions: int = 30,
        difficulty: str = "medium",
    ) -> Dict[str, Any]:
        """Generate 30 unique questions FAST in ONE API call. Includes explanation for each answer."""
        
        # Build compact avoidance hint (only first 5 for speed)
        avoid_hint = ""
        if avoidance_list and len(avoidance_list) > 0:
            avoid_hint = f" Avoid: {', '.join([q[:30] for q in avoidance_list[:5]])}..."
        
        # Ultra-compact prompt for speed
        prompt = (
            f'{num_questions} unique {job_role} interview questions.{avoid_hint}\n'
            f'JSON: {{"questions":[{{"question":str,"options":[4 strings],"correct_answer":"A-D","explanation":str,"topic":str}}]}}'
        )
        
        try:
            # Use faster model if available
            fast_model = "gemini-2.0-flash-exp" if "2.0" in self._model_name else self._model_name
            
            if self._client:
                response = self._client.models.generate_content(
                    model=fast_model,
                    contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0.7, "max_output_tokens": 16000}
                )
                text = response.text
            elif self._legacy_model:
                model = self._legacy_model.GenerativeModel(
                    fast_model,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.7, "max_output_tokens": 16000}
                )
                response = model.generate_content(prompt)
                text = response.text
            else:
                raise RuntimeError("No Gemini client")
            
            data = json.loads(text)
            raw_questions = data.get("questions", [])
            
            # Deduplicate questions - ensure uniqueness
            questions = []
            seen_questions = set()
            avoid_set = {q.lower().strip() for q in (avoidance_list or [])}
            
            for q in raw_questions:
                qtext = str(q.get("question", "")).strip()
                if not qtext or len(qtext) < 10:
                    continue
                    
                # Check if question is unique
                qkey = qtext.lower().strip()
                if qkey in seen_questions or qkey in avoid_set:
                    continue
                
                # Ensure 4 options
                options = q.get("options", [])
                if not isinstance(options, list):
                    options = []
                while len(options) < 4:
                    options.append(f"Option {len(options) + 1}")
                options = [str(opt).strip() for opt in options[:4]]
                
                # Normalize correct answer
                correct = q.get("correct_answer", "A")
                if isinstance(correct, int) and 0 <= correct < 4:
                    correct = ['A', 'B', 'C', 'D'][correct]
                else:
                    correct = str(correct)[0].upper() if correct else 'A'
                    if correct not in ['A', 'B', 'C', 'D']:
                        correct = 'A'
                
                # Ensure explanation exists
                explanation = str(q.get("explanation", "")).strip()
                if not explanation or len(explanation) < 5:
                    explanation = f"The correct answer is {correct} because it is the most appropriate option for this {job_role} question."
                
                questions.append({
                    "question": qtext,
                    "options": options,
                    "correct_answer": correct,
                    "explanation": explanation,
                    "topic": str(q.get("topic", job_role)).strip()
                })
                seen_questions.add(qkey)
                
                # Stop when we have enough unique questions
                if len(questions) >= num_questions:
                    break
            
            return {"questions": questions}
        except Exception as e:
            # Log error and return empty
            import logging
            logging.error(f"Question generation failed: {str(e)}")
            return {"questions": []}








