# PROJECT APE - Technical Overview

<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="150"/>
</div>

---

## Executive Summary

**Project APE** (Account Planning Engine) is an enterprise AI automation platform that transforms account planning from a multi-day manual process into an automated 15-60 minute workflow powered by Google's NotebookLM platform.

**Key Differentiator:** 100% GUI-driven user experience—no command-line knowledge required.

---

## Business Value Proposition

### Problem Solved

Traditional enterprise account planning requires:
- **Time**: 3-5 days per account (manual research)
- **Resources**: Multiple analysts and researchers
- **Inconsistency**: Variable quality based on analyst experience
- **Scalability**: Limited to 2-3 accounts per week per team

### Solution Delivered

Project APE delivers:
- **Speed**: 15-20 minutes (fast) or 45-60 minutes (deep) per account
- **Automation**: Single-click launch, zero manual intervention
- **Quality**: AI-powered analysis with 90-400+ source citations
- **Scale**: Process 5 accounts in parallel simultaneously

### ROI Impact

- **Time Savings**: 95% reduction in research time
- **Cost Efficiency**: 1 automation platform vs. team of analysts
- **Coverage**: 5-10x more accounts researched per week
- **Quality**: Consistent framework across all accounts

---

## User Workflow (GUI-First Experience)

```
┌─────────────────────────────────────────┐
│         USER JOURNEY (GUI-ONLY)         │
└─────────────────────────────────────────┘

1. LAUNCH
   ├─ Double-click launch-project-ape.py
   └─ Browser opens to http://localhost:8765
          ↓
2. CONFIGURE (Web Interface)
   ├─ Add clients (name, Drive folder URL)
   ├─ Authenticate NotebookLM (OAuth)
   └─ Authenticate Google Drive (OAuth)
          ↓
3. START WORKFLOW
   ├─ Click "Launch Workflows" button
   └─ Select execution mode (Fast/Deep)
          ↓
4. MONITOR (Real-Time Dashboard)
   ├─ Live progress bars per client
   ├─ Real-time log streaming
   └─ Quality scores on completion
          ↓
5. REVIEW OUTPUTS
   ├─ NotebookLM notebooks (6 analysis notes each)
   ├─ Mind maps and visualizations
   └─ Quality reports (1-10 scale)
```

**Critical Design Principle:** Zero terminal commands for end users. Everything is point-and-click.

---

## Technical Architecture

### System Components

```
┌──────────────────────────────────────────────────┐
│           PROJECT APE ARCHITECTURE                │
└──────────────────────────────────────────────────┘

User Interface Layer:
    Web Browser (Chrome/Firefox)
         ↓ HTTP
    Flask Dashboard Server (Port 8765)
         ├─ /configure (Setup wizard)
         ├─ / (Monitoring dashboard)
         └─ /api/* (RESTful endpoints)
         ↓
Orchestration Layer:
    main.py (Multi-Process Manager)
         ├─ Spawns client pipeline processes
         ├─ Manages status tracking
         └─ Parallel execution (up to 5 clients)
         ↓
Execution Layer (Per-Client Processes):
    core/client_pipeline.py
         ├─ Phase 1: Drive download (30-60s)
         ├─ Phase 2: Notebook creation (10-15s)
         ├─ Phase 3: AI research (3-8 min)
         ├─ Phase 4: AI analysis (8-12 min)
         └─ Phase 5: Quality validation (1-2 min)
         ↓
External Services:
         ├─ Google Drive API (document storage)
         ├─ Google NotebookLM (AI research)
         └─ Google Gemini (optional orchestration)
```

### Core Modules

| Module | Responsibility |
|--------|----------------|
| `launch-project-ape.py` | **Primary entry point** - Cross-platform GUI launcher |
| `dashboard/server.py` | Flask web server - Configuration UI, monitoring dashboard |
| `main.py` | Multi-process orchestrator - Spawns client pipelines |
| `core/client_pipeline.py` | Single-client workflow executor - 5 sequential phases |
| `core/drive_manager.py` | Google Drive integration - Download, cache, sync |
| `core/notebook_manager.py` | NotebookLM API wrapper - Create, find, manage notebooks |
| `core/source_manager.py` | Research execution - Upload PDFs, run queries |
| `core/quality_scorer.py` | Output validation - 1-10 quality scoring |
| `core/gemini_agent.py` | AI orchestration (optional) - Quality monitoring |

---

## Pipeline Workflow

### Five Sequential Phases

**Phase 1: Document Download (30-60 seconds)**
- Connect to Google Drive via OAuth
- Download PDFs and Google Docs from configured folder
- Convert all formats to PDF
- Smart caching (7-day TTL, change detection)

**Phase 2: Notebook Creation (10-15 seconds)**
- Check for existing notebook (deduplication)
- Create NotebookLM notebook if needed
- Upload consolidated PDF source
- Wait for source processing

**Phase 3: Research - Ask Prompts (3-8 minutes)**
- Execute 2 AI research queries
- Import 20-90 external web sources (mode-dependent)
- Analyze industry trends and competitive landscape
- Deduplicate sources

**Phase 4: Analysis - Chat Prompts (8-12 minutes)**
- Execute 6 consolidated analysis prompts:
  - Industry analysis & business profile
  - Innovation assessment & executive summary
  - Technology partners & value propositions
  - Strategic ideas & opportunities
  - Account team & partner onboarding
  - Comprehensive account plan
- Generate structured notes in NotebookLM

**Phase 5: Quality Validation (1-2 minutes)**
- Validate completeness (sources, notes, outputs)
- Calculate quality score (1-10 scale)
- Generate mind map visualization
- Create summary reports

### Execution Modes

| Mode | Duration | Sources | Use Case |
|------|----------|---------|----------|
| **Fast** | 15-20 min | 40-80 | Quick turnaround, initial research |
| **Deep** | 45-60 min | 200-500 | Comprehensive analysis, strategic accounts |

---

## Integration Points

### 1. Google NotebookLM

**Purpose:** Core AI research and analysis engine

**Integration Method:**
- CLI wrapper: `notebooklm` command (notebooklm-py package)
- Authentication: OAuth2 (`~/.notebooklm/credentials.json`)

**Operations:**
- Create notebooks
- Upload PDF sources
- Execute research queries (web source import)
- Generate analysis notes
- Create mind map visualizations

### 2. Google Drive API

**Purpose:** Document storage and synchronization

**Integration Method:**
- Python client: `google-api-python-client`
- Authentication: OAuth2 Application Default Credentials

**Features:**
- Download PDFs from shared folders
- Convert Google Docs/Sheets to PDF
- Smart caching with change detection
- 7-day TTL (configurable)

### 3. Google Gemini AI (Optional)

**Purpose:** Advanced orchestration and quality monitoring

**Integration Method:**
- Direct API: `google-generativeai` SDK
- Model: `gemini-2.0-flash-exp`

**Use Cases:**
- Industry/subsegment auto-detection
- Quality score prediction
- Error recovery and retry logic

---

## Deployment Models

### 1. Local GUI Mode (Default)

**Launch:** Double-click `launch-project-ape.py`

**Characteristics:**
- Zero CLI required
- Auto-setup virtual environment
- Dashboard runs in background
- Cross-platform (Windows/macOS/Linux)

**When to Use:**
- First-time users
- Development and testing
- Single-machine deployments

### 2. Container Mode (Advanced)

**Launch:** `./developer-docs/ape-run.sh --vars ./vars.py --clients client1 --mode fast`

**Characteristics:**
- Reproducible container image
- Multi-architecture (amd64/arm64)
- Isolated from host dependencies
- Registry: `quay.io/jasoande/project_ape/project-ape:4.0.1`

**When to Use:**
- Production deployments
- Scheduled automation (cron)
- Cloud environments
- Shared infrastructure

---

## Configuration System

### vars.py (Auto-Generated)

Generated by web UI, contains:
- Client definitions (`clients = ["acme", "techstart"]`)
- Per-client settings (name, industry, Drive folder URL)
- Global settings (persona, execution mode, port)
- Timing configurations (fast vs. deep mode)

**Example:**
```python
clients = ["acme_corp"]

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/ABC123"
acme_corp_industry = ""  # Auto-detect
acme_corp_subsegments = "cloud, AI/ML, DevOps"

persona = "solutions architect"
default_mode = "fast"
```

### Web Configuration Interface

**Pages:**
- `/configure` - Setup wizard (add clients, authenticate)
- `/launch` - Workflow trigger (preview and start)
- `/` - Monitoring dashboard (real-time progress)

**API Endpoints:**
- `/api/save-config` - Generate vars.py
- `/api/start-workflow` - Trigger main.py execution
- `/api/status` - Get real-time status
- `/api/logs/<client_id>` - Stream logs (SSE)

---

## Extension Points for Developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed developer documentation.

**Key Extension Points:**
1. Custom prompts (`ask_*.txt`, `chat_prompt_*.txt`)
2. Custom pipeline modules (`core/custom_analyzer.py`)
3. Quality score customization (`core/client_pipeline.py`)
4. Dashboard routes and UI (`dashboard/server.py`, `dashboard/templates/`)
5. Container customization (`Containerfile.custom`)

---

## Performance Characteristics

**Throughput:**
- Fast mode: 15-20 minutes per client
- Deep mode: 45-60 minutes per client
- Parallel: 5 clients simultaneously

**Scalability:**
- Process-based parallelism (multi-core)
- Isolated client pipelines (failure doesn't cascade)
- Staggered startup (anti-thundering-herd)

**Resource Usage:**
- Memory: ~500MB per client process
- Disk: ~50MB per client (cache + outputs)
- Network: Variable (research phase is network-intensive)

---

## Quality Assurance

**Quality Scoring (1-10 scale):**
- Source count validation
- Completeness checks (notes, artifacts)
- Citation coverage analysis

**Factors Affecting Quality:**
- Number of sources imported (more = better)
- PDF relevance and quality
- Industry specificity
- Execution mode (Deep > Fast)

---

## Security and Privacy

**Authentication:**
- OAuth2 for Google services (no embedded secrets)
- Credentials stored locally (`~/.notebooklm`, `~/.project-ape`)
- Token refresh automatic

**Data Privacy:**
- Client data never leaves your machine (except to Google services)
- No third-party analytics or tracking
- Logs stored locally only

**Container Security:**
- Non-root execution (UID 1000)
- Read-only volume mounts for input data
- Isolated filesystem namespace

---

## Troubleshooting

See [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) for comprehensive troubleshooting guide.

**Common Issues:**
- Dashboard won't open → Check port 8765, firewall
- Authentication failed → Re-run OAuth flow, check credentials
- Workflow stuck → Review logs, check internet connection, verify quotas
- Low quality score → Switch to deep mode, add more source documents

---

## Additional Documentation

- [README.md](README.md) - Main project overview
- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start
- [CLAUDE.md](CLAUDE.md) - Developer technical documentation
- [Docs/USER_GUIDE.md](Docs/USER_GUIDE.md) - Complete user manual
- [Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md) - Detailed architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer contribution guide

---

<div align="center">

**Project APE v4.0.1**

*Transforming Account Research from Days to Minutes*

[GitHub](https://github.com/yourusername/Project-APE-dev) | [Documentation](Docs/) | [Issues](https://github.com/yourusername/Project-APE-dev/issues)

</div>
