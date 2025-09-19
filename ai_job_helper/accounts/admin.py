from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile
from exam.models import Exam
from analysis.models import AgentMemory
from ai_agents.ai_service import AIService
from analysis.models import AnalysisResult


def hard_delete_users(modeladmin, request, queryset):
    # Directly delete users and their cascaded relations in MongoDB without admin's collector
    for user in queryset:
        user.delete()
hard_delete_users.short_description = "Delete selected users (direct)"


class UserAdmin(BaseUserAdmin):
    actions = [hard_delete_users]

    def performance_summary(self, obj):
        latest_exams = Exam.objects.filter(user=obj).order_by('-created_at')[:5]
        scores = [e.score for e in latest_exams]
        return f"Recent scores: {scores}"

    def agent_memory(self, obj):
        try:
            mem = AgentMemory.objects.get(user=obj)
            return f"S:{len(mem.strengths)} W:{len(mem.weaknesses)}"
        except AgentMemory.DoesNotExist:
            return "No memory"

    list_display = BaseUserAdmin.list_display + ('performance_summary', 'agent_memory')

    actions = BaseUserAdmin.actions + ['reanalyze_resume'] if hasattr(BaseUserAdmin, 'actions') else ['reanalyze_resume']

    def reanalyze_resume(self, request, queryset):
        created = 0
        for user in queryset:
            try:
                profile = user.userprofile
                text = profile.extracted_text or profile.resume_text or ''
                if not text:
                    continue
                # Use Gemini (via agno) to analyze resume text against a generic role context
                ai = AIService()
                analysis = ai.analyze_resume(text, job_description="Generic Software/Tech Role") or {}
                score = float(analysis.get('ats_score', 75))
                feedback = analysis.get('overall_feedback') or analysis.get('suggestions') or 'AI re-analysis'
                AnalysisResult.objects.create(user=user, score=round(score, 1), feedback=feedback)
                created += 1
            except Exception:
                continue
        self.message_user(request, f"Re-analyzed resume for {created} user(s).")
    reanalyze_resume.short_description = "Re-analyze Resume and update latest score"

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the built-in bulk delete which triggers Djongo issues
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# Replace default admin to inject our action
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name")
