from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId

class InterviewSession(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_description = models.TextField()
    resume_text = models.TextField()
    current_question = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    feedback_summary = models.TextField(null=True, blank=True)
    performance_score = models.FloatField(null=True, blank=True)  # 0-100 score

    def __str__(self):
        return f"Interview for {self.user.username}"

class InterviewMessage(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=15, choices=(
        ("interviewer", "Interviewer"),
        ("candidate", "Candidate")
    ))
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} message in {self.session}"
