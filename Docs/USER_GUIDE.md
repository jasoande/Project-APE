<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence" width="150"/>

  # User Guide

  **Account Intelligence - Account Planning Engine**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration Wizard](#configuration-wizard)
- [Adding Clients](#adding-clients)
- [Running Workflows](#running-workflows)
- [Monitoring with the Dashboard](#monitoring-with-the-dashboard)
- [Stopping a Workflow](#stopping-a-workflow)
- [Pre-flight Checks](#pre-flight-checks)
- [Webhook Notifications](#webhook-notifications)
- [Resuming from Checkpoint](#resuming-from-checkpoint)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launch the Application

The recommended way to start Account Intelligence is with the GUI launcher. No terminal experience is required.

**macOS:**

Double-click `launch-project-ape.command` in Finder, or run from terminal:

```bash
python3 launch-project-ape.py
```

**Windows / Linux:**

Double-click `launch-project-ape.py`, or run from terminal:

```bash
python3 launch-project-ape.py
```

On first run, the launcher will:

1. Create a virtual environment at `~/.project-ape-venv`
2. Install all required dependencies (Flask, notebooklm-py, pypdf, etc.)
3. Start the dashboard server on port 8765
4. Open your browser to `http://localhost:8765/configure`

### Prerequisites

- Python 3.10 or later
- Google Chrome (required for NotebookLM authentication)
- Internet connection for NotebookLM API access
- Google Drive folder with client PDFs (or local PDF directory)

---

## Configuration Wizard

When you first open the dashboard, you will see a 3-step setup wizard at `http://localhost:8765/configure`.

### Step 1: Authenticate NotebookLM

Click the "Authenticate NotebookLM" button. This opens Chrome and walks you through Google OAuth. Once complete, the wizard shows a green check mark.

If you have already authenticated on another machine, you can copy the credentials:

```bash
scp ~/.notebooklm/credentials.json user@this-machine:~/.notebooklm/
```

### Step 2: Setup Drive OAuth

1. Click "Setup Drive OAuth"
2. Upload your `credentials.json` file (downloaded from Google Cloud Console)
3. A browser window opens for Google authorization
4. Grant access to Google Drive

The resulting token is saved at `~/.project-ape/drive_token.json` and is valid for approximately 90 days.

### Step 3: Environment Validation

The wizard automatically checks that all required components are in place:

- NotebookLM CLI installed and responsive
- NotebookLM authentication valid
- Google Drive token present
- Virtual environment activated

---

## Adding Clients

### Via Web UI

1. Navigate to `http://localhost:8765/configure`
2. Scroll to the "Add New Client" form
3. Fill in the required fields:

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| Client Name | Yes | Display name for the client | `Acme Corporation` |
| Client ID | Auto | Generated from name (editable) | `acme_corporation` |
| Drive Folder URL | Yes | Google Drive folder with client PDFs | `https://drive.google.com/drive/folders/1ABC...` |
| Industry | No | Leave blank for auto-detection | `technology` |
| Subsegments | No | Comma-separated focus areas | `cloud, AI, enterprise software` |
| Mode | Yes | Fast (15-20 min) or Deep (45-60 min) | `fast` |

4. Click "Add Client"
5. Click "Save Configuration" to write `vars.py`

### Via CSV Import

For batch setup, prepare a CSV file with columns: `name`, `folder`, `industry`, `subsegments`. Upload it through the web UI import form.

### Common Industry/Subsegment Combinations

| Industry | Subsegments |
|----------|-------------|
| Technology | cloud services, SaaS platforms, cybersecurity, AI/ML, DevOps |
| Financial Services | banking, insurance, wealth management, fintech, payments |
| Healthcare | hospitals, pharmaceuticals, medical devices, health IT, telehealth |
| Manufacturing | automotive, aerospace, electronics, supply chain, IoT |
| Retail | e-commerce, omnichannel, supply chain, customer analytics |

---

## Running Workflows

### Fast Mode (15-20 minutes)

Best for initial account planning and quick turnaround. Imports 10-25 external sources per research query with a retry rate of approximately 5%.

### Deep Mode (45-60 minutes)

Best for thorough analysis with maximum source coverage. Imports 45-90 sources per query. Accepts a higher retry rate (~30%) to achieve broader coverage.

### Starting a Workflow

**From the Web UI:**

1. Configure your clients at `/configure`
2. Click "Launch Workflow"
3. The dashboard automatically switches to the monitoring view at `/status`

**From the Terminal:**

```bash
# Fast mode
./run-workflow.sh fast

# Deep mode
./run-workflow.sh deep
```

**Container execution:**

```bash
./ape-run.sh --vars ./vars.py --clients client_a,client_b --mode fast
```

### What Happens During a Workflow

Each client goes through 5 phases:

1. **PDF Download & Consolidation (30-60s):** Downloads PDFs from Google Drive (with 7-day caching), merges into a single document with table of contents.
2. **Notebook Creation (10s):** Creates a NotebookLM notebook (or reuses an existing one), uploads the consolidated PDF.
3. **Research (3-5 min):** Executes 2 research queries that trigger web research and import external sources.
4. **Analysis (8-12 min):** Runs 6 chat prompts covering industry overview, technology trends, competitive positioning, pain points, decision makers, value proposition, and strategic recommendations.
5. **Quality Validation (1-2 min):** Scores output quality across 4 dimensions, generates a mind map artifact, and creates a summary document.

---

## Monitoring with the Dashboard

The dashboard at `http://localhost:8765` provides real-time monitoring:

- **Progress bars:** Per-client progress (0-100%) with current phase description
- **Status indicators:** RUNNING, COMPLETE, FAILED, or CANCELLED
- **Live log streaming:** Click on a client to view real-time log output via SSE
- **Quality scores:** Displayed upon completion (1.0-10.0 scale)
- **Execution metrics:** Start time, elapsed time, mode

The dashboard auto-refreshes every 2 seconds via server-sent events.

### Status File Structure

Each client's status is tracked in `.multi_process_status/{client_id}.json`:

```json
{
  "name": "Client Corp",
  "token": "client_corp",
  "step": "Running chat prompts (4/6)",
  "progress": 65,
  "status": "RUNNING",
  "mode": "fast",
  "notebook_id": "nb_abc123",
  "last_update": 1720000000.0,
  "start_time": 1719999000.0,
  "quality_score": null,
  "run_id": "run_20260708_120000"
}
```

---

## Stopping a Workflow

To cancel a running workflow:

1. Click the "Stop Workflow" button on the dashboard
2. The system sends SIGTERM to the workflow process group
3. If processes do not terminate within a few seconds, SIGKILL is used as a fallback
4. Running clients are marked as `CANCELLED` in their status files

From the terminal, press `Ctrl+C` to trigger a graceful shutdown.

---

## Pre-flight Checks

Before launching a workflow, the system can run pre-flight checks to validate that all prerequisites are met. Access this from the dashboard or via the API:

```
GET /api/preflight-check
```

The following checks are performed:

| Check | What It Validates |
|-------|-------------------|
| NotebookLM CLI | The `notebooklm` command is installed and responds |
| NotebookLM Auth | OAuth credentials are present and valid |
| Drive Auth | Drive token exists with a valid `token` key |
| Config Valid | `vars.py` has a non-empty `clients` list with required attributes |

All checks must pass before a workflow can proceed.

---

## Webhook Notifications

Account Intelligence can send a notification when a workflow completes. Add the following to your `vars.py`:

```python
NOTIFICATION_WEBHOOK_URL = "https://hooks.slack.com/services/T.../B.../xxx"
```

When a workflow finishes (whether all clients succeed or some fail), a Slack Block Kit message is sent to the webhook with:

- Total number of clients processed
- Successful / failed counts
- Total workflow duration

The notification fires once per workflow run. If the webhook URL is not configured, no notification is sent.

Compatible with any webhook endpoint that accepts JSON POST requests with Slack Block Kit format.

---

## Resuming from Checkpoint

If a workflow is interrupted (network failure, system crash, quota exhaustion), you can resume from the last completed phase using the `--resume` flag:

```bash
./run-workflow.sh fast --resume
```

The checkpoint system:

- Saves progress after each of the 8 pipeline phases
- Stores checkpoint files in `logs/.checkpoints/{client_id}.json`
- Skips already-completed phases on resume
- Clears the checkpoint file upon successful completion

### Checkpoint Phases

1. `setup_folder` - Download/locate client documents
2. `determine_industry` - Industry classification
3. `check_auth` - Authentication validation
4. `create_notebook` - Notebook creation
5. `consolidate_pdf` - PDF merging
6. `run_research` - Research queries
7. `run_chat` - Analysis prompts
8. `generate_mindmap` - Mind map generation

If a failure occurs during phase 6 (research), resuming will skip phases 1-5 and pick up at phase 6.

---

## Troubleshooting

### Authentication Issues

**"Authentication failed" or "NotebookLM authentication not found"**

- Run `notebooklm login` on a machine with Chrome
- Or copy credentials: `scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/`
- Verify the file exists: `ls -la ~/.notebooklm/credentials.json`

**"Drive token not found"**

- Complete the Drive OAuth setup in the configuration wizard
- Or run: `python3 setup-oauth-drive.py`
- Verify: `ls -la ~/.project-ape/drive_token.json`

### Dashboard Issues

**"Dashboard not accessible" at localhost:8765**

- Check the server is running: `ps aux | grep server.py`
- Check port availability: `lsof -i :8765`
- Try restarting: `./restart-dashboard.sh`

### Workflow Issues

**High retry rate in fast mode**

- Normal rate is approximately 5%. If higher, increase delays in `TIMINGS` configuration.
- Consider switching to deep mode for accounts with many sources.

**"Research timeout" errors**

- Normal for large accounts in deep mode (~30% retry rate is acceptable)
- The system retries automatically with exponential backoff
- Check network connectivity if retries are consistently failing

**Workflow hangs or no progress**

- Check logs: `tail -f logs/{client_id}.log`
- Look for errors: `grep "ERROR" logs/*.log`
- Check status files: `cat .multi_process_status/{client_id}.json`

### Output Verification

After a successful run, verify outputs:

- Check `docs_generated/{client_id}/` for generated documents
- Review `Quality_Score.json` for quality metrics
- Open the NotebookLM link in the summary document to view the notebook

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
