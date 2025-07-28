# APODPaper Build Script (PowerShell)
# This script builds the APODPaper application into a standalone executable

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APODPaper Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install PyInstaller if not already installed
Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the application
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building APODPaper executable..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pyinstaller main.spec

# Check if build was successful
if (Test-Path "dist\APODPaper.exe") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\APODPaper.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the application by double-clicking:" -ForegroundColor Green
    Write-Host "$PWD\dist\APODPaper.exe" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Build failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the output above for errors." -ForegroundColor Red
}

Write-Host "Deactivating virtual environment..." -ForegroundColor Yellow
deactivate

Write-Host ""
Read-Host "Press Enter to exit"
