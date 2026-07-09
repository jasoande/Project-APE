<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="200"/>
  
  # CLAUDE.md
  
  **Developer Guidance for Claude Code**
</div>

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Account Intelligence (Account Planning Engine)** - AI-powered enterprise account planning automation using Google's NotebookLM platform.

- **Current Version:** 4.0.1
- **Architecture:** Containerized Python application with multi-process orchestration
- **Primary Use:** Automated account research, industry analysis, and intelligence generation for enterprise sales teams
- **Deployment:** Podman containers (linux/amd64, linux/arm64), registry: quay.io/jasoande/project_ape/project-ape

## Quick Development Commands

### Running the Application

**GUI launcher (recommended - zero terminal):**
```bash
# macOS: Double-click launch-project-ape.command
# Windows/Linux: Double-click launch-project-ape.py
# Or run manually:
python3 launch-project-ape.py

# Opens browser to http://localhost:8765/configure
# Configure clients via web UI, then launch workflows
```

**Container execution (alternative workflow):**
```bash
# Fast mode (15-20 minutes)
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast

# Deep mode (45-60 minutes, 8-9x more sources)
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep

# Multiple clients in parallel
./ape-run.sh --vars ./vars.py --clients client1,client2,client3 --mode fast
```

### Container Operations

```bash
# Build container locally
podman build -t project-ape:latest -f Containerfile.debian .

# Pull from registry
podman pull quay.io/jasoande/project_ape/project-ape:latest

# View running containers
podman ps | grep project-ape

# View container logs
podman logs -f <container-id>

# Stop all Account Intelligence containers
podman stop $(podman ps -aq --filter ancestor=project-ape)
```

### Authentication Setup

**Via Web UI (recommended):**
```bash
# 1. Launch GUI
python3 launch-project-ape.py

# 2. Browser opens to http://localhost:8765/configure
# 3. Follow 3-step setup wizard:
#    - Click "Authenticate NotebookLM" button (OAuth flow)
#    - Click "Setup Drive OAuth" button (upload credentials.json, generate token)
#    - Environment validation (automatic)
```

**Via Terminal (alternative):**
```bash
# NotebookLM authentication (requires Chrome)
notebooklm login

# Google Drive OAuth setup
python3 setup-oauth-drive.py

# Setup container credentials volume (for container deployments)
./setup-credentials.sh

# Copy credentials from another machine
scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/
scp credentials/token_drive.json user@remote:~/Project-APE-dev/credentials/
```

### Monitoring and Debugging

```bash
# Dashboard URL (auto-opens in browser)
http://localhost:8765

# Follow client logs
tail -f logs/clientname.log

# Monitor all logs
tail -f logs/*.log

# Search for errors
grep "ERROR" logs/*.log
grep "FAILED" logs/*.log

# View status files (real-time progress tracking)
cat .multi_process_status/clientname.json
```

## Architecture Overview

### Core Components

**Multi-Process Orchestrator (`main.py`):**
- Launches Flask dashboard server (port 8765)
- Spawns independent client pipeline processes (one per client)
- Manages process lifecycle, status tracking, and cleanup
- Supports parallel execution of up to 5 clients simultaneously
- Each client runs in isolation with independent logs and status files

**Client Pipeline (`core/client_pipeline.py`):**
- Single-client workflow execution
- Five sequential phases: PDF consolidation → Notebook creation → Research (Ask prompts) → Analysis (Chat prompts) → Mind map generation
- Status updates via JSON files for dashboard integration
- Configurable timing based on mode (fast vs deep)

**NotebookLM SDK Integration:**
- All NotebookLM API calls via `notebooklm` CLI (notebooklm-py package)
- Authentication managed via `~/.notebooklm/credentials.json` (OAuth2)
- Container uses volume mount: `project-ape-credentials:/opt/app-root/src/.notebooklm`

**Dashboard (`dashboard/server.py`):**
- Flask app serving real-time status updates and web-based configuration
- Dual interface: `/configure` (setup wizard + client management) and `/status` (live monitoring)
- Configuration wizard: NotebookLM auth, Drive OAuth setup, client addition
- Reads status JSON files from `.multi_process_status/`
- Streams logs, displays progress bars, shows execution metrics
- Auto-refreshes every 2 seconds via server-sent events (SSE)

### Web UI Components

**`launch-project-ape.py` (Primary Entry Point):**
- Cross-platform launcher (Windows, macOS, Linux)
- Automatic virtual environment setup (`~/.project-ape-venv`)
- Dependency installation on first run (Flask, notebooklm-py, pypdf, etc.)
- Starts dashboard server in background
- Opens browser to http://localhost:8765/configure
- Designed for double-click execution (zero terminal required)

**`dashboard/config_generator.py`:**
- Generates `vars.py` configuration from web form input
- Validates client IDs, Drive URLs, industry/subsegment selections
- Preserves existing configuration when adding new clients
- Writes Python-executable configuration with proper formatting

**`dashboard/config_parser.py`:**
- Parses existing `vars.py` to populate web UI forms
- Extracts client configurations for editing
- Handles both Drive URLs and local folder paths
- Enables configuration round-tripping (web → file → web)

**Web UI Routes:**
- `/configure` - Setup wizard + client management (primary interface)
- `/status` - Live workflow monitoring (auto-switches after launch)
- `/stream-logs/{client_id}` - Server-sent events for log streaming
- `/health` - Dashboard health check
- `/api/*` - REST endpoints for configuration and control

### Module Responsibilities

**`core/auth_manager.py`:**
- Validates NotebookLM authentication
- Checks credential file existence and validity
- Used at pipeline startup to fail fast if auth missing

**`core/notebook_manager.py`:**
- Deduplication: finds existing notebooks by name to avoid re-creation
- Notebook lifecycle management (create, find, delete)
- Parses `notebooklm list --json` output

**`core/source_manager.py`:**
- Adds file sources (consolidated PDFs) to notebooks
- Executes research queries (Ask prompts) with automatic source import
- Parses research citations and imports discovered URLs/sources
- Handles retry logic for quota-limited operations

**`core/pdf_consolidator_fast.py`:**
- Merges all client PDFs into single document with table of contents
- Fast mode: simple concatenation (~30 seconds)
- Deep mode variant (not currently in use): enhanced metadata

**`core/drive_manager.py`:**
- Google Drive API v3 integration for direct PDF downloads
- Supports Drive folder URLs (extracts folder ID automatically)
- 7-day intelligent caching (`.drive_cache/` directory)
- Handles Google Docs/Sheets auto-conversion to PDF
- OAuth 2.0 authentication via `credentials/token_drive.json`

**`core/quality_scorer.py`:**
- AI-powered quality validation using Gemini API
- Scores completeness across 6 dimensions (industry, SWOT, tech, competitive, pain points, recommendations)
- Generates overall quality score (1.0-10.0 scale)
- Output: `docs_generated/{client_id}/Quality_Score.json`
- Requires `GEMINI_API_KEY` environment variable (optional feature)

**`core/claude_industry_detector.py`:**
- Automatic industry classification from client documents
- Analyzes consolidated PDF content via Claude API
- Used when `industry` field left blank in configuration
- Provides industry + subsegments for prompt targeting

**`core/retry_strategy.py`:**
- Shared retry logic with exponential backoff for NotebookLM CLI operations
- `RetryConfig` dataclass, `is_retryable_error()`, `execute_with_retry()` orchestrator
- Canonical `RETRYABLE_PATTERNS` list (rate limit, quota, RPC codes, auth errors)
- `RetryableError` / `NonRetryableError` exception classes

**`core/checkpoint_manager.py`:**
- Pipeline checkpoint/resume for crash recovery
- `PipelineCheckpoint` dataclass tracks completed phases, notebook_id, PDF path
- `CheckpointManager` persists checkpoints as JSON in `logs/.checkpoints/`
- Used with `--resume` flag to skip completed pipeline phases

**`core/health_checks.py`:**
- Pre-flight validation before pipeline execution
- Checks: NotebookLM CLI available, NotebookLM authenticated, Drive OAuth valid, config valid
- `run_preflight_checks()` aggregates all checks
- Called from main.py before spawning client processes

**`core/notification_manager.py`:**
- Webhook notifications on workflow completion
- `send_webhook()` via urllib.request (no external dependency)
- `format_slack_payload()` for Slack Block Kit messages
- Configured via `NOTIFICATION_WEBHOOK_URL` in vars.py

### Security Features

- **CSRF Protection:** flask-wtf CSRFProtect on all POST endpoints (SSE streaming endpoints exempted)
- **Path Traversal Prevention:** Regex validation on `/logs/<client_token>` with `is_relative_to()` check
- **No shell=True:** All subprocess calls use explicit argument lists
- **Error Sanitization:** `_safe_error()` helper logs full errors server-side, returns generic messages to client
- **Non-root Container:** Runs as `apeuser` (UID 1000)

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=core --cov=dashboard --cov-report=term-missing

# Run specific test file
pytest tests/test_retry_strategy.py -v

# Skip slow/integration tests
pytest tests/ -m "not slow and not integration"
```

Test files: `test_retry_strategy.py`, `test_checkpoint_manager.py`, `test_health_checks.py`, `test_notification_manager.py`, `test_config_generator.py`, `test_config_parser.py`, `test_server_security.py`, `test_client_pipeline.py`

### Configuration System

**Configuration System (Two Approaches):**

1. **Web UI Configuration (Recommended):**
   - Browser-based form at http://localhost:8765/configure
   - Add clients dynamically: name, Drive folder URL, industry, subsegments, mode
   - Generates `vars.py` automatically via `dashboard/config_generator.py`
   - Real-time validation and preview

2. **Manual Configuration File (`vars.py`):**
   - Start from templates: `example-container.py` (single client), `container-vars.py` (multi-client)
   - Per-client attributes: `{client_id}_name`, `{client_id}_folder` (now supports Drive URLs), `{client_id}_industry`, `{client_id}_subsegments`
   - Global settings: `persona` (AI role, e.g., "Red Hat solutions architect"), `MODE`, `DASHBOARD_PORT`
   - Timing configurations: `TIMINGS` (fast mode), `DEEP_TIMINGS` (deep mode)
   - Retry settings: `RETRY_CONFIG` for API error handling

**Container Paths (for containerized execution):**
- `PROJECT_ROOT = /app`
- Client data: `/app/client_data/` (host: `./client_data/`, mounted read-only)
- Generated docs: `/app/docs_generated/` (host: `./docs_generated/`)
- Logs: `/app/logs/` (host: `./logs/`, writable)
- Config: `/app/vars.py` (host: `./vars.py`, mounted read-only)

## Pipeline Workflow

### Phase 1: PDF Download & Consolidation (~30-60 seconds)
1. Download PDFs from Google Drive folder (if Drive URL configured)
   - 7-day cache check (skip download if cached)
   - Auto-convert Google Docs/Sheets to PDF
2. Or scan local `{client_folder}` for PDFs (legacy support)
3. Merge all PDFs into single document with table of contents
4. Save to `docs/{client_id}/{client_name}-One.pdf`

### Phase 2: Notebook Creation (~10 seconds)
1. Check for existing notebook (deduplication via `notebook_manager.find_notebook_by_name()`)
2. Create new notebook if needed: `notebooklm create "{client_name}"`
3. Upload consolidated PDF: `notebooklm source add {pdf_path} -n {notebook_id}`
4. Wait for source processing (30s fast, 45s deep)

### Phase 3: Research - Ask Prompts (3-5 minutes)
1. Execute 2 research queries from `ask_prompt_01.txt`, `ask_prompt_02.txt`
2. Each query triggers web research via NotebookLM
3. AI imports 10-25 external sources per query (fast) or 45-90 sources (deep)
4. Delays: 8-12s between queries (fast), 15-25s (deep)

### Phase 4: Analysis - Chat Prompts (8-12 minutes)
1. Execute 6 consolidated chat prompts (`chat_prompt_consolidated_01.txt` through `06.txt`)
2. Each prompt covers 2 analysis dimensions (industry, challenges, technology, competitive, pain points, opportunities, decision makers, buying process, value proposition, metrics, risks, recommendations)
3. Persona substitution: `$persona` replaced with value from `vars.py`
4. Delays: 5-8s between prompts (fast), 10-15s (deep)

### Phase 5: Quality Validation (1-2 minutes)
1. Analyze generated content for completeness
2. Score across 6 dimensions via Gemini API (if configured)
3. Generate overall quality score (1.0-10.0)
4. Save `Quality_Score.json` to `docs_generated/{client_id}/`
5. Create summary document with NotebookLM link

### Timing Strategy

**Anti-Thundering-Herd Protection:**
- Random initial offset (0-30s) when multiple clients start simultaneously
- Prevents synchronized API calls from parallel processes

**Mode-Specific Delays:**
- Fast mode: aggressive timing, ~5% retry rate, optimized for speed
- Deep mode: conservative delays, ~30% retry rate (acceptable), optimized for maximum source coverage

**Retry Logic:**
- `max_attempts: 5`, `base_delay: 10s` for standard operations
- `ask_max_attempts: 7`, `ask_base_delay: 30s` for research queries (quota-sensitive)
- Exponential backoff on retries

## Prompt Engineering

### Prompt Files

All prompts use variable substitution:
- `$name` → client name
- `$industry` → client industry
- `$subsegments` → industry subsegments
- `$persona` → AI role/perspective (only in chat prompts)

**Research Prompts (Ask):**
- `ask_prompt_01.txt` - Industry analysis and trends
- `ask_prompt_02.txt` - Competitive landscape

**Analysis Prompts (Chat):**
- `chat_prompt_consolidated_01.txt` - Industry overview + key challenges
- `chat_prompt_consolidated_02.txt` - Technology trends + competitive positioning
- `chat_prompt_consolidated_03.txt` - Pain points + opportunity areas
- `chat_prompt_consolidated_04.txt` - Decision makers + buying process
- `chat_prompt_consolidated_05.txt` - Value proposition + success metrics
- `chat_prompt_consolidated_06.txt` - Risk factors + strategic recommendations

### Subsegment Examples

Subsegments provide targeted research focus:
- Technology: "cloud services, SaaS platforms, cybersecurity, AI/ML, DevOps"
- Financial: "banking, insurance, wealth management, fintech, payments"
- Healthcare: "hospitals, pharmaceuticals, medical devices, health IT, telehealth"
- Manufacturing: "automotive, aerospace, electronics, supply chain, IoT"

## Testing and Validation

**No automated test suite currently.** Manual testing workflow:

1. **Single-client fast mode test:**
   ```bash
   ./ape-run.sh --vars ./example-container.py --clients example_client --mode fast
   ```

2. **Verify outputs:**
   - Check `logs/example_client.log` for errors
   - Verify `docs_generated/example_client/` contains outputs
   - Check dashboard at http://localhost:8765 shows COMPLETE status

3. **Multi-client parallel test:**
   ```bash
   ./ape-run.sh --vars ./container-vars.py --clients client1,client2,client3 --mode fast
   ```

4. **Deep mode validation:**
   - Expect 30-35 minute runtime
   - Verify 90-180 sources imported (check logs: "Imported X sources")
   - Expect ~30% retry rate (acceptable for deep mode)

## Common Development Tasks

### Adding a New Client

**Via Web UI (Recommended):**
1. Launch dashboard: `python3 launch-project-ape.py`
2. Navigate to http://localhost:8765/configure
3. Scroll to "Add New Client" form
4. Fill in:
   - Client Name: "New Client Corporation"
   - Client ID: Auto-generated (or customize)
   - Drive Folder URL: https://drive.google.com/drive/folders/1A2B3C...
   - Industry: "technology" (or leave blank for auto-detect)
   - Subsegments: "cloud, AI, enterprise software"
   - Mode: Fast or Deep
5. Click "Add Client" → "Save Configuration" → "Launch Workflow"

**Via Manual Configuration (Alternative):**
1. Upload PDFs to Google Drive folder, get shareable link
2. Add to `vars.py`:
   ```python
   clients = ["newclient"]
   
   newclient_name = "New Client Corporation"
   newclient_folder = "https://drive.google.com/drive/folders/1A2B3C..."  # Drive URL
   newclient_industry = "technology"  # Or "" for auto-detect
   newclient_subsegments = "cloud, AI, enterprise software"
   ```

3. Run pipeline:
   ```bash
   ./ape-run.sh --vars ./vars.py --clients newclient --mode fast
   ```

### Modifying Prompts

1. Edit prompt files directly (no compilation step)
2. Use `$name`, `$industry`, `$subsegments`, `$persona` for substitution
3. Test with single client before batch runs
4. Chat prompts support persona context; Ask prompts do not

### Adjusting Timing

**Fast mode timing** (edit `vars.py`):
```python
TIMINGS = {
    'ask_prompt_delay': (8.0, 12.0),  # Seconds between research queries
    'chat_prompt_delay': (5.0, 8.0),  # Seconds between chat prompts
    # ... other timings
}
```

**Deep mode timing:**
```python
DEEP_TIMINGS = {
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    # ... other timings
}
```

### Building and Pushing Containers

```bash
# Build multi-arch container
podman build -t project-ape:latest -f Containerfile.debian .

# Tag for registry
podman tag project-ape:latest quay.io/jasoande/project_ape/project-ape:latest
podman tag project-ape:latest quay.io/jasoande/project_ape/project-ape:v3.0.4

# Push to registry
podman push quay.io/jasoande/project_ape/project-ape:latest
podman push quay.io/jasoande/project_ape/project-ape:v3.0.4
```

## Key Constraints and Considerations

**NotebookLM API Quotas:**
- Research queries (Ask prompts) are quota-limited
- Use retry logic with exponential backoff
- Deep mode intentionally accepts higher retry rate for maximum coverage

**Container User Permissions:**
- Container runs as `apeuser` (UID 1000, non-root)
- Host directories mounted with `:z` SELinux label for RHEL/Fedora compatibility
- Logs directory must be writable by UID 1000 (handled by `ape-run.sh`)

**Parallel Client Execution:**
- Each client runs in independent Python process
- Maximum 5 clients recommended (resource and quota considerations)
- Anti-thundering-herd offset prevents synchronized API hits

**Authentication:**
- NotebookLM credentials are OAuth2, stored in `~/.notebooklm/credentials.json`
- Google Drive OAuth tokens stored in `credentials/token_drive.json` (90-day expiry)
- Gemini API key (optional) via `GEMINI_API_KEY` environment variable
- Containers use volume mount to share host credentials
- No embedded API keys or secrets in code/config
- Web UI provides guided OAuth setup wizards

**Status File Race Conditions:**
- Status files (`.multi_process_status/*.json`) are single-writer (one client process)
- Dashboard reads status files (read-only)
- No locking needed due to single-writer pattern

## File Naming Conventions

**Client IDs:** lowercase, underscores (e.g., `merck_test`, `example_client`)
**Client Names:** proper case, spaces allowed (e.g., `Merck Pharmaceuticals`)
**Generated PDFs:** `{ClientName}-One.pdf`
**Log files:** `{client_id}.log`
**Status files:** `{client_id}.json`

**Launcher Files:**
- `launch-project-ape.py` - Universal Python launcher (cross-platform)
- `launch-project-ape.command` - macOS double-click launcher (executes .py)
- `project-ape-launcher.desktop` - Linux desktop integration file

## Troubleshooting

**"Authentication failed":**
- Run `notebooklm login` on machine with Chrome
- Or copy credentials: `scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/`
- Verify: `ls -la ~/.notebooklm/credentials.json`

**"Container won't start":**
- Check credentials volume: `podman volume exists project-ape-credentials`
- Run setup: `./setup-credentials.sh`
- Verify permissions: `chmod -R 700 ~/.notebooklm`

**"Dashboard not accessible":**
- Check container is running: `podman ps | grep project-ape`
- Verify port mapping: `podman port <container-name>`
- Test: `curl http://localhost:8765/status`

**"Research timeout" or high retry rate:**
- Normal for large accounts in deep mode (~30% retry rate acceptable)
- Increase delays in `DEEP_TIMINGS` if needed
- Consider fast mode for initial runs

**See `Docs/TROUBLESHOOTING.md` for comprehensive troubleshooting guide.**
