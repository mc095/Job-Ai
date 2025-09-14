from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'photo', 'resume_file', 'resume_text']
        widgets = {
            'resume_text': forms.Textarea(attrs={
                'placeholder': 'Paste your resume content here...'
            })
        }
