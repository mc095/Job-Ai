from django import forms
from .models import Portfolio, PORTFOLIO_TEMPLATES

class PortfolioDataForm(forms.Form):
    # Personal Information
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'Your full name'
    }))
    
    titles = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 3,
        'placeholder': 'Enter your job titles, one per line\nExample:\nSoftware Developer\nUI/UX Designer\nFull Stack Engineer'
    }), help_text="Enter each title on a new line")
    
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 5,
        'placeholder': 'Tell us about yourself, your passion, and what you do...'
    }))
    
    location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'City, Country'
    }))
    
    # Contact Information
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'your.email@example.com'
    }))
    
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': '+1 (555) 123-4567'
    }))
    
    # Social Links
    github_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://github.com/yourusername'
    }))
    
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://linkedin.com/in/yourusername'
    }))
    
    website_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://yourwebsite.com'
    }))
    
    twitter_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://twitter.com/yourusername'
    }))
    
    # Experience
    experience = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 8,
        'placeholder': 'Enter your work experience in this format:\n\nCompany Name | Job Title | Duration | Description\nExample:\n\nGoogle | Software Engineer | 2020 - Present | Developed scalable web applications using React and Node.js\nMicrosoft | Frontend Developer | 2018 - 2020 | Built responsive user interfaces and improved user experience'
    }), help_text="Format: Company | Title | Duration | Description (one per line)")
    
    # Education
    education = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 6,
        'placeholder': 'Enter your education in this format:\n\nInstitution | Degree | Year | GPA (optional)\nExample:\n\nStanford University | Bachelor of Science in Computer Science | 2018 | 3.8\nMIT | Master of Science in Software Engineering | 2020 | 3.9'
    }), help_text="Format: Institution | Degree | Year | GPA (one per line)")
    
    # Skills
    skills = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 4,
        'placeholder': 'Enter your skills, separated by commas:\nExample:\n\nJavaScript, Python, React, Node.js, Django, PostgreSQL, AWS, Docker, Git'
    }), help_text="Separate skills with commas")
    
    # Projects
    projects = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 10,
        'placeholder': 'Enter your projects in this format:\n\nProject Name | Short Description | Long Description | Technologies | Live URL | GitHub URL\nExample:\n\nE-Commerce App | A full-stack e-commerce platform | Built a complete e-commerce solution with user authentication, payment processing, and admin dashboard. Features include product catalog, shopping cart, order management, and real-time notifications. | React, Node.js, MongoDB, Stripe | https://myecommerce.com | https://github.com/username/ecommerce'
    }), help_text="Format: Name | Short Desc | Long Desc | Technologies | Live URL | GitHub URL (one per line)")
    
    # Certifications
    certifications = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'rows': 4,
        'placeholder': 'Enter your certifications in this format:\n\nCertification Name | Issuer | Year\nExample:\n\nAWS Certified Solutions Architect | Amazon Web Services | 2023\nGoogle Cloud Professional Developer | Google | 2022'
    }), help_text="Format: Name | Issuer | Year (one per line)")
    
    # Profile Images
    profile_image_small = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://example.com/profile-small.jpg'
    }), help_text="URL for small profile image (60x60px)")
    
    profile_image_large = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'placeholder': 'https://example.com/profile-large.jpg'
    }), help_text="URL for large profile image (300x300px)")

class TemplateSelectionForm(forms.Form):
    template = forms.ChoiceField(
        choices=[(template['id'], template['name']) for template in PORTFOLIO_TEMPLATES],
        widget=forms.RadioSelect(attrs={'class': 'template-radio'})
    )

