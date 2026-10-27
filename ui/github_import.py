import customtkinter as ctk
from tkinter import messagebox
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, COLOR_SUCCESS, get_font, create_section_header

class GitHubImportPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Scrollable panel
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # Header
        header = create_section_header(self.scroll_frame, "GitHub Resume Integration")
        header.pack(fill="x", padx=10, pady=(0, 15))

        # Input card
        self.input_card = ctk.CTkFrame(self.scroll_frame, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.input_card.pack(fill="x", padx=10, pady=5)

        lbl = ctk.CTkLabel(self.input_card, text="Import Projects from GitHub", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=15, pady=(15, 5))

        desc = ctk.CTkLabel(
            self.input_card, 
            text="Enter a GitHub username to load repositories. Select projects to import and the AI will auto-write professional descriptions for your resume.",
            font=get_font(11),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        desc.pack(anchor="w", padx=15, pady=(0, 15))

        # Horizontal input fields
        in_row = ctk.CTkFrame(self.input_card, fg_color="transparent")
        in_row.pack(fill="x", padx=15, pady=(0, 15))

        self.username_entry = ctk.CTkEntry(
            in_row, 
            placeholder_text="e.g. torvalds", 
            font=get_font(12),
            fg_color="#0f172a",
            border_color=PANEL_BORDER,
            width=250,
            height=32
        )
        self.username_entry.pack(side="left", padx=(0, 10))

        fetch_btn = ctk.CTkButton(
            in_row,
            text="Fetch Repositories",
            font=get_font(12, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            height=32,
            command=self.fetch_github_repos
        )
        fetch_btn.pack(side="left")

        # Repos scroll box
        self.repos_card = ctk.CTkFrame(self.scroll_frame, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.repos_card.pack(fill="both", expand=True, padx=10, pady=15)

        self.repos_title = ctk.CTkLabel(self.repos_card, text="Available Repositories", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        self.repos_title.pack(anchor="w", padx=15, pady=15)

        self.repos_list_frame = ctk.CTkScrollableFrame(self.repos_card, fg_color="#0f172a", height=220)
        self.repos_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.placeholder_lbl = ctk.CTkLabel(self.repos_list_frame, text="No username loaded yet.", font=get_font(12, "italic"), text_color=TEXT_MUTED)
        self.placeholder_lbl.pack(pady=40)

        # Import button at bottom
        self.import_btn = ctk.CTkButton(
            self.repos_card,
            text="🚀 Import Selected to Projects Section",
            font=get_font(13, "bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            height=36,
            command=self.import_selected_repos
        )
        self.import_btn.pack(anchor="w", padx=15, pady=15)
        self.import_btn.configure(state="disabled")

        # Loaded list references
        self.repo_checkboxes = []
        self.fetched_repos_data = []

    def fetch_github_repos(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Username Required", "Please enter a GitHub username.")
            return

        # Clear active checklists
        self.placeholder_lbl.destroy()
        for w in self.repos_list_frame.winfo_children():
            w.destroy()
            
        load_lbl = ctk.CTkLabel(self.repos_list_frame, text="Fetching from GitHub API... please wait...", font=get_font(12, "italic"), text_color=ACCENT_COLOR)
        load_lbl.pack(pady=40)
        self.update()

        try:
            repos = self.controller.github_client.fetch_user_repos(username)
            load_lbl.destroy()
            
            if not repos:
                self.placeholder_lbl = ctk.CTkLabel(self.repos_list_frame, text="This user has no original public repositories.", font=get_font(12, "italic"), text_color=TEXT_MUTED)
                self.placeholder_lbl.pack(pady=40)
                self.import_btn.configure(state="disabled")
                return

            self.fetched_repos_data = repos
            self.repo_checkboxes.clear()

            # Render checkbox rows
            for idx, r in enumerate(repos):
                row = ctk.CTkFrame(self.repos_list_frame, fg_color="transparent")
                row.pack(fill="x", pady=6, padx=5)

                var = ctk.BooleanVar(value=False)
                chk = ctk.CTkCheckBox(
                    row, 
                    text="", 
                    variable=var, 
                    fg_color=ACCENT_COLOR, 
                    hover_color=ACCENT_HOVER,
                    width=24
                )
                chk.pack(side="left", padx=(5, 10))
                self.repo_checkboxes.append((var, r))

                # Text detail panel
                det = ctk.CTkFrame(row, fg_color="transparent")
                det.pack(side="left", fill="x", expand=True)

                title_row = ctk.CTkFrame(det, fg_color="transparent")
                title_row.pack(fill="x")
                
                title_lbl = ctk.CTkLabel(title_row, text=r["name"], font=get_font(13, "bold"), text_color=TEXT_MAIN)
                title_lbl.pack(side="left")

                lang_star = f" | ⭐️ {r['stars']} | {r['language']}"
                meta_lbl = ctk.CTkLabel(title_row, text=lang_star, font=get_font(11, "semibold"), text_color=TEXT_MUTED)
                meta_lbl.pack(side="left", padx=5)

                desc_lbl = ctk.CTkLabel(det, text=r["description"], font=get_font(11), text_color=TEXT_MUTED, justify="left", wraplength=480)
                desc_lbl.pack(anchor="w", pady=2)

            self.import_btn.configure(state="normal")
            
        except Exception as e:
            load_lbl.destroy()
            self.import_btn.configure(state="disabled")
            err_lbl = ctk.CTkLabel(self.repos_list_frame, text=f"Failed to fetch repositories: {e}", font=get_font(12), text_color="#ef4444")
            err_lbl.pack(pady=40)

    def import_selected_repos(self):
        selected_repos = [repo for var, repo in self.repo_checkboxes if var.get()]
        
        if not selected_repos:
            messagebox.showwarning("Selection Required", "Please select at least one repository to import.")
            return

        # Show overlay or modal loading indicator
        loading = ctk.CTkLabel(self.repos_list_frame, text="Generating bullet point descriptions using AI... please wait...", font=get_font(12, "bold"), text_color=ACCENT_COLOR)
        loading.pack(pady=10)
        self.update()

        imported_count = 0
        active_resume = self.controller.resume_manager.current_data
        
        # Add imported projects key if missing
        if "projects" not in active_resume:
            active_resume["projects"] = []

        for repo in selected_repos:
            # Build AI description
            prompt = (
                f"Generate a professional, resume-ready project description (exactly 2 bullet points) for a project "
                f"named '{repo['name']}' built in '{repo['language']}'. "
                f"Project description from GitHub: '{repo['description']}'.\n"
                f"Make the bullets action-oriented, professional, and focus on coding accomplishments. "
                f"Output ONLY the bullet points separated by newlines, starting with '-'."
            )
            system_prompt = "You are a senior tech resume developer writer."
            
            try:
                ai_bullets_text = self.controller.ai_service.run_prompt(prompt, system_prompt)
                bullets = [b.strip().lstrip("- *").strip() for b in ai_bullets_text.split("\n") if b.strip()]
            except Exception:
                # Mock fallback if everything fails
                bullets = [
                    f"Designed and deployed the '{repo['name']}' repository using {repo['language']}, structuring modules for clean reuse.",
                    "Configured development dependencies and optimized system files to enable automated pipeline testing."
                ]

            # Format to Project structure
            project_entry = {
                "name": repo["name"],
                "date": repo["updated_at"],
                "technologies": repo["language"],
                "link": repo["url"],
                "bullets": bullets
            }

            active_resume["projects"].append(project_entry)
            imported_count += 1

        loading.destroy()
        
        # Save modifications
        self.controller.resume_manager.save_current_resume(active_resume)
        
        messagebox.showinfo("Success", f"Successfully imported {imported_count} projects!\nThey have been added to your Resume Editor Projects tab.")
        
        # Uncheck all
        for var, _ in self.repo_checkboxes:
            var.set(False)
            
        # Switch to Editor Projects
        self.controller.show_frame("Resume Editor")
        editor_frame = self.controller.frames.get("Resume Editor")
        if editor_frame:
            # Select projects tab programmatically
            editor_frame.tabview.set("Projects")
            editor_frame.on_refresh()

    def on_refresh(self):
        pass
