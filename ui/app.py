import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

# Import style constants
from ui.styles import BG_DARK, PANEL_BG, PANEL_BORDER, ACCENT_COLOR, ACCENT_HOVER, TEXT_MAIN, TEXT_MUTED, COLOR_SUCCESS, get_font

# Import core classes
from core.resume_manager import ResumeManager
from core.ai_service import AIService
from core.ats_analyzer import ATSAnalyzer
from core.github_client import GitHubClient
from core.portfolio_builder import PortfolioBuilder

# Import sub-panels
from ui.dashboard import DashboardPanel
from ui.editor import EditorPanel
from ui.ai_assistant import AIAssistantPanel
from ui.ats_matcher import ATSMatcherPanel
from ui.github_import import GitHubImportPanel
from ui.portfolio_gen import PortfolioGenPanel

class ResumeStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("AI Resume Studio")
        self.geometry("1100x700")
        self.minsize(1000, 650)
        
        # Set dark theme globally
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize Core Services
        # Workspace is current working directory
        self.workspace_dir = os.getcwd()
        self.resume_manager = ResumeManager(self.workspace_dir)
        self.ai_service = AIService(self.workspace_dir)
        self.ats_analyzer = ATSAnalyzer()
        self.github_client = GitHubClient()
        self.portfolio_builder = PortfolioBuilder(self.workspace_dir)

        # Main Layout: Grid (1 row, 2 columns)
        # Col 0: Sidebar (width: 250)
        # Col 1: Main Content Area
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create Sidebar
        self.setup_sidebar()

        # Create Main Content Container
        self.main_container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Dictionary of active view frames
        self.frames = {}
        
        # Load all panel frames
        self.load_frames()

        # Default Active Tab
        self.show_frame("Dashboard")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, fg_color=PANEL_BG, corner_radius=0, border_color=PANEL_BORDER, border_width=1)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Logo / Title
        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🚀 AI Resume Studio", 
            font=get_font(18, "bold"), 
            text_color=TEXT_MAIN
        )
        logo_label.pack(pady=20, padx=10, anchor="w")

        # Menu Buttons Frame
        self.menu_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.menu_frame.pack(fill="x", padx=10, pady=10)

        # Sidebar Menu Items
        self.menu_buttons = {}
        menu_items = [
            ("Dashboard", "Dashboard"),
            ("Resume Editor", "Resume Editor"),
            ("AI Assistant", "AI Assistant"),
            ("ATS & Job Matcher", "ATS & Matcher"),
            ("GitHub Import", "GitHub Import"),
            ("Portfolio Website", "Portfolio Gen"),
            ("Settings", "Settings")
        ]

        for display_name, frame_id in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=display_name,
                font=get_font(13, "semibold"),
                height=38,
                fg_color="transparent",
                text_color=TEXT_MUTED,
                hover_color=PANEL_BORDER,
                anchor="w",
                command=lambda fid=frame_id: self.show_frame(fid)
            )
            btn.pack(fill="x", pady=4)
            self.menu_buttons[frame_id] = btn

        # Bottom section: Resume File Switcher & Save Options
        self.file_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.file_frame.pack(fill="x", side="bottom", padx=10, pady=20)

        # Divider
        div = ctk.CTkFrame(self.file_frame, height=1, fg_color=PANEL_BORDER)
        div.pack(fill="x", pady=10)

        # Version label
        ver_label = ctk.CTkLabel(self.file_frame, text="RESUME VERSION", font=get_font(10, "bold"), text_color=TEXT_MUTED)
        ver_label.pack(anchor="w", padx=5, pady=2)

        # Dropdown to select saved resume versions
        self.resume_dropdown = ctk.CTkOptionMenu(
            self.file_frame,
            values=["default_resume.json"],
            font=get_font(12),
            dropdown_font=get_font(12),
            fg_color=PANEL_BORDER,
            button_color=PANEL_BORDER,
            button_hover_color=ACCENT_COLOR,
            command=self.on_resume_version_changed
        )
        self.resume_dropdown.pack(fill="x", pady=5)
        self.refresh_resume_list()

        # Action Buttons for resume version files
        btn_layout = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        btn_layout.pack(fill="x", pady=5)
        btn_layout.grid_columnconfigure(0, weight=1)
        btn_layout.grid_columnconfigure(1, weight=1)

        # Save Button
        self.save_btn = ctk.CTkButton(
            btn_layout,
            text="Save Current",
            font=get_font(11, "bold"),
            height=28,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.save_active_resume
        )
        self.save_btn.grid(row=0, column=0, padx=2, sticky="ew")

        # Save As... Button
        self.save_as_btn = ctk.CTkButton(
            btn_layout,
            text="New Version",
            font=get_font(11, "bold"),
            height=28,
            fg_color=PANEL_BORDER,
            hover_color=ACCENT_COLOR,
            command=self.save_resume_as_new
        )
        self.save_as_btn.grid(row=0, column=1, padx=2, sticky="ew")

    def load_frames(self):
        # Instantiate views and add them to the main container
        self.frames["Dashboard"] = DashboardPanel(self.main_container, self)
        self.frames["Resume Editor"] = EditorPanel(self.main_container, self)
        self.frames["AI Assistant"] = AIAssistantPanel(self.main_container, self)
        self.frames["ATS & Matcher"] = ATSMatcherPanel(self.main_container, self)
        self.frames["GitHub Import"] = GitHubImportPanel(self.main_container, self)
        self.frames["Portfolio Gen"] = PortfolioGenPanel(self.main_container, self)
        self.frames["Settings"] = self.setup_settings_frame()

        for name, frame in self.frames.items():
            if isinstance(frame, ctk.CTkFrame):
                frame.grid(row=0, column=0, sticky="nsew")

    def setup_settings_frame(self):
        settings_frame = ctk.CTkFrame(self.main_container, fg_color=PANEL_BG, corner_radius=8, border_color=PANEL_BORDER, border_width=1)
        
        # Scrollable container for settings
        scroll_frame = ctk.CTkScrollableFrame(settings_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(scroll_frame, text="Settings & AI Integration", font=get_font(20, "bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 20))

        # API Type Selector
        api_type_label = ctk.CTkLabel(scroll_frame, text="AI Service Provider:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        api_type_label.pack(anchor="w", pady=(10, 5))

        self.api_type_menu = ctk.CTkOptionMenu(
            scroll_frame,
            values=["Offline Simulator (No API Key Required)", "Gemini API", "OpenAI API", "Custom / Ollama Local"],
            font=get_font(12),
            fg_color=PANEL_BORDER,
            button_color=PANEL_BORDER,
            button_hover_color=ACCENT_COLOR,
            command=self.on_api_type_changed
        )
        self.api_type_menu.pack(fill="x", pady=5)

        # API Key input
        self.key_label = ctk.CTkLabel(scroll_frame, text="API Key:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        self.key_label.pack(anchor="w", pady=(15, 5))

        self.key_entry = ctk.CTkEntry(
            scroll_frame, 
            show="*", 
            placeholder_text="Enter your API Key...", 
            font=get_font(12),
            fg_color=BG_DARK,
            border_color=PANEL_BORDER
        )
        self.key_entry.pack(fill="x", pady=5)

        # Base URL input (for custom endpoints / Ollama)
        self.url_label = ctk.CTkLabel(scroll_frame, text="API Base URL (OpenAI/Ollama Custom):", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        self.url_label.pack(anchor="w", pady=(15, 5))

        self.url_entry = ctk.CTkEntry(
            scroll_frame, 
            placeholder_text="e.g. http://localhost:11434/v1 or https://api.openai.com/v1", 
            font=get_font(12),
            fg_color=BG_DARK,
            border_color=PANEL_BORDER
        )
        self.url_entry.pack(fill="x", pady=5)

        # Model Name input
        self.model_label = ctk.CTkLabel(scroll_frame, text="Model Name:", font=get_font(13, "bold"), text_color=TEXT_MAIN)
        self.model_label.pack(anchor="w", pady=(15, 5))

        self.model_entry = ctk.CTkEntry(
            scroll_frame, 
            placeholder_text="e.g. gpt-4o, llama3, etc.", 
            font=get_font(12),
            fg_color=BG_DARK,
            border_color=PANEL_BORDER
        )
        self.model_entry.pack(fill="x", pady=5)

        # Info Box about the active mode
        self.info_box = ctk.CTkLabel(
            scroll_frame,
            text="",
            font=get_font(12, "italic"),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=600
        )
        self.info_box.pack(anchor="w", pady=20)

        # Save Button
        save_btn = ctk.CTkButton(
            scroll_frame,
            text="Save Settings",
            font=get_font(13, "bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.save_settings
        )
        save_btn.pack(anchor="w", pady=10)

        # Fill with loaded settings
        self.load_settings_into_ui()
        return settings_frame

    def load_settings_into_ui(self):
        config = self.ai_service.config
        
        # Set dropdown selection
        api_type_map = {
            "offline": "Offline Simulator (No API Key Required)",
            "gemini": "Gemini API",
            "openai": "OpenAI API",
            "custom": "Custom / Ollama Local"
        }
        self.api_type_menu.set(api_type_map.get(config.get("api_type", "offline"), "Offline Simulator (No API Key Required)"))
        
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, config.get("api_key", ""))
        
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, config.get("openai_base_url", "https://api.openai.com/v1"))
        
        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, config.get("custom_model", "gpt-4o"))
        
        self.on_api_type_changed(self.api_type_menu.get())

    def on_api_type_changed(self, choice):
        if "Offline" in choice:
            self.key_entry.configure(state="disabled")
            self.url_entry.configure(state="disabled")
            self.model_entry.configure(state="disabled")
            self.info_box.configure(
                text="ℹ️ Running in Offline Mode. AI operations (rewriting, bullet improvements, chatbot, interview generator) are fully simulated using rules and patterns. No internet connection or API keys are required."
            )
        elif "Gemini" in choice:
            self.key_entry.configure(state="normal")
            self.url_entry.configure(state="disabled")
            self.model_entry.configure(state="disabled")
            self.info_box.configure(
                text="ℹ️ Gemini API mode. Uses the official Google Generative AI endpoints. Please provide a valid Gemini API Key. Model will default to gemini-2.5-flash."
            )
        elif "OpenAI" in choice:
            self.key_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            self.model_entry.configure(state="normal")
            self.info_box.configure(
                text="ℹ️ OpenAI API mode. Uses OpenAI chat completions endpoint. Enter your API Key. You can specify a custom model name (e.g. gpt-4o, gpt-3.5-turbo)."
            )
        elif "Custom" in choice:
            self.key_entry.configure(state="normal")
            self.url_entry.configure(state="normal")
            self.model_entry.configure(state="normal")
            self.info_box.configure(
                text="ℹ️ Custom endpoint / Local LLM mode. Can connect to Ollama (typically http://localhost:11434/v1) or other local gateway APIs. No API key is required if your local server doesn't enforce auth."
            )

    def save_settings(self):
        choice = self.api_type_menu.get()
        api_type_map = {
            "Offline Simulator (No API Key Required)": "offline",
            "Gemini API": "gemini",
            "OpenAI API": "openai",
            "Custom / Ollama Local": "custom"
        }
        api_type = api_type_map.get(choice, "offline")
        
        self.ai_service.update_config("api_type", api_type)
        self.ai_service.update_config("api_key", self.key_entry.get().strip())
        self.ai_service.update_config("openai_base_url", self.url_entry.get().strip())
        self.ai_service.update_config("custom_model", self.model_entry.get().strip())
        
        messagebox.showinfo("Success", "Settings saved successfully!")

    def show_frame(self, frame_name):
        # Unselect all buttons
        for btn in self.menu_buttons.values():
            btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

        # Select target button (if exists in menu)
        if frame_name in self.menu_buttons:
            self.menu_buttons[frame_name].configure(fg_color=PANEL_BORDER, text_color=TEXT_MAIN)

        # Show target frame
        frame = self.frames[frame_name]
        frame.tkraise()
        
        # Trigger refresh callbacks on the frames when opened
        if hasattr(frame, "on_refresh"):
            frame.on_refresh()

    def refresh_resume_list(self):
        files = self.resume_manager.list_saved_resumes()
        self.resume_dropdown.configure(values=files)
        # Update dropdown setting to match in-memory file
        if self.resume_manager.current_filename in files:
            self.resume_dropdown.set(self.resume_manager.current_filename)
        else:
            self.resume_dropdown.set("default_resume.json")

    def on_resume_version_changed(self, selected_file):
        path = os.path.join(self.resume_manager.resumes_dir, selected_file)
        data = self.resume_manager.load_resume_file(path)
        if data:
            # Refresh current active view
            active_frame = self.get_active_frame_name()
            if active_frame:
                self.show_frame(active_frame)
            messagebox.showinfo("Loaded", f"Loaded resume: {selected_file}")
        else:
            messagebox.showerror("Error", f"Failed to load resume: {selected_file}")

    def save_active_resume(self):
        # We need to collect data from EditorPanel if it's currently loaded
        editor = self.frames.get("Resume Editor")
        if editor and hasattr(editor, "get_edited_data"):
            data = editor.get_edited_data()
            self.resume_manager.current_data = data
            
        success = self.resume_manager.save_current_resume()
        if success:
            messagebox.showinfo("Saved", f"Successfully saved to {self.resume_manager.current_filename}!")
            # Trigger refresh of analytics score if editor isn't showing
            self.refresh_current_view()
        else:
            messagebox.showerror("Error", "Failed to save resume.")

    def save_resume_as_new(self):
        # Open small dialog prompt for filename
        dialog = ctk.CTkInputDialog(text="Enter new version name (e.g. software_engineer):", title="New Resume Version")
        name = dialog.get_input()
        if name:
            name = name.strip().replace(" ", "_")
            if not name.endswith(".json"):
                name += ".json"
            
            # Collect data from editor first
            editor = self.frames.get("Resume Editor")
            if editor and hasattr(editor, "get_edited_data"):
                data = editor.get_edited_data()
            else:
                data = self.resume_manager.current_data
                
            success = self.resume_manager.save_resume_as(data, name)
            if success:
                self.refresh_resume_list()
                messagebox.showinfo("Success", f"Created new version: {name}")
                self.refresh_current_view()
            else:
                messagebox.showerror("Error", "Failed to create new version file.")

    def refresh_current_view(self):
        active_frame = self.get_active_frame_name()
        if active_frame:
            frame = self.frames[active_frame]
            if hasattr(frame, "on_refresh"):
                frame.on_refresh()

    def get_active_frame_name(self):
        for name, frame in self.frames.items():
            # Check which frame is raised (mapped in TK terms)
            if isinstance(frame, ctk.CTkFrame) and frame.winfo_ismapped():
                return name
        return "Dashboard"
