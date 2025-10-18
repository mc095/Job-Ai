from django.contrib import admin
from .models import Portfolio

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'selected_template', 'created_at']
    list_filter = ['selected_template', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['portfolio_data']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['user']
        return self.readonly_fields

