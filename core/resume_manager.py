import os
import json

DEFAULT_RESUME = {
    "personal": {
        "name": "Alex Mercer",
        "title": "Software Engineer",
        "email": "alex.mercer@email.com",
        "phone": "+1 (555) 019-2834",
        "location": "San Francisco, CA",
        "website": "https://alexmercer.dev",
        "github": "https://github.com/alexmercer",
        "linkedin": "https://linkedin.com/in/alexmercer"
    },
    "summary": "Innovative and results-driven Software Engineer with 3+ years of experience building scalable web applications and AI-driven solutions. Proven expertise in Python, JavaScript, and cloud architectures. Passionate about solving complex problems and optimizing system performance.",
    "experiences": [
        {
            "company": "Tech Solutions Inc.",
            "role": "Software Engineer",
            "location": "San Francisco, CA",
            "start_date": "Jun 2024",
            "end_date": "Present",
            "bullets": [
                "Led the development of a microservices backend in FastAPI, increasing API response times by 35% through Redis caching.",
                "Collaborated with cross-functional teams of 5 to integrate OpenAI API for automated content moderation, reducing manual workload by 50%.",
                "Deployed and maintained CI/CD pipelines using GitHub Actions, reducing deployment errors by 25%."
            ]
        },
        {
            "company": "Innovate Systems",
            "role": "Junior Developer",
            "location": "San Jose, CA",
            "start_date": "Jan 2023",
            "end_date": "May 2024",
            "bullets": [
                "Developed responsive frontend features in React and Tailwind CSS, increasing user engagement by 15%.",
                "Optimized SQL queries in PostgreSQL database, reducing report generation times from 10 seconds to under 2 seconds.",
                "Participated in agile ceremonies and code reviews to ensure high-quality software standards."
            ]
        }
    ],
    "projects": [
        {
            "name": "AI Task Manager",
            "date": "Oct 2024",
            "technologies": "Python, React, Ollama",
            "link": "https://github.com/alexmercer/ai-task-manager",
            "bullets": [
                "Built a desktop productivity app that uses local LLMs to prioritize, summarize, and categorize user tasks.",
                "Implemented drag-and-drop kanban board in React with offline capability using IndexedDB."
            ]
        }
    ],
    "education": [
        {
            "institution": "State University",
            "degree": "B.S. in Computer Science",
            "start_date": "Sep 2019",
            "end_date": "Dec 2022",
            "gpa": "3.8/4.0"
        }
    ],
    "skills": ["Python", "FastAPI", "React", "JavaScript", "TypeScript", "Tailwind CSS", "PostgreSQL", "Docker", "Git", "GitHub Actions"]
}

class ResumeManager:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.resumes_dir = os.path.join(workspace_dir, "saved_resumes")
        os.makedirs(self.resumes_dir, exist_ok=True)
        
        # Current active resume data in memory
        self.current_data = DEFAULT_RESUME.copy()
        self.current_filename = "default_resume.json"
        
        # Load default or create it
        default_path = os.path.join(self.resumes_dir, self.current_filename)
        if not os.path.exists(default_path):
            self.save_resume_to_file(self.current_data, default_path)
        else:
            self.load_resume_file(default_path)

    def get_empty_resume(self):
        return {
            "personal": {"name": "", "title": "", "email": "", "phone": "", "location": "", "website": "", "github": "", "linkedin": ""},
            "summary": "",
            "experiences": [],
            "projects": [],
            "education": [],
            "skills": []
        }

    def save_current_resume(self, data=None):
        if data is not None:
            self.current_data = data
        path = os.path.join(self.resumes_dir, self.current_filename)
        return self.save_resume_to_file(self.current_data, path)

    def save_resume_as(self, data, filename):
        if not filename.endswith(".json"):
            filename += ".json"
        self.current_filename = filename
        self.current_data = data
        path = os.path.join(self.resumes_dir, filename)
        return self.save_resume_to_file(data, path)

    def save_resume_to_file(self, data, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving resume: {e}")
            return False

    def load_resume_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Fill missing keys if any (migration/safety)
            cleaned_data = self.get_empty_resume()
            
            if "personal" in data:
                cleaned_data["personal"].update(data["personal"])
            if "summary" in data:
                cleaned_data["summary"] = data["summary"]
            if "experiences" in data:
                cleaned_data["experiences"] = data["experiences"]
            if "projects" in data:
                cleaned_data["projects"] = data["projects"]
            if "education" in data:
                cleaned_data["education"] = data["education"]
            if "skills" in data:
                cleaned_data["skills"] = data["skills"]
                
            self.current_data = cleaned_data
            self.current_filename = os.path.basename(filepath)
            return cleaned_data
        except Exception as e:
            print(f"Error loading resume: {e}")
            return None

    def list_saved_resumes(self):
        try:
            files = [f for f in os.listdir(self.resumes_dir) if f.endswith(".json")]
            return files
        except Exception as e:
            print(f"Error listing resumes: {e}")
            return []
            
    def delete_resume(self, filename):
        if filename == "default_resume.json":
            return False # Keep the default
        try:
            path = os.path.join(self.resumes_dir, filename)
            if os.path.exists(path):
                os.remove(path)
                # Fallback if we deleted the current one
                if self.current_filename == filename:
                    self.current_filename = "default_resume.json"
                    self.load_resume_file(os.path.join(self.resumes_dir, self.current_filename))
                return True
            return False
        except Exception as e:
            print(f"Error deleting resume: {e}")
            return False
