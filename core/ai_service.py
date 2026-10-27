import os
import json
import random
import requests

class AIService:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.config_path = os.path.join(workspace_dir, "config.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {
                "api_type": "offline",  # options: "offline", "gemini", "openai", "custom"
                "api_key": "",
                "openai_base_url": "https://api.openai.com/v1",
                "custom_model": "gpt-4o"
            }
            self.save_config()

    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def _call_gemini(self, prompt):
        key = self.config.get("api_key", "")
        if not key:
            raise ValueError("Gemini API Key is missing.")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        res_json = response.json()
        
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ValueError("Failed to parse Gemini API response format.")

    def _call_openai(self, prompt, system_prompt="You are a helpful career assistant."):
        key = self.config.get("api_key", "")
        base_url = self.config.get("openai_base_url", "https://api.openai.com/v1")
        model = self.config.get("custom_model", "gpt-4o")
        
        if not key and "openai.com" in base_url:
            raise ValueError("OpenAI API Key is missing.")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}" if key else ""
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        # Check trailing slash
        endpoint = base_url.rstrip("/") + "/chat/completions"
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        res_json = response.json()
        
        try:
            return res_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError("Failed to parse OpenAI API response format.")

    def run_prompt(self, prompt, system_prompt="You are a helpful career assistant."):
        api_type = self.config.get("api_type", "offline")
        
        if api_type == "gemini":
            try:
                # Combine system prompt and user prompt for Gemini
                full_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}"
                return self._call_gemini(full_prompt)
            except Exception as e:
                print(f"Gemini API Error: {e}. Falling back to offline simulator.")
                return self._heuristic_fallback(prompt, system_prompt)
                
        elif api_type in ["openai", "custom"]:
            try:
                return self._call_openai(prompt, system_prompt)
            except Exception as e:
                print(f"OpenAI API Error: {e}. Falling back to offline simulator.")
                return self._heuristic_fallback(prompt, system_prompt)
                
        else:
            # Explicitly offline or fallback
            return self._heuristic_fallback(prompt, system_prompt)

    # --- OFFLINE HEURISTIC SIMULATOR ---
    def _heuristic_fallback(self, prompt, system_prompt):
        prompt_lower = prompt.lower()
        
        # Determine intent based on keywords in prompt or system prompt
        if "bullet" in prompt_lower or "improve" in prompt_lower:
            return self._mock_improve_bullets(prompt)
        elif "summary" in prompt_lower or "profile" in prompt_lower:
            return self._mock_summary_rewrite(prompt)
        elif "interview" in prompt_lower or "question" in prompt_lower:
            return self._mock_interview_questions(prompt)
        elif "gap" in prompt_lower or "learn" in prompt_lower:
            return self._mock_skill_gap(prompt)
        elif "github" in prompt_lower or "repo" in prompt_lower:
            return self._mock_github_desc(prompt)
        else:
            return self._mock_general_chat(prompt)

    def _mock_improve_bullets(self, prompt):
        # Extract something that looks like the bullet point
        # For simplicity, extract lines or clean prompt
        input_bullet = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*") or len(line) > 15:
                if "improve" not in line.lower() and "prompt" not in line.lower() and "api" not in line.lower():
                    input_bullet = line.lstrip("- *").strip()
                    break
        
        if not input_bullet or len(input_bullet) < 5:
            input_bullet = "Developed software and fixed bugs"

        # Action verbs for replacement
        verbs = ["Spearheaded", "Engineered", "Architected", "Orchestrated", "Designed", "Optimized", "Revamped", "Streamlined", "Formulated"]
        metrics = [
            "improving application throughput by 35% and reducing server costs by $12,000 annually",
            "reducing latency by 45% while handling 50k+ active weekly users",
            "boosting team operational efficiency by 20% and automating manual testing cycles",
            "resulting in a 30% increase in user retention rates and a 99.9% uptime score",
            "facilitating seamless horizontal scaling and cutting deployment duration in half"
        ]
        methods = [
            "using robust backend design practices and implementing Redis-driven caching policies",
            "by refactoring legacy systems into service-oriented Docker containers on AWS",
            "leveraging advanced asynchronous Python protocols (asyncio) and parallel processing",
            "through comprehensive unit-testing suites and automated CI/CD deployment pipelines",
            "utilizing modular architectures and implementing strict RESTful API specifications"
        ]
        
        # Make three distinct bullets
        options = []
        for i in range(3):
            verb = verbs[i % len(verbs)]
            metric = metrics[(i + random.randint(0, 10)) % len(metrics)]
            method = methods[(i + random.randint(0, 10)) % len(methods)]
            
            # Simple heuristic modification of input
            words = input_bullet.split()
            core_activity = " ".join(words[2:]) if len(words) > 3 else input_bullet
            core_activity = core_activity.lower().rstrip(".")
            
            options.append(f"{i+1}. **{verb}** the execution of {core_activity}, {metric} {method}.")
            
        header = f"### Optimized Resume Bullet Points (Offline Simulation Mode)\nHere are three high-impact, results-oriented alternatives:\n\n"
        return header + "\n".join(options)

    def _mock_summary_rewrite(self, prompt):
        # Determine tone
        tone = "Professional"
        if "creative" in prompt.lower():
            tone = "Creative"
        elif "confident" in prompt.lower() or "bold" in prompt.lower():
            tone = "Confident"
            
        summaries = {
            "Professional": (
                "Highly analytical and results-driven professional with a proven track record of "
                "delivering scalable software solutions and high-performing engineering architectures. "
                "Expertise lies in designing modular backend microservices, optimizing database schemas, "
                "and driving collaborative development workflows. Committed to maintaining code quality, "
                "continuous integration, and translating complex requirements into robust, clean software."
            ),
            "Confident": (
                "Dynamic and forward-thinking technologist who thrives on solving complex engineering "
                "challenges and building next-generation products. Recognized for pioneering tech initiatives "
                "that directly improve developer productivity and system performance. A natural problem-solver "
                "who merges deep technical expertise in Python/cloud infrastructure with strong business acumen "
                "to deliver outstanding software deliverables."
            ),
            "Creative": (
                "Passionate developer and tech explorer who blends clean code with innovative system designs. "
                "Dedicated to crafting elegant digital experiences, hacking together AI prototypes, and "
                "pushing the envelope of technology. Enjoys leveraging modern frontend framworks alongside "
                "robust API systems to solve real-world problems in unique and engaging ways."
            )
        }
        
        return f"### Rewritten Summary ({tone} Tone - Offline Simulation Mode)\n\n{summaries[tone]}"

    def _mock_interview_questions(self, prompt):
        # Look for skills in prompt to tailor questions
        techs = ["python", "react", "sql", "javascript", "docker", "django", "fastapi"]
        matched_tech = "Software Engineering"
        for t in techs:
            if t in prompt.lower():
                matched_tech = t.capitalize()
                break
                
        questions = [
            ("Technical", f"Explain how you would handle performance bottleneck issues in a {matched_tech}-based architecture? What steps would you take to profile and resolve it?",
             "Profile database queries, implement caching (Redis), optimize async calls, profile compute memory/CPU usage, load test."),
            ("Technical", f"What are the best practices for designing secure APIs in {matched_tech}? How do you handle authorization?",
             "Use HTTPS, implement OAuth2/JWT tokens, sanitize inputs, enforce rate limiting, use CORS headers properly."),
            ("HR/Behavioral", "Describe a time when you disagreed with a technical design decision. How did you resolve the conflict?",
             "Focus on data/metrics, build a quick prototype of both options, seek consensus, support the final decision productively."),
            ("HR/Behavioral", "How do you stay updated with emerging tech trends, especially around AI and modern architectures?",
             "Read newsletters (TLDR, HackerNews), build personal side projects, follow open-source repositories, read documentations."),
            ("System Design", "How would you design a rate limiter for an API endpoint that handles high traffic?",
             "Implement Token Bucket or Leaky Bucket algorithm, store requests/tokens in Redis, handle HTTP 429 Too Many Requests response.")
        ]
        
        output = f"### Generated Interview Questions ({matched_tech} Focus - Offline Simulation Mode)\n\n"
        for idx, (q_type, q, a) in enumerate(questions):
            output += f"**Q{idx+1} ({q_type}):** {q}\n"
            output += f"> *Suggested Guideline:* {a}\n\n"
        return output

    def _mock_skill_gap(self, prompt):
        # Parse the goal
        goal = "AI Engineer"
        for g in ["data analyst", "frontend engineer", "fullstack", "devops", "cloud engineer"]:
            if g in prompt.lower():
                goal = g.title()
                break
                
        skill_sets = {
            "AI Engineer": {
                "learn": ["PyTorch or TensorFlow", "NumPy & Pandas", "SQL & Vector Databases (Milvus/FAISS)", "Scikit-Learn", "LLM APIs & Prompt Engineering (LangChain/LlamaIndex)"],
                "time": "4-5 months"
            },
            "Data Analyst": {
                "learn": ["SQL (Advanced Queries)", "Excel / Google Sheets", "Tableau or PowerBI", "Python (Pandas, Matplotlib)", "A/B Testing & Statistics"],
                "time": "3 months"
            },
            "Frontend Engineer": {
                "learn": ["TypeScript", "Next.js / React Router", "CSS Frameworks (Tailwind CSS)", "Testing (Jest, Cypress)", "Web Performance Optimization"],
                "time": "3-4 months"
            },
            "DevOps": {
                "learn": ["Linux Administration", "Docker & Kubernetes", "CI/CD (GitHub Actions, GitLab CI)", "Terraform (IaC)", "Cloud Providers (AWS/GCP)"],
                "time": "5-6 months"
            },
            "default": {
                "learn": ["System Design Basics", "Docker Containers", "RESTful API Best Practices", "SQL & NoSQL Databases", "Unit Testing & Mocking"],
                "time": "3 months"
            }
        }
        
        selected = skill_sets.get(goal, skill_sets["default"])
        
        output = f"### Skill Gap Analysis for Target Role: **{goal}** (Offline Simulation Mode)\n\n"
        output += "#### 🛠 Current Skills (Detected from Resume)\n"
        output += "- Detected core coding languages & dev frameworks.\n\n"
        output += "#### 🚀 Need to Learn (Skills Gap)\n"
        for skill in selected["learn"]:
            output += f"- [ ] {skill}\n"
        output += f"\n#### ⏱ Estimated Time Commitment\n**{selected['time']}** (approx. 10-15 hours/week of dedicated study)\n\n"
        output += "*Recommendation:* Begin by building small projects incorporating 1-2 new skills, then document them on GitHub."
        return output

    def _mock_github_desc(self, prompt):
        # Generate project description based on repo info
        # Extract repo name or description if possible
        repo_name = "awesome-project"
        if "repo:" in prompt.lower():
            try:
                repo_name = prompt.split("repo:")[1].split()[0]
            except Exception:
                pass
                
        return (
            f"### Generated Project Description for `{repo_name}` (Offline Simulation Mode)\n\n"
            f"- Built and configured `{repo_name}` using modern development practices, optimizing code structure for clean maintainability.\n"
            f"- Implemented core components and integrated responsive API data flows, enhancing load efficiency.\n"
            f"- Structured project repository architecture to allow automated deployments and simplified codebase navigation."
        )

    def _mock_general_chat(self, prompt):
        responses = [
            "Your resume looks solid overall! To improve your ATS score, make sure you quantify your bullet points with metrics (e.g., 'saved 10 hours per week' or 'optimized API speed by 25%').",
            "I noticed you have strong Python skills. Have you considered adding a project showcasing REST API development using FastAPI or Flask? That is highly in-demand.",
            "Adding clear subheadings like 'Professional Experience', 'Projects', and 'Skills' makes it easier for both human recruiters and ATS parsing software to read your resume.",
            "Make sure your contact information is up-to-date and include clickable links to your GitHub and LinkedIn profiles directly in the header section.",
            "When describing your work experience, try using the CAR framework: Context, Action, Result. Start each bullet point with a powerful action verb!"
        ]
        return f"### AI Resume Assistant (Offline Simulation Mode)\n\n{random.choice(responses)}\n\n*Type another question to chat further! If you have a Gemini or OpenAI API Key, you can configure it in the **Settings** tab for real-time intelligent responses.*"
