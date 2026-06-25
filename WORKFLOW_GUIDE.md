# Project APE Workflow Guide

**Visual guide to understanding Project APE's execution flow**

---

## Complete Workflow Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                    PROJECT APE WORKFLOW                            │
└───────────────────────────────────────────────────────────────────┘

START
  │
  ├─→ [1] User Configuration
  │   ├─→ Web UI (http://localhost:8765/configure)
  │   │   ├─ Add clients
  │   │   ├─ Configure settings
  │   │   └─ Save & Launch
  │   │
  │   └─→ Manual (vars.py)
  │       ├─ Copy example-vars.py
  │       ├─ Edit configuration
  │       └─ Save file
  │
  ├─→ [2] Launch Workflow
  │   │
  │   ├─→ Container Mode (Recommended)
  │   │   └─→ ./launch_ape.sh {fast|deep}
  │   │       ├─ Detect architecture (Intel/ARM)
  │   │       ├─ Pull container image
  │   │       ├─ Mount volumes (code, logs, credentials)
  │   │       ├─ Start container with --rm flag
  │   │       └─ Execute main.py inside container
  │   │
  │   └─→ Local Mode (Development)
  │       └─→ python3 main.py --mode {fast|deep}
  │           ├─ Activate virtual environment
  │           ├─ Load vars.py configuration
  │           └─ Execute directly on host
  │
  ├─→ [3] Orchestration (main.py)
  │   ├─→ Initialize status directory
  │   ├─→ Start Flask dashboard (background)
  │   ├─→ Open browser → http://localhost:8765
  │   └─→ Spawn client processes (parallel)
  │       ├─ Process 1: client_1
  │       ├─ Process 2: client_2
  │       ├─ Process 3: client_3
  │       ├─ Process 4: client_4
  │       ├─ Process 5: client_5
  │       └─ Process 6: client_6
  │
  ├─→ [4] Client Pipeline (per process)
  │   │
  │   ├─→ Phase 1: Download Files
  │   │   ├─ Authenticate (OAuth/Service Account)
  │   │   ├─ List Drive folder contents
  │   │   ├─ Check cache (7-day TTL)
  │   │   ├─ Download files (parallel)
  │   │   │   ├─ PDFs → download
  │   │   │   ├─ Docs → export to PDF
  │   │   │   ├─ Sheets → export to PDF
  │   │   │   └─ Images → download
  │   │   └─ Save to ~/.project-ape/cache/
  │   │
  │   ├─→ Phase 2: Create Notebook
  │   │   ├─ Authenticate NotebookLM
  │   │   ├─ Create new notebook
  │   │   ├─ Set title: "{client_name} Research"
  │   │   └─ Store notebook_id
  │   │
  │   ├─→ Phase 3: Upload Sources
  │   │   ├─ Batch files (20 at a time)
  │   │   ├─ Upload to NotebookLM
  │   │   ├─ Wait for processing
  │   │   │   └─ Poll status every 5s
  │   │   └─ Verify upload success
  │   │
  │   ├─→ Phase 4: Industry Detection (Optional)
  │   │   ├─ Check if industry specified
  │   │   ├─ If empty → Use Gemini AI
  │   │   │   ├─ Analyze source content
  │   │   │   ├─ Classify industry
  │   │   │   └─ Detect subsegments
  │   │   └─ Update configuration
  │   │
  │   ├─→ Phase 5: Research Prompts
  │   │   ├─→ Ask Prompts (3x)
  │   │   │   ├─ Ask: Company overview
  │   │   │   ├─ Ask: Strategic initiatives
  │   │   │   └─ Ask: Technology landscape
  │   │   │   │
  │   │   │   └─ For each prompt:
  │   │   │       ├─ Send to NotebookLM
  │   │   │       ├─ Poll for completion
  │   │   │       ├─ Wait 8-12s (fast) or 15-25s (deep)
  │   │   │       └─ Save response
  │   │   │
  │   │   └─→ Chat Prompts (6x)
  │   │       ├─ Chat: Consolidated plan
  │   │       ├─ Chat: Industry analysis
  │   │       ├─ Chat: Competitive landscape
  │   │       ├─ Chat: Technology stack
  │   │       ├─ Chat: Strategic recommendations
  │   │       └─ Chat: Executive summary
  │   │       │
  │   │       └─ For each prompt:
  │   │           ├─ Send to NotebookLM
  │   │           ├─ Poll for completion
  │   │           ├─ Wait 5-8s (fast) or 10-15s (deep)
  │   │           └─ Save response
  │   │
  │   ├─→ Phase 6: Quality Validation
  │   │   ├─ Count sources (min: 15)
  │   │   ├─ Count notes (min: 6)
  │   │   ├─ Analyze responses
  │   │   ├─ Calculate score (1-10)
  │   │   │   ├─ Sources: 30%
  │   │   │   ├─ Notes: 30%
  │   │   │   └─ Content: 40%
  │   │   └─ If Gemini enabled:
  │   │       ├─ AI quality analysis
  │   │       ├─ Error detection
  │   │       └─ Self-healing (if needed)
  │   │
  │   └─→ Phase 7: Save Results
  │       ├─ Update status file
  │       │   ├─ notebook_id
  │       │   ├─ quality_score
  │       │   ├─ progress: 100%
  │       │   └─ status: COMPLETE
  │       ├─ Write log file
  │       └─ Return to orchestrator
  │
  ├─→ [5] Dashboard Updates (Real-time)
  │   ├─→ Poll /status endpoint (every 2s)
  │   │   ├─ Aggregate status files
  │   │   ├─ Calculate overall progress
  │   │   └─ Return JSON
  │   │
  │   ├─→ Update UI
  │   │   ├─ Client progress bars
  │   │   ├─ Quality scores
  │   │   ├─ Status badges
  │   │   └─ Overall completion
  │   │
  │   └─→ Stream Logs (SSE)
  │       ├─ Read log files
  │       ├─ Send new lines
  │       └─ Auto-scroll viewer
  │
  ├─→ [6] Completion
  │   ├─ All processes finish
  │   ├─ Aggregate results
  │   │   ├─ Total: 6 clients
  │   │   ├─ Successful: X
  │   │   └─ Failed: Y
  │   ├─ Print summary
  │   └─ Start 5-minute countdown
  │
  └─→ [7] Auto-Shutdown
      ├─ Wait 5 minutes (user review time)
      ├─ Stop Flask server
      ├─ Exit Python process
      ├─ Container stops (main process exit)
      └─ Container removed (--rm flag)

END
```

---

## Timing Breakdown

### Fast Mode (15-20 minutes total)

```
Timeline for 6 clients (parallel execution):

0:00  ├─ Launch workflow
0:15  ├─ All processes start
      │
0:30  ├─ Phase 1: Download Files (30s - 1min)
      │  └─ Parallel downloads for all clients
      │
1:30  ├─ Phase 2: Create Notebooks (10s each)
      │  └─ 6 notebooks created in parallel
      │
2:00  ├─ Phase 3: Upload Sources (2-3 min)
      │  └─ Batch uploads, parallel processing
      │
5:00  ├─ Phase 4: Industry Detection (30s - 1min)
      │  └─ Gemini AI analysis (if enabled)
      │
6:00  ├─ Phase 5: Research Prompts (8-12 min)
      │  │
      │  ├─ Ask Prompts (3x ~10s each)
      │  │  0:00 → Prompt 1 sent
      │  │  0:10 → Prompt 2 sent
      │  │  0:20 → Prompt 3 sent
      │  │  0:30 → All complete
      │  │
      │  └─ Chat Prompts (6x ~7s each)
      │     0:30 → Prompt 1 sent
      │     0:37 → Prompt 2 sent
      │     ... (staggered)
      │     1:12 → All complete
      │
18:00 ├─ Phase 6: Quality Validation (30s)
      │  └─ Score calculation
      │
18:30 ├─ Phase 7: Save Results (10s)
      │  └─ Write status files
      │
19:00 └─ COMPLETE (all 6 clients)
      │
      └─ 5-minute review period
          │
24:00     └─ Auto-shutdown
```

### Deep Mode (45-60 minutes total)

```
Timeline for 6 clients (parallel execution):

0:00  ├─ Launch workflow
      │
2:00  ├─ Phases 1-4: Same as Fast (2-6 min)
      │
8:00  ├─ Phase 5: Research Prompts (35-45 min)
      │  │
      │  ├─ Ask Prompts (3x ~20s each)
      │  │  └─ Longer processing delays
      │  │
      │  └─ Chat Prompts (6x ~12s each)
      │     └─ More thorough analysis
      │
53:00 ├─ Phase 6: Quality Validation (1-2 min)
      │  └─ Gemini AI deep validation
      │
55:00 ├─ Phase 7: Save Results (10s)
      │
56:00 └─ COMPLETE (all 6 clients)
      │
      └─ 5-minute review period
          │
61:00     └─ Auto-shutdown
```

---

## State Machine Diagram

```
Client Process State Transitions:

PENDING
  │
  ├─→ START
  │     │
  │     ├─→ DOWNLOADING
  │     │     │
  │     │     ├─→ SUCCESS → CREATING_NOTEBOOK
  │     │     └─→ FAIL → ERROR_DOWNLOAD
  │     │
  │     ├─→ CREATING_NOTEBOOK
  │     │     │
  │     │     ├─→ SUCCESS → UPLOADING_SOURCES
  │     │     └─→ FAIL → ERROR_NOTEBOOK
  │     │
  │     ├─→ UPLOADING_SOURCES
  │     │     │
  │     │     ├─→ SUCCESS → DETECTING_INDUSTRY
  │     │     └─→ FAIL → ERROR_UPLOAD
  │     │
  │     ├─→ DETECTING_INDUSTRY
  │     │     │
  │     │     ├─→ SUCCESS → RUNNING_RESEARCH
  │     │     └─→ FAIL → RUNNING_RESEARCH (optional)
  │     │
  │     ├─→ RUNNING_RESEARCH
  │     │     │
  │     │     ├─→ Ask Prompt 1 → WAITING
  │     │     ├─→ Ask Prompt 2 → WAITING
  │     │     ├─→ Ask Prompt 3 → WAITING
  │     │     ├─→ Chat Prompt 1 → WAITING
  │     │     ├─→ Chat Prompt 2 → WAITING
  │     │     ├─→ Chat Prompt 3 → WAITING
  │     │     ├─→ Chat Prompt 4 → WAITING
  │     │     ├─→ Chat Prompt 5 → WAITING
  │     │     ├─→ Chat Prompt 6 → WAITING
  │     │     │
  │     │     ├─→ ALL SUCCESS → VALIDATING_QUALITY
  │     │     └─→ ANY FAIL → ERROR_RESEARCH
  │     │
  │     ├─→ VALIDATING_QUALITY
  │     │     │
  │     │     ├─→ PASS → SAVING_RESULTS
  │     │     └─→ FAIL → DEGRADED
  │     │
  │     └─→ SAVING_RESULTS
  │           │
  │           └─→ COMPLETE
  │
  └─→ Error States
        ├─→ ERROR_DOWNLOAD
        ├─→ ERROR_NOTEBOOK
        ├─→ ERROR_UPLOAD
        ├─→ ERROR_RESEARCH
        └─→ DEGRADED (partial success)
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

Configuration Data:
vars.py
  ├─→ Clients list
  ├─→ Drive folder URLs
  ├─→ Execution settings
  └─→ Timing profiles

           ↓

Main Orchestrator (main.py):
  ├─→ Reads vars.py
  ├─→ Spawns processes
  └─→ Manages lifecycle

           ↓

Client Process (per client):
  ├─→ Reads configuration
  ├─→ Executes pipeline
  └─→ Writes outputs

           ↓

Outputs:
  ├─→ Status Files (.multi_process_status/)
  │   ├─ client_1.json
  │   ├─ client_2.json
  │   └─ ...
  │
  ├─→ Log Files (logs/)
  │   ├─ client_1.log
  │   ├─ client_2.log
  │   ├─ overall.log
  │   └─ ...
  │
  └─→ Cache (~/project-ape/cache/)
      ├─ drive_files/
      └─ metadata/

           ↓

Dashboard (dashboard/server.py):
  ├─→ Aggregates status files
  ├─→ Streams log files
  └─→ Serves web UI

           ↓

User Browser:
  ├─→ Views progress
  ├─→ Monitors logs
  └─→ Clicks NotebookLM links

           ↓

NotebookLM:
  └─→ Opens research notebook
```

---

## Error Handling Flow

```
Error Occurs
  │
  ├─→ Transient Error
  │   ├─ Network timeout
  │   ├─ API rate limit
  │   └─ Temporary service issue
  │       │
  │       └─→ Retry Logic
  │           ├─ Exponential backoff
  │           ├─ Max 5 retries
  │           │
  │           ├─→ SUCCESS → Continue
  │           └─→ FAIL → Permanent Error
  │
  └─→ Permanent Error
      ├─ Invalid credentials
      ├─ Missing file
      └─ Configuration error
          │
          ├─→ If Gemini Enabled
          │   ├─ Analyze error
          │   ├─ Suggest fix
          │   ├─ Attempt self-heal
          │   │
          │   ├─→ SUCCESS → Continue
          │   └─→ FAIL → Log & Exit
          │
          └─→ If Gemini Disabled
              ├─ Log error
              ├─ Update status: FAILED
              └─ Exit process
```

---

## Quality Scoring Algorithm

```
Quality Score Calculation (1-10 scale):

Input:
  ├─ source_count (number of files uploaded)
  ├─ notes_count (number of notes created)
  └─ content_analysis (Gemini AI evaluation)

Weights:
  ├─ Sources: 30%
  ├─ Notes: 30%
  └─ Content: 40%

Formulas:
  source_score = min(source_count / 15, 1.0) * 3.0
  notes_score = min(notes_count / 6, 1.0) * 3.0
  content_score = ai_rating * 4.0

  quality_score = source_score + notes_score + content_score

Thresholds:
  9.0 - 10.0 → Excellent
  8.0 - 8.9  → Good
  7.0 - 7.9  → Acceptable
  6.0 - 6.9  → Needs Review
  < 6.0      → Failed

Example:
  Sources: 20 files → min(20/15, 1.0) * 3.0 = 3.0
  Notes: 8 notes   → min(8/6, 1.0) * 3.0 = 3.0
  Content: AI=0.85 → 0.85 * 4.0 = 3.4
  
  Total: 3.0 + 3.0 + 3.4 = 9.4 (Excellent)
```

---

## File Structure During Execution

```
project-ape/
│
├── vars.py                    # User configuration (INPUT)
│
├── logs/                      # Created at runtime
│   ├── overall.log            # Orchestrator logs
│   ├── client_1.log           # Per-client logs
│   ├── client_2.log
│   └── ...
│
├── .multi_process_status/     # Created at runtime
│   ├── client_1.json          # Real-time status
│   │   {
│   │     "name": "Acme Corp",
│   │     "status": "RUNNING",
│   │     "progress": 65,
│   │     "step": "Running research prompts",
│   │     "notebook_id": "abc123",
│   │     "quality_score": null,
│   │     "start_time": 1719324000
│   │   }
│   ├── client_2.json
│   └── ...
│
└── ~/.project-ape/            # User home directory
    ├── cache/                 # Drive file cache
    │   ├── drive_files/
    │   │   ├── client_1/
    │   │   │   ├── doc1.pdf
    │   │   │   ├── doc2.pdf
    │   │   │   └── ...
    │   │   └── client_2/
    │   └── metadata/
    │       └── cache_manifest.json
    │
    └── credentials/           # Authentication
        ├── drive_token.json
        └── drive_credentials.json
```

---

## API Endpoints Flow

```
Dashboard Web Server (Flask)

GET /
  └─→ Serve dashboard.html
      ├─ Loads client cards
      ├─ Starts auto-refresh
      └─ Fetches /status

GET /status
  └─→ Read status files
      ├─ Aggregate data
      └─ Return JSON
          {
            "total": 6,
            "running": 2,
            "complete": 4,
            "failed": 0,
            "clients": [...]
          }

GET /stream-logs?log=overall
  └─→ Open SSE connection
      ├─ Read log file
      ├─ Tail new lines
      └─ Push updates
          data: [LOG LINE]\n\n

GET /configure
  └─→ Serve configure.html
      └─ Load configuration UI

POST /api/start-workflow
  └─→ Receive workflow config
      ├─ Spawn launch_ape.sh
      └─ Return success

POST /api/shutdown
  └─→ Graceful shutdown
      ├─ Wait 2 seconds
      └─ Exit process
```

---

## Container Volume Mounts

```
Container Runtime (Podman):

podman run --rm \
  ├─ -v $(pwd)/vars.py:/app/vars.py:ro
  │    └─→ Configuration (read-only)
  │
  ├─ -v $(pwd)/main.py:/app/main.py:ro
  │    └─→ Main script (read-only)
  │
  ├─ -v $(pwd)/core:/app/core:ro
  │    └─→ Core modules (read-only)
  │
  ├─ -v $(pwd)/dashboard:/app/dashboard:ro
  │    └─→ Dashboard code (read-only)
  │
  ├─ -v $(pwd)/logs:/app/logs:z
  │    └─→ Log output (read-write)
  │
  ├─ -v $(pwd)/.multi_process_status:/app/.multi_process_status:z
  │    └─→ Status files (read-write)
  │
  ├─ -v $HOME/.project-ape:/home/apeuser/.project-ape:z
  │    └─→ Cache & credentials (read-write)
  │
  ├─ -v project-ape-credentials:/home/apeuser/.notebooklm
  │    └─→ NotebookLM auth (volume)
  │
  └─ -p 8765:8765
       └─→ Dashboard port mapping
```

---

## Summary

**Total Workflow Time:**
- Fast mode: 15-20 minutes (6 clients in parallel)
- Deep mode: 45-60 minutes (6 clients in parallel)

**Key Phases:**
1. Download (30s-1min)
2. Create Notebook (10s)
3. Upload Sources (2-3min)
4. Detect Industry (30s-1min, optional)
5. Research Prompts (8-45min, mode-dependent)
6. Quality Validation (30s-2min)
7. Save Results (10s)

**Outputs:**
- NotebookLM notebooks with research
- Quality scores (1-10 scale)
- Detailed logs
- Real-time status

**Auto-Cleanup:**
- 5-minute review period
- Container auto-removes
- Logs persist for review

---

**Version**: 3.2.0  
**Last Updated**: June 25, 2026
