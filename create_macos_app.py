#!/usr/bin/env python3
"""
Create a native macOS App Bundle for Cash Balance Tracker

This creates a proper .app bundle that can be distributed on macOS
"""

import os
import shutil
import sys
import stat
from pathlib import Path

def create_app_bundle():
    """Create a macOS .app bundle"""
    
    app_name = "CashBalanceTracker"
    app_dir = f"{app_name}.app"
    
    print(f"Creating macOS App Bundle: {app_dir}")
    
    # Remove existing app bundle
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    
    # Create app bundle structure
    os.makedirs(f"{app_dir}/Contents/MacOS", exist_ok=True)
    os.makedirs(f"{app_dir}/Contents/Resources", exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.cashbalancetracker.app</string>
    <key>CFBundleName</key>
    <string>Cash Balance Tracker</string>
    <key>CFBundleDisplayName</key>
    <string>Cash Balance Tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>csv</string>
                <string>xlsx</string>
                <string>xls</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Trading Data Files</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
</dict>
</plist>"""
    
    with open(f"{app_dir}/Contents/Info.plist", 'w') as f:
        f.write(info_plist)
    
    # Create launcher script
    launcher_script = f"""#!/bin/bash
# Cash Balance Tracker macOS App Launcher

# Get the directory containing this script
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Change to resources directory
cd "$RESOURCES_DIR"

# Find Python
PYTHON_CMD=""
for cmd in python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v "$cmd" &> /dev/null; then
        # Check if this Python version has tkinter
        if "$cmd" -c "import tkinter" 2>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    # Show error dialog using macOS native dialog
    osascript -e 'display dialog "Python 3.8+ with tkinter is required to run Cash Balance Tracker.\\n\\nPlease install Python from python.org or using Homebrew:\\nbrew install python3" with title "Cash Balance Tracker" buttons {{"OK"}} default button "OK" with icon stop'
    exit 1
fi

# Check for required packages and install if needed
if ! "$PYTHON_CMD" -c "import pandas" 2>/dev/null; then
    # Ask user if they want to install dependencies
    response=$(osascript -e 'display dialog "Cash Balance Tracker needs to install required packages (pandas, openpyxl).\\n\\nThis is safe and only affects this application." with title "Install Dependencies" buttons {{"Cancel", "Install"}} default button "Install" with icon note')
    
    if [[ "$response" == *"Install"* ]]; then
        # Try to install packages
        "$PYTHON_CMD" -m pip install --user pandas openpyxl
        
        # Check if installation was successful
        if ! "$PYTHON_CMD" -c "import pandas" 2>/dev/null; then
            osascript -e 'display dialog "Failed to install required packages. Please install manually:\\n\\npip3 install pandas openpyxl" with title "Installation Failed" buttons {{"OK"}} default button "OK" with icon stop'
            exit 1
        fi
    else
        exit 1
    fi
fi

# Launch the application
exec "$PYTHON_CMD" cash_balance_gui.py
"""
    
    launcher_path = f"{app_dir}/Contents/MacOS/{app_name}"
    with open(launcher_path, 'w') as f:
        f.write(launcher_script)
    
    # Make launcher executable
    os.chmod(launcher_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    # Copy Python files to Resources
    files_to_copy = [
        'cash_balance_gui.py',
        'cash_balance_tracker.py',
        'requirements.txt',
        'GUI_README.md',
        'CSV_Usage_Guide.md'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, f"{app_dir}/Contents/Resources/")
    
    print(f"✅ macOS App Bundle created: {app_dir}")
    print("📱 You can now:")
    print(f"   1. Double-click {app_dir} to run")
    print(f"   2. Drag {app_dir} to Applications folder")
    print("   3. Distribute the .app bundle to other Mac users")
    
    return app_dir

def create_dmg_instructions():
    """Create instructions for creating a DMG file"""
    
    instructions = """# Creating a DMG for Distribution

To create a professional DMG file for distribution:

## Option 1: Using Disk Utility (GUI)
1. Open Disk Utility
2. File → New Image → Image from Folder
3. Select the CashBalanceTracker.app
4. Choose compressed format
5. Save as CashBalanceTracker.dmg

## Option 2: Using Terminal
```bash
hdiutil create -volname "Cash Balance Tracker" -srcfolder CashBalanceTracker.app -ov -format UDZO CashBalanceTracker.dmg
```

## Option 3: Professional DMG with background
1. Create a folder with:
   - CashBalanceTracker.app
   - Applications folder shortcut
   - Background image
2. Use create-dmg tool or DMG Canvas

The resulting DMG file can be distributed to users who can:
1. Double-click to mount
2. Drag app to Applications
3. Eject and delete DMG
"""
    
    with open('CREATE_DMG.md', 'w') as f:
        f.write(instructions)
    
    print("📄 DMG creation instructions saved to: CREATE_DMG.md")

if __name__ == "__main__":
    print("🍎 macOS App Bundle Creator")
    print("=" * 40)
    
    if not os.path.exists('cash_balance_gui.py'):
        print("❌ Error: cash_balance_gui.py not found")
        print("Run this script in the same directory as your Python files")
        sys.exit(1)
    
    app_bundle = create_app_bundle()
    create_dmg_instructions()
    
    print("\n🎉 macOS App Bundle creation completed!")
    print(f"📁 App Bundle: {app_bundle}")
    print("📋 Next steps:")
    print("1. Test the app bundle by double-clicking it")
    print("2. Create a DMG file for distribution (see CREATE_DMG.md)")
    print("3. The app will automatically handle Python dependencies")
    print("\n💡 Note: Users need Python 3.8+ installed on their Mac")
