# macOS Complete Guide - Project APE

**Complete guide for installing, configuring, and running Project APE on macOS**

Version: 3.2.2  
Last Updated: June 25, 2026  
Platform: macOS (Intel & Apple Silicon)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [macOS-Specific Commands](#macos-specific-commands)
- [Launcher Options](#launcher-options)
- [Troubleshooting macOS Issues](#troubleshooting-macos-issues)
- [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

### System Requirements

- **macOS Version**: 10.15 (Catalina) or later
- **Processor**: Intel x86_64 or Apple Silicon (M1/M2/M3)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for installation + storage for client documents
- **Internet**: Required for Google APIs

### Required Software

1. **Python 3.10 or later** (Python 3.11+ recommended)
2. **Homebrew** (recommended but optional)
3. **Google Account** with access to:
   - Google Drive
   - Google NotebookLM
4. **Web Browser** (Safari, Chrome, Firefox, or Edge)

### Installing Prerequisites on macOS

#### Option 1: Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Verify installation
python3 --version  # Should show 3.11.x or higher
```

#### Option 2: Using Python.org Installer

1. Download from: https://www.python.org/downloads/macos/
2. Run the installer package
3. Follow the installation wizard
4. Verify in Terminal:
   ```bash
   python3 --version
   ```

---

## Installation

### Method 1: Web-Based Setup (Recommended)

**No terminal needed! Complete everything from your browser.**

1. **Download Project APE**
   ```bash
   git clone https://github.com/yourusername/project-ape.git
   cd project-ape
   ```

2. **Launch the Dashboard**
   - Double-click `launch-project-ape.command` in Finder
   - Browser opens automatically to `http://localhost:8765/configure`

3. **Click "Setup Environment"**
   - Automated setup runs (2-5 minutes)
   - Creates virtual environment
   - Installs all dependencies
   - No manual commands required

4. **Continue with web-based configuration** (see Quick Start below)

### Method 2: Command-Line Installation

**For advanced users who prefer terminal control.**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# 2. Run automated setup script
./setup-environment.sh

# Expected output:
# ✓ Creating Python virtual environment...
# ✓ Installing NotebookLM CLI...
# ✓ Installing dependencies...
# ✓ Setup complete!

# 3. Verify installation
source ~/.project-ape-venv/bin/activate
python3 -c "import core.client_pipeline; print('✓ Installation successful')"
```

**Time required**: 5-10 minutes depending on internet speed

---

## Quick Start

### Step 1: Launch Dashboard (30 seconds)

**Choose your preferred method:**

#### Option A: Double-Click Launcher (Easiest)

1. Open Finder
2. Navigate to `project-ape` folder
3. Double-click `launch-project-ape.command`
4. Grant permission if macOS asks (first time only)
5. Browser opens automatically

**First-time Security Note**: macOS Gatekeeper may show "unidentified developer" warning.

**Fix**:
```bash
# Make executable and remove quarantine
chmod +x launch-project-ape.command
xattr -d com.apple.quarantine launch-project-ape.command
```

Or right-click → Open → "Open Anyway"

#### Option B: Terminal Launch

```bash
cd /path/to/project-ape

# Method 1: Shell script
./launch-project-ape.sh

# Method 2: Python launcher (universal)
python3 launch-project-ape.py

# Method 3: Direct command
open http://localhost:8765 && python3 dashboard/server.py
```

### Step 2: Environment Setup (2-5 minutes)

1. Click **"Setup Environment"** button
2. Progress indicator shows:
   - Creating virtual environment
   - Installing NotebookLM CLI
   - Installing dependencies
3. Wait for ✅ **"Environment Ready"**

### Step 3: NotebookLM Authentication (1 minute)

1. Click **"Login to NotebookLM"**
2. Browser tab opens to Google sign-in
3. Sign in with your Google account
4. Click **"Allow"** for NotebookLM permissions
5. Return to dashboard
6. See ✅ **"Authenticated"**

### Step 4: Google Drive OAuth Setup (5 minutes, one-time)

**Complete 5-step wizard by clicking "Google Drive Setup":**

1. **Create Google Cloud Project**
2. **Enable Google Drive API**
3. **Configure OAuth Consent Screen**
4. **Create OAuth Client ID** → Download JSON
5. **Upload JSON** → Authenticate

See [QUICK_START.md](QUICK_START.md) for detailed wizard instructions.

### Step 5: Configure Clients (3 minutes)

Add your clients using the web form:

```
Client Name: Acme Corporation
Google Drive Folder: https://drive.google.com/drive/folders/YOUR_FOLDER_ID
Industry: (leave blank for auto-detect)
Subsegments: (optional)
```

Click **"➕ Add Client"** for each additional client.

### Step 6: Run Workflow (1 minute)

1. Select mode: **Fast** (15-20 min) or **Deep** (45-60 min)
2. Click **"🚀 Start Workflow"**
3. Monitor in real-time dashboard

**Total setup time**: 15-30 minutes (first time only)  
**Subsequent runs**: 15-60 minutes depending on mode

---

## macOS-Specific Commands

### Launcher Scripts

#### 1. launch-project-ape.command

**Purpose**: Double-click launcher for macOS Finder

**Usage**:
```bash
# Make executable (first time only)
chmod +x launch-project-ape.command

# Double-click in Finder, or run in terminal:
./launch-project-ape.command
```

**What it does**:
- Activates Python virtual environment
- Starts Flask dashboard server
- Opens browser to http://localhost:8765
- Keeps terminal window open for logs

**Location**: Root of project directory

#### 2. launch-project-ape.sh

**Purpose**: Shell script launcher (bash/zsh compatible)

**Usage**:
```bash
chmod +x launch-project-ape.sh
./launch-project-ape.sh
```

**What it does**:
- Same as .command file
- Works in any shell (bash, zsh, fish)
- Better for automation and scripts

#### 3. launch-project-ape.py

**Purpose**: Universal Python launcher (cross-platform)

**Usage**:
```bash
python3 launch-project-ape.py
```

**What it does**:
- Checks Python version
- Verifies virtual environment
- Starts dashboard
- Opens browser
- Platform-independent

### Setup Scripts

#### 1. setup-environment.sh

**Purpose**: Automated environment setup

**Usage**:
```bash
./setup-environment.sh
```

**What it does**:
- Creates `~/.project-ape-venv` virtual environment
- Installs Python dependencies from `developer-docs/requirements.txt`
- Installs NotebookLM CLI (`pip install notebooklm-cli`)
- Sets up logging directories
- Verifies installation

**Time**: 5-10 minutes

#### 2. setup-credentials.sh

**Purpose**: Guide for OAuth credential setup

**Usage**:
```bash
./setup-credentials.sh
```

**What it does**:
- Provides step-by-step OAuth instructions
- Checks for credential files
- Validates JSON format
- Creates ~/.project-ape directory

#### 3. setup-oauth-drive.py

**Purpose**: Interactive OAuth flow for Google Drive

**Usage**:
```bash
# Activate environment first
source ~/.project-ape-venv/bin/activate

# Run OAuth setup
python3 setup-oauth-drive.py
```

**What it does**:
- Reads OAuth credentials JSON
- Opens browser for authentication
- Saves token to `~/.project-ape/drive_token.json`
- Tests Drive API access

### Workflow Execution

#### 1. run-workflow.sh

**Purpose**: Run workflow from command line

**Usage**:
```bash
# Fast mode - all clients
./run-workflow.sh fast

# Deep mode - all clients
./run-workflow.sh deep

# Fast mode - specific clients
./run-workflow.sh fast acme_corp techstart_inc

# Force refresh Drive cache
./run-workflow.sh fast --refresh
```

**Options**:
- `fast`: 15-20 minute execution
- `deep`: 45-60 minute execution
- `--refresh`: Force re-download from Drive (ignore cache)
- Client names: Process only specified clients

#### 2. main.py

**Purpose**: Core orchestrator (Python entry point)

**Usage**:
```bash
# Activate environment
source ~/.project-ape-venv/bin/activate

# Run workflow
python3 main.py --mode fast
python3 main.py --mode deep --refresh
python3 main.py --mode fast --clients acme_corp
```

**Arguments**:
- `--mode {fast,deep}`: Execution mode
- `--refresh`: Force cache refresh
- `--clients CLIENT [CLIENT ...]`: Specific clients to process

### Dashboard Control

#### Start Dashboard

```bash
# Method 1: Via launcher
./launch-project-ape.sh

# Method 2: Direct Python
source ~/.project-ape-venv/bin/activate
python3 dashboard/server.py

# Method 3: Custom port
DASHBOARD_PORT=9000 python3 dashboard/server.py
```

#### Stop Dashboard

```bash
# Press Ctrl+C in terminal

# Or find and kill process
lsof -ti:8765 | xargs kill -9
```

### Testing Commands

```bash
# Test launcher scripts
./launch-project-ape.command  # Should open browser
./launch-project-ape.sh       # Should open browser
python3 launch-project-ape.py # Should open browser

# Test environment
source ~/.project-ape-venv/bin/activate
python3 -c "import core.client_pipeline; print('OK')"

# Test NotebookLM auth
notebooklm auth check

# Test main.py help
python3 main.py --help
```

---

## Launcher Options

### Comparison Matrix

| Launcher | Method | Best For | Pros | Cons |
|----------|--------|----------|------|------|
| `launch-project-ape.command` | Double-click | Non-technical users | Easy, no terminal | macOS only, Gatekeeper warnings |
| `launch-project-ape.sh` | Terminal | Automation | Fast, scriptable | Requires terminal |
| `launch-project-ape.py` | Python | Cross-platform | Universal, reliable | Requires Python in PATH |
| Direct Flask | Python module | Development | Full control | Most manual steps |

### When to Use Each

**Use .command file when**:
- You prefer GUI/Finder interaction
- First-time users or demos
- Don't want to touch terminal

**Use .sh script when**:
- Running from terminal already
- Automating with other scripts
- Comfortable with command line

**Use .py launcher when**:
- Testing on multiple platforms
- Python environment issues
- Maximum compatibility needed

**Use direct Flask when**:
- Developing or debugging
- Need custom configuration
- Want full control of process

---

## Troubleshooting macOS Issues

### Issue 1: "Unidentified Developer" Warning

**Symptom**: macOS won't open .command file

**Fix**:
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine launch-project-ape.command

# Or right-click → Open → "Open Anyway"
```

### Issue 2: Permission Denied

**Symptom**: `bash: ./launch-project-ape.command: Permission denied`

**Fix**:
```bash
# Make all scripts executable
chmod +x launch-project-ape.command
chmod +x launch-project-ape.sh
chmod +x setup-environment.sh
chmod +x run-workflow.sh
```

### Issue 3: Python Not Found

**Symptom**: `python3: command not found`

**Fix**:
```bash
# Install Python via Homebrew
brew install python@3.11

# Or verify installation
which python3
python3 --version
```

### Issue 4: Port Already in Use

**Symptom**: `Address already in use: 8765`

**Fix**:
```bash
# Find process using port 8765
lsof -ti:8765

# Kill the process
lsof -ti:8765 | xargs kill -9

# Or use different port
DASHBOARD_PORT=9000 python3 dashboard/server.py
```

### Issue 5: Virtual Environment Not Activating

**Symptom**: `source: command not found` or wrong Python version

**Fix**:
```bash
# Re-create virtual environment
rm -rf ~/.project-ape-venv
python3 -m venv ~/.project-ape-venv

# Activate and reinstall
source ~/.project-ape-venv/bin/activate
pip install -r developer-docs/requirements.txt
pip install notebooklm-cli
```

### Issue 6: Browser Doesn't Open Automatically

**Symptom**: Launcher runs but browser doesn't open

**Fix**:
```bash
# Manually open browser to:
open http://localhost:8765

# Or specify browser:
open -a "Google Chrome" http://localhost:8765
open -a Safari http://localhost:8765
```

### Issue 7: Slow Installation on Apple Silicon

**Symptom**: Dependency installation takes very long on M1/M2/M3

**Fix**:
```bash
# Use Rosetta-compatible Python (if needed)
arch -x86_64 /usr/local/bin/python3 -m venv ~/.project-ape-venv

# Or install ARM-native Python via Homebrew
brew install python@3.11
```

### Issue 8: Google Drive OAuth Fails

**Symptom**: OAuth flow doesn't complete

**Fix**:
```bash
# Clear existing tokens
rm -f ~/.project-ape/drive_token.json
rm -f ~/.project-ape/drive_credentials.json

# Re-run OAuth setup
python3 setup-oauth-drive.py

# Ensure default browser is set correctly
# System Preferences → General → Default web browser
```

---

## Advanced Configuration

### Custom Virtual Environment Location

```bash
# Edit launch scripts to use custom path
export PROJECT_APE_VENV="/path/to/custom/venv"
./launch-project-ape.sh
```

### Custom Dashboard Port

```bash
# Via environment variable
export DASHBOARD_PORT=9000
./launch-project-ape.sh

# Or edit vars.py
DASHBOARD_PORT = 9000
```

### Running Multiple Instances

```bash
# Instance 1 (default port)
./launch-project-ape.sh

# Instance 2 (custom port in new terminal)
DASHBOARD_PORT=9000 python3 dashboard/server.py
```

### Logging Configuration

```bash
# View real-time logs
tail -f logs/overall.log

# View specific client logs
tail -f logs/acme_corp.log

# Clear old logs
rm -rf logs/*.log
```

### Auto-Start on Login

```bash
# Create LaunchAgent plist
cat > ~/Library/LaunchAgents/com.project-ape.dashboard.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.project-ape.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/project-ape/launch-project-ape.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

# Load LaunchAgent
launchctl load ~/Library/LaunchAgents/com.project-ape.dashboard.plist
```

---

## macOS-Specific Features

### Finder Integration

- **Quick Look**: Works with generated PDFs
- **Spotlight**: Searches log files and documentation
- **Tags**: Tag client folders for organization

### Notification Center

```python
# Enable macOS notifications (add to dashboard/server.py)
import subprocess

def notify(title, message):
    subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])

# Call on workflow completion
notify("Project APE", "Research complete for Acme Corp!")
```

### Keyboard Shortcuts

- **⌘+W**: Close dashboard tab (browser)
- **⌘+R**: Refresh dashboard
- **⌘+Q**: Quit terminal (stops server)
- **⌘+.**: Cancel running process

---

## Verification Checklist

**After installation, verify everything works:**

```bash
# 1. Python version
python3 --version  # Should be 3.10+

# 2. Virtual environment
source ~/.project-ape-venv/bin/activate
which python3  # Should show ~/.project-ape-venv/bin/python3

# 3. Dependencies
pip list | grep -i flask  # Should show Flask
pip list | grep -i notebooklm  # Should show notebooklm-cli

# 4. Core modules
python3 -c "import core.client_pipeline; print('✓')"
python3 -c "import dashboard.server; print('✓')"

# 5. Launcher scripts
ls -l launch-project-ape.* | grep -E '^-rwx'  # All should be executable

# 6. Dashboard
curl -s http://localhost:8765 | grep -q "Project APE" && echo "✓ Dashboard running"

# 7. OAuth credentials (after setup)
ls -la ~/.project-ape/drive_*.json

# 8. NotebookLM auth
notebooklm auth check
```

**Expected**: All commands should complete without errors

---

## Getting Help

1. **Documentation**: Check [README.md](README.md) and [QUICK_START.md](QUICK_START.md)
2. **Logs**: Review `logs/overall.log` for errors
3. **Dashboard**: Check real-time logs in browser
4. **Issues**: Open GitHub issue with:
   - macOS version (`sw_vers`)
   - Python version (`python3 --version`)
   - Log files
   - Screenshot of error

---

**Version**: 3.2.2  
**Last Updated**: June 25, 2026  
**Platform**: macOS (Intel & Apple Silicon)  
**Author**: Jason Anderson

---

## Quick Reference Card

```bash
# Setup (one-time)
./setup-environment.sh

# Launch dashboard
./launch-project-ape.command  # Double-click or:
./launch-project-ape.sh       # Terminal

# Run workflow
./run-workflow.sh fast        # All clients, 15-20 min
./run-workflow.sh deep        # All clients, 45-60 min

# Troubleshoot
chmod +x *.sh *.command       # Fix permissions
xattr -d com.apple.quarantine launch-project-ape.command  # Fix Gatekeeper
lsof -ti:8765 | xargs kill    # Kill port 8765
tail -f logs/overall.log      # View logs

# Verify
python3 --version             # Check Python
source ~/.project-ape-venv/bin/activate  # Activate env
notebooklm auth check         # Check auth
```
