<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # Architecture Documentation
  **Project APE - Account Planning Engine**
  
  Version 4.0.1 | June 30, 2026
</div>

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Overview](#component-overview)
4. [Data Flow](#data-flow)
5. [Multi-Process Execution Model](#multi-process-execution-model)
6. [Status Tracking and Dashboard](#status-tracking-and-dashboard)
7. [Container Architecture](#container-architecture)
8. [Security Model](#security-model)
9. [Technology Stack](#technology-stack)
10. [Design Decisions](#design-decisions)

---

## System Overview

Project APE is a **multi-process, containerized Python application** that orchestrates AI-powered account research using Google NotebookLM. The architecture is designed for:

- **Parallel execution**: Process multiple accounts simultaneously
- **Real-time monitoring**: Web dashboard with live progress tracking
- **Containerized deployment**: Consistent execution across platforms
- **OAuth security**: No embedded credentials or API keys
- **Fault tolerance**: Retry logic, graceful degradation, error recovery

### Key Architectural Principles

1. **Process Isolation**: Each client runs in independent Python process
2. **Stateless Execution**: No shared memory between processes
3. **File-Based IPC**: JSON status files for inter-process communication
4. **Container-First**: Primary deployment target is containerized
5. **API-Driven**: All NotebookLM interactions via official SDK

---

## Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CLI Launcher            Web Dashboard (Flask)       Container Runtime  │
│  ./ape-run.sh    ←────→  http://localhost:8765  ←→   podman/docker     │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  main.py (Multi-Process Orchestrator)                                   │
│  ├─ ProcessManager: Lifecycle, status tracking, cleanup                 │
│  ├─ Flask Dashboard Server (background process)                         │
│  └─ Client Pipeline Processes (1-5 parallel)                            │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        EXECUTION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Process 1   │  │  Process 2   │  │  Process N   │                  │
│  │  Client A    │  │  Client B    │  │  Client N    │                  │
│  │              │  │              │  │              │                  │
│  │  Pipeline:   │  │  Pipeline:   │  │  Pipeline:   │                  │
│  │  1. Download │  │  1. Download │  │  1. Download │                  │
│  │  2. Notebook │  │  2. Notebook │  │  2. Notebook │                  │
│  │  3. Research │  │  3. Research │  │  3. Research │                  │
│  │  4. Analysis │  │  4. Analysis │  │  4. Analysis │                  │
│  │  5. Validate │  │  5. Validate │  │  5. Validate │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                 │                           │
│         └─────────────────┴─────────────────┘                           │
│                           │                                              │
│                  Writes status.json                                      │
│                           ↓                                              │
│              .multi_process_status/                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        CORE COMPONENTS                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  DriveManager    │  │ NotebookManager  │  │  SourceManager   │      │
│  │  • OAuth auth    │  │  • Create NB     │  │  • Upload PDFs   │      │
│  │  • Download PDFs │  │  • Find by name  │  │  • Research      │      │
│  │  • Cache (7-day) │  │  • Delete        │  │  • Parse results │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  GeminiAgent     │  │  QualityScorer   │  │  AuthManager     │      │
│  │  • Auto-detect   │  │  • Validate      │  │  • Check creds   │      │
│  │  • Error recovery│  │  • Score 1-10    │  │  • Fail fast     │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Google Drive    │  │  NotebookLM      │  │  Gemini API      │      │
│  │  API             │  │  API             │  │  (optional)      │      │
│  │  • OAuth 2.0     │  │  • Research      │  │  • AI agent      │      │
│  │  • File download │  │  • Analysis      │  │  • Industry ID   │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Client Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CLIENT PIPELINE FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

START (main.py spawns process)
  │
  ├─> Anti-thundering-herd offset (0-30s random delay)
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Document Download (30-60 seconds)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Parse Drive folder URL                                          │
│  2. OAuth authentication check                                      │
│  3. List files in folder (recursive)                                │
│  4. Check cache (7-day TTL)                                         │
│     ├─> Cache hit: Use cached files                                │
│     └─> Cache miss: Download from Drive                            │
│  5. Convert Google Docs to PDF                                      │
│  6. Save to local cache                                             │
│                                                                      │
│  Output: PDFs in ~/.project-ape/drive_cache/{client_id}/           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Notebook Creation (10-15 seconds)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Check for existing notebook (by name)                           │
│     ├─> Found: Reuse existing notebook                             │
│     └─> Not found: Create new notebook                             │
│  2. Upload PDFs as sources                                          │
│  3. Wait for source processing (30s fast, 45s deep)                │
│  4. Verify sources ready                                            │
│                                                                      │
│  Output: NotebookLM notebook with uploaded sources                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Research Phase (3-8 minutes)                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  For each research query (2 queries):                               │
│    1. Load prompt from ask_prompt_0X.txt                           │
│    2. Substitute variables ($name, $industry, $subsegments)        │
│    3. Execute NotebookLM "Ask" query                               │
│    4. Parse response and citations                                 │
│    5. Import cited sources (10-90 sources per query)               │
│    6. Wait (8-12s fast, 15-25s deep)                               │
│    7. Retry on quota errors (exponential backoff)                  │
│                                                                      │
│  Prompts:                                                            │
│    • ask_prompt_01.txt: Industry analysis & trends                 │
│    • ask_prompt_02.txt: Competitive landscape                      │
│                                                                      │
│  Output: Research responses + 20-180 imported sources               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Analysis Phase (8-12 minutes)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  For each analysis prompt (6 prompts):                              │
│    1. Load prompt from chat_prompt_consolidated_0X.txt             │
│    2. Substitute variables ($name, $industry, $subsegments,        │
│       $persona)                                                     │
│    3. Execute NotebookLM "Chat" query                              │
│    4. Parse response                                                │
│    5. Wait (5-8s fast, 10-15s deep)                                │
│    6. Retry on errors (exponential backoff)                        │
│                                                                      │
│  Prompts:                                                            │
│    • 01: Industry overview + key challenges                        │
│    • 02: Technology trends + competitive positioning               │
│    • 03: Pain points + opportunity areas                           │
│    • 04: Decision makers + buying process                          │
│    • 05: Value proposition + success metrics                       │
│    • 06: Risk factors + strategic recommendations                  │
│                                                                      │
│  Output: Strategic analysis covering 12 dimensions                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: Quality Validation (1-2 minutes)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Count imported sources                                          │
│  2. Validate content completeness                                   │
│  3. Assess source quality                                           │
│  4. Calculate quality score (1-10)                                  │
│  5. Generate execution summary                                      │
│  6. Write outputs to docs_generated/{client_id}/                   │
│                                                                      │
│  Quality Metrics:                                                    │
│    • Source count (20%)                                             │
│    • Source quality (25%)                                           │
│    • Content completeness (25%)                                     │
│    • Research depth (15%)                                           │
│    • Analysis coverage (15%)                                        │
│                                                                      │
│  Output: Quality score + summary files                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
END (mark status as COMPLETE)
```

---

## Component Overview

### 1. Main Orchestrator (`main.py`)

**Responsibilities:**
- Parse command-line arguments and configuration
- Validate authentication (NotebookLM, Drive)
- Spawn Flask dashboard server (background process)
- Spawn client pipeline processes (parallel)
- Monitor process health
- Aggregate status from all clients
- Handle graceful shutdown

**Key Functions:**
- `spawn_dashboard_server()`: Launch Flask app in subprocess
- `spawn_client_process(client_id)`: Create isolated process per client
- `monitor_processes()`: Check process health, aggregate status
- `cleanup()`: Terminate processes, close resources

**Process Model:**
```
main.py (PID 1000)
├─> dashboard/server.py (PID 1001) - Flask app
├─> client_pipeline.py client_a (PID 1002)
├─> client_pipeline.py client_b (PID 1003)
└─> client_pipeline.py client_c (PID 1004)
```

### 2. Client Pipeline (`core/client_pipeline.py`)

**Responsibilities:**
- Execute complete workflow for single client
- Update status file at each phase
- Handle errors and retries
- Write outputs to `docs_generated/`

**Key Functions:**
- `run_pipeline(client_id, config, mode)`: Main entry point
- `execute_phase_1_download()`: Drive file download
- `execute_phase_2_notebook()`: Notebook creation
- `execute_phase_3_research()`: Research queries
- `execute_phase_4_analysis()`: Analysis prompts
- `execute_phase_5_validation()`: Quality validation

**State Management:**
- Writes status to `.multi_process_status/{client_id}.json`
- Updates every 5 seconds during execution
- Final status: COMPLETE, FAILED, or ERROR

### 3. Drive Manager (`core/drive_manager.py`)

**Responsibilities:**
- Google Drive API integration
- OAuth 2.0 authentication
- File download with caching
- Google Docs → PDF conversion

**Key Functions:**
- `__init__()`: Initialize OAuth flow, load credentials
- `authenticate()`: Complete OAuth flow, save token
- `list_files(folder_id)`: Recursive folder traversal
- `download_file(file_id, dest_path)`: Download with caching
- `export_google_doc(file_id)`: Convert Docs to PDF

**Caching Strategy:**
- Cache location: `~/.project-ape/drive_cache/{client_id}/`
- TTL: 7 days (configurable)
- Cache key: Drive file ID + modification timestamp
- Invalidation: TTL expiry or `--refresh` flag

### 4. Notebook Manager (`core/notebook_manager.py`)

**Responsibilities:**
- NotebookLM API wrapper
- Notebook lifecycle management
- Deduplication (find by name)
- Error handling and retries

**Key Functions:**
- `create_notebook(name)`: Create new notebook
- `find_notebook_by_name(name)`: Search for existing notebook
- `delete_notebook(notebook_id)`: Remove notebook
- `list_notebooks()`: Get all user notebooks
- `add_source(notebook_id, file_path)`: Upload source

**API Integration:**
- Uses `notebooklm` CLI subprocess calls
- Parses JSON output from CLI
- Handles authentication errors
- Implements retry logic (5 attempts, exponential backoff)

### 5. Source Manager (`core/source_manager.py`)

**Responsibilities:**
- Source upload to NotebookLM
- Research query execution ("Ask" prompts)
- Analysis query execution ("Chat" prompts)
- Citation parsing and source import

**Key Functions:**
- `upload_sources(notebook_id, file_paths)`: Batch upload
- `execute_research_query(notebook_id, prompt)`: Run Ask prompt
- `execute_analysis_query(notebook_id, prompt)`: Run Chat prompt
- `parse_citations(response)`: Extract source URLs
- `import_cited_sources(notebook_id, citations)`: Add web sources

**Prompt Processing:**
1. Load prompt template from file
2. Substitute variables:
   - `$name` → client name
   - `$industry` → client industry
   - `$subsegments` → industry subsegments
   - `$persona` → AI analysis persona (Chat prompts only)
3. Execute via NotebookLM API
4. Parse response and metadata
5. Import cited sources (research queries only)

### 6. Gemini Agent (`core/gemini_agent.py`)

**Responsibilities:**
- Industry auto-detection
- Error analysis and recovery
- Quality validation assistance

**Key Functions:**
- `detect_industry(client_name, documents)`: AI-powered industry classification
- `analyze_error(error_message, context)`: Error diagnosis
- `suggest_recovery(error_analysis)`: Recovery recommendations

**Optional Feature:**
- Requires Gemini API key
- Gracefully degrades if unavailable
- Used for advanced features only

### 7. Quality Scorer (`core/quality_scorer.py`)

**Responsibilities:**
- Validate research completeness
- Calculate quality scores
- Generate validation reports

**Key Functions:**
- `calculate_score(notebook_data)`: Compute 1-10 score
- `validate_sources(source_count, mode)`: Check source adequacy
- `validate_completeness(responses)`: Check all prompts answered
- `assess_source_quality(sources)`: Evaluate source authority

**Scoring Algorithm:**
```python
score = (
    source_count_score * 0.20 +
    source_quality_score * 0.25 +
    completeness_score * 0.25 +
    research_depth_score * 0.15 +
    analysis_coverage_score * 0.15
)
```

### 8. Dashboard Server (`dashboard/server.py`)

**Responsibilities:**
- Flask web application
- Real-time status aggregation
- Log streaming (Server-Sent Events)
- API endpoints for control

**Routes:**
- `GET /` - Main dashboard
- `GET /configure` - Configuration UI
- `GET /status` - JSON status endpoint
- `GET /stream-logs` - SSE log stream
- `POST /api/start-workflow` - Launch pipeline
- `POST /api/shutdown` - Graceful shutdown

**Status Aggregation:**
1. Read all `.multi_process_status/*.json` files
2. Aggregate overall progress
3. Calculate counts (total, running, complete, failed)
4. Serve as JSON every 2 seconds

---

## Data Flow

### Authentication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      AUTHENTICATION FLOW                          │
└──────────────────────────────────────────────────────────────────┘

NotebookLM Authentication:
  1. User runs: notebooklm login
  2. CLI opens Chrome browser
  3. User signs in with Google
  4. OAuth callback saves credentials
  5. Credentials saved: ~/.notebooklm/credentials.json
  6. Container mounts as volume

Google Drive Authentication:
  1. User runs: setup-oauth-drive-improved.py
  2. Script guides through GCP setup:
     a. Create/select project
     b. Enable Drive API
     c. Create OAuth credentials
     d. Download client_secret_*.json
  3. Script finds and moves credentials
  4. Script launches OAuth flow
  5. Browser consent screen
  6. Token saved: ~/.project-ape/drive_token.json
  7. Credentials: ~/.project-ape/drive_credentials.json
```

### Document Processing Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   DOCUMENT PROCESSING FLOW                        │
└──────────────────────────────────────────────────────────────────┘

1. Drive Folder → DriveManager
   ├─> Parse folder URL
   ├─> Authenticate with OAuth
   ├─> List files (recursive)
   └─> Download PDFs
       ├─> Check cache (7-day TTL)
       ├─> Download if cache miss
       └─> Convert Google Docs to PDF

2. Local Files → NotebookManager
   ├─> Check for existing notebook (by name)
   └─> Create new notebook if needed

3. Files → SourceManager
   ├─> Upload PDFs to notebook
   ├─> Wait for processing (30-45s)
   └─> Verify sources ready

4. Research Phase → SourceManager
   ├─> Execute Ask queries (2)
   ├─> Parse citations from responses
   ├─> Import cited web sources (20-180 sources)
   └─> Save research outputs

5. Analysis Phase → SourceManager
   ├─> Execute Chat queries (6)
   ├─> Parse analysis responses
   └─> Save analysis outputs

6. Quality Validation → QualityScorer
   ├─> Count sources
   ├─> Validate completeness
   ├─> Calculate score (1-10)
   └─> Generate summary

7. Outputs → docs_generated/{client_id}/
   ├─> Research_Output.txt
   ├─> Analysis_Output.txt
   ├─> Quality_Score.json
   ├─> NotebookLM_Link.txt
   └─> Execution_Summary.json
```

---

## Multi-Process Execution Model

### Process Architecture

**Main Process (main.py):**
- Orchestrates all workflows
- Does NOT execute client pipelines directly
- Spawns child processes
- Monitors child health
- Aggregates status

**Child Processes:**
- One process per client
- Completely isolated (no shared memory)
- Independent execution
- Writes status to JSON file
- Exits on completion or error

### Inter-Process Communication (IPC)

**Method**: File-based JSON status files

**Status File Location**: `.multi_process_status/{client_id}.json`

**Status File Schema**:
```json
{
  "client_id": "acme_corp",
  "client_name": "Acme Corporation",
  "status": "RUNNING",
  "current_phase": "Research Phase",
  "progress": 45,
  "quality_score": null,
  "notebook_url": "https://notebooklm.google.com/notebook/abc123",
  "start_time": "2026-06-30T10:15:00",
  "phase_timings": {
    "download": 42,
    "notebook_creation": 12,
    "research": 187,
    "analysis": null,
    "validation": null
  },
  "sources_imported": 67,
  "errors": []
}
```

**Update Frequency**: Every 5 seconds (during execution)

**Readers**: Main process, Dashboard server

**Writers**: Client pipeline process (single writer per file)

### Concurrency Model

**Parallel Execution:**
- Up to 5 clients recommended
- Each client: independent process
- No synchronization required
- No race conditions (single writer per status file)

**Anti-Thundering-Herd:**
```python
# Random offset before starting (0-30 seconds)
import random
import time

offset = random.uniform(0, 30)
time.sleep(offset)

# Then start pipeline
run_pipeline(client_id, config, mode)
```

This prevents all clients from hitting APIs simultaneously.

---

## Status Tracking and Dashboard

### Status File Lifecycle

**1. Initialization (main.py):**
```python
status = {
    "client_id": client_id,
    "client_name": config[f"{client_id}_name"],
    "status": "PENDING",
    "current_phase": "Initializing",
    "progress": 0,
    "start_time": datetime.now().isoformat()
}
write_status(client_id, status)
```

**2. Updates (client_pipeline.py):**
```python
# Phase transition
update_status(client_id, {
    "status": "RUNNING",
    "current_phase": "Research Phase",
    "progress": 35
})

# Progress within phase
update_status(client_id, {
    "progress": 45
})
```

**3. Completion:**
```python
update_status(client_id, {
    "status": "COMPLETE",
    "current_phase": "Finished",
    "progress": 100,
    "quality_score": 8.5,
    "completion_time": datetime.now().isoformat()
})
```

### Dashboard Real-Time Updates

**Server-Sent Events (SSE) for Logs:**

```python
# dashboard/server.py
@app.route('/stream-logs')
def stream_logs():
    def generate():
        with open('logs/overall.log', 'r') as f:
            f.seek(0, 2)  # Seek to end
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')
```

**Client-Side Auto-Refresh:**

```javascript
// Auto-refresh every 2 seconds
setInterval(async () => {
    const response = await fetch('/status');
    const status = await response.json();
    updateDashboard(status);
}, 2000);
```

---

## Container Architecture

### Container Image Structure

**Base Image**: `registry.access.redhat.com/ubi9/python-311`

**Layers:**
1. Base UBI 9 + Python 3.11
2. System dependencies (git, gcc)
3. Python packages (requirements.txt)
4. NotebookLM CLI
5. Application code
6. Entrypoint script

**User**: `apeuser` (UID 1000, non-root)

### Volume Mounts

**Production Container Run:**
```bash
podman run -it --rm \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:z \
  -v ./docs_generated:/app/docs_generated:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -p 8765:8765 \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients acme_corp --mode fast
```

**Volume Purposes:**

| Volume | Purpose | Permissions |
|--------|---------|-------------|
| `vars.py` | Configuration | Read-only (`:ro`) |
| `logs/` | Execution logs | Read-write |
| `docs_generated/` | Outputs | Read-write |
| `project-ape-credentials` | NotebookLM credentials | Read-only |

**SELinux Labels (`:z`):**
- Required on RHEL/Fedora systems
- Applies private unshared label
- Allows container access to host files

### Multi-Architecture Support

**Supported Platforms:**
- `linux/amd64` (x86_64)
- `linux/arm64` (Apple Silicon, ARM servers)

**Build Command:**
```bash
podman build \
  --platform linux/amd64,linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:4.0.1 \
  -f Containerfile.debian .
```

---

## Security Model

### Authentication Security

**NotebookLM:**
- OAuth 2.0 flow via official SDK
- Credentials: `~/.notebooklm/credentials.json`
- No API keys in code or config
- Container: volume mount (not copied into image)

**Google Drive:**
- OAuth 2.0 Desktop app flow
- Client secrets: `~/.project-ape/drive_credentials.json`
- Access tokens: `~/.project-ape/drive_token.json`
- Scopes: `drive.readonly` (minimum required)
- Token refresh: automatic (90-day expiry)

### Container Security

**Non-Root Execution:**
```dockerfile
# Create non-root user
RUN useradd -u 1000 -r -g 0 -m -d /opt/app-root -s /sbin/nologin apeuser

# Switch to non-root
USER 1000
```

**Read-Only Mounts:**
- Configuration: mounted as `:ro`
- Credentials: mounted as `:ro`
- Application code: immutable in image

**No Secrets in Image:**
- No API keys baked into image
- No credentials in environment variables
- All secrets via volume mounts

### Data Security

**Credentials Storage:**
- Host: `~/.project-ape/` and `~/.notebooklm/`
- Permissions: `chmod 600` (owner read/write only)
- Never committed to version control (`.gitignore`)

**Output Data:**
- Written to `docs_generated/` (user-owned)
- No sensitive data in logs
- Client names sanitized in file paths

**Cache Security:**
- Drive cache: `~/.project-ape/drive_cache/`
- 7-day TTL (automatic cleanup)
- No sensitive data cached

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core application language |
| **Flask** | 3.0+ | Web dashboard server |
| **NotebookLM SDK** | Latest | NotebookLM API integration |
| **Google API Client** | Latest | Drive API integration |
| **PyPDF2** | Latest | PDF processing |
| **Requests** | Latest | HTTP client |

### Frontend

| Technology | Purpose |
|------------|---------|
| **HTML5** | Dashboard structure |
| **CSS3** | Styling and responsive design |
| **Vanilla JavaScript** | Client-side logic (no frameworks) |
| **Server-Sent Events** | Real-time log streaming |
| **Fetch API** | AJAX requests |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Podman/Docker** | Containerization |
| **UBI 9** | Base container image |
| **Quay.io** | Container registry |
| **Git** | Version control |

### External Services

| Service | Purpose | Authentication |
|---------|---------|----------------|
| **Google Drive API** | File download | OAuth 2.0 |
| **Google NotebookLM** | AI research | OAuth 2.0 |
| **Google Gemini API** | Advanced AI (optional) | API key |

---

## Design Decisions

### Why Multi-Process (not Multi-Threading)?

**Decision**: Use Python multiprocessing for parallel execution

**Rationale**:
1. **GIL Avoidance**: Multiprocessing bypasses Python's Global Interpreter Lock
2. **True Parallelism**: Each process uses separate CPU core
3. **Isolation**: Process crashes don't affect other clients
4. **Simplicity**: No need for locks, semaphores, or shared memory
5. **Scalability**: Easy to distribute across machines (future)

**Trade-Off**: Higher memory usage vs. threads (acceptable for 1-5 clients)

### Why File-Based IPC?

**Decision**: Use JSON files for status sharing between processes

**Rationale**:
1. **Simplicity**: No need for message queues or shared memory
2. **Debuggability**: Status files are human-readable
3. **Persistence**: Status survives process crashes
4. **Single Writer**: No race conditions (one writer per file)
5. **Framework Independence**: Works with any language/runtime

**Trade-Off**: Slightly slower than in-memory (acceptable for 2-second refresh rate)

### Why Container-First?

**Decision**: Design for containerized deployment as primary target

**Rationale**:
1. **Consistency**: Same environment across dev/test/prod
2. **Portability**: Runs on any platform with Podman/Docker
3. **Isolation**: Clean separation from host system
4. **Versioning**: Immutable deployments via tags
5. **Security**: Non-root execution, minimal attack surface

**Trade-Off**: Additional complexity for native execution (acceptable)

### Why OAuth (not Service Accounts)?

**Decision**: Use OAuth 2.0 for Google APIs instead of service accounts

**Rationale**:
1. **User Context**: Access user's Drive folders (not shared folders)
2. **Simpler Setup**: No domain admin required
3. **Revocability**: Users can revoke access anytime
4. **Scope Limitation**: Minimal scopes (`drive.readonly`)
5. **Security**: No long-lived credentials in repositories

**Trade-Off**: Requires browser for initial auth (acceptable one-time setup)

### Why Flask (not FastAPI)?

**Decision**: Use Flask for dashboard server

**Rationale**:
1. **Simplicity**: Lightweight, easy to understand
2. **Maturity**: Stable, well-documented, large ecosystem
3. **SSE Support**: Native support for Server-Sent Events
4. **Template Engine**: Built-in Jinja2 for HTML rendering
5. **Deployment**: Works well in containers

**Alternative Considered**: FastAPI (async, modern, but overkill for this use case)

---

## Extension Points

### Adding New Prompts

**Location**: Project root (e.g., `ask_prompt_03.txt`, `chat_prompt_consolidated_07.txt`)

**Integration**: Update `core/source_manager.py`:
```python
# Add new prompt to list
RESEARCH_PROMPTS = ['ask_prompt_01.txt', 'ask_prompt_02.txt', 'ask_prompt_03.txt']
ANALYSIS_PROMPTS = ['chat_prompt_consolidated_01.txt', ..., 'chat_prompt_consolidated_07.txt']
```

### Adding New Phases

**Location**: `core/client_pipeline.py`

**Implementation**:
```python
def execute_phase_6_custom(client_id, config):
    update_status(client_id, {
        "current_phase": "Custom Phase",
        "progress": 85
    })
    
    # Custom logic here
    
    update_status(client_id, {"progress": 95})
```

### Adding New Quality Metrics

**Location**: `core/quality_scorer.py`

**Implementation**:
```python
def calculate_custom_metric(data):
    # Custom scoring logic
    return score

def calculate_score(notebook_data):
    scores = {
        'source_count': calculate_source_count_score(notebook_data),
        'custom_metric': calculate_custom_metric(notebook_data),
        # ... other metrics
    }
    
    # Update weights
    overall_score = (
        scores['source_count'] * 0.15 +
        scores['custom_metric'] * 0.10 +
        # ... other weights
    )
    
    return overall_score
```

### Adding New Dashboard Views

**Location**: `dashboard/templates/`

**Route Definition** (`dashboard/server.py`):
```python
@app.route('/custom-view')
def custom_view():
    data = get_custom_data()
    return render_template('custom_view.html', data=data)
```

---

**For implementation details, see source code in `/core` and `/dashboard` directories.**

Return to: [README.md](../README.md) | See also: [USER_GUIDE.md](USER_GUIDE.md)
