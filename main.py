import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import ResumeStudioApp

def main():
    try:
        app = ResumeStudioApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print("Application error:")
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
