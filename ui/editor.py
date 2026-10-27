import os
import customtkinter as ctk
import webbrowser
from tkinter import messagebox
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, get_font, create_section_header

class EditorPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Title Header
        header = create_section_header(self, "Resume Editor")
        header.pack(fill="x", padx=10, pady=(0, 10))

        # Create Tabview for different resume sections
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color=PANEL_BG, 
            segmented_button_selected_color=ACCENT_COLOR,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_hover_color=PANEL_BORDER,
            text_color=TEXT_MAIN
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Tabs
        self.tabview.add("Personal")
        self.tabview.add("Summary")
        self.tabview.add("Experience")
        self.tabview.add("Projects")
        self.tabview.add("Education")
        self.tabview.add("Skills")
        self.tabview.add("Templates & Export")

        # Initialize sub-structures for dynamic sections
        self.exp_fields = []
        self.proj_fields = []
        self.edu_fields = []

        # Setup Tab contents
        self.setup_personal_tab()
        self.setup_summary_tab()
        self.setup_experience_tab()
        self.setup_projects_tab()
        self.setup_education_tab()
        self.setup_skills_tab()
        self.setup_templates_tab()

        # Load initial active data
        self.load_active_data()

    def setup_personal_tab(self):
        tab = self.tabview.tab("Personal")
        
        # Scrollable container for entries
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        fields = [
            ("name", "Full Name:"),
            ("title", "Professional Title:"),
            ("email", "Email Address:"),
            ("phone", "Phone Number:"),
            ("location", "Location (City, State):"),
            ("website", "Portfolio / Website Link:"),
            ("github", "GitHub Profile URL:"),
            ("linkedin", "LinkedIn Profile URL:")
        ]

        self.personal_entries = {}
        for key, label_text in fields:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=6)
            
            lbl = ctk.CTkLabel(row, text=label_text, font=get_font(13, "bold"), text_color=TEXT_MAIN, width=150, anchor="w")
            lbl.pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(row, font=get_font(12), fg_color="#0f172a", border_color=PANEL_BORDER, height=32)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            
            self.personal_entries[key] = entry

    def setup_summary_tab(self):
        tab = self.tabview.tab("Summary")
        
        lbl = ctk.CTkLabel(tab, text="Professional Summary", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=10, pady=10)
        
        desc = ctk.CTkLabel(tab, text="Write a brief (3-5 sentences) summary focusing on your key achievements, skills, and career objectives.", font=get_font(11), text_color=TEXT_MUTED)
        desc.pack(anchor="w", padx=10, pady=(0, 10))

        self.summary_text = ctk.CTkTextbox(tab, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1)
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_experience_tab(self):
        tab = self.tabview.tab("Experience")
        
        # Add button at the top
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        lbl = ctk.CTkLabel(btn_frame, text="Work History", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="+ Add Experience",
            font=get_font(12, "bold"),
            width=120,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.add_experience_row
        )
        add_btn.pack(side="right", padx=5)

        # Scrollable container for experience cards
        self.exp_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.exp_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def add_experience_row(self, data=None):
        card = ctk.CTkFrame(self.exp_scroll, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        card.pack(fill="x", pady=10, padx=5)

        # Header of card (Row 0)
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=5)
        
        card_lbl = ctk.CTkLabel(hdr, text=f"Work Entry #{len(self.exp_fields)+1}", font=get_font(12, "bold"), text_color=TEXT_MUTED)
        card_lbl.pack(side="left")

        rem_btn = ctk.CTkButton(
            hdr,
            text="Remove",
            font=get_font(11, "bold"),
            width=60,
            height=22,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.remove_experience_row(card)
        )
        rem_btn.pack(side="right")

        # Grid form fields (Row 1)
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        # Company & Role
        company_entry = ctk.CTkEntry(form, placeholder_text="Company Name", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        company_entry.grid(row=0, column=0, padx=2, pady=4, sticky="ew")
        
        role_entry = ctk.CTkEntry(form, placeholder_text="Role / Job Title", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        role_entry.grid(row=0, column=1, padx=2, pady=4, sticky="ew")

        # Location & Dates
        loc_entry = ctk.CTkEntry(form, placeholder_text="Location (e.g. San Francisco, CA)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        loc_entry.grid(row=1, column=0, padx=2, pady=4, sticky="ew")

        dates_frame = ctk.CTkFrame(form, fg_color="transparent")
        dates_frame.grid(row=1, column=1, padx=2, pady=4, sticky="ew")
        dates_frame.grid_columnconfigure(0, weight=1)
        dates_frame.grid_columnconfigure(1, weight=1)

        start_entry = ctk.CTkEntry(dates_frame, placeholder_text="Start Date (e.g. Jun 2024)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        start_entry.grid(row=0, column=0, padx=2, sticky="ew")

        end_entry = ctk.CTkEntry(dates_frame, placeholder_text="End Date (e.g. Present)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        end_entry.grid(row=0, column=1, padx=2, sticky="ew")

        # Bullets Textbox (Row 2)
        bullets_label = ctk.CTkLabel(card, text="Job Description / Achievements (one bullet point per line):", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        bullets_label.pack(anchor="w", padx=10, pady=(5, 2))

        bullets_box = ctk.CTkTextbox(card, height=80, font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1)
        bullets_box.pack(fill="x", padx=10, pady=(0, 10))

        # Store in dict references
        row_refs = {
            "card": card,
            "company": company_entry,
            "role": role_entry,
            "location": loc_entry,
            "start": start_entry,
            "end": end_entry,
            "bullets": bullets_box
        }

        # Populate if editing existing
        if data:
            company_entry.insert(0, data.get("company", ""))
            role_entry.insert(0, data.get("role", ""))
            loc_entry.insert(0, data.get("location", ""))
            start_entry.insert(0, data.get("start_date", ""))
            end_entry.insert(0, data.get("end_date", ""))
            
            bullets_text = "\n".join(data.get("bullets", []))
            bullets_box.insert("1.0", bullets_text)

        self.exp_fields.append(row_refs)

    def remove_experience_row(self, card_widget):
        card_widget.destroy()
        # Filter out from fields list
        self.exp_fields = [ref for ref in self.exp_fields if ref["card"] != card_widget]

    def setup_projects_tab(self):
        tab = self.tabview.tab("Projects")
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        lbl = ctk.CTkLabel(btn_frame, text="Personal Projects", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="+ Add Project",
            font=get_font(12, "bold"),
            width=120,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.add_project_row
        )
        add_btn.pack(side="right", padx=5)

        self.proj_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.proj_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def add_project_row(self, data=None):
        card = ctk.CTkFrame(self.proj_scroll, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        card.pack(fill="x", pady=10, padx=5)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=5)
        
        card_lbl = ctk.CTkLabel(hdr, text=f"Project #{len(self.proj_fields)+1}", font=get_font(12, "bold"), text_color=TEXT_MUTED)
        card_lbl.pack(side="left")

        rem_btn = ctk.CTkButton(
            hdr,
            text="Remove",
            font=get_font(11, "bold"),
            width=60,
            height=22,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.remove_project_row(card)
        )
        rem_btn.pack(side="right")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        name_entry = ctk.CTkEntry(form, placeholder_text="Project Name", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        name_entry.grid(row=0, column=0, padx=2, pady=4, sticky="ew")

        date_entry = ctk.CTkEntry(form, placeholder_text="Completion Date (e.g. Oct 2024)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        date_entry.grid(row=0, column=1, padx=2, pady=4, sticky="ew")

        tech_entry = ctk.CTkEntry(form, placeholder_text="Technologies Used (e.g. Python, React, PostgreSQL)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        tech_entry.grid(row=1, column=0, padx=2, pady=4, sticky="ew")

        link_entry = ctk.CTkEntry(form, placeholder_text="Project URL / GitHub Link", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        link_entry.grid(row=1, column=1, padx=2, pady=4, sticky="ew")

        bullets_label = ctk.CTkLabel(card, text="Project Description / Bullet Points (one per line):", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        bullets_label.pack(anchor="w", padx=10, pady=(5, 2))

        bullets_box = ctk.CTkTextbox(card, height=80, font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1)
        bullets_box.pack(fill="x", padx=10, pady=(0, 10))

        row_refs = {
            "card": card,
            "name": name_entry,
            "date": date_entry,
            "tech": tech_entry,
            "link": link_entry,
            "bullets": bullets_box
        }

        if data:
            name_entry.insert(0, data.get("name", ""))
            date_entry.insert(0, data.get("date", ""))
            tech_entry.insert(0, data.get("technologies", ""))
            link_entry.insert(0, data.get("link", ""))
            bullets_text = "\n".join(data.get("bullets", []))
            bullets_box.insert("1.0", bullets_text)

        self.proj_fields.append(row_refs)

    def remove_project_row(self, card_widget):
        card_widget.destroy()
        self.proj_fields = [ref for ref in self.proj_fields if ref["card"] != card_widget]

    def setup_education_tab(self):
        tab = self.tabview.tab("Education")
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        lbl = ctk.CTkLabel(btn_frame, text="Academic History", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="+ Add Education",
            font=get_font(12, "bold"),
            width=120,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.add_education_row
        )
        add_btn.pack(side="right", padx=5)

        self.edu_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.edu_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def add_education_row(self, data=None):
        card = ctk.CTkFrame(self.edu_scroll, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        card.pack(fill="x", pady=10, padx=5)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=5)
        
        card_lbl = ctk.CTkLabel(hdr, text=f"Education #{len(self.edu_fields)+1}", font=get_font(12, "bold"), text_color=TEXT_MUTED)
        card_lbl.pack(side="left")

        rem_btn = ctk.CTkButton(
            hdr,
            text="Remove",
            font=get_font(11, "bold"),
            width=60,
            height=22,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.remove_education_row(card)
        )
        rem_btn.pack(side="right")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=10, pady=5)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        institution_entry = ctk.CTkEntry(form, placeholder_text="School / Institution Name", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        institution_entry.grid(row=0, column=0, padx=2, pady=4, sticky="ew")

        degree_entry = ctk.CTkEntry(form, placeholder_text="Degree (e.g. B.S. in Computer Science)", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        degree_entry.grid(row=0, column=1, padx=2, pady=4, sticky="ew")

        dates_frame = ctk.CTkFrame(form, fg_color="transparent")
        dates_frame.grid(row=1, column=0, padx=2, pady=4, sticky="ew")
        dates_frame.grid_columnconfigure(0, weight=1)
        dates_frame.grid_columnconfigure(1, weight=1)

        start_entry = ctk.CTkEntry(dates_frame, placeholder_text="Start Date", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        start_entry.grid(row=0, column=0, padx=2, sticky="ew")

        end_entry = ctk.CTkEntry(dates_frame, placeholder_text="End Date / Grad Date", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        end_entry.grid(row=0, column=1, padx=2, sticky="ew")

        gpa_entry = ctk.CTkEntry(form, placeholder_text="GPA or Grade (e.g. 3.8/4.0) [Optional]", font=get_font(12), fg_color=PANEL_BG, border_color=PANEL_BORDER, height=28)
        gpa_entry.grid(row=1, column=1, padx=2, pady=4, sticky="ew")

        row_refs = {
            "card": card,
            "institution": institution_entry,
            "degree": degree_entry,
            "start": start_entry,
            "end": end_entry,
            "gpa": gpa_entry
        }

        if data:
            institution_entry.insert(0, data.get("institution", ""))
            degree_entry.insert(0, data.get("degree", ""))
            start_entry.insert(0, data.get("start_date", ""))
            end_entry.insert(0, data.get("end_date", ""))
            gpa_entry.insert(0, data.get("gpa", ""))

        self.edu_fields.append(row_refs)

    def remove_education_row(self, card_widget):
        card_widget.destroy()
        self.edu_fields = [ref for ref in self.edu_fields if ref["card"] != card_widget]

    def setup_skills_tab(self):
        tab = self.tabview.tab("Skills")
        
        lbl = ctk.CTkLabel(tab, text="Technical Skills", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=10, pady=10)
        
        desc = ctk.CTkLabel(tab, text="Enter your technical, soft, or domain skills separated by commas (e.g., Python, FastAPI, SQL, Project Management).", font=get_font(11), text_color=TEXT_MUTED)
        desc.pack(anchor="w", padx=10, pady=(0, 10))

        self.skills_text = ctk.CTkTextbox(tab, font=get_font(13), fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, height=180)
        self.skills_text.pack(fill="x", padx=10, pady=10)

    def setup_templates_tab(self):
        tab = self.tabview.tab("Templates & Export")
        
        lbl = ctk.CTkLabel(tab, text="Compile and Export Resume", font=get_font(16, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=20, pady=15)

        # Template Picker
        picker_frame = ctk.CTkFrame(tab, fg_color="transparent")
        picker_frame.pack(fill="x", padx=20, pady=10)

        t_lbl = ctk.CTkLabel(picker_frame, text="Select Styling Template:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        t_lbl.pack(side="left", padx=5)

        self.template_menu = ctk.CTkOptionMenu(
            picker_frame,
            values=["Modern Minimalist (modern)", "Traditional Executive (traditional)", "Creative Accent (creative)"],
            font=get_font(12),
            fg_color=PANEL_BORDER,
            button_color=PANEL_BORDER,
            button_hover_color=ACCENT_COLOR
        )
        self.template_menu.pack(side="left", padx=15)
        self.template_menu.set("Modern Minimalist (modern)")

        # Export Buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        preview_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Live Preview in Browser",
            font=get_font(13, "bold"),
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.preview_resume_browser
        )
        preview_btn.pack(side="left", padx=5)

        export_html_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Export HTML File",
            font=get_font(13, "bold"),
            height=40,
            fg_color=PANEL_BORDER,
            hover_color=ACCENT_COLOR,
            command=self.export_html_only
        )
        export_html_btn.pack(side="left", padx=5)

        # PDF instructions alert
        info_card = ctk.CTkFrame(tab, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        info_card.pack(fill="x", padx=20, pady=15)

        info_lbl = ctk.CTkLabel(
            info_card,
            text="💡 How to Save as PDF:\n"
                 "1. Click 'Live Preview in Browser' to render and load the resume in your default browser.\n"
                 "2. In your browser, press Ctrl + P (or Cmd + P on macOS) to open the print dialog.\n"
                 "3. Change the Print Destination to 'Save as PDF'.\n"
                 "4. Turn on 'Background Graphics' and turn off 'Headers and Footers' for a pixel-perfect, recruiter-ready copy!",
            font=get_font(12),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        info_lbl.pack(padx=15, pady=15)

    def load_active_data(self):
        data = self.controller.resume_manager.current_data

        # 1. Personal details
        for key, entry in self.personal_entries.items():
            entry.delete(0, "end")
            entry.insert(0, data["personal"].get(key, ""))

        # 2. Summary
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", data.get("summary", ""))

        # 3. Clear and reload dynamic sections
        for ref in self.exp_fields:
            ref["card"].destroy()
        self.exp_fields.clear()
        for exp in data.get("experiences", []):
            self.add_experience_row(exp)

        for ref in self.proj_fields:
            ref["card"].destroy()
        self.proj_fields.clear()
        for proj in data.get("projects", []):
            self.add_project_row(proj)

        for ref in self.edu_fields:
            ref["card"].destroy()
        self.edu_fields.clear()
        for edu in data.get("education", []):
            self.add_education_row(edu)

        # 4. Skills
        skills_text = ", ".join(data.get("skills", []))
        self.skills_text.delete("1.0", "end")
        self.skills_text.insert("1.0", skills_text)

    def get_edited_data(self):
        # Package UI inputs into JSON format
        personal = {}
        for key, entry in self.personal_entries.items():
            personal[key] = entry.get().strip()

        summary = self.summary_text.get("1.0", "end").strip()

        experiences = []
        for ref in self.exp_fields:
            bullets_raw = ref["bullets"].get("1.0", "end").strip()
            bullets = [b.strip() for b in bullets_raw.split("\n") if b.strip()]
            experiences.append({
                "company": ref["company"].get().strip(),
                "role": ref["role"].get().strip(),
                "location": ref["location"].get().strip(),
                "start_date": ref["start"].get().strip(),
                "end_date": ref["end"].get().strip(),
                "bullets": bullets
            })

        projects = []
        for ref in self.proj_fields:
            bullets_raw = ref["bullets"].get("1.0", "end").strip()
            bullets = [b.strip() for b in bullets_raw.split("\n") if b.strip()]
            projects.append({
                "name": ref["name"].get().strip(),
                "date": ref["date"].get().strip(),
                "technologies": ref["tech"].get().strip(),
                "link": ref["link"].get().strip(),
                "bullets": bullets
            })

        education = []
        for ref in self.edu_fields:
            education.append({
                "institution": ref["institution"].get().strip(),
                "degree": ref["degree"].get().strip(),
                "start_date": ref["start"].get().strip(),
                "end_date": ref["end"].get().strip(),
                "gpa": ref["gpa"].get().strip()
            })

        skills_raw = self.skills_text.get("1.0", "end").strip()
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

        return {
            "personal": personal,
            "summary": summary,
            "experiences": experiences,
            "projects": projects,
            "education": education,
            "skills": skills
        }

    def on_refresh(self):
        self.load_active_data()

    def get_template_filename_choice(self):
        choice = self.template_menu.get()
        if "modern" in choice:
            return "modern"
        elif "traditional" in choice:
            return "traditional"
        else:
            return "creative"

    def preview_resume_browser(self):
        # 1. Sync data
        data = self.get_edited_data()
        self.controller.resume_manager.current_data = data
        self.controller.resume_manager.save_current_resume()

        # 2. Compile HTML
        template_name = self.get_template_filename_choice()
        try:
            html_content = self.controller.portfolio_builder.compile_resume(data, template_name)
            
            # Save to temporary preview.html file
            preview_path = os.path.join(self.controller.workspace_dir, "resume_preview.html")
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            # Open browser
            webbrowser.open(f"file:///{preview_path.replace(os.sep, '/')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {e}")

    def export_html_only(self):
        # 1. Sync data
        data = self.get_edited_data()
        self.controller.resume_manager.current_data = data
        self.controller.resume_manager.save_current_resume()

        # 2. Get save location
        template_name = self.get_template_filename_choice()
        default_name = f"{data['personal'].get('name', 'resume').replace(' ', '_').lower()}_resume.html"
        
        # Save file picker dialog
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialfile=default_name,
            title="Export Resume HTML"
        )
        
        if file_path:
            try:
                html_content = self.controller.portfolio_builder.compile_resume(data, template_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo("Export Successful", f"Saved resume to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")
