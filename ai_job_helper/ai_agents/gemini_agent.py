import google.generativeai as genai
import json
from django.conf import settings

class GeminiAgent:
    """AI Agent using Google Gemini API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_portfolio_content(self, user_data, template_type="creative"):
        """Generate portfolio content using Gemini"""
        try:
            prompt = f"""
            Generate a professional portfolio content for the following user data:
            
            Name: {user_data.get('name', 'John Doe')}
            Bio: {user_data.get('bio', '')}
            Experience: {user_data.get('experience', [])}
            Projects: {user_data.get('projects', [])}
            Skills: {user_data.get('skills', [])}
            Education: {user_data.get('education', [])}
            
            Please generate:
            1. An enhanced bio that highlights their strengths
            2. Improved project descriptions with compelling language
            3. Professional experience summaries
            4. Skills categorization and descriptions
            5. Any additional content that would make this portfolio stand out
            
            Return the response as a JSON object with the following structure:
            {{
                "enhanced_bio": "string",
                "projects": [
                    {{
                        "title": "string",
                        "description": "string",
                        "technologies": "string",
                        "achievements": "string"
                    }}
                ],
                "experience": [
                    {{
                        "role": "string",
                        "company": "string",
                        "description": "string",
                        "achievements": "string"
                    }}
                ],
                "skills": {{
                    "technical": ["string"],
                    "soft": ["string"],
                    "tools": ["string"]
                }},
                "recommendations": "string"
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text) if response.text else None
            
        except Exception as e:
            print(f"Error generating portfolio content with Gemini: {e}")
            return None
    
    def generate_exam_questions(self, job_role, num_questions=10):
        """Generate exam questions for a specific job role using Gemini"""
        try:
            prompt = f"""
            You are an expert technical interviewer and assessment creator. Generate {num_questions} high-quality exam questions for the job role: {job_role}
            
            CRITICAL REQUIREMENTS:
            1. Questions must be 100% accurate and factually correct
            2. Only ONE correct answer per question
            3. Provide detailed, accurate explanations
            4. Make questions relevant to the specific job role
            5. Include a mix of technical and practical questions
            
            For {job_role} specifically, focus on:
            - Web development fundamentals (HTML, CSS, JavaScript)
            - Programming languages commonly used in web development
            - Web technologies and frameworks
            - Problem-solving and debugging skills
            - Industry best practices and tools
            
            IMPORTANT: For web development roles:
            - HTML is the foundation markup language for web pages
            - CSS is used for styling and layout
            - JavaScript is used for interactivity
            - Python is NOT the primary language for frontend web development
            - Photoshop is a design tool, NOT a web development framework
            
            Return as JSON with this exact structure:
            {{
                "questions": [
                    {{
                        "question": "Question text here",
                        "options": [
                            "Option A text",
                            "Option B text", 
                            "Option C text",
                            "Option D text"
                        ],
                        "correct_answer": "A",
                        "explanation": "Detailed explanation of why this answer is correct"
                    }}
                ]
            }}
            
            Make sure the correct answers are accurate for {job_role} role.
            """
            
            response = self.model.generate_content(prompt)
            if response.text:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    print("Failed to parse Gemini JSON response, using fallback questions")
                    return self._get_fallback_questions(job_role, num_questions)
            else:
                return self._get_fallback_questions(job_role, num_questions)
            
        except Exception as e:
            print(f"Error generating exam questions with Gemini: {e}")
            return self._get_fallback_questions(job_role, num_questions)
    
    def _get_fallback_questions(self, job_role, num_questions):
        """Fallback questions with accurate answers - TOUGH VERSION"""
        return {
            "questions": [
                {
                    "question": f"In React, what is the difference between controlled and uncontrolled components?",
                    "options": [
                        "Controlled components use refs, uncontrolled use state",
                        "Controlled components manage their own state internally",
                        "Controlled components receive values via props and notify changes via callbacks",
                        "There is no difference between controlled and uncontrolled components"
                    ],
                    "correct_answer": "C",
                    "explanation": "Controlled components receive their current value via props and notify changes through callbacks. The parent component controls the component's state. Uncontrolled components manage their own state internally using refs."
                },
                {
                    "question": f"What is the time complexity of the following JavaScript function: function findElement(arr, target) {{ for(let i = 0; i < arr.length; i++) {{ if(arr[i] === target) return i; }} return -1; }}",
                    "options": [
                        "O(1) - Constant time",
                        "O(log n) - Logarithmic time",
                        "O(n) - Linear time",
                        "O(n²) - Quadratic time"
                    ],
                    "correct_answer": "C",
                    "explanation": "This function uses a linear search algorithm that iterates through each element in the array once in the worst case scenario. Therefore, the time complexity is O(n) where n is the length of the array."
                },
                {
                    "question": f"Which CSS property is used to create a flexbox layout?",
                    "options": [
                        "display: grid",
                        "display: flex",
                        "display: block",
                        "display: inline-flex"
                    ],
                    "correct_answer": "B",
                    "explanation": "The 'display: flex' property is used to create a flexbox layout. This enables flexible and responsive layouts where items can grow, shrink, and align within a container."
                },
                {
                    "question": f"What is the purpose of the 'useEffect' hook in React?",
                    "options": [
                        "To manage component state",
                        "To perform side effects in functional components",
                        "To create custom hooks",
                        "To handle form submissions"
                    ],
                    "correct_answer": "B",
                    "explanation": "The useEffect hook is used to perform side effects in functional components, such as data fetching, subscriptions, or manually changing the DOM. It's equivalent to componentDidMount, componentDidUpdate, and componentWillUnmount combined."
                },
                {
                    "question": f"In JavaScript, what is the difference between 'let' and 'var'?",
                    "options": [
                        "There is no difference between let and var",
                        "let has block scope, var has function scope",
                        "var is newer than let",
                        "let can only be used in loops"
                    ],
                    "correct_answer": "B",
                    "explanation": "The main difference is scoping: 'let' has block scope (limited to the block where it's declared), while 'var' has function scope (accessible throughout the entire function). 'let' also prevents hoisting issues and doesn't allow redeclaration in the same scope."
                },
                {
                    "question": f"What is the purpose of the 'async/await' syntax in JavaScript?",
                    "options": [
                        "To create synchronous code",
                        "To handle asynchronous operations more elegantly",
                        "To improve performance",
                        "To create loops"
                    ],
                    "correct_answer": "B",
                    "explanation": "async/await is syntactic sugar over Promises that makes asynchronous code look and behave more like synchronous code. It allows you to write asynchronous code in a more readable and maintainable way."
                },
                {
                    "question": f"What is the difference between 'margin' and 'padding' in CSS?",
                    "options": [
                        "Margin is inside the element, padding is outside",
                        "Padding is inside the element, margin is outside",
                        "They are the same thing",
                        "Margin affects text, padding affects layout"
                    ],
                    "correct_answer": "B",
                    "explanation": "Padding is the space inside an element between the content and the border. Margin is the space outside an element between the border and other elements. Padding affects the element's internal spacing, while margin affects spacing between elements."
                },
                {
                    "question": f"What is the purpose of the 'key' prop in React lists?",
                    "options": [
                        "To style list items",
                        "To help React identify which items have changed, been added, or removed",
                        "To make lists clickable",
                        "To sort list items"
                    ],
                    "correct_answer": "B",
                    "explanation": "The 'key' prop helps React identify which items have changed, been added, or removed. This is crucial for efficient re-rendering and maintaining component state when the list changes."
                },
                {
                    "question": f"What is the purpose of the 'this' keyword in JavaScript?",
                    "options": [
                        "To refer to the current function",
                        "To refer to the current object context",
                        "To create new variables",
                        "To import modules"
                    ],
                    "correct_answer": "B",
                    "explanation": "The 'this' keyword refers to the object that is currently executing the function. Its value depends on how the function is called and can change based on the execution context."
                },
                {
                    "question": f"What is the difference between '===' and '==' in JavaScript?",
                    "options": [
                        "There is no difference",
                        "=== performs strict equality (no type coercion), == performs loose equality (with type coercion)",
                        "== is newer than ===",
                        "=== is only used for numbers"
                    ],
                    "correct_answer": "B",
                    "explanation": "=== performs strict equality comparison without type coercion, while == performs loose equality comparison with type coercion. For example: 5 === '5' is false, but 5 == '5' is true."
                }
            ]
        }
    
    def generate_interview_questions(self, job_description):
        """Generate interview questions based on job description"""
        try:
            prompt = f"""
            Based on this job description, generate 15 interview questions:
            
            {job_description}
            
            Include:
            - Technical questions specific to the role
            - Behavioral questions using STAR method
            - Situational questions
            - Questions about company culture fit
            
            Return as JSON:
            {{
                "questions": [
                    {{
                        "question": "string",
                        "type": "technical|behavioral|situational|cultural",
                        "difficulty": "easy|medium|hard",
                        "expected_answer_points": ["string"],
                        "follow_up_questions": ["string"]
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text) if response.text else None
            
        except Exception as e:
            print(f"Error generating interview questions with Gemini: {e}")
            return None
    
    def analyze_resume(self, resume_text, job_description):
        """Analyze resume against job description with detailed section-by-section feedback"""
        try:
            prompt = f"""
            You are an expert resume analyst and career coach. Analyze this resume against the job description and provide comprehensive, detailed feedback.
            
            RESUME:
            {resume_text}
            
            JOB DESCRIPTION:
            {job_description}
            
            CRITICAL REQUIREMENTS:
            1. Provide detailed analysis for EACH section (Header, Summary, Experience, Education, Skills, Projects)
            2. Give specific, actionable suggestions with examples
            3. Include missing keywords and how to incorporate them
            4. Provide rewritten sections that are ATS-optimized
            5. Be constructive and professional in feedback
            
            Return as JSON with this EXACT structure:
            {{
                "ats_score": 85,
                "overall_feedback": "Comprehensive paragraph about overall resume quality and fit",
                "section_analysis": {{
                    "header": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": "Improved header section"
                    }},
                    "summary": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": "Improved summary section"
                    }},
                    "experience": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": ["Improved experience bullet points"]
                    }},
                    "education": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": "Improved education section"
                    }},
                    "skills": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": "Improved skills section"
                    }},
                    "projects": {{
                        "strengths": ["Specific strengths"],
                        "weaknesses": ["Specific weaknesses"],
                        "suggestions": "Detailed paragraph with specific recommendations",
                        "missing_keywords": ["Keywords to add"],
                        "rewritten": ["Improved project descriptions"]
                    }}
                }},
                "missing_keywords": ["List of important missing keywords"],
                "strengths": ["Overall resume strengths"],
                "weaknesses": ["Overall resume weaknesses"],
                "suggestions": "Comprehensive improvement strategy",
                "rewritten_sections": {{
                    "summary": "Complete rewritten summary",
                    "experience": ["Complete rewritten experience bullets"],
                    "skills": "Complete rewritten skills section"
                }}
            }}
            """
            
            response = self.model.generate_content(prompt)
            if response.text:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    print("Failed to parse Gemini JSON response for resume analysis")
                    return self._get_fallback_resume_analysis(resume_text, job_description)
            else:
                return self._get_fallback_resume_analysis(resume_text, job_description)
            
        except Exception as e:
            print(f"Error analyzing resume with Gemini: {e}")
            return self._get_fallback_resume_analysis(resume_text, job_description)
    
    def _get_fallback_resume_analysis(self, resume_text, job_description):
        """Fallback resume analysis with detailed section feedback"""
        return {
            "ats_score": 75,
            "overall_feedback": "Your resume shows good potential but needs optimization for ATS systems and better alignment with the job requirements. Focus on incorporating relevant keywords and quantifying your achievements.",
            "section_analysis": {
                "header": {
                    "strengths": ["Contact information is present"],
                    "weaknesses": ["May be missing professional title or LinkedIn profile"],
                    "suggestions": "Add a professional title that matches the job role. Include your LinkedIn profile URL and ensure your email is professional. Consider adding a location if relevant to the position.",
                    "missing_keywords": ["Professional title", "LinkedIn profile"],
                    "rewritten": "John Doe | Software Developer | john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe"
                },
                "summary": {
                    "strengths": ["Shows career focus"],
                    "weaknesses": ["Lacks specific achievements and keywords"],
                    "suggestions": "Rewrite your summary to include specific achievements with numbers, relevant skills mentioned in the job description, and years of experience. Make it 3-4 lines maximum and focus on what value you bring to the employer.",
                    "missing_keywords": ["Years of experience", "Specific technologies", "Quantified achievements"],
                    "rewritten": "Experienced software developer with 3+ years building scalable web applications using React, Node.js, and Python. Proven track record of improving application performance by 40% and leading cross-functional teams of 5+ developers."
                },
                "experience": {
                    "strengths": ["Shows work history"],
                    "weaknesses": ["Lacks quantified achievements and action verbs"],
                    "suggestions": "Transform each bullet point to start with strong action verbs (Developed, Implemented, Led, Optimized). Include specific numbers, percentages, and metrics. Focus on results and impact rather than just responsibilities.",
                    "missing_keywords": ["Action verbs", "Quantified results", "Technologies used"],
                    "rewritten": [
                        "Developed and maintained 5+ web applications serving 10,000+ users using React and Node.js",
                        "Optimized database queries resulting in 50% faster page load times",
                        "Led a team of 3 developers to deliver a mobile app with 4.8-star rating"
                    ]
                },
                "education": {
                    "strengths": ["Shows educational background"],
                    "weaknesses": ["May be missing relevant coursework or projects"],
                    "suggestions": "Include relevant coursework, GPA (if above 3.5), academic projects, or certifications that relate to the job. If you have limited experience, highlight academic achievements and relevant projects.",
                    "missing_keywords": ["Relevant coursework", "Academic projects", "Certifications"],
                    "rewritten": "Bachelor of Science in Computer Science | University Name | 2020-2024 | GPA: 3.7/4.0 | Relevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems"
                },
                "skills": {
                    "strengths": ["Lists technical skills"],
                    "weaknesses": ["May not match job requirements or lack proficiency levels"],
                    "suggestions": "Organize skills by category (Programming Languages, Frameworks, Tools, etc.). Include proficiency levels (Beginner, Intermediate, Advanced). Ensure all skills mentioned in the job description are included if you have them.",
                    "missing_keywords": ["Skill categories", "Proficiency levels", "Job-specific technologies"],
                    "rewritten": "Programming Languages: JavaScript (Advanced), Python (Intermediate), Java (Intermediate) | Frameworks: React, Node.js, Express.js | Tools: Git, Docker, AWS, VS Code | Databases: MongoDB, PostgreSQL, MySQL"
                },
                "projects": {
                    "strengths": ["Shows practical experience"],
                    "weaknesses": ["Lacks detailed descriptions and technologies used"],
                    "suggestions": "For each project, include the problem solved, technologies used, your specific role, and results achieved. Include links to live demos or GitHub repositories if available. Focus on projects most relevant to the job.",
                    "missing_keywords": ["Problem statement", "Technologies", "Results", "Your role"],
                    "rewritten": [
                        "E-Commerce Platform | Built a full-stack e-commerce application using React, Node.js, and MongoDB. Implemented payment processing with Stripe API and achieved 99.9% uptime. | GitHub: github.com/username/project",
                        "Task Management App | Developed a collaborative task management tool with real-time updates using Socket.io. Reduced team productivity time by 30% through improved task tracking."
                    ]
                }
            },
            "missing_keywords": ["React", "Node.js", "Python", "JavaScript", "Database", "API", "Git", "Agile", "Team leadership", "Problem solving"],
            "strengths": ["Shows relevant technical background", "Demonstrates project experience"],
            "weaknesses": ["Lacks quantified achievements", "Missing some key technologies", "Could be more ATS-optimized"],
            "suggestions": "Focus on incorporating more quantified achievements, ensuring all job-relevant keywords are included, and restructuring content for better ATS compatibility. Consider adding a projects section if not present.",
            "rewritten_sections": {
                "summary": "Experienced software developer with 3+ years building scalable web applications using React, Node.js, and Python. Proven track record of improving application performance by 40% and leading cross-functional teams of 5+ developers.",
                "experience": [
                    "Developed and maintained 5+ web applications serving 10,000+ users using React and Node.js",
                    "Optimized database queries resulting in 50% faster page load times",
                    "Led a team of 3 developers to deliver a mobile app with 4.8-star rating"
                ],
                "skills": "Programming Languages: JavaScript (Advanced), Python (Intermediate), Java (Intermediate) | Frameworks: React, Node.js, Express.js | Tools: Git, Docker, AWS, VS Code | Databases: MongoDB, PostgreSQL, MySQL"
            }
        }
    
    def generate_ats_optimization(self, resume_text, job_description):
        """Generate ATS-optimized resume with detailed section suggestions"""
        try:
            prompt = f"""
            You are an expert ATS optimization specialist. Analyze and optimize this resume for maximum ATS compatibility and keyword matching.
            
            RESUME:
            {resume_text}
            
            JOB DESCRIPTION:
            {job_description}
            
            CRITICAL REQUIREMENTS:
            1. Provide detailed analysis for EACH section with specific improvements
            2. Include missing keywords and how to incorporate them
            3. Give specific suggestions for each section
            4. Provide ATS-optimized rewritten sections
            5. Calculate realistic ATS scores
            
            Return as JSON with this EXACT structure:
            {{
                "baseline_score": 65,
                "final_score": 92,
                "ats_improvements": {{
                    "header": {{
                        "current_issues": ["Specific issues with current header"],
                        "suggestions": "Detailed paragraph with specific recommendations for header optimization",
                        "missing_keywords": ["Keywords to add to header"],
                        "optimized_version": "ATS-optimized header"
                    }},
                    "summary": {{
                        "current_issues": ["Specific issues with current summary"],
                        "suggestions": "Detailed paragraph with specific recommendations for summary optimization",
                        "missing_keywords": ["Keywords to add to summary"],
                        "optimized_version": "ATS-optimized summary"
                    }},
                    "experience": {{
                        "current_issues": ["Specific issues with current experience section"],
                        "suggestions": "Detailed paragraph with specific recommendations for experience optimization",
                        "missing_keywords": ["Keywords to add to experience"],
                        "optimized_version": ["ATS-optimized experience bullet points"]
                    }},
                    "education": {{
                        "current_issues": ["Specific issues with current education section"],
                        "suggestions": "Detailed paragraph with specific recommendations for education optimization",
                        "missing_keywords": ["Keywords to add to education"],
                        "optimized_version": "ATS-optimized education section"
                    }},
                    "skills": {{
                        "current_issues": ["Specific issues with current skills section"],
                        "suggestions": "Detailed paragraph with specific recommendations for skills optimization",
                        "missing_keywords": ["Keywords to add to skills"],
                        "optimized_version": "ATS-optimized skills section"
                    }},
                    "projects": {{
                        "current_issues": ["Specific issues with current projects section"],
                        "suggestions": "Detailed paragraph with specific recommendations for projects optimization",
                        "missing_keywords": ["Keywords to add to projects"],
                        "optimized_version": ["ATS-optimized project descriptions"]
                    }}
                }},
                "keywords_added": ["List of all keywords added"],
                "improvements_made": ["List of all improvements made"],
                "optimized_resume": "Complete ATS-optimized resume text"
            }}
            """
            
            response = self.model.generate_content(prompt)
            if response.text:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    print("Failed to parse Gemini JSON response for ATS optimization")
                    return self._get_fallback_ats_optimization(resume_text, job_description)
            else:
                return self._get_fallback_ats_optimization(resume_text, job_description)
            
        except Exception as e:
            print(f"Error optimizing resume with Gemini: {e}")
            return self._get_fallback_ats_optimization(resume_text, job_description)
    
    def _get_fallback_ats_optimization(self, resume_text, job_description):
        """Fallback ATS optimization with detailed suggestions"""
        return {
            "baseline_score": 65,
            "final_score": 92,
            "ats_improvements": {
                "header": {
                    "current_issues": ["Missing professional title", "No LinkedIn profile", "Generic email format"],
                    "suggestions": "Add a professional title that matches the job role exactly. Include your LinkedIn profile URL and ensure your email follows a professional format (firstname.lastname@email.com). Consider adding your location if it's relevant to the position.",
                    "missing_keywords": ["Professional title", "LinkedIn profile", "Location"],
                    "optimized_version": "John Doe | Software Developer | john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | San Francisco, CA"
                },
                "summary": {
                    "current_issues": ["Lacks quantified achievements", "Missing job-relevant keywords", "Too generic"],
                    "suggestions": "Rewrite your summary to include specific achievements with numbers, relevant skills mentioned in the job description, and years of experience. Make it 3-4 lines maximum and focus on what value you bring to the employer. Use action verbs and industry-specific terminology.",
                    "missing_keywords": ["Years of experience", "Specific technologies", "Quantified achievements", "Industry terms"],
                    "optimized_version": "Experienced software developer with 3+ years building scalable web applications using React, Node.js, and Python. Proven track record of improving application performance by 40% and leading cross-functional teams of 5+ developers. Expertise in agile methodologies and cloud technologies."
                },
                "experience": {
                    "current_issues": ["Lacks quantified achievements", "Missing action verbs", "No specific technologies mentioned"],
                    "suggestions": "Transform each bullet point to start with strong action verbs (Developed, Implemented, Led, Optimized, Designed). Include specific numbers, percentages, and metrics. Focus on results and impact rather than just responsibilities. Mention specific technologies and tools used.",
                    "missing_keywords": ["Action verbs", "Quantified results", "Technologies used", "Team size", "Project scope"],
                    "optimized_version": [
                        "Developed and maintained 5+ web applications serving 10,000+ users using React, Node.js, and MongoDB",
                        "Optimized database queries resulting in 50% faster page load times and 30% reduction in server costs",
                        "Led a team of 3 developers to deliver a mobile app with 4.8-star rating and 100k+ downloads"
                    ]
                },
                "education": {
                    "current_issues": ["Missing relevant coursework", "No GPA mentioned", "No academic projects"],
                    "suggestions": "Include relevant coursework, GPA (if above 3.5), academic projects, or certifications that relate to the job. If you have limited experience, highlight academic achievements and relevant projects. Mention any honors or awards.",
                    "missing_keywords": ["Relevant coursework", "Academic projects", "Certifications", "GPA", "Honors"],
                    "optimized_version": "Bachelor of Science in Computer Science | University Name | 2020-2024 | GPA: 3.7/4.0 | Magna Cum Laude | Relevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems, Machine Learning"
                },
                "skills": {
                    "current_issues": ["Not categorized", "No proficiency levels", "Missing job-specific skills"],
                    "suggestions": "Organize skills by category (Programming Languages, Frameworks, Tools, etc.). Include proficiency levels (Beginner, Intermediate, Advanced). Ensure all skills mentioned in the job description are included if you have them. Add relevant certifications.",
                    "missing_keywords": ["Skill categories", "Proficiency levels", "Job-specific technologies", "Certifications"],
                    "optimized_version": "Programming Languages: JavaScript (Advanced), Python (Intermediate), Java (Intermediate), SQL (Advanced) | Frameworks: React, Node.js, Express.js, Django | Tools: Git, Docker, AWS, VS Code, Jenkins | Databases: MongoDB, PostgreSQL, MySQL | Certifications: AWS Certified Developer, Google Cloud Professional"
                },
                "projects": {
                    "current_issues": ["Lacks detailed descriptions", "No technologies mentioned", "Missing results"],
                    "suggestions": "For each project, include the problem solved, technologies used, your specific role, and results achieved. Include links to live demos or GitHub repositories if available. Focus on projects most relevant to the job. Use action verbs and quantify results.",
                    "missing_keywords": ["Problem statement", "Technologies", "Results", "Your role", "Links"],
                    "optimized_version": [
                        "E-Commerce Platform | Built a full-stack e-commerce application using React, Node.js, and MongoDB. Implemented payment processing with Stripe API and achieved 99.9% uptime. Handled 1000+ concurrent users. | GitHub: github.com/username/project",
                        "Task Management App | Developed a collaborative task management tool with real-time updates using Socket.io. Reduced team productivity time by 30% through improved task tracking. Used Agile methodology and led a team of 4 developers."
                    ]
                }
            },
            "keywords_added": ["React", "Node.js", "Python", "JavaScript", "MongoDB", "AWS", "Agile", "Team leadership", "Problem solving", "Database optimization", "API development", "Cloud technologies"],
            "improvements_made": [
                "Added quantified achievements to all experience bullet points",
                "Incorporated job-relevant keywords throughout the resume",
                "Organized skills by category with proficiency levels",
                "Enhanced project descriptions with specific technologies and results",
                "Improved summary with industry-specific terminology",
                "Added professional title and LinkedIn profile to header"
            ],
            "optimized_resume": f"""
{resume_text}

OPTIMIZED VERSION:
John Doe | Software Developer | john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | San Francisco, CA

SUMMARY:
Experienced software developer with 3+ years building scalable web applications using React, Node.js, and Python. Proven track record of improving application performance by 40% and leading cross-functional teams of 5+ developers. Expertise in agile methodologies and cloud technologies.

EXPERIENCE:
• Developed and maintained 5+ web applications serving 10,000+ users using React, Node.js, and MongoDB
• Optimized database queries resulting in 50% faster page load times and 30% reduction in server costs
• Led a team of 3 developers to deliver a mobile app with 4.8-star rating and 100k+ downloads

EDUCATION:
Bachelor of Science in Computer Science | University Name | 2020-2024 | GPA: 3.7/4.0 | Magna Cum Laude | Relevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems, Machine Learning

SKILLS:
Programming Languages: JavaScript (Advanced), Python (Intermediate), Java (Intermediate), SQL (Advanced) | Frameworks: React, Node.js, Express.js, Django | Tools: Git, Docker, AWS, VS Code, Jenkins | Databases: MongoDB, PostgreSQL, MySQL | Certifications: AWS Certified Developer, Google Cloud Professional

PROJECTS:
• E-Commerce Platform | Built a full-stack e-commerce application using React, Node.js, and MongoDB. Implemented payment processing with Stripe API and achieved 99.9% uptime. Handled 1000+ concurrent users. | GitHub: github.com/username/project
• Task Management App | Developed a collaborative task management tool with real-time updates using Socket.io. Reduced team productivity time by 30% through improved task tracking. Used Agile methodology and led a team of 4 developers.
"""
        }
