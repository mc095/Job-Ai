// Resume Builder JavaScript
class ResumeBuilder {
    constructor() {
        this.currentSection = 'personal';
        this.formData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadResumeData();
        this.setupFormValidation();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Section expand/collapse
        document.querySelectorAll('.expand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.toggleSection(e.target.dataset.section);
            });
        });

        // Entry expand/collapse
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.toggleEntry(e.target.closest('.entry-content'));
            });
        });

        // Add entry buttons
        document.querySelectorAll('.add-entry-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.addEntry(e.target.dataset.section);
            });
        });

        // Delete entry buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-btn')) {
                this.deleteEntry(e.target);
            }
        });

        // Form auto-save
        document.querySelectorAll('.resume-form input, .resume-form textarea, .resume-form select').forEach(input => {
            input.addEventListener('input', (e) => {
                this.debounce(() => this.saveFormData(e.target.closest('form')), 1000)();
            });
        });

        // Preview controls
        document.getElementById('refresh-preview')?.addEventListener('click', () => {
            this.updatePreview();
        });

        document.getElementById('compile-resume')?.addEventListener('click', () => {
            this.compileResume();
        });

        // Add link functionality
        document.querySelector('.add-link-btn')?.addEventListener('click', () => {
            this.addLink();
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update content based on tab
        if (tabName === 'personal') {
            this.currentSection = 'personal';
        } else if (tabName === 'matcher') {
            this.currentSection = 'matcher';
            // TODO: Implement resume matcher functionality
        }
    }

    toggleSection(sectionName) {
        const section = document.getElementById(`${sectionName}-section`);
        const content = section.querySelector('.section-content');
        const btn = section.querySelector('.expand-btn');

        content.classList.toggle('expanded');
        btn.textContent = content.classList.contains('expanded') ? '▼' : '▲';
    }

    toggleEntry(entryContent) {
        entryContent.classList.toggle('expanded');
        const btn = entryContent.previousElementSibling.querySelector('.toggle-btn');
        btn.textContent = entryContent.classList.contains('expanded') ? '▼' : '▲';
    }

    addEntry(sectionType) {
        const container = document.querySelector(`.${sectionType}-entries`);
        const form = document.getElementById(`${sectionType}-form`);
        const formIndex = container.children.length;

        // Create new entry HTML
        const entryHTML = this.generateEntryHTML(sectionType, formIndex);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = entryHTML;
        
        const newEntry = tempDiv.firstElementChild;
        container.appendChild(newEntry);

        // Add event listeners to new entry
        this.setupEntryEventListeners(newEntry);

        // Expand the new entry
        const entryContent = newEntry.querySelector('.entry-content');
        entryContent.classList.add('expanded');
        newEntry.querySelector('.toggle-btn').textContent = '▼';

        // Focus on first input
        const firstInput = newEntry.querySelector('input, textarea, select');
        if (firstInput) firstInput.focus();
    }

    generateEntryHTML(sectionType, formIndex) {
        const templates = {
            education: `
                <div class="education-entry" data-form-index="${formIndex}">
                    <div class="entry-header">
                        <span class="entry-title">Institute Name</span>
                        <div class="entry-controls">
                            <button type="button" class="move-btn">⋮⋮</button>
                            <button type="button" class="delete-btn">🗑️</button>
                            <button type="button" class="toggle-btn">▲</button>
                        </div>
                    </div>
                    <div class="entry-content">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Institution</label>
                                <input type="text" name="education-${formIndex}-institution" class="form-control" placeholder="Institution Name">
                            </div>
                            <div class="form-group">
                                <label>Location</label>
                                <input type="text" name="education-${formIndex}-location" class="form-control" placeholder="Location">
                            </div>
                            <div class="form-group">
                                <label>Degree Type</label>
                                <input type="text" name="education-${formIndex}-degree_type" class="form-control" placeholder="Degree Type">
                            </div>
                            <div class="form-group">
                                <label>Field of Study</label>
                                <input type="text" name="education-${formIndex}-field_of_study" class="form-control" placeholder="Field of Study">
                            </div>
                            <div class="form-group">
                                <label>Start Month / Year</label>
                                <div class="date-inputs">
                                    <input type="text" name="education-${formIndex}-start_month" class="form-control" placeholder="Start Month">
                                    <input type="number" name="education-${formIndex}-start_year" class="form-control" placeholder="Start Year">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Grad Month / Year</label>
                                <div class="date-inputs">
                                    <input type="text" name="education-${formIndex}-grad_month" class="form-control" placeholder="Graduation Month">
                                    <input type="number" name="education-${formIndex}-grad_year" class="form-control" placeholder="Graduation Year">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Scores</label>
                                <div class="score-inputs">
                                    <input type="text" name="education-${formIndex}-gpa_scale" class="form-control" placeholder="GPA Scale" value="4.0">
                                    <input type="number" name="education-${formIndex}-gpa" class="form-control" placeholder="GPA" step="0.01">
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="education-${formIndex}-description" class="form-control" rows="3" placeholder="Description"></textarea>
                        </div>
                    </div>
                </div>
            `,
            experience: `
                <div class="experience-entry" data-form-index="${formIndex}">
                    <div class="entry-header">
                        <span class="entry-title">Experience Entry</span>
                        <div class="entry-controls">
                            <button type="button" class="move-btn">⋮⋮</button>
                            <button type="button" class="delete-btn">🗑️</button>
                            <button type="button" class="toggle-btn">▲</button>
                        </div>
                    </div>
                    <div class="entry-content">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Company</label>
                                <input type="text" name="experience-${formIndex}-company" class="form-control" placeholder="Company Name">
                            </div>
                            <div class="form-group">
                                <label>Position</label>
                                <input type="text" name="experience-${formIndex}-position" class="form-control" placeholder="Position Title">
                            </div>
                            <div class="form-group">
                                <label>Location</label>
                                <input type="text" name="experience-${formIndex}-location" class="form-control" placeholder="Location">
                            </div>
                            <div class="form-group">
                                <label>Start Date</label>
                                <div class="date-inputs">
                                    <input type="text" name="experience-${formIndex}-start_month" class="form-control" placeholder="Start Month">
                                    <input type="number" name="experience-${formIndex}-start_year" class="form-control" placeholder="Start Year">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>End Date</label>
                                <div class="date-inputs">
                                    <input type="text" name="experience-${formIndex}-end_month" class="form-control" placeholder="End Month">
                                    <input type="number" name="experience-${formIndex}-end_year" class="form-control" placeholder="End Year">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="experience-${formIndex}-is_current" class="form-check-input">
                                    Current Position
                                </label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="experience-${formIndex}-description" class="form-control" rows="4" placeholder="Job Description"></textarea>
                        </div>
                    </div>
                </div>
            `,
            skills: `
                <div class="skill-entry" data-form-index="${formIndex}">
                    <div class="entry-header">
                        <span class="entry-title">Skill Entry</span>
                        <div class="entry-controls">
                            <button type="button" class="move-btn">⋮⋮</button>
                            <button type="button" class="delete-btn">🗑️</button>
                            <button type="button" class="toggle-btn">▲</button>
                        </div>
                    </div>
                    <div class="entry-content">
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Skill Name</label>
                                <input type="text" name="skill-${formIndex}-name" class="form-control" placeholder="Skill Name">
                            </div>
                            <div class="form-group">
                                <label>Category</label>
                                <select name="skill-${formIndex}-category" class="form-control">
                                    <option value="technical">Technical Skills</option>
                                    <option value="languages">Programming Languages</option>
                                    <option value="tools">Tools & Technologies</option>
                                    <option value="soft">Soft Skills</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Proficiency</label>
                                <select name="skill-${formIndex}-proficiency" class="form-control">
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                    <option value="expert">Expert</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            `
        };

        return templates[sectionType] || '';
    }

    setupEntryEventListeners(entry) {
        // Toggle button
        const toggleBtn = entry.querySelector('.toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleEntry(entry.querySelector('.entry-content'));
            });
        }

        // Delete button
        const deleteBtn = entry.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.deleteEntry(deleteBtn);
            });
        }

        // Form inputs
        entry.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('input', () => {
                this.debounce(() => this.saveFormData(input.closest('form')), 1000)();
            });
        });
    }

    deleteEntry(deleteBtn) {
        if (confirm('Are you sure you want to delete this entry?')) {
            const entry = deleteBtn.closest('.education-entry, .experience-entry, .skill-entry, .project-entry, .certification-entry, .additional-entry');
            entry.remove();
            this.updatePreview();
        }
    }

    addLink() {
        const container = document.querySelector('.links-container');
        const linkCount = container.children.length;
        
        if (linkCount < 5) {
            const linkHTML = `
                <div class="link-item">
                    <input type="url" placeholder="Link URL" class="form-control">
                    <button type="button" class="delete-btn">🗑️</button>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', linkHTML);
            
            // Add delete functionality to new link
            const newLink = container.lastElementChild;
            newLink.querySelector('.delete-btn').addEventListener('click', () => {
                newLink.remove();
                this.updateLinkCount();
            });
            
            this.updateLinkCount();
        }
    }

    updateLinkCount() {
        const count = document.querySelectorAll('.links-container .link-item').length;
        document.querySelector('.links-section label').textContent = `Links (${count}/5)`;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    saveFormData(form) {
        const formData = new FormData(form);
        const section = form.id.replace('-form', '');
        
        // Convert FormData to object
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Send to server
        fetch(`/resume/save/${section}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updatePreview();
            } else {
                console.error('Save failed:', data.errors);
            }
        })
        .catch(error => {
            console.error('Error saving form:', error);
        });
    }

    loadResumeData() {
        fetch('/resume/data/')
            .then(response => response.json())
            .then(data => {
                this.formData = data;
                this.updatePreview();
            })
            .catch(error => {
                console.error('Error loading resume data:', error);
            });
    }

    updatePreview() {
        const preview = document.getElementById('resume-preview');
        const personalInfo = this.formData.personal_info || {};
        
        let html = `
            <div class="resume-header">
                <h1>${personalInfo.first_name || ''} ${personalInfo.last_name || ''}</h1>
                <div class="contact-info">
                    ${personalInfo.email ? `<div>${personalInfo.email}</div>` : ''}
                    ${personalInfo.phone ? `<div>${personalInfo.phone}</div>` : ''}
                    ${personalInfo.address ? `<div>${personalInfo.address}</div>` : ''}
                </div>
            </div>
        `;

        // Education section
        if (this.formData.educations && this.formData.educations.length > 0) {
            html += '<div class="section"><div class="section-title">EDUCATION</div>';
            this.formData.educations.forEach(edu => {
                if (edu.institution) {
                    html += `
                        <div class="entry">
                            <div class="entry-header">
                                <div class="entry-title">${edu.degree_type} in ${edu.field_of_study}</div>
                                <div class="entry-subtitle">${edu.institution}, ${edu.location}</div>
                                <div class="entry-date">${edu.start_month} ${edu.start_year} - ${edu.grad_month} ${edu.grad_year}</div>
                            </div>
                            ${edu.description ? `<div class="entry-description">${edu.description}</div>` : ''}
                        </div>
                    `;
                }
            });
            html += '</div>';
        }

        // Experience section
        if (this.formData.experiences && this.formData.experiences.length > 0) {
            html += '<div class="section"><div class="section-title">EXPERIENCE</div>';
            this.formData.experiences.forEach(exp => {
                if (exp.company) {
                    const endDate = exp.is_current ? 'Present' : `${exp.end_month} ${exp.end_year}`;
                    html += `
                        <div class="entry">
                            <div class="entry-header">
                                <div class="entry-title">${exp.position}</div>
                                <div class="entry-subtitle">${exp.company}, ${exp.location}</div>
                                <div class="entry-date">${exp.start_month} ${exp.start_year} - ${endDate}</div>
                            </div>
                            <div class="entry-description">${exp.description}</div>
                        </div>
                    `;
                }
            });
            html += '</div>';
        }

        // Skills section
        if (this.formData.skills && this.formData.skills.length > 0) {
            html += '<div class="section"><div class="section-title">SKILLS</div>';
            const skillCategories = {};
            this.formData.skills.forEach(skill => {
                if (skill.name) {
                    if (!skillCategories[skill.category]) {
                        skillCategories[skill.category] = [];
                    }
                    skillCategories[skill.category].push(skill.name);
                }
            });
            
            Object.keys(skillCategories).forEach(category => {
                html += `<div class="entry"><strong>${category}:</strong> ${skillCategories[category].join(', ')}</div>`;
            });
            html += '</div>';
        }

        preview.innerHTML = html;
    }

    compileResume() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'flex';

        fetch('/resume/compile/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            overlay.style.display = 'none';
            if (data.success) {
                // Open PDF in new tab
                window.open(data.pdf_url, '_blank');
            } else {
                alert('Error compiling resume: ' + data.error);
            }
        })
        .catch(error => {
            overlay.style.display = 'none';
            console.error('Error compiling resume:', error);
            alert('Error compiling resume. Please try again.');
        });
    }

    setupFormValidation() {
        // Add real-time validation
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        
        // Remove existing error styling
        field.classList.remove('error');
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Basic validation rules
        if (field.required && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }

        if (field.type === 'email' && value && !this.isValidEmail(value)) {
            this.showFieldError(field, 'Please enter a valid email address');
            return false;
        }

        if (field.type === 'url' && value && !this.isValidURL(value)) {
            this.showFieldError(field, 'Please enter a valid URL');
            return false;
        }

        return true;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize the resume builder when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResumeBuilder();
});

