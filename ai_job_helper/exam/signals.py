from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Exam, Question, Answer
from analysis.models import AgentMemory


@receiver(post_save, sender=Exam)
def update_agent_memory_after_exam(sender, instance: Exam, created: bool, **kwargs):
    """Update per-user AgentMemory based on latest exam score."""
    try:
        user = instance.user
        memory, _ = AgentMemory.objects.get_or_create(user=user)

        # Compute topic stats for this exam
        topic_stats = memory.topic_stats or {}
        answers = Answer.objects.filter(question__exam=instance, user=user)
        for ans in answers.select_related('question'):
            topic = (ans.question.topic or 'general').strip().lower()
            ts = topic_stats.get(topic, {"attempted": 0, "correct": 0, "accuracy": 0.0})
            ts["attempted"] += 1
            if ans.is_correct:
                ts["correct"] += 1
            ts["accuracy"] = round((ts["correct"] / ts["attempted"]) * 100.0, 2)
            topic_stats[topic] = ts

        # Update strengths/weaknesses based on topic accuracies
        strengths = set(memory.strengths or [])
        weaknesses = set(memory.weaknesses or [])
        for topic, ts in topic_stats.items():
            if ts["attempted"] >= 3:
                if ts["accuracy"] >= 80.0:
                    strengths.add(topic)
                    weaknesses.discard(topic)
                elif ts["accuracy"] <= 50.0:
                    weaknesses.add(topic)
        memory.topic_stats = topic_stats
        memory.strengths = sorted(list(strengths))
        memory.weaknesses = sorted(list(weaknesses))

        # Track preferred difficulty if present in preferences
        prefs = memory.preferences or {}
        prefs.setdefault('preferred_difficulty', 'medium')
        memory.preferences = prefs
        memory.save()
    except Exception:
        # Avoid breaking exam flow if memory update fails
        pass


