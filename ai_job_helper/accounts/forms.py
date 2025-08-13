from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture_url', 'resume_text']
        widgets = {
            'resume_text': forms.Textarea(attrs={
                'placeholder': 'Paste your resume content here...'
            })
        }
