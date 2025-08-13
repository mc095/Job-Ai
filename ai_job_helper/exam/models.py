from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId

class ExamResult(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField()  # Store as percentage
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exam Result for {self.user.username}: {self.score}%"

    class Meta:
        ordering = ['-created_at']

class Exam(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.job_role} - {self.created_at}"

class Question(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    # The fix is to add null=True and blank=True to make the field optional during migration.
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, default='A')

    def __str__(self):
        return f"Question for {self.exam.job_role}"

    def get_options(self):
        return [
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]

    @property
    def mongo_id(self):
        """Template-friendly ID accessor"""
        return str(self._id)

class Answer(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return f"Answer for {self.question.exam.job_role}"