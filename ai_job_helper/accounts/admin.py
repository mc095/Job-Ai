from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


def hard_delete_users(modeladmin, request, queryset):
    # Directly delete users and their cascaded relations in MongoDB without admin's collector
    for user in queryset:
        user.delete()
hard_delete_users.short_description = "Delete selected users (direct)"


class UserAdmin(BaseUserAdmin):
    actions = [hard_delete_users]

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
