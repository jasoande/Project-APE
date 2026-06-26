<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
</div>

# API Reference - Project APE

**Technical reference for advanced users, developers, and CI/CD integration**

Version: 3.2.2  
Last Updated: June 25, 2026

---

## Table of Contents

- [Overview](#overview)
- [Configuration File (vars.py)](#configuration-file-varspy)
- [Dashboard API Endpoints](#dashboard-api-endpoints)
- [Command-Line Interface](#command-line-interface)
- [Container Usage](#container-usage)
- [Environment Variables](#environment-variables)
- [File Locations](#file-locations)
- [Status File Format](#status-file-format)
- [Log Format](#log-format)
- [Core Modules](#core-modules)
- [Advanced Configuration](#advanced-configuration)

---

## Overview

Project APE provides three interfaces for automation:

1. **Web Dashboard API** - RESTful endpoints for programmatic control
2. **Command-Line Interface** - Shell scripts and Python entry points
3. **Container Runtime** - Docker/Podman for isolated execution

This document covers all technical details for integrating Project APE into automated workflows.

---

## Configuration File (vars.py)

### File Location

```
/Users/jasona/test/Project-APE-dev/vars.py
```

### Structure

```python
from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATIONS
# ==============================================================================

clients = [
    "client_1",
    "client_2"
]

# Client 1 Configuration
client_1_name = "Client Name"
client_1_folder = "https://drive.google.com/drive/folders/FOLDER_ID"
client_1_industry = "industry name"  # Optional: auto-detect if blank
client_1_subsegments = "subsegment1, subsegment2"  # Optional

# Client 2 Configuration
client_2_name = "Another Client"
client_2_folder = "https://drive.google.com/drive/folders/FOLDER_ID_2"
client_2_industry = ""
client_2_subsegments = ""

# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

persona = "solutions architect"
default_mode = "fast"  # "fast" or "deep"

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds

# ==============================================================================
# EXECUTION TIMING PROFILES
# ==============================================================================

# FAST MODE - 15-20 minutes per workflow
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

# DEEP MODE - 45-60 minutes per workflow
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
# QUALITY THRESHOLDS
# ==============================================================================

QUALITY_THRESHOLDS = {
    'min_sources': 15,
    'required_notes': 6,
    'min_quality_score': 8.5,
}

# ==============================================================================
# GOOGLE DRIVE CONFIGURATION
# ==============================================================================

DRIVE_CONFIG = {
    'cache_enabled': True,
    'cache_ttl_hours': 168,  # 7 days
    'download_timeout': 300,
}

# ==============================================================================
# GEMINI AI ORCHESTRATION
# ==============================================================================

GEMINI_AGENT_CONFIG = {
    'enabled': True,
    'model': 'gemini-2.0-flash-exp',
    'temperature': 0.2,
    'max_retries': 5,
    'retry_base_delay': 10.0,
    'timeout': 60,
    'enable_error_analysis': True,
    'enable_quality_validation': True,
    'enable_self_healing': True,
    'quality_target': 8.5,
}

# ==============================================================================
# PATHS (Container vs Local)
# ==============================================================================

# Container paths (when running in Docker/Podman)
# STATUS_DIR = Path('/app/.multi_process_status')
# LOGS_DIR = Path('/app/logs')

# Local paths (when running in venv)
# STATUS_DIR = Path(__file__).parent / '.multi_process_status'
# LOGS_DIR = Path(__file__).parent / 'logs'
```

### Client Configuration Options

#### Required Fields

- `clients` - List of client IDs (must match client variable prefixes)
- `{client_id}_name` - Human-readable client name
- `{client_id}_folder` - Google Drive folder URL or local path

#### Optional Fields

- `{client_id}_industry` - Industry classification (auto-detected if blank)
- `{client_id}_subsegments` - Comma-separated subsegments (auto-detected if blank)

### Validation Rules

1. **Client ID**: Lowercase alphanumeric + underscores only
2. **Folder URL**: Must match `https://drive.google.com/drive/folders/{ID}` or `drive://{ID}`
3. **Local Path**: Absolute path when not using Drive
4. **Name**: Required, non-empty string
5. **Industry**: Optional string
6. **Subsegments**: Optional comma-separated string

---

## Dashboard API Endpoints

Base URL: `http://localhost:8765`

### GET /

**Main Dashboard**

Returns HTML dashboard with real-time monitoring.

### GET /configure

**Configuration UI**

Returns HTML configuration page for setting up clients.

### GET /status

**Workflow Status (JSON)**

Returns current status of all clients.

**Response:**

```json
{
  "total": 3,
  "running": 1,
  "complete": 2,
  "failed": 0,
  "mode": "fast",
  "run_id": "1719345678",
  "clients": [
    {
      "name": "Client Name",
      "token": "client_id",
      "step": "Uploading sources...",
      "progress": 45,
      "status": "RUNNING",
      "notebook_id": "abc123",
      "mode": "fast",
      "last_update": 1719345700.123,
      "start_time": 1719345600.000,
      "quality_score": null,
      "plan_link": null,
      "log_file": "/path/to/logs/client_id.log",
      "run_id": "1719345678"
    }
  ]
}
```

### GET /logs/overall

**Stream Combined Logs (SSE)**

Server-Sent Events stream of all log output.

**Example:**

```javascript
const eventSource = new EventSource('/logs/overall');
eventSource.onmessage = (event) => {
  console.log(event.data);
};
```

### POST /api/start-workflow

**Start Workflow Execution**

Triggers pipeline execution in background.

**Request Body:**

```json
{
  "command": "./run-workflow.sh fast",
  "mode": "fast",
  "clients": ["client1", "client2"],
  "dashboard_url": "http://localhost:8765"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Workflow started in background",
  "dashboard_url": "http://localhost:8765"
}
```

### POST /api/save-config

**Save Configuration**

Saves client configuration to vars.py.

**Request Body:**

```json
{
  "clients": [
    {
      "id": "client1",
      "name": "Client Name",
      "folder": "https://drive.google.com/drive/folders/ABC123",
      "industry": "technology",
      "subsegments": "cloud, AI"
    }
  ],
  "settings": {
    "persona": "solutions architect",
    "default_mode": "fast",
    "dashboard_port": 8765
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Configuration saved successfully",
  "backup_created": "/path/to/vars.py.backup.20260625_140530"
}
```

### GET /api/check-auth-status

**Check NotebookLM Authentication**

Returns authentication status.

**Response:**

```json
{
  "success": true,
  "authenticated": true,
  "profile": "default",
  "checked_at": 1719345678.123
}
```

### POST /api/notebooklm-login

**Trigger NotebookLM Login**

Initiates OAuth flow (opens browser).

**Response:**

```json
{
  "success": true,
  "message": "Login flow initiated. A browser window should open for authentication.",
  "instructions": [
    "A browser window should open automatically for Google login.",
    "After login completes, credentials will automatically sync to container."
  ]
}
```

### POST /api/refresh-sources

**Refresh Drive Cache**

Force refresh of Google Drive files for specified clients.

**Request Body:**

```json
{
  "clients": ["client1", "client2"]  // Optional: all clients if omitted
}
```

**Returns SSE Stream:**

```
data: {"type": "info", "message": "Starting refresh for 2 client(s)..."}
data: {"type": "progress", "current": 1, "total": 2, "client": "Client Name"}
data: {"type": "success", "message": "✅ Client Name: 15 files refreshed"}
data: {"type": "complete", "success": true, "total_clients": 2, "successful": 2, "failed": 0, "total_files": 30}
```

### GET /api/cache-stats

**Cache Statistics**

Returns Drive cache statistics for all clients.

**Response:**

```json
{
  "success": true,
  "stats": [
    {
      "client_id": "client1",
      "client_name": "Client Name",
      "type": "drive",
      "cached": true,
      "size_bytes": 52428800,
      "size_mb": 50.0,
      "file_count": 15,
      "last_refresh": "2026-06-25T14:30:00",
      "age": "2h ago"
    }
  ],
  "total_size_mb": 150.5,
  "total_files": 45,
  "cache_path": "/Users/username/.project-ape/drive_cache"
}
```

### POST /api/clear-cache

**Clear Drive Cache**

Deletes cached Drive files for specified clients.

**Request Body:**

```json
{
  "clients": ["client1"]  // Optional: all clients if omitted
}
```

**Response:**

```json
{
  "success": true,
  "message": "Cleared cache for 1 client(s)",
  "cleared_count": 1,
  "cleared_size_mb": 50.0
}
```

### GET /api/oauth-status

**OAuth Status**

Check if OAuth credentials exist for Drive access.

**Response:**

```json
{
  "credentials_exist": true,
  "token_exist": true,
  "authenticated": true,
  "email": "Authenticated",
  "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
}
```

### POST /api/upload-oauth-credentials

**Upload OAuth Credentials**

Upload client_secret JSON file from Google Cloud Console.

**Request:**

Multipart form data with `file` field containing JSON.

**Response:**

```json
{
  "success": true,
  "message": "Credentials uploaded successfully",
  "client_id": "123456789012-abc..."
}
```

### POST /api/shutdown

**Shutdown Server**

Gracefully shuts down dashboard and container.

**Response:**

```json
{
  "success": true,
  "message": "Server shutting down..."
}
```

---

## Command-Line Interface

### Main Orchestrator

**File:** `main.py`

**Usage:**

```bash
python3 main.py [options]
```

**Options:**

- `--mode {fast,deep,update}` - Execution mode (default: fast)
- `--clients CLIENT [CLIENT ...]` - Specific clients to run
- `--no-dashboard` - Disable web dashboard
- `--refresh` - Force refresh Drive cache

**Examples:**

```bash
# Fast mode, all clients, with dashboard
python3 main.py --mode fast

# Deep mode, specific clients
python3 main.py --mode deep --clients merck organon

# Fast mode, force refresh cache
python3 main.py --mode fast --refresh

# Headless mode (no dashboard)
python3 main.py --mode fast --no-dashboard
```

### Local Mode Launcher

**File:** `run-workflow.sh`

**Usage:**

```bash
./run-workflow.sh {fast|deep} [--refresh] [clients...]
```

**Examples:**

```bash
# Fast mode, all clients
./run-workflow.sh fast

# Deep mode, specific clients
./run-workflow.sh deep merck organon

# Force refresh cache
./run-workflow.sh fast --refresh
```

**Requirements:**

- Virtual environment at `~/.project-ape-venv`
- NotebookLM CLI installed
- Activated credentials

### Container Mode Launcher

**File:** `launch_ape.sh`

**Usage:**

```bash
./launch_ape.sh {fast|deep} [--refresh] [clients...]
```

**Examples:**

```bash
# Fast mode, all clients
./launch_ape.sh fast

# Deep mode with cache refresh
./launch_ape.sh deep --refresh

# Specific clients only
./launch_ape.sh fast merck organon
```

**Features:**

- Auto-detects architecture (amd64/arm64)
- Selects appropriate container runtime (podman/docker)
- Mounts credentials volume
- Port forwarding for dashboard
- Auto-shutdown after completion

### Workflow Detection

**File:** `workflow_detector.py`

**Usage:**

```bash
python3 workflow_detector.py [--json] [--config PATH]
```

**Output:**

```json
{
  "mode": "fast",
  "clients": ["merck", "organon"],
  "client_count": 2,
  "estimated_minutes_min": 15,
  "estimated_minutes_max": 20,
  "time_range": "15-20 minutes (all 2 clients in parallel)",
  "command": "./run-workflow.sh fast merck organon",
  "drive_enabled": true,
  "cache_enabled": true,
  "dashboard_port": 8765,
  "dashboard_url": "http://localhost:8765"
}
```

### Dashboard Server

**File:** `dashboard/server.py`

**Usage:**

```bash
python3 dashboard/server.py
```

**Environment:**

- `DASHBOARD_PORT` - Port number (default: 8765)

---

## Container Usage

### Image Registry

**Location:** `quay.io/jasoande/project_ape`

**Tags:**

- `latest` - Latest ARM64 build (Mac development)
- `3.0.5-amd64` - Stable AMD64 build (production)
- `3.0.5-arm64` - Stable ARM64 build

### Pull Image

```bash
# Auto-detect architecture
podman pull quay.io/jasoande/project_ape:latest

# Specific architecture
podman pull quay.io/jasoande/project_ape:3.0.5-amd64
```

### Run Container

**Manual Execution:**

```bash
podman run -d \
  --name project-ape \
  -p 8765:8765 \
  -v project-ape-credentials:/root/.config \
  -v $(pwd):/app \
  quay.io/jasoande/project_ape:latest \
  python3 main.py --mode fast
```

**With Launcher Script:**

```bash
./launch_ape.sh fast
```

### Volume Mounts

1. **Credentials Volume:** `project-ape-credentials:/root/.config`
   - Contains NotebookLM credentials
   - OAuth tokens
   - Service account keys

2. **Working Directory:** `$(pwd):/app`
   - Project files
   - vars.py configuration
   - Logs and status files

### Container Environment

**Paths:**

- Working directory: `/app`
- Status files: `/app/.multi_process_status`
- Logs: `/app/logs`
- Credentials: `/root/.config`

**Networking:**

- Dashboard port: 8765 (exposed)
- Binds to: 0.0.0.0 (accessible from host)

**Process Management:**

- Entry point: `python3 main.py`
- Auto-shutdown: 5 minutes after completion
- Signal handling: Graceful SIGTERM/SIGINT

---

## Environment Variables

### Required

None - all configuration is in `vars.py`

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key for AI features | None (optional) |

### NotebookLM CLI

NotebookLM CLI stores credentials in:

- `~/.config/notebooklm/credentials.json` (local)
- `/root/.config/notebooklm/credentials.json` (container)

---

## File Locations

### User Home Directory

```
~/.project-ape/
├── drive_cache/              # Google Drive file cache
│   └── {folder_id}/
│       ├── metadata.json
│       └── *.pdf
├── drive_credentials.json    # OAuth credentials
└── drive_token.json          # OAuth access token
```

### Project Directory

```
project-ape/
├── .multi_process_status/    # Status files (runtime)
│   ├── client1.json
│   └── client2.json
├── logs/                     # Execution logs (runtime)
│   ├── overall.log
│   ├── client1.log
│   └── client2.log
├── vars.py                   # Configuration (user-created)
├── main.py                   # Main orchestrator
├── launch_ape.sh             # Container launcher
├── run-workflow.sh           # Local launcher
└── core/                     # Core modules
    ├── client_pipeline.py
    ├── drive_manager.py
    ├── notebook_manager.py
    └── ...
```

---

## Status File Format

**Location:** `.multi_process_status/{client_id}.json`

**Structure:**

```json
{
  "name": "Client Name",
  "token": "client_id",
  "step": "Uploading sources...",
  "progress": 45,
  "status": "RUNNING",
  "notebook_id": "abc123xyz",
  "mode": "fast",
  "last_update": 1719345700.123,
  "start_time": 1719345600.000,
  "quality_score": 8.5,
  "plan_link": "https://notebooklm.google.com/notebook/abc123",
  "log_file": "/path/to/logs/client_id.log",
  "run_id": "1719345678"
}
```

**Fields:**

- `name` - Client display name
- `token` - Client ID (unique identifier)
- `step` - Current pipeline phase
- `progress` - Percentage complete (0-100)
- `status` - `PENDING`, `RUNNING`, `COMPLETE`, `FAILED`, `DEGRADED`
- `notebook_id` - NotebookLM notebook ID
- `mode` - Execution mode (`fast` or `deep`)
- `last_update` - Unix timestamp of last update
- `start_time` - Unix timestamp when workflow started
- `quality_score` - Quality score (1-10) when complete
- `plan_link` - URL to NotebookLM notebook
- `log_file` - Path to client log file
- `run_id` - Unique run identifier

---

## Log Format

**Location:** `logs/{client_id}.log`

**Format:**

```
HH:MM:SS | LEVEL | Message
```

**Example:**

```
14:30:15 | INFO | Starting pipeline for Merck
14:30:18 | INFO | Downloading files from Drive: 1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen
14:30:45 | INFO | Downloaded 15 files (52.3 MB)
14:31:00 | INFO | Creating NotebookLM notebook: Merck Account Plan
14:31:05 | INFO | Notebook created: abc123xyz
14:31:10 | INFO | Uploading sources (15 files)...
14:32:30 | INFO | Source upload complete
14:32:35 | INFO | Running research prompts...
14:35:00 | INFO | Quality score: 8.5/10
14:35:05 | INFO | ✅ Pipeline complete for Merck
```

**Log Levels:**

- `INFO` - Normal operation
- `WARNING` - Non-critical issues
- `ERROR` - Errors that don't stop execution
- `CRITICAL` - Fatal errors

---

## Core Modules

### client_pipeline.py

**Purpose:** Executes complete workflow for a single client

**Entry Point:**

```bash
python3 core/client_pipeline.py {client_id} --mode {fast|deep} --status-file {path}
```

**Pipeline Phases:**

1. Download files from Drive
2. Create NotebookLM notebook
3. Upload sources
4. Wait for processing
5. Execute research prompts
6. Quality validation
7. Result storage

### drive_manager.py

**Purpose:** Google Drive integration with caching

**Key Features:**

- OAuth 2.0 user authentication
- Recursive folder traversal
- Smart caching with TTL
- Google Docs export to PDF
- Concurrent downloads

**Usage:**

```python
from core.drive_manager import DriveManager

with DriveManager(
    client_id="merck",
    folder_spec="https://drive.google.com/drive/folders/ABC123",
    cache_enabled=True,
    force_refresh=False
) as folder_path:
    files = list(Path(folder_path).glob("*.pdf"))
```

### notebook_manager.py

**Purpose:** NotebookLM API wrapper

**Key Features:**

- Notebook creation/deletion
- Source upload (PDF, TXT, Google Docs)
- Prompt execution (Ask/Chat)
- Status polling
- Error handling with retries

**Usage:**

```python
from core.notebook_manager import NotebookManager

manager = NotebookManager()
notebook_id = manager.create_notebook("Account Plan")
manager.add_source(notebook_id, "/path/to/file.pdf")
response = manager.ask_question(notebook_id, "What is the company strategy?")
```

### gemini_agent.py

**Purpose:** AI-powered orchestration and error recovery

**Key Features:**

- Industry auto-detection
- Error analysis and recovery
- Quality validation
- Self-healing workflows

**Usage:**

```python
from core.gemini_agent import GeminiAgent

agent = GeminiAgent()
industry = agent.detect_industry(["tech_doc.pdf", "annual_report.pdf"])
is_quality = agent.validate_quality(notebook_id, target_score=8.5)
```

### quality_scorer.py

**Purpose:** Result validation and scoring

**Criteria:**

- Source count (≥15 recommended)
- Note completeness (≥6 sections)
- Content quality assessment
- 1-10 scoring scale

**Usage:**

```python
from core.quality_scorer import QualityScorer

scorer = QualityScorer()
score = scorer.score_notebook(notebook_id, sources_count=20)
```

---

## Advanced Configuration

### Custom Timing Profiles

Create custom timing profiles for specific workflows:

```python
CUSTOM_TIMINGS = {
    'notebook_creation_delay': 5.0,
    'source_add_delay': (3.0, 5.0),
    'source_processing_delay': 60.0,
    'ask_prompt_delay': (20.0, 30.0),
    'chat_prompt_delay': (12.0, 18.0),
    'deduplication_delay': 30.0,
    'mindmap_delay': 25.0,
    'source_import_wait': 20.0,
}
```

### Container-Specific Paths

When running in containers, override default paths:

```python
from pathlib import Path

STATUS_DIR = Path('/app/.multi_process_status')
LOGS_DIR = Path('/app/logs')
```

### Quality Validation Tuning

Adjust quality thresholds for your use case:

```python
QUALITY_THRESHOLDS = {
    'min_sources': 20,        # Require more sources
    'required_notes': 8,      # More comprehensive notes
    'min_quality_score': 9.0, # Higher quality target
}
```

### Gemini Configuration

Fine-tune AI orchestration:

```python
GEMINI_AGENT_CONFIG = {
    'enabled': True,
    'model': 'gemini-2.0-flash-exp',
    'temperature': 0.1,       # More deterministic
    'max_retries': 10,        # More retry attempts
    'retry_base_delay': 15.0, # Longer delays
    'timeout': 120,           # Longer timeout
    'enable_error_analysis': True,
    'enable_quality_validation': True,
    'enable_self_healing': True,
    'quality_target': 9.0,
}
```

---

## Integration Examples

### CI/CD Pipeline

**GitLab CI:**

```yaml
research_accounts:
  image: quay.io/jasoande/project_ape:3.0.5-amd64
  script:
    - python3 main.py --mode fast --no-dashboard
  artifacts:
    paths:
      - logs/
      - .multi_process_status/
```

### Scheduled Execution

**Cron:**

```bash
# Run weekly account research
0 6 * * 1 cd /path/to/project-ape && ./run-workflow.sh fast
```

### Python Integration

```python
import subprocess
import json
from pathlib import Path

def run_account_research(clients, mode="fast"):
    """Run Project APE workflow programmatically"""
    
    cmd = ["python3", "main.py", "--mode", mode, "--no-dashboard"]
    
    if clients:
        cmd.extend(["--clients"] + clients)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse status files
    status_dir = Path(".multi_process_status")
    results = {}
    
    for status_file in status_dir.glob("*.json"):
        with open(status_file) as f:
            results[status_file.stem] = json.load(f)
    
    return results

# Usage
results = run_account_research(["merck", "organon"], mode="deep")
for client_id, status in results.items():
    print(f"{status['name']}: {status['quality_score']}/10")
```

---

## Troubleshooting API Issues

### Authentication Failures

**Problem:** API returns 401 Unauthorized

**Solution:**

```bash
# Re-authenticate NotebookLM
notebooklm login

# Check authentication status
curl http://localhost:8765/api/check-auth-status
```

### Port Conflicts

**Problem:** Dashboard won't start (port 8765 in use)

**Solution:**

```python
# In vars.py
DASHBOARD_PORT = 8766  # Use different port
```

### Container Access Issues

**Problem:** Can't access dashboard from browser

**Solution:**

```bash
# Ensure container binds to 0.0.0.0
podman run -p 8765:8765 ...

# Check firewall rules
sudo ufw allow 8765/tcp
```

### Cache Corruption

**Problem:** Drive files not downloading correctly

**Solution:**

```bash
# Clear cache via API
curl -X POST http://localhost:8765/api/clear-cache \
  -H "Content-Type: application/json" \
  -d '{"clients": ["all"]}'

# Or manually
rm -rf ~/.project-ape/drive_cache/*
```

---

## Support and Resources

- **Documentation:** [README.md](README.md), [QUICK_START.md](QUICK_START.md)
- **Troubleshooting:** [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/project-ape/issues)
- **API Updates:** Check version tags for breaking changes

---

**Version:** 3.2.2  
**Last Updated:** June 25, 2026  
**Author:** Jason Anderson
