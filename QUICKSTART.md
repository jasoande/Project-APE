# Project APE - Quick Start Guide

**Get running in 30 minutes** (complete first-time setup)

---

## Prerequisites

Before you begin, you need:

✅ **Mac (M1/M2/M3/M4) or Linux (x86_64)**  
✅ **Google account** with NotebookLM access  
✅ **Google Drive folders** with client documents  
✅ **30 minutes** for one-time setup

**This guide assumes you're starting from scratch.**

---

## 30-Minute Setup

### 1. Create Google Service Account (~15 min, one-time)

**Why:** Allows Project APE to download files from your Google Drive folders automatically.

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable Google Drive API
4. Create service account
5. Download JSON key file
6. Save key file to `~/Downloads/`

**Detailed guide:** [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)

**Save the service account email** (e.g., `project-ape-service@your-project.iam.gserviceaccount.com`)

---

### 2. Clone Repository (~1 min)

```bash
cd ~
git clone <repository-url>
cd Project-APE
```

---

### 3. Install Requirements (~5 min, automated)

```bash
./setup-environment.sh
```

**What it installs:**
- Podman (container runtime)
- Python 3 (for NotebookLM CLI)
- NotebookLM CLI (notebooklm-py with browser support)
- Playwright browser (Chromium)

**Note:** Python for the pipeline runs in container - only needed for notebooklm CLI.

---

### 4. Configure vars.py (~5 min)

```bash
# Copy example
cp example-vars.py vars.py

# Edit with your clients
nano vars.py
```

**Add your clients:**
```python
clients = [
    "client1",
]

client1_name = "Your Client Name"
client1_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
client1_industry = "your industry"
client1_subsegments = "segment1, segment2, segment3"
```

**How to get folder ID:**
1. Open Google Drive folder in browser
2. Copy URL from address bar
3. Extract the ID after `/folders/`

---

### 5. Authenticate NotebookLM (~2 min, one-time)

```bash
notebooklm login
```

**What happens:**
- Opens browser for Google authentication
- You sign in and grant permissions
- Credentials saved to `~/.notebooklm/`

**Linux/SSH users:** If connecting via SSH, use `ssh -X -Y user@host` for X11 forwarding, or run `xvfb-run notebooklm login` for headless mode.

---

### 6. Setup Credentials (~1 min)

```bash
./setup-credentials.sh
```

**What it does:**
- Copies NotebookLM credentials to container
- Creates persistent volume
- You only do this once

---

### 7. Share Drive Folders (~2 min per folder)

For each folder in `vars.py`:

1. **Open Google Drive** in browser
2. **Right-click folder** → **Share**
3. **Paste service account email** (from Step 1)
4. **Set permission to "Viewer"**
5. **Uncheck "Notify people"**
6. **Click Share**

---

### 8. Launch Pipeline! (~15-40 min automated)

**Fast mode (15-20 min):**
```bash
./launch_ape.sh fast
```

**Deep mode (35-40 min):**
```bash
./launch_ape.sh deep
```

**What happens automatically:**
- Downloads container image
- Starts dashboard at http://localhost:8765
- Downloads files from Google Drive
- Consolidates PDFs
- Generates 40+ research sources
- Creates 6 analysis notes
- Builds mind maps
- Calculates quality scores

---

### 9. Monitor Progress

**Open dashboard:**
```bash
open http://localhost:8765
```

**Dashboard shows:**
- Real-time client status
- Execution timers
- Progress through pipeline stages
- Quality scores

---

### 10. View Results

**Open NotebookLM:**
1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Sign in with your Google account
3. Find your notebooks (named after clients)

**Each notebook contains:**
- Consolidated PDF source
- 40+ research sources
- 6 detailed analysis notes
- Interactive mind map
- Chat interface

---

## Quick Reference

### Run All Clients (Fast Mode)
```bash
./launch_ape.sh fast
```

### Run All Clients (Deep Mode)
```bash
./launch_ape.sh deep
```

### Run Specific Clients
Edit `vars.py` and comment out clients you don't want:
```python
clients = [
    "client1",
    # "client2",  # Skip this one
]
```

### View Logs
```bash
tail -f logs/client1.log
```

### Stop Pipeline
```bash
# Press Ctrl+C in terminal
# Or:
podman stop <container-id>
```

---

## Common Issues

### "Service account key not found"
```bash
# Verify file exists
ls -la ~/Project-APE/*.json

# Should show your service account key file
```

### "403 Forbidden" from Google Drive
**Cause:** Drive folder not shared with service account

**Fix:** Complete Step 7 above for each folder

### Dashboard not loading
```bash
# Check if port 8765 is in use
lsof -i :8765

# Kill process if needed
kill <PID>

# Restart
./launch_ape.sh fast
```

### "Permission denied" errors (Linux only)
```bash
# Run permission fix script
./fix-permissions.sh

# Then restart
./launch_ape.sh fast
```

---

## What's Next?

After your first successful run:

1. ✅ **Explore** your NotebookLM notebooks
2. ✅ **Try deep mode** for higher quality research
3. ✅ **Add more clients** to vars.py
4. ✅ **Review** [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md) for full value prop
5. ✅ **Read** [README.md](README.md) for detailed documentation

---

## Time Breakdown

| Step | Time | Frequency |
|------|------|-----------|
| Create service account | 15 min | One-time |
| Clone repository | 1 min | One-time |
| Install requirements | 5 min | One-time |
| Configure vars.py | 5 min | Per client batch |
| Authenticate NotebookLM | 2 min | One-time |
| Setup credentials | 1 min | One-time |
| Share folders | 2 min | Per folder |
| **First-time total** | **~30 min** | - |
| Run pipeline | 15-40 min | Every run |

**After first setup:** Just edit vars.py and run `./launch_ape.sh fast`

---

**For detailed documentation:** [README.md](README.md)  
**For service account setup:** [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)

**Project APE - Transform 40 hours of manual research into 20 minutes of automated intelligence.**
