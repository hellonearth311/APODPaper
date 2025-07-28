@echo off
REM APODPaper Build Script
REM This script builds the APODPaper application into a standalone executable

echo ========================================
echo APODPaper Build Script
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

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build the application
echo.
echo ========================================
echo Building APODPaper executable...
echo ========================================
echo.

pyinstaller main.spec

REM Check if build was successful
if exist "dist\APODPaper.exe" (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\APODPaper.exe
    echo.
    echo You can now run the application by double-clicking:
    echo %cd%\dist\APODPaper.exe
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
    echo Please check the output above for errors.
)

echo Deactivating virtual environment...
deactivate

echo.
echo Press any key to exit...
pause >nul
