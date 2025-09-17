#!/usr/bin/env python3
"""
Dependency checker for Cash Balance Tracker GUI

Run this script to check if all required dependencies are installed.
"""

import sys

def check_dependencies():
    """Check if all required dependencies are available"""
    
    missing_packages = []
    available_packages = []
    
    print("=== Cash Balance Tracker - Dependency Check ===\n")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 6):
        print("❌ ERROR: Python 3.6 or higher is required")
        return False
    else:
        print("✅ Python version is compatible\n")
    
    # Check required packages
    packages_to_check = [
        ('tkinter', 'GUI framework (usually included with Python)'),
        ('pandas', 'Data analysis library'),
        ('numpy', 'Numerical computing (required by pandas)'),
        ('datetime', 'Date/time handling (built-in)'),
        ('threading', 'Multi-threading support (built-in)'),
        ('os', 'Operating system interface (built-in)'),
        ('sys', 'System-specific parameters (built-in)')
    ]
    
    print("Checking required packages:")
    print("-" * 50)
    
    for package, description in packages_to_check:
        try:
            if package == 'tkinter':
                import tkinter as tk
                # Test if tkinter actually works
                root = tk.Tk()
                root.withdraw()  # Hide the window
                root.destroy()
            elif package == 'pandas':
                import pandas as pd
            elif package == 'numpy':
                import numpy as np
            elif package == 'datetime':
                import datetime
            elif package == 'threading':
                import threading
            elif package == 'os':
                import os
            elif package == 'sys':
                import sys as sys_module
                
            print(f"✅ {package:12} - {description}")
            available_packages.append(package)
            
        except ImportError:
            print(f"❌ {package:12} - {description} (MISSING)")
            missing_packages.append(package)
        except Exception as e:
            print(f"⚠️  {package:12} - {description} (ERROR: {e})")
            missing_packages.append(package)
    
    # Check optional packages
    print("\nChecking optional packages:")
    print("-" * 50)
    
    optional_packages = [
        ('openpyxl', 'Excel file support (.xlsx)'),
        ('xlrd', 'Excel file support (.xls)')
    ]
    
    for package, description in optional_packages:
        try:
            if package == 'openpyxl':
                import openpyxl
            elif package == 'xlrd':
                import xlrd
                
            print(f"✅ {package:12} - {description}")
            
        except ImportError:
            print(f"⚠️  {package:12} - {description} (Optional, install for Excel support)")
    
    # Summary
    print("\n" + "=" * 60)
    
    if not missing_packages:
        print("✅ ALL REQUIRED DEPENDENCIES ARE AVAILABLE!")
        print("\nYou can run the Cash Balance Tracker GUI by:")
        print("1. Double-clicking 'run_gui.py'")
        print("2. Or running: python cash_balance_gui.py")
        
        # Check if Excel support is available
        excel_support = True
        try:
            import openpyxl
        except ImportError:
            excel_support = False
            
        if excel_support:
            print("\n✅ Excel file support is available")
        else:
            print("\n⚠️  Excel support not available. Install openpyxl for .xlsx files:")
            print("   pip install openpyxl")
            
        return True
        
    else:
        print("❌ MISSING REQUIRED DEPENDENCIES:")
        for package in missing_packages:
            print(f"   - {package}")
            
        print("\nTo install missing packages, run:")
        if 'pandas' in missing_packages:
            print("   pip install pandas")
        if 'tkinter' in missing_packages:
            print("   # tkinter usually comes with Python")
            print("   # Try: sudo apt-get install python3-tk (on Ubuntu/Debian)")
            print("   # Or reinstall Python with tkinter support")
            
        print("\nFor Excel support (optional):")
        print("   pip install openpyxl")
        
        return False

def main():
    """Main function"""
    try:
        success = check_dependencies()
        
        if success:
            print("\n🎉 Ready to use Cash Balance Tracker!")
        else:
            print("\n⚠️  Please install missing dependencies before using the GUI.")
            
    except Exception as e:
        print(f"\n❌ Error during dependency check: {e}")
        
    try:
        input("\nPress Enter to exit...")
    except (EOFError, KeyboardInterrupt):
        pass  # Handle non-interactive environments

if __name__ == "__main__":
    main()
