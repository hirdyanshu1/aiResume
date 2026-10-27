import customtkinter as ctk
from tkinter import messagebox
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, COLOR_SUCCESS, COLOR_WARNING, get_font, create_section_header

class ATSMatcherPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Scrollable Layout
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # Header
        header = create_section_header(self.scroll_frame, "ATS Analyzer & Job Matcher")
        header.pack(fill="x", padx=10, pady=(0, 15))

        # Main Layout split: Left Side (Section Scores), Right Side (Job Description Matcher)
        self.split_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.split_frame.pack(fill="both", expand=True, padx=10)
        self.split_frame.grid_columnconfigure(0, weight=4)
        self.split_frame.grid_columnconfigure(1, weight=6)

        # LEFT SIDE: Section Breakdown
        self.left_panel = ctk.CTkFrame(self.split_frame, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        lbl_break = ctk.CTkLabel(self.left_panel, text="Resume Section Scores", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        lbl_break.pack(anchor="w", padx=15, pady=15)

        self.sec_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.sec_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.score_labels = {}
        sections = [
            ("contact", "Contact Info Header"),
            ("summary", "Professional Summary"),
            ("experience", "Work Experience"),
            ("projects", "Projects Section"),
            ("education", "Education History"),
            ("skills", "Technical Skills List")
        ]
        
        for key, display in sections:
            row = ctk.CTkFrame(self.sec_frame, fg_color="transparent", height=30)
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)
            
            lbl = ctk.CTkLabel(row, text=display, font=get_font(12), text_color=TEXT_MUTED)
            lbl.pack(side="left", padx=5)
            
            val = ctk.CTkLabel(row, text="0/0", font=get_font(12, "bold"), text_color=TEXT_MAIN)
            val.pack(side="right", padx=5)
            
            self.score_labels[key] = val

        # RIGHT SIDE: Job Description Matcher
        self.right_panel = ctk.CTkFrame(self.split_frame, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.right_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        lbl_jd = ctk.CTkLabel(self.right_panel, text="Job Description Matcher", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl_jd.pack(anchor="w", padx=15, pady=(15, 5))

        desc_jd = ctk.CTkLabel(self.right_panel, text="Paste a target job description below to check your resume compatibility, missing technical keywords, and suggested bullet points.", font=get_font(11), text_color=TEXT_MUTED, justify="left", wraplength=400)
        desc_jd.pack(anchor="w", padx=15, pady=(0, 10))

        # Text input for JD
        self.jd_input = ctk.CTkTextbox(self.right_panel, font=get_font(12), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, height=120)
        self.jd_input.pack(fill="x", padx=15, pady=5)

        # Match Button
        match_btn = ctk.CTkButton(
            self.right_panel,
            text="🔍 Calculate Match Percentage",
            font=get_font(12, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.run_job_matching
        )
        match_btn.pack(anchor="w", padx=15, pady=10)

        # RESULTS PANEL
        self.res_card = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.res_card.pack(fill="both", expand=True, padx=15, pady=5)

        # Matching score value
        score_row = ctk.CTkFrame(self.res_card, fg_color="transparent")
        score_row.pack(fill="x", pady=5)
        
        lbl_match = ctk.CTkLabel(score_row, text="Job Match Percentage:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        lbl_match.pack(side="left")
        
        self.match_val = ctk.CTkLabel(score_row, text="--%", font=get_font(18, "bold"), text_color=ACCENT_COLOR)
        self.match_val.pack(side="right")

        # Missing Keywords
        self.missing_lbl = ctk.CTkLabel(self.res_card, text="Missing Tech Keywords:", font=get_font(12, "bold"), text_color=COLOR_WARNING)
        self.missing_lbl.pack(anchor="w", pady=(10, 2))
        
        self.missing_tags_frame = ctk.CTkFrame(self.res_card, fg_color="transparent")
        self.missing_tags_frame.pack(fill="x", pady=2)
        
        self.missing_tags_lbl = ctk.CTkLabel(self.missing_tags_frame, text="No match run yet.", font=get_font(12, "italic"), text_color=TEXT_MUTED, wraplength=400, justify="left")
        self.missing_tags_lbl.pack(anchor="w")

        # Suggested actions
        self.actions_lbl = ctk.CTkLabel(self.res_card, text="Suggested Action Steps:", font=get_font(12, "bold"), text_color=TEXT_MAIN)
        self.actions_lbl.pack(anchor="w", pady=(15, 2))

        self.actions_box = ctk.CTkScrollableFrame(self.res_card, fg_color="#0f172a", height=100, border_color=PANEL_BORDER, border_width=1)
        self.actions_box.pack(fill="both", expand=True, pady=(0, 15))

    def on_refresh(self):
        # Refresh left side section scores
        resume_data = self.controller.resume_manager.current_data
        ats_result = self.controller.ats_analyzer.calculate_ats_score(resume_data)
        details = ats_result["details"]

        for key, val_label in self.score_labels.items():
            if key in details:
                val_label.configure(text=str(details[key]))

    def run_job_matching(self):
        jd_text = self.jd_input.get("1.0", "end").strip()
        if not jd_text:
            messagebox.showwarning("Input Required", "Please paste a job description first.")
            return

        resume_data = self.controller.resume_manager.current_data
        match_res = self.controller.ats_analyzer.analyze_job_match(resume_data, jd_text)

        # 1. Update Match %
        pct = match_res["match_percentage"]
        self.match_val.configure(text=f"{pct}%")
        
        # Color matching score
        if pct >= 75:
            self.match_val.configure(text_color=COLOR_SUCCESS)
        elif pct >= 50:
            self.match_val.configure(text_color=COLOR_WARNING)
        else:
            self.match_val.configure(text_color="#f43f5e")

        # 2. Update Missing Keywords
        missing = match_res["missing_keywords"]
        if not missing:
            self.missing_tags_lbl.configure(text="None! You have matched all detected key technologies.", text_color=COLOR_SUCCESS)
        else:
            self.missing_tags_lbl.configure(text=", ".join(missing), text_color=COLOR_WARNING)

        # 3. Clear and update action steps
        for widget in self.actions_box.winfo_children():
            widget.destroy()

        suggestions = match_res["suggestions"]
        for s in suggestions:
            item = ctk.CTkFrame(self.actions_box, fg_color="transparent")
            item.pack(fill="x", pady=4, padx=5)
            
            bullet = ctk.CTkLabel(item, text="•", font=get_font(16, "bold"), text_color=ACCENT_COLOR)
            bullet.pack(side="left", padx=(0, 5), anchor="n")
            
            lbl = ctk.CTkLabel(item, text=s, font=get_font(12), text_color=TEXT_MUTED, justify="left", wraplength=350)
            lbl.pack(side="left", fill="x", expand=True, anchor="w")
