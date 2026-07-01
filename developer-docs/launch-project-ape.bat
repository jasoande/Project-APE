@echo off
REM Project APE - Windows Batch Launcher
REM Double-click this file to launch Project APE dashboard on Windows

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Run the Python launcher script
python "%SCRIPT_DIR%launch-project-ape.py"

REM Pause to see any error messages (only if script exits with error)
if errorlevel 1 pause
