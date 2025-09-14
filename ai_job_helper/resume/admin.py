from django.contrib import admin
from .models import Resume, PersonalInfo, Education, Experience, Skill, Project, Certification, AdditionalSection

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'title']

@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution', 'degree_type', 'field_of_study', 'start_year', 'grad_year']
    list_filter = ['degree_type', 'start_year', 'grad_year']
    search_fields = ['institution', 'field_of_study']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['company', 'position', 'start_year', 'is_current']
    list_filter = ['is_current', 'start_year']
    search_fields = ['company', 'position']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency']
    list_filter = ['category', 'proficiency']
    search_fields = ['name']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_year', 'is_ongoing']
    list_filter = ['is_ongoing', 'start_year']
    search_fields = ['name', 'technologies']

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuer', 'issue_year']
    list_filter = ['issue_year']
    search_fields = ['name', 'issuer']

@admin.register(AdditionalSection)
class AdditionalSectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title', 'content']
