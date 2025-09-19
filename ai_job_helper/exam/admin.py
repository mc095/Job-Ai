from django.contrib import admin
from .models import ExamResult, Exam, Question, Answer

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("user", "job_role", "score", "created_at")
    list_filter = ("created_at", "job_role")
    search_fields = ("user__username", "job_role")
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "text", "correct_option")
    search_fields = ("text",)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "user", "selected_option", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("user__username",)
