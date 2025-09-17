#!/usr/bin/env python3
"""
Simple launcher for the Cash Balance Tracker GUI

Double-click this file to open the Cash Balance Tracker interface.
"""

import sys
import os

# Add current directory to path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from cash_balance_gui import main
    
    if __name__ == "__main__":
        print("Starting Cash Balance Tracker GUI...")
        main()
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure all required files are in the same directory:")
    print("- cash_balance_gui.py")
    print("- cash_balance_tracker.py")
    input("Press Enter to exit...")
    
except Exception as e:
    print(f"Error starting application: {e}")
    input("Press Enter to exit...")
