# Project APE - Account Planning Engine

**AI-Powered Enterprise Account Planning Automation**

**Version:** 3.0.5  
**Created by:** Jason Anderson  
**Powered by:** Claude AI & Google NotebookLM

---

## What is Project APE?

Project APE (Account Planning Engine) automates the creation of comprehensive account planning research for enterprise clients using AI. It combines Google NotebookLM's deep research capabilities with Claude AI orchestration to generate detailed account intelligence.

### What It Does

- **Automates Research:** Downloads company materials from Google Drive
- **Consolidates Documents:** Converts all files to a single PDF per client
- **Generates Intelligence:** Creates 40+ research sources and 6 detailed analysis notes
- **Produces Deliverables:** Complete NotebookLM notebooks with mind maps
- **Parallel Processing:** Handles up to 6 clients simultaneously

### Key Features

- ✅ **Google Drive Integration** - All data pulled from Google Drive folders
- ✅ **Multi-Architecture Support** - Works on ARM64 (Mac) and x86_64 (Linux)
- ✅ **Container-Based** - Consistent environment across all platforms  
- ✅ **Real-Time Dashboard** - Monitor progress at http://localhost:8765
- ✅ **Dual Execution Modes** - Fast (15-20 min) or Deep (35-40 min)

---

## Quick Start

### Prerequisites

1. **Google Service Account** - For Drive access (see [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md))
2. **Google Gemini API Key** - For AI orchestration
3. **NotebookLM Access** - Google account with NotebookLM enabled
4. **Container Runtime** - Podman or Docker installed

### Run Project APE

```bash
# 1. Clone repository
git clone <repository-url>
cd Project-APE

# 2. Configure environment
cp .env.template .env
# Edit .env and add your API keys

# 3. Setup clients in vars.py
cp example-vars.py vars.py
# Add your Google Drive folder URLs

# 4. Run pipeline
./launch_ape.sh fast

# 5. Monitor dashboard
open http://localhost:8765
```

**That's it!** Project APE will:
- Auto-detect your architecture (ARM64/x86_64)
- Pull the correct container image from Quay.io
- Download files from Google Drive
- Consolidate to PDF
- Generate research and analysis
- Create complete NotebookLM notebooks

---

## Architecture

```
┌─────────────────────────────────────────┐
│  launch_ape.sh (Launcher)               │
│  • Auto-detects architecture            │
│  • Pulls correct container image        │
│  • Starts dashboard + pipeline          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Container Image (Debian-based)         │
│  • ARM64: quay.io/.../project-ape:arm64 │
│  • x86_64: quay.io/.../project-ape:amd64│
│  • Includes LibreOffice, Python 3.13    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Google Drive Integration                │
│  • Service account authentication       │
│  • Download PDFs from Drive folders     │
│  • Convert Office files to PDF          │
│  • Cache for faster subsequent runs     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  NotebookLM Pipeline                     │
│  • Upload consolidated PDF               │
│  • Generate 2 deep research prompts     │
│  • Create 6 analysis notes               │
│  • Generate mind map                     │
│  • Quality scoring >8.5/10               │
└─────────────────────────────────────────┘
```

---

## Data Flow

**All data comes from Google Drive - no local files needed!**

1. **Google Drive Setup**
   - Create folder per client
   - Upload company PDFs and documents
   - Share folder with service account

2. **vars.py Configuration**
   ```python
   merck_test_folder = "https://drive.google.com/drive/folders/FOLDER_ID"
   ```

3. **Automatic Processing**
   - Container downloads files from Drive
   - Converts to PDF if needed
   - Consolidates into single PDF
   - Uploads to NotebookLM
   - Generates research

4. **Output**
   - NotebookLM notebook with 40+ sources
   - 6 comprehensive analysis notes
   - Interactive mind map
   - Quality score report

---

## Execution Modes

### Fast Mode (15-20 minutes)
```bash
./launch_ape.sh fast
```
- Research timeout: 10 minutes
- Target: 15+ sources
- Quality threshold: 8.5/10
- Best for: Quick turnaround

### Deep Mode (35-40 minutes)
```bash
./launch_ape.sh deep
```
- Research timeout: 20 minutes
- Target: 40+ sources
- Quality threshold: 9.0/10
- Best for: Comprehensive analysis

---

## Documentation

- **[GETTING-STARTED.md](GETTING-STARTED.md)** - Complete setup guide
- **[SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)** - Google Drive authentication
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **[TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)** - Common issues

---

## System Requirements

### Minimum
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB free
- **Network:** Broadband internet

### Recommended
- **CPU:** 6-8 cores (for parallel processing)
- **RAM:** 8-12 GB
- **Disk:** 20 GB free

### Supported Platforms
- ✅ macOS (ARM64 - M1/M2/M3)
- ✅ Linux x86_64 (RHEL, Ubuntu, Fedora)
- ✅ Windows WSL2

---

## Project Structure

```
Project-APE/
├── launch_ape.sh              # Main launcher (auto-detects architecture)
├── vars.py                    # Client configuration (Google Drive URLs)
├── .env                       # API keys (Gemini, optional Claude)
│
├── core/                      # Core modules
│   ├── client_pipeline.py     # Main pipeline orchestration
│   ├── drive_manager.py       # Google Drive integration
│   ├── gemini_agent.py        # AI orchestration
│   └── ...                    # Additional core modules
│
├── dashboard/                 # Real-time monitoring
│   └── server.py              # Flask dashboard
│
└── Containerfile              # Container image definition
```

---

## Google Drive Workflow

### 1. Create Service Account
See [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)

### 2. Organize Drive Folders
```
Client Folders/
├── Merck/
│   ├── company_overview.pdf
│   ├── financial_report.pdf
│   └── technical_specs.pdf
│
└── Blue Yonder/
    ├── about.pdf
    └── products.pdf
```

### 3. Share with Service Account
- Right-click folder → Share
- Add service account email
- Grant "Viewer" permission

### 4. Configure vars.py
```python
merck_test_folder = "https://drive.google.com/drive/folders/1zi3Jbvv..."
blue_yonder_test_folder = "https://drive.google.com/drive/folders/1Gno..."
```

### 5. Run Pipeline
```bash
./launch_ape.sh fast
```

**Project APE handles everything else automatically!**

---

## Multi-Architecture Support

Project APE automatically detects your system architecture and uses the appropriate container image:

| Platform | Architecture | Container Image | LibreOffice |
|----------|-------------|-----------------|-------------|
| **macOS M1/M2/M3** | ARM64 | `project-ape:latest-arm64` | ✅ Yes |
| **Linux Intel/AMD** | x86_64 | `project-ape:latest-amd64` | ✅ Yes |
| **Windows WSL2** | x86_64 | `project-ape:latest-amd64` | ✅ Yes |

**No manual configuration needed** - `launch_ape.sh` handles detection automatically.

---

## Output

Each client generates:

### NotebookLM Notebook
- **40+ Research Sources** - Web articles, reports, documentation
- **1 Consolidated PDF** - All client materials combined
- **6 Analysis Notes:**
  1. Industry Analysis & Future Trends
  2. Customer Business Profile
  3. Technical Landscape Assessment
  4. Opportunity Assessment
  5. Strategic Recommendations
  6. Executive Summary
- **Interactive Mind Map** - Visual representation of findings
- **Quality Score** - Automated assessment (target: >8.5/10)

### Local Outputs
- **Logs:** `logs/<client_id>.log`
- **Status:** `.multi_process_status/<client_id>.json`
- **Dashboard:** Real-time monitoring at http://localhost:8765

---

## Performance

### Benchmarks

| Mode | Single Client | 6 Clients Parallel | Sources | Quality |
|------|--------------|-------------------|---------|---------|
| **Fast** | 15-20 min | 20-25 min | 15-40 | 8.5+ |
| **Deep** | 35-40 min | 40-45 min | 40-70 | 9.0+ |

### Success Rate
- **100%** with Claude AI orchestration
- Self-healing error recovery
- Automatic retry logic

---

## API Keys Required

### Required
1. **Google Gemini API** - AI orchestration
   - Get at: https://aistudio.google.com/app/apikey
   - Used for: Industry detection, orchestration

2. **Google Service Account** - Drive access
   - Setup: [SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)
   - Used for: Downloading client materials

### Optional
3. **Claude via Vertex AI** - Industry auto-detection
   - Enhances industry classification
   - Falls back to Gemini if not configured

---

## Technology Stack

- **Python 3.13** - Core runtime
- **NotebookLM CLI** - Research and notebook management
- **Google Gemini AI** - Orchestration and analysis
- **Google Drive API** - Document retrieval
- **Flask** - Real-time dashboard
- **Debian 12** - Container base image
- **LibreOffice** - Document conversion
- **Podman/Docker** - Container runtime

---

## License

Created, developed, and maintained by **Jason Anderson**.

All rights reserved.

---

## Support

For issues or questions, contact **Jason Anderson**.

---

**Project APE - Making Enterprise Account Planning Effortless**
