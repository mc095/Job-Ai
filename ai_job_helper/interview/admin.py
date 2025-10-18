from django.contrib import admin
from .models import InterviewSession, InterviewMessage

class InterviewMessageInline(admin.TabularInline):
    model = InterviewMessage
    extra = 0

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "current_question", "total_questions", "completed", "created_at")
    list_filter = ("completed", "created_at")
    search_fields = ("user__username",)
    inlines = [InterviewMessageInline]

@admin.register(InterviewMessage)
class InterviewMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "timestamp")
    list_filter = ("role", "timestamp")
    search_fields = ("session__user__username", "content")
