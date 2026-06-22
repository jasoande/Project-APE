# Project APE - Quick Start Guide

**Get up and running in 30 minutes**

---

## Prerequisites

Before you start, ensure you have:
- [ ] macOS or Linux machine
- [ ] Google Cloud account
- [ ] Google Drive folders with client documents
- [ ] Terminal access

---

## Step 1: Clone Repository

```bash
git clone <repository-url> Project-APE
cd Project-APE
```

---

## Step 2: Run Setup

```bash
./setup.sh
```

This will:
1. Install Podman (or Docker), Python 3.14, NotebookLM CLI
2. Open browser for NotebookLM authentication
3. Create Google Cloud service account
4. Configure container credentials
5. Prompt for client configuration

**Follow the prompts** - the script guides you through each step.

---

## Step 3: Configure Clients

Edit `vars.py`:

```bash
nano vars.py
```

Add your clients:

```python
clients = [
    "acme_corp",
    "globex_industries"
]

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/1abc...xyz"

globex_industries_name = "Globex Industries" 
globex_industries_folder = "https://drive.google.com/drive/folders/2def...uvw"
```

**Save and exit:** Ctrl+O, Enter, Ctrl+X

---

## Step 4: Share Drive Folders

Get your service account email:

```bash
grep SERVICE_ACCOUNT_EMAIL .env
```

For **each** client folder:

1. Open https://drive.google.com
2. Right-click the folder → **Share**
3. Paste service account email
4. Set permission to **"Viewer"**
5. Uncheck **"Notify people"**
6. Click **"Share"**

---

## Step 5: Launch Project APE

```bash
./launch_ape.sh fast
```

**Monitor progress:**
- Dashboard: http://localhost:8765
- Logs: `tail -f logs/*.log`

**Wait for completion:**
- 1 client: ~15-20 minutes
- 3 clients: ~45-60 minutes

---

## Step 6: View Results

Open NotebookLM:

```bash
open https://notebooklm.google.com
```

You'll see a notebook for each client with 6 comprehensive notes:
1. Industry Analysis & Business Profile
2. Innovation Assessment & Executive Summary
3. Technology Partners & Value Propositions
4. Strategic Ideas & How Might We Statements
5. Account Team & Partner Onboarding
6. Comprehensive Account Plan

---

## Next Steps

### Run Again for Updates

```bash
./launch_ape.sh fast client_name
```

### Add New Client

```bash
# 1. Edit vars.py
nano vars.py

# 2. Add new client entry

# 3. Share Drive folder with service account

# 4. Run analysis
./launch_ape.sh fast new_client
```

### Try Deep Mode

```bash
./launch_ape.sh deep
```

More thorough analysis (35-40 min/client)

---

## Troubleshooting

### Command Not Found: notebooklm

```bash
source ./activate-ape-env.sh
notebooklm --version
```

### Can't Access Drive Folder

Make sure folder is shared with service account:

```bash
grep SERVICE_ACCOUNT_EMAIL .env
# Share folder with this email in Google Drive
```

### Podman/Docker Not Running

**macOS (Podman):**
```bash
podman machine start
```

**Docker:**
```bash
open -a Docker
```

---

## Command Reference

```bash
# Setup
./setup.sh                      # Complete setup

# Run pipeline
./launch_ape.sh fast            # Fast mode (all clients)
./launch_ape.sh deep            # Deep mode (all clients)
./launch_ape.sh fast client1    # Specific client

# Activate venv (new terminals)
source ./activate-ape-env.sh

# View dashboard
open http://localhost:8765

# View results
open https://notebooklm.google.com

# Check status
podman ps                       # Running containers
docker ps                       # (if using Docker)
tail -f logs/*.log             # Live logs
```

---

## Getting Help

- **Full documentation:** README.md
- **Detailed troubleshooting:** TROUBLESHOOTING.md
- **Setup issues:** Check logs in `./logs/`
- **Dashboard:** http://localhost:8765

---

**That's it! You're ready to generate AI-powered account plans.**
