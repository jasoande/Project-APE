# Getting Started with Project APE

**Complete setup guide for first-time users**

---

## Overview

Project APE automates enterprise account planning research. This guide walks you through setup to your first successful run.

**Time to complete:** 30-45 minutes

---

## Prerequisites

Before starting, you need:

1. ✅ Google account with NotebookLM access
2. ✅ Podman or Docker installed  
3. ✅ Internet connection
4. ✅ macOS (M1/M2/M3) OR Linux x86_64

---

## Step 1: Install Container Runtime

### macOS
```bash
# Install Podman Desktop
brew install podman-desktop
# OR install Docker Desktop from docker.com
```

### Linux (RHEL/Fedora)
```bash
sudo dnf install podman
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install podman
```

**Verify installation:**
```bash
podman --version
# Should show: podman version 4.x or higher
```

---

## Step 2: Get Google Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with "AIza...")
4. Save for Step 5

---

## Step 3: Setup Google Service Account

**This is required for Google Drive access.**

See complete guide: **[SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)**

Quick steps:
1. Go to https://console.cloud.google.com
2. Create new project "Project APE"
3. Enable Google Drive API
4. Create Service Account
5. Download JSON key file
6. Save as `jasoande-3aec1043e544.json` in Project APE directory

**Copy the service account email** (format: `name@project.iam.gserviceaccount.com`)

---

## Step 4: Setup Google Drive Folders

### Create Client Folders

```
My Drive/
└── Client Research/
    ├── Merck/
    │   ├── company_overview.pdf
    │   ├── 10k_report.pdf
    │   └── tech_stack.pdf
    │
    └── Blue Yonder/
        ├── company_profile.pdf
        └── solutions.pdf
```

### Share with Service Account

For each client folder:
1. Right-click folder → **Share**
2. Paste service account email
3. Grant **Viewer** access
4. Click **Send**

### Get Folder URLs

1. Open folder in Google Drive
2. Copy URL from browser address bar
3. Should look like: `https://drive.google.com/drive/folders/1zi3Jbvv9eW...`

---

## Step 5: Clone and Configure Project APE

### Clone Repository

```bash
cd ~/Projects  # or your preferred location
git clone <repository-url>
cd Project-APE
```

### Configure Environment (.env)

```bash
# Copy template
cp .env.template .env

# Edit with your API keys
nano .env  # or use your favorite editor
```

Add your keys:
```bash
# Gemini API (required)
GEMINI_API_KEY=AIzaSy...your-key-here

# Google Drive Service Account path
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json

# Optional: Claude via Vertex AI
CLAUDE_CODE_USE_VERTEX=1
ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project
ANTHROPIC_VERTEX_REGION=us-east5
```

Save and close.

### Configure Clients (vars.py)

```bash
# Copy example
cp example-vars.py vars.py

# Edit configuration
nano vars.py
```

Add your clients:
```python
clients = [
    "merck_test",
    "blue_yonder_test"
]

# Merck Configuration
merck_test_name = "Merck"
merck_test_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
merck_test_industry = "pharmaceuticals and life sciences"
merck_test_subsegments = "drug discovery, clinical trials, manufacturing"

# Blue Yonder Configuration  
blue_yonder_test_name = "Blue Yonder"
blue_yonder_test_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
blue_yonder_test_industry = "supply chain software"
blue_yonder_test_subsegments = "demand planning, warehouse management, logistics"
```

Save and close.

### Place Service Account File

```bash
# Copy your service account JSON to project directory
cp ~/Downloads/service-account-key.json ./jasoande-3aec1043e544.json

# Verify it's there
ls -la jasoande-*.json
```

---

## Step 6: Authenticate NotebookLM

**This step requires NotebookLM CLI - only available after first container run.**

We'll do this in Step 7 on first run.

---

## Step 7: Run Your First Pipeline

### Run Fast Mode (Single Client)

```bash
./launch_ape.sh fast merck_test
```

**What happens:**
1. Script detects your architecture (ARM64 or x86_64)
2. Pulls correct container image from Quay.io
3. Starts dashboard at http://localhost:8765
4. Downloads files from Google Drive
5. Consolidates to PDF
6. Runs NotebookLM pipeline

**Expected output:**
```
════════════════════════════════════════════════════════════════
  Project APE - Account Planning Engine
  Automatic Architecture Detection & Container Launcher
════════════════════════════════════════════════════════════════

[INFO] Detected architecture: arm64
[INFO] Detected runtime: podman

[STEP] Pulling image from Quay.io...
[INFO] Image: quay.io/jasoande/project_ape/project-ape:3.0.5-arm64
[INFO] ✅ Image pulled successfully

[STEP] Starting Project APE...
[INFO] Mode: fast
[INFO] Clients: merck_test
[INFO] Dashboard: http://localhost:8765
```

### First-Time NotebookLM Auth

On first run, you'll be prompted:
```
ERROR: NotebookLM authentication required

Please authenticate by running:
  notebooklm login
```

**To authenticate:**

1. **Open new terminal** (keep pipeline running)

2. **Enter container:**
   ```bash
   podman exec -it project-ape bash
   ```

3. **Login to NotebookLM:**
   ```bash
   notebooklm login
   ```

4. **Follow prompts:**
   - Browser will open
   - Login to Google account
   - Grant permissions
   - Return to terminal

5. **Exit container:**
   ```bash
   exit
   ```

6. **Restart pipeline:**
   ```bash
   ./launch_ape.sh fast merck_test
   ```

### Monitor Progress

Open dashboard in browser:
```bash
open http://localhost:8765
```

**Dashboard shows:**
- Real-time progress for each client
- Current pipeline step
- Elapsed time
- Quality scores
- Direct links to NotebookLM notebooks

### Expected Timeline (Fast Mode)
- Download from Drive: 1-2 min
- PDF consolidation: 1-2 min  
- Research generation: 10-12 min
- Note creation: 2-4 min
- Mind map: 1-2 min

**Total: 15-20 minutes**

---

## Step 8: View Results

### Check Dashboard

Dashboard shows:
- ✅ **Status:** COMPLETED
- 📊 **Quality Score:** 8.7/10 (or similar)
- 🔗 **NotebookLM Link:** Click to open notebook

### Open NotebookLM Notebook

Click the notebook link in dashboard, or:
1. Go to https://notebooklm.google.com
2. Find notebook named `DEV_merck_test-TEST`
3. Review:
   - 40+ sources
   - 6 analysis notes
   - Interactive mind map

### Check Logs

```bash
tail -f logs/merck_test.log
```

---

## Step 9: Run Multiple Clients

### All Clients (Fast Mode)

```bash
./launch_ape.sh fast
```

Runs all clients defined in `vars.py` in parallel.

### All Clients (Deep Mode)

```bash
./launch_ape.sh deep
```

Takes 35-40 minutes but produces higher quality research.

### Specific Clients

```bash
./launch_ape.sh fast merck_test blue_yonder_test organon_test
```

---

## Common Issues

### Issue: Container image not found

**Solution:**
```bash
# Login to Quay.io
podman login quay.io

# Pull manually
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

### Issue: Permission denied on service account

**Solution:**
1. Verify file exists: `ls -la jasoande-*.json`
2. Check permissions: `chmod 644 jasoande-*.json`
3. Verify in .env: `GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json`

### Issue: Can't download from Google Drive

**Solution:**
1. Verify folder is shared with service account email
2. Check folder URL in vars.py is correct
3. Test service account has access:
   ```bash
   # In container
   python3 -c "from core.drive_manager import DriveManager; print('OK')"
   ```

### Issue: Dashboard not accessible

**Solution:**
```bash
# Check if port 8765 is already in use
lsof -i :8765

# Kill existing process if needed
kill <PID>

# Restart pipeline
./launch_ape.sh fast
```

---

## Next Steps

1. ✅ **Read** [QUICKSTART.md](QUICKSTART.md) for quick reference
2. ✅ **Review** [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md) for Drive details
3. ✅ **Check** [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) for common issues
4. ✅ **Optimize** Run deep mode for higher quality research

---

## Summary

**You've successfully:**
- ✅ Installed container runtime
- ✅ Created Google service account
- ✅ Setup Google Drive folders
- ✅ Configured Project APE
- ✅ Run your first pipeline
- ✅ Generated NotebookLM research

**Project APE is now ready for production use!**

---

**Need Help?** Contact Jason Anderson

**All data flows through Google Drive - no local files needed!**
