#!/usr/bin/env python3
"""
Build script for creating standalone Cash Balance Tracker releases

This script creates platform-specific executables using PyInstaller
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Darwin":
        return "macOS", "app"
    elif system == "Windows":
        return "Windows", "exe"
    else:
        return "Linux", "bin"

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for the application"""
    
    platform_name, _ = get_platform_info()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cash_balance_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cash_balance_tracker.py', '.'),
        ('requirements.txt', '.'),
        ('GUI_README.md', '.'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'openpyxl',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CashBalanceTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if platform.system() == 'Windows' else 'app_icon.icns',
)

# macOS App Bundle
{"app = BUNDLE(exe, name='CashBalanceTracker.app', icon='app_icon.icns', bundle_identifier='com.cashbalancetracker.app')" if platform_name == "macOS" else ""}
'''
    
    with open('CashBalanceTracker.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")

def create_icons():
    """Create application icons (placeholder text files for now)"""
    
    # Create a simple text-based icon description
    icon_info = """
# Application Icons

For a professional release, you should create:

1. app_icon.ico (Windows) - 256x256 or multiple sizes
2. app_icon.icns (macOS) - Multiple resolutions
3. app_icon.png (Linux) - 512x512

You can create these from a source image using online converters or tools like:
- GIMP (free)
- Icon Generator websites
- Command line tools (iconutil on macOS)

For now, the app will use default system icons.
"""
    
    with open('ICON_README.txt', 'w') as f:
        f.write(icon_info)

def build_executable():
    """Build the standalone executable"""
    
    platform_name, extension = get_platform_info()
    
    print(f"🔨 Building for {platform_name}...")
    
    # Create the spec file
    create_spec_file()
    create_icons()
    
    # Build with PyInstaller
    try:
        cmd = [sys.executable, "-m", "PyInstaller", "CashBalanceTracker.spec", "--clean"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Show output location
            if platform_name == "macOS":
                app_path = "dist/CashBalanceTracker.app"
                if os.path.exists(app_path):
                    print(f"📱 macOS App Bundle created: {app_path}")
                    print("   You can drag this to Applications folder")
            else:
                exe_path = f"dist/CashBalanceTracker{'.exe' if platform_name == 'Windows' else ''}"
                if os.path.exists(exe_path):
                    print(f"💻 Executable created: {exe_path}")
            
            return True
        else:
            print("❌ Build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_release_package():
    """Create a complete release package"""
    
    platform_name, _ = get_platform_info()
    
    # Create release directory
    release_dir = f"release_package_{platform_name.lower()}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    print(f"📦 Creating release package in {release_dir}/")
    
    # Copy documentation
    docs_to_copy = [
        "GUI_README.md",
        "CSV_Usage_Guide.md", 
        "FIXES_AND_USAGE_GUIDE.md",
        "requirements.txt",
        "ICON_README.txt"
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, release_dir)
    
    # Copy the built executable/app
    if platform_name == "macOS":
        app_path = "dist/CashBalanceTracker.app"
        if os.path.exists(app_path):
            shutil.copytree(app_path, f"{release_dir}/CashBalanceTracker.app")
    else:
        exe_name = f"CashBalanceTracker{'.exe' if platform_name == 'Windows' else ''}"
        exe_path = f"dist/{exe_name}"
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, f"{release_dir}/{exe_name}")
    
    # Create installation instructions
    install_instructions = create_install_instructions(platform_name)
    with open(f"{release_dir}/INSTALLATION.md", 'w') as f:
        f.write(install_instructions)
    
    print(f"✅ Release package created: {release_dir}/")
    return release_dir

def create_install_instructions(platform_name):
    """Create platform-specific installation instructions"""
    
    if platform_name == "macOS":
        return """# Cash Balance Tracker - macOS Installation

## Installation Options

### Option 1: App Bundle (Recommended)
1. Double-click `CashBalanceTracker.app` to run directly
2. Or drag `CashBalanceTracker.app` to your Applications folder
3. Launch from Launchpad or Applications

### Option 2: Python Source (If you have Python installed)
1. Install Python 3.8+ from python.org
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python cash_balance_gui.py`

## Usage
1. Launch Cash Balance Tracker
2. Click "Browse..." to select your trading data file
3. Set starting cash amount
4. Click "Analyze Trading Data"
5. View results and save if needed

## Supported File Formats
- CSV files (recommended)
- Excel files (.xlsx, .xls) - requires openpyxl

## Troubleshooting

### "App can't be opened because it is from an unidentified developer"
1. Right-click the app and select "Open"
2. Click "Open" in the security dialog
3. Or go to System Preferences > Security & Privacy > General > "Open Anyway"

### Missing Excel Support
Install openpyxl: `pip3 install openpyxl`

## System Requirements
- macOS 10.12 (Sierra) or later
- 64-bit Intel or Apple Silicon Mac
"""

    elif platform_name == "Windows":
        return """# Cash Balance Tracker - Windows Installation

## Installation Options

### Option 1: Standalone Executable (Recommended)
1. Double-click `CashBalanceTracker.exe` to run
2. No installation required - runs directly

### Option 2: Python Source (If you have Python installed)
1. Install Python 3.8+ from python.org
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python cash_balance_gui.py`

## Usage
1. Double-click CashBalanceTracker.exe
2. Click "Browse..." to select your trading data file
3. Set starting cash amount
4. Click "Analyze Trading Data"
5. View results and save if needed

## Supported File Formats
- CSV files (recommended)
- Excel files (.xlsx, .xls) - built-in support

## Troubleshooting

### Windows Defender Warning
1. Click "More info" in the warning dialog
2. Click "Run anyway"
3. This happens because the executable isn't digitally signed

### Missing Excel Support
The standalone version includes Excel support

## System Requirements
- Windows 7 SP1 or later
- 64-bit Windows recommended
"""

    else:  # Linux
        return """# Cash Balance Tracker - Linux Installation

## Installation Options

### Option 1: Standalone Binary (If available)
1. Make executable: `chmod +x CashBalanceTracker`
2. Run: `./CashBalanceTracker`

### Option 2: Python Source (Recommended)
1. Install Python 3.8+: `sudo apt install python3 python3-pip python3-tk`
2. Install dependencies: `pip3 install -r requirements.txt`
3. Run: `python3 cash_balance_gui.py`

## Usage
1. Launch Cash Balance Tracker
2. Click "Browse..." to select your trading data file
3. Set starting cash amount
4. Click "Analyze Trading Data"
5. View results and save if needed

## Supported File Formats
- CSV files (recommended)
- Excel files (.xlsx, .xls) - requires openpyxl

## Dependencies
Install required packages:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
pip3 install pandas openpyxl
```

## System Requirements
- Linux with X11 (most desktop distributions)
- Python 3.8 or later
- tkinter support
"""

def main():
    """Main build function"""
    
    print("🚀 Cash Balance Tracker - Release Builder")
    print("=" * 50)
    
    platform_name, extension = get_platform_info()
    print(f"Platform detected: {platform_name}")
    
    # Check if we can build standalone executables
    if not install_pyinstaller():
        print("⚠️  PyInstaller not available. Creating source release only.")
        release_dir = create_release_package()
        print(f"✅ Source release package created: {release_dir}")
        return
    
    # Build executable
    if build_executable():
        # Create complete release package
        release_dir = create_release_package()
        
        print("\n🎉 Release build completed successfully!")
        print(f"📁 Release package: {release_dir}/")
        print(f"🔧 Platform: {platform_name}")
        
        if platform_name == "macOS":
            print("📱 App bundle ready for distribution")
        elif platform_name == "Windows":
            print("💻 Standalone .exe ready for distribution")
        else:
            print("🐧 Linux binary ready for distribution")
            
        print("\n📋 Next steps:")
        print(f"1. Test the application in {release_dir}/")
        print("2. Distribute the entire release_package folder")
        print("3. Users can follow INSTALLATION.md instructions")
        
    else:
        print("\n❌ Build failed. Check the error messages above.")
        print("💡 You can still distribute the Python source files.")

if __name__ == "__main__":
    main()
