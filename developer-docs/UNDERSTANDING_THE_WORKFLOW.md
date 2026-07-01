# Understanding Project APE Workflow vs Dashboard

## What You're Seeing

The screenshot shows the **dashboard** displaying:
- **0 Total Clients**
- **0 Running, 0 Complete, 0 Failed**
- **Execution Time: 00m 00s**

This is **completely normal** - it means **no workflow has been started yet**.

## Key Concept

Project APE has two separate components:

### 1. Dashboard Server (Always Running)
- Shows workflow status in real-time
- Accessible at http://localhost:8765
- Can be started independently with: `python3 dashboard/server.py`
- **Only displays information - doesn't run workflows**

### 2. Workflow Execution (Started on Demand)
- Processes clients through the research pipeline
- Downloads files from Google Drive
- Creates NotebookLM notebooks
- Runs AI analysis and generates reports
- **Must be launched separately**

## How to Start a Workflow

The dashboard showing "0 clients" means you need to **launch a workflow**.

### Quick Start

```bash
# Launch workflow with all configured clients
./run-workflow.sh fast
```

This will:
1. ✅ Validate the virtual environment
2. ✅ Check dependencies
3. ✅ Read configuration from `vars.py`
4. ✅ Start processing all configured clients
5. ✅ Update the dashboard with real-time progress

### Available Options

```bash
# Fast mode (15-20 minutes)
./run-workflow.sh fast

# Deep mode (35-40 minutes) 
./run-workflow.sh deep

# Specific clients only
./run-workflow.sh fast merck organon

# Force refresh Drive cache
./run-workflow.sh fast --refresh

# Show help
./run-workflow.sh --help
```

## Complete Workflow

### Step 1: Configure Clients

**Option A: Web UI (Recommended)**
```bash
# Dashboard should already be running at http://localhost:8765
# If not, start it:
python3 dashboard/server.py

# Open browser: http://localhost:8765/configure
# Add clients, configure settings, click "Save Configuration"
```

**Option B: Manual Edit**
```bash
# Copy template
cp example-vars.py vars.py

# Edit configuration
nano vars.py  # or your preferred editor
```

### Step 2: Launch Workflow

```bash
./run-workflow.sh fast
```

### Step 3: Monitor Progress

The dashboard automatically shows:
- Current status for each client
- Pipeline progress
- Quality scores
- Live logs
- Direct links to NotebookLM notebooks

## Troubleshooting

### ❌ "No module named 'dotenv'"

**Cause:** Running with system Python instead of virtual environment

**Fix:** Use the launcher script:
```bash
./run-workflow.sh fast
```

Or activate virtual environment manually:
```bash
source ~/.project-ape-venv/bin/activate
python3 main.py --mode fast
```

### ❌ "Virtual environment not found"

**Cause:** Setup hasn't been run

**Fix:**
```bash
./setup-environment.sh
```

### ❌ "Configuration file not found: vars.py"

**Cause:** No client configuration exists

**Fix:** Configure clients (see Step 1 above)

### ❌ Dashboard shows "0 clients" after launching

**Possible causes:**
1. Workflow command failed to start - check terminal output
2. Configuration file has errors - check `vars.py` syntax
3. Virtual environment issues - verify with:
   ```bash
   source ~/.project-ape-venv/bin/activate
   python3 -c "import dotenv; print('OK')"
   ```

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Browser @ http://localhost:8765    │
│  (Shows real-time status)           │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  Dashboard Server                   │
│  (python3 dashboard/server.py)      │
│  - Serves web UI                    │
│  - Streams status from JSON files   │
│  - Reads logs for display           │
└─────────────────┬───────────────────┘
                  │
                  ↓ (reads status files)
┌─────────────────────────────────────┐
│  .multi_process_status/             │
│  - Client status JSON files         │
│  - Updated by workflow processes    │
└─────────────────────────────────────┘
                  ↑
                  │ (written by)
┌─────────────────────────────────────┐
│  Workflow Execution                 │
│  (./run-workflow.sh fast)           │
│  → main.py                          │
│    → Spawns client processes        │
│    → Each runs core pipeline        │
│    → Updates status files           │
└─────────────────────────────────────┘
```

## Summary

**Dashboard vs Workflow:**
- **Dashboard**: Passive viewer - shows what's happening
- **Workflow**: Active processor - does the actual work

**To see activity in the dashboard:**
1. Make sure clients are configured in `vars.py`
2. Launch a workflow with `./run-workflow.sh fast`
3. Watch the dashboard update in real-time

**Current state:**
- ✅ Dashboard is running correctly
- ⏸️  No workflow has been started
- ▶️  Launch with: `./run-workflow.sh fast`
