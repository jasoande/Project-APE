<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence" width="150"/>

  # API Reference

  **Dashboard REST API and Integration Endpoints**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [Overview](#overview)
- [Health and Status](#health-and-status)
- [Configuration](#configuration)
- [Workflow Control](#workflow-control)
- [Log Streaming](#log-streaming)
- [Authentication](#authentication)
- [Google Drive](#google-drive)
- [System](#system)

---

## Overview

The Account Intelligence dashboard exposes a REST API at `http://localhost:8765`. All endpoints return JSON unless otherwise noted. SSE (Server-Sent Events) endpoints stream `text/event-stream` responses.

**Base URL:** `http://localhost:8765`

**CSRF:** All POST endpoints require a CSRF token (via flask-wtf) except SSE streaming endpoints, which are explicitly exempt.

---

## Health and Status

### GET /health

Health check endpoint for monitoring.

**Response:**

```json
{
  "status": "healthy",
  "pid": 12345,
  "active_threads": 4,
  "memory_mb": 45.2,
  "status_dir_exists": true,
  "logs_dir_exists": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"healthy"` or `"unhealthy"` |
| `pid` | int | Server process ID |
| `active_threads` | int | Number of active threads |
| `memory_mb` | float | Memory usage in megabytes |
| `status_dir_exists` | bool | Whether `.multi_process_status/` directory exists |
| `logs_dir_exists` | bool | Whether `logs/` directory exists |

---

### GET /status

Aggregated client status from all status files.

**Response:**

```json
{
  "total": 3,
  "running": 1,
  "complete": 1,
  "failed": 1,
  "clients": [
    {
      "name": "Client Corp",
      "token": "client_corp",
      "step": "Running chat prompts",
      "progress": 65,
      "status": "RUNNING",
      "mode": "fast",
      "notebook_id": "nb_abc123",
      "last_update": 1720000000.0,
      "start_time": 1719999000.0,
      "quality_score": null,
      "log_file": "client_corp.log",
      "run_id": "run_20260708_120000"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of clients |
| `running` | int | Clients currently executing |
| `complete` | int | Successfully completed clients |
| `failed` | int | Failed clients |
| `clients` | array | Per-client status objects |

---

### GET /api/system-status

System resource information.

**Response:**

```json
{
  "disk_usage": {
    "total_gb": 500.0,
    "used_gb": 250.0,
    "free_gb": 250.0,
    "percent": 50.0
  },
  "python_version": "3.12.4",
  "venv_active": true,
  "is_container": false
}
```

---

### GET /api/preflight-check

Run pre-flight health checks before workflow launch.

**Response:**

```json
{
  "all_passed": true,
  "checks": [
    {
      "check": "notebooklm_cli",
      "passed": true,
      "message": "NotebookLM CLI is available"
    },
    {
      "check": "notebooklm_auth",
      "passed": true,
      "message": "NotebookLM authentication is valid"
    },
    {
      "check": "drive_auth",
      "passed": true,
      "message": "Google Drive authentication is valid"
    },
    {
      "check": "config_valid",
      "passed": true,
      "message": "Config valid with 2 client(s): client_a, client_b"
    }
  ],
  "summary": "4/4 checks passed"
}
```

| Check | What It Validates |
|-------|-------------------|
| `notebooklm_cli` | NotebookLM CLI is installed and responds to `notebooklm list --json` |
| `notebooklm_auth` | NotebookLM OAuth credentials are present and valid |
| `drive_auth` | Google Drive token exists at `~/.project-ape/drive_token.json` with a `token` key |
| `config_valid` | `vars.py` exists, has a non-empty `clients` list, and each client has `_name` and `_folder` attributes |

---

## Configuration

### GET /api/config-status

Check whether `vars.py` exists and is valid.

**Response:**

```json
{
  "configured": true,
  "client_count": 2,
  "clients": ["client_a", "client_b"]
}
```

---

### GET /api/load-config

Load and parse the current `vars.py` configuration.

**Response:**

```json
{
  "success": true,
  "clients": [
    {
      "id": "client_a",
      "name": "Client A Corp",
      "folder": "https://drive.google.com/drive/folders/1ABC...",
      "industry": "technology",
      "subsegments": "cloud, AI"
    }
  ],
  "settings": {
    "persona": "Red Hat solutions architect",
    "default_mode": "fast",
    "DASHBOARD_PORT": 8765,
    "TIMINGS": { "..." : "..." },
    "DEEP_TIMINGS": { "..." : "..." },
    "RETRY_CONFIG": { "..." : "..." }
  },
  "file_info": {
    "modified": 1720000000.0,
    "size": 2048
  }
}
```

---

### POST /api/generate-config

Generate `vars.py` content from client data without writing to disk.

**Request body:**

```json
{
  "clients": [
    {
      "id": "client_a",
      "name": "Client A Corp",
      "folder": "https://drive.google.com/drive/folders/1ABC...",
      "industry": "technology",
      "subsegments": "cloud, AI"
    }
  ],
  "settings": {
    "persona": "solutions architect",
    "default_mode": "fast"
  }
}
```

**Response (success):**

```json
{
  "success": true,
  "content": "# Generated vars.py content...",
  "client_count": 1
}
```

**Response (error):**

```json
{
  "success": false,
  "error": "Validation failed: ..."
}
```

---

### POST /api/save-config

Save configuration to `vars.py`. Creates an automatic timestamped backup before writing.

**Request body:** Same format as `/api/generate-config`.

**Response:**

```json
{
  "success": true,
  "message": "Configuration saved",
  "backup": "vars.py.backup.20260708_120000"
}
```

Validates Python syntax before writing. Restores backup on syntax error.

---

### POST /api/preview-config

Generate `vars.py` preview without saving to disk. Same request format as `/api/generate-config`.

---

### POST /api/validate-drive-url

Validate a Google Drive URL format (no API call).

**Request body:**

```json
{
  "url": "https://drive.google.com/drive/folders/1ABC123..."
}
```

**Response:**

```json
{
  "valid": true,
  "folder_id": "1ABC123..."
}
```

---

### POST /api/import-csv

Parse an uploaded CSV file and return validated client data.

**Request:** Multipart form data with a `file` field containing the CSV.

**Expected CSV columns:** `name`, `folder`, `industry`, `subsegments`

**Response:**

```json
{
  "success": true,
  "clients": [ { "id": "...", "name": "...", "folder": "...", "industry": "...", "subsegments": "..." } ],
  "errors": [],
  "total_rows": 5,
  "valid_rows": 5
}
```

---

## Workflow Control

### POST /api/start-workflow

Launch the pipeline workflow in the background. Validates authentication before execution.

**Request body:**

```json
{
  "mode": "fast",
  "clients": ["client_a", "client_b"]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Workflow started",
  "pid": 12345
}
```

The workflow runs as a background process. Monitor progress via `/status` or `/logs/<client_token>`.

---

### POST /api/stop-workflow

Cancel a running workflow and all child processes.

**Response:**

```json
{
  "success": true,
  "message": "Workflow stopped"
}
```

Uses SIGTERM with SIGKILL fallback for process group termination. Updates status of running clients to `CANCELLED`.

---

### POST /api/shutdown

Gracefully shut down the dashboard server.

**Response:**

```json
{
  "success": true,
  "message": "Shutting down"
}
```

Includes a 2-second delay before forced exit to allow the response to be delivered.

---

## Log Streaming

### GET /logs/\<client_token\>

Stream logs for a specific client via Server-Sent Events (SSE).

**Content-Type:** `text/event-stream`

**Path parameter:** `client_token` must match `^[a-zA-Z0-9_-]+$` (max 128 characters).

**Event format:**

```
data: {"line": "14:30:00 | INFO | [client_a] Creating notebook...", "timestamp": 1720000000.0}

data: {"heartbeat": true}
```

- Sends heartbeat events every 10 seconds to prevent proxy timeouts.
- Times out after 60 seconds of idle (no new log lines).

---

### GET /logs/overall

Stream combined logs from all components via SSE. Same event format as client-specific streaming. Longer timeout (600s) to accommodate deep mode workflows.

---

### GET /api/available-logs

List available log files with metadata.

**Response:**

```json
{
  "logs": [
    {
      "name": "client_a.log",
      "type": "client",
      "path": "/path/to/logs/client_a.log",
      "size": 45678
    }
  ]
}
```

---

## Authentication

### GET /api/check-auth-status

Check NotebookLM authentication status.

**Response:**

```json
{
  "authenticated": true,
  "message": "NotebookLM authentication is valid"
}
```

---

### POST /api/notebooklm-login

Trigger the NotebookLM OAuth login flow. Opens a browser window for user authentication.

**Response:**

```json
{
  "success": true,
  "message": "Login completed successfully"
}
```

Uses 300-second timeout. On Linux headless environments, uses `xvfb-run` for browser automation.

---

### POST /api/notebooklm-logout

Clear NotebookLM authentication credentials.

**Response:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### GET /api/oauth-status

Check Google Drive OAuth credential and token status.

**Response:**

```json
{
  "credentials_exist": true,
  "token_exists": true,
  "token_valid": true,
  "client_id": "1234567890-abc..."
}
```

---

### POST /api/upload-oauth-credentials

Upload a Google OAuth `client_secret.json` file.

**Request:** Multipart form data with a `file` field.

**Validation:** Requires `installed.client_id` keys in the JSON structure.

**Response:**

```json
{
  "success": true,
  "message": "Credentials saved",
  "client_id": "1234567890-abcdef..."
}
```

Saves with `0o600` permissions (owner-only read/write).

---

### GET/POST /api/start-oauth-flow

Start the Google Drive OAuth authorization flow via SSE.

**Content-Type:** `text/event-stream`

Opens a browser for user authorization. Streams progress events. Saves the resulting token with `0o600` permissions.

---

### GET /api/test-drive-access

Verify Google Drive API access by listing sample files.

**Response:**

```json
{
  "success": true,
  "message": "Drive access verified",
  "file_count": 10
}
```

Auto-refreshes expired tokens before testing.

---

## Google Drive

### POST /api/refresh-sources

Refresh cached Google Drive sources via SSE. CSRF-exempt.

**Request body:**

```json
{
  "clients": ["client_a", "client_b"]
}
```

**Content-Type:** `text/event-stream`

Streams progress events as each client's Drive folder is re-downloaded. Omitting `clients` refreshes all configured clients.

---

### POST /api/update-notebook-sources

Update sources in existing NotebookLM notebooks via SSE. CSRF-exempt.

**Request body:**

```json
{
  "clients": ["client_a"]
}
```

**Content-Type:** `text/event-stream`

Performs a 5-step process per client: download from Drive, consolidate PDFs, find existing notebook, delete old sources, add new consolidated PDF.

---

### GET /api/cache-stats

Return cache statistics for all configured clients.

**Response:**

```json
{
  "clients": {
    "client_a": {
      "cached": true,
      "file_count": 12,
      "total_size_mb": 8.5,
      "last_refresh": "2026-07-08T12:00:00"
    }
  }
}
```

---

### GET /api/cache-files/\<client_id\>

List individual cached files for a specific client.

**Response:**

```json
{
  "files": [
    {
      "name": "report.pdf",
      "size": 1048576,
      "cached_at": "2026-07-08T12:00:00"
    }
  ]
}
```

---

### POST /api/clear-cache

Clear cached Drive files for selected clients.

**Request body:**

```json
{
  "clients": ["client_a"]
}
```

**Response:**

```json
{
  "success": true,
  "cleared": ["client_a"],
  "freed_mb": 8.5
}
```

---

## System

### GET/POST /api/run-setup

Execute the `setup-environment.sh` script with real-time SSE progress streaming. CSRF-exempt.

**Content-Type:** `text/event-stream`

Strips ANSI color codes from output before streaming. 300-second timeout. Uses `yes |` to auto-answer interactive prompts.

---

### GET / 

Serves the main dashboard HTML page (status monitoring view).

---

### GET /configure

Serves the configuration wizard HTML page.

---

### GET /launch

Serves the launch confirmation page with workflow summary details.
