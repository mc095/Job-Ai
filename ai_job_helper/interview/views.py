import requests
import json
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import InterviewSession, InterviewMessage
from ai_agents.ai_service import AIService

@login_required
def interview_home(request):
    """
    Handles the interview home page, allowing a user to start a new session.
    It retrieves the user's resume and initializes a new interview session.
    """
    # Get user's resume if available
    resume_text = request.user.userprofile.resume_text.strip() if request.user.userprofile.resume_text else ""

    if request.method == "POST":
        jd = request.POST.get("job_description")
        session = InterviewSession.objects.create(
            user=request.user,
            job_description=jd,
            resume_text=resume_text
        )

        # Create initial interviewer message
        welcome_message = (
            "Hello! I will be conducting your interview today. "
            "I've reviewed your resume and the job description. "
            "I'll ask you a series of questions relevant to the position. "
            "Please take your time to provide detailed and specific answers. "
            "Are you ready to begin?"
        )
        InterviewMessage.objects.create(session=session, role="interviewer", content=welcome_message)

        # Redirect to the chat page, casting the ObjectId to a string
        return redirect("interview_chat", session_id=str(session._id))

    return render(request, "interview/home.html")


@login_required
def interview_chat(request, session_id):
    """
    Manages the interview chat interface, displaying messages and handling user responses.
    This view also triggers the LLM to generate new questions or final feedback.
    """
    try:
        session = InterviewSession.objects.get(_id=ObjectId(session_id), user=request.user)
    except (InterviewSession.DoesNotExist, ValueError):
        return render(request, "interview/error.html", {"message": "Interview session not found"})

    messages = session.messages.all().order_by("timestamp")

    if request.method == "POST" and not session.completed:
        candidate_answer = request.POST.get("answer")
        InterviewMessage.objects.create(session=session, role="candidate", content=candidate_answer)

        # Prepare conversation history
        history = [{"role": m.role, "content": m.content} for m in messages]
        history.append({"role": "candidate", "content": candidate_answer})

        # Check if the interview is over or if a new question is needed
        if session.current_question >= session.total_questions:
            # Generate and save final feedback
            feedback = generate_feedback(session, history)
            InterviewMessage.objects.create(session=session, role="interviewer", content=feedback)
            
            # Parse the feedback response for score and feedback text
            try:
                parts = feedback.split("FEEDBACK:", 1)
                score_part = parts[0].strip()
                feedback_part = parts[1].strip() if len(parts) > 1 else feedback
                
                # Extract score
                score = float(score_part.replace("SCORE:", "").strip())
                
                # Save score and feedback
                session.performance_score = score
                session.feedback_summary = feedback_part
                session.completed = True
            except Exception as e:
                print(f"Error parsing feedback: {str(e)}")
                session.completed = True
                # Set default values if parsing fails
                session.performance_score = 0
                session.feedback_summary = feedback
        else:
            # Generate and save the next question
            next_q = generate_interview_question(session.resume_text, session.job_description, history)
            InterviewMessage.objects.create(session=session, role="interviewer", content=next_q)
            session.current_question += 1

        session.save()
        return redirect("interview_chat", session_id=str(session._id))

    return render(request, "interview/chat.html", {
        "session": session,
        "messages": messages,
        "is_completed": session.completed
    })


def generate_interview_question(resume, jd, history):
    """
    Helper function to generate interview questions using AI agents.
    """
    try:
        ai_service = AIService()
        questions_data = ai_service.generate_interview_questions(jd)
        
        if questions_data and 'questions' in questions_data and questions_data['questions']:
            # Get the next question based on current question number
            current_q_num = len([m for m in history if m['role'] == 'interviewer']) - 1  # Subtract welcome message
            if current_q_num < len(questions_data['questions']):
                return questions_data['questions'][current_q_num]['question']
        
        # Fallback to a generic question
        return "Can you tell me about a challenging project you worked on and how you overcame the obstacles?"
        
    except Exception as e:
        return f"Error generating question: {str(e)}"


def generate_feedback(session, history):
    """
    Helper function to generate final interview feedback using AI agents.
    """
    try:
        # Prepare conversation context
        conversation = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        # Use AI service for feedback generation
        ai_service = AIService()
        
        # For now, we'll use a simple scoring mechanism
        # In a real implementation, you'd want to use AI to analyze the conversation
        score = 75  # Default score
        feedback = f"""
        SCORE: {score}
        FEEDBACK: Thank you for participating in this interview. Based on our conversation, I can see that you have relevant experience and skills for this position. Here are some key observations:
        
        Strengths:
        - Good communication skills
        - Relevant technical background
        - Shows enthusiasm for the role
        
        Areas for Improvement:
        - Consider providing more specific examples
        - Practice explaining complex technical concepts
        - Prepare more detailed responses about your achievements
        
        Overall Assessment:
        You demonstrated a solid understanding of the role requirements and showed good potential. With some additional preparation and experience, you could be a strong candidate for this position.
        """
        
        return feedback
        
    except Exception as e:
        return f"SCORE: 0\nFEEDBACK: Error generating feedback: {str(e)}"
