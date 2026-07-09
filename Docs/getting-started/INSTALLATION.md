# Installation Guide

Complete installation instructions for Account Intelligence on all platforms.

---

## System Requirements

### Minimum Requirements
- **Python:** 3.11 or higher
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk:** 2 GB free space (500 MB app + 1.5 GB for caching)
- **Network:** Internet connection for API access
- **Browser:** Chrome/Firefox/Safari (for OAuth flows)

### Platform Support
- ✅ macOS 12+ (Intel and Apple Silicon)
- ✅ Linux (Ubuntu 20.04+, RHEL 8+, Fedora 35+)
- ✅ Windows 10/11 (via WSL2 or native Python)
- ✅ Docker/Podman containers (linux/amd64, linux/arm64)

---

## Prerequisites

### 1. Python 3.11+

**macOS (Homebrew):**
```bash
brew install python@3.11
python3 --version  # Should show 3.11 or higher
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

**Linux (RHEL/Fedora):**
```bash
sudo dnf install python3.11 python3.11-pip
python3.11 --version
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/) or use WSL2:
```powershell
wsl --install
wsl
# Now follow Linux instructions inside WSL
```

### 2. Google Chrome

Required for NotebookLM OAuth authentication.

**macOS:**
```bash
brew install --cask google-chrome
```

**Linux:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

**Windows:** Download from [google.com/chrome](https://www.google.com/chrome/)

### 3. Google Account with NotebookLM Access

1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Sign in with your Google account
3. Accept terms of service if prompted

### 4. Google Drive (Optional)

Only needed if you plan to use Drive folder URLs for document input. You can also use local PDF files.

---

## Installation Methods

### Method 1: GUI Launcher (Recommended)

**Easiest method** — Double-click to install and launch.

#### macOS/Linux

```bash
# Clone repository
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE

# Make launcher executable
chmod +x launch-project-ape.command  # macOS
chmod +x launch-project-ape.py        # Linux

# Double-click the file in Finder/File Manager
# OR run from terminal:
./launch-project-ape.command  # macOS
python3 launch-project-ape.py  # Linux
```

**What it does automatically:**
1. Creates virtual environment at `~/.project-ape-venv`
2. Installs all dependencies (Flask, notebooklm-py, pypdf, etc.)
3. Starts dashboard server
4. Opens browser to http://localhost:8765/configure

#### Windows

```powershell
# Clone repository
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE

# Double-click launch-project-ape.bat in File Explorer
# OR run from PowerShell:
.\launch-project-ape.bat
```

---

### Method 2: Manual Installation

For developers or users who prefer manual control.

#### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate  # Linux/macOS

# Windows (PowerShell):
# python -m venv %USERPROFILE%\.project-ape-venv
# %USERPROFILE%\.project-ape-venv\Scripts\Activate.ps1
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencies installed:**
- `flask` — Web framework
- `flask-wtf` — CSRF protection
- `waitress` — Production WSGI server
- `notebooklm-py` — NotebookLM SDK
- `pypdf` — PDF manipulation
- `google-api-python-client` — Google Drive API
- `google-auth-oauthlib` — OAuth2 authentication
- `pillow` — Image processing
- `python-pptx` — PowerPoint conversion
- `python-docx` — Word document conversion

#### Step 4: Verify Installation

```bash
python3 -c "import flask, notebooklm, pypdf; print('✅ Dependencies OK')"
```

#### Step 5: Start Dashboard

```bash
python3 dashboard/server.py
```

Open http://localhost:8765/configure in your browser.

---

### Method 3: Container Deployment

For production environments or users familiar with containers.

#### Prerequisites

- **Podman** (recommended) or **Docker**
- 4 GB RAM minimum
- SELinux enabled (RHEL/Fedora) or disabled (Ubuntu)

#### Install Podman

**macOS:**
```bash
brew install podman
podman machine init
podman machine start
```

**Linux (RHEL/Fedora):**
```bash
sudo dnf install podman
```

**Linux (Ubuntu):**
```bash
sudo apt install podman
```

#### Pull Image

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

#### Setup Credentials Volume

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
./setup-credentials.sh
```

This creates a Podman volume and copies your `~/.notebooklm/credentials.json` and `credentials/token_drive.json` into it.

#### Run Container

```bash
./ape-run.sh --vars ./vars.py --clients example_client --mode fast
```

**Container mounts:**
- `/app/vars.py` — Configuration (read-only)
- `/app/client_data/` — Input PDFs (read-only)
- `/app/docs_generated/` — Output files (writable)
- `/app/logs/` — Log files (writable)
- `/opt/app-root/src/.notebooklm` — Credentials volume

---

## Post-Installation Setup

### 1. NotebookLM Authentication

**Via Web UI (Recommended):**

1. Navigate to http://localhost:8765/configure
2. Click **"Authenticate NotebookLM"** button
3. Browser opens Chrome, sign in with Google account
4. Credentials saved to `~/.notebooklm/credentials.json`

**Via Terminal:**

```bash
source ~/.project-ape-venv/bin/activate
notebooklm login
```

**Verification:**
```bash
notebooklm list  # Should show your notebooks
```

### 2. Google Drive OAuth (Optional)

Only needed if using Drive folder URLs.

**Via Web UI (Recommended):**

1. Navigate to http://localhost:8765/configure
2. Click **"Setup Drive OAuth"** button
3. Upload your `credentials.json` from Google Cloud Console
4. Click **"Generate Token"** — browser opens for OAuth flow
5. Token saved to `credentials/token_drive.json`

**Via Terminal:**

```bash
python3 setup-oauth-drive.py
```

**Getting credentials.json:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `credentials.json`
6. Upload via web UI or place in `credentials/` directory

### 3. Verify Installation

```bash
# Start dashboard
python3 launch-project-ape.py

# In browser, check:
# - Dashboard loads at http://localhost:8765
# - NotebookLM auth shows ✅
# - Drive auth shows ✅ (if configured)
# - Can add a client and see validation
```

---

## Upgrading

### From Previous Version

```bash
cd Project-APE
git pull origin production
source ~/.project-ape-venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Container Upgrade

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
podman image prune -f  # Remove old images
```

---

## Uninstalling

### Remove Application

```bash
rm -rf ~/Project-APE
rm -rf ~/.project-ape-venv
```

### Remove Credentials (Optional)

```bash
rm -rf ~/.notebooklm
rm -rf ~/Project-APE/credentials
```

### Remove Container Images

```bash
podman rmi quay.io/jasoande/project_ape/project-ape:latest
podman volume rm project-ape-credentials
```

---

## Troubleshooting Installation

### "python3: command not found"

**Solution:** Python not installed or not in PATH. Install Python 3.11+ following Prerequisites section.

### "pip: command not found"

**Solution:**
```bash
# Linux
sudo apt install python3-pip

# macOS
python3 -m ensurepip --upgrade
```

### "Permission denied" when running launcher

**Solution:**
```bash
chmod +x launch-project-ape.command
chmod +x launch-project-ape.py
```

### "Port 8765 already in use"

**Solution:** Kill existing process:
```bash
lsof -ti :8765 | xargs kill -9
```

### "ModuleNotFoundError: No module named 'flask'"

**Solution:** Activate virtual environment:
```bash
source ~/.project-ape-venv/bin/activate
pip install -r requirements.txt
```

### "Could not find Google Chrome"

**Solution:** NotebookLM OAuth requires Chrome. Install Chrome or set `BROWSER` environment variable:
```bash
export BROWSER=/usr/bin/chromium  # Or your browser path
notebooklm login
```

---

## Next Steps

- ✅ Installation complete? → [Quick Start Tutorial](QUICKSTART.md)
- ✅ Want to run your first workflow? → [First Workflow Guide](FIRST_WORKFLOW.md)
- ✅ Need to configure Drive integration? → [Google Drive Integration](../user-guide/DRIVE_INTEGRATION.md)
- ✅ Deploying in production? → [Deployment Guide](../admin-guide/DEPLOYMENT.md)

---

**Need help?** See [Troubleshooting Guide](../admin-guide/TROUBLESHOOTING.md) or [open an issue](https://github.com/jasoande/Project-APE/issues).
