import os
from django.template.loader import render_to_string
from ai_agents.ai_service import AIService

class PortfolioGenerator:
    """Generates portfolio HTML from data and template using AI agents"""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'portfolio', 'templates')
        self.ai_service = AIService()
    
    def generate_portfolio(self, portfolio_data, template_id):
        """Generate portfolio HTML based on selected template id"""
        if template_id in ('template1', 'template2', 'template3'):
            template_map = {
                'template1': 'portfolio/template-1.html',
                'template2': 'portfolio/template-2.html',
                'template3': 'portfolio/template-3.html',
            }
            return render_to_string(template_map[template_id], {
                'portfolio': portfolio_data,
                'sample': True,
            })
        # Backward compatibility with previous ids
        if template_id == 'creative':
            return self._generate_creative_portfolio(portfolio_data)
        elif template_id == 'minimal':
            return self._generate_minimal_portfolio(portfolio_data)
        elif template_id == 'professional':
            return self._generate_professional_portfolio(portfolio_data)
        return render_to_string('portfolio/template-1.html', {
            'portfolio': portfolio_data,
            'sample': True,
        })
    
    def _generate_creative_portfolio(self, data):
        """Generate the creative portfolio template (Angie's style) using AI"""
        # Enhance data using AI
        enhanced_data = self.ai_service.generate_portfolio_content(data, 'creative')
        
        if enhanced_data:
            # Use AI-enhanced data
            personal_info = data['personalInfo'].copy()
            personal_info['bio'] = enhanced_data.get('enhanced_bio', personal_info.get('bio', ''))
            
            # Enhance projects with AI
            projects = []
            for i, project in enumerate(data['projects']):
                enhanced_project = project.copy()
                if i < len(enhanced_data.get('projects', [])):
                    ai_project = enhanced_data['projects'][i]
                    enhanced_project['description'] = ai_project.get('description', project.get('description', ''))
                    enhanced_project['achievements'] = ai_project.get('achievements', '')
                projects.append(enhanced_project)
            
            # Enhance experience with AI
            experience = []
            for i, exp in enumerate(data['experience']):
                enhanced_exp = exp.copy()
                if i < len(enhanced_data.get('experience', [])):
                    ai_exp = enhanced_data['experience'][i]
                    enhanced_exp['description'] = ai_exp.get('description', exp.get('description', ''))
                    enhanced_exp['achievements'] = ai_exp.get('achievements', '')
                experience.append(enhanced_exp)
        else:
            # Fallback to original data
            personal_info = data['personalInfo']
            experience = data['experience']
            projects = data['projects']
        
        # Generate project images with placeholders
        for i, project in enumerate(projects):
            if not project.get('image'):
                project['image'] = f"https://placehold.co/600x400/eeeeee/4A4A4A?text={project['title'].replace(' ', '+')}"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personal_info['name']} - Creative Portfolio</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts: Poppins -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">

    <!-- Custom Styles -->
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            background-color: #F5F5F5;
            color: #4A4A4A;
            overflow: hidden; /* Prevent body scroll */
        }}
        
        /* Main Layout */
        .main-container {{
            display: flex;
            height: 100vh;
            width: 100vw;
        }}

        #left-panel {{
            width: 120px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #FFFFFF;
            box-shadow: 4px 0 10px rgba(0,0,0,0.05);
            z-index: 20;
        }}

        #right-panel {{
            flex-grow: 1;
            height: 100vh;
            overflow-y: scroll;
            scroll-behavior: smooth;
        }}
        
        /* Custom Scrollbar for Right Panel */
        #right-panel::-webkit-scrollbar {{ width: 5px; }}
        #right-panel::-webkit-scrollbar-track {{ background: #EAEAEA; }}
        #right-panel::-webkit-scrollbar-thumb {{
            background: #C4459B;
            border-radius: 5px;
        }}
        #right-panel::-webkit-scrollbar-thumb:hover {{ background: #a83c84; }}

        /* Circular Navigation */
        .circular-nav {{
            position: relative;
            width: 70px;
            height: 70px;
        }}

        .nav-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background-color: #C4459B;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        }}

        .nav-center img {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
        }}

        .circular-nav-items {{
            list-style: none;
            padding: 0;
            margin: 0;
            width: 100%;
            height: 100%;
        }}

        .circular-nav-items li {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 40px;
            height: 40px;
            margin: -20px;
            transform-origin: center center;
            transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            opacity: 0;
        }}
        
        .circular-nav:hover .circular-nav-items li {{
            opacity: 1;
        }}

        .circular-nav-items a {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #FFFFFF;
            color: #4A4A4A;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: background-color 0.3s, color 0.3s;
            text-decoration: none;
        }}

        .circular-nav-items a:hover,
        .circular-nav-items a.active {{
            background-color: #C4459B;
            color: #FFFFFF;
        }}

        /* Hero Section Gradient Background */
        #home {{
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }}

        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .section-title {{
            position: relative;
            display: inline-block;
            padding-bottom: 0.5rem;
            font-weight: 700;
            font-size: 2.25rem;
        }}
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 50%;
            height: 4px;
            background-color: #C4459B;
            border-radius: 2px;
        }}
        
        /* Project Card Overlay */
        .project-card .overlay {{
            opacity: 0;
            transition: opacity 0.4s ease;
        }}
        .project-card:hover .overlay {{
            opacity: 1;
        }}

        /* Experience Timeline */
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -31px;
            top: 8px;
            width: 14px;
            height: 14px;
            border: 2px solid #C4459B;
            background-color: #F5F5F5;
            border-radius: 50%;
            z-index: 1;
        }}

        /* Modal Styles */
        .modal {{ transition: opacity 0.3s ease; }}
        .modal-content {{ transition: transform 0.3s ease; }}
    </style>
</head>
<body>

    <div class="main-container">
        <!-- Left Panel: Navigation -->
        <div id="left-panel">
            <nav class="circular-nav">
                <div class="nav-center">
                    <img id="nav-profile-pic" src="{personal_info['profileImageSmall']}" alt="Profile Picture">
                </div>
                <ul class="circular-nav-items">
                    <!-- Nav items will be injected by JS -->
                </ul>
            </nav>
        </div>

        <!-- Right Panel: Content -->
        <div id="right-panel">
            <main>
                <!-- Home Section -->
                <section id="home" class="h-screen w-full flex flex-col items-center justify-center text-white text-center p-4">
                    <h1 class="text-6xl md:text-8xl font-bold uppercase tracking-wider">{personal_info['name']}</h1>
                    <p class="text-xl md:text-2xl mt-4">I am a <span id="hero-title" class="font-semibold"></span></p>
                </section>

                <!-- About Section -->
                <section id="about" class="min-h-screen w-full flex items-center justify-center py-20 px-6">
                    <div class="max-w-4xl w-full">
                        <h2 class="section-title mb-12">About Me</h2>
                        <div class="flex flex-col md:flex-row items-center gap-12">
                            <img id="about-profile-pic" src="{personal_info['profileImageLarge']}" alt="Profile" class="w-48 h-48 md:w-64 md:h-64 rounded-full object-cover shadow-lg">
                            <p id="about-bio" class="text-lg text-gray-600 leading-relaxed">{personal_info['bio']}</p>
                        </div>
                    </div>
                </section>

                <!-- Experience Section -->
                <section id="experience" class="min-h-screen w-full flex items-center justify-center py-20 px-6 bg-white">
                    <div class="max-w-4xl w-full">
                        <h2 class="section-title mb-16">My Experience</h2>
                        <div id="experience-container" class="relative border-l-2 border-gray-200 pl-8 space-y-12">
                            {self._generate_experience_html(experience)}
                        </div>
                    </div>
                </section>

                <!-- Projects Section -->
                <section id="projects" class="min-h-screen w-full flex items-center justify-center py-20 px-6">
                    <div class="max-w-6xl w-full">
                         <h2 class="section-title mb-12">My Portfolio</h2>
                         <div id="projects-container" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                            {self._generate_projects_html(projects)}
                         </div>
                    </div>
                </section>

                <!-- Contact Section -->
                <section id="contact" class="min-h-screen w-full flex items-center justify-center py-20 px-6 bg-white">
                    <div class="max-w-4xl w-full text-center">
                        <h2 class="section-title mb-8 mx-auto">Get In Touch</h2>
                        <p class="max-w-2xl mx-auto mb-8 text-gray-500">
                           Have a project in mind or just want to say hello? My inbox is always open.
                        </p>
                        <a id="contact-email" href="mailto:{personal_info['contact']['email']}" class="inline-block bg-[#C4459B] text-white px-8 py-3 rounded-full font-semibold tracking-wide hover:bg-[#a83c84] transition-colors duration-300 shadow-lg">
                           Contact Me
                        </a>
                        <div id="social-links-container" class="flex justify-center space-x-6 mt-12 text-2xl text-gray-500">
                            {self._generate_social_links_html(personal_info['socials'])}
                        </div>
                    </div>
                </section>
                
                <footer class="text-center py-6 text-sm text-gray-400">
                    <p>&copy; {self._get_current_year()} {personal_info['name']}. All Rights Reserved.</p>
                </footer>
            </main>
        </div>
    </div>

    <!-- Project Modal -->
    <div id="project-modal" class="modal fixed inset-0 bg-black/70 flex items-center justify-center p-4 opacity-0 pointer-events-none z-50">
        <div class="modal-content bg-white max-w-3xl w-full rounded-lg relative transform scale-95 overflow-hidden">
            <button id="close-modal" class="absolute top-3 right-4 text-gray-500 hover:text-[#C4459B] text-3xl z-10">&times;</button>
            <div class="grid md:grid-cols-2">
                <img id="modal-image" src="https://placehold.co/600x800/eeeeee/4A4A4A?text=Project" alt="Project Image" class="w-full h-full object-cover">
                <div class="p-8">
                    <h3 id="modal-title" class="text-3xl font-bold mb-2"></h3>
                    <p id="modal-description" class="text-gray-600 mb-6"></p>
                    <div class="flex space-x-4">
                        <a id="modal-live-link" href="#" target="_blank" class="bg-[#C4459B] text-white px-6 py-2 rounded-full text-sm font-semibold hover:bg-[#a83c84] transition-colors">Live Demo</a>
                        <a id="modal-repo-link" href="#" target="_blank" class="bg-gray-200 text-gray-700 px-6 py-2 rounded-full text-sm font-semibold hover:bg-gray-300 transition-colors">Source Code</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Typed.js for typing animation -->
    <script src="https://cdn.jsdelivr.net/npm/typed.js@2.0.12"></script>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{

            const navItemsData = [
                {{ id: 'home', icon: 'fa-home' }},
                {{ id: 'about', icon: 'fa-user' }},
                {{ id: 'experience', icon: 'fa-briefcase' }},
                {{ id: 'projects', icon: 'fa-layer-group' }},
                {{ id: 'contact', icon: 'fa-envelope' }}
            ];

            const navList = document.querySelector('.circular-nav-items');
            const nav = document.querySelector('.circular-nav');
            const numItems = navItemsData.length;
            const angleIncrement = 360 / numItems;

            // --- GENERATE CIRCULAR NAVIGATION ---
            navItemsData.forEach((item, index) => {{
                const angle = index * angleIncrement;
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = `#${{item.id}}`;
                a.dataset.section = item.id;
                a.innerHTML = `<i class="fas ${{item.icon}}"></i>`;
                li.appendChild(a);
                navList.appendChild(li);

                nav.addEventListener('mouseenter', () => {{
                    const radius = 90; // The distance from the center
                    const x = radius * Math.cos((angle - 90) * (Math.PI / 180));
                    const y = radius * Math.sin((angle - 90) * (Math.PI / 180));
                    li.style.transform = `translate(${{x}}px, ${{y}}px) scale(1)`;
                }});
                
                nav.addEventListener('mouseleave', () => {{
                    li.style.transform = 'translate(0, 0) scale(0)';
                }});

                a.addEventListener('click', (e) => {{
                    e.preventDefault();
                    document.getElementById(item.id).scrollIntoView({{ behavior: 'smooth' }});
                }});
            }});

            // --- PORTFOLIO DATA (Embedded to avoid fetch error) ---
            const portfolioData = {self._json_to_js(data)};

            // Directly populate the HTML with the embedded data
            populateHTML(portfolioData);

            function populateHTML(data) {{
                const {{ personalInfo, projects, experience }} = data;
                
                // Set images
                document.getElementById('nav-profile-pic').src = personalInfo.profileImageSmall;
                document.getElementById('about-profile-pic').src = personal_info.profileImageLarge;

                // Hero
                document.getElementById('hero-name').textContent = personalInfo.name;
                new Typed('#hero-title', {{
                    strings: personalInfo.titles,
                    typeSpeed: 70, backSpeed: 40, loop: true
                }});

                // About
                document.getElementById('about-bio').textContent = personalInfo.bio;

                setupModal(projects);
            }}

            // --- MODAL FUNCTIONALITY ---
            function setupModal(projects) {{
                const modal = document.getElementById('project-modal');
                const modalContent = document.querySelector('.modal-content');
                const closeModalBtn = document.getElementById('close-modal');
                
                document.querySelectorAll('.project-card').forEach(card => {{
                    card.addEventListener('click', () => {{
                        const project = projects[card.dataset.index];
                        
                        document.getElementById('modal-image').src = project.image;
                        document.getElementById('modal-title').textContent = project.title;
                        document.getElementById('modal-description').textContent = project.longDescription;
                        document.getElementById('modal-live-link').href = project.links.live;
                        document.getElementById('modal-repo-link').href = project.links.repo;

                        modal.classList.remove('opacity-0', 'pointer-events-none');
                        modalContent.classList.remove('scale-95');
                    }});
                }});

                const closeModal = () => {{
                    modal.classList.add('opacity-0', 'pointer-events-none');
                    modalContent.classList.add('scale-95');
                }};

                closeModalBtn.addEventListener('click', closeModal);
                modal.addEventListener('click', (e) => {{
                    if (e.target === modal) closeModal();
                }});
            }}

            // --- Intersection Observer for Active Nav Link ---
            const sections = document.querySelectorAll('section');
            const navLinks = document.querySelectorAll('.circular-nav-items a');

            const observer = new IntersectionObserver(entries => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        navLinks.forEach(link => {{
                            link.classList.remove('active');
                            if (link.dataset.section === entry.target.id) {{
                                link.classList.add('active');
                            }}
                        }});
                    }}
                }});
            }}, {{ root: document.getElementById('right-panel'), threshold: 0.5 }});

            sections.forEach(section => observer.observe(section));
        }});
    </script>
</body>
</html>"""
        return html_content
    
    def _generate_experience_html(self, experience):
        """Generate experience HTML"""
        html = ""
        for job in experience:
            html += f"""
                        <div class="timeline-item">
                            <h3 class="text-xl font-semibold text-[#C4459B]">{job['role']}</h3>
                            <p class="font-medium text-gray-700 mb-1">{job['company']}</p>
                            <p class="text-sm text-gray-400 mb-2">{job['duration']}</p>
                            <p class="text-gray-600">{job['description']}</p>
                        </div>"""
        return html
    
    def _generate_projects_html(self, projects):
        """Generate projects HTML"""
        html = ""
        for i, project in enumerate(projects):
            html += f"""
                        <div class="project-card relative rounded-lg overflow-hidden shadow-lg cursor-pointer group" data-index="{i}">
                            <img src="{project['image']}" alt="{project['title']}" class="w-full h-60 object-cover">
                            <div class="overlay absolute inset-0 bg-black/60 flex flex-col items-center justify-center p-4 text-white">
                                <h3 class="text-xl font-bold">{project['title']}</h3>
                                <p class="text-sm">{project['shortDescription']}</p>
                            </div>
                        </div>"""
        return html
    
    def _generate_social_links_html(self, socials):
        """Generate social links HTML"""
        html = ""
        for social in socials:
            html += f"""
                        <a href="{social['url']}" target="_blank" class="hover:text-[#C4459B] transition-colors">
                            <i class="{social['icon']}"></i>
                        </a>"""
        return html
    
    def _json_to_js(self, data):
        """Convert Python dict to JavaScript object string"""
        import json
        return json.dumps(data, indent=16)
    
    def _get_current_year(self):
        """Get current year"""
        from datetime import datetime
        return datetime.now().year
    
    def _generate_minimal_portfolio(self, data):
        """Generate minimal portfolio template"""
        # TODO: Implement minimal template
        return self._generate_creative_portfolio(data)
    
    def _generate_professional_portfolio(self, data):
        """Generate professional portfolio template"""
        # TODO: Implement professional template
        return self._generate_creative_portfolio(data)
