import re

# Standard list of tech keywords for local/offline analysis
TECH_KEYWORDS = {
    "languages": ["python", "javascript", "typescript", "c++", "c#", "java", "ruby", "golang", "php", "rust", "scala", "kotlin", "swift", "html", "css", "sql", "bash"],
    "frameworks": ["react", "angular", "vue", "next.js", "django", "flask", "fastapi", "spring", "express", "laravel", "rails", "svelte", "jquery", "bootstrap", "tailwind"],
    "tools_cloud": ["docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "git", "github", "gitlab", "terraform", "ansible", "nginx", "firebase", "clerk", "postman"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "sqlite", "sqlite3", "oracle", "mariadb", "cassandra", "dynamodb", "elasticsearch"],
    "concepts_ai": ["machine learning", "deep learning", "nlp", "llm", "neural networks", "tensorflow", "pytorch", "scikit-learn", "numpy", "pandas", "data science", "statistics", "computer vision", "transformers"]
}

# Standard English stopwords to filter out for keyword analysis
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "can't", "cannot", 
    "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", 
    "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", 
    "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", 
    "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", 
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", 
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", 
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", 
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", 
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", 
    "yours", "yourself", "yourselves"
}

class ATSAnalyzer:
    def __init__(self):
        pass

    def tokenize_and_clean(self, text):
        # Convert to lowercase and find words
        text = text.lower()
        words = re.findall(r'[a-z\+\#\.\-]+', text)
        return [w for w in words if w not in STOPWORDS and len(w) > 1]

    def extract_tech_keywords(self, word_list):
        detected = set()
        flat_keywords = []
        for category, list_of_tech in TECH_KEYWORDS.items():
            flat_keywords.extend(list_of_tech)
            
        word_set = set(word_list)
        for kw in flat_keywords:
            # Handle multi-word keywords like "machine learning"
            if " " in kw:
                # We'll check the raw text for this multi-word keyword
                pass
            elif kw in word_set:
                detected.add(kw)
                
        return list(detected)

    def calculate_ats_score(self, resume_data):
        score = 0
        details = {}
        suggestions = []
        
        # 1. Contact Information (Max 20 points)
        personal = resume_data.get("personal", {})
        contact_points = 0
        contact_items = ["name", "email", "phone", "location"]
        for item in contact_items:
            if personal.get(item, "").strip():
                contact_points += 4
        
        # GitHub & LinkedIn check
        has_linkedin = bool(personal.get("linkedin", "").strip())
        has_github = bool(personal.get("github", "").strip())
        
        if has_linkedin:
            contact_points += 2
        else:
            suggestions.append("Add your LinkedIn profile link to the contact details.")
            
        if has_github:
            contact_points += 2
        else:
            suggestions.append("Add your GitHub profile link to make it easy to inspect projects.")
            
        score += contact_points
        details["contact"] = f"{contact_points}/20"
        
        # 2. Professional Summary (Max 10 points)
        summary = resume_data.get("summary", "").strip()
        if len(summary) > 100:
            score += 10
            details["summary"] = "10/10"
        elif len(summary) > 20:
            score += 5
            details["summary"] = "5/10"
            suggestions.append("Expand your summary to describe your years of experience, core tech stack, and key value.")
        else:
            details["summary"] = "0/10"
            suggestions.append("Write a professional summary (3-4 sentences) outlining your background and career goals.")
            
        # 3. Work Experience (Max 25 points)
        experiences = resume_data.get("experiences", [])
        if len(experiences) >= 2:
            exp_points = 15
        elif len(experiences) == 1:
            exp_points = 10
            suggestions.append("Add more professional experience entries if available (internships, freelancing count!).")
        else:
            exp_points = 0
            suggestions.append("Add a Work Experience section. If none, list freelance work or open-source contribution.")
            
        # Check experience bullet point quality (do they contain numbers/metrics?)
        has_metrics = False
        total_bullets = 0
        metric_pattern = re.compile(r'\d+%|\d+\s*years|\$\d+|\d+\s*x|reduced\s*\d+|increased\s*\d+|saved\s*\d+')
        
        for exp in experiences:
            bullets = exp.get("bullets", [])
            total_bullets += len(bullets)
            for bullet in bullets:
                if metric_pattern.search(bullet.lower()):
                    has_metrics = True
                    
        if total_bullets >= 4:
            exp_points += 5
        else:
            suggestions.append("Add more descriptive bullet points under your work experience (aim for 3-4 per job).")
            
        if has_metrics:
            exp_points += 5
        else:
            suggestions.append("Quantify your accomplishments! Add metrics like percentage improvements, money saved, or hours reduced (e.g. 'optimized speed by 30%').")
            
        score += exp_points
        details["experience"] = f"{exp_points}/25"
        
        # 4. Projects (Max 15 points)
        projects = resume_data.get("projects", [])
        proj_points = 0
        if len(projects) >= 2:
            proj_points += 10
        elif len(projects) == 1:
            proj_points += 5
            suggestions.append("Include at least 2 strong side projects with links and bullet descriptions.")
        else:
            suggestions.append("Add a Projects section to showcase your hands-on building capabilities.")
            
        # Link check
        has_proj_links = any(bool(proj.get("link", "").strip()) for proj in projects)
        if has_proj_links:
            proj_points += 5
        else:
            if projects:
                suggestions.append("Include live links or repository URLs for your projects so recruiters can review them.")
                
        score += proj_points
        details["projects"] = f"{proj_points}/15"
        
        # 5. Education (Max 15 points)
        education = resume_data.get("education", [])
        edu_points = 0
        if len(education) >= 1:
            edu_points += 10
            # GPA check (optional point boost/verification)
            has_gpa = any(bool(edu.get("gpa", "").strip()) for edu in education)
            if has_gpa:
                edu_points += 5
            else:
                edu_points += 3 # standard if no GPA listed
        else:
            suggestions.append("Add your education details (degrees, bootcamps, or certifications).")
            
        score += edu_points
        details["education"] = f"{edu_points}/15"
        
        # 6. Skills Section (Max 15 points)
        skills = resume_data.get("skills", [])
        skills_points = 0
        if len(skills) >= 10:
            skills_points = 15
        elif len(skills) >= 5:
            skills_points = 10
            suggestions.append("Expand your skills list! Aim for at least 10 core technical languages, tools, or frameworks.")
        elif len(skills) > 0:
            skills_points = 5
            suggestions.append("Add more tags to your Skills list to trigger ATS keyword searches.")
        else:
            suggestions.append("Add a Skills section! This is critical for matching job keywords.")
            
        score += skills_points
        details["skills"] = f"{skills_points}/15"
        
        # Overall completion check
        details["completion"] = sum([
            bool(personal.get("name")),
            bool(personal.get("email")),
            bool(summary),
            len(experiences) > 0,
            len(projects) > 0,
            len(education) > 0,
            len(skills) > 0
        ]) / 7.0 * 100
        
        return {
            "score": score,
            "details": details,
            "suggestions": suggestions
        }

    def analyze_job_match(self, resume_data, job_description):
        if not job_description.strip():
            return {
                "match_percentage": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": ["Please enter a job description to perform matching."]
            }
            
        # 1. Compile resume text for search
        resume_text = ""
        personal = resume_data.get("personal", {})
        resume_text += f" {personal.get('title', '')}"
        resume_text += f" {resume_data.get('summary', '')}"
        
        for exp in resume_data.get("experiences", []):
            resume_text += f" {exp.get('role', '')} {exp.get('company', '')}"
            resume_text += f" {' '.join(exp.get('bullets', []))}"
            
        for proj in resume_data.get("projects", []):
            resume_text += f" {proj.get('name', '')} {proj.get('technologies', '')}"
            resume_text += f" {' '.join(proj.get('bullets', []))}"
            
        for edu in resume_data.get("education", []):
            resume_text += f" {edu.get('degree', '')} {edu.get('institution', '')}"
            
        resume_text += f" {' '.join(resume_data.get('skills', []))}"
        
        # 2. Tokenize resume and JD
        resume_words = self.tokenize_and_clean(resume_text)
        jd_words = self.tokenize_and_clean(job_description)
        
        # 3. Extract technical keywords from both
        resume_tech = set(self.extract_tech_keywords(resume_words))
        
        # Add exact matching skills list to be safe
        for skill in resume_data.get("skills", []):
            resume_tech.add(skill.lower())
            
        jd_tech = set(self.extract_tech_keywords(jd_words))
        
        # Fallback keyword scan: Check if any tech keyword in the categories is in the raw JD text
        # (This catches keywords that might be split differently or have special punctuation)
        raw_jd_lower = job_description.lower()
        for category, list_of_tech in TECH_KEYWORDS.items():
            for tech in list_of_tech:
                # Add word boundary matches
                pattern = r'\b' + re.escape(tech) + r'\b'
                # Handle things like c++ or c# which are not word boundary friendly
                if '++' in tech or '#' in tech or '.js' in tech:
                    pattern = re.escape(tech)
                if re.search(pattern, raw_jd_lower):
                    jd_tech.add(tech)
                    
        # 4. Calculate matches
        matched_keywords = list(jd_tech.intersection(resume_tech))
        missing_keywords = list(jd_tech.difference(resume_tech))
        
        # Sort for display
        matched_keywords.sort()
        missing_keywords.sort()
        
        # Calculate percentage
        if not jd_tech:
            # No tech keywords found in JD, do a general word matching percentage
            match_percentage = 40.0 # base match
        else:
            match_percentage = (len(matched_keywords) / len(jd_tech)) * 100.0
            
        # Add heuristics to refine match
        # If job title terms overlap, increase match
        title_matches = 0
        jd_title_terms = self.tokenize_and_clean(job_description.split("\n")[0]) # assume first line has title
        res_title_terms = self.tokenize_and_clean(personal.get("title", ""))
        for term in res_title_terms:
            if term in jd_title_terms and term not in ["developer", "engineer", "software", "junior", "senior", "lead"]:
                title_matches += 1
                
        if title_matches > 0:
            match_percentage = min(match_percentage + 15, 100.0)
            
        # Generate match recommendations
        suggestions = []
        if match_percentage < 50:
            suggestions.append("Your resume matches less than 50% of the job criteria. We highly recommend adding some of the missing keywords below.")
        elif match_percentage < 75:
            suggestions.append("Good match! Adding 2-3 of the missing keywords listed below could place you in the top tier of candidates.")
        else:
            suggestions.append("Excellent match! Your resume strongly aligns with this job description.")
            
        for kw in missing_keywords[:5]:
            suggestions.append(f"Consider adding practical experience or listing the skill **'{kw.capitalize()}'** in your resume.")
            
        return {
            "match_percentage": round(match_percentage),
            "matched_keywords": [k.capitalize() for k in matched_keywords],
            "missing_keywords": [k.capitalize() for k in missing_keywords],
            "suggestions": suggestions
        }
