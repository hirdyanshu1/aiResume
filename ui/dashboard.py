import customtkinter as ctk
import re
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, TEXT_MAIN, TEXT_MUTED, COLOR_SUCCESS, COLOR_WARNING, get_font, create_section_header

class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Scrollable container for dashboard contents
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # Header
        header = create_section_header(self.scroll_frame, "Resume Analytics Dashboard")
        header.pack(fill="x", padx=10, pady=(0, 20))

        # Main grid layout: 2 columns (Left: score widgets, Right: details/stats)
        self.grid_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=10)
        self.grid_container.grid_columnconfigure(0, weight=1)
        self.grid_container.grid_columnconfigure(1, weight=1)

        # LEFT COLUMN: ATS score indicator and Completion meter
        self.left_col = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.left_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        # ATS Score card
        self.ats_card = ctk.CTkFrame(self.left_col, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.ats_card.pack(fill="x", pady=(0, 15))

        self.ats_title = ctk.CTkLabel(self.ats_card, text="ATS Score", font=get_font(14, "bold"), text_color=TEXT_MUTED)
        self.ats_title.pack(pady=(15, 5))

        self.ats_val = ctk.CTkLabel(self.ats_card, text="0/100", font=get_font(42, "bold"), text_color=ACCENT_COLOR)
        self.ats_val.pack(pady=5)

        self.ats_progress = ctk.CTkProgressBar(self.ats_card, progress_color=ACCENT_COLOR)
        self.ats_progress.pack(fill="x", padx=30, pady=(5, 10))
        self.ats_progress.set(0)

        self.ats_rating = ctk.CTkLabel(self.ats_card, text="Needs Work", font=get_font(12, "bold"), text_color=TEXT_MUTED)
        self.ats_rating.pack(pady=(5, 15))

        # Completion meter card
        self.comp_card = ctk.CTkFrame(self.left_col, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.comp_card.pack(fill="x", pady=5)

        self.comp_title = ctk.CTkLabel(self.comp_card, text="Resume Completeness", font=get_font(14, "bold"), text_color=TEXT_MUTED)
        self.comp_title.pack(pady=(15, 5))

        self.comp_val = ctk.CTkLabel(self.comp_card, text="0%", font=get_font(28, "bold"), text_color=COLOR_SUCCESS)
        self.comp_val.pack(pady=5)

        self.comp_progress = ctk.CTkProgressBar(self.comp_card, progress_color=COLOR_SUCCESS)
        self.comp_progress.pack(fill="x", padx=30, pady=(5, 20))
        self.comp_progress.set(0)

        # RIGHT COLUMN: Stats & Quick info
        self.right_col = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.right_col.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        # Key stats grid
        self.stats_grid = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.stats_grid.pack(fill="x", pady=(0, 15))
        self.stats_grid.grid_columnconfigure(0, weight=1)
        self.stats_grid.grid_columnconfigure(1, weight=1)

        # Card 1: Experience Years
        self.exp_card = ctk.CTkFrame(self.stats_grid, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8, height=100)
        self.exp_card.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.exp_card.pack_propagate(False)
        self.exp_lbl = ctk.CTkLabel(self.exp_card, text="Work Entries", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        self.exp_lbl.pack(pady=(15, 2))
        self.exp_val = ctk.CTkLabel(self.exp_card, text="0", font=get_font(24, "bold"), text_color=TEXT_MAIN)
        self.exp_val.pack(pady=2)

        # Card 2: Projects Count
        self.proj_card = ctk.CTkFrame(self.stats_grid, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8, height=100)
        self.proj_card.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        self.proj_card.pack_propagate(False)
        self.proj_lbl = ctk.CTkLabel(self.proj_card, text="Projects Listed", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        self.proj_lbl.pack(pady=(15, 2))
        self.proj_val = ctk.CTkLabel(self.proj_card, text="0", font=get_font(24, "bold"), text_color=TEXT_MAIN)
        self.proj_val.pack(pady=2)

        # Card 3: Skills Count
        self.skills_card = ctk.CTkFrame(self.stats_grid, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8, height=100)
        self.skills_card.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.skills_card.pack_propagate(False)
        self.skills_lbl = ctk.CTkLabel(self.skills_card, text="Skills Count", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        self.skills_lbl.pack(pady=(15, 2))
        self.skills_val = ctk.CTkLabel(self.skills_card, text="0", font=get_font(24, "bold"), text_color=TEXT_MAIN)
        self.skills_val.pack(pady=2)

        # Card 4: Interview Readiness
        self.ready_card = ctk.CTkFrame(self.stats_grid, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8, height=100)
        self.ready_card.grid(row=1, column=1, padx=(5, 0), pady=5, sticky="ew")
        self.ready_card.pack_propagate(False)
        self.ready_lbl = ctk.CTkLabel(self.ready_card, text="Interview Readiness", font=get_font(11, "semibold"), text_color=TEXT_MUTED)
        self.ready_lbl.pack(pady=(15, 2))
        self.ready_val = ctk.CTkLabel(self.ready_card, text="Low", font=get_font(20, "bold"), text_color=COLOR_WARNING)
        self.ready_val.pack(pady=2)

        # Suggestions card
        self.sug_card = ctk.CTkFrame(self.right_col, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.sug_card.pack(fill="both", expand=True, pady=5)

        self.sug_title = ctk.CTkLabel(self.sug_card, text="ATS Recommendations", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        self.sug_title.pack(pady=(15, 10), padx=15, anchor="w")

        # Inner scroll frame for suggestions list
        self.sug_list_frame = ctk.CTkScrollableFrame(self.sug_card, fg_color="transparent", height=130)
        self.sug_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

    def on_refresh(self):
        # Fetch current resume data
        resume_data = self.controller.resume_manager.current_data

        # Calculate ATS score details
        ats_result = self.controller.ats_analyzer.calculate_ats_score(resume_data)
        score = ats_result["score"]
        details = ats_result["details"]
        suggestions = ats_result["suggestions"]

        # Update ATS Labels & progress
        self.ats_val.configure(text=f"{score}/100")
        self.ats_progress.set(score / 100.0)
        
        # Color based on score
        if score >= 80:
            score_color = COLOR_SUCCESS
            rating = "Excellent"
        elif score >= 50:
            score_color = COLOR_WARNING
            rating = "Good Progress"
        else:
            score_color = "#f43f5e" # red-500
            rating = "Needs Optimization"
            
        self.ats_val.configure(text_color=score_color)
        self.ats_progress.configure(progress_color=score_color)
        self.ats_rating.configure(text=rating, text_color=score_color)

        # Update Completion
        completion = details.get("completion", 0)
        self.comp_val.configure(text=f"{round(completion)}%")
        self.comp_progress.set(completion / 100.0)

        # Update quick stats
        experiences = resume_data.get("experiences", [])
        projects = resume_data.get("projects", [])
        skills = resume_data.get("skills", [])
        
        self.exp_val.configure(text=str(len(experiences)))
        self.proj_val.configure(text=str(len(projects)))
        self.skills_val.configure(text=str(len(skills)))

        # Estimate readiness: based on score & experience
        if score >= 75 and len(experiences) >= 2:
            self.ready_val.configure(text="High", text_color=COLOR_SUCCESS)
        elif score >= 50 and len(experiences) >= 1:
            self.ready_val.configure(text="Moderate", text_color=COLOR_WARNING)
        else:
            self.ready_val.configure(text="Low", text_color="#f43f5e")

        # Clear and update suggestions
        for widget in self.sug_list_frame.winfo_children():
            widget.destroy()

        if not suggestions:
            lbl = ctk.CTkLabel(
                self.sug_list_frame, 
                text="🎉 Fantastic job! No critical improvements needed. Your resume structure is highly optimized.",
                font=get_font(12),
                text_color=COLOR_SUCCESS,
                wraplength=450,
                justify="left"
            )
            lbl.pack(pady=10, padx=5, fill="x", anchor="w")
        else:
            for s in suggestions:
                item_frame = ctk.CTkFrame(self.sug_list_frame, fg_color="transparent")
                item_frame.pack(fill="x", pady=4, padx=2)
                
                bullet = ctk.CTkLabel(item_frame, text="⚡", font=get_font(12, "bold"), text_color=COLOR_WARNING)
                bullet.pack(side="left", padx=(0, 5), anchor="n")
                
                lbl = ctk.CTkLabel(
                    item_frame, 
                    text=s, 
                    font=get_font(12), 
                    text_color=TEXT_MUTED,
                    wraplength=420,
                    justify="left"
                )
                lbl.pack(side="left", fill="x", expand=True, anchor="w")
