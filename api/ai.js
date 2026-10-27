const MAX_PROMPT_LENGTH = 12000;

function sendJson(res, status, value) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(value));
}

function resumeContext(resume) {
  if (!resume || typeof resume !== "object" || Array.isArray(resume)) return "";
  const personal = resume.personal && typeof resume.personal === "object" ? resume.personal : {};
  const sections = [
    `Name: ${String(personal.name || "").slice(0, 200)}`,
    `Title: ${String(personal.title || "").slice(0, 200)}`,
    `Summary: ${String(resume.summary || "").slice(0, 2500)}`,
    `Skills: ${Array.isArray(resume.skills) ? resume.skills.slice(0, 100).map((item) => String(item).slice(0, 100)).join(", ") : ""}`,
    `Experience: ${JSON.stringify(Array.isArray(resume.experiences) ? resume.experiences.slice(0, 15) : []).slice(0, 6000)}`,
    `Projects: ${JSON.stringify(Array.isArray(resume.projects) ? resume.projects.slice(0, 15) : []).slice(0, 4000)}`
  ];
  return sections.join("\n");
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return sendJson(res, 405, { error: "Use POST for AI requests." });
  }

  const body = typeof req.body === "string" ? (() => {
    try { return JSON.parse(req.body); } catch { return null; }
  })() : req.body;
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return sendJson(res, 400, { error: "Request body must be valid JSON." });
  }

  const provider = body.provider;
  const apiKey = typeof body.apiKey === "string" ? body.apiKey.trim() : "";
  const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";
  if (!["openai", "gemini"].includes(provider)) return sendJson(res, 400, { error: "Choose OpenAI or Google Gemini." });
  if (!apiKey || apiKey.length > 512) return sendJson(res, 400, { error: "A valid API key is required." });
  if (!prompt || prompt.length > MAX_PROMPT_LENGTH) return sendJson(res, 400, { error: `Prompt must be between 1 and ${MAX_PROMPT_LENGTH} characters.` });

  const context = resumeContext(body.resume);
  const fullPrompt = `${prompt}\n\nUse the following resume information as context. Do not invent facts or metrics:\n${context}`;
  const url = provider === "openai"
    ? "https://api.openai.com/v1/chat/completions"
    : `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${encodeURIComponent(apiKey)}`;
  const headers = { "Content-Type": "application/json" };
  let payload;

  if (provider === "openai") {
    headers.Authorization = `Bearer ${apiKey}`;
    payload = {
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a practical career writing assistant. Preserve the user's facts and never invent qualifications, numbers, or work history." },
        { role: "user", content: fullPrompt }
      ],
      max_tokens: 1200,
      temperature: 0.5
    };
  } else {
    payload = {
      contents: [{ parts: [{ text: `You are a practical career writing assistant. Preserve facts and never invent qualifications or metrics.\n\n${fullPrompt}` }] }],
      generationConfig: { maxOutputTokens: 1200, temperature: 0.5 }
    };
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(30000)
    });
    if (!response.ok) {
      return sendJson(res, 502, { error: `The ${provider === "openai" ? "OpenAI" : "Gemini"} request failed (HTTP ${response.status}). Check your API key and account access.` });
    }
    const result = await response.json();
    const text = provider === "openai"
      ? result.choices?.[0]?.message?.content
      : result.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("");
    if (typeof text !== "string" || !text.trim()) {
      return sendJson(res, 502, { error: "The AI provider returned an empty or unsupported response." });
    }
    return sendJson(res, 200, { text: text.trim() });
  } catch (error) {
    const timeout = error?.name === "TimeoutError" || error?.name === "AbortError";
    return sendJson(res, 502, { error: timeout ? "The AI request timed out. Please try again." : "Could not connect to the AI provider. Please try again." });
  }
}
