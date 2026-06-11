# Project APE - Technical Architecture

**Version:** 1.0.0  
**Date:** June 2026  
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Process Flow](#process-flow)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Security Architecture](#security-architecture)
8. [Scalability](#scalability)

---

## System Overview

Project APE (Account Planning Engine) is a distributed, multi-process automation system designed to generate comprehensive account plans using Google NotebookLM's AI capabilities.

### Key Characteristics

- **Architecture Pattern**: Multi-Process with Central Orchestration
- **Concurrency Model**: True OS-level parallelization (not async/await)
- **Communication**: File-based status sharing
- **UI Pattern**: Server-Side Rendering with AJAX polling
- **Deployment**: Single-server, multi-client

### Core Principles

1. **Process Isolation**: Each client runs in independent Python process
2. **Fail-Safe**: One client failure doesn't affect others
3. **Observable**: Real-time status via web dashboard
4. **Idempotent**: Re-running is safe (notebook deduplication)
5. **Extensible**: Easy to add new clients or modify pipeline

---

## Component Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   MAIN ORCHESTRATOR                      │
│                     (main.py)                            │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Process  │  │   Status     │  │   Dashboard    │  │
│  │  Manager   │  │  Management  │  │    Server      │  │
│  └────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────┘
         │                    │                 │
         │                    │                 │
    ┌────▼─────┐         ┌───▼───┐        ┌───▼─────┐
    │Client    │         │Status │        │ Flask   │
    │Process 1 │  ...    │Files  │        │Dashboard│
    └────┬─────┘         └───┬───┘        └────┬────┘
         │                   │                  │
    ┌────▼────────────────────────────────────────┐
    │        CLIENT PIPELINE                      │
    │       (client_pipeline.py)                  │
    ├─────────────────────────────────────────────┤
    │  ┌──────────────┐  ┌──────────────────┐   │
    │  │ Auth Manager │  │ Notebook Manager │   │
    │  └──────────────┘  └──────────────────┘   │
    │  ┌──────────────┐  ┌──────────────────┐   │
    │  │Source Manager│  │  PDF Consolidator│   │
    │  └──────────────┘  └──────────────────┘   │
    └─────────────────────────────────────────────┘
                        │
                        ▼
             ┌──────────────────┐
             │  NotebookLM CLI  │
             │  (External API)  │
             └──────────────────┘
```

---

## Component Responsibilities

### 1. Main Orchestrator (`main.py`)

**Purpose**: Central coordinator for the entire system

**Responsibilities**:
- Parse command-line arguments
- Initialize status directory structure
- Start Flask dashboard server
- Spawn client processes
- Monitor process completion
- Aggregate and report results
- Handle graceful shutdown

**Dependencies**:
- `vars.py` - Configuration
- `dashboard/server.py` - Web server
- `core/client_pipeline.py` - Client executor

### 2. Client Pipeline (`core/client_pipeline.py`)

**Purpose**: Execute complete pipeline for single client

**Responsibilities**:
- Check and ensure authentication
- Get or create notebook (with deduplication)
- Consolidate client files to PDF
- Upload sources to NotebookLM
- Execute research prompts sequentially
- Import cited web sources
- Deduplicate sources
- Execute chat prompts with note creation
- Generate mind map
- Update status file throughout

**Dependencies**:
- Auth Manager
- Notebook Manager
- Source Manager
- PDF Consolidator

### 3. Notebook Manager (`core/notebook_manager.py`)

**Purpose**: Manage NotebookLM notebooks with deduplication

**Key Methods**:
- `find_notebook_by_name()` - Search for existing notebook
- `create_notebook()` - Create new notebook
- `get_or_create_notebook()` - Deduplication entry point
- `set_context()` - Set current notebook context

**Deduplication Logic**:
```python
existing = self.find_notebook_by_name(name)
if existing:
    return existing  # Use existing
else:
    return self.create_notebook(name)  # Create new
```

### 4. Source Manager (`core/source_manager.py`)

**Purpose**: Manage sources with import and deduplication

**Key Methods**:
- `add_file_source()` - Upload file
- `add_research_with_import()` - Research + import sources
- `list_sources()` - Get all sources
- `deduplicate_sources()` - Remove duplicates

**Deduplication Algorithm**:
1. List all sources
2. Track seen URLs and titles
3. Mark duplicates for deletion
4. Delete marked sources

### 5. PDF Consolidator (`core/pdf_consolidator.py`)

**Purpose**: Universal file-to-PDF converter

**Supported Formats**:
- Text: .txt, .md, .log, .json, .xml, .py, .js
- Images: .jpg, .png, .gif, .bmp, .tiff, .webp
- Office: .docx, .doc, .xlsx, .xls, .pptx, .ppt
- PDF: .pdf (pass-through)

**Conversion Strategy**:
- Text → ReportLab PDF
- Images → PIL to PDF
- Office → LibreOffice conversion
- PDF → Direct inclusion

### 6. Auth Manager (`core/auth_manager.py`)

**Purpose**: Manage NotebookLM authentication

**Strategy**:
- Check auth status periodically (5 min intervals)
- Cache auth state to avoid repeated checks
- Graceful degradation if auth fails

### 7. Dashboard Server (`dashboard/server.py`)

**Purpose**: Real-time web monitoring interface

**Endpoints**:
- `GET /` - Main dashboard HTML
- `GET /status` - JSON status aggregation
- `GET /logs/<client>` - Log streaming (SSE)

**Update Mechanism**:
- Client JavaScript polls `/status` every 2 seconds
- Server reads JSON files from `.multi_process_status/`
- Aggregates and returns current state

---

## Process Flow

### Startup Sequence

```
1. main.py starts
   ├─ Parse arguments
   ├─ Load configuration
   ├─ Create directories
   │
2. Initialize status files
   ├─ For each client:
   │  └─ Create {client}.json with PENDING status
   │
3. Start dashboard server
   ├─ Flask app on port 8765
   ├─ Open browser automatically
   │
4. Spawn client processes
   ├─ For each client:
   │  ├─ Open log file
   │  ├─ Start client_pipeline.py as subprocess
   │  └─ Pass client_id, mode, status_file
   │
5. Monitor processes
   ├─ Poll process.poll() every 5 seconds
   ├─ Wait until all processes complete
   │
6. Report results
   ├─ Count successful/failed
   ├─ Display summary
   │
7. Keep dashboard running
   ├─ Allow user review
   ├─ Wait for Ctrl+C
   │
8. Cleanup
   └─ Terminate all processes gracefully
```

### Client Pipeline Flow

```
1. Authenticate
   └─ Check auth, re-login if needed
   
2. Get/Create Notebook
   ├─ Search for existing notebook by name
   ├─ Use existing if found
   └─ Create new if not found
   
3. Consolidate PDFs
   ├─ Find all files in client folder
   ├─ Convert each to PDF
   │  ├─ Text files → ReportLab
   │  ├─ Images → PIL
   │  ├─ Office → LibreOffice
   │  └─ PDFs → Pass through
   └─ Merge into {Client}-One.pdf
   
4. Upload Sources
   └─ Upload consolidated PDF to notebook
   
5. Execute Ask Prompts (Sequential)
   ├─ For each ask_*.txt in order:
   │  ├─ Run research with --import-all
   │  ├─ Import cited web sources
   │  └─ Wait (rate limiting)
   
6. Deduplicate Sources
   ├─ List all sources
   ├─ Identify duplicates (URL/title)
   └─ Delete duplicates
   
7. Execute Chat Prompts (Sequential)
   ├─ For each chat_*.txt in order:
   │  ├─ Run ask command
   │  ├─ Save as note (--save-as-note)
   │  └─ Wait (rate limiting)
   
8. Generate Mind Map
   └─ Create mind-map artifact
   
9. Complete
   └─ Set status to COMPLETE
```

---

## Data Flow

### Status Files

**Location**: `.multi_process_status/{client_id}.json`

**Format**:
```json
{
  "name": "Merck",
  "token": "merck_test",
  "step": "Running chat prompts 3/10",
  "progress": 75,
  "status": "RUNNING",
  "notebook_id": "abc123-def456",
  "mode": "fast",
  "last_update": 1717977600.0,
  "quality_score": null,
  "plan_link": null,
  "log_file": "logs/merck_test.log"
}
```

**Update Frequency**: After each major step (5-10% progress increments)

**Readers**: Dashboard server, main orchestrator

**Writers**: Client pipeline process

### Log Files

**Location**: `logs/{client_id}.log`

**Format**: Plain text with timestamps

**Update Frequency**: Real-time as pipeline executes

**Readers**: Dashboard (for streaming), developers (for debugging)

**Writers**: Client pipeline stdout/stderr

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.10+ | Main language |
| Process Mgmt | subprocess | stdlib | Multi-process execution |
| Web Framework | Flask | 3.0+ | Dashboard server |
| PDF Generation | ReportLab | 4.0+ | Text-to-PDF |
| PDF Manipulation | pypdf/PyPDF2 | 3.0+/4.0+ | PDF merging |
| Image Processing | Pillow | 10.0+ | Image-to-PDF |
| Office Conversion | LibreOffice | - | DOCX/XLSX to PDF |
| API Client | NotebookLM CLI | Latest | Google NotebookLM |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| HTML/CSS | Custom | Dashboard UI |
| JavaScript | Vanilla JS | AJAX polling |
| Theme | Red Hat Design | Professional styling |

### External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Google NotebookLM | AI processing | Yes |
| LibreOffice | Office conversion | Recommended |

---

## Design Decisions

### Why Multi-Process vs Async?

**Decision**: Use OS-level processes instead of asyncio

**Reasoning**:
1. **True Parallelization**: NotebookLM CLI is I/O bound; processes allow OS-level scheduling
2. **Isolation**: One client crash doesn't affect others
3. **Simplicity**: Easier to reason about than async/await with external CLI calls
4. **Observability**: Each process has own PID, log file, status
5. **Resource Management**: OS handles CPU/memory allocation

**Trade-offs**:
- Higher memory overhead (6 Python interpreters)
- More complex inter-process communication
- Benefits outweigh costs for this use case

### Why File-Based Status vs Database?

**Decision**: JSON files in `.multi_process_status/`

**Reasoning**:
1. **Simplicity**: No database setup required
2. **Portability**: Works anywhere Python runs
3. **Debuggable**: Human-readable JSON
4. **Atomic Writes**: OS-level file writes are atomic on most filesystems
5. **Sufficient**: 6-10 clients don't need database

**Trade-offs**:
- Not suitable for 100+ clients
- No built-in locking (rely on atomic writes)
- For this scale (6 clients), perfect solution

### Why Flask vs WebSockets?

**Decision**: Flask with AJAX polling every 2 seconds

**Reasoning**:
1. **Simplicity**: No WebSocket library needed
2. **Reliability**: Polling is more reliable than persistent connections
3. **Sufficient**: 2-second updates are fast enough
4. **Debugging**: Easier to debug than WebSockets
5. **Browser Compatibility**: Works in all browsers

**Trade-offs**:
- Slightly higher latency than WebSockets
- More HTTP requests
- For dashboard use case, acceptable

---

## Security Architecture

### Authentication

- **Method**: NotebookLM CLI handles Google OAuth
- **Storage**: Tokens stored in `~/.notebooklm/`
- **Scope**: User's Google account
- **Refresh**: Automatic via CLI

### Data Security

- **Client Data**: Stays in client folders, never transmitted except to NotebookLM
- **Status Files**: Local only, not transmitted
- **Logs**: May contain sensitive data, should be secured
- **Network**: Only outbound to Google APIs

### Access Control

- **Dashboard**: No authentication (localhost only)
- **NotebookLM**: Google account required
- **File System**: Standard UNIX permissions

### Recommendations

1. Run on trusted machine
2. Secure log files appropriately
3. Don't expose dashboard port publicly
4. Use VPN if accessing dashboard remotely
5. Review logs before sharing

---

## Scalability

### Current Capacity

- **Clients**: 6 simultaneous (configurable)
- **Files per Client**: ~100-500
- **Prompts**: 2 ask + 10 chat = 12 total per client
- **Duration**: 15-60 minutes depending on mode
- **Resources**: ~2GB RAM, minimal CPU

### Scaling Up

**To 20 Clients**:
- Increase `config.clients` list
- May need to increase rate limit delays
- More memory required (~4-6GB)
- Dashboard handles 20 clients easily

**To 50+ Clients**:
- Consider batch processing (10 at a time)
- May need database instead of JSON files
- Consider distributed architecture
- Add queue system

### Horizontal Scaling

Current design is single-server. For true horizontal scaling:

1. **Queue-Based Architecture**:
   - Add message queue (RabbitMQ, Redis)
   - Workers pull from queue
   - Central status database

2. **Distributed Dashboard**:
   - Central status aggregation service
   - Multiple worker nodes
   - Load balancer

3. **Cloud Deployment**:
   - Containerize with Docker
   - Deploy on Kubernetes
   - Auto-scaling workers

---

## Performance Characteristics

### Throughput

- **Sequential (single process)**: ~90 minutes for 6 clients
- **Parallel (6 processes)**: ~15-20 minutes for 6 clients
- **Speedup**: ~4.5x-6x

### Resource Usage

- **Memory**: ~300MB per client process
- **CPU**: Minimal (mostly I/O wait)
- **Network**: ~10-50MB per client (depends on sources)
- **Disk**: ~100MB per client (PDFs, logs)

### Bottlenecks

1. **NotebookLM API Rate Limits**: Primary bottleneck
2. **LibreOffice Conversion**: Can be slow for large documents
3. **Network Latency**: Affects all API calls

### Optimization Opportunities

1. Cache authentication checks longer
2. Parallel PDF conversion within client
3. Batch source uploads
4. Optimize deduplication algorithm

---

## Monitoring & Observability

### Live Monitoring

- **Dashboard**: Real-time web UI
- **Logs**: Per-client log files
- **Status Files**: JSON inspection

### Metrics

- Total clients
- Running/complete/failed counts
- Per-client progress percentage
- Overall pipeline progress
- Execution duration

### Debugging

1. **Check Logs**: `tail -f logs/{client}.log`
2. **Check Status**: `cat .multi_process_status/{client}.json`
3. **Check Processes**: `ps aux | grep client_pipeline`
4. **Check Dashboard**: http://localhost:8765

---

## Error Handling

### Strategy: Fail Independently

- One client failure doesn't stop others
- Errors logged to client log file
- Status updated to FAILED
- Pipeline continues

### Recovery

- **Auth Failures**: Detect early, fail fast
- **Network Errors**: Retry with exponential backoff
- **Rate Limits**: Extended backoff, multiple retries
- **PDF Conversion**: Skip problematic files, continue

### Graceful Degradation

- If LibreOffice missing, skip Office docs
- If source upload fails, continue to prompts
- If mind map fails, pipeline still completes

---

**Document Version**: 1.0.0  
**Last Updated**: June 2026  
**Author**: Project APE Team
