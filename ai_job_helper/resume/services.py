import os
import subprocess
import tempfile
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Resume

def compile_latex_resume(resume):
    """
    Compile resume data into LaTeX and generate PDF
    """
    try:
        # Get resume data
        personal_info = getattr(resume, 'personal_info', None)
        educations = resume.educations.all()
        experiences = resume.experiences.all()
        skills = resume.skills.all()
        projects = resume.projects.all()
        certifications = resume.certifications.all()
        additional_sections = resume.additional_sections.all()
        
        # Generate LaTeX content
        latex_content = generate_latex_content(
            personal_info, educations, experiences, 
            skills, projects, certifications, additional_sections
        )
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX file
            tex_file = os.path.join(temp_dir, 'resume.tex')
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Compile LaTeX to PDF
            try:
                subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', temp_dir,
                    tex_file
                ], check=True, capture_output=True, cwd=temp_dir)
                
                # Move PDF to media directory
                pdf_path = os.path.join(temp_dir, 'resume.pdf')
                if os.path.exists(pdf_path):
                    # Save to media directory
                    with open(pdf_path, 'rb') as f:
                        saved_path = default_storage.save(
                            f'resumes/{resume.user.username}_resume_{resume._id}.pdf',
                            f
                        )
                    
                    return default_storage.url(saved_path)
                else:
                    raise Exception("PDF compilation failed")
                    
            except subprocess.CalledProcessError as e:
                raise Exception(f"LaTeX compilation error: {e.stderr.decode()}")
            except FileNotFoundError:
                raise Exception("pdflatex not found. Please install LaTeX.")
    
    except Exception as e:
        raise Exception(f"Resume compilation failed: {str(e)}")

def generate_latex_content(personal_info, educations, experiences, skills, projects, certifications, additional_sections):
    """
    Generate LaTeX content for the resume
    """
    latex_template = r"""
\documentclass[11pt,a4paper,sans]{moderncv}

% modern themes
\moderncvstyle{classic}
\moderncvcolor{blue}

% character encoding
\usepackage[utf8]{inputenc}

% adjust the page margins
\usepackage[scale=0.75]{geometry}

% personal data
\name{%s}{%s}
\title{%s}
\address{%s}
\phone[mobile]{%s}
\email{%s}
%s%s%s

\begin{document}

\makecvtitle

%s

%s

%s

%s

%s

%s

\end{document}
"""
    
    # Personal info
    first_name = personal_info.first_name if personal_info else ""
    last_name = personal_info.last_name if personal_info else ""
    job_title = personal_info.job_title if personal_info else ""
    address = personal_info.address if personal_info else ""
    phone = personal_info.phone if personal_info else ""
    email = personal_info.email if personal_info else ""
    
    # Social links
    linkedin = ""
    github = ""
    website = ""
    if personal_info:
        if personal_info.linkedin_url:
            linkedin = f"\\social[linkedin]{{{personal_info.linkedin_url}}}"
        if personal_info.github_url:
            github = f"\\social[github]{{{personal_info.github_url}}}"
        if personal_info.website_url:
            website = f"\\social[homepage]{{{personal_info.website_url}}}"
    
    # Education section
    education_section = ""
    if educations:
        education_section = "\\section{Education}\n"
        for edu in educations:
            gpa_text = ""
            if edu.gpa:
                gpa_text = f" (GPA: {edu.gpa}/{edu.gpa_scale})"
            
            education_section += f"\\cventry{{{edu.start_month} {edu.start_year} -- {edu.grad_month} {edu.grad_year}}}{{{edu.degree_type} in {edu.field_of_study}}}{{{edu.institution}}}{{{edu.location}}}{{}}{{{edu.description or ''}{gpa_text}}}\n"
    
    # Experience section
    experience_section = ""
    if experiences:
        experience_section = "\\section{Experience}\n"
        for exp in experiences:
            end_date = "Present" if exp.is_current else f"{exp.end_month} {exp.end_year}"
            experience_section += f"\\cventry{{{exp.start_month} {exp.start_year} -- {end_date}}}{{{exp.position}}}{{{exp.company}}}{{{exp.location}}}{{}}{{{exp.description}}}\n"
    
    # Skills section
    skills_section = ""
    if skills:
        skills_section = "\\section{Skills}\n"
        # Group skills by category
        skill_categories = {}
        for skill in skills:
            if skill.category not in skill_categories:
                skill_categories[skill.category] = []
            skill_categories[skill.category].append(skill.name)
        
        for category, skill_list in skill_categories.items():
            skills_section += f"\\cvitem{{{category.title()}}}{{{', '.join(skill_list)}}}\n"
    
    # Projects section
    projects_section = ""
    if projects:
        projects_section = "\\section{Projects}\n"
        for proj in projects:
            end_date = "Present" if proj.is_ongoing else f"{proj.end_month} {proj.end_year}"
            projects_section += f"\\cventry{{{proj.start_month} {proj.start_year} -- {end_date}}}{{{proj.name}}}{{{proj.technologies}}}{{}}{{}}{{{proj.description}}}\n"
    
    # Certifications section
    certifications_section = ""
    if certifications:
        certifications_section = "\\section{Certifications}\n"
        for cert in certifications:
            certifications_section += f"\\cvitem{{{cert.name}}}{{{cert.issuer} -- {cert.issue_date} {cert.issue_year}}}\n"
    
    # Additional sections
    additional_sections_content = ""
    if additional_sections:
        for section in additional_sections:
            additional_sections_content += f"\\section{{{section.title}}}\n"
            additional_sections_content += f"\\cvitem{{}}{{section.content}}\n"
    
    return latex_template % (
        first_name, last_name, job_title, address, phone, email,
        linkedin, github, website,
        education_section, experience_section, skills_section, 
        projects_section, certifications_section, additional_sections_content
    )
