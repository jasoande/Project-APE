![Project APE Logo](king_kong_logo.webp)

# Project APE Installation Guide

**Project Owner & Maintainer:** Jason Anderson

---

## Installation Steps

### Prerequisites

**System Requirements:**
- Podman installed and running
- Python 3.11 or higher
- Git
- Google Chrome (for NotebookLM authentication)

### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
git checkout QA
```

### Step 2: Install NotebookLM SDK

```bash
pip install notebooklm-py
```

### Step 3: Authenticate with NotebookLM

```bash
notebooklm login
```

This will open Chrome for Google authentication. Sign in and grant NotebookLM API access.

### Step 4: Set Up Container Credentials

```bash
./setup-credentials.sh
```

This copies your NotebookLM credentials to the container's expected location.

### Step 5: Pull Container Image

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

Or build locally:
```bash
podman build -t project-ape:latest -f Containerfile .
```

### Step 6: Google Drive Setup (Optional - Recommended)

**For Google Drive folder integration:**

```bash
# Create service account in Google Cloud Console
# Download service account key JSON
# Set environment variable
echo "GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/path/to/key.json" >> .env

# Share your Drive folder with the service account email
# (found in the JSON key file, e.g., project-ape@yourproject.iam.gserviceaccount.com)
```

### Step 7: Configure Your First Client

```bash
# Copy example configuration
cp example-container.py vars.py

# Edit with your client details
nano vars.py
```

**Option A: Google Drive Folder (Recommended)**
```python
clients = ["yourclient"]

yourclient_name = "Your Client Name"
yourclient_industry = "Technology"
yourclient_subsegments = "Cloud, AI, Enterprise Software"
yourclient_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

DRIVE_CONFIG = {
    'enabled': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'auth_method': 'service_account',
    'export_google_docs': True,
    'max_file_size_mb': 50,
}
```

**Option B: Local Files**
```python
clients = ["yourclient"]

yourclient_name = "Your Client Name"
yourclient_industry = "Technology"
yourclient_subsegments = "Cloud, AI, Enterprise Software"
yourclient_folder = "/app/client_data/YourClient"
```

### Step 8: Add Client Documents (Local Files Only)

**Skip this step if using Google Drive folders**

```bash
mkdir -p client_data/YourClient
cp /path/to/documents/* client_data/YourClient/
```

Supported formats: PDF, DOCX, PPTX, XLSX, TXT, PNG, JPG  
Google Workspace files (Docs, Sheets, Slides) automatically exported when using Drive

### Step 9: Run Project APE

**Fast Mode** (10-12 minutes per client):
```bash
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

**Deep Mode** (30-35 minutes per client):
```bash
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep
```

### Step 9: View Dashboard

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
