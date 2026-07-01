# ARCHITECTURE.md

**Project APE (Account Planning Engine) - System Architecture**

Version: 4.0.1  
Last Updated: 2026-06-30

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Authentication Architecture](#authentication-architecture)
4. [Container Architecture](#container-architecture)
5. [Process Model](#process-model)
6. [Data Flow Architecture](#data-flow-architecture)
7. [Security Model](#security-model)
8. [Deployment Architecture](#deployment-architecture)
9. [Extension Points](#extension-points)
10. [Performance & Scalability](#performance--scalability)

---

## System Overview

### 10,000-Foot View

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION LAYER                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CLI Launcher            Web Dashboard (Flask)       Container Runtime  │
│  ./ape-run.sh    ←────→  http://localhost:8765  ←→   podman/docker     │
│                                                                          │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  main.py (Multi-Process Orchestrator)                                   │
│  ├─ ProcessManager: Lifecycle, status tracking, cleanup                 │
│  ├─ Flask Dashboard Server (background process)                         │
│  └─ Client Pipeline Processes (1-5 parallel)                            │
│                                                                          │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                          PIPELINE LAYER                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  core/client_pipeline.py (per-client workflow)                          │
│  ├─ Phase 1: Google Drive Download & PDF Consolidation                  │
│  ├─ Phase 2: NotebookLM Notebook Creation/Deduplication                 │
│  ├─ Phase 3: Research (Ask Prompts) + Web Source Import                 │
│  ├─ Phase 4: Analysis (Chat Prompts) → Notes                            │
│  └─ Phase 5: Mind Map Generation & Quality Scoring                      │
│                                                                          │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                         INTEGRATION LAYER                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ DriveManager     │  │ NotebookManager  │  │ SourceManager        │  │
│  │ OAuth 2.0        │  │ Deduplication    │  │ Import & Dedupe      │  │
│  │ Caching (24h)    │  │ Context Mgmt     │  │ Research Automation  │  │
│  └──────────────────┘  └──────────────────┘  │ Retry Logic          │  │
│                                              └──────────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐                            │
│  │ AuthManager      │  │ UpdateManager    │                            │
│  │ Session Check    │  │ Change Detection │                            │
│  │ Retry Logic      │  │ Incremental Sync │                            │
│  └──────────────────┘  └──────────────────┘                            │
│                                                                          │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────┐
│                          EXTERNAL SERVICES                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  NotebookLM API        Google Drive API         Claude/Gemini API       │
│  (via notebooklm-py)   (OAuth 2.0)              (Industry Detection)    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Core Responsibilities

**Orchestration Layer (`main.py`):**
- Multi-process lifecycle management
- Dashboard server coordination
- Status file initialization
- Graceful shutdown handling
- Anti-thundering-herd launch staggering

**Pipeline Layer (`client_pipeline.py`):**
- Single-client workflow execution
- Five-phase sequential processing
- Status updates to JSON files
- Error handling and recovery
- Quality score calculation

**Integration Layer (Managers):**
- External API abstraction
- Retry logic and error handling
- Caching and optimization
- Authentication management
- Resource deduplication

---

## Component Architecture

### 1. Main Orchestrator (`main.py`)

**Purpose:** Multi-process coordinator and lifecycle manager

**Key Classes:**

```python
class ProcessManager:
    """Manages client processes and dashboard server."""
    
    def __init__(self, run_id: str)
    def initialize_status_file(client_id, mode)
    def start_dashboard()
    def start_client_process(client_id, mode, refresh) -> subprocess.Popen
    def monitor_processes()
    def get_results() -> Dict
    def cleanup()
```

**Process Flow:**

1. **Initialization:**
   - Parse command-line arguments (`--mode`, `--clients`, `--refresh`)
   - Load configuration from `vars.py`
   - Create status and logs directories
   - Clean up old status files from previous runs

2. **Status File Creation:**
   - One JSON file per client in `.multi_process_status/`
   - Initial state: `PENDING`, progress: 0
   - Includes: `run_id`, `start_time`, `mode`, `log_file` path

3. **Dashboard Launch:**
   - Spawns Flask server as subprocess
   - Port: 8765 (configurable via `DASHBOARD_PORT`)
   - Auto-opens browser to dashboard URL
   - Runs in background for entire pipeline duration

4. **Client Process Launch:**
   - Staggered launch with delay (10s deep, 2s fast)
   - Each client runs in separate Python process
   - Command: `python3 core/client_pipeline.py <client_id> --mode <mode> --status-file <path>`
   - Stdout/stderr redirected to `logs/<client_id>.log`

5. **Process Monitoring:**
   - Polls all client processes every 5 seconds
   - Waits until all processes complete
   - Handles `KeyboardInterrupt` gracefully

6. **Results & Cleanup:**
   - Aggregates success/failure counts
   - Displays summary statistics
   - Keeps dashboard running 5 minutes post-completion (container mode)
   - Terminates all child processes
   - Exits with code 0 (all success) or 1 (any failures)

**Signal Handling:**

```python
# SIGTERM and SIGINT handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Graceful shutdown sequence:
# 1. Stop accepting new work
# 2. Terminate client processes (SIGTERM → wait → SIGKILL)
# 3. Terminate dashboard (SIGTERM → wait → SIGKILL)
# 4. Exit with os._exit() to force immediate termination
```

---

### 2. Client Pipeline (`core/client_pipeline.py`)

**Purpose:** Single-client workflow execution with five phases

**Key Classes:**

```python
class ClientPipeline:
    """Executes complete pipeline for a single client."""
    
    def __init__(client_id, config, status_file, mode, force_refresh)
    def execute() -> bool
    def update_status(step, progress, status, **kwargs)
    
    # Phase implementations
    def _setup_client_folder(folder_spec) -> Path
    def _determine_industry_and_subsegments() -> Tuple[str, str]
    def _consolidate_pdfs(output_filename) -> Optional[Path]
    def _run_ask_prompts()
    def _deduplicate_sources()
    def _run_chat_prompts()
    def _generate_mindmap()
    def _calculate_quality_score() -> float
```

**Execution Modes:**

1. **Standard Mode (`_execute_standard()`):**
   - Default workflow for `fast` and `deep` modes
   - Full pipeline from scratch or reuse existing notebook

2. **Update Mode (`_execute_update_mode()`):**
   - Refresh existing notebook with new data
   - Skips notebook creation (finds existing)
   - Re-runs research and updates all notes
   - Regenerates mind map

3. **Agent Mode (`_execute_with_agent()`)** (optional):
   - Gemini AI orchestration for quality monitoring
   - Adaptive retry logic based on quality scores
   - Enabled via `GEMINI_AGENT_CONFIG` in `vars.py`

**Phase Details:**

**Phase 1: Google Drive Download & PDF Consolidation (Progress: 1-30%)**

```python
# Step 1: Setup client folder
self.client_folder = self._setup_client_folder(self.client_folder_spec)

# Detects Drive URL vs local path:
if 'drive.google.com' in folder_spec:
    with DriveManager(client_id, folder_spec, cache_enabled=True) as temp_dir:
        # Downloads files to cache (~/.project-ape/drive_cache/<folder_id>)
        # Exports Google Docs/Sheets/Slides → PDF
        # Respects 24-hour TTL (skips download if cache valid)
        return Path(temp_dir)
else:
    return Path(folder_spec)  # Local folder

# Step 2: Industry detection (AI-powered or manual config)
industry, subsegments = self._determine_industry_and_subsegments()
# Uses Claude/Gemini API to analyze client name + Drive file list
# Falls back to manual config from vars.py

# Step 3: Consolidate all files to PDF
consolidated_pdf = self._consolidate_pdfs(f"{client_name}-Consolidated-{timestamp}.pdf")
# Converts: PDFs, images, Office docs (xlsx, docx, pptx) → single PDF
# Handles text files, JSON, CSV via direct PDF conversion
# Uses FastPDFConsolidator with table of contents
```

**Phase 2: Notebook Creation/Deduplication (Progress: 10-30%)**

```python
# Check for existing notebook
notebook_name = f"DEV_{client_id}-TEST"
existing_notebook = self.notebook_manager.find_notebook_by_name(notebook_name)

if existing_notebook:
    # Reuse existing notebook (deduplication)
    self.notebook_id = existing_notebook
else:
    # Create new notebook
    self.notebook_id = self.notebook_manager.create_notebook(notebook_name)

# Set context for all subsequent operations
self.notebook_manager.set_context(self.notebook_id)

# Initialize source manager
self.source_manager = SourceManager(self.client_id, self.notebook_id)

# Upload consolidated PDF (with change detection)
needs_update, newest_file_time = self._check_consolidation_needed()
if needs_update:
    # Delete old consolidated PDFs
    self.source_manager.delete_old_consolidated_pdfs(self.client_name)
    # Upload new PDF
    self.source_manager.add_file_source(consolidated_pdf)
    # Save timestamp for future comparison
    self._save_consolidation_timestamp(newest_file_time)
```

**Phase 3: Research - Ask Prompts (Progress: 30-60%)**

```python
# Find all research prompts
ask_prompts = sorted(self.project_root.glob("ask_*.txt"))

# Anti-collision delay (deep mode: 0-15s, fast mode: 0-12s)
delay = random.uniform(0, 15 if mode == "deep" else 12)
time.sleep(delay)

for prompt_file in ask_prompts:
    # Substitute variables
    prompt_text = prompt_file.read_text()
    prompt_text = prompt_text.replace('$name', self.client_name)
    prompt_text = prompt_text.replace('$industry', self.industry)
    prompt_text = prompt_text.replace('$subsegments', self.subsegments)
    
    # Run research with automatic source import
    result = self.source_manager.add_research_with_import(
        prompt_file,
        mode=self.mode,
        client_name=self.client_name,
        client_industry=self.industry,
        client_subsegments=self.subsegments
    )
    
    # Deep mode: Deduplicate after EACH prompt
    if self.mode == "deep":
        self.source_manager.deduplicate_sources()

# Fast mode: Deduplicate ONCE at the end
if self.mode == "fast":
    self.source_manager.deduplicate_sources()
```

**Phase 4: Analysis - Chat Prompts (Progress: 65-95%)**

```python
# Find all chat prompts
chat_prompts = sorted(self.project_root.glob("chat_prompt_consolidated_*.txt"))

# Descriptive note titles
note_titles = {
    'chat_prompt_consolidated_01.txt': 'Industry Analysis & Customer Business Profile',
    'chat_prompt_consolidated_02.txt': 'Innovation Assessment & Executive Summary',
    # ... 6 total prompts
}

for prompt_file in chat_prompts:
    # Substitute variables (includes $persona for chat context)
    prompt_text = prompt_text.replace('$persona', self.persona)
    
    # Execute ask command with --json (preserves formatting)
    result = subprocess.run([
        "notebooklm", "ask",
        "--prompt-file", tmp_path,
        "-n", self.notebook_id,
        "--json"
    ])
    
    # Create note from response
    response_data = json.loads(result.stdout)
    note_content = response_data.get('answer', '')
    
    subprocess.run([
        "notebooklm", "note", "create",
        "--content", note_content,
        "-t", note_titles[prompt_file.name],
        "-n", self.notebook_id
    ])
```

**Phase 5: Mind Map Generation & Quality Scoring (Progress: 95-100%)**

```python
# Generate mind map
subprocess.run([
    "notebooklm", "generate", "mind-map",
    "-n", self.notebook_id
])

# Calculate quality score (0-10)
quality_score = self._calculate_quality_score()
# Scoring breakdown:
# - Sources count (0-3 pts): 15+ sources = 3 pts
# - Has PDF source (0-1 pt): Consolidated PDF present
# - Research sources (0-1 pt): 10+ web sources
# - Notes created (0-4 pts): 6 notes = 4 pts
# - Has mind map (0-1 pt): Artifact generated

# Update final status
self.update_status("Pipeline complete", 100, status="COMPLETE", quality_score=quality_score)
```

---

### 3. Google Drive Manager (`core/drive_manager.py`)

**Purpose:** Google Drive file downloads with OAuth 2.0 and intelligent caching

**Architecture:**

```python
class DriveManager:
    """Context manager for Google Drive folder downloads."""
    
    # OAuth 2.0 configuration
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Google Workspace export formats (all → PDF for NotebookLM)
    EXPORT_FORMATS = {
        'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.spreadsheet': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
    }
    
    # Retry configuration
    MAX_RETRIES = 5
    RETRY_BASE_DELAY = 10.0
    
    def __enter__(self) -> Path:
        # Download files and return cache/temp directory
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup temp directory (if not cached)
```

**Usage Pattern:**

```python
with DriveManager(
    client_id="merck_test",
    folder_spec="https://drive.google.com/drive/folders/ABC123",
    cache_enabled=True,
    force_refresh=False,
    config=DRIVE_CONFIG
) as folder_path:
    # Use folder_path as local directory
    files = list(folder_path.glob("*.pdf"))
    # DriveManager handles cleanup on exit
```

**Caching Strategy:**

- **Cache Location:** `~/.project-ape/drive_cache/<folder_id>/`
- **TTL:** 24 hours (configurable via `cache_ttl_hours`)
- **Metadata File:** `metadata.json` with timestamps and file counts
- **Force Refresh:** `--refresh` flag bypasses cache entirely

**Authentication Flow:** See [Authentication Architecture](#authentication-architecture)

---

### 4. Notebook Manager (`core/notebook_manager.py`)

**Purpose:** NotebookLM notebook lifecycle and deduplication

**Key Operations:**

```python
class NotebookManager:
    def find_notebook_by_name(name: str) -> Optional[str]:
        # List all notebooks via CLI
        result = subprocess.run(["notebooklm", "list", "--json"])
        notebooks = json.loads(result.stdout).get('notebooks', [])
        
        # Find exact match
        for notebook in notebooks:
            if notebook.get('name') == name:
                return notebook.get('id')
        
        return None
    
    def create_notebook(name: str) -> Optional[str]:
        result = subprocess.run(["notebooklm", "create", name])
        notebook_id = self._parse_notebook_id(result.stdout)
        return notebook_id
    
    def get_or_create_notebook(name: str) -> Optional[str]:
        # Deduplication: check for existing first
        notebook_id = self.find_notebook_by_name(name)
        if notebook_id:
            return notebook_id
        
        # Create new
        return self.create_notebook(name)
    
    def set_context(notebook_id: str) -> bool:
        # Set current notebook for subsequent operations
        subprocess.run(["notebooklm", "use", notebook_id])
```

**Deduplication Strategy:**
- Exact name matching on `DEV_{client_id}-TEST`
- Prevents duplicate notebooks on pipeline re-runs
- Reuses existing notebooks for incremental updates

---

### 5. Source Manager (`core/source_manager.py`)

**Purpose:** NotebookLM source import, research automation, deduplication

**Key Operations:**

```python
class SourceManager:
    def add_file_source(file_path: Path) -> bool:
        # Upload PDF/file to notebook
        subprocess.run(["notebooklm", "source", "add", str(file_path), "-n", notebook_id])
    
    def add_research_with_import(query_file, mode, **kwargs) -> Dict:
        # Run research query with automatic source import
        cmd = [
            "notebooklm", "source", "add-research",
            "--mode", mode,  # "fast" or "deep"
            "--prompt-file", query_file,
            "-n", notebook_id,
            "--import-all",  # Auto-import discovered sources
            "--timeout", "600"  # 10 minutes
        ]
        
        # Retry logic with exponential backoff
        for attempt in range(max_attempts):
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                imported = self._count_imported_sources(result.stdout)
                return {"success": True, "imported": imported}
            
            # Check for retryable errors
            if is_retryable_error(result.stderr):
                time.sleep(base_delay * (2 ** attempt))
                continue
            
            break
        
        return {"success": False, "error": result.stderr}
    
    def deduplicate_sources() -> int:
        # Get all sources
        sources = self.list_sources()
        
        # Track URLs and titles
        seen_urls = set()
        seen_titles = set()
        duplicates = []
        
        for source in sources:
            url = source.get('url', '').strip()
            title = source.get('title', '').strip().lower()
            
            # Check for duplicates
            if url and url in seen_urls:
                duplicates.append(source['id'])
            elif title and title in seen_titles:
                duplicates.append(source['id'])
            else:
                seen_urls.add(url)
                seen_titles.add(title)
        
        # Delete duplicates
        for source_id in duplicates:
            self.delete_source(source_id)
        
        return len(duplicates)
```

**Research Retry Logic:**

- **Fast Mode:** 5 attempts, 30s base delay, exponential backoff
- **Deep Mode:** 3 attempts, 30s base delay (fewer retries to avoid excessive delays)
- **Retryable Errors:** Rate limits, quota exceeded, authentication expired, RPC errors

**Deduplication Timing:**

- **Fast Mode:** Once at end of research phase (minimizes API calls)
- **Deep Mode:** After EACH research prompt (prevents accumulation, critical with 90-180 sources)

---

### 6. Dashboard Server (`dashboard/server.py`)

**Purpose:** Real-time status monitoring and log streaming

**Flask Endpoints:**

```python
@app.route('/')
def dashboard():
    # Main dashboard UI with client status grid

@app.route('/status')
def status():
    # JSON aggregation of all client status files
    # Returns: total, running, complete, failed, mode, run_id, clients[]

@app.route('/logs/<client_token>')
def stream_logs(client_token):
    # Server-Sent Events (SSE) stream of client logs
    # Reads from logs/<client_token>.log
    # Streams new content in real-time

@app.route('/logs/overall')
def stream_overall_logs():
    # Combined stream of all component logs

@app.route('/configure')
def configure():
    # Configuration UI for vars.py generation

@app.route('/launch')
def launch_page():
    # Launch confirmation page with workflow detection

@app.route('/api/start-workflow', methods=['POST'])
def start_workflow():
    # Trigger pipeline execution in background thread
    # Validates authentication before launch

@app.route('/api/refresh-sources', methods=['POST'])
def refresh_sources():
    # Force refresh of Google Drive cache
    # SSE stream of progress updates
```

**Status File Format:**

```json
{
  "name": "Merck Pharmaceuticals",
  "token": "merck_test",
  "step": "Research 2/2: ask_prompt_02",
  "progress": 45,
  "status": "RUNNING",
  "notebook_id": "abc-123-def-456",
  "mode": "fast",
  "last_update": 1719782400.0,
  "start_time": 1719782100.0,
  "quality_score": null,
  "plan_link": null,
  "log_file": "/app/logs/merck_test.log",
  "run_id": "1719782100"
}
```

**Dashboard Features:**

- **Auto-refresh:** Every 2 seconds via JavaScript polling
- **Live Logs:** SSE streaming with automatic reconnection
- **Progress Bars:** Visual indication of pipeline progress
- **Quality Scores:** Real-time display of notebook completeness (0-10)
- **Mode Indicator:** Fast vs Deep mode badge
- **Status Colors:** PENDING (gray), RUNNING (blue), COMPLETE (green), FAILED (red)

---

## Authentication Architecture

### NotebookLM Authentication (Primary)

**Method:** OAuth 2.0 via browser-based flow (Playwright automation)

**Credential Storage:**

```
~/.notebooklm/
├── profiles/
│   └── default/
│       └── storage_state.json    # Browser session cookies/tokens
└── credentials.json               # (Not used - legacy)
```

**Authentication Flow:**

```
┌─────────────┐                          ┌─────────────────────┐
│  User runs  │                          │  NotebookLM CLI     │
│  notebooklm │─────── Launch ────────→  │  (notebooklm-py)    │
│  login      │                          └──────────┬──────────┘
└─────────────┘                                     │
                                                    │ Spawns
                                                    ▼
                                          ┌─────────────────────┐
                                          │  Playwright         │
                                          │  Headless Chrome    │
                                          └──────────┬──────────┘
                                                     │
                                           Opens browser to
                                           notebooklm.google.com
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │  Google OAuth 2.0   │
                                          │  Login Page         │
                                          └──────────┬──────────┘
                                                     │
                                            User authenticates
                                            with Google account
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │  Playwright saves   │
                                          │  browser session    │
                                          │  to storage_state   │
                                          └──────────┬──────────┘
                                                     │
                                           Writes to disk
                                                     ▼
                            ~/.notebooklm/profiles/default/storage_state.json
                                        (Contains cookies & tokens)
```

**Session Validation (AuthManager):**

```python
class AuthManager:
    def is_authenticated(self, max_retries=3) -> bool:
        """Check authentication without launching browser."""
        
        storage_file = Path.home() / '.notebooklm' / 'profiles' / 'default' / 'storage_state.json'
        
        # File-based check (no browser launch)
        if not storage_file.exists():
            return False
        
        # Validate JSON structure
        with open(storage_file) as f:
            data = json.load(f)
        
        # Check for cookies (indicates valid session)
        if 'cookies' not in data or len(data['cookies']) == 0:
            return False
        
        return True
    
    def ensure_authenticated(self, client_id=None, force_check=False) -> bool:
        """Ensure authenticated, prompt user if not."""
        
        # Rate-limit auth checks (1 minute interval)
        if not force_check and time.time() - self.last_check < 60:
            return True
        
        # Anti-collision delay (prevents profile lock contention)
        time.sleep(random.uniform(0, 3))
        
        if self.is_authenticated():
            return True
        
        # Not authenticated - prompt user to login
        logger.warning("Run: notebooklm login")
        
        # Wait 60 seconds for user to login
        for i in range(6):
            time.sleep(10)
            if self.is_authenticated():
                return True
        
        return False
```

**Container Authentication:**

```bash
# On host machine (one-time setup)
notebooklm login

# Sync credentials to container volume
./setup-credentials.sh

# Container mounts credentials volume
podman run \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  quay.io/jasoande/project_ape/project-ape:latest
```

**Volume Structure:**

```
project-ape-credentials (podman volume)
└── profiles/
    └── default/
        └── storage_state.json    # Copied from host ~/.notebooklm/
```

---

### Google Drive Authentication

**Method:** OAuth 2.0 Desktop App Flow

**Credential Storage:**

```
~/.project-ape/
├── drive_credentials.json    # OAuth client secret (from Google Cloud Console)
└── drive_token.json          # User access/refresh tokens
```

**Authentication Flow:**

```
┌──────────────────┐                        ┌─────────────────────────┐
│  First-time      │                        │  DriveManager           │
│  Setup           │──── OAuth Setup ────→  │  _oauth_authenticate()  │
└──────────────────┘                        └───────────┬─────────────┘
                                                        │
                                              Check token file
                                                        │
                                                        ▼
                                            ┌───────────────────────────┐
                                            │  Token exists & valid?    │
                                            └──────┬────────────┬───────┘
                                                   │ Yes        │ No
                                                   │            │
                                                   ▼            ▼
                                         ┌─────────────┐  ┌───────────────────┐
                                         │ Return creds│  │ Check for refresh │
                                         └─────────────┘  │ token             │
                                                          └────────┬──────────┘
                                                                   │
                                                          ┌────────▼──────────┐
                                                          │ Has refresh token?│
                                                          └────┬──────┬───────┘
                                                               │ Yes  │ No
                                                               │      │
                                                               ▼      ▼
                                                     ┌──────────┐  ┌──────────────┐
                                                     │ Refresh  │  │ Run OAuth    │
                                                     │ token    │  │ flow (browser)│
                                                     └──────────┘  └──────┬───────┘
                                                                          │
                                                                          ▼
                                                              ┌────────────────────────┐
                                                              │ InstalledAppFlow       │
                                                              │ .run_local_server()    │
                                                              └────────────┬───────────┘
                                                                           │
                                                               Opens browser to
                                                               accounts.google.com
                                                                           │
                                                                           ▼
                                                              ┌────────────────────────┐
                                                              │ User grants Drive      │
                                                              │ read-only access       │
                                                              └────────────┬───────────┘
                                                                           │
                                                                Save tokens to
                                                                drive_token.json
```

**Token Refresh:**

```python
if creds.expired and creds.refresh_token:
    from google.auth.transport.requests import Request
    creds.refresh(Request())
    
    # Save refreshed token
    with open(token_file, 'w') as f:
        f.write(creds.to_json())
```

**Scopes Required:**

- `https://www.googleapis.com/auth/drive.readonly` (read-only access)

---

### Claude/Gemini API Authentication (Optional)

**Method:** API key via environment variables

**Configuration:**

```bash
# .env file (local development)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Container runtime
podman run -e ANTHROPIC_API_KEY=sk-ant-... ...
```

**Usage:**

```python
# Industry detection with Claude
from core.claude_industry_detector import ClaudeIndustryDetector

detector = ClaudeIndustryDetector(config)
industry, subsegments = detector.detect_industry(
    client_name="Merck Pharmaceuticals",
    drive_files=["10K_2024.pdf", "Investor_Presentation.pdf"]
)
# Falls back to Gemini if ANTHROPIC_API_KEY not set
```

**Security:**

- API keys NEVER embedded in code or container images
- Loaded from environment variables only
- Not required for core functionality (manual config fallback)

---

## Container Architecture

**Platform Naming Convention:** This document uses `x86_64` (Intel/AMD 64-bit) and `arm64` (ARM 64-bit) to clearly distinguish CPU architectures. Note that `x86_64` and `amd64` refer to the same architecture, but `x86_64` is preferred for clarity.

### Multi-Stage Build Strategy

**Stage 1: Builder (Python 3.13-slim)**

```dockerfile
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libjpeg-dev zlib1g-dev

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
```

**Benefits:**
- Isolates build tools from runtime
- Smaller final image (no gcc, g++, build headers)
- Faster builds (layer caching)

**Stage 2: Runtime (Python 3.13-slim)**

```dockerfile
FROM python:3.13-slim

# Install runtime dependencies ONLY
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-core-nogui \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libjpeg62-turbo zlib1g ca-certificates

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash apeuser && \
    mkdir -p /app /app/logs && \
    chown -R apeuser:apeuser /app

# Copy application code
COPY --chown=apeuser:apeuser core/ /app/core/
COPY --chown=apeuser:apeuser dashboard/ /app/dashboard/
COPY --chown=apeuser:apeuser *.txt /app/
COPY --chown=apeuser:apeuser main.py /app/

USER apeuser
WORKDIR /app

ENTRYPOINT ["/app/container-entrypoint.sh"]
CMD ["python3", "main.py", "--mode", "fast"]
```

---

### Volume Mount Strategy

**Required Mounts:**

```bash
podman run \
  # Credentials (NotebookLM OAuth session)
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  
  # Configuration (vars.py with client definitions)
  -v ./vars.py:/app/vars.py:ro,z \
  
  # Client data (source PDFs for local mode - optional)
  -v ./client_data:/app/client_data:ro,z \
  
  # Generated documents (outputs from pipeline)
  -v ./docs_generated:/app/docs_generated:z \
  
  # Logs (writable for status files and logs)
  -v ./logs:/app/logs:z \
  
  # Port mapping (dashboard access)
  -p 8765:8765 \
  
  quay.io/jasoande/project_ape/project-ape:latest
```

**Mount Types:**

- **Named Volume (`project-ape-credentials`):** Persistent, managed by Podman
- **Bind Mount (`./vars.py`):** Direct host path mapping
- **Read-Only (`:ro`):** Prevents container writes (configuration, client data)
- **SELinux Label (`:z`):** RHEL/Fedora compatibility (relabels files for container access)

**File Permissions:**

```bash
# Host directories must be writable by UID 1000 (apeuser in container)
chown -R 1000:1000 ./logs ./docs_generated

# Or use podman unshare for rootless containers
podman unshare chown -R 0:0 ./logs ./docs_generated
```

---

### Network Isolation

**Container Network:**

```bash
# Default bridge network
# Containers can reach external APIs (NotebookLM, Drive, Claude)
# Host can access dashboard via port mapping (-p 8765:8765)

# For custom network isolation:
podman network create ape-network
podman run --network ape-network ...
```

**Firewall Configuration:**

```bash
# Allow dashboard access from specific IPs
firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="8765" protocol="tcp" accept'
```

---

### Security Hardening

**Non-Root User:**

```dockerfile
# Create user with specific UID (1000)
RUN useradd -m -u 1000 -s /bin/bash apeuser

# Switch to non-root
USER apeuser
```

**Benefits:**
- Prevents privilege escalation
- Limits container breakout impact
- Filesystem isolation (can't write outside /app)

**Restrictive Permissions:**

```dockerfile
# Application directory: owner-only access
chmod 750 /app

# Logs/status: owner + group write
chmod 770 /app/logs /app/.multi_process_status
```

**No Secrets in Layers:**

- API keys via environment variables (not baked into image)
- Credentials via volume mounts (not COPY'd)
- `.env` files NOT included in image

**Health Check:**

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from urllib.request import urlopen; urlopen('http://localhost:8765/', timeout=5)" || exit 1
```

**Minimal Attack Surface:**

- Only essential runtime packages (no build tools, no shells besides bash)
- No SSH daemon, no debugging tools in production image
- Read-only filesystem for application code

---

## Process Model

### Multi-Process Orchestration

**Process Tree:**

```
main.py (PID 1)
├── dashboard/server.py (Flask, PID 123)
│   └── Werkzeug workers (threads)
├── core/client_pipeline.py (client1, PID 124)
├── core/client_pipeline.py (client2, PID 125)
├── core/client_pipeline.py (client3, PID 126)
└── ... (up to 5 client processes)
```

**Process Isolation:**

- **Separate Python Processes:** Each client in independent `subprocess.Popen()`
- **Independent Logs:** Stdout/stderr to `logs/<client_id>.log`
- **Independent Status:** JSON file per client in `.multi_process_status/`
- **No Shared State:** Except status files (single-writer pattern)

**Parallelism:**

- **Maximum Clients:** 5 (configurable limit to prevent resource exhaustion)
- **Staggered Launch:** 10s (deep) or 2s (fast) delay between client starts
- **Anti-Thundering-Herd:** Random initial offset (0-15s) for API rate limit protection

---

### IPC via Status Files

**Communication Pattern:**

```
Client Process (Writer)              Dashboard (Reader)
─────────────────────                ────────────────────
client_pipeline.py                   dashboard/server.py
        │                                     │
        │ write                               │ read (polling)
        ▼                                     ▼
 .multi_process_status/merck_test.json (shared file)
```

**Single-Writer Pattern:**

- **Writer:** One client process per status file
- **Reader:** Dashboard polls all status files every 2s (via `/status` endpoint)
- **No Locking Needed:** Single writer guarantees no race conditions
- **Atomic Writes:** JSON written in full, then file replaced (Python's file write semantics)

**Status File Lifecycle:**

1. **Initialization:** `main.py` creates initial status file (PENDING)
2. **Updates:** `client_pipeline.py` updates via `update_status()` method
3. **Completion:** Final update sets `status=COMPLETE` and `quality_score`
4. **Cleanup:** Files persist until next `main.py` run (dashboard history)

---

### Graceful Shutdown

**Signal Handling:**

```python
# main.py
def signal_handler(sig, frame):
    logger.warning(f"Received signal {sig}")
    if global_manager:
        global_manager.cleanup()
    os._exit(1)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

**Cleanup Sequence:**

1. **Terminate Client Processes:**
   ```python
   for process in self.client_processes:
       if process.poll() is None:  # Still running
           process.terminate()     # Send SIGTERM
           time.sleep(1)           # Wait 1 second
           if process.poll() is None:
               process.kill()      # Force kill with SIGKILL
   ```

2. **Terminate Dashboard:**
   ```python
   if self.dashboard_process and self.dashboard_process.poll() is None:
       self.dashboard_process.terminate()
       time.sleep(2)  # Give Flask time to flush logs
       if self.dashboard_process.poll() is None:
           self.dashboard_process.kill()
   ```

3. **Force Exit:**
   ```python
   os._exit(exit_code)  # Immediate termination (no Python cleanup handlers)
   ```

**Container Shutdown:**

```bash
# Podman sends SIGTERM to PID 1 (main.py)
podman stop <container-id>

# main.py catches SIGTERM → cleanup() → os._exit()
# Container stops within 2-3 seconds
```

---

## Data Flow Architecture

### End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  INPUT SOURCES                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Google Drive Folder          Local Folder           vars.py Config    │
│  ├─ PDFs                      ├─ PDFs                ├─ client_name    │
│  ├─ Google Docs → PDF         ├─ Office docs         ├─ industry       │
│  ├─ Sheets → PDF              └─ Images              └─ subsegments    │
│  └─ Slides → PDF                                                       │
│                                                                         │
└────────────┬────────────────────────────┬───────────────────┬───────────┘
             │                            │                   │
             │ DriveManager               │ Local access      │ Config load
             │ (OAuth 2.0 + caching)      │                   │
             ▼                            ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CONSOLIDATION LAYER                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FastPDFConsolidator                                                   │
│  ├─ Convert all files → PDF                                            │
│  ├─ Merge into single PDF with TOC                                     │
│  ├─ Change detection (Drive API timestamps)                            │
│  └─ Output: {ClientName}-Consolidated-{timestamp}.pdf                  │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Upload to NotebookLM
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  NOTEBOOKLM LAYER                                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Notebook: DEV_{client_id}-TEST                                        │
│  ├─ Sources:                                                            │
│  │   ├─ Consolidated PDF (client data)                                 │
│  │   └─ Web URLs (research imports: 20-180 sources)                    │
│  │                                                                      │
│  ├─ Research Queries (Ask Prompts):                                    │
│  │   ├─ ask_prompt_01.txt: Industry analysis                           │
│  │   └─ ask_prompt_02.txt: Competitive landscape                       │
│  │                                                                      │
│  ├─ Analysis Notes (Chat Prompts):                                     │
│  │   ├─ Industry Analysis & Customer Business Profile                  │
│  │   ├─ Innovation Assessment & Executive Summary                      │
│  │   ├─ Technology Partners & Value Propositions                       │
│  │   ├─ Strategic Ideas & How Might We Statements                      │
│  │   ├─ Account Team & Partner Onboarding                              │
│  │   └─ Comprehensive Account Plan                                     │
│  │                                                                      │
│  └─ Artifacts:                                                          │
│      └─ Mind Map (visual overview)                                     │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Export / Access via NotebookLM UI
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  OUTPUT ARTIFACTS                                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NotebookLM Notebook (cloud)       Quality Score      Status Dashboard │
│  ├─ 6 Notes (markdown)             ├─ 0-10 rating    ├─ Real-time     │
│  ├─ 20-180 Sources                 ├─ Completeness   └─ Progress       │
│  └─ Mind Map                       └─ Metrics                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Variable Substitution Flow

**Prompt Templates:**

```
ask_prompt_01.txt (Research)
───────────────────────────────
Analyze the $industry industry, focusing on $subsegments.
Identify trends and challenges facing $name.
```

**Substitution Pipeline:**

```python
# 1. Read template
prompt_text = prompt_file.read_text()

# 2. Substitute variables
prompt_text = prompt_text.replace('$name', client_name)
prompt_text = prompt_text.replace('$industry', industry)
prompt_text = prompt_text.replace('$subsegments', subsegments)
prompt_text = prompt_text.replace('$persona', persona)  # Chat prompts only

# 3. Create temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
    tmp.write(prompt_text)
    tmp_path = tmp.name

# 4. Execute with substituted prompt
subprocess.run(["notebooklm", "ask", "--prompt-file", tmp_path, ...])

# 5. Cleanup
Path(tmp_path).unlink()
```

**Variable Sources:**

- `$name` → `{client_id}_name` from `vars.py`
- `$industry` → AI detection or `{client_id}_industry` from `vars.py`
- `$subsegments` → AI detection or `{client_id}_subsegments` from `vars.py`
- `$persona` → Global `persona` setting from `vars.py` (default: "Red Hat solutions architect")

---

## Security Model

### Credential Protection

**NotebookLM Credentials:**

```
Host Machine:
~/.notebooklm/profiles/default/storage_state.json
├─ Permissions: 600 (owner read/write only)
└─ Contains: OAuth cookies, session tokens

Container:
/opt/app-root/src/.notebooklm/profiles/default/storage_state.json
├─ Mounted from named volume: project-ape-credentials
├─ Permissions: 600 (apeuser read/write only)
└─ Never copied to image layers
```

**Google Drive Credentials:**

```
Host Machine:
~/.project-ape/drive_credentials.json    # OAuth client secret
~/.project-ape/drive_token.json          # Access/refresh tokens
├─ Permissions: 600
└─ Not used in containers (Drive download on host only)
```

**API Keys:**

```bash
# Local development: .env file (gitignored)
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Container runtime: environment variables
podman run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY ...

# Production: Secret management (AWS Secrets Manager, Vault, etc.)
# Never hardcoded in code or image layers
```

---

### File Permission Strategy

**Container Filesystem:**

```
/app/                                     # 750 (owner rwx, group rx)
├── core/                                 # 755 (owner rwx, group rx, other rx)
├── dashboard/                            # 755
├── logs/                                 # 770 (owner rwx, group rwx) - WRITABLE
├── .multi_process_status/                # 770 - WRITABLE
├── client_data/                          # 750 (mounted read-only via :ro)
├── docs_generated/                       # 770 - WRITABLE
├── main.py                               # 644 (owner rw, group r)
├── vars.py                               # 644 (mounted read-only)
└── container-entrypoint.sh               # 755 (executable)
```

**Host Mount Permissions:**

```bash
# Logs directory (must be writable by UID 1000)
mkdir -p logs docs_generated
chown -R 1000:1000 logs docs_generated
chmod 770 logs docs_generated

# Or for rootless podman:
podman unshare chown -R 0:0 logs docs_generated
```

---

### Container Hardening

**1. Non-Root User:**

```dockerfile
# Create dedicated user
RUN useradd -m -u 1000 -s /bin/bash apeuser

# Switch context
USER apeuser

# All processes run as UID 1000 (not root)
```

**2. Read-Only Root Filesystem (Optional):**

```bash
# Run container with read-only root
podman run --read-only \
  -v ./logs:/app/logs:z \
  -v ./docs_generated:/app/docs_generated:z \
  ...

# Only /app/logs and /app/docs_generated are writable
```

**3. Resource Limits:**

```bash
# CPU limits (2 cores)
podman run --cpus=2 ...

# Memory limits (4 GB)
podman run --memory=4g ...

# Prevent fork bombs
podman run --pids-limit=100 ...
```

**4. Network Isolation:**

```bash
# Disable network access (if running offline)
podman run --network=none ...

# Custom network with firewall rules
podman network create --subnet 172.20.0.0/16 ape-network
podman run --network ape-network ...
```

**5. Drop Capabilities:**

```bash
# Remove all capabilities except essential ones
podman run \
  --cap-drop=ALL \
  --cap-add=CHOWN \
  --cap-add=SETGID \
  --cap-add=SETUID \
  ...
```

---

### Secret Management

**Environment Variables (Recommended):**

```bash
# Local development
export ANTHROPIC_API_KEY=$(cat ~/.secrets/anthropic.key)
./ape-run.sh

# Container runtime
podman run -e ANTHROPIC_API_KEY=$(cat ~/.secrets/anthropic.key) ...
```

**Secret Vaults (Production):**

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id project-ape/anthropic-api-key \
  --query SecretString --output text

# HashiCorp Vault
vault kv get -field=api_key secret/project-ape/anthropic
```

**Podman Secrets (Podman 4.0+):**

```bash
# Create secret
echo "sk-ant-..." | podman secret create anthropic-api-key -

# Use secret in container
podman run --secret anthropic-api-key,type=env,target=ANTHROPIC_API_KEY ...
```

**Never:**

- Hardcode secrets in `vars.py`, `main.py`, or any Python files
- Commit secrets to Git (use `.gitignore` for `.env`, credentials)
- Mount `.env` files in containers (use environment variables instead)
- Embed secrets in container image layers (use runtime injection)

---

## Deployment Architecture

### Local Development

**Prerequisites:**

```bash
# Python 3.11+
python3 --version

# NotebookLM CLI
pip install notebooklm-py

# Google Drive API dependencies (optional)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# LibreOffice (for Office doc conversion)
# macOS:
brew install libreoffice
# Linux:
apt-get install libreoffice-core-nogui
```

**Setup:**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Project-APE-dev.git
cd Project-APE-dev

# 2. Setup virtual environment
./setup-environment.sh

# 3. Authenticate with NotebookLM
notebooklm login

# 4. Configure clients
cp example-vars.py vars.py
# Edit vars.py with your client details

# 5. Run pipeline
./ape-run.sh --vars ./vars.py --clients example_client --mode fast
```

**Directory Structure:**

```
Project-APE-dev/
├── core/                      # Pipeline modules
├── dashboard/                 # Flask dashboard
├── client_data/               # Local client files (optional)
├── docs_generated/            # Output documents
├── logs/                      # Execution logs
├── .multi_process_status/     # Status JSON files
├── main.py                    # Orchestrator
├── vars.py                    # Configuration (user-created)
├── example-vars.py            # Template
├── ape-run.sh                 # Local launcher
└── requirements.txt           # Python dependencies
```

---

### Container Deployment

**Build Container:**

```bash
# Build multi-arch image
podman build \
  -t project-ape:latest \
  -f developer-docs/Containerfile.debian \
  .

# Tag for registry
podman tag project-ape:latest quay.io/jasoande/project_ape/project-ape:v4.0.1
```

**Push to Registry:**

```bash
# Login to registry
podman login quay.io

# Push image
podman push quay.io/jasoande/project_ape/project-ape:v4.0.1
podman push quay.io/jasoande/project_ape/project-ape:latest
```

**Run Container:**

```bash
# 1. Setup credentials volume (one-time)
./setup-credentials.sh

# 2. Run container
./ape-run.sh --vars ./vars.py --clients client1,client2 --mode fast

# Or manually:
podman run \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./client_data:/app/client_data:ro,z \
  -v ./docs_generated:/app/docs_generated:z \
  -v ./logs:/app/logs:z \
  -p 8765:8765 \
  --name project-ape-run \
  quay.io/jasoande/project_ape/project-ape:latest \
  python3 main.py --mode fast
```

**Container Lifecycle:**

```bash
# View running containers
podman ps | grep project-ape

# View logs
podman logs -f project-ape-run

# Stop container
podman stop project-ape-run

# Remove container
podman rm project-ape-run

# Remove image
podman rmi quay.io/jasoande/project_ape/project-ape:latest
```

---

### Cloud Deployment (AWS EC2)

**EC2 Instance Setup:**

```bash
# 1. Launch EC2 instance
# - Instance type: t3.medium (2 vCPU, 4 GB RAM minimum)
# - OS: Amazon Linux 2023 or Ubuntu 22.04
# - Storage: 20 GB SSD minimum
# - Security group: Allow 8765 (dashboard), 22 (SSH)

# 2. Install dependencies
sudo yum install -y podman  # Amazon Linux
# or
sudo apt-get install -y podman  # Ubuntu

# 3. Clone repository
git clone https://github.com/yourusername/Project-APE-dev.git
cd Project-APE-dev

# 4. Setup credentials
notebooklm login  # Requires X11 forwarding or local setup
./setup-credentials.sh

# 5. Configure clients
cp example-vars.py vars.py
# Edit vars.py

# 6. Run container
./ape-run.sh --vars ./vars.py --clients client1 --mode fast
```

**Systemd Service (Auto-start):**

```ini
# /etc/systemd/system/project-ape.service
[Unit]
Description=Project APE - Account Planning Engine
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/Project-APE-dev
ExecStart=/usr/bin/podman run \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -v /home/ec2-user/Project-APE-dev/vars.py:/app/vars.py:ro,z \
  -v /home/ec2-user/Project-APE-dev/docs_generated:/app/docs_generated:z \
  -v /home/ec2-user/Project-APE-dev/logs:/app/logs:z \
  -p 8765:8765 \
  --name project-ape-service \
  --rm \
  quay.io/jasoande/project_ape/project-ape:latest \
  python3 main.py --mode fast
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable Service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ape
sudo systemctl start project-ape
sudo systemctl status project-ape
```

---

### Multi-Architecture Support

**Build for Multiple Architectures:**

```bash
# Create buildx builder (Docker)
docker buildx create --name multiarch-builder --use

# Build multi-arch image
docker buildx build \
  --platform linux/x86_64,linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:latest \
  -f developer-docs/Containerfile.debian \
  --push \
  .

# Or with Podman (requires qemu)
podman build \
  --platform linux/x86_64,linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:latest \
  -f developer-docs/Containerfile.debian \
  .
```

**Supported Platforms:**

- **linux/x86_64:** Intel/AMD 64-bit (EC2 t3.*, m5.*, c5.*)
- **linux/arm64:** ARM 64-bit (EC2 t4g.*, m6g.*, Graviton processors)

---

## Extension Points

### 1. Adding New Prompts

**Research Prompts (Ask):**

```bash
# 1. Create new prompt file
touch ask_prompt_03.txt

# 2. Write prompt with variable substitution
cat > ask_prompt_03.txt <<EOF
Analyze the technology landscape for $name in the $industry industry.
Focus on emerging technologies in $subsegments.
Identify digital transformation initiatives and innovation programs.
EOF

# 3. Run pipeline - automatically detected
./ape-run.sh --vars ./vars.py --clients example_client --mode fast
```

**Analysis Prompts (Chat):**

```bash
# 1. Create new consolidated prompt
touch chat_prompt_consolidated_07.txt

# 2. Write prompt with persona context
cat > chat_prompt_consolidated_07.txt <<EOF
You are a $persona analyzing $name.

Based on all sources, create a risk mitigation strategy addressing:
- Technical risks
- Business risks
- Competitive risks
- Market risks

Format as a comprehensive risk matrix.
EOF

# 3. Update note titles in client_pipeline.py
# Edit core/client_pipeline.py, line ~800:
note_titles = {
    # ... existing titles
    'chat_prompt_consolidated_07.txt': 'Risk Mitigation Strategy',
}

# 4. Run pipeline
./ape-run.sh --vars ./vars.py --clients example_client --mode fast
```

**Prompt Naming Convention:**

- Research: `ask_prompt_##.txt` (lexicographically sorted)
- Analysis: `chat_prompt_consolidated_##.txt` (lexicographically sorted)
- Variables: `$name`, `$industry`, `$subsegments`, `$persona`

---

### 2. Custom Processors

**Adding a New Pipeline Phase:**

```python
# core/client_pipeline.py

class ClientPipeline:
    def execute(self) -> bool:
        try:
            # ... existing phases
            
            # Step 8: Custom Phase
            self._run_custom_analysis()
            self.update_status("Custom analysis complete", 98)
            
            # ... existing phases
        except Exception as e:
            # ... error handling
    
    def _run_custom_analysis(self):
        """Custom analysis phase."""
        logger.info(f"[{self.client_id}] Running custom analysis...")
        
        # Example: Generate executive summary
        result = subprocess.run([
            "notebooklm", "ask",
            "--prompt", f"Create a 2-page executive summary for {self.client_name}",
            "-n", self.notebook_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Save summary to file
            summary_file = self.project_root / "docs_generated" / self.client_id / "executive_summary.md"
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            summary_file.write_text(result.stdout)
            
            logger.info(f"[{self.client_id}] ✅ Executive summary generated")
```

**Adding Custom Managers:**

```python
# core/custom_manager.py

class CustomManager:
    """Handles custom integration."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
    
    def process(self, data):
        """Process custom data."""
        # Implementation
        pass

# Usage in client_pipeline.py
from core.custom_manager import CustomManager

class ClientPipeline:
    def __init__(self, ...):
        # ... existing managers
        self.custom_manager = CustomManager(self.client_id)
    
    def _run_custom_analysis(self):
        result = self.custom_manager.process(self.client_data)
```

---

### 3. Alternative Authentication Methods

**Service Account Authentication (Google Drive):**

```python
# core/drive_manager.py

def _service_account_authenticate(self) -> Credentials:
    """Authenticate using service account JSON key."""
    from google.oauth2 import service_account
    
    service_account_file = Path.home() / '.project-ape' / 'service-account.json'
    
    creds = service_account.Credentials.from_service_account_file(
        str(service_account_file),
        scopes=self.SCOPES
    )
    
    return creds

# Update authenticate() method
def authenticate(self) -> bool:
    try:
        # Check for service account first
        service_account_file = Path.home() / '.project-ape' / 'service-account.json'
        if service_account_file.exists():
            creds = self._service_account_authenticate()
        else:
            # Fall back to OAuth
            creds = self._oauth_authenticate()
        
        self.service = build('drive', 'v3', credentials=creds)
        return True
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return False
```

**API Key Authentication (Custom APIs):**

```python
# core/custom_api_manager.py

import os
from typing import Dict

class CustomAPIManager:
    """Manages custom API authentication."""
    
    def __init__(self):
        self.api_key = os.getenv('CUSTOM_API_KEY')
        if not self.api_key:
            raise ValueError("CUSTOM_API_KEY environment variable required")
    
    def make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make authenticated API request."""
        import requests
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()
```

---

### 4. Custom Quality Metrics

**Extending Quality Score Calculation:**

```python
# core/client_pipeline.py

def _calculate_quality_score(self) -> float:
    """Calculate quality score with custom metrics."""
    score = 0.0
    
    # Existing metrics (0-10 total)
    # ... sources count, notes, mind map
    
    # Custom metric 1: Source diversity (0-2 pts)
    sources = self.source_manager.list_sources()
    domains = set()
    for source in sources:
        if 'url' in source:
            from urllib.parse import urlparse
            domains.add(urlparse(source['url']).netloc)
    
    # Award points for source diversity
    if len(domains) >= 10:
        score += 2.0
    elif len(domains) >= 5:
        score += 1.0
    
    # Custom metric 2: Content freshness (0-1 pt)
    from datetime import datetime, timedelta
    
    recent_sources = 0
    for source in sources:
        if 'created_at' in source:
            created = datetime.fromisoformat(source['created_at'])
            if datetime.now() - created < timedelta(days=30):
                recent_sources += 1
    
    if recent_sources >= 10:
        score += 1.0
    elif recent_sources >= 5:
        score += 0.5
    
    # Normalize to 0-10 scale (adjust weights)
    # Original score: 0-10, custom metrics: 0-3
    # New total: 0-13, normalize to 0-10
    normalized_score = (score / 13.0) * 10.0
    
    return round(normalized_score, 1)
```

---

## Performance & Scalability

### Timing Optimization

**Mode Comparison:**

| Mode  | Duration | Sources | Retry Rate | Use Case |
|-------|----------|---------|------------|----------|
| Fast  | 10-15 min | 20-40 | ~5% | Rapid prototyping, demos |
| Deep  | 30-35 min | 90-180 | ~30% | Production, comprehensive analysis |
| Update | 5-10 min | +10-20 | ~10% | Incremental refresh |

**Timing Configuration:**

```python
# vars.py

# Fast mode timing (aggressive)
TIMINGS = {
    'ask_prompt_delay': (8.0, 12.0),        # 8-12s between research queries
    'chat_prompt_delay': (5.0, 8.0),        # 5-8s between chat prompts
    'source_processing_wait': 30.0,         # 30s PDF processing
    'research_import_wait': (15.0, 25.0),   # 15-25s source import
}

# Deep mode timing (conservative)
DEEP_TIMINGS = {
    'ask_prompt_delay': (15.0, 25.0),       # 15-25s between research queries
    'chat_prompt_delay': (10.0, 15.0),      # 10-15s between chat prompts
    'source_processing_wait': 45.0,         # 45s PDF processing
    'research_import_wait': (30.0, 45.0),   # 30-45s source import
}
```

**Anti-Rate-Limit Strategy:**

```python
# Staggered launch (main.py)
stagger_delay = 10 if mode == "deep" else 2
for i, client_id in enumerate(clients):
    process = manager.start_client_process(client_id, mode)
    manager.client_processes.append(process)
    
    if i < len(clients) - 1:
        time.sleep(stagger_delay)

# Random jitter (client_pipeline.py)
delay = random.uniform(0, 15 if mode == "deep" else 12)
time.sleep(delay)
```

---

### Resource Limits

**Memory Usage:**

- **Per Client Process:** ~500 MB - 1 GB
- **Dashboard Server:** ~200 MB
- **Total (5 clients):** ~3-5 GB RAM

**CPU Usage:**

- **PDF Consolidation:** High CPU (LibreOffice conversion)
- **Research Phase:** Low CPU (network I/O bound)
- **Analysis Phase:** Low CPU (API calls)

**Disk I/O:**

- **Drive Cache:** ~100-500 MB per client
- **Logs:** ~10-50 MB per client
- **Consolidated PDFs:** ~10-100 MB per client

**Container Resource Recommendations:**

```bash
# Minimum resources (1-2 clients)
podman run --cpus=2 --memory=4g ...

# Recommended resources (3-5 clients)
podman run --cpus=4 --memory=8g ...

# High-performance resources (5+ clients, deep mode)
podman run --cpus=8 --memory=16g ...
```

---

### Scalability Limits

**Current Limits:**

- **Maximum Parallel Clients:** 5 (hard-coded in orchestrator)
- **Maximum Sources per Notebook:** ~200 (NotebookLM API limit)
- **Maximum Prompts:** Unlimited (file-based discovery)

**Scaling Beyond 5 Clients:**

```python
# main.py

# Option 1: Batch processing
all_clients = config.clients  # 20 clients
batch_size = 5

for batch_start in range(0, len(all_clients), batch_size):
    batch = all_clients[batch_start:batch_start + batch_size]
    
    # Run batch
    for client_id in batch:
        process = manager.start_client_process(client_id, mode)
        manager.client_processes.append(process)
    
    # Wait for batch completion
    manager.monitor_processes()
    
    # Cleanup and prepare for next batch
    manager.cleanup()
    time.sleep(60)  # Cooldown between batches
```

**Horizontal Scaling (Multi-Instance):**

```bash
# Run multiple container instances with different client sets

# Instance 1: Clients 1-5
podman run -e CLIENTS="client1,client2,client3,client4,client5" ...

# Instance 2: Clients 6-10
podman run -e CLIENTS="client6,client7,client8,client9,client10" ...

# Aggregate results via shared volume
-v ./all_results:/app/docs_generated:z
```

---

## Appendix

### Key Files Reference

**Core Application:**

- `main.py` - Multi-process orchestrator
- `core/client_pipeline.py` - Single-client workflow
- `core/drive_manager.py` - Google Drive integration
- `core/notebook_manager.py` - NotebookLM notebook management
- `core/source_manager.py` - Source import and deduplication
- `core/auth_manager.py` - Authentication validation
- `dashboard/server.py` - Flask dashboard server

**Configuration:**

- `vars.py` - Client definitions and settings (user-created)
- `example-vars.py` - Configuration template
- `requirements.txt` - Python dependencies
- `.env` - API keys (local development, gitignored)

**Containerization:**

- `developer-docs/Containerfile.debian` - Multi-stage Dockerfile
- `container-entrypoint.sh` - Container startup script
- `setup-credentials.sh` - Credential volume setup

**Launchers:**

- `ape-run.sh` - CLI launcher for local and container modes
- `setup-environment.sh` - Virtual environment setup

### Architecture Diagrams Summary

1. **System Overview:** 10,000-foot view of layers and components
2. **Process Tree:** Multi-process orchestration hierarchy
3. **Data Flow:** End-to-end source processing pipeline
4. **Authentication Flow:** OAuth 2.0 for NotebookLM and Drive
5. **Container Architecture:** Multi-stage build and runtime

### Version History

- **v4.0.1 (2026-06-30):** OAuth race condition fix, improved retry logic
- **v4.0.0:** Major update with Drive integration and industry detection
- **v3.2.2:** Auth retry and lock contention fix
- **v3.0.4:** Consolidated prompts (12 → 6)
- **v2.0.0:** Containerization and multi-architecture support
- **v1.0.0:** Initial release

---

**END OF ARCHITECTURE.md**
