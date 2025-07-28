@echo off
REM Development Setup Script for APODPaper
REM This script sets up the development environment

echo ========================================
echo APODPaper Development Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Install development dependencies
echo Installing development dependencies...
pip install pyinstaller

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To run the application in development mode:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python main.py
echo.
echo To build the executable:
echo 1. Run: build.bat
echo.

echo Deactivating virtual environment...
deactivate

echo.
echo Press any key to exit...
pause >nul
