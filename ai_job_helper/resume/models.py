from django.db import models
from django.contrib.auth.models import User
from djongo import models as djongo_models
from bson import ObjectId

class Resume(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="My Resume")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class PersonalInfo(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    job_title = models.CharField(max_length=200)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Education(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=100)  # Bachelor's, Master's, PhD, etc.
    field_of_study = models.CharField(max_length=200)
    start_month = models.CharField(max_length=20)
    start_year = models.IntegerField()
    grad_month = models.CharField(max_length=20)
    grad_year = models.IntegerField()
    gpa = models.FloatField(blank=True, null=True)
    gpa_scale = models.CharField(max_length=20, default="4.0")
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.degree_type} in {self.field_of_study} from {self.institution}"

class Experience(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_month = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_month = models.CharField(max_length=20, blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class Skill(models.Model):
    SKILL_CATEGORIES = [
        ('technical', 'Technical Skills'),
        ('languages', 'Programming Languages'),
        ('tools', 'Tools & Technologies'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ]
    
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES, default='technical')
    proficiency = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='intermediate')
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Project(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    technologies = models.CharField(max_length=500)  # Comma-separated
    start_month = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_month = models.CharField(max_length=20, blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)
    github_url = models.URLField(blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Certification(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    issue_date = models.CharField(max_length=20)
    issue_year = models.IntegerField()
    credential_id = models.CharField(max_length=100, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} from {self.issuer}"

class AdditionalSection(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='additional_sections')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def __str__(self):
        return self.title
