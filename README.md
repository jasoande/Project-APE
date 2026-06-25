# Project APE - Account Planning Engine

**Automated account research and planning using Google NotebookLM and AI orchestration**

✨ **95% browser-accessible** - No terminal needed for daily operations

[![Version](https://img.shields.io/badge/version-3.2.2-blue.svg)](https://github.com/yourusername/project-ape)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🌐 Web-First Experience

**Launch your research in 5 clicks:**

1. Open your browser → `http://localhost:8765/configure`
2. Click "Setup Environment" → Automated installation (2-5 min)
3. Click "Login to NotebookLM" → Authenticate with Google
4. Click "Google Drive Setup" → 5-step wizard (one-time, 5 min)
5. Fill in client form → Click "Start Workflow" → Done!

**Monitor in real-time:** Live dashboard with progress tracking, quality scores, and instant access to results.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start (Browser-Based)](#quick-start-browser-based)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Web Configuration](#web-configuration)
- [Dashboard](#dashboard)
- [Execution Modes](#execution-modes)
- [Troubleshooting](#troubleshooting)
- [Advanced: Command Line Usage](#advanced-command-line-usage)
- [Architecture Details](#architecture-details)
- [Contributing](#contributing)

---

## 🎯 Overview

Project APE (Account Planning Engine) automates comprehensive account research by:
1. Downloading documents from Google Drive folders
2. Creating Google NotebookLM notebooks
3. Uploading sources and analyzing content
4. Generating structured account plans with quality scoring
5. Providing real-time monitoring via web dashboard

**Use Cases:**
- Sales teams researching enterprise accounts
- Solutions architects preparing for customer meetings
- Account executives developing strategic plans
- Business development teams analyzing prospects

**Key Benefits:**
- 🌐 **Web-First**: 95%+ browser-accessible, no terminal needed
- ⚡ **Fast**: 15-20 minutes per account (parallel execution)
- 🎯 **Accurate**: AI-powered industry detection and quality scoring
- 📊 **Transparent**: Real-time dashboard with progress tracking
- 🔄 **Scalable**: Process multiple accounts concurrently
- 🐳 **Portable**: Containerized for consistent deployment

---

## 🚀 Quick Start (Browser-Based)

**No terminal commands required! Complete setup and execution from your browser.**

### Step 1: Launch the Dashboard (30 seconds)

Double-click `launch-project-ape.command` in Finder (macOS) or run the launcher script.

Your browser automatically opens to: `http://localhost:8765/configure`

![Configuration Page](Docs/screenshots/configure-page.png)

### Step 2: Setup Environment (2-5 minutes)

1. On the configuration page, click **"Setup Environment"**
2. Watch automated installation progress:
   - Python virtual environment creation
   - NotebookLM CLI installation
   - Required dependencies
3. Wait for green checkmark: ✅ **Environment Ready**

![Setup Environment](Docs/screenshots/setup-environment.png)

### Step 3: Authenticate NotebookLM (1 minute)

1. Click **"Login to NotebookLM"**
2. Browser opens → Sign in with your Google account
3. Grant NotebookLM permissions
4. Return to dashboard → See ✅ **Authenticated**

![Auth Status](Docs/screenshots/auth-status.png)

### Step 4: Setup Google Drive Access (5 minutes, one-time)

Click **"Google Drive Setup"** to launch the OAuth wizard:

1. **Step 1**: Click "Open Google Cloud Console" → Create project
2. **Step 2**: Enable Google Drive API (one-click)
3. **Step 3**: Configure OAuth consent screen
4. **Step 4**: Create OAuth credentials → Download JSON
5. **Step 5**: Upload JSON file → Authenticate

![OAuth Wizard](Docs/screenshots/oauth-wizard.png)

**That's it!** Drive access configured. You'll never need to repeat this.

### Step 5: Configure Your Clients (3 minutes)

In the web form, add your first client:

- **Client Name**: `Acme Corporation`
- **Google Drive Folder**: Paste folder URL from Drive
- **Industry**: Leave blank for auto-detection
- **Subsegments**: Optional (e.g., "cloud, AI/ML")

Click **"➕ Add Client"** to add more.

### Step 6: Launch Your First Workflow (1 minute)

1. Review your configuration
2. Select execution mode: **Fast** (15-20 min) or **Deep** (45-60 min)
3. Click **"🚀 Start Workflow"**
4. Dashboard automatically switches to monitoring view

![Dashboard](Docs/screenshots/dashboard-monitoring.png)

### What Success Looks Like

✅ **Live dashboard** shows real-time progress for each client  
✅ **Progress bars** update every 2 seconds  
✅ **Quality scores** appear when complete (e.g., "8.5/10")  
✅ **NotebookLM links** are clickable → Opens your research  
✅ **Status shows** "COMPLETE" with green indicator  

![Completed Workflow](Docs/screenshots/completed-workflow.png)

**Total time from zero to first results: 15-30 minutes**

For detailed step-by-step instructions, see **[QUICK_START.md](QUICK_START.md)**

---

## ✨ Features

### Core Capabilities
- **Multi-Process Architecture**: Process 6 accounts in parallel
- **Dual-Mode Execution**: 
  - Fast mode: 15-20 minutes (all clients)
  - Deep mode: 45-60 minutes (all clients)
- **Automatic Industry Detection**: AI-powered classification using Gemini
- **Quality Scoring**: Automated validation (1-10 scale)
- **Smart Caching**: 7-day Drive cache with selective refresh
- **Error Recovery**: Self-healing with Gemini agent orchestration
- **Real-Time Monitoring**: Live web dashboard with logs

### Dashboard Features
- Live progress tracking per client
- Quality score visualization
- Real-time log streaming
- NotebookLM direct links
- Auto-refresh every 2 seconds
- Collapsible log viewer

### Advanced Features
- **Gemini Agent Mode**: AI-powered error analysis and recovery
- **PDF Consolidation**: Automatic document merging (optional)
- **Update System**: Force refresh Drive cache on demand
- **Web Configuration**: Browser-based client setup
- **Auto-Shutdown**: Container cleanup after completion

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Project APE Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Interface Layer                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Web Dashboard (Flask)                                │  │
│  │  - Real-time progress                                 │  │
│  │  - Live logs                                          │  │
│  │  - Configuration UI                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  Orchestration Layer                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py (Multi-Process Manager)                      │  │
│  │  - Process spawning                                   │  │
│  │  - Status aggregation                                 │  │
│  │  - Resource management                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  Execution Layer (Parallel Processes)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │  │
│  │ Pipeline │  │ Pipeline │  │ Pipeline │  │ Pipeline │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       ↓              ↓              ↓              ↓        │
│  Core Components Layer                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • DriveManager (Download files)                      │  │
│  │  • NotebookManager (NotebookLM API)                   │  │
│  │  • SourceManager (Upload & process)                   │  │
│  │  • GeminiAgent (Error recovery, Quality validation)   │  │
│  │  • QualityScorer (Result validation)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  External Services                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Google Drive API                                   │  │
│  │  • Google NotebookLM                                  │  │
│  │  • Google Gemini API (optional)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User configures clients via web UI or vars.py
2. Main orchestrator spawns parallel client processes
3. Each process downloads files from Google Drive
4. NotebookLM notebooks created and sources uploaded
5. AI prompts executed for research and analysis
6. Quality scoring and validation performed
7. Results aggregated and displayed in dashboard

---

## 📋 Prerequisites

**Everything you need to get started:**

### Required
- **macOS or Linux** system (Intel/Apple Silicon/ARM64)
- **Google Account** with access to:
  - Google Drive (for client documents)
  - Google NotebookLM (free at notebooklm.google.com)
- **10 minutes** for initial setup

### Optional
- Gemini API key (for advanced AI features)

**That's it!** The web interface handles all technical setup automatically.

---

## 🌐 Web Configuration

**All configuration happens in your browser - no command line needed!**

### Access the Configuration Interface

1. **Launch the dashboard:**
   - Double-click `launch-project-ape.command` in Finder (macOS)
   - Or browse to: `http://localhost:8765/configure`

2. **Complete the setup wizard:**
   - Environment setup (automated)
   - NotebookLM authentication (browser-based)
   - Google Drive OAuth (5-step wizard)
   - Client configuration (web form)

3. **Click "Start Workflow"** and monitor in real-time

**See [QUICK_START.md](QUICK_START.md) for detailed browser-based walkthrough**

---

## 📊 Dashboard

The web dashboard provides real-time monitoring at `http://localhost:8765`

### Features

**Header Section:**
- King Kong logo (150x150px)
- Execution timer
- Total/Running/Complete/Failed counts
- Overall progress bar

**Client Cards:**
- Individual progress per client
- Current pipeline phase
- Quality score (1-10)
- NotebookLM direct link
- Status indicators (RUNNING, COMPLETE, FAILED)

**Logs Section (Collapsible):**
- Real-time log streaming
- Pause/Resume controls
- Clear log button
- Download logs
- Auto-scroll with visual indicators

**Auto-Refresh:**
- Updates every 2 seconds
- Continues for 5 minutes after completion
- Graceful shutdown

### Dashboard Routes

```
GET  /                    Main dashboard
GET  /configure           Configuration UI
GET  /launch              Launch confirmation page
GET  /status              JSON status endpoint
GET  /stream-logs         SSE log stream
POST /api/start-workflow  Start pipeline
POST /api/shutdown        Shutdown server
```

---

## ⚡ Execution Modes

### Fast Mode
- **Duration**: 15-20 minutes (all clients in parallel)
- **Best for**: Quick account overviews, initial research
- **Processing delays**: Shorter wait times between operations
- **Quality target**: 8.0/10

### Deep Mode
- **Duration**: 45-60 minutes (all clients in parallel)
- **Best for**: Comprehensive analysis, high-value accounts
- **Processing delays**: Longer processing for better results
- **Quality target**: 8.5/10

### Parallel Execution

Both modes process **all clients in parallel**:

```
Client 1: [====================================] 100%
Client 2: [====================================] 100%
Client 3: [====================================] 100%
Client 4: [====================================] 100%
Client 5: [====================================] 100%
Client 6: [====================================] 100%

Fast Mode Total: 15-20 minutes
Deep Mode Total: 45-60 minutes
```

---

## 💻 Advanced: Command Line Usage

**For power users, automation, and CI/CD pipelines**

The web interface handles 95%+ of use cases. Use command line only for:
- Automated workflows and scripting
- CI/CD pipeline integration
- Advanced debugging
- Custom container configurations

### Installation (Advanced)

<details>
<summary>Click to expand manual installation steps</summary>

#### Step 1: Install Dependencies

**macOS:**
```bash
brew install podman
brew install --cask google-cloud-sdk
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update && sudo apt-get install -y podman
curl https://sdk.cloud.google.com | bash
sudo apt-get install -y python3.11 python3.11-venv python3-pip
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/project-ape.git
cd project-ape
```

#### Step 3: Run Setup Script

```bash
./setup.sh
```

**Expected Time:** 20-30 minutes

</details>

### Command Line Execution

**Container Mode:**

```bash
# Fast mode - all clients
./launch_ape.sh fast

# Deep mode - specific clients
./launch_ape.sh deep acme_corp techstart_inc

# Force refresh Drive cache
./launch_ape.sh fast --refresh
```

**Local Mode:**

```bash
# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Start workflow
python3 main.py --mode fast

# With options
python3 main.py --mode deep --refresh --clients merck organon
```

### Manual Configuration (vars.py)

<details>
<summary>Click to expand manual configuration</summary>

Create `vars.py` from template:

```bash
cp example-vars.py vars.py
```

Edit with your preferred editor:

```python
clients = ["acme_corp", "techstart_inc"]

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/ABC123XYZ"
acme_corp_industry = ""  # Auto-detect
acme_corp_subsegments = ""

persona = "solutions architect"
default_mode = "fast"
DASHBOARD_PORT = 8765
```

See `example-vars.py` for complete configuration options.

</details>

### Google Drive Authentication (CLI)

<details>
<summary>Click to expand OAuth setup via command line</summary>

**OAuth Setup:**

1. Create OAuth credentials at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Download JSON file
3. Save credentials:
   ```bash
   mkdir -p ~/.project-ape
   mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
   ```
4. Authenticate:
   ```bash
   python3 setup-oauth-drive.py
   ```

**Service Account Setup:**

```bash
./create-service-account.sh
```

Then share Drive folders with the service account email.

See [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md) for detailed instructions.

</details>

---

## 🔧 Troubleshooting

**Most issues can be resolved from the web dashboard.**

### Dashboard Indicators

✅ **Green checkmarks** = Everything working  
⚠️ **Yellow warnings** = Attention needed  
❌ **Red errors** = Action required  

### Common Issues

#### 1. NotebookLM Authentication Failed

**Dashboard shows:** ❌ "NotebookLM auth expired"

**Web Solution:**
1. Click **"Login to NotebookLM"** button in dashboard
2. Browser opens → Sign in with Google
3. Grant permissions → Return to dashboard
4. ✅ Should now show "Authenticated"

**Command line alternative:** `notebooklm auth refresh`

#### 2. Google Drive Access Denied

**Dashboard shows:** ❌ "Cannot access Drive folder"

**Web Solution:**
1. Click **"Google Drive Setup"** in dashboard
2. Complete OAuth wizard (5 steps)
3. Re-authenticate if prompted
4. ✅ Should now show "Drive Connected"

**Command line alternative:** Run `python3 setup-oauth-drive.py`

#### 3. Dashboard Won't Load

**Browser shows:** "Connection refused" or "Page not found"

**Solution:**
1. Check if dashboard is running: Look for terminal window
2. If not running: Double-click `launch-project-ape.command`
3. Wait 10 seconds for server to start
4. Refresh browser: `http://localhost:8765`

#### 4. Port 8765 Already in Use

**Dashboard shows:** Error starting server

**Web Solution:**
1. Close any other Project APE instances
2. Restart your browser
3. Re-launch the dashboard

**Command line alternative:** Kill process on port 8765 and restart

#### 5. Workflow Stuck or Not Progressing

**Dashboard shows:** Same progress for 5+ minutes

**Solution:**
1. Check **"📋 Real-Time Logs"** section (click to expand)
2. Look for error messages in red
3. Download logs with **"📥 Download"** button
4. See detailed troubleshooting in [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)

### View Logs from Dashboard

**No terminal needed!**

1. Click **"📋 Real-Time Logs"** to expand log section
2. Logs stream automatically with real-time updates
3. Use **"⏸ Pause"** to stop scrolling
4. Use **"📥 Download"** to save logs for analysis
5. Use **"🗑 Clear"** to reset view

### Getting Help

1. **First**: Check dashboard logs (📋 Real-Time Logs section)
2. **Second**: Review [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
3. **Third**: Open GitHub issue with:
   - Screenshot of dashboard error
   - Downloaded log files (📥 Download button)
   - Browser console errors (F12 → Console tab)

---

## 🏛️ Architecture Details

### Technology Stack

**Backend:**
- Python 3.11+ (core logic)
- Flask 3.0+ (web server)
- Google APIs (Drive, NotebookLM)
- Gemini AI (optional orchestration)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Server-Sent Events (real-time logs)
- Responsive CSS

**Infrastructure:**
- Podman/Docker (containerization)
- Multi-process Python (parallel execution)
- JSON file-based status tracking

### Core Components

#### 1. Client Pipeline (`core/client_pipeline.py`)
Executes complete workflow for single client:
- Download files from Drive
- Create NotebookLM notebook
- Upload sources
- Run research prompts
- Quality validation
- Result storage

#### 2. Drive Manager (`core/drive_manager.py`)
Handles Google Drive interactions:
- OAuth/Service Account authentication
- Recursive folder traversal
- File download with caching
- Google Docs export to PDF
- TTL-based cache management

#### 3. Notebook Manager (`core/notebook_manager.py`)
NotebookLM API wrapper:
- Notebook creation/deletion
- Source upload (PDF, TXT, Google Docs)
- Prompt execution (Ask/Chat)
- Status polling
- Error handling

#### 4. Gemini Agent (`core/gemini_agent.py`)
AI-powered orchestration:
- Industry auto-detection
- Error analysis and recovery
- Quality validation
- Self-healing workflows

#### 5. Quality Scorer (`core/quality_scorer.py`)
Result validation:
- Source count verification
- Note completeness check
- Content quality assessment
- 1-10 scoring scale

### Process Architecture

```
main.py (Orchestrator)
├── Process 1: acme_corp
│   ├── Download Drive files
│   ├── Create NotebookLM
│   ├── Upload sources
│   ├── Run research prompts
│   ├── Quality validation
│   └── Write status.json
├── Process 2: techstart_inc
│   └── (same pipeline)
├── Process 3: globalbank_llc
│   └── (same pipeline)
└── Dashboard (Flask)
    ├── Serve web UI
    ├── Aggregate status files
    ├── Stream logs (SSE)
    └── Handle API requests
```

### File Structure

```
project-ape/
├── main.py                      # Orchestrator
├── launch_ape.sh                # Container launcher
├── launch-project-ape.command   # macOS double-click launcher
├── setup.sh                     # Automated setup
├── vars.py                      # Configuration (user-created)
├── example-vars.py              # Configuration template
├── requirements.txt             # Python dependencies (in developer-docs/)
│
├── core/                        # Core pipeline components
│   ├── client_pipeline.py       # Single client workflow
│   ├── drive_manager.py         # Google Drive integration
│   ├── notebook_manager.py      # NotebookLM API wrapper
│   ├── source_manager.py        # Source upload manager
│   ├── gemini_agent.py          # AI orchestration
│   ├── quality_scorer.py        # Result validation
│   └── update_manager.py        # Cache refresh system
│
├── dashboard/                   # Web interface
│   ├── server.py                # Flask application
│   ├── templates/
│   │   ├── dashboard.html       # Main dashboard
│   │   ├── configure.html       # Configuration UI
│   │   └── launch.html          # Launch confirmation
│   ├── static/
│   │   ├── configure.js         # Configuration logic
│   │   └── kingkong.png         # Logo (150x150px)
│   ├── config_generator.py      # vars.py generator
│   └── config_parser.py         # vars.py parser
│
├── logs/                        # Execution logs (auto-created)
│   ├── overall.log              # Aggregated log
│   ├── acme_corp.log            # Per-client logs
│   └── ...
│
├── .multi_process_status/       # Status files (auto-created)
│   ├── acme_corp.json           # Client status
│   └── ...
│
├── Docs/                        # User documentation
│   ├── TROUBLESHOOTING.md
│   └── WEB_CONFIGURATION_GUIDE.md
│
├── developer-docs/              # Developer documentation
│   ├── requirements.txt         # Python dependencies
│   └── ...
│
└── .project-ape/                # User credentials (in home dir)
    ├── drive_token.json         # OAuth token
    ├── drive_credentials.json   # OAuth client secrets
    └── service-account-key.json # Service account key
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repo
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Create virtual environment
python3 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate

# Install dependencies
pip install -r developer-docs/requirements.txt

# Install NotebookLM CLI
pip install notebooklm-cli

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Test single client
python3 main.py --mode fast --clients test_client
```

### Code Style

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, no jQuery
- **Shell**: ShellCheck compliant

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Google NotebookLM team for the research platform
- Google Gemini team for AI orchestration capabilities
- Open source community for dependencies and tools

---

## 📧 Support

- **Documentation**: [Docs/](Docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/project-ape/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/project-ape/discussions)

---

**Version**: 3.2.2  
**Last Updated**: June 25, 2026  
**Author**: Jason Anderson

---

## Quick Reference Card

```bash
# Setup (one-time)
./setup.sh

# Configure clients
python3 dashboard/server.py
# → Open http://localhost:8765/configure

# Launch workflow
./launch_ape.sh fast                    # All clients, fast mode
./launch_ape.sh deep client1 client2    # Specific clients, deep mode
./launch_ape.sh fast --refresh          # Force cache refresh

# Monitor
# → Dashboard: http://localhost:8765
# → Logs: Click "📋 Real-Time Logs" in dashboard

# Troubleshoot
tail -f logs/overall.log                # View logs
podman ps -a                            # Check containers
notebooklm auth check                   # Verify auth
```

**Need help?** See [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
