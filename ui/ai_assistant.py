import customtkinter as ctk
from tkinter import messagebox
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, get_font, create_section_header

class AIAssistantPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Title Header
        header = create_section_header(self, "AI Career & Writing Assistant")
        header.pack(fill="x", padx=10, pady=(0, 10))

        # Main Tabview
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color=PANEL_BG, 
            segmented_button_selected_color=ACCENT_COLOR,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_hover_color=PANEL_BORDER,
            text_color=TEXT_MAIN
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Bullet Improver")
        self.tabview.add("Summary Rewriter")
        self.tabview.add("Interview Prep")
        self.tabview.add("Resume Chat")

        # Setup Sub-Tabs
        self.setup_bullet_tab()
        self.setup_summary_tab()
        self.setup_interview_tab()
        self.setup_chat_tab()

    # --- BULLET IMPROVER TAB ---
    def setup_bullet_tab(self):
        tab = self.tabview.tab("Bullet Improver")
        
        lbl = ctk.CTkLabel(tab, text="AI Bullet Point Improver", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=15, pady=(15, 5))
        
        desc = ctk.CTkLabel(
            tab, 
            text="Enter a simple description of something you did in a job. The AI will turn it into strong, action-oriented, and quantified statements.",
            font=get_font(11), 
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        desc.pack(anchor="w", padx=15, pady=(0, 15))

        # Input
        self.bullet_input = ctk.CTkEntry(
            tab, 
            placeholder_text="e.g., I worked on backend bugs and maintained the database...", 
            font=get_font(12),
            fg_color="#0f172a",
            border_color=PANEL_BORDER,
            height=36
        )
        self.bullet_input.pack(fill="x", padx=15, pady=5)

        # Optimize Button
        opt_btn = ctk.CTkButton(
            tab,
            text="✨ Optimize Bullet Point",
            font=get_font(12, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.improve_bullet_point
        )
        opt_btn.pack(anchor="w", padx=15, pady=10)

        # Output
        lbl_out = ctk.CTkLabel(tab, text="AI Suggestions:", font=get_font(12, "bold"), text_color=TEXT_MAIN)
        lbl_out.pack(anchor="w", padx=15, pady=(10, 2))

        self.bullet_output = ctk.CTkTextbox(tab, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1)
        self.bullet_output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def improve_bullet_point(self):
        input_txt = self.bullet_input.get().strip()
        if not input_txt:
            messagebox.showwarning("Input Required", "Please enter a bullet point description first.")
            return

        self.bullet_output.delete("1.0", "end")
        self.bullet_output.insert("1.0", "Thinking... please wait...\n")
        self.update()

        # Prompt AI
        prompt = (
            f"You are a professional resume writer. Rewrite the following resume bullet point description "
            f"to make it extremely high-impact. Use strong action verbs, focus on results, and add realistic quantified metrics:\n\n"
            f"'{input_txt}'\n\n"
            f"Provide exactly 3 distinct bullet point options formatted in markdown, starting with '-'. Make them sound professional."
        )
        system_prompt = "You are a professional executive resume writer and career coach."
        
        try:
            result = self.controller.ai_service.run_prompt(prompt, system_prompt)
            self.bullet_output.delete("1.0", "end")
            self.bullet_output.insert("1.0", result)
        except Exception as e:
            self.bullet_output.delete("1.0", "end")
            self.bullet_output.insert("1.0", f"Error connecting to AI: {e}")

    # --- SUMMARY REWRITER TAB ---
    def setup_summary_tab(self):
        tab = self.tabview.tab("Summary Rewriter")
        
        lbl = ctk.CTkLabel(tab, text="AI Summary Rewriter", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=15, pady=(15, 5))

        # Horizontal setting layout
        settings = ctk.CTkFrame(tab, fg_color="transparent")
        settings.pack(fill="x", padx=15, pady=5)
        
        t_lbl = ctk.CTkLabel(settings, text="Desired Tone:", font=get_font(12, "semibold"), text_color=TEXT_MAIN)
        t_lbl.pack(side="left", padx=(0, 10))

        self.tone_menu = ctk.CTkOptionMenu(
            settings,
            values=["Professional", "Confident & Energetic", "Creative & Innovative"],
            font=get_font(11),
            fg_color=PANEL_BORDER,
            button_color=PANEL_BORDER,
            button_hover_color=ACCENT_COLOR
        )
        self.tone_menu.pack(side="left")
        self.tone_menu.set("Professional")

        rewrite_btn = ctk.CTkButton(
            settings,
            text="✨ Rewrite Summary",
            font=get_font(12, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.rewrite_summary
        )
        rewrite_btn.pack(side="right")

        # Input summary field
        lbl_in = ctk.CTkLabel(tab, text="Your Current Summary (or draft ideas):", font=get_font(12, "bold"), text_color=TEXT_MAIN)
        lbl_in.pack(anchor="w", padx=15, pady=(10, 2))

        self.summary_input = ctk.CTkTextbox(tab, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, height=100)
        self.summary_input.pack(fill="x", padx=15, pady=(0, 10))

        # Output field
        lbl_out = ctk.CTkLabel(tab, text="AI Optimization Suggestions:", font=get_font(12, "bold"), text_color=TEXT_MAIN)
        lbl_out.pack(anchor="w", padx=15, pady=(10, 2))

        self.summary_output = ctk.CTkTextbox(tab, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1)
        self.summary_output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def rewrite_summary(self):
        curr_text = self.summary_input.get("1.0", "end").strip()
        if not curr_text:
            # Fall back to using the text in the active resume
            active_data = self.controller.resume_manager.current_data
            curr_text = active_data.get("summary", "")
            if curr_text:
                self.summary_input.delete("1.0", "end")
                self.summary_input.insert("1.0", curr_text)
                
        if not curr_text or len(curr_text) < 10:
            messagebox.showwarning("Input Required", "Please write a draft summary or import your current resume summary.")
            return

        self.summary_output.delete("1.0", "end")
        self.summary_output.insert("1.0", "Rewriting... please wait...\n")
        self.update()

        tone = self.tone_menu.get()
        prompt = (
            f"You are a master career consultant. Rewrite the following resume professional summary to make it highly polished "
            f"and tailored. The target tone is '{tone}'. Keep it concise (about 3-4 sentences, 60-80 words total):\n\n"
            f"'{curr_text}'\n\n"
            f"Write the output summary in a clear block of text."
        )
        system_prompt = "You are a senior hiring partner and executive writer."

        try:
            result = self.controller.ai_service.run_prompt(prompt, system_prompt)
            self.summary_output.delete("1.0", "end")
            self.summary_output.insert("1.0", result)
        except Exception as e:
            self.summary_output.delete("1.0", "end")
            self.summary_output.insert("1.0", f"Error connecting to AI: {e}")

    # --- INTERVIEW PREP TAB ---
    def setup_interview_tab(self):
        tab = self.tabview.tab("Interview Prep")
        
        # Grid Controls
        ctrls = ctk.CTkFrame(tab, fg_color="transparent")
        ctrls.pack(fill="x", padx=15, pady=(15, 10))
        
        diff_lbl = ctk.CTkLabel(ctrls, text="Interview Level:", font=get_font(12, "semibold"), text_color=TEXT_MAIN)
        diff_lbl.pack(side="left", padx=(0, 10))

        self.diff_menu = ctk.CTkOptionMenu(
            ctrls,
            values=["Junior (Entry-Level)", "Mid-Level Standard", "Senior / Lead Architect"],
            font=get_font(11),
            fg_color=PANEL_BORDER,
            button_color=PANEL_BORDER,
            button_hover_color=ACCENT_COLOR
        )
        self.diff_menu.pack(side="left")
        self.diff_menu.set("Mid-Level Standard")

        gen_btn = ctk.CTkButton(
            ctrls,
            text="🎯 Generate Questions from Resume",
            font=get_font(12, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.generate_interview_questions
        )
        gen_btn.pack(side="right")

        # Scrollable area showing interview questions
        self.q_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.q_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Placeholder
        self.placeholder_lbl = ctk.CTkLabel(
            self.q_scroll, 
            text="Your generated interview questions and guidelines will appear here. Click 'Generate Questions' to start.",
            font=get_font(12, "italic"),
            text_color=TEXT_MUTED
        )
        self.placeholder_lbl.pack(pady=40)

    def generate_interview_questions(self):
        # 1. Sync data
        resume_data = self.controller.resume_manager.current_data
        
        # Clear placeholder
        self.placeholder_lbl.destroy()
        
        for w in self.q_scroll.winfo_children():
            w.destroy()
            
        load_lbl = ctk.CTkLabel(self.q_scroll, text="Analyzing resume and generating interview questions... please wait...", font=get_font(12, "italic"), text_color=ACCENT_COLOR)
        load_lbl.pack(pady=40)
        self.update()

        difficulty = self.diff_menu.get()
        
        # Compile resume text representation
        summary = resume_data.get("summary", "")
        skills = ", ".join(resume_data.get("skills", []))
        exp_roles = ", ".join([e.get("role", "") for e in resume_data.get("experiences", [])])
        
        prompt = (
            f"Review the resume properties: Roles: {exp_roles}, Summary: {summary}, Skills: {skills}.\n"
            f"Generate 5 realistic and tailored interview questions (3 Technical, 2 HR/Behavioral) "
            f"assuming the candidate is interviewing for a '{difficulty}' level role.\n"
            f"Format the output strictly as a JSON list of objects containing fields: "
            f"'question' (the question text) and 'answer_guideline' (bullet points on how to structure a good answer, key terms to include).\n"
            f"Output ONLY the raw valid JSON list. Do not write any markdown code fences or headers."
        )
        
        system_prompt = "You are an expert interviewer and technical recruiter."

        try:
            result = self.controller.ai_service.run_prompt(prompt, system_prompt)
            load_lbl.destroy()
            
            # Parse JSON safely
            # Clean possible markdown wrap ```json
            cleaned_res = result.strip()
            if cleaned_res.startswith("```"):
                cleaned_res = cleaned_res.replace("```json", "").replace("```", "").strip()
                
            try:
                q_list = json_data = json_data = [] # fallback
                import json
                q_list = json.loads(cleaned_res)
            except Exception as e:
                # Fallback: display raw response if JSON parsing fails
                tb = ctk.CTkTextbox(self.q_scroll, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, height=300)
                tb.pack(fill="both", expand=True, padx=5, pady=5)
                tb.insert("1.0", result)
                return

            if not isinstance(q_list, list):
                q_list = []

            for idx, q_data in enumerate(q_list):
                q_text = q_data.get("question", "Question")
                a_guideline = q_data.get("answer_guideline", "Guidelines...")
                
                # Card frame
                q_card = ctk.CTkFrame(self.q_scroll, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=8)
                q_card.pack(fill="x", pady=8, padx=5)

                q_lbl = ctk.CTkLabel(
                    q_card,
                    text=f"Q{idx+1}: {q_text}",
                    font=get_font(13, "bold"),
                    text_color=TEXT_MAIN,
                    wraplength=600,
                    justify="left"
                )
                q_lbl.pack(anchor="w", padx=15, pady=(15, 10))

                # Hidden content box
                guide_box = ctk.CTkTextbox(q_card, height=100, font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1)
                guide_box.insert("1.0", f"How to Answer Guideline:\n{a_guideline}")
                guide_box.configure(state="disabled")
                
                # Expand button
                exp_btn = ctk.CTkButton(
                    q_card,
                    text="Show Suggested Answer Guideline",
                    font=get_font(11, "bold"),
                    fg_color=PANEL_BORDER,
                    hover_color=ACCENT_COLOR,
                    height=24,
                    command=lambda gb=guide_box, b=None: self.toggle_element(gb)
                )
                exp_btn.pack(anchor="w", padx=15, pady=(0, 15))
                
        except Exception as e:
            load_lbl.destroy()
            err_lbl = ctk.CTkLabel(self.q_scroll, text=f"Failed to generate questions: {e}", font=get_font(12), text_color="#ef4444")
            err_lbl.pack(pady=40)

    def toggle_element(self, widget):
        # Toggle packing
        if widget.winfo_ismapped():
            widget.pack_forget()
        else:
            # pack before the expand button
            widget.pack(fill="x", padx=15, pady=(0, 10))

    # --- RESUME CHAT TAB ---
    def setup_chat_tab(self):
        tab = self.tabview.tab("Resume Chat")
        
        # Grid layout for chat
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Main frame
        chat_frame = ctk.CTkFrame(tab, fg_color="transparent")
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        # Log Scrollable Frame
        self.chat_log = ctk.CTkScrollableFrame(chat_frame, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1)
        self.chat_log.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        # Welcome message
        self.add_chat_bubble("AI Assistant", "Hello! I am your AI Career Mentor. Ask me anything about your resume, such as:\n- 'How can I optimize my projects section?'\n- 'What skills should I add for an AI Engineer role?'\n- 'Rewrite my project descriptions.'")

        # Entry Box
        self.chat_entry = ctk.CTkEntry(
            chat_frame, 
            placeholder_text="Type a message to chat with your resume...", 
            font=get_font(12),
            fg_color=PANEL_BG,
            border_color=PANEL_BORDER,
            height=36
        )
        self.chat_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat_message())

        # Send Button
        send_btn = ctk.CTkButton(
            chat_frame,
            text="Send",
            font=get_font(12, "bold"),
            width=80,
            height=36,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.send_chat_message
        )
        send_btn.grid(row=1, column=1, sticky="e")

    def add_chat_bubble(self, sender, message):
        bubble_bg = PANEL_BG if sender == "AI Assistant" else PANEL_BORDER
        align = "w" if sender == "AI Assistant" else "e"
        padx_side = (10, 40) if sender == "AI Assistant" else (40, 10)
        text_color = ACCENT_COLOR if sender == "AI Assistant" else TEXT_MAIN

        bubble_card = ctk.CTkFrame(self.chat_log, fg_color=bubble_bg, corner_radius=10)
        bubble_card.pack(fill="x", pady=6, padx=padx_side)

        sender_lbl = ctk.CTkLabel(bubble_card, text=sender, font=get_font(10, "bold"), text_color=text_color)
        sender_lbl.pack(anchor="w", padx=12, pady=(8, 2))

        msg_lbl = ctk.CTkLabel(
            bubble_card, 
            text=message, 
            font=get_font(12), 
            text_color=TEXT_MAIN, 
            justify="left",
            wraplength=480
        )
        msg_lbl.pack(anchor="w", padx=12, pady=(0, 10))
        
        # Auto scroll to bottom
        self.chat_log._parent_canvas.yview_moveto(1.0)

    def send_chat_message(self):
        msg = self.chat_entry.get().strip()
        if not msg:
            return

        self.chat_entry.delete(0, "end")
        self.add_chat_bubble("You", msg)

        # Generate prompt using resume details
        resume_data = self.controller.resume_manager.current_data
        
        # Compile resume text representation
        summary = resume_data.get("summary", "")
        skills = ", ".join(resume_data.get("skills", []))
        exp_text = ""
        for exp in resume_data.get("experiences", []):
            exp_text += f"\n- {exp.get('role')} at {exp.get('company')} ({exp.get('start_date')} - {exp.get('end_date')}):\n  " + "\n  ".join(exp.get("bullets", []))
            
        proj_text = ""
        for proj in resume_data.get("projects", []):
            proj_text += f"\n- {proj.get('name')} ({proj.get('technologies')}):\n  " + "\n  ".join(proj.get("bullets", []))

        prompt = (
            f"CONTEXT:\n"
            f"Here is the candidate's current resume:\n"
            f"SUMMARY: {summary}\n"
            f"SKILLS: {skills}\n"
            f"EXPERIENCES: {exp_text}\n"
            f"PROJECTS: {proj_text}\n\n"
            f"USER QUESTION: {msg}\n\n"
            f"Please respond directly to the user question in a conversational tone. Focus on giving constructive, actionable advice based on the resume details provided."
        )
        
        system_prompt = "You are a helpful and experienced tech career counselor chatbot called AI Resume Assistant."

        # Show loading indicator in bubble
        self.add_chat_bubble("AI Assistant", "Thinking...")
        # Get reference to the last frame child so we can rewrite its label
        children = self.chat_log.winfo_children()
        last_card = children[-1]
        last_lbl = last_card.winfo_children()[1] # index 1 is msg_lbl
        
        self.update()

        try:
            result = self.controller.ai_service.run_prompt(prompt, system_prompt)
            last_lbl.configure(text=result)
        except Exception as e:
            last_lbl.configure(text=f"Failed to generate answer: {e}")
            
        self.chat_log._parent_canvas.yview_moveto(1.0)

    def on_refresh(self):
        pass
