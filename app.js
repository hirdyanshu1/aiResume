const STORAGE_KEY = "ai-resume-studio-web-v1";

const EMPTY_RESUME = {
  personal: { name: "", title: "", email: "", phone: "", location: "", website: "", github: "", linkedin: "" },
  summary: "",
  experiences: [],
  projects: [],
  education: [],
  skills: []
};

const PERSONAL_FIELDS = [
  ["name", "Full name"], ["title", "Professional title"], ["email", "Email"], ["phone", "Phone"],
  ["location", "Location"], ["website", "Website"], ["github", "GitHub URL"], ["linkedin", "LinkedIn URL"]
];
const ENTRY_FIELDS = {
  experiences: [["role", "Job title"], ["company", "Company"], ["location", "Location"], ["start_date", "Start date"], ["end_date", "End date"], ["bullets", "Achievements (one per line)", "textarea"]],
  projects: [["name", "Project name"], ["technologies", "Technologies"], ["date", "Date"], ["link", "Project URL"], ["bullets", "Details (one per line)", "textarea"]],
  education: [["institution", "Institution"], ["degree", "Degree"], ["start_date", "Start date"], ["end_date", "End date"], ["gpa", "GPA"]]
};
const VIEW_TITLES = {
  dashboard: ["YOUR CAREER WORKSPACE", "Overview"],
  editor: ["RESUME BUILDER", "Resume editor"],
  matcher: ["ATS & JOB MATCHER", "ATS match"],
  assistant: ["AI WRITING ASSISTANT", "AI assistant"],
  github: ["PROJECT IMPORTER", "GitHub projects"],
  portfolio: ["PORTFOLIO GENERATOR", "Portfolio"]
};
const TECH_KEYWORDS = [
  "python", "javascript", "typescript", "c++", "c#", "java", "ruby", "golang", "php", "rust", "scala", "kotlin", "swift", "html", "css", "sql",
  "react", "angular", "vue", "next.js", "django", "flask", "fastapi", "spring", "express", "laravel", "rails", "svelte", "jquery", "bootstrap", "tailwind",
  "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "git", "github", "gitlab", "terraform", "ansible", "nginx", "firebase", "postman",
  "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "mariadb", "cassandra", "dynamodb", "elasticsearch",
  "machine learning", "deep learning", "nlp", "llm", "neural networks", "tensorflow", "pytorch", "scikit-learn", "numpy", "pandas", "data science", "statistics", "computer vision", "transformers"
];

let state = { resumes: {}, active: "My Resume" };
let toastTimer;
let githubRepos = [];

const byId = (id) => document.getElementById(id);
const currentResume = () => state.resumes[state.active];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function safeUrl(value) {
  const candidate = String(value || "").trim();
  try {
    const url = new URL(candidate);
    if (["https:", "http:", "mailto:"].includes(url.protocol)) return url.href;
  } catch {}
  return "";
}

function normalizeResume(value) {
  const resume = structuredClone(EMPTY_RESUME);
  if (!value || typeof value !== "object" || Array.isArray(value)) return resume;
  if (value.personal && typeof value.personal === "object") {
    for (const [key] of PERSONAL_FIELDS) resume.personal[key] = String(value.personal[key] ?? "");
  }
  resume.summary = String(value.summary ?? "");
  for (const key of ["experiences", "projects", "education"]) {
    resume[key] = Array.isArray(value[key]) ? value[key].filter((item) => item && typeof item === "object").map((item) => {
      const clean = {};
      for (const [field] of ENTRY_FIELDS[key]) clean[field] = field === "bullets"
        ? Array.isArray(item[field]) ? item[field].join("\n") : String(item[field] ?? "")
        : String(item[field] ?? "");
      return clean;
    }) : [];
  }
  resume.skills = Array.isArray(value.skills) ? value.skills.map(String) : typeof value.skills === "string" ? value.skills.split(",").map((skill) => skill.trim()).filter(Boolean) : [];
  return resume;
}

function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed && parsed.resumes && typeof parsed.resumes === "object" && Object.keys(parsed.resumes).length) {
        state.resumes = Object.fromEntries(Object.entries(parsed.resumes).map(([name, resume]) => [name, normalizeResume(resume)]));
        state.active = state.resumes[parsed.active] ? parsed.active : Object.keys(state.resumes)[0];
        return;
      }
    }
    state = { resumes: { "My Resume": normalizeResume(EMPTY_RESUME) }, active: "My Resume" };
    saveState(false);
  } catch (error) {
    console.error("Could not load saved resumes.", error);
    state = { resumes: { "My Resume": normalizeResume(EMPTY_RESUME) }, active: "My Resume" };
    showToast("Saved resume data could not be read. A new blank resume has been opened.", true);
  }
}

function saveState(showMessage = true) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    if (showMessage) showToast("Changes saved in this browser.");
  } catch (error) {
    console.error("Could not save resume data.", error);
    showToast("Could not save in this browser. Export a JSON backup or free up browser storage.", true);
  }
}

function showToast(message, isError = false) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3300);
}

function showView(name) {
  if (!VIEW_TITLES[name]) return;
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === `view-${name}`));
  document.querySelectorAll(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.view === name));
  byId("section-eyebrow").textContent = VIEW_TITLES[name][0];
  byId("page-title").textContent = VIEW_TITLES[name][1];
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateResumePicker() {
  const picker = byId("resume-picker");
  picker.replaceChildren(...Object.keys(state.resumes).sort((a, b) => a.localeCompare(b)).map((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    option.selected = name === state.active;
    return option;
  }));
}

function renderEntries(section, containerId) {
  const container = byId(containerId);
  const entries = currentResume()[section];
  const fields = ENTRY_FIELDS[section];
  container.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = `No ${section === "education" ? "education entries" : section} added yet.`;
    container.append(empty);
  }
  entries.forEach((entry, index) => {
    const card = document.createElement("article");
    card.className = "entry-card";
    const head = document.createElement("div");
    head.className = "entry-card-head";
    const title = document.createElement("span");
    title.textContent = entry.role || entry.name || entry.institution || `${section.slice(0, -1)} ${index + 1}`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove-entry";
    remove.dataset.removeSection = section;
    remove.dataset.index = String(index);
    remove.textContent = "Remove";
    head.append(title, remove);
    const grid = document.createElement("div");
    grid.className = "entry-fields";
    for (const [field, label, type] of fields) {
      const wrapper = document.createElement("label");
      wrapper.className = `field${type === "textarea" ? " full-width" : ""}`;
      const labelText = document.createElement("span");
      labelText.textContent = label;
      const control = document.createElement(type === "textarea" ? "textarea" : "input");
      if (type !== "textarea") control.type = "text";
      else control.rows = 3;
      control.value = entry[field] || "";
      control.dataset.section = section;
      control.dataset.index = String(index);
      control.dataset.field = field;
      control.placeholder = type === "textarea" ? "Add one item per line" : label;
      wrapper.append(labelText, control);
      grid.append(wrapper);
    }
    card.append(head, grid);
    container.append(card);
  });
}

function renderEditor() {
  const personal = byId("personal-fields");
  personal.replaceChildren();
  for (const [key, label] of PERSONAL_FIELDS) {
    const wrapper = document.createElement("label");
    wrapper.className = "field";
    const labelText = document.createElement("span");
    labelText.textContent = label;
    const input = document.createElement("input");
    input.type = key === "email" ? "email" : "text";
    input.value = currentResume().personal[key] || "";
    input.name = `personal.${key}`;
    input.dataset.personal = key;
    input.autocomplete = key === "name" ? "name" : key === "email" ? "email" : "off";
    wrapper.append(labelText, input);
    personal.append(wrapper);
  }
  byId("resume-form").elements.summary.value = currentResume().summary;
  byId("resume-form").elements.skills.value = currentResume().skills.join(", ");
  renderEntries("experiences", "experience-list");
  renderEntries("projects", "project-list");
  renderEntries("education", "education-list");
}

function updateDashboard() {
  const resume = currentResume();
  const score = getResumeScore(resume).score;
  byId("dash-score").textContent = `${score}%`;
  byId("dash-score-note").textContent = score >= 75 ? "A strong foundation" : score >= 45 ? "A few areas to improve" : "Add your details to get started";
  byId("dash-experience").textContent = resume.experiences.length;
  byId("dash-projects").textContent = resume.projects.length;
  byId("dash-skills").textContent = resume.skills.length;
  byId("portfolio-name").textContent = resume.personal.name || "Your Name";
  byId("portfolio-title").textContent = resume.personal.title || "Your professional title";
}

function getResumeScore(resume) {
  const suggestions = [];
  const personal = resume.personal;
  const contactCount = ["name", "email", "phone", "location"].filter((key) => personal[key]?.trim()).length;
  let score = contactCount * 5;
  if (!personal.linkedin?.trim()) suggestions.push("Add a LinkedIn profile link to your contact details.");
  if (!personal.github?.trim()) suggestions.push("Add a GitHub profile link if you have relevant projects.");
  if (resume.summary.trim().length > 100) score += 15;
  else if (resume.summary.trim().length > 25) score += 8;
  else suggestions.push("Write a concise professional summary describing your experience and strengths.");
  if (resume.experiences.length >= 2) score += 15;
  else if (resume.experiences.length === 1) score += 10;
  else suggestions.push("Add work experience, internships, freelance work, or open-source contributions.");
  const bullets = resume.experiences.flatMap((entry) => splitLines(entry.bullets));
  if (bullets.length >= 4) score += 5;
  else suggestions.push("Add more achievement-focused bullet points under your experience.");
  if (bullets.some((line) => /\d+%|\$\d+|\b\d+\s*(?:years|users|hours|projects|x)\b/i.test(line))) score += 5;
  else suggestions.push("Where accurate, quantify results with metrics such as time saved, growth, or scale.");
  if (resume.projects.length >= 2) score += 10;
  else if (resume.projects.length === 1) score += 5;
  else suggestions.push("Add relevant projects to show practical experience.");
  if (resume.projects.some((project) => project.link.trim())) score += 5;
  else if (resume.projects.length) suggestions.push("Add a working link to a project or repository.");
  if (resume.education.length) score += 12;
  else suggestions.push("Add your education or relevant training.");
  if (resume.skills.length >= 5) score += 15;
  else if (resume.skills.length) score += 8;
  else suggestions.push("List relevant skills and tools from the job descriptions you are targeting.");
  if (resume.experiences.length && resume.experiences.every((entry) => entry.role.trim() && entry.company.trim())) score += 5;
  return { score: Math.min(score, 100), suggestions };
}

function updateATS() {
  const { score, suggestions } = getResumeScore(currentResume());
  byId("ats-score").textContent = String(score);
  byId("score-ring").style.borderColor = score >= 75 ? "#64d6a5" : score >= 45 ? "#a78bfa" : "#7f8798";
  byId("ats-grade").textContent = score >= 75 ? "Strong foundation" : score >= 45 ? "Good start" : "Room to grow";
  byId("ats-summary").textContent = score >= 75 ? "Your resume has many key sections in place." : "Use these suggestions as a checklist, then tailor the resume to each role.";
  const list = byId("ats-suggestions");
  list.replaceChildren();
  (suggestions.length ? suggestions : ["Your resume covers the key basics. Tailor the details to each role."]).forEach((suggestion) => {
    const item = document.createElement("li");
    item.textContent = suggestion;
    list.append(item);
  });
}

function fullResumeText(resume) {
  return [
    ...Object.values(resume.personal), resume.summary, ...resume.skills,
    ...resume.experiences.flatMap((entry) => [entry.role, entry.company, entry.location, entry.bullets]),
    ...resume.projects.flatMap((entry) => [entry.name, entry.technologies, entry.bullets]),
    ...resume.education.flatMap((entry) => [entry.institution, entry.degree])
  ].join(" ").toLowerCase();
}

function uniqueKeywords(text) {
  const lower = text.toLowerCase();
  return [...new Set(TECH_KEYWORDS.filter((keyword) => {
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`(^|[^a-z0-9+#])${escaped}($|[^a-z0-9+#])`, "i").test(lower);
  }))];
}

function analyzeJobMatch() {
  const description = byId("job-description").value.trim();
  const result = byId("match-results");
  if (!description) {
    showToast("Paste a job description before analyzing.", true);
    return;
  }
  const jobKeywords = uniqueKeywords(description);
  const resumeKeywords = uniqueKeywords(fullResumeText(currentResume()));
  const found = jobKeywords.filter((keyword) => resumeKeywords.includes(keyword));
  const missing = jobKeywords.filter((keyword) => !resumeKeywords.includes(keyword));
  const score = jobKeywords.length ? Math.round((found.length / jobKeywords.length) * 100) : 0;
  result.replaceChildren();
  const scoreLine = document.createElement("div");
  scoreLine.className = "match-score";
  scoreLine.textContent = `${score}%`;
  const explanation = document.createElement("span");
  explanation.textContent = `keyword overlap · ${found.length} of ${jobKeywords.length} detected job keywords`;
  scoreLine.append(explanation);
  result.append(scoreLine);
  result.append(createKeywordGroup("Found in your resume", found, false));
  result.append(createKeywordGroup("Consider adding if accurate", missing, true));
  if (!jobKeywords.length) {
    const note = document.createElement("p");
    note.className = "muted";
    note.textContent = "No supported technology keywords were detected. Review the job post manually for role-specific language.";
    result.append(note);
  }
}

function createKeywordGroup(title, keywords, missing) {
  const wrapper = document.createElement("div");
  const heading = document.createElement("strong");
  heading.textContent = title;
  heading.style.fontSize = "11px";
  const chips = document.createElement("div");
  chips.className = "keyword-list";
  if (keywords.length) keywords.forEach((keyword) => {
    const chip = document.createElement("span");
    chip.className = `keyword${missing ? " missing" : ""}`;
    chip.textContent = keyword;
    chips.append(chip);
  });
  else {
    const none = document.createElement("p");
    none.className = "muted";
    none.textContent = "None detected.";
    chips.append(none);
  }
  wrapper.append(heading, chips);
  return wrapper;
}

function splitLines(value) {
  return String(value || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
}

function handleResumeEdit(event) {
  const target = event.target;
  if (target.dataset.personal) {
    currentResume().personal[target.dataset.personal] = target.value;
  } else if (target.name === "summary") {
    currentResume().summary = target.value;
  } else if (target.name === "skills") {
    currentResume().skills = target.value.split(",").map((skill) => skill.trim()).filter(Boolean);
  } else if (target.dataset.section && target.dataset.field) {
    const entry = currentResume()[target.dataset.section][Number(target.dataset.index)];
    if (entry) entry[target.dataset.field] = target.value;
    if (target.dataset.field === "bullets") entry[target.dataset.field] = target.value;
    const title = target.closest(".entry-card")?.querySelector(".entry-card-head span");
    if (title && ["role", "name", "institution"].includes(target.dataset.field)) title.textContent = target.value || `${target.dataset.section.slice(0, -1)} ${Number(target.dataset.index) + 1}`;
  } else {
    return;
  }
  saveState(false);
  updateDashboard();
  updateATS();
}

function createPrintableResume(resume, style = "modern") {
  const personal = resume.personal;
  const contact = [personal.email, personal.phone, personal.location, personal.website, personal.linkedin, personal.github].filter(Boolean).map(escapeHtml).join(" <span>·</span> ");
  const list = (items) => items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const experience = resume.experiences.map((item) => `<article><div class="entry-head"><div><h3>${escapeHtml(item.role)}</h3><strong>${escapeHtml(item.company)}</strong></div><span>${escapeHtml([item.start_date, item.end_date].filter(Boolean).join(" – "))}</span></div><p class="sub">${escapeHtml(item.location)}</p><ul>${list(splitLines(item.bullets))}</ul></article>`).join("");
  const projects = resume.projects.map((item) => {
    const link = safeUrl(item.link);
    return `<article><div class="entry-head"><div><h3>${escapeHtml(item.name)}</h3><span>${escapeHtml(item.technologies)}</span></div><span>${escapeHtml(item.date)}</span></div>${link ? `<a href="${escapeHtml(link)}" rel="noreferrer">${escapeHtml(item.link)}</a>` : ""}<ul>${list(splitLines(item.bullets))}</ul></article>`;
  }).join("");
  const education = resume.education.map((item) => `<article class="entry-head"><div><h3>${escapeHtml(item.degree)}</h3><strong>${escapeHtml(item.institution)}</strong></div><span>${escapeHtml([item.start_date, item.end_date].filter(Boolean).join(" – "))}${item.gpa ? ` · GPA ${escapeHtml(item.gpa)}` : ""}</span></article>`).join("");
  const section = (title, content) => content ? `<section><h2>${title}</h2>${content}</section>` : "";
  const skills = resume.skills.map(escapeHtml).join(" · ");
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${escapeHtml(personal.name || "Resume")}</title><style>
    *{box-sizing:border-box}body{max-width:850px;margin:40px auto;padding:0 40px;color:#242837;font:14px/1.55 Arial,sans-serif}.resume-header{padding-bottom:18px;border-bottom:2px solid #7458b8}.creative .resume-header{border:0;background:#f3effb;padding:25px}.classic .resume-header{text-align:center;border-color:#393939}.resume-header h1{margin:0;font-size:32px;letter-spacing:-.7px}.resume-header h2{margin:4px 0 9px;color:#6b5b8c;font-size:16px}.contact{color:#626b7a;font-size:11px}.contact span{padding:0 3px;color:#aaa}.summary{margin-top:17px}section{margin-top:20px}section>h2{padding-bottom:5px;border-bottom:1px solid #dfe1e8;color:#674da5;font-size:13px;letter-spacing:1px;text-transform:uppercase}.entry-head{display:flex;justify-content:space-between;gap:12px}.entry-head h3{margin:9px 0 1px;font-size:14px}.entry-head strong,.entry-head span,.sub{color:#666e7e;font-size:11px}.entry-head>span{text-align:right}article{margin:9px 0 13px}ul{margin:6px 0;padding-left:18px}li{margin:3px 0}a{color:#674da5;font-size:11px}.skills{color:#50596a}.print{position:fixed;right:20px;top:15px;padding:9px 14px;border:0;border-radius:6px;background:#7458b8;color:white;cursor:pointer}@media print{body{margin:0 auto;padding:0 25px}.print{display:none}}@media(max-width:600px){body{padding:0 20px}.entry-head{flex-direction:column;gap:0}.entry-head>span{text-align:left}}</style></head><body class="${style}"><button class="print" onclick="window.print()">Print / Save PDF</button><header class="resume-header"><h1>${escapeHtml(personal.name || "Your Name")}</h1><h2>${escapeHtml(personal.title)}</h2><div class="contact">${contact}</div></header>${resume.summary ? `<section class="summary"><p>${escapeHtml(resume.summary)}</p></section>` : ""}${section("Experience", experience)}${section("Projects", projects)}${section("Education", education)}${section("Skills", skills ? `<p class="skills">${skills}</p>` : "")}</body></html>`;
}

function openPreview(html) {
  byId("preview-frame").srcdoc = html;
  byId("preview-dialog").showModal();
}

function downloadFile(filename, content, mime) {
  const link = document.createElement("a");
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function exportResume() {
  const safeName = state.active.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "resume";
  downloadFile(`${safeName}.json`, JSON.stringify(currentResume(), null, 2), "application/json");
}

async function importResumeFile(file) {
  try {
    const data = normalizeResume(JSON.parse(await file.text()));
    const name = window.prompt("Name this resume version:", "Imported Resume");
    if (!name?.trim()) return;
    state.resumes[name.trim()] = data;
    state.active = name.trim();
    saveState(false);
    renderAll();
    showToast("Resume imported.");
  } catch (error) {
    console.error("Resume import failed.", error);
    showToast("Could not import that file. Choose a valid resume JSON file.", true);
  }
}

function createPortfolioPage(style) {
  const data = currentResume();
  const colors = {
    modern: ["#111827", "#8b5cf6", "#f9fafb"],
    classic: ["#f5f2eb", "#315c50", "#20241f"],
    creative: ["#20152e", "#f08c62", "#fff8f1"]
  }[style] || ["#111827", "#8b5cf6", "#f9fafb"];
  const projects = data.projects.map((project) => {
    const link = safeUrl(project.link);
    return `<article class="card"><h3>${escapeHtml(project.name)}</h3><p class="muted">${escapeHtml(project.technologies)}</p><p>${splitLines(project.bullets).map(escapeHtml).join("<br>")}</p>${link ? `<a href="${escapeHtml(link)}" target="_blank" rel="noreferrer">View project ↗</a>` : ""}</article>`;
  }).join("");
  const experience = data.experiences.map((entry) => `<article class="card"><div class="row"><h3>${escapeHtml(entry.role)} · ${escapeHtml(entry.company)}</h3><span>${escapeHtml([entry.start_date, entry.end_date].filter(Boolean).join(" – "))}</span></div><ul>${splitLines(entry.bullets).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul></article>`).join("");
  const contact = [
    ["Email", data.personal.email, safeUrl(`mailto:${data.personal.email}`)],
    ["GitHub", "GitHub", safeUrl(data.personal.github)],
    ["LinkedIn", "LinkedIn", safeUrl(data.personal.linkedin)],
    ["Website", data.personal.website, safeUrl(data.personal.website)]
  ].filter((item) => item[2]);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${escapeHtml(data.personal.name || "Portfolio")}</title><style>
    :root{--bg:${colors[0]};--accent:${colors[1]};--fg:${colors[2]}}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 Arial,sans-serif}main{width:min(920px,calc(100% - 40px));margin:auto}.hero{padding:100px 0 70px;border-bottom:1px solid color-mix(in srgb,var(--fg) 20%,transparent)}.tag{color:var(--accent);font-size:12px;font-weight:bold;letter-spacing:2px;text-transform:uppercase}.hero h1{max-width:740px;margin:10px 0;font-size:clamp(42px,8vw,76px);line-height:1.04;letter-spacing:-3px}.hero h2{margin:0;color:color-mix(in srgb,var(--fg) 70%,transparent);font-size:clamp(18px,3vw,25px);font-weight:400}.hero p{max-width:660px;color:color-mix(in srgb,var(--fg) 75%,transparent)}.links{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}.links a,.card a{color:var(--accent);text-decoration:none}.links a{padding:8px 11px;border:1px solid color-mix(in srgb,var(--fg) 25%,transparent);border-radius:8px;font-size:13px}section{padding:35px 0;border-bottom:1px solid color-mix(in srgb,var(--fg) 18%,transparent)}section h2{font-size:13px;letter-spacing:2px;text-transform:uppercase}.card{margin:14px 0;padding:19px;border:1px solid color-mix(in srgb,var(--fg) 17%,transparent);border-radius:12px;background:color-mix(in srgb,var(--fg) 5%,transparent)}.card h3{margin:0;font-size:17px}.card p,.card li{color:color-mix(in srgb,var(--fg) 76%,transparent)}.card ul{padding-left:20px}.muted{opacity:.7}.row{display:flex;justify-content:space-between;gap:15px}.row span{opacity:.65;font-size:12px}.skills{display:flex;flex-wrap:wrap;gap:8px}.skills span{padding:7px 10px;border:1px solid color-mix(in srgb,var(--fg) 22%,transparent);border-radius:30px;font-size:13px}@media(max-width:600px){.hero{padding:65px 0 45px}.hero h1{letter-spacing:-2px}.row{flex-direction:column;gap:4px}}</style></head><body><main><header class="hero"><span class="tag">Portfolio</span><h1>${escapeHtml(data.personal.name || "Your Name")}</h1><h2>${escapeHtml(data.personal.title || "Your professional title")}</h2><p>${escapeHtml(data.summary)}</p><nav class="links">${contact.map(([label, text, href]) => `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}${label === "Email" ? ` · ${escapeHtml(text)}` : " ↗"}</a>`).join("")}</nav></header>${experience ? `<section><h2>Experience</h2>${experience}</section>` : ""}${projects ? `<section><h2>Selected projects</h2>${projects}</section>` : ""}${data.skills.length ? `<section><h2>Skills</h2><div class="skills">${data.skills.map((skill) => `<span>${escapeHtml(skill)}</span>`).join("")}</div></section>` : ""}${data.education.length ? `<section><h2>Education</h2>${data.education.map((item) => `<article class="card"><h3>${escapeHtml(item.degree)}</h3><div class="muted">${escapeHtml(item.institution)} · ${escapeHtml([item.start_date, item.end_date].filter(Boolean).join(" – "))}</div></article>`).join("")}</section>` : ""}</main></body></html>`;
}

async function sendAIRequest() {
  const prompt = byId("ai-prompt").value.trim();
  const apiKey = byId("ai-key").value.trim();
  const provider = byId("ai-provider").value;
  if (!prompt) {
    showToast("Enter a request for the assistant.", true);
    return;
  }
  if (!apiKey) {
    showToast("Enter your API key to use the AI assistant.", true);
    byId("ai-key").focus();
    return;
  }
  const button = byId("ai-send");
  button.disabled = true;
  button.textContent = "Generating…";
  byId("ai-response").textContent = "Working on your request…";
  try {
    const response = await fetch("/api/ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider,
        apiKey,
        prompt,
        resume: currentResume()
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `AI request failed (${response.status}).`);
    byId("ai-response").textContent = result.text;
  } catch (error) {
    console.error("AI request failed.", error);
    byId("ai-response").textContent = error.message || "Could not reach the AI service.";
    showToast(error.message || "Could not reach the AI service.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = "Generate response <span>→</span>";
  }
}

async function searchGitHub(event) {
  event.preventDefault();
  const username = byId("github-username").value.trim();
  const results = byId("github-results");
  const importButton = byId("import-repos");
  results.textContent = "Searching GitHub…";
  importButton.disabled = true;
  try {
    const response = await fetch(`https://api.github.com/users/${encodeURIComponent(username)}/repos?per_page=100&sort=updated`, {
      headers: { Accept: "application/vnd.github+json" }
    });
    if (response.status === 404) throw new Error("GitHub username not found.");
    if (!response.ok) throw new Error(`GitHub returned an error (${response.status}).`);
    const repos = await response.json();
    githubRepos = repos.filter((repo) => !repo.fork).map((repo) => ({
      name: repo.name,
      description: repo.description || "No description provided.",
      stars: repo.stargazers_count || 0,
      language: repo.language || "Other",
      url: repo.html_url,
      updated_at: (repo.updated_at || "").slice(0, 10)
    })).sort((a, b) => b.stars - a.stars || b.updated_at.localeCompare(a.updated_at));
    renderGitHubResults();
    if (!githubRepos.length) showToast("No original public repositories were found for that user.");
  } catch (error) {
    results.textContent = "";
    const message = document.createElement("div");
    message.className = "empty-state";
    message.textContent = error.message;
    results.append(message);
    showToast(error.message, true);
  }
}

function renderGitHubResults() {
  const container = byId("github-results");
  container.replaceChildren();
  if (!githubRepos.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No original public repositories found.";
    container.append(empty);
    return;
  }
  githubRepos.forEach((repo, index) => {
    const label = document.createElement("label");
    label.className = "repo-card";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = String(index);
    checkbox.className = "repo-select";
    checkbox.addEventListener("change", () => {
      byId("import-repos").disabled = !document.querySelector(".repo-select:checked");
    });
    const content = document.createElement("span");
    content.className = "repo-card-content";
    content.innerHTML = `<strong>${escapeHtml(repo.name)}</strong><p>${escapeHtml(repo.description)}</p><span class="repo-meta"><span>${escapeHtml(repo.language)}</span><span>★ ${repo.stars}</span><span>Updated ${escapeHtml(repo.updated_at)}</span></span>`;
    label.append(checkbox, content);
    container.append(label);
  });
}

function importSelectedRepos() {
  const selected = [...document.querySelectorAll(".repo-select:checked")].map((checkbox) => githubRepos[Number(checkbox.value)]).filter(Boolean);
  if (!selected.length) return;
  for (const repo of selected) {
    if (currentResume().projects.some((project) => project.link === repo.url)) continue;
    currentResume().projects.push({
      name: repo.name, technologies: repo.language, date: repo.updated_at, link: repo.url,
      bullets: repo.description
    });
  }
  saveState(false);
  renderEditor();
  updateDashboard();
  updateATS();
  showToast(`${selected.length} project${selected.length === 1 ? "" : "s"} added to your resume.`);
}

function renderAll() {
  updateResumePicker();
  renderEditor();
  updateDashboard();
  updateATS();
}

function createNewVersion() {
  const name = window.prompt("Name your new resume version:", "New Resume");
  if (!name?.trim()) return;
  const cleanName = name.trim();
  if (state.resumes[cleanName] && !window.confirm(`"${cleanName}" already exists. Replace it?`)) return;
  state.resumes[cleanName] = normalizeResume(currentResume());
  state.active = cleanName;
  saveState(false);
  renderAll();
  showToast(`"${cleanName}" is now your active resume.`);
}

function bindEvents() {
  document.querySelector(".brand").addEventListener("click", (event) => {
    event.preventDefault();
    showView("dashboard");
  });
  document.querySelectorAll(".nav-link").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
  document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.go)));
  byId("resume-picker").addEventListener("change", (event) => {
    state.active = event.target.value;
    saveState(false);
    renderAll();
  });
  byId("new-version-button").addEventListener("click", createNewVersion);
  byId("save-button").addEventListener("click", () => saveState(true));
  byId("resume-form").addEventListener("input", handleResumeEdit);
  byId("resume-form").addEventListener("click", (event) => {
    const addButton = event.target.closest("[data-add]");
    const removeButton = event.target.closest("[data-remove-section]");
    if (addButton) {
      const section = addButton.dataset.add;
      const item = Object.fromEntries(ENTRY_FIELDS[section].map(([key]) => [key, ""]));
      currentResume()[section].push(item);
      saveState(false);
      renderEditor();
      updateDashboard();
    }
    if (removeButton) {
      const section = removeButton.dataset.removeSection;
      currentResume()[section].splice(Number(removeButton.dataset.index), 1);
      saveState(false);
      renderEditor();
      updateDashboard();
      updateATS();
    }
  });
  byId("import-button").addEventListener("click", () => byId("import-file").click());
  byId("import-file").addEventListener("change", (event) => {
    const [file] = event.target.files;
    if (file) importResumeFile(file);
    event.target.value = "";
  });
  byId("export-button").addEventListener("click", exportResume);
  byId("preview-button").addEventListener("click", () => openPreview(createPrintableResume(currentResume())));
  byId("preview-close").addEventListener("click", () => byId("preview-dialog").close());
  byId("preview-dialog").addEventListener("click", (event) => {
    if (event.target === byId("preview-dialog")) byId("preview-dialog").close();
  });
  byId("match-button").addEventListener("click", analyzeJobMatch);
  byId("ai-send").addEventListener("click", sendAIRequest);
  document.querySelectorAll("[data-prompt]").forEach((button) => button.addEventListener("click", () => {
    byId("ai-prompt").value = button.dataset.prompt;
    showView("assistant");
    byId("ai-prompt").focus();
  }));
  byId("github-form").addEventListener("submit", searchGitHub);
  byId("import-repos").addEventListener("click", importSelectedRepos);
  byId("portfolio-preview").addEventListener("click", () => openPreview(createPortfolioPage(byId("portfolio-style").value)));
  byId("portfolio-download").addEventListener("click", () => {
    const name = currentResume().personal.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "portfolio";
    downloadFile(`${name}-portfolio.html`, createPortfolioPage(byId("portfolio-style").value), "text/html");
  });
}

loadState();
bindEvents();
renderAll();
