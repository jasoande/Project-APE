# Cross-Platform Launcher Guide

## Overview

Project APE now includes **cross-platform launchers** that work on Windows, Linux, and macOS. Choose the launcher that matches your operating system.

## Available Launchers

### 1. **Universal Python Launcher** (Recommended for all platforms)
**File**: `launch-project-ape.py`

- ✅ Works on Windows, Linux, and macOS
- ✅ No platform-specific dependencies
- ✅ Automatic platform detection
- ✅ Robust error handling

**Usage**:
```bash
# From terminal (any platform)
python3 launch-project-ape.py

# Direct execution (Unix/Linux/macOS)
./launch-project-ape.py

# Windows (command prompt or PowerShell)
python launch-project-ape.py
```

### 2. **Windows Batch Launcher**
**File**: `launch-project-ape.bat`

- 🪟 Windows only
- ✅ Double-click to run (no terminal needed)
- ✅ Automatically checks for Python installation

**Usage**:
- **Double-click** `launch-project-ape.bat` in Windows Explorer
- Or run from Command Prompt: `launch-project-ape.bat`

### 3. **Windows PowerShell Launcher**
**File**: `launch-project-ape.ps1`

- 🪟 Windows PowerShell
- ✅ More modern than batch script
- ✅ Better error messages

**Usage**:
```powershell
# Right-click → "Run with PowerShell"
# Or from PowerShell terminal:
.\launch-project-ape.ps1
```

**Note**: You may need to allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. **Linux/Unix Shell Launcher**
**File**: `launch-project-ape.sh`

- 🐧 Linux and Unix systems
- ✅ Double-click from file manager (if configured for shell scripts)
- ✅ Standard bash script

**Usage**:
```bash
# From terminal
./launch-project-ape.sh

# Or with explicit bash
bash launch-project-ape.sh
```

### 5. **macOS Command Launcher** (Legacy)
**File**: `launch-project-ape.command`

- 🍎 macOS only
- ✅ Double-click in Finder
- ⚠️ macOS-specific, not cross-platform

**Usage**:
- **Double-click** in macOS Finder
- macOS automatically runs `.command` files in Terminal

---

## Quick Start by Platform

### Windows Users

**Option A - Double-click** (Easiest):
1. Double-click `launch-project-ape.bat`
2. Dashboard opens in your browser automatically

**Option B - PowerShell**:
1. Right-click `launch-project-ape.ps1` → "Run with PowerShell"
2. Dashboard opens in your browser automatically

**Option C - Python** (Most reliable):
1. Open Command Prompt or PowerShell
2. Navigate to Project APE directory
3. Run: `python launch-project-ape.py`

### Linux Users

**Option A - Shell script**:
```bash
./launch-project-ape.sh
```

**Option B - Direct Python**:
```bash
python3 launch-project-ape.py
```

**Option C - Double-click** (if file manager supports):
1. Make script executable: `chmod +x launch-project-ape.sh`
2. Double-click in file manager
3. Select "Run" or "Execute" when prompted

### macOS Users

**Option A - Original launcher**:
1. Double-click `launch-project-ape.command` in Finder

**Option B - New cross-platform**:
```bash
./launch-project-ape.py
# or
./launch-project-ape.sh
```

---

## How It Works

All launchers perform the same core functions:

1. **Check if server is already running**
   - Sends HTTP request to `http://localhost:8765/configure`
   - If running, just opens browser

2. **Start the dashboard server** (if not running)
   - Locates virtual environment: `~/.project-ape-venv`
   - Platform-specific Python path:
     - Windows: `Scripts\python.exe`
     - Unix/Linux/macOS: `bin/python3`
   - Starts `dashboard/server.py` in background

3. **Wait for server to become ready**
   - Polls server health for up to 10 seconds
   - Checks every 0.5 seconds

4. **Open browser**
   - Platform-specific browser launch:
     - Windows: `webbrowser.open()` or `start`
     - macOS: `webbrowser.open()` or `open`
     - Linux: `webbrowser.open()` or `xdg-open`

---

## Troubleshooting

### "Virtual environment not found"

**Windows**:
```bash
# Install Git Bash, WSL, or Cygwin first, then:
bash ./setup-environment.sh
```

**Linux/macOS**:
```bash
./setup-environment.sh
```

### "Python is not installed"

**Windows**:
1. Download Python 3.10+ from https://www.python.org/downloads/
2. During installation, check **"Add Python to PATH"**
3. Restart terminal and try again

**Linux**:
```bash
# Debian/Ubuntu
sudo apt install python3 python3-pip

# RHEL/Fedora
sudo dnf install python3 python3-pip
```

**macOS**:
```bash
brew install python3
```

### "Server did not start within timeout period"

**Possible causes**:
1. **Port 8765 already in use**
   - Check: `netstat -an | grep 8765` (Unix) or `netstat -an | findstr 8765` (Windows)
   - Kill existing process or change port in `vars.py`

2. **Virtual environment corrupted**
   - Delete: `~/.project-ape-venv`
   - Re-run: `./setup-environment.sh`

3. **Missing dependencies**
   - Activate venv: `source ~/.project-ape-venv/bin/activate` (Unix) or `~\.project-ape-venv\Scripts\activate` (Windows)
   - Install: `pip install -r developer-docs/requirements.txt`

### "Permission denied" (Linux/macOS)

Make script executable:
```bash
chmod +x launch-project-ape.py
chmod +x launch-project-ape.sh
```

### PowerShell script blocked (Windows)

Allow scripts in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Advanced Usage

### Running on a different port

Edit `vars.py`:
```python
DASHBOARD_PORT = 9000  # Change from default 8765
```

Then update the port in launcher (if hardcoded) or launcher will read from vars.py.

### Running server manually

```bash
# Activate virtual environment
source ~/.project-ape-venv/bin/activate  # Unix
~\.project-ape-venv\Scripts\activate     # Windows

# Start server
python dashboard/server.py
```

### Checking server status

```bash
# Unix/Linux/macOS
curl -I http://localhost:8765/configure

# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8765/configure -Method Head

# Any platform with Python
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8765/configure').status)"
```

---

## File Permissions Summary

**Unix/Linux/macOS**:
```bash
chmod +x launch-project-ape.py     # Make Python launcher executable
chmod +x launch-project-ape.sh     # Make shell launcher executable
chmod +x launch-project-ape.command # Make macOS launcher executable
```

**Windows**:
- No chmod needed
- `.bat` and `.ps1` files are executable by default

---

## Migration from Original Launcher

If you were using `launch-project-ape.command` (macOS only), you can now:

1. **Continue using it** - Still works on macOS
2. **Switch to cross-platform** - Use `.py` or `.sh` for consistency
3. **Use both** - Keep both launchers, choose based on preference

The new launchers provide **identical functionality** with **broader compatibility**.

---

## Summary

| Launcher | Windows | Linux | macOS | Double-Click | Notes |
|----------|---------|-------|-------|--------------|-------|
| `launch-project-ape.py` | ✅ | ✅ | ✅ | ✅* | Universal, recommended |
| `launch-project-ape.bat` | ✅ | ❌ | ❌ | ✅ | Windows batch |
| `launch-project-ape.ps1` | ✅ | ❌ | ❌ | ✅ | Windows PowerShell |
| `launch-project-ape.sh` | ❌ | ✅ | ✅ | ✅* | Unix shell |
| `launch-project-ape.command` | ❌ | ❌ | ✅ | ✅ | Legacy macOS |

\* Requires executable permission (`chmod +x`) and proper file associations

---

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
2. Review [README.md](README.md) for setup instructions
3. Open issue on GitHub with launcher logs

**Launcher Version**: 1.0.0 (Cross-Platform)
**Last Updated**: June 25, 2026
