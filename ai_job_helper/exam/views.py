import json
import requests
from bson import ObjectId
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Answer
from django.conf import settings

@login_required
def home(request):
    """
    Renders the home page where the user can input a job role.
    Handles form submission to start the exam generation process.
    """
    if request.method == "POST":
        job_role = request.POST.get("job_role")
        request.session["job_role"] = job_role
        return redirect("exam_loading")
    return render(request, "exam/home.html")


@login_required
def exam_loading(request):
    """
    Initiates the exam generation process by calling the Gemini API.
    The API call is configured to return a structured JSON response.
    """
    try:
        job_role = request.session.get("job_role")
        if not job_role:
            return redirect("exam_home")

        # Use the settings to get the API key safely.
        gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not gemini_api_key:
            return render(request, "exam/error.html", {"message": "Gemini API key not configured"})

        # API endpoint for the Gemini model.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={gemini_api_key}"

        # Define the JSON schema for the desired output.
        # This tells the model exactly what structure to return, making parsing reliable.
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "question": {"type": "STRING"},
                    "options": {
                        "type": "OBJECT",
                        "properties": {
                            "A": {"type": "STRING"},
                            "B": {"type": "STRING"},
                            "C": {"type": "STRING"},
                            "D": {"type": "STRING"}
                        },
                        "propertyOrdering": ["A", "B", "C", "D"]
                    },
                    "correct": {"type": "STRING"}
                },
                "propertyOrdering": ["question", "options", "correct"]
            }
        }

        # The prompt is simplified because the response schema handles the structure.
        prompt_text = (
            f"Create a 30-question multiple-choice exam for the job role '{job_role}'. "
            "Each question should have exactly 4 concise options. "
            "'correct' must be one of 'A', 'B', 'C', 'D'."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema
            }
        }

        headers = {"Content-Type": "application/json"}
        try:
            # Make the API call with the structured payload.
            r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            r.raise_for_status()  # Raises an HTTPError for bad responses
            data = r.json()

            # For a structured output, the JSON is in a specific part of the response.
            raw_text_json = data["candidates"][0]["content"]["parts"][0]["text"]
            questions_data = json.loads(raw_text_json)

        except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            return render(request, "exam/error.html", {"message": f"API request failed or response invalid: {str(e)}"})

        if not questions_data or not isinstance(questions_data, list):
            return render(request, "exam/error.html", {"message": "Invalid response format from AI"})

        try:
            # Create the exam first
            exam = Exam.objects.create(
                user=request.user,
                job_role=job_role
            )

            # Then create all questions
            for q in questions_data:
                Question.objects.create(
                    exam=exam,
                    text=q["question"],
                    option_a=q["options"]["A"],
                    option_b=q["options"]["B"],
                    option_c=q["options"]["C"],
                    option_d=q["options"]["D"],
                    correct_option=q["correct"]
                )

            return redirect("exam_test", exam_id=str(exam._id))

        except Exception as e:
            # If anything goes wrong during exam/question creation, clean up and show error
            if 'exam' in locals():
                exam.delete()
            return render(request, "exam/error.html", {"message": f"Failed to create exam: {str(e)}"})

    except Exception as e:
        # A broad exception handler to catch any other issues.
        return render(request, "exam/error.html", {"message": f"An unexpected error occurred: {str(e)}"})


@login_required
def exam_test(request, exam_id):
    """
    Displays the exam questions for the user to take the test.
    Handles form submission after the user has answered all questions.
    """
    try:
        # Convert string exam_id to ObjectId for MongoDB
        exam = Exam.objects.get(_id=ObjectId(exam_id), user=request.user)
    except (Exam.DoesNotExist, ValueError):
        return render(request, "exam/error.html", {"message": "Exam not found"})

    questions = exam.questions.all()

    if request.method == "POST":
        score = 0
        for question in questions:
            selected = request.POST.get(question.mongo_id)
            if selected:
                Answer.objects.create(
                    question=question,
                    user=request.user,
                    selected_option=selected
                )
                if selected == question.correct_option:
                    score += 1
        exam.score = score
        exam.save()
        return redirect("exam_result", exam_id=str(exam._id))

    return render(request, "exam/test.html", {"exam": exam, "questions": questions})


@login_required
def exam_result(request, exam_id):
    """
    Displays the user's exam results.
    """
    try:
        # Convert string exam_id to ObjectId for MongoDB
        exam = Exam.objects.get(_id=ObjectId(exam_id), user=request.user)
    except (Exam.DoesNotExist, ValueError):
        return render(request, "exam/error.html", {"message": "Exam not found"})
    
    return render(request, "exam/result.html", {"exam": exam})