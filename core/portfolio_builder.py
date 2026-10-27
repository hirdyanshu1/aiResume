import os
import re
import json

class PortfolioBuilder:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.templates_dir = os.path.join(workspace_dir, "templates")

    def render_mustache(self, template, context):
        """
        A zero-dependency mini Mustache rendering engine in Python.
        Supports lists {{#list}}...{{/list}}, conditionals {{#cond}}...{{/cond}},
        primitives {{.}}, and standard variables {{var}}.
        """
        # 1. Process Section blocks: {{#key}}...{{/key}}
        pattern = re.compile(r'\{\{\#([\w_]+)\}\}(.*?)\{\{\/\1\}\}', re.DOTALL)
        
        def replace_section(match):
            key = match.group(1)
            content = match.group(2)
            val = context.get(key)
            
            # If val is a list, render the content for each list item
            if isinstance(val, list):
                rendered_items = []
                for item in val:
                    if isinstance(item, (str, int, float)):
                        item_ctx = {".": item}
                    else:
                        item_ctx = item.copy() if isinstance(item, dict) else {}
                    # Merge parent context with item context
                    merged_ctx = {**context, **item_ctx}
                    rendered_items.append(self.render_mustache(content, merged_ctx))
                return "".join(rendered_items)
                
            # If val is a truthy value, render the content with the current context
            elif val:
                return self.render_mustache(content, context)
                
            # Otherwise, remove the block
            else:
                return ""
                
        # Repeat until no more section blocks are left (handles nesting)
        rendered = template
        while True:
            new_rendered, count = pattern.subn(replace_section, rendered)
            if count == 0:
                break
            rendered = new_rendered
            
        # 2. Process variable tags: {{var}} and {{.}}
        var_pattern = re.compile(r'\{\{([\w_\.]+)\}\}')
        def replace_var(match):
            key = match.group(1)
            if key == ".":
                return str(context.get(".", ""))
            
            # Support nested lookup (e.g. personal.name)
            if "." in key:
                parts = key.split(".")
                curr = context
                for p in parts:
                    if isinstance(curr, dict) and p in curr:
                        curr = curr[p]
                    else:
                        return ""
                return str(curr)
                
            return str(context.get(key, ""))
            
        rendered = var_pattern.sub(replace_var, rendered)
        return rendered

    def compile_resume(self, resume_data, template_name):
        """
        Compiles the resume_data using the specified template HTML file.
        Returns the rendered HTML string.
        """
        template_path = os.path.join(self.templates_dir, f"{template_name}.html")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template '{template_name}' not found at {template_path}")
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Prepare context data
        context = {
            "name": resume_data["personal"].get("name", ""),
            "title": resume_data["personal"].get("title", ""),
            "email": resume_data["personal"].get("email", ""),
            "phone": resume_data["personal"].get("phone", ""),
            "location": resume_data["personal"].get("location", ""),
            "website": resume_data["personal"].get("website", ""),
            "github": resume_data["personal"].get("github", ""),
            "linkedin": resume_data["personal"].get("linkedin", ""),
            "summary": resume_data.get("summary", ""),
            "experiences": resume_data.get("experiences", []),
            "projects": resume_data.get("projects", []),
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", []),
            # Section flags
            "experience_section": len(resume_data.get("experiences", [])) > 0,
            "project_section": len(resume_data.get("projects", [])) > 0,
            "education_section": len(resume_data.get("education", [])) > 0,
            "skills_section": len(resume_data.get("skills", [])) > 0,
        }
        
        # Add helper flags for personal contacts
        context["website_exists"] = bool(context["website"])
        context["github_exists"] = bool(context["github"])
        context["linkedin_exists"] = bool(context["linkedin"])
        
        return self.render_mustache(template_content, context)

    def generate_portfolio_site(self, resume_data, output_dir):
        """
        Generates a premium portfolio website files inside output_dir.
        Creates index.html and styles.css.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup context
        context = {
            "name": resume_data["personal"].get("name", "John Doe"),
            "title": resume_data["personal"].get("title", "Full Stack Developer"),
            "email": resume_data["personal"].get("email", ""),
            "phone": resume_data["personal"].get("phone", ""),
            "location": resume_data["personal"].get("location", ""),
            "website": resume_data["personal"].get("website", ""),
            "github": resume_data["personal"].get("github", ""),
            "linkedin": resume_data["personal"].get("linkedin", ""),
            "summary": resume_data.get("summary", ""),
            "experiences": resume_data.get("experiences", []),
            "projects": resume_data.get("projects", []),
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", []),
            "has_experience": len(resume_data.get("experiences", [])) > 0,
            "has_projects": len(resume_data.get("projects", [])) > 0,
            "has_education": len(resume_data.get("education", [])) > 0,
            "has_skills": len(resume_data.get("skills", [])) > 0,
        }
        
        # Build the HTML template for the Portfolio Site
        portfolio_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{name}} | Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body class="dark-theme">
    <!-- Navbar -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="#" class="logo">{{name}}</a>
            <ul class="nav-links">
                <li><a href="#about">About</a></li>
                {{#has_skills}}<li><a href="#skills">Skills</a></li>{{/has_skills}}
                {{#has_experience}}<li><a href="#experience">Experience</a></li>{{/has_experience}}
                {{#has_projects}}<li><a href="#projects">Projects</a></li>{{/has_projects}}
                {{#has_education}}<li><a href="#education">Education</a></li>{{/has_education}}
                <li><a href="#contact">Contact</a></li>
            </ul>
            <button id="theme-toggle" class="theme-btn">
                <span class="sun-icon">☀️</span>
                <span class="moon-icon">🌙</span>
            </button>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-container">
            <h1 class="hero-title">Hi, I'm <span class="gradient-text">{{name}}</span></h1>
            <p class="hero-subtitle">{{title}}</p>
            <p class="hero-desc">{{summary}}</p>
            <div class="hero-cta">
                <a href="#contact" class="btn btn-primary">Get In Touch</a>
                <a href="#projects" class="btn btn-secondary">View Work</a>
            </div>
        </div>
    </section>

    <!-- Main Content Container -->
    <main class="main-content">
        <!-- About Section -->
        <section id="about" class="section">
            <h2 class="section-title">About Me</h2>
            <div class="card about-card">
                <p>{{summary}}</p>
                <div class="about-details">
                    <div class="detail-item"><strong>Location:</strong> {{location}}</div>
                    <div class="detail-item"><strong>Email:</strong> {{email}}</div>
                    {{#phone}}<div class="detail-item"><strong>Phone:</strong> {{phone}}</div>{{/phone}}
                </div>
            </div>
        </section>

        <!-- Skills Section -->
        {{#has_skills}}
        <section id="skills" class="section">
            <h2 class="section-title">Technical Expertise</h2>
            <div class="skills-grid">
                {{#skills}}
                <div class="skill-pill">{{.}}</div>
                {{/skills}}
            </div>
        </section>
        {{/has_skills}}

        <!-- Experience Section -->
        {{#has_experience}}
        <section id="experience" class="section">
            <h2 class="section-title">Work Experience</h2>
            <div class="timeline">
                {{#experiences}}
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-date">{{start_date}} - {{end_date}}</div>
                    <div class="card timeline-card">
                        <h3 class="role-title">{{role}}</h3>
                        <h4 class="company-name">{{company}} <span class="location-tag">({{{location}}})</span></h4>
                        <ul class="bullet-list">
                            {{#bullets}}
                            <li>{{.}}</li>
                            {{/bullets}}
                        </ul>
                    </div>
                </div>
                {{/experiences}}
            </div>
        </section>
        {{/has_experience}}

        <!-- Projects Section -->
        {{#has_projects}}
        <section id="projects" class="section">
            <h2 class="section-title">Projects Showcase</h2>
            <div class="projects-grid">
                {{#projects}}
                <div class="card project-card">
                    <div class="project-header">
                        <span class="project-tech">{{technologies}}</span>
                    </div>
                    <h3 class="project-name">{{name}}</h3>
                    <p class="project-date">{{date}}</p>
                    <ul class="bullet-list project-bullets">
                        {{#bullets}}
                        <li>{{.}}</li>
                        {{/bullets}}
                    </ul>
                    {{#link}}
                    <div class="project-footer">
                        <a href="{{link}}" target="_blank" class="project-link">View Repository &rarr;</a>
                    </div>
                    {{/link}}
                </div>
                {{/projects}}
            </div>
        </section>
        {{/has_projects}}

        <!-- Education Section -->
        {{#has_education}}
        <section id="education" class="section">
            <h2 class="section-title">Education</h2>
            <div class="education-grid">
                {{#education}}
                <div class="card edu-card">
                    <h3 class="edu-degree">{{degree}}</h3>
                    <h4 class="edu-institution">{{institution}}</h4>
                    <p class="edu-date">{{start_date}} - {{end_date}}</p>
                    {{#gpa}}<p class="edu-gpa"><strong>GPA:</strong> {{gpa}}</p>{{/gpa}}
                </div>
                {{/education}}
            </div>
        </section>
        {{/has_education}}

        <!-- Contact Section -->
        <section id="contact" class="section">
            <h2 class="section-title">Let's Connect</h2>
            <div class="card contact-card">
                <p class="contact-prompt">Interested in working together or hiring me? Reach out via any of the channels below.</p>
                <div class="contact-methods">
                    <a href="mailto:{{email}}" class="contact-link mail">Email: {{email}}</a>
                    {{#website}}<a href="{{website}}" target="_blank" class="contact-link link">Website</a>{{/website}}
                    {{#github}}<a href="{{github}}" target="_blank" class="contact-link github">GitHub</a>{{/github}}
                    {{#linkedin}}<a href="{{linkedin}}" target="_blank" class="contact-link linkedin">LinkedIn</a>{{/linkedin}}
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2026 {{name}}. Powered by AI Resume Studio.</p>
    </footer>

    <!-- Dark Mode Script -->
    <script>
        const themeToggle = document.getElementById('theme-toggle');
        const body = document.body;
        
        // Load preference
        const savedTheme = localStorage.getItem('theme') || 'dark';
        if (savedTheme === 'light') {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
        }
        
        themeToggle.addEventListener('click', () => {
            if (body.classList.contains('dark-theme')) {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            }
        });
    </script>
</body>
</html>
"""
        
        portfolio_css = """/* Base Variables & Theme colors */
:root {
    --bg-color: #0f172a;
    --card-bg: #1e293b;
    --text-color: #f8fafc;
    --text-muted: #94a3b8;
    --primary-color: #6366f1;
    --primary-hover: #4f46e5;
    --accent-color: #38bdf8;
    --border-color: #334155;
    --gradient-1: #6366f1;
    --gradient-2: #3b82f6;
    --gradient-3: #ec4899;
}

.light-theme {
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-color: #0f172a;
    --text-muted: #64748b;
    --primary-color: #4f46e5;
    --primary-hover: #3730a3;
    --accent-color: #0284c7;
    --border-color: #e2e8f0;
}

/* Global Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Layout Containers */
.navbar, .hero-container, .main-content, .nav-container {
    max-width: 1100px;
    margin: 0 auto;
    width: 90%;
}

/* Navigation bar styling */
.navbar {
    position: sticky;
    top: 0;
    width: 100%;
    z-index: 100;
    background-color: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.3s ease;
}
.light-theme .navbar {
    background-color: rgba(248, 250, 252, 0.8);
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0;
}

.logo {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-color);
    text-decoration: none;
    background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links {
    list-style: none;
    display: flex;
    gap: 25px;
}

.nav-links a {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s ease;
}

.nav-links a:hover {
    color: var(--primary-color);
}

.theme-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    outline: none;
}

.dark-theme .sun-icon { display: block; }
.dark-theme .moon-icon { display: none; }
.light-theme .sun-icon { display: none; }
.light-theme .moon-icon { display: block; }

/* Hero Section styling */
.hero {
    padding: 100px 0 60px 0;
    text-align: center;
}

.hero-title {
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 15px;
}

.gradient-text {
    background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2), var(--gradient-3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 24px;
    font-weight: 500;
    color: var(--accent-color);
    margin-bottom: 20px;
}

.hero-desc {
    font-size: 16px;
    color: var(--text-muted);
    max-width: 650px;
    margin: 0 auto 30px auto;
}

.hero-cta {
    display: flex;
    justify-content: center;
    gap: 15px;
}

/* Card layout utility */
.card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 30px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Buttons */
.btn {
    display: inline-block;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: background-color 0.2s ease, transform 0.1s ease;
}

.btn-primary {
    background-color: var(--primary-color);
    color: #ffffff;
}

.btn-primary:hover {
    background-color: var(--primary-hover);
}

.btn-secondary {
    background-color: transparent;
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

/* Sections spacing */
.section {
    padding: 80px 0 40px 0;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 30px;
    position: relative;
    display: inline-block;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 0;
    width: 40px;
    height: 3px;
    background-color: var(--primary-color);
    border-radius: 2px;
}

/* About Card info alignment */
.about-details {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
    font-size: 14px;
    color: var(--text-muted);
}

/* Skills list grid */
.skills-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.skill-pill {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 500;
    transition: border-color 0.2s ease, background-color 0.2s ease;
}

.skill-pill:hover {
    border-color: var(--primary-color);
    background-color: rgba(99, 102, 241, 0.05);
}

/* Experience timeline */
.timeline {
    position: relative;
    border-left: 2px solid var(--border-color);
    padding-left: 30px;
    margin-left: 10px;
}

.timeline-item {
    position: relative;
    margin-bottom: 40px;
}

.timeline-dot {
    position: absolute;
    left: -41px;
    top: 6px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: var(--primary-color);
    border: 4px solid var(--bg-color);
}

.timeline-date {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent-color);
    margin-bottom: 8px;
}

.role-title {
    font-size: 18px;
    font-weight: 600;
}

.company-name {
    font-size: 14px;
    color: var(--primary-color);
    margin-bottom: 15px;
}

.location-tag {
    color: var(--text-muted);
    font-weight: normal;
}

.bullet-list {
    padding-left: 20px;
    font-size: 14.5px;
    color: var(--text-muted);
}

.bullet-list li {
    margin-bottom: 8px;
}

/* Projects grid showcase */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 25px;
}

.project-card {
    display: flex;
    flex-direction: column;
}

.project-header {
    margin-bottom: 15px;
}

.project-tech {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--accent-color);
}

.project-name {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 5px;
}

.project-date {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 15px;
}

.project-bullets {
    flex-grow: 1;
    margin-bottom: 20px;
}

.project-link {
    color: var(--primary-color);
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
}

.project-link:hover {
    color: var(--primary-hover);
    text-decoration: underline;
}

/* Education Cards grid */
.education-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 25px;
}

.edu-degree {
    font-size: 16px;
    font-weight: 600;
}

.edu-institution {
    font-size: 14px;
    color: var(--primary-color);
    margin-bottom: 10px;
}

.edu-date {
    font-size: 13px;
    color: var(--text-muted);
}

.edu-gpa {
    font-size: 13px;
    margin-top: 5px;
}

/* Contact methods display */
.contact-card {
    text-align: center;
}

.contact-prompt {
    font-size: 16px;
    color: var(--text-muted);
    margin-bottom: 25px;
}

.contact-methods {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
}

.contact-link {
    display: inline-block;
    padding: 10px 20px;
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: border-color 0.2s ease, background-color 0.2s ease;
}

.contact-link:hover {
    border-color: var(--primary-color);
    background-color: rgba(99, 102, 241, 0.05);
}

/* Footer Section */
.footer {
    padding: 40px 0;
    border-top: 1px solid var(--border-color);
    text-align: center;
    color: var(--text-muted);
    font-size: 13px;
    margin-top: 60px;
}

/* Responsive adjustment */
@media (max-width: 768px) {
    .nav-links { display: none; }
    .hero-title { font-size: 38px; }
    .hero-subtitle { font-size: 20px; }
    .timeline { padding-left: 20px; }
}
"""
        
        # Render html
        rendered_html = self.render_mustache(portfolio_html, context)
        
        # Save HTML
        with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(rendered_html)
            
        # Save CSS
        with open(os.path.join(output_dir, "styles.css"), 'w', encoding='utf-8') as f:
            f.write(portfolio_css)
            
        return os.path.join(output_dir, "index.html")
