<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="150"/>
  
  # Installation Guide
  **Account Intelligence - Account Planning Engine**
</div>

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [macOS Installation](#macos-installation)
4. [Linux Installation](#linux-installation)
5. [Windows Installation](#windows-installation)
6. [Container Installation](#container-installation)
7. [Authentication Setup](#authentication-setup)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: macOS 10.15+, Linux (Ubuntu 20.04+, RHEL 8+, Fedora 35+), Windows 10/11
- **Python**: 3.10 or higher (3.11+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 2GB for application and dependencies
- **Internet**: Required for API access and package installation

### Required Accounts

1. **Google Account** with access to:
   - Google Drive (for storing client documents)
   - Google NotebookLM (free at https://notebooklm.google.com)

2. **Google Cloud Project** (free tier sufficient):
   - Drive API enabled
   - OAuth 2.0 credentials configured

### Optional

- **Gemini API Key**: For advanced AI features (industry auto-detection, error recovery)
- **Podman or Docker**: For containerized deployment

---

## Installation Methods

Account Intelligence supports three installation methods:

| Method | Best For | Complexity |
|--------|----------|-----------|
| **Native (Python)** | Development, macOS/Linux | Medium |
| **Container** | Production, multi-platform | Low |
| **Windows Native** | Windows development | Medium |

Choose the method that best fits your environment.

---

## macOS Installation

### Step 1: Install Homebrew (if not installed)

```bash
# Install Homebrew package manager
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python 3.11

```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
python3 --version  # Should show 3.11.x or higher
```

### Step 3: Install Chrome Browser

NotebookLM authentication requires Chrome:

```bash
# Install Chrome via Homebrew
brew install --cask google-chrome

# Or download from: https://www.google.com/chrome/
```

### Step 4: Install Podman (Optional, for Containers)

```bash
# Install Podman
brew install podman

# Initialize Podman machine
podman machine init
podman machine start

# Verify installation
podman --version
```

### Step 5: Clone Repository

```bash
# Clone Account Intelligence repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape
```

### Step 6: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv ~/.project-ape-venv

# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Your prompt should now show: (project-ape-venv)
```

### Step 7: Install Python Dependencies

```bash
# Install NotebookLM CLI
pip install notebooklm

# Install other dependencies
pip install -r developer-docs/requirements.txt
```

**Expected time**: 2-3 minutes

### Step 8: Verify Installation

```bash
# Verify NotebookLM CLI
notebooklm --version

# Verify Python packages
pip list | grep -E "(flask|google|PyPDF2)"
```

---

## Linux Installation

### Ubuntu/Debian

#### Step 1: Update System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

#### Step 2: Install Python 3.11

```bash
# Add deadsnakes PPA (for Python 3.11)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# Install Python 3.11 and dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
```

#### Step 3: Install Chrome Browser

```bash
# Download Chrome package
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install Chrome
sudo apt install ./google-chrome-stable_current_amd64.deb

# Verify installation
google-chrome --version
```

#### Step 4: Install Podman (Optional)

```bash
# Install Podman
sudo apt-get install -y podman

# Verify installation
podman --version
```

#### Step 5: Clone Repository and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Create virtual environment
python3.11 -m venv ~/.project-ape-venv

# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Install dependencies
pip install notebooklm
pip install -r developer-docs/requirements.txt
```

### RHEL/Fedora

#### Step 1: Install Python 3.11

```bash
# Fedora
sudo dnf install -y python3.11 python3-pip

# RHEL 8/9 (enable EPEL first)
sudo dnf install -y epel-release
sudo dnf install -y python3.11 python3-pip
```

#### Step 2: Install Chrome

```bash
# Add Chrome repository
sudo dnf install -y fedora-workstation-repositories
sudo dnf config-manager --set-enabled google-chrome

# Install Chrome
sudo dnf install -y google-chrome-stable
```

#### Step 3: Install Podman

```bash
# Podman is pre-installed on RHEL/Fedora
# Verify or install
sudo dnf install -y podman

# Start Podman
sudo systemctl enable --now podman
```

#### Step 4: Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Create virtual environment
python3.11 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate

# Install dependencies
pip install notebooklm
pip install -r developer-docs/requirements.txt
```

---

## Windows Installation

### Step 1: Install Python 3.11

1. Download Python 3.11 from https://www.python.org/downloads/
2. Run installer with these options:
   - ✅ **Add Python 3.11 to PATH**
   - ✅ Install pip
   - ✅ Install for all users (optional)
3. Verify installation:

```powershell
python --version  # Should show 3.11.x
```

### Step 2: Install Chrome Browser

Download and install from: https://www.google.com/chrome/

### Step 3: Install Git for Windows

Download from: https://git-scm.com/download/win

### Step 4: Clone Repository

```powershell
# Open PowerShell or Command Prompt
git clone https://github.com/yourusername/project-ape.git
cd project-ape
```

### Step 5: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv %USERPROFILE%\.project-ape-venv

# Activate virtual environment
%USERPROFILE%\.project-ape-venv\Scripts\activate

# Your prompt should change to: (project-ape-venv)
```

### Step 6: Install Dependencies

```powershell
# Install NotebookLM CLI
pip install notebooklm

# Install other dependencies
pip install -r developer-docs\requirements.txt
```

### Step 7: Install Podman Desktop (Optional)

For container support:

1. Download Podman Desktop from: https://podman-desktop.io/
2. Install and launch Podman Desktop
3. Follow setup wizard to initialize Podman machine

---

## Container Installation

Container installation provides the easiest deployment path across all platforms.

### Step 1: Install Container Runtime

**macOS:**

```bash
brew install podman
podman machine init
podman machine start
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get install -y podman

# RHEL/Fedora (pre-installed)
sudo dnf install -y podman
```

**Windows:**

Download and install Podman Desktop from: https://podman-desktop.io/

### Step 2: Pull Account Intelligence Image

```bash
# Pull latest stable release
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1

# Or pull latest
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Verify image
podman images | grep project-ape
```

### Step 3: Setup Credentials Volume

```bash
# Clone repository (for setup scripts)
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Run credentials setup
./setup-credentials.sh
```

This creates a persistent volume for NotebookLM credentials.

### Step 4: Verify Container

```bash
# Test run
podman run --rm quay.io/jasoande/project_ape/project-ape:4.0.1 --version
```

---

## Authentication Setup

### NotebookLM Authentication

#### Step 1: Install NotebookLM CLI

```bash
# Already installed in previous steps, but verify:
pip install --upgrade notebooklm
```

#### Step 2: Login to NotebookLM

```bash
# Start login flow (opens Chrome browser)
notebooklm login

# Follow prompts:
# 1. Sign in with Google account
# 2. Grant NotebookLM permissions
# 3. Return to terminal - should show "Login successful"
```

#### Step 3: Verify Authentication

```bash
# Check credentials
ls -la ~/.notebooklm/credentials.json

# Test API access
notebooklm list
```

**Expected output**: List of your NotebookLM notebooks (may be empty)

### Google Drive OAuth Setup

#### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `Project-APE` (or your choice)
4. Click **"Create"**
5. Wait for project creation (15-30 seconds)

#### Step 2: Enable Drive API

1. Navigate to: https://console.cloud.google.com/apis/library
2. Search for: **"Google Drive API"**
3. Click **"Google Drive API"**
4. Click **"Enable"**
5. Wait for activation (10-15 seconds)

#### Step 3: Configure OAuth Consent Screen

1. Navigate to: https://console.cloud.google.com/apis/credentials/consent
2. Select **"External"** user type
3. Click **"Create"**
4. Fill in required fields:
   - **App name**: Account Intelligence
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click **"Save and Continue"**
6. **Scopes**: Click **"Add or Remove Scopes"**
   - Search for: `drive.readonly`
   - Select: `https://www.googleapis.com/auth/drive.readonly`
   - Click **"Update"**
7. Click **"Save and Continue"**
8. **Test users**: Add your Google email
9. Click **"Save and Continue"**

#### Step 4: Create OAuth Credentials

1. Navigate to: https://console.cloud.google.com/apis/credentials
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Desktop app"**
4. Name: `Project-APE-Desktop`
5. Click **"Create"**
6. Click **"Download JSON"** (downloads `client_secret_*.json`)
7. Click **"OK"**

#### Step 5: Configure Account Intelligence

**Option A: Automated Setup (Recommended)**

```bash
# Run automated OAuth setup
python3 setup-oauth-drive-improved.py

# Script will:
# - Find downloaded client_secret_*.json
# - Move to ~/.project-ape/drive_credentials.json
# - Set secure permissions (chmod 600)
# - Launch OAuth flow
# - Save token to ~/.project-ape/drive_token.json
```

**Option B: Manual Setup**

```bash
# Create credentials directory
mkdir -p ~/.project-ape

# Move downloaded credentials
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json

# Set permissions
chmod 600 ~/.project-ape/drive_credentials.json

# Run OAuth authentication
python3 setup-oauth-drive-improved.py
```

#### Step 6: Complete OAuth Flow

1. Script opens browser automatically
2. Sign in with Google account
3. Click **"Advanced"** → **"Go to Account Intelligence (unsafe)"**
   - This warning appears because app is in testing mode (normal)
4. Click **"Allow"** to grant permissions
5. Browser shows: **"The authentication flow has completed"**
6. Return to terminal - should show: **"Authentication successful!"**

#### Step 7: Verify Drive Access

```bash
# Verify credentials exist
ls -la ~/.project-ape/drive_credentials.json
ls -la ~/.project-ape/drive_token.json

# Test Drive API access (requires Python)
python3 -c "from core.drive_manager import DriveManager; dm = DriveManager(); print('Drive access: OK')"
```

**Expected output**: `Drive access: OK`

---

## Verification

### Full System Verification

Run these commands to verify complete installation:

```bash
# 1. Python version
python3 --version  # Should be 3.10+

# 2. Virtual environment active
which python  # Should show path to .project-ape-venv

# 3. NotebookLM authentication
notebooklm list  # Should list notebooks (or empty list)

# 4. Drive authentication
ls -la ~/.project-ape/*.json  # Should show drive_credentials.json and drive_token.json

# 5. Python dependencies
pip list | grep -E "(flask|google|PyPDF2|notebooklm)"

# 6. Container runtime (if using containers)
podman --version  # Should show version number
```

### Test Run

Execute a minimal test to verify end-to-end functionality:

```bash
# 1. Copy example configuration
cp developer-docs/example-vars.py vars.py

# 2. Edit vars.py with a test client
# (Use a small Drive folder for testing)

# 3. Run test workflow
./developer-docs/ape-run.sh --vars ./vars.py --clients test_client --mode fast

# 4. Monitor in dashboard
# Open: http://localhost:8765

# 5. Check outputs
ls -la docs_generated/test_client/
```

**Expected time**: 15-20 minutes

---

## Troubleshooting

### Python Installation Issues

**Issue**: `python3: command not found`

**Solution**:

```bash
# macOS
brew install python@3.11
export PATH="/usr/local/opt/python@3.11/bin:$PATH"

# Linux
sudo apt-get install python3.11
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Windows
# Reinstall Python and check "Add to PATH"
```

---

### NotebookLM Authentication Issues

**Issue**: `notebooklm login` fails or Chrome doesn't open

**Solution**:

```bash
# 1. Verify Chrome is installed
google-chrome --version  # Linux
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # macOS

# 2. Set Chrome path manually
export CHROME_BROWSER="/path/to/chrome"
notebooklm login

# 3. Use manual authentication
notebooklm login --manual
# Follow console URL in any browser
```

---

### Google Drive OAuth Issues

**Issue**: "Credentials not found" error

**Solution**:

```bash
# Verify credentials file exists
ls -la ~/.project-ape/drive_credentials.json

# If missing, re-download from Google Cloud Console
# Or re-run setup script
python3 setup-oauth-drive-improved.py
```

**Issue**: "Token has expired" error

**Solution**:

```bash
# Delete expired token
rm ~/.project-ape/drive_token.json

# Re-authenticate
python3 setup-oauth-drive-improved.py
```

**Issue**: OAuth redirect URI mismatch

**Solution**:

1. Verify OAuth client type is **"Desktop app"** (not "Web application")
2. Re-create credentials with correct type
3. Download new `client_secret_*.json`
4. Re-run `setup-oauth-drive-improved.py`

---

### Container Issues

**Issue**: `podman: command not found`

**Solution**:

```bash
# macOS
brew install podman
podman machine init
podman machine start

# Linux
sudo apt-get install podman  # Ubuntu/Debian
sudo dnf install podman      # RHEL/Fedora
```

**Issue**: Container fails to start with permission errors

**Solution**:

```bash
# Recreate credentials volume
podman volume rm project-ape-credentials
./setup-credentials.sh

# Verify volume exists
podman volume ls | grep project-ape-credentials
```

---

### Dependency Installation Issues

**Issue**: `pip install` fails with SSL errors

**Solution**:

```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Try installation again
pip install -r developer-docs/requirements.txt
```

**Issue**: `requirements.txt` not found

**Solution**:

```bash
# Verify you're in project root directory
pwd  # Should end with /project-ape

# Check file exists
ls developer-docs/requirements.txt

# If missing, clone repository again
```

---

### Platform-Specific Issues

#### macOS: SSL Certificate Error

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or update certifi
pip install --upgrade certifi
```

#### Linux: Chrome Sandbox Issues

```bash
# Run Chrome with --no-sandbox (if needed)
export CHROME_FLAGS="--no-sandbox"
notebooklm login
```

#### Windows: Path Too Long Errors

```powershell
# Enable long paths in Windows
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1

# Or use shorter directory paths
```

---

## Next Steps

After successful installation:

1. **Read the User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
2. **Configure your clients**: Edit `vars.py` with real client data
3. **Run your first workflow**: Follow Quick Start in README.md
4. **Monitor in dashboard**: http://localhost:8765

---

## Getting Help

If you encounter issues not covered here:

1. **Check Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Search GitHub Issues**: https://github.com/yourusername/project-ape/issues
3. **Open New Issue**: Include:
   - Operating system and version
   - Python version (`python3 --version`)
   - Error messages (full output)
   - Steps to reproduce

---

**Installation complete! You're ready to start using Account Intelligence.**

Return to: [README.md](../README.md) | Continue to: [User Guide](USER_GUIDE.md)
