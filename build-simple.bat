@echo off
REM Alternative build script using direct PyInstaller command
REM This often works better for GUI applications with DLL issues

echo ========================================
echo APODPaper Alternative Build Script
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

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build using direct PyInstaller command with compatibility options
echo.
echo ========================================
echo Building APODPaper executable...
echo ========================================
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "APODPaper" ^
    --icon "assets\icon.ico" ^
    --add-data "assets\icon.png;assets" ^
    --add-data "assets\icon.ico;assets" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "pystray._win32" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "_tkinter" ^
    --hidden-import "PIL.ImageTk" ^
    --exclude-module "matplotlib" ^
    --exclude-module "numpy" ^
    --exclude-module "scipy" ^
    --exclude-module "pandas" ^
    --exclude-module "jupyter" ^
    --exclude-module "PyQt5" ^
    --exclude-module "PyQt6" ^
    --exclude-module "PySide2" ^
    --exclude-module "PySide6" ^
    --noupx ^
    main.py

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
    echo Try running: build-simple.bat
)

if exist "venv\Scripts\activate.bat" (
    echo Deactivating virtual environment...
    deactivate
)

echo.
echo Press any key to exit...
pause >nul
