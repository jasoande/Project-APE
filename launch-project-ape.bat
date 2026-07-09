@echo off
REM Account Intelligence - Windows Launcher
REM Double-click this file to launch the Account Intelligence dashboard

setlocal

REM Configuration
set DASHBOARD_PORT=8765
set CONFIG_URL=http://localhost:%DASHBOARD_PORT%/configure

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if server is already running
curl -s -o nul -w "%%{http_code}" %CONFIG_URL% | findstr "200" >nul
if %ERRORLEVEL%==0 (
    echo Dashboard is already running, opening browser...
    start "" %CONFIG_URL%
    exit /b 0
)

REM Check for virtual environment
set VENV_PYTHON=%USERPROFILE%\.project-ape-venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo Error: Virtual environment not found
    echo Please run setup-environment.sh first
    pause
    exit /b 1
)

REM Start dashboard server in background
echo Starting Account Intelligence dashboard...
start /b "" "%VENV_PYTHON%" "%SCRIPT_DIR%dashboard\server.py" >nul 2>&1

REM Wait for server to start
timeout /t 2 /nobreak >nul

for /L %%i in (1,1,20) do (
    curl -s -o nul -w "%%{http_code}" %CONFIG_URL% | findstr "200" >nul
    if not ERRORLEVEL 1 (
        start "" %CONFIG_URL%
        exit /b 0
    )
    timeout /t 1 /nobreak >nul
)

echo Failed to start dashboard server
pause
exit /b 1
