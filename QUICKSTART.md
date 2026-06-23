<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="200"/>
</div>

# Project APE - Quick Start Guide
## From Zero to First Research in 30 Minutes

**This guide walks you through setting up and running your first account research.**

Expected time: **30 minutes** (mostly waiting for automated downloads)

---

## ✅ Before You Begin

**What you need:**
- [ ] **Computer:** macOS (Intel/ARM) or Linux (RHEL, Ubuntu, Fedora, Debian)
- [ ] **Google Account:** Free account (for NotebookLM and Drive)
- [ ] **Google Cloud:** Free tier account with billing enabled (~$0 actual usage)
- [ ] **Documents:** Client files in a Google Drive folder (PDFs, Word, PowerPoint)
- [ ] **Internet:** Stable connection for downloads and API calls

**What you DON'T need:**
- ❌ Deep technical knowledge (script automates everything)
- ❌ Expensive hardware (8GB RAM, 20GB disk is enough)
- ❌ Manual AI setup (NotebookLM handles it)

---

## 📥 Step 1: Download Project APE (2 minutes)

```bash
git clone <repository-url> Project-APE
cd Project-APE
```

**What just happened:** You downloaded all the code, scripts, and configuration files.

---

## ⚙️ Step 2: Run Automated Setup (15-20 minutes)

```bash
./setup.sh
```

**The script automates everything:**

| Step | What Happens | Time | Action Required |
|------|--------------|------|-----------------|
| 1️⃣ | Detect OS and architecture | 5 sec | None (automatic) |
| 2️⃣ | Install Google Cloud SDK | 2-3 min | Accept prompts |
| 3️⃣ | Authenticate with Google | 1 min | Click "Allow" in browser |
| 4️⃣ | Install Podman/Docker | 3-5 min | Accept prompts (macOS/Linux) |
| 5️⃣ | Install Python 3.11+ and dependencies | 2-3 min | None (automatic) |
| 6️⃣ | Install NotebookLM CLI | 1 min | None (automatic) |
| 7️⃣ | Authenticate with NotebookLM | 1 min | Click "Allow" in browser |
| 8️⃣ | Create Google Cloud service account | 2 min | Provide project ID |
| 9️⃣ | Configure container credentials | 30 sec | None (automatic) |
| 🔟 | (Optional) Automated Drive folder sharing | 1 min | Provide folder URLs |

**Total:** 15-20 minutes (most of it is waiting for downloads)

**Pro Tip:** Have your Google Cloud project ID ready. Create one at https://console.cloud.google.com if you don't have one.

---

## 📝 Step 3: Configure Your Clients (3 minutes)

Edit the configuration file:

```bash
nano vars.py  # Or use your favorite editor
```

**Add your clients** (example with 2 clients):

```python
# List of clients to research
clients = [
    "acme_corp",
    "globex_industries"
]

# Acme Corporation configuration
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/1abc...xyz"
acme_corp_industry = "pharmaceuticals and life sciences"
acme_corp_subsegments = "drug discovery, clinical trials, manufacturing"

# Globex Industries configuration
globex_industries_name = "Globex Industries"
globex_industries_folder = "https://drive.google.com/drive/folders/2def...uvw"
globex_industries_industry = "supply chain software"
globex_industries_subsegments = "warehouse management, demand planning"
```

**Configuration tips:**
- **Client ID** (`acme_corp`) - Use lowercase, underscores only, no spaces
- **Name** - The official company name (displayed in outputs)
- **Folder** - Copy the full URL from Google Drive (right-click folder → "Get link")
- **Industry** - General industry category (helps AI focus research)
- **Subsegments** - Specific areas within the industry (optional but recommended)

**Save and exit:** 
- **nano:** Ctrl+O, Enter, Ctrl+X
- **vim:** Esc, `:wq`, Enter
- **Other editors:** Save normally

---

## 🔗 Step 4: Share Drive Folders with Service Account (2 minutes)

### Option A: Automated Sharing (Recommended)

```bash
python3 share-drive-folders.py
```

The script automatically shares all folders in `vars.py` with your service account.

### Option B: Manual Sharing

If you prefer manual control or the script doesn't work:

**1. Get your service account email:**
```bash
grep SERVICE_ACCOUNT_EMAIL .env
# Example output: project-ape-service@your-project.iam.gserviceaccount.com
```

**2. For EACH client folder:**
1. Open https://drive.google.com
2. Navigate to the client folder
3. Right-click folder → **"Share"**
4. Paste the service account email
5. Set permission to **"Viewer"** (read-only)
6. **UNCHECK** "Notify people" (no email notification needed)
7. Click **"Share"**

**Verification:**
```bash
# Test Drive access (optional)
python3 -c "from core.drive_manager import DriveManager; print('Drive access OK')"
```

---

## 🚀 Step 5: Launch Your First Research (15-20 minutes)

```bash
./launch_ape.sh fast
```

**What happens now:**

| Time | What's Happening |
|------|------------------|
| **0:00** | Dashboard opens in browser automatically |
| **0:05** | Downloads client documents from Drive |
| **0:10** | Consolidates files into searchable PDF |
| **1:00** | Uploads PDF to NotebookLM |
| **2:00** | Runs AI research (generates 40+ sources) |
| **10:00** | Creates 6 analysis notes |
| **15:00** | Generates mind map |
| **15-20** | **Complete!** ✅ |

**Monitor real-time progress:**

```bash
# Dashboard (auto-opens)
open http://localhost:8765

# Live logs (optional)
tail -f logs/*.log

# Check specific client
cat logs/acme_corp.log
```

**Dashboard features:**
- ⏱️ Live execution timer (stops when complete)
- 📊 Overall pipeline progress bar
- 🎯 Individual client status cards
- ⭐ Quality scores (target: 8.5+/10)
- 🔗 Direct links to NotebookLM notebooks

**Duration guide:**

| Clients | Fast Mode | Deep Mode |
|---------|-----------|-----------|
| 1 | 15-20 min | 35-40 min |
| 3 | 15-20 min | 35-40 min |
| 6 | 15-20 min | 35-40 min |

**Why same time?** Clients run in parallel - 6 accounts take the same wall-clock time as 1!

---

## 📊 Step 6: Review Your Research (5 minutes)

### Open NotebookLM

```bash
open https://notebooklm.google.com
```

**Or click the dashboard link** when pipeline completes.

### What You'll Find

Each client has a complete notebook with:

**📑 6 Strategic Analysis Notes:**
1. **Industry Analysis & Business Profile** - Context, objectives, challenges
2. **Innovation Assessment & Executive Summary** - Tech stack, digital maturity
3. **Technology Partners & Red Hat Value Propositions** - Ecosystem analysis
4. **Strategic Ideas & How Might We Statements** - 10 ideas + 15 prompts
5. **Account Team & Partner Onboarding** - Stakeholders, decision-makers
6. **Comprehensive Account Plan** - Complete overview, next steps

**🔍 Research Foundation:**
- 40+ web sources (articles, reports, news)
- Consolidated PDF of your documents
- Mind map visualizations
- Chat interface for questions

### Try the Chat Interface

Ask questions like:
- "What is their biggest technology challenge?"
- "Who leads their digital transformation?"
- "What Red Hat products align with their stack?"
- "What are their top 3 strategic priorities?"

**Every answer includes citations** - click to see the source.

---

## 🎯 What's Next?

### ✅ You're Done! But Here's More...

### 🔄 Update Existing Research

```bash
# Re-run for one client (picks up new documents/web data)
./launch_ape.sh fast acme_corp

# Re-run all clients
./launch_ape.sh fast
```

### ➕ Add More Clients

**1. Edit configuration:**
```bash
nano vars.py
```

**2. Add new client** (follow same pattern as existing):
```python
clients = [
    "acme_corp",
    "globex_industries",
    "new_client"  # ← Add to list
]

# Add configuration
new_client_name = "New Client Inc"
new_client_folder = "https://drive.google.com/drive/folders/..."
new_client_industry = "industry name"
```

**3. Share Drive folder** with service account (or use `share-drive-folders.py`)

**4. Run analysis:**
```bash
./launch_ape.sh fast new_client
```

### 🎯 Try Deep Mode (More Thorough Research)

```bash
./launch_ape.sh deep
```

**Differences from Fast mode:**
- **Duration:** 35-40 minutes (vs. 15-20)
- **Research Time:** Longer AI research per query
- **Best For:** Strategic accounts, first-time analysis, major deals
- **Retry Logic:** 1 attempt (faster, assumes good data)

### 🔧 Advanced Usage

**Run specific clients:**
```bash
./launch_ape.sh fast acme_corp globex_industries
```

**Parallel processing (all clients):**
```bash
./launch_ape.sh fast  # Up to 6 clients run simultaneously
```

**Disable dashboard (Advanced):**
```bash
# Dashboard runs automatically and stops after completion
# To run without dashboard (advanced users only):
python3 main.py --mode fast --no-dashboard
```

**Check container status:**
```bash
podman ps  # Or: docker ps
```

---

## 🔧 Common Issues & Quick Fixes

### ❌ "Command not found: notebooklm"

**Problem:** Virtual environment not activated  
**Fix:**
```bash
source ./activate-ape-env.sh
notebooklm --version  # Verify
```

### ❌ "Permission denied: Drive folder"

**Problem:** Folder not shared with service account  
**Fix:**
```bash
# Get service account email
grep SERVICE_ACCOUNT_EMAIL .env

# Share folder in Google Drive:
# Right-click folder → Share → Add email → Viewer permission
```

**Or use automated sharing:**
```bash
python3 share-drive-folders.py
```

### ❌ "Podman/Docker not running"

**macOS (Podman):**
```bash
podman machine list  # Check status
podman machine start  # Start if stopped
```

**Docker:**
```bash
open -a Docker  # Start Docker Desktop
# Wait 30 seconds for it to fully start
docker ps  # Verify
```

### ❌ "Rate limit exceeded"

**Problem:** Too many API calls to NotebookLM  
**Solution:** The script automatically retries after 60 seconds. Just wait.

### ❌ Pipeline stuck or slow

**Check:**
```bash
# View live logs
tail -f logs/*.log

# Check dashboard
open http://localhost:8765

# Verify container is running
podman ps  # or: docker ps
```

### 📚 More Help

- **Full troubleshooting:** [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
- **README:** [README.md](README.md) - Complete documentation
- **Executive summary:** [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md) - Business value

---

## 📖 Command Reference Cheat Sheet

### 🔧 Setup & Installation
```bash
./setup.sh                           # One-time setup (20-30 min)
source ./activate-ape-env.sh         # Activate venv (for new terminals)
```

### 🚀 Running Research
```bash
./launch_ape.sh fast                 # Fast mode - all clients (15-20 min)
./launch_ape.sh deep                 # Deep mode - all clients (35-40 min)
./launch_ape.sh fast client1 client2 # Specific clients only
```

### 📊 Monitoring
```bash
open http://localhost:8765           # Dashboard (auto-opens)
tail -f logs/*.log                   # Live logs (all clients)
tail -f logs/acme_corp.log          # Specific client log
cat .multi_process_status/client.json  # JSON status file
```

### 🔍 Viewing Results
```bash
open https://notebooklm.google.com   # Your research notebooks
```

### 🐳 Container Management
```bash
podman ps                            # List running containers
podman logs <container-id>           # View container logs
podman machine start                 # Start Podman (macOS)
podman machine stop                  # Stop Podman (macOS)

# Or with Docker:
docker ps                            # List containers
docker logs <container-id>           # View logs
open -a Docker                       # Start Docker Desktop
```

### 🔧 Maintenance
```bash
python3 share-drive-folders.py      # Automated Drive sharing
grep SERVICE_ACCOUNT_EMAIL .env     # Get service account email
rm -rf logs/*                       # Clear old logs
rm -rf .multi_process_status/*      # Clear status files
```

---

## 🎓 Learning Path

**Now that you've completed your first research:**

1. ✅ **Read the full README** - [README.md](README.md)
2. ✅ **Review pilot results** - [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md)
3. ✅ **Understand the architecture** - See "System Architecture" in README
4. ✅ **Check code quality** - [CODE-REVIEW-2026-06-23.md](CODE-REVIEW-2026-06-23.md)
5. ✅ **Troubleshooting guide** - [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)

---

## 🎉 Success!

**You've just:**
- ✅ Installed Project APE
- ✅ Generated your first AI-powered account research
- ✅ Saved 40-60 hours of manual work
- ✅ Created a searchable, cited knowledge base
- ✅ Unlocked 10x research capacity

**What took 40 hours now takes 15 minutes. Welcome to the future of account planning.**

---

## 📞 Need Help?

| Resource | Purpose |
|----------|---------|
| **[README.md](README.md)** | Complete documentation |
| **[EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md)** | Business value and ROI |
| **[Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)** | Common issues and fixes |
| **Dashboard** | Real-time status: http://localhost:8765 |
| **Logs** | `./logs/` directory |

---

**Version:** 3.2.0 - Simplified Dependencies Release  
**Status:** ✅ Ready for Organization-Wide Deployment

**Questions?** Check the documentation above or open an issue on GitHub.
