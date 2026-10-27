# AI Resume Studio 🚀

**Build. Optimize. Analyze. Get Hired.**

AI Resume Studio is a premium desktop application built in Python using **CustomTkinter**. It serves as an all-in-one suite for candidates to build high-quality resumes, analyze them against target job descriptions using ATS keyword matches, write optimized bullet points and summaries using AI, fetch project details directly from GitHub, practice mock interviews, and generate stunning responsive portfolio websites with a single click.

---

## Key Features

- 📑 **Resume Builder**: A form-based, multi-tab structured editor to manage personal details, professional experience, projects, education, and skills.
- 🎨 **HTML Resume Templates**: Support for multiple templates (Modern Minimalist, Traditional serif, Creative dual-column layout) featuring professional typography (Inter, Outfit, Georgia).
- 🖨️ **Browser-based Live Preview & PDF Export**: Real-time rendering of resumes to print-ready HTML files. Recruiter-ready PDF generation via the browser's native print controls.
- 📈 **Analytics Dashboard**: Instant scoring of resume strength, completeness checks, and quantitative metrics tracking.
- 🔍 **ATS Score & Job Matcher**: Real-time evaluation of how well a resume matches a target job description. Extracts missing tech keywords and provides actionable suggestions.
- 🧠 **AI Writing Assistant**:
  - **Bullet Point Optimizer**: Upgrades passive work descriptions into active, result-oriented statements.
  - **Summary Rewriter**: Rewrites summaries in selected tones (Professional, Confident, Creative).
- 💬 **Resume Chat**: Chat directly with your resume to identify weaknesses, skill gaps, and get recommendations.
- 🎯 **AI Interview Generator**: Generates 5 tailored technical and behavioral questions from the resume contents at different experience levels (Junior, Mid, Senior) with collapsible answer guidelines.
- 🐙 **GitHub Project Importer**: Fetches repositories for a username, allowing checkboxes imports. The AI auto-generates polished descriptions for the projects.
- 🌐 **Responsive Portfolio Website Generator**: Creates a complete responsive personal website folder containing `index.html` and `styles.css` with a built-in dark/light mode toggle.
- ⚙️ **Offline Fallback Simulation**: No API keys? No problem! The application features a robust offline heuristic model that simulates AI responses, making it fully testable out-of-the-box.

---

## Tech Stack

- **UI Framework**: CustomTkinter (Python GUI wrapper for modern widgets)
- **Networking**: Requests (API integrations)
- **AI Integrations**: Google Generative AI (Gemini API), OpenAI client (supporting OpenAI and local Ollama servers)
- **Data Manager**: Pure JSON serialization
- **Templates Engine**: Custom Regex-based micro-Mustache renderer (dependency-free)

---

## Folder Structure

```text
AI-Resume-Studio/
│
├── main.py                   # Entry point script
├── requirements.txt          # Python dependencies
├── config.json               # Local configuration file (created automatically)
│
├── core/                     # Business Logic Core
│   ├── __init__.py
│   ├── resume_manager.py     # JSON operations & version switching
│   ├── ai_service.py         # Gemini, OpenAI, & Offline simulation routing
│   ├── ats_analyzer.py       # ATS keyword scan & text similarity
│   ├── github_client.py      # GitHub API integrations
│   └── portfolio_builder.py  # Mustache templates compiler & portfolio generator
│
├── ui/                       # Modern Desktop GUI
│   ├── __init__.py
│   ├── app.py                # Main shell, sidebar, and routing
│   ├── styles.py             # Custom colors, fonts, and separators
│   ├── dashboard.py          # Metrics & ATS summary panel
│   ├── editor.py             # Resume forms & browser preview
│   ├── ai_assistant.py       # Bullet improver, Chat, & Interview prep
│   ├── ats_matcher.py        # ATS scores & Job Matcher panel
│   ├── github_import.py      # GitHub repo list checklist
│   └── portfolio_gen.py      # Portfolio site builder controls
│
└── templates/                # Resume templates
    ├── modern.html           # Sleek Inter-based template
    ├── traditional.html      # Centered serif Georgia template
    └── creative.html         # Dual-column Outfit-based template
```

---

## Setup & Execution

### Prerequisites

- Python 3.9 or higher installed on your system.

### Installation

1. Clone or download this project.
2. Navigate to the project root and install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

Run the following command to launch the GUI:
```bash
python main.py
```

### Configuring AI Settings

By default, the application runs in **Offline Simulator Mode** which requires no internet or setup. 
To connect a live AI model:
1. Navigate to the **Settings** tab in the sidebar.
2. Select your AI service (Gemini API, OpenAI API, or Local Ollama).
3. Enter your API Key or custom Base URL.
4. Click **Save Settings**.
