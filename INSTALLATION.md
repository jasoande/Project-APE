![Project APE Logo](king_kong_logo.webp)

# Project APE Installation Guide

**Project Owner & Maintainer:** Jason Anderson

---

## Installation Steps

### Prerequisites

**System Requirements:**
- Git
- Google Chrome (for NotebookLM authentication)
- Internet connection

All other dependencies will be installed by the setup script.

### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
git checkout QA
```

### Step 2: Run Automated Environment Setup

```bash
./setup-environment.sh
```

This interactive script will:
1. **Install Podman** (container runtime)
2. **Install Node.js 20+** (required for NotebookLM CLI)
3. **Install NotebookLM CLI** (npm package)
4. **Install Python dependencies** (optional, for local execution)
5. **Authenticate with NotebookLM** (opens browser for Google login)

The script detects your operating system (macOS, RHEL/Fedora, Debian/Ubuntu) and uses the appropriate package manager.

**Note:** You may be prompted for your password (sudo) during installation.

### Step 3: Set Up Container Credentials

```bash
./setup-credentials.sh
```

This copies your NotebookLM credentials to the container's expected location.

### Step 4: Pull Container Image

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

Or build locally:
```bash
podman build -t project-ape:latest -f Containerfile .
```

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

## Troubleshooting

### Authentication Issues

**Problem:** `notebooklm login` fails or requires display

**Solution:** Authenticate on a machine with a browser, then copy credentials:
```bash
# On machine with browser (local workstation):
notebooklm login

# Copy credentials to remote server:
scp ~/.notebooklm/credentials.json user@remote-host:~/.notebooklm/
```

### Container Image Pull Fails

**Problem:** `unauthorized: access to the requested resource is not authorized`

**Solution:** Build the image locally:
```bash
cd ~/account_planning/Project-APE
podman build -t project-ape:latest -f Containerfile .
```

### Python Package Issues

**Problem:** `notebooklm` command not found

**Solution:** Ensure notebooklm-py is installed:
```bash
pip install notebooklm-py
# Or reinstall:
pip install --upgrade --force-reinstall notebooklm-py
```

### Podman Issues

**Problem:** Podman not running or containers fail to start

**Solution:**
```bash
# Check Podman status
podman info

# Restart Podman (macOS)
podman machine stop
podman machine start

# RHEL/Linux - check service
systemctl --user status podman.socket
systemctl --user start podman.socket
```

---

## Uninstallation

### Complete Removal

```bash
# Remove Project APE directory
rm -rf Project-APE

# Remove NotebookLM credentials (optional)
rm -rf ~/.notebooklm

# Remove NotebookLM SDK (optional)
pip uninstall notebooklm-py
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
