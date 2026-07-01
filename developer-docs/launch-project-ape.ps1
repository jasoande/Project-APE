# Project APE - PowerShell Launcher
# Run this script on Windows to launch Project APE dashboard
# Usage: .\launch-project-ape.ps1

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion"
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Run the Python launcher
$pythonScript = Join-Path $ScriptDir "launch-project-ape.py"

if (Test-Path $pythonScript) {
    python $pythonScript
} else {
    Write-Host "Error: Launcher script not found at $pythonScript" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Pause if there was an error
if ($LASTEXITCODE -ne 0) {
    Read-Host -Prompt "Press Enter to exit"
}
