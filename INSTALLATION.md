![Project APE Logo](king_kong_logo.webp)

# Project APE Installation Guide

**Project Owner & Maintainer:** Jason Anderson

---

## ⚠️ IMPORTANT: Which Setup Script to Use

**USE THIS SCRIPT:**
- ✅ **`setup.sh`** - Universal setup script (RHEL 8/9/10 and macOS)
  - Creates isolated virtual environment
  - Does NOT pollute system Python
  - Recommended for all installations

**DO NOT USE:**
- ❌ **`rhel-setup.sh`** - OLD RHEL-only script (deprecated)
  - Installs packages globally
  - Can break system Python
  - Kept for reference only

---

## Quick Start

### RHEL 8/9/10

```bash
# 1. Clone the repository
cd ~
mkdir -p account_planning
cd account_planning
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
git checkout QA

# 2. Run setup (requires sudo)
sudo ./setup.sh

# 3. Activate virtual environment
source activate-ape.sh

# 4. Authenticate (requires X11 forwarding)
./notebooklm-auth.sh
```

**SSH Connection for Authentication:**
```bash
# Connect with X11 forwarding enabled
ssh -X user@rhel-host

# Or with trusted X11 forwarding
ssh -Y user@rhel-host
```

### macOS

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Clone the repository
cd ~
mkdir -p account_planning
cd account_planning
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
git checkout QA

# 3. Run setup (NO sudo)
./setup.sh

# 4. Activate virtual environment
source activate-ape.sh

# 5. Authenticate
notebooklm login
```

---

## Detailed Installation Steps

### Prerequisites

**RHEL 8/9/10:**
- Active Red Hat subscription (for dnf package manager)
- sudo access
- SSH with X11 forwarding enabled (for authentication)

**macOS:**
- macOS 11 (Big Sur) or newer
- Homebrew installed
- No sudo required

### Step 1: System Preparation

The `setup.sh` script will install:

**RHEL Systems:**
- EPEL repository
- Python 3.11+ with development headers
- Podman container runtime
- Google Chrome
- LibreOffice (RHEL 8/9 only)
- Build tools and dependencies

**macOS Systems:**
- pyenv (Python version manager)
- Python 3.11 (via pyenv)
- Podman Desktop
- Google Chrome
- LibreOffice

### Step 2: Virtual Environment

The script creates an isolated Python environment at:
```
~/account_planning/Project-APE/venv/
```

**This ensures:**
- System Python remains untouched
- No package conflicts
- Easy to remove/reinstall
- Consistent environment across systems

### Step 3: Authentication

**RHEL (via SSH):**
```bash
# Must connect with X11 forwarding
ssh -X user@rhel-host
cd ~/account_planning/Project-APE
source activate-ape.sh
./notebooklm-auth.sh
```

**macOS (local):**
```bash
cd ~/account_planning/Project-APE
source activate-ape.sh
notebooklm login
```

The authentication process will:
1. Open Chrome browser
2. Prompt for Google login
3. Request NotebookLM API permissions
4. Save credentials to `~/.notebooklm/credentials.json`

### Step 4: Container Credentials

```bash
./setup-credentials.sh
```

This copies your NotebookLM credentials into the container's expected location.

### Step 5: Configure Your First Client

```bash
# Copy example configuration
cp example-container.py vars.py

# Edit with your client details
nano vars.py
```

**Minimum configuration:**
```python
CLIENTS = {
    "yourclient": {
        "name": "Your Client Name",
        "folder": "YourClient",
        # Optional: auto-detect will fill these in
        # "industry": "Technology",
        # "subsegments": "Cloud, AI, Enterprise Software"
    }
}
```

### Step 6: Add Client Documents

```bash
mkdir -p client_data/YourClient
cp /path/to/documents/* client_data/YourClient/
```

Supported formats: PDF, DOCX, PPTX, XLSX, TXT, PNG, JPG

### Step 7: Run Project APE

**Fast Mode** (10-12 minutes per client):
```bash
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

**Deep Mode** (30-35 minutes per client):
```bash
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep
```

### Step 8: View Dashboard

Open browser to: **http://localhost:8765**

---

## Virtual Environment Management

### Activating the Environment

Every time you work with Project APE:
```bash
cd ~/account_planning/Project-APE
source activate-ape.sh
```

Or manually:
```bash
source venv/bin/activate
```

### Deactivating the Environment

```bash
deactivate
```

### Checking Active Environment

```bash
which python
# Should show: ~/account_planning/Project-APE/venv/bin/python

python --version
# Should show: Python 3.11.x or 3.12.x
```

### Reinstalling the Environment

```bash
cd ~/account_planning/Project-APE
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install 'notebooklm-py[browser]'
pip install flask requests pypdf reportlab Pillow python-magic
python -m playwright install chromium
```

---

## Troubleshooting

### Authentication Issues

**Problem:** `Missing X server or $DISPLAY`

**Solution:**
1. Disconnect from SSH
2. Reconnect with X11 forwarding:
   ```bash
   ssh -X user@rhel-host
   ```
3. Verify DISPLAY is set:
   ```bash
   echo $DISPLAY
   # Should show: localhost:10.0 (or similar)
   ```
4. Run authentication:
   ```bash
   ./notebooklm-auth.sh
   ```

### Container Image Pull Fails

**Problem:** `unauthorized: access to the requested resource is not authorized`

**Solution:** Build the image locally:
```bash
cd ~/account_planning/Project-APE
podman build -t project-ape:latest -f Containerfile .
```

### Virtual Environment Not Found

**Problem:** `ERROR: Virtual environment not found`

**Solution:** Re-run setup:
```bash
sudo ./setup.sh  # RHEL
./setup.sh       # macOS
```

### Permission Errors

**Problem:** `Permission denied` or `cannot create directory`

**RHEL Solution:**
- Ensure you ran setup with `sudo`
- Check directory ownership:
  ```bash
  ls -la ~/account_planning/
  # Should be owned by your user, not root
  ```

**macOS Solution:**
- Ensure you did NOT run setup with `sudo`
- macOS setup should run as regular user

### Python Package Conflicts

**Problem:** Package version conflicts or import errors

**Solution:** Recreate virtual environment:
```bash
cd ~/account_planning/Project-APE
rm -rf venv/
source activate-ape.sh  # This will recreate it
```

---

## Uninstallation

### Complete Removal

```bash
# Remove Project APE directory
rm -rf ~/account_planning/Project-APE

# Remove NotebookLM credentials
rm -rf ~/.notebooklm

# RHEL: Remove system packages (optional)
sudo dnf remove podman buildah skopeo google-chrome-stable

# macOS: Remove via Homebrew (optional)
brew uninstall podman
brew uninstall --cask google-chrome
```

### Keep Credentials (Reinstall Later)

```bash
# Only remove project directory
rm -rf ~/account_planning/Project-APE

# Credentials remain in ~/.notebooklm
# Rerun setup.sh to reinstall
```

---

## Getting Help

- **Documentation:** See `README.md`, `QUICKSTART.md`, `TESTING-GUIDE.md`
- **Issues:** https://github.com/jasoande/Project-APE/issues
- **Project Owner:** Jason Anderson

---

## Version History

- **v3.0.4** - Universal setup script with virtual environment support
- **v3.0.3** - Auto-detect industry/subsegments feature
- **v3.0.2** - Deep mode optimization
- **v3.0.1** - Containerized deployment
- **v3.0.0** - Initial containerized release

---

**Project APE v3.0.4** - Revolutionizing Account Planning with AI
