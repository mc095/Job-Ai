from django import forms
from .models import Resume, PersonalInfo, Education, Experience, Skill, Project, Certification, AdditionalSection

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'job_title', 
                 'linkedin_url', 'github_url', 'website_url']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn URL'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub URL'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website URL'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'location', 'degree_type', 'field_of_study', 
                 'start_month', 'start_year', 'grad_month', 'grad_year', 
                 'gpa', 'gpa_scale', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'degree_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree Type'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Field of Study'}),
            'start_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Month'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Start Year'}),
            'grad_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Graduation Month'}),
            'grad_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Graduation Year'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'GPA', 'step': '0.01'}),
            'gpa_scale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GPA Scale'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'location', 'start_month', 'start_year', 
                 'end_month', 'end_year', 'is_current', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Position Title'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'start_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Month'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Start Year'}),
            'end_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'End Month'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'End Year'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job Description'}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'proficiency': forms.Select(attrs={'class': 'form-control'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'technologies', 'start_month', 'start_year', 
                 'end_month', 'end_year', 'is_ongoing', 'github_url', 'live_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Project Description'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Technologies (comma-separated)'}),
            'start_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Month'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Start Year'}),
            'end_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'End Month'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'End Year'}),
            'is_ongoing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub URL'}),
            'live_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Live URL'}),
        }

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuer', 'issue_date', 'issue_year', 'credential_id', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certification Name'}),
            'issuer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issuing Organization'}),
            'issue_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issue Date'}),
            'issue_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Issue Year'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Credential ID'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Credential URL'}),
        }

class AdditionalSectionForm(forms.ModelForm):
    class Meta:
        model = AdditionalSection
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Section Content'}),
        }

# Formset for multiple entries
EducationFormSet = forms.inlineformset_factory(Resume, Education, form=EducationForm, extra=1, can_delete=True)
ExperienceFormSet = forms.inlineformset_factory(Resume, Experience, form=ExperienceForm, extra=1, can_delete=True)
SkillFormSet = forms.inlineformset_factory(Resume, Skill, form=SkillForm, extra=1, can_delete=True)
ProjectFormSet = forms.inlineformset_factory(Resume, Project, form=ProjectForm, extra=1, can_delete=True)
CertificationFormSet = forms.inlineformset_factory(Resume, Certification, form=CertificationForm, extra=1, can_delete=True)
AdditionalSectionFormSet = forms.inlineformset_factory(Resume, AdditionalSection, form=AdditionalSectionForm, extra=1, can_delete=True)
