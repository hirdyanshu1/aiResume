# Custom Styling and Colors for AI Resume Studio

import customtkinter as ctk

# Color Palette (Slate / Indigo theme)
BG_DARK = "#0f172a"          # Slate 900
PANEL_BG = "#1e293b"         # Slate 800
PANEL_BORDER = "#334155"     # Slate 700
ACCENT_COLOR = "#6366f1"     # Indigo 500
ACCENT_HOVER = "#4f46e5"     # Indigo 600

TEXT_MAIN = "#f8fafc"        # Slate 50
TEXT_MUTED = "#94a3b8"       # Slate 400

# Functional Colors
COLOR_SUCCESS = "#10b981"    # Emerald 500
COLOR_WARNING = "#f59e0b"    # Amber 500
COLOR_DANGER = "#ef4444"     # Red 500
COLOR_INFO = "#38bdf8"       # Sky 400

# Typography
FONT_FAMILY = "Segoe UI"     # Fallback system font that looks clean

def get_font(size=12, weight="normal"):
    # Tkinter natively supports: "normal", "bold", "italic", "roman"
    # Map semibold/medium to bold to avoid _tkinter.TclError on Windows/Linux
    if weight in ["semibold", "medium"]:
        weight = "bold"
    elif weight not in ["bold", "italic", "normal"]:
        weight = "normal"
    return (FONT_FAMILY, size, weight)


# Helper function to create standard section headers
def create_section_header(parent, title_text):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    
    label = ctk.CTkLabel(
        frame, 
        text=title_text, 
        font=get_font(18, "bold"), 
        text_color=TEXT_MAIN
    )
    label.pack(side="left", pady=10)

    
    # Bottom separator line
    sep = ctk.CTkFrame(frame, height=2, fg_color=PANEL_BORDER)
    sep.pack(fill="x", side="bottom")
    
    return frame
