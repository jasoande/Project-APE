# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project APE (Account Planning Engine)** - AI-powered enterprise account planning automation using Google's NotebookLM platform.

- **Current Version:** 3.0.4
- **Architecture:** Containerized Python application with multi-process orchestration
- **Primary Use:** Automated account research, industry analysis, and intelligence generation for enterprise sales teams
- **Deployment:** Podman containers (linux/amd64, linux/arm64), registry: quay.io/jasoande/project_ape/project-ape

## Quick Development Commands

### Running the Application

**Container-based execution (recommended):**
```bash
# Fast mode (10-12 minutes)
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast

# Deep mode (30-35 minutes, 8-9x more sources)
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep

# Multiple clients in parallel
./ape-run.sh --vars ./vars.py --clients client1,client2,client3 --mode fast
```

**Direct execution (development/testing):**
```bash
python3 main.py --mode fast --clients yourclient
python3 main.py --mode deep --clients client1 client2
python3 main.py --no-dashboard --mode fast  # Disable web dashboard
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

# Stop all Project APE containers
podman stop $(podman ps -aq --filter ancestor=project-ape)
```

### Authentication Setup

```bash
# Initial NotebookLM authentication (requires Chrome)
notebooklm login

# Setup container credentials volume
./setup-credentials.sh

# Copy credentials from another machine
scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/
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
- Flask app serving real-time status updates
- Reads status JSON files from `.multi_process_status/`
- Streams logs, displays progress bars, shows execution metrics
- Auto-refreshes every 2 seconds

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

### Configuration System

**Configuration File (`vars.py`):**
- Start from templates: `example-container.py` (single client), `container-vars.py` (multi-client)
- Per-client attributes: `{client_id}_name`, `{client_id}_folder`, `{client_id}_industry`, `{client_id}_subsegments`
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

### Phase 1: PDF Consolidation (~30 seconds)
1. Scan `{client_folder}` for PDFs
2. Merge into single PDF with table of contents
3. Save to `docs/{client_id}/{client_name}-One.pdf`

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

### Phase 5: Mind Map Generation (1-2 minutes)
1. Request visual mind map generation
2. Save outputs to `docs_generated/{client_id}/`
3. Create summary document

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

1. Create client data directory:
   ```bash
   mkdir -p client_data/NewClient
   cp /path/to/pdfs/* client_data/NewClient/
   ```

2. Add to `vars.py`:
   ```python
   clients = ["newclient"]
   
   newclient_name = "New Client Corporation"
   newclient_industry = "technology"
   newclient_subsegments = "cloud, AI, enterprise software"
   newclient_folder = "/app/client_data/NewClient"  # Container path
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
- Containers use volume mount to share host credentials
- No embedded API keys or secrets in code/config

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
