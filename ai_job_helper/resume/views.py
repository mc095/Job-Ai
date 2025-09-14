from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Resume, PersonalInfo, Education, Experience, Skill, Project, Certification, AdditionalSection
from .forms import (PersonalInfoForm, EducationFormSet, ExperienceFormSet, 
                   SkillFormSet, ProjectFormSet, CertificationFormSet, AdditionalSectionFormSet)
from .services import compile_latex_resume

@login_required
def home(request):
    # Simple test - just render the template without forms for now
    context = {
        'personal_form': None,
        'education_formset': None,
        'experience_formset': None,
        'skill_formset': None,
        'project_formset': None,
        'certification_formset': None,
        'additional_formset': None,
    }
    
    return render(request, "resume/builder.html", context)

@login_required
@csrf_exempt
def save_section(request, section):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        resume, created = Resume.objects.get_or_create(user=request.user)
        data = json.loads(request.body)
        
        if section == 'personal_info':
            # Handle personal info
            if hasattr(resume, 'personal_info'):
                form = PersonalInfoForm(data, instance=resume.personal_info)
            else:
                form = PersonalInfoForm(data)
            
            if form.is_valid():
                personal_info = form.save(commit=False)
                personal_info.resume = resume
                personal_info.save()
                return JsonResponse({'success': True, 'message': 'Personal info saved'})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})
        
        elif section == 'education':
            formset = EducationFormSet(data, instance=resume, prefix='education')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Education saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        elif section == 'experience':
            formset = ExperienceFormSet(data, instance=resume, prefix='experience')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Experience saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        elif section == 'skills':
            formset = SkillFormSet(data, instance=resume, prefix='skill')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Skills saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        elif section == 'projects':
            formset = ProjectFormSet(data, instance=resume, prefix='project')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Projects saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        elif section == 'certifications':
            formset = CertificationFormSet(data, instance=resume, prefix='certification')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Certifications saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        elif section == 'additional':
            formset = AdditionalSectionFormSet(data, instance=resume, prefix='additional')
            if formset.is_valid():
                formset.save()
                return JsonResponse({'success': True, 'message': 'Additional sections saved'})
            else:
                return JsonResponse({'success': False, 'errors': formset.errors})
        
        else:
            return JsonResponse({'error': 'Invalid section'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def compile_resume(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        resume = get_object_or_404(Resume, user=request.user)
        
        # Compile LaTeX resume
        pdf_url = compile_latex_resume(resume)
        
        return JsonResponse({
            'success': True, 
            'pdf_url': pdf_url,
            'message': 'Resume compiled successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_resume_data(request):
    """Get resume data for live preview"""
    try:
        resume = get_object_or_404(Resume, user=request.user)
        
        # Get all related data
        personal_info = getattr(resume, 'personal_info', None)
        educations = resume.educations.all()
        experiences = resume.experiences.all()
        skills = resume.skills.all()
        projects = resume.projects.all()
        certifications = resume.certifications.all()
        additional_sections = resume.additional_sections.all()
        
        data = {
            'personal_info': {
                'first_name': personal_info.first_name if personal_info else '',
                'last_name': personal_info.last_name if personal_info else '',
                'email': personal_info.email if personal_info else '',
                'phone': personal_info.phone if personal_info else '',
                'address': personal_info.address if personal_info else '',
                'job_title': personal_info.job_title if personal_info else '',
                'linkedin_url': personal_info.linkedin_url if personal_info else '',
                'github_url': personal_info.github_url if personal_info else '',
                'website_url': personal_info.website_url if personal_info else '',
            } if personal_info else {},
            'educations': [{
                'institution': edu.institution,
                'location': edu.location,
                'degree_type': edu.degree_type,
                'field_of_study': edu.field_of_study,
                'start_month': edu.start_month,
                'start_year': edu.start_year,
                'grad_month': edu.grad_month,
                'grad_year': edu.grad_year,
                'gpa': edu.gpa,
                'gpa_scale': edu.gpa_scale,
                'description': edu.description,
            } for edu in educations],
            'experiences': [{
                'company': exp.company,
                'position': exp.position,
                'location': exp.location,
                'start_month': exp.start_month,
                'start_year': exp.start_year,
                'end_month': exp.end_month,
                'end_year': exp.end_year,
                'is_current': exp.is_current,
                'description': exp.description,
            } for exp in experiences],
            'skills': [{
                'name': skill.name,
                'category': skill.category,
                'proficiency': skill.proficiency,
            } for skill in skills],
            'projects': [{
                'name': proj.name,
                'description': proj.description,
                'technologies': proj.technologies,
                'start_month': proj.start_month,
                'start_year': proj.start_year,
                'end_month': proj.end_month,
                'end_year': proj.end_year,
                'is_ongoing': proj.is_ongoing,
                'github_url': proj.github_url,
                'live_url': proj.live_url,
            } for proj in projects],
            'certifications': [{
                'name': cert.name,
                'issuer': cert.issuer,
                'issue_date': cert.issue_date,
                'issue_year': cert.issue_year,
                'credential_id': cert.credential_id,
                'credential_url': cert.credential_url,
            } for cert in certifications],
            'additional_sections': [{
                'title': section.title,
                'content': section.content,
            } for section in additional_sections],
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
