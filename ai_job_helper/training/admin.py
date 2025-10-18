from django.contrib import admin
from .models import TrainingSession, TrainingMessage

class TrainingMessageInline(admin.TabularInline):
    model = TrainingMessage
    extra = 0

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)
    inlines = [TrainingMessageInline]

@admin.register(TrainingMessage)
class TrainingMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "timestamp")
    list_filter = ("role", "timestamp")
    search_fields = ("session__user__username", "content")
