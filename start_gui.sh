#!/bin/bash
# Cash Balance Tracker GUI Launcher for Linux/Mac
# Enhanced version with better macOS support

echo "Starting Cash Balance Tracker GUI..."
echo "======================================"

# Detect operating system
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    PLATFORM="macOS";;
    Linux*)     PLATFORM="Linux";;
    *)          PLATFORM="Unknown";;
esac

echo "Platform: $PLATFORM"

# Function to find Python
find_python() {
    # Try different Python commands in order of preference
    for cmd in python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v "$cmd" &> /dev/null; then
            # Check if this Python version is suitable
            version=$("$cmd" -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>/dev/null)
            if [ $? -eq 0 ]; then
                major=$(echo "$version" | cut -d. -f1)
                minor=$(echo "$version" | cut -d. -f2)
                if [ "$major" -eq 3 ] && [ "$minor" -ge 6 ]; then
                    echo "Found suitable Python: $cmd (version $version)" >&2  # Send to stderr
                    echo "$cmd"  # Send command to stdout for capture
                    return 0
                fi
            fi
        fi
    done
    
    # If no suitable Python found
    echo "Error: No suitable Python found. Need Python 3.6 or higher." >&2
    
    if [ "$PLATFORM" = "macOS" ]; then
        echo "" >&2
        echo "To install Python on macOS:" >&2
        echo "1. Visit https://www.python.org/downloads/" >&2
        echo "2. Download Python 3.8 or later" >&2
        echo "3. Or install via Homebrew: brew install python3" >&2
    else
        echo "" >&2
        echo "To install Python on Linux:" >&2
        echo "sudo apt update && sudo apt install python3 python3-pip" >&2
    fi
    
    return 1
}

# Check if Python 3 is available
PYTHON_CMD=$(find_python)
if [ $? -ne 0 ]; then
    read -p "Press Enter to exit..."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"

# Check for and activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Virtual environment activated: $(which python3)"
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Virtual environment activated: $(which python3)"
fi

# Check if required files exist
if [ ! -f "cash_balance_gui.py" ]; then
    echo "Error: cash_balance_gui.py not found in current directory."
    echo "Make sure all files are in the same folder:"
    echo "  - cash_balance_gui.py"
    echo "  - cash_balance_tracker.py"
    echo "  - requirements.txt"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -f "cash_balance_tracker.py" ]; then
    echo "Error: cash_balance_tracker.py not found in current directory."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import pandas, tkinter" 2>/dev/null; then
    echo "Warning: Missing dependencies detected."
    
    # Check if we're in a virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Installing packages in virtual environment..."
        $PYTHON_CMD -m pip install -r requirements.txt
    else
        echo "Not in a virtual environment. Attempting to install..."
        echo "If this fails, please:"
        echo "1. Create a virtual environment: python3 -m venv .venv"
        echo "2. Activate it: source .venv/bin/activate"  
        echo "3. Install packages: pip install -r requirements.txt"
        echo "4. Run this script again"
        echo ""
        
        # Try to install with user flag first
        if ! $PYTHON_CMD -m pip install --user -r requirements.txt 2>/dev/null; then
            echo "❌ Installation failed. Please set up a virtual environment:"
            echo ""
            echo "python3 -m venv .venv"
            echo "source .venv/bin/activate"
            echo "pip install -r requirements.txt"
            echo "./start_gui.sh"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
    fi
fi

# macOS-specific setup
if [ "$PLATFORM" = "macOS" ]; then
    # Ensure proper display environment
    if [ -z "$DISPLAY" ] && [ -n "$TERM_PROGRAM" ]; then
        export DISPLAY=:0
    fi
    
    # Use open command to ensure proper macOS app launching
    echo "Launching GUI with macOS integration..."
    exec $PYTHON_CMD cash_balance_gui.py
else
    # Linux/Unix
    echo "Launching GUI with $PYTHON_CMD..."
    exec $PYTHON_CMD cash_balance_gui.py
fi
