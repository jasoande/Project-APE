<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE" width="150"/>

  # Architecture Documentation

  **Project APE - Account Planning Engine**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [System Overview](#system-overview)
- [Core Components Diagram](#core-components-diagram)
- [Module Reference](#module-reference)
- [Pipeline Flow](#pipeline-flow)
- [Checkpoint and Resume](#checkpoint-and-resume)
- [Configuration System](#configuration-system)
- [Data Flow](#data-flow)
- [Deployment Architecture](#deployment-architecture)

---

## System Overview

Project APE is a containerized Python application that automates enterprise account planning using Google's NotebookLM platform. The system uses a multi-process orchestrator pattern: `main.py` spawns independent client pipeline processes (one per client), each running through a 5-phase workflow. A Flask/Waitress dashboard provides real-time monitoring via Server-Sent Events (SSE) and JSON status files.

Key architectural properties:

- **Process isolation:** Each client runs in its own Python process with independent logs, status files, and error handling.
- **Single-writer status files:** Each client process exclusively writes its own `.multi_process_status/{client_id}.json` file. The dashboard reads these files without locking.
- **Anti-thundering-herd protection:** Random initial offsets (0-30s) prevent synchronized API calls when multiple clients start simultaneously.
- **Checkpoint/resume:** Pipeline state persists to disk after each phase, allowing interrupted runs to resume from where they left off.

---

## Core Components Diagram

```
                          +---------------------------+
                          |   launch-project-ape.py    |
                          |  (cross-platform launcher) |
                          +-------------+-------------+
                                        |
                                        v
+-----------------------------------------------------------------------+
|                          main.py (Orchestrator)                        |
|                                                                        |
|  - Loads vars.py configuration                                         |
|  - Starts dashboard server (Flask/Waitress, port 8765)                 |
|  - Spawns N client_pipeline.py processes (max 5 concurrent)            |
|  - Monitors process lifecycle                                          |
|  - Sends completion notifications (webhook)                            |
+---+----------+----------+----------+----------+-----------------------+
    |          |          |          |          |
    v          v          v          v          v
+--------+ +--------+ +--------+ +--------+ +--------+
|Client 1| |Client 2| |Client 3| |Client 4| |Client 5|
|Pipeline| |Pipeline| |Pipeline| |Pipeline| |Pipeline|
+--------+ +--------+ +--------+ +--------+ +--------+
    |          |          |          |          |
    +----------+----------+----------+----------+
                          |
                          v
              +------------------------+
              | .multi_process_status/  |
              |   client1.json          |
              |   client2.json          |       +------------------+
              |   ...                   | <---- | dashboard/server |
              +------------------------+       | (reads status)   |
                                               +--------+---------+
                                                        |
                                                        v
                                               +------------------+
                                               |     Browser      |
                                               | localhost:8765    |
                                               +------------------+
```

---

## Module Reference

### Orchestration

| Module | Description |
|--------|-------------|
| `main.py` | Multi-process orchestrator. Loads configuration, starts the dashboard server, spawns client pipeline processes, monitors their lifecycle, and triggers completion notifications. |
| `launch-project-ape.py` | Cross-platform GUI launcher. Sets up virtual environment, installs dependencies, starts the dashboard server, and opens the browser. Designed for double-click execution. |

### Core Pipeline

| Module | Description |
|--------|-------------|
| `core/client_pipeline.py` | Single-client 5-phase pipeline execution. Handles PDF consolidation, notebook creation, research queries, analysis prompts, and quality scoring. Supports fast, deep, update, and agent-orchestrated modes. Integrates with checkpoint/resume for fault tolerance. |
| `core/auth_manager.py` | NotebookLM authentication validation. Checks credential file existence and validity (`~/.notebooklm/profiles/default/storage_state.json`). Includes retry logic with anti-collision delays for multi-client scenarios. |
| `core/notebook_manager.py` | Notebook lifecycle management. Creates, finds, and deletes NotebookLM notebooks. Supports deduplication by name to avoid re-creating existing notebooks. |
| `core/source_manager.py` | Source addition with retry logic. Adds file sources (consolidated PDFs) to notebooks, executes research queries (Ask prompts), and imports discovered URLs/sources with automatic retry on quota errors. |
| `core/pdf_consolidator_fast.py` | PDF merging with table of contents. Consolidates all client PDFs (and exported Google Workspace files) into a single document. |
| `core/drive_manager.py` | Google Drive API v3 integration with OAuth 2.0. Downloads files from Drive folders, exports Google Docs/Sheets to PDF, and implements a TTL-based cache (`~/.project-ape/drive_cache/`). Supports timestamp-based change detection. |

### Quality and Intelligence

| Module | Description |
|--------|-------------|
| `core/quality_scorer.py` | Quality validation with optional Gemini AI enhancement. Scores output across source quality (0-3), research depth (0-2), note completeness (0-4), and mind map presence (0-1) for a total of 10.0. |
| `core/claude_industry_detector.py` | Automatic industry classification from client documents. Analyzes consolidated PDF content via Claude API when the industry field is left blank. |
| `core/gemini_agent.py` | Gemini AI agent for orchestrating pipeline steps with quality monitoring. Used in agent-orchestrated execution mode. |
| `core/gemini_manager.py` | Gemini API session management and configuration. |
| `core/error_analyzer.py` | Pipeline error analysis and classification. |
| `core/artifact_verifier.py` | Notebook artifact verification (sources, notes, mind maps). |

### Reliability

| Module | Description |
|--------|-------------|
| `core/retry_strategy.py` | Shared retry logic with exponential backoff. Provides `RetryConfig` dataclass, `RetryableError`/`NonRetryableError` exceptions, pattern-based error classification, and the `execute_with_retry()` orchestrator. Retryable patterns include rate limits, quota exhaustion, RPC errors, and authentication failures. |
| `core/checkpoint_manager.py` | Pipeline checkpoint/resume capability. `PipelineCheckpoint` tracks 8 phases of execution. `CheckpointManager` saves/loads checkpoints as JSON, determines which phases to skip on resume, and clears checkpoints on completion. |
| `core/health_checks.py` | Pre-flight validation before pipeline execution. Checks NotebookLM CLI availability, NotebookLM authentication, Google Drive OAuth token, and configuration file validity. `run_preflight_checks()` aggregates all results. |
| `core/notification_manager.py` | Webhook notifications for pipeline completion. Sends Slack Block Kit formatted payloads via `NOTIFICATION_WEBHOOK_URL`. Fires only when configured. |

### Dashboard

| Module | Description |
|--------|-------------|
| `dashboard/server.py` | Flask application served by Waitress. Provides REST API endpoints, SSE log streaming, configuration wizard, and real-time status monitoring. CSRF protection via flask-wtf, path traversal prevention, and error message sanitization. |
| `dashboard/config_generator.py` | Generates `vars.py` configuration from web form input. Validates client data, sanitizes client IDs, and formats Python-executable configuration. |
| `dashboard/config_parser.py` | Parses existing `vars.py` to populate web UI forms. Extracts client configurations and global settings. Enables round-trip editing (web to file to web). |

### Utilities

| Module | Description |
|--------|-------------|
| `core/notebooklm_cmd.py` | NotebookLM CLI command wrapper. |
| `core/notebooklm_utils.py` | NotebookLM utility functions. |
| `core/research_queue.py` | Research query queue management. |
| `core/update_manager.py` | Application update management. |
| `workflow_detector.py` | Workflow configuration detection and validation. |

---

## Pipeline Flow

Each client pipeline executes 5 sequential phases, with checkpoint persistence between phases:

```
Phase 1                Phase 2              Phase 3
PDF Download &         Notebook             Research
Consolidation          Creation             (Ask Prompts)
(30-60s)               (10s)                (3-5 min)
+------------------+   +----------------+   +------------------+
| Download PDFs    |   | Check for      |   | Execute 2 ask    |
| from Drive       |-->| existing       |-->| prompts          |
| (7-day cache)    |   | notebook       |   | Import 10-90     |
| Merge into       |   | Create/reuse   |   | external sources |
| single PDF + TOC |   | Upload PDF     |   | per query        |
+------------------+   +----------------+   +------------------+
                                                     |
                  +----------------------------------+
                  |
                  v
Phase 4                              Phase 5
Analysis                             Quality Validation
(Chat Prompts)                       & Mind Map
(8-12 min)                           (1-2 min)
+------------------------------+     +------------------+
| Execute 6 consolidated       |     | Score across 4   |
| chat prompts with            |---->| dimensions       |
| variable substitution        |     | Generate mind    |
| ($name, $industry,           |     | map artifact     |
|  $subsegments, $persona)     |     | Create summary   |
+------------------------------+     +------------------+
```

### Execution Modes

| Mode | Duration | Sources Imported | Retry Rate | Use Case |
|------|----------|------------------|------------|----------|
| Fast | 15-20 min | 10-25 per query | ~5% | Quick account planning, initial runs |
| Deep | 45-60 min | 45-90 per query | ~30% (acceptable) | Maximum source coverage, thorough analysis |
| Update | Variable | Refreshes existing | Variable | Refresh notebook with new web data |

---

## Checkpoint and Resume

The checkpoint system enables fault-tolerant pipeline execution. When a pipeline is interrupted (crash, network failure, quota exhaustion), it can resume from the last completed phase.

### Phase Order

1. `setup_folder` - Download/locate client documents
2. `determine_industry` - Detect or load industry classification
3. `check_auth` - Validate NotebookLM authentication
4. `create_notebook` - Create or find existing notebook
5. `consolidate_pdf` - Merge PDFs into single document
6. `run_research` - Execute Ask prompts for web research
7. `run_chat` - Execute Chat prompts for analysis
8. `generate_mindmap` - Create notebook mind map artifact

### How It Works

```
Pipeline Start
     |
     v
Load checkpoint (if --resume flag)
     |
     +---> No checkpoint found: start from phase 1
     |
     +---> Checkpoint found: skip completed phases
           |
           v
     For each phase:
       1. Check should_skip_phase() against completed_phases
       2. If skipped, log and continue
       3. If not skipped, execute phase
       4. On success, save checkpoint with updated completed_phases
       5. On failure, checkpoint preserves progress for next resume
     |
     v
Pipeline Complete: clear checkpoint file
```

Checkpoint files are stored as JSON in `logs/.checkpoints/{client_id}.json` and track: client_id, run_id, mode, current phase, completed phases, notebook_id, industry, subsegments, quality_score, and last_update timestamp.

---

## Configuration System

Project APE supports two configuration approaches:

### 1. Web UI Configuration (Recommended)

The browser-based form at `http://localhost:8765/configure` provides:

- Client management (add, edit, remove)
- Google Drive URL validation
- Industry and subsegment selection
- Mode selection (fast/deep)
- Real-time validation and preview
- CSV import for batch client setup

Configuration is generated by `dashboard/config_generator.py` and written to `vars.py`.

### 2. Manual Configuration (`vars.py`)

Direct Python file with per-client attributes:

```python
clients = ["client_a", "client_b"]

client_a_name = "Client A Corporation"
client_a_folder = "https://drive.google.com/drive/folders/1ABC..."
client_a_industry = "technology"
client_a_subsegments = "cloud, AI, enterprise software"

persona = "Red Hat solutions architect"
default_mode = "fast"
```

### Key Configuration Sections

| Section | Purpose |
|---------|---------|
| `clients` | List of client IDs to process |
| `{id}_name`, `{id}_folder`, etc. | Per-client attributes |
| `persona` | AI role/perspective for chat prompts |
| `TIMINGS` / `DEEP_TIMINGS` | Mode-specific delay configurations |
| `RETRY_CONFIG` | Retry behavior (max attempts, delays) |
| `DRIVE_CONFIG` | Drive download settings (cache TTL, file size limit) |
| `GEMINI_AGENT_CONFIG` | Gemini AI agent settings |
| `QUALITY_THRESHOLDS` | Minimum quality standards |
| `NOTIFICATION_WEBHOOK_URL` | Webhook URL for completion notifications |

---

## Data Flow

```
Google Drive Folder         Local PDFs
        |                       |
        v                       v
  +----------------------------+
  |   core/drive_manager.py    |
  |   (download + cache)       |
  +-------------+--------------+
                |
                v
  +----------------------------+
  | core/pdf_consolidator_fast |
  | Merge into {Name}-One.pdf  |
  +-------------+--------------+
                |
                v
  +----------------------------+
  |   NotebookLM (via CLI)     |
  |   Create notebook          |
  |   Upload consolidated PDF  |
  |   Run Ask prompts          |   <-- ask_prompt_01.txt, ask_prompt_02.txt
  |   Run Chat prompts         |   <-- chat_prompt_consolidated_01-06.txt
  |   Generate mind map        |
  +-------------+--------------+
                |
                v
  +----------------------------+
  | core/quality_scorer.py     |
  | Score 4 dimensions (0-10)  |
  +-------------+--------------+
                |
                v
  docs_generated/{client_id}/
    Quality_Score.json
    Summary document
```

---

## Deployment Architecture

### Container Layout

```
/app (PROJECT_ROOT)
  /client_data/       (host: ./client_data/, mounted read-only)
  /docs_generated/    (host: ./docs_generated/)
  /logs/              (host: ./logs/, writable)
  /vars.py            (host: ./vars.py, mounted read-only)
```

- Container runs as `apeuser` (UID 1000, non-root)
- Host directories mounted with `:z` SELinux label for RHEL/Fedora compatibility
- Credentials via volume mount: `project-ape-credentials:/opt/app-root/src/.notebooklm`
- Multi-arch support: `linux/amd64`, `linux/arm64`
- Registry: `quay.io/jasoande/project_ape/project-ape`
