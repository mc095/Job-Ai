from django.contrib import admin
from .models import AnalysisResult, ResumeAnalysis, AgentMemory

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)

@admin.register(AgentMemory)
class AgentMemoryAdmin(admin.ModelAdmin):
    list_display = ("user", "last_updated")
    readonly_fields = ("user", "strengths", "weaknesses", "preferences", "last_updated")
    search_fields = ("user__username",)
