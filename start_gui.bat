@echo off
REM Cash Balance Tracker GUI Launcher for Windows

echo Starting Cash Balance Tracker GUI...
echo ======================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.6 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "cash_balance_gui.py" (
    echo Error: cash_balance_gui.py not found in current directory.
    pause
    exit /b 1
)

if not exist "cash_balance_tracker.py" (
    echo Error: cash_balance_tracker.py not found in current directory.
    pause
    exit /b 1
)

REM Try to run the GUI
echo Launching GUI with Python...
python cash_balance_gui.py

REM If we get here, the GUI has closed or there was an error
if %errorlevel% neq 0 (
    echo.
    echo Error occurred while running the GUI.
    echo Please check that all dependencies are installed:
    echo   pip install pandas openpyxl
    echo.
    pause
)

echo GUI closed.
