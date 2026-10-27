# AI Resume Studio 🚀

**Build. Optimize. Analyze. Get Hired.**

AI Resume Studio is available as both a Python desktop application and a browser-based web app. Use the web app to build resumes, check ATS keyword matches, get AI writing help, import public GitHub projects, and generate a responsive portfolio page.

---

## Desktop App Features

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

## Browser App Features

- Resume editing, local browser storage, multiple versions, and JSON import/export.
- Local resume-strength and job-description keyword checks.
- AI writing requests through a Vercel function using a key entered for that session.
- Public GitHub repository import, print-ready resume previews, and downloadable portfolio pages.

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
├── index.html                # Browser app entry point
├── app.js                    # Browser app and local resume storage
├── styles.css                # Responsive web app styles
├── api/
│   └── ai.js                 # Vercel serverless AI proxy
├── main.py                   # Desktop app entry point
├── requirements.txt          # Desktop Python dependencies
├── config.json               # Local desktop configuration (ignored by Git)
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

### Deploying the web app to Vercel

The desktop application uses Tkinter and cannot run in a browser. This repository also includes a browser-based version that Vercel can host.

1. Push this repository to GitHub.
2. In Vercel, choose **Add New → Project** and import the repository.
3. Keep the project root set to the repository root. No build command or output directory is required; Vercel serves `index.html` and deploys the AI endpoint in `api/ai.js`.
4. Deploy. The web app stores resume versions in the browser's local storage. Use **Export JSON** to back up or move a resume between devices.
5. To use the AI assistant, provide an OpenAI or Gemini API key in the assistant screen. The key is used only for that request and is not saved by the app. Your key provider may charge for API usage.

You can also try the browser version locally by running `py -m http.server 8000` from the project folder and opening `http://localhost:8000`. Static features work locally; the AI endpoint is available after deploying to Vercel.

### Running the desktop app

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
