from django.contrib import admin
from .models import ATSResult

@admin.register(ATSResult)
class ATSResultAdmin(admin.ModelAdmin):
    list_display = ("user", "final_score", "created_at")
    list_filter = ("created_at", "final_score")
    search_fields = ("user__username",)
