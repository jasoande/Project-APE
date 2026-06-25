# Project APE - Account Planning Engine

**Automated account research and planning using Google NotebookLM and AI orchestration**

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/yourusername/project-ape)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Detailed Setup](#detailed-setup)
- [Google Drive Authentication](#google-drive-authentication)
  - [Option 1: OAuth (Recommended)](#option-1-oauth-recommended)
  - [Option 2: Service Account](#option-2-service-account)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dashboard](#dashboard)
- [Execution Modes](#execution-modes)
- [Troubleshooting](#troubleshooting)
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
- ⚡ **Fast**: 15-20 minutes per account (parallel execution)
- 🎯 **Accurate**: AI-powered industry detection and quality scoring
- 📊 **Transparent**: Real-time dashboard with progress tracking
- 🔄 **Scalable**: Process multiple accounts concurrently
- 🐳 **Portable**: Containerized for consistent deployment

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

### System Requirements
- **OS**: macOS (Intel/Apple Silicon) or Linux (x86_64/ARM64)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **Python**: 3.11+ (Python 3.14 recommended)
- **Container Runtime**: Podman or Docker

### Required Accounts
1. **Google Account** with:
   - Access to Google Drive
   - Access to Google NotebookLM (notebooklm.google.com)
   - Google Cloud project (can be created during setup)

2. **Optional**:
   - Gemini API key (for advanced features)

### Network Requirements
- Outbound HTTPS (443) access to:
  - `drive.google.com`
  - `notebooklm.google.com`
  - `generativelanguage.googleapis.com` (Gemini API)
  - `googleapis.com` (Drive API)

---

## 🚀 Installation

### Quick Start

**For macOS/Linux users with Podman installed:**

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Make launcher executable
chmod +x launch-project-ape.command

# Double-click launch-project-ape.command in Finder (macOS)
# Or run: ./launch-project-ape.command
```

The launcher will:
1. Detect if first run and install dependencies
2. Open configuration UI in browser
3. Guide you through setup

### Detailed Setup

#### Step 1: Install Dependencies

**macOS:**
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Podman
brew install podman

# Install Google Cloud SDK
brew install --cask google-cloud-sdk

# Install Python 3.11+
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
# Install Podman
sudo apt-get update
sudo apt-get install -y podman

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Python 3.11+
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

This will:
- Create Python virtual environment
- Install Python dependencies
- Install NotebookLM CLI
- Authenticate with Google services
- Set up Drive credentials (OAuth or Service Account)
- Configure container credentials

**Expected Time:** 20-30 minutes

---

## 🔐 Google Drive Authentication

Project APE needs access to your Google Drive folders to download client documents. You have two options:

### Option 1: OAuth (Recommended)

**Best for:** Personal use, development, small teams

**Advantages:**
- No manual folder sharing required
- Uses your personal Google account
- Easier setup
- More secure (browser-based auth)

#### Setup Steps:

1. **Create OAuth Client ID:**

   Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

   ```
   1. Select your project (or create new)
   2. Click "Create Credentials" → "OAuth client ID"
   3. Application type: "Desktop app"
   4. Name: "Project APE Desktop"
   5. Click "Create"
   6. Download JSON file
   ```

2. **Save Credentials:**

   ```bash
   # Create credentials directory
   mkdir -p ~/.project-ape
   
   # Move downloaded JSON file
   mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
   ```

3. **Authenticate:**

   ```bash
   # Run OAuth setup
   python3 setup-oauth-drive.py
   ```

   This will:
   - Open browser for Google sign-in
   - Request Drive read-only permissions
   - Save token to `~/.project-ape/drive_token.json`

4. **Verify:**

   ```bash
   # Test Drive access
   python3 verify-drive-access.py
   ```

**Token Lifetime:**
- Tokens expire after 7 days of inactivity
- Refresh automatically on first use
- Re-run `setup-oauth-drive.py` if auth fails

---

### Option 2: Service Account

**Best for:** Production, automation, multiple team members

**Advantages:**
- Non-interactive (no browser required)
- Long-lived credentials
- Works in containers/headless environments
- Better for CI/CD pipelines

**Disadvantages:**
- Requires manual folder sharing
- More complex setup

#### Setup Steps:

1. **Create Service Account:**

   ```bash
   ./create-service-account.sh
   ```

   This script will:
   - Create Google Cloud project (or use existing)
   - Enable required APIs
   - Create service account
   - Download key file to `service-account-key.json`

   **Manual alternative:**

   Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)

   ```
   1. Select your project
   2. Click "Create Service Account"
   3. Name: "project-ape-service"
   4. Description: "Service account for Project APE"
   5. Click "Create and Continue"
   6. Skip role assignment (no project-level permissions needed)
   7. Click "Done"
   8. Click on the service account email
   9. Go to "Keys" tab → "Add Key" → "Create new key"
   10. Format: JSON
   11. Click "Create" and save as service-account-key.json
   ```

2. **Share Drive Folders:**

   For each client folder in Google Drive:

   ```
   1. Open Google Drive (drive.google.com)
   2. Right-click on client folder
   3. Click "Share"
   4. Add service account email:
      project-ape-service@YOUR-PROJECT-ID.iam.gserviceaccount.com
   5. Role: "Viewer"
   6. Uncheck "Notify people"
   7. Click "Share"
   ```

   **Important:** The service account email format is:
   ```
   SERVICE-ACCOUNT-NAME@PROJECT-ID.iam.gserviceaccount.com
   ```

3. **Verify:**

   ```bash
   # Test service account access
   python3 verify-drive-access.py --service-account
   ```

---

## ⚙️ Configuration

### Web Configuration (Recommended)

1. **Start Dashboard:**

   ```bash
   # Double-click launch-project-ape.command
   # Or run:
   source ~/.project-ape-venv/bin/activate
   python3 dashboard/server.py
   ```

2. **Open Browser:**

   Navigate to: `http://localhost:8765/configure`

3. **Add Clients:**

   - Click "➕ Add Client"
   - Fill in details:
     - **Name**: `Acme Corporation`
     - **Drive Folder**: `https://drive.google.com/drive/folders/ABC123...`
     - **Industry**: `technology` (optional - auto-detected if blank)
     - **Subsegments**: `cloud, AI/ML` (optional)

4. **Configure Settings:**

   - **Persona**: `solutions architect` (default)
   - **Execution Mode**: `fast` or `deep`
   - **Dashboard Port**: `8765` (default)

5. **Save & Launch:**

   Click "🚀 Save & Launch" to generate `vars.py` and start workflow

---

### Manual Configuration (Advanced)

Create `vars.py` from template:

```bash
cp example-vars.py vars.py
```

Edit `vars.py`:

```python
"""
Project APE Configuration
"""
from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATIONS
# ==============================================================================

clients = [
    "acme_corp",
    "techstart_inc",
]

# --- Acme Corporation ---
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/ABC123XYZ"
acme_corp_industry = "manufacturing"  # Optional - leave empty for auto-detect
acme_corp_subsegments = "aerospace, industrial automation"

# --- TechStart Inc ---
techstart_inc_name = "TechStart Inc"
techstart_inc_folder = "https://drive.google.com/drive/folders/DEF456UVW"
techstart_inc_industry = ""  # Auto-detect
techstart_inc_subsegments = ""  # Auto-detect

# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

persona = "Red Hat solutions architect"  # AI response perspective
default_mode = "fast"  # "fast" or "deep"

# ==============================================================================
# DASHBOARD
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds

# ==============================================================================
# EXECUTION TIMING
# ==============================================================================

# Fast Mode (15-20 min total for all clients in parallel)
TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'deduplication_delay': 20.0,
    'mindmap_delay': 15.0,
    'source_import_wait': 10.0,
}

# Deep Mode (45-60 min total for all clients in parallel)
DEEP_TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 45.0,
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    'deduplication_delay': 25.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 15.0,
}

# ==============================================================================
# GOOGLE DRIVE
# ==============================================================================

DRIVE_CONFIG = {
    'cache_enabled': True,
    'cache_ttl_hours': 168,  # 7 days
    'export_google_docs': True,  # Export Docs/Sheets to PDF
    'recursive': False,  # Don't download subfolders
    'max_file_size_mb': 50,  # Skip files larger than 50MB
}

# ==============================================================================
# GEMINI AI (Optional)
# ==============================================================================

GEMINI_AGENT_CONFIG = {
    'enabled': True,  # Set to False to disable
    'model': 'gemini-2.0-flash-exp',
    'temperature': 0.2,
    'enable_error_analysis': True,
    'enable_quality_validation': True,
    'quality_target': 8.5,
}

# ==============================================================================
# PATHS (Do not modify for container)
# ==============================================================================

STATUS_DIR = Path('/app/.multi_process_status')
LOGS_DIR = Path('/app/logs')
```

---

## 🎮 Usage

### Container Mode (Recommended)

**Start workflow with auto-detection:**

```bash
./launch_ape.sh fast
```

This will:
1. Detect architecture (Intel/ARM)
2. Pull container image
3. Start dashboard at `http://localhost:8765`
4. Launch all clients in parallel
5. Auto-shutdown after 5 minutes

**Specify clients:**

```bash
# Run specific clients
./launch_ape.sh fast acme_corp techstart_inc

# Deep mode
./launch_ape.sh deep acme_corp

# Force refresh Drive cache
./launch_ape.sh fast --refresh
```

**Command Options:**

```bash
./launch_ape.sh {fast|deep} [--refresh] [client1 client2 ...]

Modes:
  fast     Quick research (15-20 minutes total)
  deep     Thorough research (45-60 minutes total)

Options:
  --refresh    Force refresh Google Drive cache (ignore 7-day TTL)

Examples:
  ./launch_ape.sh fast
  ./launch_ape.sh deep --refresh
  ./launch_ape.sh fast acme_corp techstart_inc
```

---

### Local Mode (Development)

**Run without container:**

```bash
# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Start workflow
python3 main.py --mode fast

# Options:
python3 main.py --mode deep --refresh
python3 main.py --mode fast --clients acme_corp
python3 main.py --mode fast --no-dashboard
```

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

## 🔧 Troubleshooting

### Common Issues

#### 1. NotebookLM Authentication Failed

**Symptoms:**
```
ERROR: NotebookLM authentication expired
```

**Solution:**
```bash
# Refresh credentials
notebooklm auth refresh

# Or re-authenticate
notebooklm auth login
```

#### 2. Google Drive Access Denied

**OAuth:**
```bash
# Re-run OAuth setup
python3 setup-oauth-drive.py
```

**Service Account:**
```
1. Verify service account email in Drive folder share settings
2. Check folder permissions (must be "Viewer" or higher)
3. Ensure folder ID is correct in vars.py
```

#### 3. Container Won't Stop

**Symptoms:**
Container remains running after workflow completes

**Solution:**
```bash
# Auto-shutdown is now enabled (5 minutes after completion)
# Or manually stop:
podman stop project-ape

# Force remove:
podman rm -f project-ape
```

#### 4. Rocket Ship Still Shows on Launch Page

**Cause:** Browser cache

**Solution:**
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or restart Flask server and refresh normally

#### 5. Port 8765 Already in Use

**Solution:**
```bash
# Find process using port
lsof -i :8765

# Kill process
kill -9 <PID>

# Or change port in vars.py:
DASHBOARD_PORT = 8766
```

### Debug Mode

**Enable verbose logging:**

```bash
# Container mode
./launch_ape.sh fast --debug

# Local mode
python3 main.py --mode fast --log-level DEBUG
```

**Check logs:**

```bash
# View client logs
tail -f logs/acme_corp.log

# View overall logs
tail -f logs/overall.log

# Download from dashboard
# Click "📥 Download" in Logs section
```

### Getting Help

1. Check [Troubleshooting Guide](Docs/TROUBLESHOOTING.md)
2. Review logs in `logs/` directory
3. Check container logs: `podman logs project-ape`
4. Open GitHub issue with:
   - Error message
   - Log snippets
   - System info (`uname -a`, `python --version`)

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

**Version**: 3.2.0  
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
