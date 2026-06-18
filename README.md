# Project APE - Account Planning Engine

![King Kong Logo](dashboard/static/kingkong.png)

**AI-Powered Enterprise Account Planning Automation**

**Version:** 3.0.6  
**Created by:** Jason Anderson  
**Powered by:** Google NotebookLM

---

## What is Project APE?

Project APE (Account Planning Engine) **transforms 40-60 hours of manual account research into 15-40 minutes of automated, AI-powered intelligence gathering**.

It automates the entire account planning research process:
- ✅ Downloads company documents from Google Drive
- ✅ Consolidates materials into a single PDF
- ✅ Generates 40+ research sources using Google NotebookLM
- ✅ Creates 6 detailed strategic analysis notes
- ✅ Produces searchable notebooks with mind maps
- ✅ Processes up to 6 accounts simultaneously

**See [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md) for the full value proposition.**

---

## Quick Start - Complete Workflow

### Overview

Here's exactly what you'll do from start to finish:

```
1. Create Google service account  (one-time, ~15 min)
2. Clone Project APE repository   (2 min)
3. Run setup-environment.sh       (automated, ~5 min)
4. Configure vars.py              (5 min per client)
5. Authenticate with NotebookLM   (one-time, 2 min)
6. Run setup-credentials.sh       (automated, 1 min)
7. Launch pipeline                (15-40 min automated)
8. View status at localhost:8765  (real-time monitoring)
9. Access results in NotebookLM   (browse notebooks)
```

**Total setup time:** ~30 minutes (one-time)  
**Per-run time:** 15-40 minutes (fully automated)

---

## Step-by-Step Setup

### Step 1: Create Google Service Account

The service account allows Project APE to automatically download documents from your Google Drive folders.

**Follow the detailed guide:** [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)

**What you'll get:**
- Google Cloud project
- Service account with Drive API access
- Service account JSON key file (e.g., `project-ape-service-key.json`)
- Service account email (e.g., `project-ape-service@project-ape.iam.gserviceaccount.com`)

**Time:** ~15 minutes (one-time)

---

### Step 2: Clone Project APE Repository

```bash
# Clone the repository
git clone <repository-url>
cd Project-APE

# Verify you're in the right place
ls -la launch_ape.sh
# Should show: -rwxr-xr-x ... launch_ape.sh
```

**What happens:**
- Downloads all Project APE code and scripts
- Sets up the directory structure
- Provides launch scripts for Mac and Linux

**Time:** ~2 minutes

---

### Step 3: Run setup-environment.sh

This script installs everything you need to run Project APE.

```bash
./setup-environment.sh
```

**What it installs:**
1. **Podman** (container runtime)
   - macOS: via Homebrew, includes Podman machine initialization
   - Linux: via dnf (RHEL/Fedora) or apt (Debian/Ubuntu)

2. **Node.js 20+** (required for NotebookLM CLI)
   - macOS: via Homebrew
   - Linux: via NodeSource repository

3. **NotebookLM CLI** (notebooklm-py)
   - Installed globally via npm
   - Provides `notebooklm` command

**What you DON'T need:**
- ❌ Python (runs inside pre-built container)
- ❌ LibreOffice (included in container)
- ❌ Document conversion tools (included in container)
- ❌ Image building tools (pre-built images provided)

**Time:** ~5 minutes (automated, requires sudo on Linux)

---

### Step 4: Configure vars.py

Define your clients and their Google Drive folders.

```bash
# Copy the example configuration
cp example-vars.py vars.py

# Edit with your favorite editor
nano vars.py
# or
code vars.py
```

**For each client, configure:**

```python
clients = [
    "your_client_test",
]

# Client configuration
your_client_test_name = "Your Client Name"
your_client_test_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
your_client_test_industry = "pharmaceuticals and life sciences"
your_client_test_subsegments = "drug discovery, clinical trials, manufacturing"
```

**How to get the folder URL:**
1. Open Google Drive in your browser
2. Navigate to the client's folder
3. Copy the URL from the address bar
   ```
   https://drive.google.com/drive/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen
   ```

**Industry and Subsegments:**
- **Industry:** The primary industry (e.g., "pharmaceuticals", "supply chain software", "asset management")
- **Subsegments:** 2-3 specific areas of focus (e.g., "drug discovery, clinical trials, manufacturing")
- These are used to guide the research focus - be specific

**Example - Multiple Clients:**

```python
clients = [
    "merck_test",
    "blue_yonder_test",
]

# Merck
merck_test_name = "Merck"
merck_test_folder = "https://drive.google.com/drive/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen"
merck_test_industry = "pharmaceuticals and life sciences"
merck_test_subsegments = "drug discovery, clinical trials, manufacturing operations"

# Blue Yonder
blue_yonder_test_name = "Blue Yonder"
blue_yonder_test_folder = "https://drive.google.com/drive/folders/1GnoQMM8ZK-0PSZElLIWa2z_3fy1TpoBK"
blue_yonder_test_industry = "supply chain and logistics software"
blue_yonder_test_subsegments = "demand planning, warehouse management, transportation optimization"
```

**Time:** ~5 minutes per client

---

### Step 5: Authenticate with NotebookLM

NotebookLM authentication happens on your host machine (not inside the container).

```bash
notebooklm login
```

**What happens:**
1. Opens your browser to Google authentication
2. You sign in with your Google account
3. Grant NotebookLM CLI permissions
4. Credentials saved to `~/.notebooklm/profiles/default/`

**You only do this once** - credentials persist across runs.

**Time:** ~2 minutes (one-time)

---

### Step 6: Run setup-credentials.sh

Copy your NotebookLM credentials into the container's persistent volume.

```bash
./setup-credentials.sh
```

**What happens:**
1. Checks that you authenticated in Step 5
2. Creates a Podman volume: `project-ape-credentials`
3. Copies `~/.notebooklm/` credentials into the volume
4. Sets correct permissions inside the volume

**Why?** The container needs its own copy of credentials because it runs in an isolated environment.

**You only do this once** (unless you re-authenticate with NotebookLM).

**Time:** ~1 minute

---

### Step 7: Share Drive Folders with Service Account

For each folder in `vars.py`, grant your service account "Viewer" access.

**Your service account email** (from Step 1):
```
project-ape-service@project-ape.iam.gserviceaccount.com
```

**For each client folder:**

1. **Open Google Drive** → Find the client folder
2. **Right-click folder** → **"Share"**
3. **Add service account email**
4. **Set permission to "Viewer"**
5. **Uncheck "Notify people"** (service accounts don't get emails)
6. **Click "Share"**

**Verify:** Service account appears in "People with access" with "Viewer" permission.

**Repeat for all clients** in `vars.py`.

**Time:** ~2 minutes per folder

---

### Step 8: Launch Pipeline

**Fast Mode (15-20 minutes):**
```bash
./launch_ape.sh fast
```

**Deep Mode (35-40 minutes):**
```bash
./launch_ape.sh deep
```

**What happens automatically:**

1. **Architecture detection** - Identifies ARM64 (Mac) or x86_64 (Linux)
2. **Image pull** - Downloads correct container image from Quay.io
3. **Container launch** - Starts containerized pipeline with all mounts
4. **Dashboard start** - Flask server on http://localhost:8765
5. **For each client in `vars.py`:**
   - Download files from Google Drive folder
   - Convert Office docs to PDF (if needed)
   - Consolidate all PDFs into one
   - Upload to NotebookLM
   - Generate 40+ research sources
   - Create 6 analysis notes
   - Generate mind map
   - Calculate quality score

**Time:** 15-40 minutes (fully automated)

---

### Step 9: Monitor Progress

Open your browser to the real-time dashboard:

```bash
open http://localhost:8765
```

**Dashboard shows:**
- ✅ Client names
- ✅ Current status for each client
- ✅ Execution timer (live updates)
- ✅ Progress through pipeline stages
- ✅ Quality scores
- ✅ Error indicators

**Stages you'll see:**
1. `Downloading` - Pulling files from Google Drive
2. `Consolidating` - Merging PDFs
3. `Uploading` - Creating NotebookLM notebook
4. `Researching` - Generating sources and notes
5. `Completed` - Notebook ready!

**Time:** Runs in parallel with Step 8

---

### Step 10: Access Results in NotebookLM

Once pipeline completes, view your notebooks:

1. **Open NotebookLM:** [https://notebooklm.google.com](https://notebooklm.google.com)
2. **Sign in** with your Google account (same as Step 5)
3. **Find your notebooks:**
   - Named after your clients (e.g., "Merck Test", "Blue Yonder Test")
   - Sorted by creation date (most recent first)

**Each notebook contains:**
- 📄 **Consolidated PDF source** - All client documents in one file
- 🔍 **40+ research sources** - Auto-generated articles and analyses
- 📝 **6 analysis notes:**
  1. Company Overview & Strategic Positioning
  2. Product Portfolio & Technology Stack
  3. Business Challenges & Pain Points
  4. Organizational Structure & Decision Makers
  5. Market Position & Competitive Landscape
  6. Strategic Opportunities & Engagement Points
- 🗺️ **Mind map** - Visual relationship diagram
- 💬 **Chat interface** - Ask follow-up questions

**Time:** Results ready immediately after Step 8 completes

---

## Execution Modes Explained

### Fast Mode

```bash
./launch_ape.sh fast
```

**Duration:** 15-20 minutes  
**Sources:** 40+  
**Quality target:** 8.5/10  
**Best for:** Quick account briefings, opportunity qualification

**Use when:**
- Need rapid turnaround for discovery calls
- Qualifying new opportunities
- Initial account research
- Time-sensitive deliverables

---

### Deep Mode

```bash
./launch_ape.sh deep
```

**Duration:** 35-40 minutes  
**Sources:** 40+  
**Quality target:** 9.0/10  
**Best for:** Strategic account planning, major deal preparation

**Use when:**
- Preparing for strategic account reviews
- High-value deal preparation
- Comprehensive competitive analysis
- Executive presentations

---

## What Happens Behind the Scenes

### Container Runtime

Project APE runs in a containerized environment for consistency and reliability:

**Mac (ARM64):**
```bash
Image: quay.io/jasoande/project_ape/project-ape:latest
Architecture: arm64
Runtime: Podman with libkrun VM
```

**Linux (x86_64):**
```bash
Image: quay.io/jasoande/project_ape/project-ape:3.0.6-amd64
Architecture: amd64
Runtime: Podman on native kernel
```

**Automatic detection** - `launch_ape.sh` picks the right image for your platform.

### File Mounts

The container mounts these host directories:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./vars.py` | `/app/vars.py` | Client configuration |
| `./.env` | `/app/.env` | API credentials |
| `./logs/` | `/app/logs/` | Execution logs |
| `./.multi_process_status/` | `/app/.multi_process_status/` | Status files for dashboard |
| `./service-account-key.json` | `/app/service-account.json` | Google service account credentials |
| `project-ape-credentials` | `/home/apeuser/.notebooklm` | NotebookLM authentication (volume) |
| `project-ape-cache` | `/home/apeuser/.project-ape` | Drive download cache (volume) |

**Result:** Container reads your config, writes logs to host, persists credentials.

### Network Ports

- **8765** - Dashboard (Flask web server)
- **Auto** - Ephemeral ports for Google APIs

---

## Configuration Files

### vars.py

**Purpose:** Define clients and their Google Drive folders

**Location:** Project root (`./vars.py`)

**Format:**
```python
clients = ["client1_test", "client2_test"]

client1_test_name = "Client Name"
client1_test_folder = "https://drive.google.com/drive/folders/..."
client1_test_industry = "industry name"
client1_test_subsegments = "segment1, segment2, segment3"
```

**See:** `example-vars.py` for complete template

---

### .env

**Purpose:** Store service account path (automatically configured)

**Location:** Project root (`./.env`)

**Contents:**
```bash
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

**You don't need to edit this** - already correct in `.env.template`.

---

### Service Account JSON Key

**Purpose:** Authenticate with Google Drive API

**Location:** Project root (e.g., `./project-ape-service-key.json`)

**Created in:** Step 1 (SERVICE-ACCOUNT-SETUP.md)

**Security:**
```bash
# Set restrictive permissions
chmod 600 project-ape-service-key.json

# Verify
ls -la project-ape-service-key.json
# Should show: -rw-------
```

**Never commit to git** - already in `.gitignore`.

---

## Output Files

### Logs

**Location:** `./logs/<client_id>.log`

**Contents:**
- Detailed execution log for each client
- Google Drive download activity
- PDF consolidation steps
- NotebookLM API calls
- Error messages and retries

**View logs:**
```bash
tail -f logs/merck_test.log
```

---

### Status Files

**Location:** `./.multi_process_status/<client_id>.json`

**Purpose:** Real-time status for dashboard

**Contents:**
```json
{
  "name": "Merck",
  "token": "merck_test",
  "status": "Researching",
  "start_time": 1718654321.5,
  "quality_score": 8.7,
  "sources_count": 42
}
```

**Updated continuously** during execution.

---

### NotebookLM Notebooks

**Location:** Your Google account at [notebooklm.google.com](https://notebooklm.google.com)

**Naming:** Client name (e.g., "Merck", "Blue Yonder")

**Persistent** - notebooks remain in your account indefinitely.

---

## Advanced Usage

### Running Specific Clients

By default, `launch_ape.sh` runs **all clients** in `vars.py`.

To run specific clients, edit `vars.py`:
```python
# Comment out clients you don't want to run
clients = [
    "merck_test",
    # "blue_yonder_test",  # Skip this one
]
```

---

### Stopping a Running Pipeline

```bash
# Find the container
podman ps

# Stop it
podman stop <container-id>
```

---

### Viewing Container Logs

```bash
# Follow container output
podman logs -f <container-id>
```

---

### Clearing Cache

Drive downloads are cached in `project-ape-cache` volume for faster subsequent runs.

**To clear cache:**
```bash
podman volume rm project-ape-cache
```

**Next run will re-download** all files from Drive.

---

## Troubleshooting

### "Permission denied" errors

**Linux only** - SELinux blocks file access.

**Fix:** Already handled in `launch_ape.sh` with `:z` flags on mounts.

**Verify:**
```bash
grep ":z" launch_ape.sh
# Should show multiple mount points with :z flag
```

---

### "Service account key not found"

**Cause:** Service account JSON file not in Project APE directory.

**Fix:**
```bash
# Check file exists
ls -la project-ape-service-key.json

# If missing, re-download from Google Cloud Console
# See SERVICE-ACCOUNT-SETUP.md Step 4
```

---

### "NotebookLM credentials not found"

**Cause:** Skipped Step 5 or Step 6.

**Fix:**
```bash
# Authenticate
notebooklm login

# Setup credentials in container
./setup-credentials.sh
```

---

### "403 Forbidden" downloading from Drive

**Cause:** Drive folder not shared with service account.

**Fix:**
1. Get service account email from JSON key:
   ```bash
   grep client_email project-ape-service-key.json
   ```
2. Share each folder in `vars.py` with this email
3. Grant "Viewer" permission

---

### Dashboard shows "00m 00s" timer

**Cause:** Running older container image (before timer fix).

**Fix:** Image will auto-update on next pull:
```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

---

## System Requirements

### Minimum

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB free
- **Network:** Broadband internet
- **OS:** macOS 12+, RHEL 9+, Ubuntu 22.04+

### Recommended

- **CPU:** 6-8 cores (for 6 parallel clients)
- **RAM:** 8-12 GB
- **Disk:** 20 GB free
- **Network:** 100 Mbps+

### Supported Platforms

- ✅ macOS (ARM64 - M1/M2/M3/M4)
- ✅ Linux x86_64 (RHEL, Fedora, Ubuntu, Debian)
- ✅ Windows WSL2 (via Linux x86_64 image)

---

## Documentation

- **[EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md)** - Why Project APE? Problem, solution, advantages
- **[SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)** - Complete Google service account guide with screenshots
- **[GETTING-STARTED.md](GETTING-STARTED.md)** - Detailed setup walkthrough
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick reference
- **[CHANGES-SUMMARY.md](CHANGES-SUMMARY.md)** - Recent fixes and improvements

**Developer docs:** See `developer-docs/` for image building and internal architecture.

---

## Support

**Created and maintained by Jason Anderson**

For issues, questions, or feature requests, contact the project maintainer.

---

## Version History

- **3.0.6** (2026-06-17) - Rate limit fixes, cross-platform improvements, documentation overhaul
- **3.0.5** (2026-06-16) - Multi-architecture support, container improvements
- **3.0.0** (2026-06-15) - Google Drive integration, containerization

---

**Project APE - Making Enterprise Account Planning Effortless**

*Transform 40 hours of manual research into 20 minutes of automated intelligence.*
