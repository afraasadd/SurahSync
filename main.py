"""
Hifz Companion - Main Application Entry Point
"""

import tkinter as tk
from gui import HifzCompanionGUI
from hifz_tester import HifzTester


def main():
    """Start the Hifz Companion application"""
    print("🕌 Starting Hifz Companion...")

    try:
        # Initialize the tester
        tester = HifzTester()
        print("✅ HifzTester initialized successfully!")

        # Start GUI
        root = tk.Tk()
        app = HifzCompanionGUI(root, tester)

        print("✅ GUI loaded successfully!")
        print("🚀 Application ready!")
        root.mainloop()

    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()