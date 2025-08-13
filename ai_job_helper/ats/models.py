from django.db import models
from django.contrib.auth.models import User

class ATSResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_description = models.TextField()
    baseline_score = models.PositiveIntegerField(default=0)   # heuristic overlap score
    final_score = models.PositiveIntegerField(default=0)      # fused with LLM (0-100)
    missing_keywords = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    optimized_resume = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ATSResult(user={self.user.username}, score={self.final_score}, at={self.created_at:%Y-%m-%d %H:%M})"
