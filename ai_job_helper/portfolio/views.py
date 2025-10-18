from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from bson import ObjectId
import json
from .models import Portfolio, PORTFOLIO_TEMPLATES
from .forms import PortfolioDataForm, TemplateSelectionForm
from .portfolio_generator import PortfolioGenerator

@login_required
def home(request):
    """Portfolio home page - shows user's portfolio or create option"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        if portfolio.selected_template:
            return render(request, 'portfolio/dashboard.html', {'portfolio': portfolio})
        else:
            return render(request, 'portfolio/select_template.html', {'portfolio': portfolio})
    except Portfolio.DoesNotExist:
        return render(request, 'portfolio/create.html')

@login_required
def create_portfolio(request):
    """Create a new portfolio by collecting user data"""
    if request.method == 'POST':
        form = PortfolioDataForm(request.POST)
        if form.is_valid():
            # Process form data into structured JSON
            portfolio_data = process_portfolio_data(form.cleaned_data)
            
            # Create or update portfolio
            portfolio, created = Portfolio.objects.get_or_create(
                user=request.user,
                defaults={'portfolio_data': portfolio_data}
            )
            if not created:
                portfolio.portfolio_data = portfolio_data
                portfolio.save()
            
            messages.success(request, 'Portfolio data saved! Now choose a template.')
            return redirect('select_template')
        else:
            # Surface validation errors to the user
            from django.forms.utils import ErrorDict
            err: ErrorDict = form.errors
            if err:
                messages.error(request, 'Please complete all required fields before continuing.')
    else:
        # Prefill with existing saved data if any
        try:
            existing = Portfolio.objects.get(user=request.user)
            initial_data = _flatten_portfolio_data_for_form(existing.portfolio_data)
            form = PortfolioDataForm(initial=initial_data)
        except Portfolio.DoesNotExist:
            form = PortfolioDataForm()
    
    return render(request, 'portfolio/create.html', {'form': form})

@login_required
def new_portfolio(request):
    """Start a fresh portfolio (clears existing data) and go to create form."""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        portfolio.delete()
    except Portfolio.DoesNotExist:
        pass
    messages.info(request, 'Starting a new portfolio.')
    return redirect('create_portfolio')

@login_required
def select_template(request):
    """Select portfolio template"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
    except Portfolio.DoesNotExist:
        messages.error(request, 'Please create portfolio data first.')
        return redirect('create_portfolio')
    
    if request.method == 'POST':
        form = TemplateSelectionForm(request.POST)
        if form.is_valid():
            template_id = form.cleaned_data['template']
            portfolio.selected_template = template_id
            portfolio.save()
            messages.success(request, 'Template selected! You can now download your portfolio.')
            return redirect('portfolio_dashboard')
    else:
        form = TemplateSelectionForm()
    
    return render(request, 'portfolio/select_template.html', {
        'form': form, 
        'portfolio': portfolio,
        'templates': PORTFOLIO_TEMPLATES
    })

@login_required
def portfolio_dashboard(request):
    """Portfolio dashboard with download option"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        if not portfolio.selected_template:
            return redirect('select_template')
    except Portfolio.DoesNotExist:
        messages.error(request, 'Please create a portfolio first.')
        return redirect('create_portfolio')
    
    return render(request, 'portfolio/dashboard.html', {'portfolio': portfolio})

@login_required
def download_portfolio(request):
    """Download generated portfolio code"""
    try:
        portfolio = Portfolio.objects.get(user=request.user)
        if not portfolio.selected_template:
            messages.error(request, 'Please select a template first.')
            return redirect('select_template')
        
        # Generate portfolio HTML
        generator = PortfolioGenerator()
        html_content = generator.generate_portfolio(portfolio.portfolio_data, portfolio.selected_template)
        
        # Create response
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="{portfolio.user.username}_portfolio.html"'
        return response
        
    except Portfolio.DoesNotExist:
        messages.error(request, 'Portfolio not found.')
        return redirect('create_portfolio')

def _flatten_portfolio_data_for_form(portfolio_data):
    """Convert structured portfolio JSON back to form format for editing"""
    flat_data = {}
    
    # Personal info
    personal = portfolio_data.get('personalInfo', {})
    flat_data['name'] = personal.get('name', '')
    flat_data['titles'] = '\n'.join(personal.get('titles', []))
    flat_data['bio'] = personal.get('bio', '')
    flat_data['location'] = personal.get('contact', {}).get('location', '')
    flat_data['email'] = personal.get('contact', {}).get('email', '')
    flat_data['phone'] = personal.get('contact', {}).get('phone', '')
    
    # Profile images
    flat_data['profile_image_small'] = personal.get('profileImageSmall', '')
    flat_data['profile_image_large'] = personal.get('profileImageLarge', '')
    
    # Socials
    socials = personal.get('socials', [])
    for social in socials:
        name = social.get('name', '').lower()
        if name == 'github':
            flat_data['github_url'] = social.get('url', '')
        elif name == 'linkedin':
            flat_data['linkedin_url'] = social.get('url', '')
        elif name == 'twitter':
            flat_data['twitter_url'] = social.get('url', '')
        elif name == 'website':
            flat_data['website_url'] = social.get('url', '')
    
    # Experience
    exp_lines = []
    for exp in portfolio_data.get('experience', []):
        line = f"{exp.get('company', '')} | {exp.get('role', '')} | {exp.get('duration', '')} | {exp.get('description', '')}"
        exp_lines.append(line)
    flat_data['experience'] = '\n'.join(exp_lines)
    
    # Education
    edu_lines = []
    for edu in portfolio_data.get('education', []):
        line = f"{edu.get('institution', '')} | {edu.get('degree', '')} | {edu.get('year', '')}"
        if edu.get('gpa'):
            line += f" | {edu.get('gpa')}"
        edu_lines.append(line)
    flat_data['education'] = '\n'.join(edu_lines)
    
    # Skills
    flat_data['skills'] = ', '.join(portfolio_data.get('skills', []))
    
    # Projects
    proj_lines = []
    for proj in portfolio_data.get('projects', []):
        links = proj.get('links', {})
        line = f"{proj.get('title', '')} | {proj.get('shortDescription', '')} | {proj.get('image', '')} | {links.get('live', '#')} | {links.get('repo', '#')}"
        proj_lines.append(line)
    flat_data['projects'] = '\n'.join(proj_lines)
    
    # Certifications
    cert_lines = []
    for cert in portfolio_data.get('certifications', []):
        line = f"{cert.get('name', '')} | {cert.get('issuer', '')} | {cert.get('year', '')}"
        cert_lines.append(line)
    flat_data['certifications'] = '\n'.join(cert_lines)
    
    return flat_data

def process_portfolio_data(form_data):
    """Process form data into structured JSON format"""
    # Parse titles
    titles = [title.strip() for title in form_data['titles'].split('\n') if title.strip()]
    
    # Parse experience
    experience = []
    for line in form_data['experience'].split('\n'):
        if line.strip():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 4:
                experience.append({
                    'company': parts[0],
                    'role': parts[1],
                    'duration': parts[2],
                    'description': parts[3]
                })
    
    # Parse education
    education = []
    for line in form_data['education'].split('\n'):
        if line.strip():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 3:
                education.append({
                    'institution': parts[0],
                    'degree': parts[1],
                    'year': parts[2],
                    'gpa': parts[3] if len(parts) > 3 else None
                })
    
    # Parse skills
    skills = [skill.strip() for skill in form_data['skills'].split(',') if skill.strip()]
    
    # Parse projects
    projects = []
    for line in form_data['projects'].split('\n'):
        if line.strip():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 5:
                projects.append({
                    'title': parts[0],
                    'shortDescription': parts[1],
                    'image': parts[2] if parts[2] else None,
                    'links': {
                        'live': parts[3] if parts[3] != '#' else '#',
                        'repo': parts[4] if parts[4] != '#' else '#'
                    }
                })
    
    # Parse certifications
    certifications = []
    for line in form_data['certifications'].split('\n'):
        if line.strip():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 3:
                certifications.append({
                    'name': parts[0],
                    'issuer': parts[1],
                    'year': parts[2]
                })
    
    # Build social links
    socials = []
    if form_data.get('github_url'):
        socials.append({'name': 'GitHub', 'url': form_data['github_url'], 'icon': 'fab fa-github'})
    if form_data.get('linkedin_url'):
        socials.append({'name': 'LinkedIn', 'url': form_data['linkedin_url'], 'icon': 'fab fa-linkedin-in'})
    if form_data.get('twitter_url'):
        socials.append({'name': 'Twitter', 'url': form_data['twitter_url'], 'icon': 'fab fa-twitter'})
    if form_data.get('website_url'):
        socials.append({'name': 'Website', 'url': form_data['website_url'], 'icon': 'fas fa-globe'})
    
    return {
        'personalInfo': {
            'name': form_data['name'],
            'titles': titles,
            'bio': form_data['bio'],
            'profileImageSmall': form_data.get('profile_image_small', 'https://placehold.co/60/C4459B/FFFFFF?text=' + form_data['name'][0].upper()),
            'profileImageLarge': form_data.get('profile_image_large', 'https://placehold.co/300x300/CCCCCC/4A4A4A?text=' + form_data['name']),
            'contact': {
                'email': form_data['email'],
                'phone': form_data.get('phone', ''),
                'location': form_data.get('location', '')
            },
            'socials': socials
        },
        'experience': experience,
        'education': education,
        'skills': skills,
        'projects': projects,
        'certifications': certifications
    }


