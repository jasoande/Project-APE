# Automated Setup Guide - Complete Project APE Workflow

**Date:** 2026-06-22  
**Purpose:** Complete automated setup from zero to running Project APE

## Overview

This guide covers the **fully automated** setup process for Project APE, including Google Cloud service account creation.

### What Gets Automated

1. ✅ **Environment Setup** - Podman/Docker, Python, NotebookLM CLI
2. ✅ **Service Account Creation** - Google Cloud project, APIs, credentials
3. ✅ **NotebookLM Authentication** - Browser-based login
4. ✅ **Credential Configuration** - Container volume setup
5. ⚙️ **Manual Only:** Sharing Google Drive folders with service account

### Prerequisites

- macOS or Linux machine (or macOS VM with Docker)
- Google account
- Google Cloud billing enabled (free tier sufficient)
- Terminal/command line access

## Complete Automated Workflow

### Step 1: Initial Environment Setup

```bash
# Clone the repository (if not already done)
cd ~/
git clone <repository-url> Project-APE
cd Project-APE

# Run environment setup
./setup-environment.sh
```

**What this does:**
- ✅ Installs Homebrew (macOS)
- ✅ Installs Podman (or Docker on macOS VMs)
- ✅ Installs Python 3.14
- ✅ Creates virtual environment
- ✅ Installs NotebookLM CLI
- ✅ Installs Playwright browser
- ✅ Creates activation helper script

**Expected duration:** 5-10 minutes

### Step 2: Google Cloud Service Account (Automated)

```bash
# Install gcloud CLI if not already installed
# macOS:
brew install --cask google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Run automated service account creator
./create-service-account.sh
```

**What this does:**
- ✅ Authenticates with Google Cloud
- ✅ Creates new GCP project (or uses existing)
- ✅ Enables Google Drive API
- ✅ Creates service account
- ✅ Generates service account key JSON
- ✅ Creates .env file with configuration
- ✅ Secures key file permissions

**Expected duration:** 3-5 minutes (plus user interaction)

**Output files:**
- `service-account-key.json` - Service account credentials
- `.env` - Environment configuration

### Step 3: Share Google Drive Folders

**This step must be done manually** (Google Drive UI required):

```bash
# The script will output your service account email, for example:
# project-ape-service@project-ape-12345.iam.gserviceaccount.com
```

For **each client folder**:

1. Open https://drive.google.com
2. Right-click the client folder → **Share**
3. Paste service account email
4. Set permission to **"Viewer"**
5. Uncheck **"Notify people"**
6. Click **"Share"**

**Expected duration:** 1-2 minutes per folder

### Step 4: Configure Client List

```bash
# Copy example configuration
cp example-vars.py vars.py

# Edit with your clients
nano vars.py
# or
vim vars.py
```

**Example `vars.py`:**
```python
clients = [
    "acme_corp",
    "globex_industries", 
    "initech",
    "wayne_enterprises"
]
```

**Expected duration:** 2-3 minutes

### Step 5: NotebookLM Authentication

```bash
# Activate virtual environment
source ./activate-ape-env.sh

# Login to NotebookLM (opens browser)
notebooklm login
```

**What this does:**
- ✅ Opens Chromium browser
- ✅ Prompts for Google login
- ✅ Saves authentication locally
- ✅ Stores credentials in `~/.notebooklm/`

**Expected duration:** 1-2 minutes

### Step 6: Container Credentials Setup

```bash
# Setup NotebookLM credentials for container
./setup-credentials.sh
```

**What this does:**
- ✅ Creates persistent volume for credentials
- ✅ Copies NotebookLM auth to volume
- ✅ Sets proper permissions
- ✅ Prepares for container launch

**Expected duration:** < 1 minute

### Step 7: Launch Project APE

```bash
# Fast mode (15-20 minutes per client)
./launch_ape.sh fast

# Or deep mode (35-40 minutes per client)
./launch_ape.sh deep

# Or specific clients
./launch_ape.sh fast acme_corp globex_industries
```

**What this does:**
- ✅ Pulls container image (first time only)
- ✅ Mounts credentials and configuration
- ✅ Starts Project APE pipeline
- ✅ Launches dashboard on http://localhost:8765

**Expected duration:**
- First time: 2-5 minutes (image pull) + processing time
- Subsequent: Processing time only

### Step 8: Monitor Progress

```bash
# Open dashboard
open http://localhost:8765

# Or watch container logs
podman logs -f <container-id>
# or
docker logs -f <container-id>
```

## Complete Command Sequence (Copy-Paste)

Here's the entire workflow in one block:

```bash
##############################################################################
# PROJECT APE - COMPLETE AUTOMATED SETUP
##############################################################################

# Step 1: Environment setup
./setup-environment.sh

# Step 2: Install gcloud CLI (if needed)
# macOS:
brew install --cask google-cloud-sdk
# Linux:
# curl https://sdk.cloud.google.com | bash && exec -l $SHELL

# Step 3: Create service account (automated)
./create-service-account.sh

# Step 4: Share Drive folders with service account
# MANUAL: Use Google Drive UI to share folders
# Service account email will be shown after Step 3

# Step 5: Configure clients
cp example-vars.py vars.py
nano vars.py

# Step 6: Activate environment
source ./activate-ape-env.sh

# Step 7: Login to NotebookLM
notebooklm login

# Step 8: Setup container credentials
./setup-credentials.sh

# Step 9: Launch Project APE
./launch_ape.sh fast

# Step 10: Open dashboard
open http://localhost:8765
```

## Verification Checklist

Before running `./launch_ape.sh`, verify:

- [x] `service-account-key.json` exists with 600 permissions
- [x] `.env` file exists with correct configuration
- [x] `vars.py` configured with client names
- [x] Google Drive folders shared with service account
- [x] NotebookLM authenticated (`~/.notebooklm/` exists)
- [x] Virtual environment activates (`source ./activate-ape-env.sh`)
- [x] Podman/Docker is running (`podman ps` or `docker ps`)

**Quick verify:**
```bash
ls -la service-account-key.json  # Should show -rw-------
cat .env | grep SERVICE_ACCOUNT  # Should show path
cat vars.py | grep clients       # Should show your clients
ls ~/.notebooklm/profiles/default/storage_state.json  # Should exist
source ./activate-ape-env.sh && notebooklm --version  # Should work
podman ps  # or docker ps - should not error
```

## Time Breakdown

| Step | Duration | Notes |
|------|----------|-------|
| Environment setup | 5-10 min | First time only |
| gcloud CLI install | 2-3 min | If not installed |
| Service account creation | 3-5 min | Automated |
| Share Drive folders | 1-2 min/folder | Manual |
| Configure vars.py | 2-3 min | One time |
| NotebookLM login | 1-2 min | One time |
| Credentials setup | < 1 min | Automated |
| Container pull | 2-5 min | First time only |
| APE fast mode | 15-20 min/client | Per run |
| APE deep mode | 35-40 min/client | Per run |

**Total first-run:** ~20-30 minutes (setup) + processing time  
**Subsequent runs:** ~15-20 minutes (fast) or ~35-40 minutes (deep)

## Troubleshooting

### Issue: gcloud command not found

**Solution:**
```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify
gcloud --version
```

### Issue: gcloud authentication failed

**Solution:**
```bash
gcloud auth login
gcloud auth list
```

### Issue: Billing not enabled

**Solution:**
1. Visit: https://console.cloud.google.com/billing
2. Link billing account (free tier is sufficient)
3. Verify: `gcloud beta billing projects describe PROJECT_ID`

### Issue: Drive API not enabled

**Solution:**
```bash
gcloud services enable drive.googleapis.com --project=PROJECT_ID
```

### Issue: Service account permission denied

**Cause:** Drive folders not shared with service account

**Solution:**
1. Get service account email from `service-account-key.json`:
   ```bash
   grep client_email service-account-key.json
   ```
2. Share each Drive folder with that email (Viewer permission)

### Issue: Podman machine won't start (macOS VM)

**Solution:**
```bash
# Use Docker instead
open -a Docker
sleep 30
docker ps  # Verify it's running

# launch_ape.sh will automatically use Docker
```

### Issue: NotebookLM login fails

**macOS VM Solution:**
```bash
# Ensure running from GUI, not SSH
# Or use X11 forwarding: ssh -X -Y user@host
```

**Linux SSH Solution:**
```bash
xvfb-run notebooklm login
```

## Files Generated by Automated Setup

```
Project-APE/
├── service-account-key.json    # Service account credentials (gitignored)
├── .env                        # Environment configuration
├── vars.py                     # Client list (from example-vars.py)
├── activate-ape-env.sh         # Venv activation helper
└── ~/.notebooklm/              # NotebookLM authentication
    └── profiles/default/
        └── storage_state.json
```

## Security Considerations

### Service Account Key

**DO:**
- ✅ Keep `service-account-key.json` with 600 permissions
- ✅ Store in Project APE directory only
- ✅ Add to `.gitignore` (already included)
- ✅ Rotate keys every 90 days

**DON'T:**
- ❌ Commit to git
- ❌ Share via email/messaging
- ❌ Upload to cloud storage
- ❌ Grant more than "Viewer" permission to Drive folders

### Best Practices

1. **Principle of Least Privilege:**
   - Service account has "Viewer" only (read-only)
   - No project-level IAM roles needed
   - Only shared specific folders, not entire Drive

2. **Key Rotation:**
   ```bash
   # Every 90 days:
   ./create-service-account.sh  # Creates new key
   # Update folder sharing if needed
   # Delete old key after verification
   ```

3. **Audit Access:**
   - Review service account activity in Google Cloud Console
   - Check which folders are shared periodically
   - Remove access to folders no longer needed

## Comparison: Manual vs Automated

| Task | Manual | Automated | Time Saved |
|------|--------|-----------|------------|
| Create GCP project | Google Cloud Console UI | `create-service-account.sh` | ~3 min |
| Enable APIs | Click through menus | `gcloud services enable` | ~2 min |
| Create service account | Fill forms | `gcloud iam service-accounts create` | ~2 min |
| Generate key | Download, move, chmod | All automated | ~2 min |
| Create .env | Copy template, edit | Auto-generated | ~1 min |
| **Total** | **15-20 min** | **3-5 min** | **~12 min** |

## Next Steps After Automated Setup

Once setup is complete:

1. **Test with one client:**
   ```bash
   echo 'clients = ["test_client"]' > vars.py
   ./launch_ape.sh fast test_client
   ```

2. **Verify results:**
   - Check dashboard: http://localhost:8765
   - Check NotebookLM: https://notebooklm.google.com
   - Verify notebook created for test client

3. **Scale to all clients:**
   ```bash
   # Edit vars.py with all clients
   nano vars.py
   
   # Launch for all
   ./launch_ape.sh fast
   ```

4. **Schedule regular runs:**
   ```bash
   # Add to crontab for weekly runs
   0 9 * * MON cd ~/Project-APE && ./launch_ape.sh fast
   ```

## Additional Resources

- **Service Account Setup (Manual):** SERVICE-ACCOUNT-SETUP.md
- **macOS VM Testing:** MACOS-VM-TESTING-GUIDE.md
- **Root Cause Analysis:** MAC-SETUP-ROOT-CAUSE-ANALYSIS.md
- **Setup Improvements:** SETUP-SCRIPT-IMPROVEMENTS.md
- **Main Documentation:** README.md

## Summary

The automated setup process reduces manual configuration from **45-60 minutes** to **20-30 minutes**, with most of that being one-time setup.

**Automated:**
- ✅ Environment setup
- ✅ Service account creation
- ✅ API enablement
- ✅ Credential generation
- ✅ Configuration file creation

**Manual (unavoidable):**
- ⚙️ Google Drive folder sharing (requires UI)
- ⚙️ Client list configuration (business logic)
- ⚙️ NotebookLM login (browser authentication)

The `create-service-account.sh` script handles all Google Cloud setup automatically, requiring only user approval at key decision points.
