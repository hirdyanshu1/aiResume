import os
import customtkinter as ctk
import webbrowser
from tkinter import filedialog, messagebox
from ui.styles import PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, COLOR_SUCCESS, get_font, create_section_header

class PortfolioGenPanel(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # Header
        header = create_section_header(self.scroll_frame, "Portfolio Website Generator")
        header.pack(fill="x", padx=10, pady=(0, 15))

        # Main panel card
        self.card = ctk.CTkFrame(self.scroll_frame, fg_color=PANEL_BG, border_color=PANEL_BORDER, border_width=1, corner_radius=8)
        self.card.pack(fill="both", expand=True, padx=10, pady=5)

        lbl = ctk.CTkLabel(self.card, text="One-Click Portfolio Website Builder", font=get_font(14, "bold"), text_color=TEXT_MAIN)
        lbl.pack(anchor="w", padx=20, pady=(20, 5))

        desc = ctk.CTkLabel(
            self.card,
            text="Transform your resume data into a completely self-contained, responsive, and stunning portfolio website. "
                 "The generated site is written in clean, modern HTML5 and CSS3, ready to host for free on GitHub Pages, Netlify, or Vercel.",
            font=get_font(12),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        desc.pack(anchor="w", padx=20, pady=(0, 20))

        # Features list
        feat_card = ctk.CTkFrame(self.card, fg_color="#0f172a", border_color=PANEL_BORDER, border_width=1, corner_radius=6)
        feat_card.pack(fill="x", padx=20, pady=(0, 20))
        
        features_html = (
            "✨ Core Website Features Included:\n"
            "• Modern dark mode / light mode toggle (saves user preferences in local storage).\n"
            "• Clean, interactive timeline detailing your Work Experience history.\n"
            "• Sleek project cards grid showcasing GitHub links and technologies used.\n"
            "• Fully responsive grid layouts adjusting cleanly to mobile, tablets, and desktops.\n"
            "• Modern typography and smooth animations (hover expansions, scroll effects)."
        )
        feat_lbl = ctk.CTkLabel(feat_card, text=features_html, font=get_font(12), text_color=TEXT_MUTED, justify="left", wraplength=550)
        feat_lbl.pack(padx=15, pady=15)

        # Destination input row
        dest_lbl = ctk.CTkLabel(self.card, text="Target Output Folder:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        dest_lbl.pack(anchor="w", padx=20, pady=(10, 5))

        dest_row = ctk.CTkFrame(self.card, fg_color="transparent")
        dest_row.pack(fill="x", padx=20, pady=(0, 20))

        self.path_entry = ctk.CTkEntry(
            dest_row,
            placeholder_text="Select folder to save portfolio website files...",
            font=get_font(12),
            fg_color="#0f172a",
            border_color=PANEL_BORDER,
            height=32
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Set default path to workspace/portfolio_site
        default_path = os.path.join(self.controller.workspace_dir, "portfolio_site")
        self.path_entry.insert(0, default_path)

        browse_btn = ctk.CTkButton(
            dest_row,
            text="Browse...",
            font=get_font(12, "bold"),
            width=90,
            height=32,
            fg_color=PANEL_BORDER,
            hover_color=ACCENT_COLOR,
            command=self.browse_output_folder
        )
        browse_btn.pack(side="right")

        # Generate Button
        self.gen_btn = ctk.CTkButton(
            self.card,
            text="🚀 Generate Portfolio Website",
            font=get_font(13, "bold"),
            height=42,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.build_portfolio_website
        )
        self.gen_btn.pack(anchor="w", padx=20, pady=(0, 20))

        # Output Success Card (Hidden initially)
        self.success_card = ctk.CTkFrame(self.card, fg_color="transparent")
        # will pack programmatically

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Portfolio Destination Directory")
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, os.path.abspath(folder))

    def build_portfolio_website(self):
        output_dir = self.path_entry.get().strip()
        if not output_dir:
            messagebox.showwarning("Directory Required", "Please specify a destination folder first.")
            return

        # Fetch active resume data
        resume_data = self.controller.resume_manager.current_data

        try:
            index_path = self.controller.portfolio_builder.generate_portfolio_site(resume_data, output_dir)
            
            # Show success card elements
            for w in self.success_card.winfo_children():
                w.destroy()
                
            self.success_card.pack(fill="x", padx=20, pady=(0, 20))
            
            # Success text
            s_lbl = ctk.CTkLabel(
                self.success_card,
                text=f"🎉 Portfolio generated successfully!\nAll files (index.html, styles.css) saved to:\n{output_dir}",
                font=get_font(12, "bold"),
                text_color=COLOR_SUCCESS,
                justify="left",
                wraplength=550
            )
            s_lbl.pack(anchor="w", pady=(0, 10))

            # Buttons row
            btn_row = ctk.CTkFrame(self.success_card, fg_color="transparent")
            btn_row.pack(fill="x")

            view_site_btn = ctk.CTkButton(
                btn_row,
                text="👁️ Open Site in Browser",
                font=get_font(12, "bold"),
                width=160,
                fg_color=COLOR_SUCCESS,
                hover_color="#059669",
                command=lambda p=index_path: webbrowser.open(f"file:///{p.replace(os.sep, '/')}")
            )
            view_site_btn.pack(side="left", padx=(0, 10))

            open_folder_btn = ctk.CTkButton(
                btn_row,
                text="📁 Open Portfolio Folder",
                font=get_font(12, "bold"),
                width=160,
                fg_color=PANEL_BORDER,
                hover_color=ACCENT_COLOR,
                command=lambda d=output_dir: os.startfile(d) if hasattr(os, "startfile") else messagebox.showinfo("Folder Info", f"Folder is located at: {d}")
            )
            open_folder_btn.pack(side="left")

            messagebox.showinfo("Success", "Portfolio Website generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate portfolio: {e}")

    def on_refresh(self):
        pass
