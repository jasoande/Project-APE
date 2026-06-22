# Project APE - Account Planning Engine

**Automated Red Hat account planning using AI-powered research and NotebookLM**

Project APE automatically generates comprehensive account plans by:
1. Downloading client documents from Google Drive
2. Analyzing with AI (Gemini)
3. Creating structured notebooks in NotebookLM
4. Generating strategic recommendations

---

## Quick Start

### Prerequisites

- **macOS** or **Linux** (RHEL, Fedora, Ubuntu, Debian)
- **Google Cloud account** with billing enabled (free tier sufficient)
- **Google Drive folders** with client documents
- **Terminal access**

### One-Command Setup

```bash
git clone <repository-url> Project-APE
cd Project-APE
./setup.sh
```

The setup script will:
1. Install Podman/Docker, Python 3.14, NotebookLM CLI
2. Authenticate with NotebookLM (opens browser)
3. Create Google Cloud service account
4. Configure container credentials
5. Guide you through client configuration

**Time:** ~20-30 minutes

### Run Your First Analysis

```bash
# 1. Configure clients (if not done during setup)
nano vars.py

# 2. Share Drive folders with service account
#    (Email shown in setup output)

# 3. Launch Project APE
./launch_ape.sh fast

# 4. Monitor progress
open http://localhost:8765

# 5. View results
open https://notebooklm.google.com
```

---

## What Project APE Does

### Input
- **Google Drive folders** containing client documents (presentations, reports, contracts, etc.)
- **Client list** in `vars.py`

### Process
1. **Download** - Fetches documents from Google Drive
2. **Consolidate** - Combines into single PDF
3. **Upload** - Adds to NotebookLM notebook
4. **Analyze** - AI generates strategic insights
5. **Deliver** - Creates 6 comprehensive notes in NotebookLM

### Output

**NotebookLM Notebook** for each client containing:

1. **Industry Analysis & Customer Business Profile**
   - Industry overview
   - Business objectives
   - Challenges and initiatives

2. **Innovation Assessment & Executive Summary**
   - Digital transformation readiness
   - Technology stack analysis
   - Executive briefing

3. **Technology Partners & Red Hat Value Propositions**
   - Existing partnerships
   - Red Hat solution alignment
   - Partner recommendations

4. **Strategic Ideas & How Might We Statements**
   - 10 solution ideas
   - 15 "How might we..." innovation prompts

5. **Account Team & Partner Onboarding**
   - Key stakeholders
   - Decision makers
   - Engagement strategy

6. **Comprehensive Red Hat Account Plan**
   - Complete account overview
   - Actionable recommendations
   - Next steps

---

## System Architecture

```
┌─────────────────────┐
│   Google Drive      │ ← Client documents
│   (Client Folders)  │
└──────────┬──────────┘
           │
           ↓ Download
┌─────────────────────┐
│   Project APE       │
│   (Podman Container)│
│                     │
│  • Download docs    │
│  • Consolidate PDF  │
│  • Upload to NLM    │
│  • AI Analysis      │
└──────────┬──────────┘
           │
           ↓ Create notebooks
┌─────────────────────┐
│   NotebookLM        │ ← Analysis results
│   (Google Cloud)    │
└─────────────────────┘
```

**Technology Stack:**
- **Container:** Podman (or Docker)
- **Runtime:** Python 3.14
- **AI:** Google Gemini
- **Storage:** NotebookLM
- **Auth:** Google Cloud Service Account

---

## Configuration

### vars.py - Client List

```python
clients = [
    "acme_corp",
    "globex_industries",
    "initech"
]

# Client details
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

globex_industries_name = "Globex Industries"
globex_industries_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

initech_name = "Initech"
initech_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"

# Optional: Customize persona
persona = "Red Hat solutions architect"
```

### .env - Environment Variables

**Auto-generated** by `create-service-account.sh`:

```bash
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
GCP_PROJECT_ID=your-project-id
SERVICE_ACCOUNT_EMAIL=project-ape-service@your-project.iam.gserviceaccount.com
```

---

## Execution Modes

### Fast Mode (Recommended)
```bash
./launch_ape.sh fast
```
- **Time:** 15-20 minutes per client
- **Best for:** Regular account planning
- **Coverage:** Comprehensive analysis

### Deep Mode
```bash
./launch_ape.sh deep
```
- **Time:** 35-40 minutes per client
- **Best for:** Strategic accounts, initial analysis
- **Coverage:** More thorough research

### Specific Clients
```bash
./launch_ape.sh fast acme_corp globex_industries
```
- Runs only specified clients
- Useful for testing or updates

---

## Monitoring

### Dashboard
```bash
open http://localhost:8765
```

Shows:
- Current progress
- Client status
- Processing logs
- Estimated completion time

### Container Logs
```bash
# Podman
podman ps
podman logs <container-id>

# Docker
docker ps
docker logs <container-id>
```

---

## Common Tasks

### Update Existing Client
```bash
# Re-run analysis for one client
./launch_ape.sh fast client_name
```

### Add New Client
```bash
# 1. Edit vars.py
nano vars.py

# 2. Add new client entry
new_client_name = "New Client Inc"
new_client_folder = "https://drive.google.com/..."

# 3. Add to clients list
clients = [..., "new_client"]

# 4. Share Drive folder with service account

# 5. Run analysis
./launch_ape.sh fast new_client
```

### Re-authenticate NotebookLM
```bash
source ./activate-ape-env.sh
notebooklm login
./setup-credentials.sh
```

### Regenerate Service Account
```bash
./create-service-account.sh
# Then re-share Drive folders
```

---

## Troubleshooting

### "notebooklm: command not found"
**Cause:** Virtual environment not activated  
**Solution:**
```bash
source ./activate-ape-env.sh
notebooklm --version
```

### "No permission to access Drive folder"
**Cause:** Drive folder not shared with service account  
**Solution:**
```bash
# 1. Get service account email
grep SERVICE_ACCOUNT_EMAIL .env

# 2. Share Drive folder
#    - Right-click folder in Drive → Share
#    - Add service account email
#    - Set permission to "Viewer"
```

### "Podman/Docker connection refused"
**macOS Podman:**
```bash
podman machine list
podman machine start
```

**Docker:**
```bash
open -a Docker
# Wait for Docker to start
docker ps
```

### "Rate limit exceeded"
**Cause:** Too many API calls to Gemini  
**Solution:** Wait 60 seconds and the script will auto-retry

---

## File Structure

```
Project-APE/
├── setup.sh                      # ⭐ Unified setup script
├── setup-environment.sh          # Install tools
├── create-service-account.sh     # GCP service account
├── setup-credentials.sh          # Container credentials
├── launch_ape.sh                 # Run the pipeline
│
├── vars.py                       # Client configuration
├── .env                          # Environment variables
├── service-account-key.json      # GCP credentials (gitignored)
│
├── activate-ape-env.sh           # Activate venv
│
├── core/                         # Python pipeline code
│   ├── client_pipeline.py
│   ├── gemini_agent.py
│   ├── notebook_manager.py
│   └── ...
│
├── dashboard/                    # Progress dashboard
│
├── logs/                         # Execution logs
│
└── README.md                     # This file
```

---

## Requirements

### System Requirements
- **macOS:** 10.15+ (Catalina or later)
- **Linux:** RHEL 9+, Fedora 38+, Ubuntu 22.04+, Debian 12+
- **RAM:** 8GB minimum, 16GB recommended
- **Disk:** 20GB free space

### Google Cloud
- Google Cloud account
- Billing enabled (free tier sufficient)
- Drive API access

### Google Drive
- Folders with client documents
- Permission to share folders

---

## Security

### Credentials Stored
- `service-account-key.json` - GCP service account (600 permissions)
- `~/.notebooklm/` - NotebookLM authentication
- `.env` - Environment variables

### Best Practices
- ✅ All credential files are in `.gitignore`
- ✅ Service account has minimal permissions (Viewer only)
- ✅ Keys stored locally, not in cloud
- ✅ 600 permissions on service account key

### Never Commit
- `service-account-key.json`
- `.env`
- `vars.py` (if contains sensitive data)

---

## Support

### Documentation
- **README.md** - This file
- **SETUP.md** - Detailed setup guide
- **TROUBLESHOOTING.md** - Common issues

### Getting Help
1. Check logs: `./logs/`
2. Check dashboard: `http://localhost:8765`
3. Review TROUBLESHOOTING.md
4. Check GitHub issues

---

## Advanced Configuration

### Custom Persona
Edit `vars.py`:
```python
persona = "Strategic account executive"
# or
persona = "Technical solutions architect"
```

### Drive API Caching
Enable/disable Drive caching in `config.py`:
```python
DRIVE_CONFIG = {
    'cache_enabled': True,  # False to always re-download
    'cache_ttl_hours': 24
}
```

### Timing Configuration
Adjust in `config.py`:
```python
TIMINGS = {
    'after_source_add': 15,      # Seconds after adding source
    'after_mindmap': 60,         # Seconds after mind map
    # ...
}
```

---

## Performance

### Expected Duration

| Clients | Fast Mode | Deep Mode |
|---------|-----------|-----------|
| 1       | 15-20 min | 35-40 min |
| 3       | 45-60 min | 2+ hours  |
| 5       | 1.5-2 hr  | 3+ hours  |

### Optimization Tips
- Use Fast mode for regular updates
- Run overnight for large client lists
- Process specific clients: `./launch_ape.sh fast client1 client2`
- Enable Drive caching to skip re-downloads

---

## License

[Your license here]

## Credits

Powered by:
- Google Gemini AI
- NotebookLM
- Podman/Docker
- Python 3

---

**Version:** 3.0.6  
**Last Updated:** June 2026
