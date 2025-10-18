from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId

class TrainingSession(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_description = models.TextField()
    resume_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Training for {self.user.username}"

class TrainingMessage(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    session = models.ForeignKey(TrainingSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=(("user", "User"), ("bot", "Interviewer")))
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} message in {self.session}"
