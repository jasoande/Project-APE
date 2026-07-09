<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Account Intelligence - Account Planning Engine" width="200"/>
  
  # Account Intelligence
  **Account Planning Engine**
  
  AI-Powered Enterprise Account Planning Automation
</div>

---

## Overview

Account Intelligence automates enterprise account research using Google's NotebookLM platform. Upload client PDFs (or point to a Google Drive folder), and the engine conducts AI-driven web research, imports external sources, and generates comprehensive account intelligence -- reducing days of manual work to minutes.

## Features

- **Web-based configuration wizard** -- zero terminal required, double-click to launch
- **Google Drive integration** with 7-day intelligent caching and auto-conversion of Docs/Sheets to PDF
- **Multi-client parallel execution** -- process up to 5 clients simultaneously
- **Fast mode** (15-20 min) and **Deep mode** (45-60 min, 8-9x more sources)
- **Real-time dashboard** with SSE log streaming, progress bars, and live status updates
- **Pipeline checkpoint and resume** for crash recovery
- **Pre-flight health checks** before workflow launch
- **Stop/cancel workflow** button for in-progress runs
- **Webhook notifications** on completion (Slack, Teams, etc.)
- **Quality scoring** via Gemini AI across 6 analysis dimensions (1.0-10.0 scale)
- **CSRF protection** and path traversal prevention
- **Containerized deployment** via Podman or Docker (linux/amd64, linux/arm64)

## Quick Start

**1. Install and launch**

```bash
python3 launch-project-ape.py
```

On first run this automatically creates a virtual environment, installs all dependencies (Flask, notebooklm-py, pypdf, etc.), and starts the dashboard server.

**2. Configure**

Your browser opens to http://localhost:8765/configure where a 3-step wizard walks you through NotebookLM authentication, Google Drive OAuth setup, and adding your first client.

**3. Launch**

Click **"Launch Workflow"** and watch real-time progress in the dashboard.

## Architecture

Account Intelligence uses a multi-process orchestration architecture:

- **Orchestrator** (`main.py`) -- spawns independent client pipeline processes, manages lifecycle and status tracking
- **Dashboard** (`dashboard/server.py`) -- Flask app served via Waitress WSGI, provides real-time monitoring with SSE, configuration wizard, and REST API
- **Client Pipeline** (`core/client_pipeline.py`) -- executes the 5-phase workflow per client in an isolated process

### Pipeline Phases

```
Phase 1: PDF Download & Consolidation .... 30-60s
Phase 2: Notebook Creation ............... 10-15s
Phase 3: Research (Ask Prompts) .......... 3-8 min
Phase 4: Analysis (Chat Prompts) ......... 8-12 min
Phase 5: Quality Validation .............. 1-2 min
```

### Core Modules

| Module | Responsibility |
|--------|---------------|
| `core/retry_strategy.py` | Exponential backoff with configurable attempts |
| `core/checkpoint_manager.py` | Pipeline state persistence for crash recovery |
| `core/health_checks.py` | Pre-flight validation of auth, connectivity, config |
| `core/notification_manager.py` | Webhook delivery on workflow completion |
| `core/drive_manager.py` | Google Drive API v3 with intelligent caching |
| `core/quality_scorer.py` | Gemini-powered completeness scoring |
| `core/source_manager.py` | NotebookLM source and research query management |
| `core/notebook_manager.py` | Notebook lifecycle and deduplication |

## Configuration

### Web UI (Recommended)

Launch the dashboard and navigate to http://localhost:8765/configure. The form lets you add clients with a name, Google Drive folder URL, industry, subsegments, and execution mode. Configuration is saved to `vars.py` automatically.

### Manual (`vars.py`)

Start from the provided templates (`example-container.py` or `container-vars.py`) and define per-client attributes:

```python
clients = ["acme"]

acme_name = "Acme Corporation"
acme_folder = "https://drive.google.com/drive/folders/1A2B3C..."
acme_industry = "technology"
acme_subsegments = "cloud, AI, enterprise software"

persona = "Red Hat solutions architect"
MODE = "fast"
```

See [WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) and [CONFIGURATION_BEST_PRACTICES.md](Docs/CONFIGURATION_BEST_PRACTICES.md) for full reference.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=core --cov=dashboard
```

## Container Deployment

```bash
# Build
podman build -t project-ape:latest -f Containerfile.debian .

# Run
podman run -d \
  -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./client_data:/app/client_data:ro,z \
  -v ./docs_generated:/app/docs_generated:z \
  -v ./logs:/app/logs:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  project-ape:latest

# Pull from registry
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

See [DEPLOYMENT_GUIDE.md](Docs/DEPLOYMENT_GUIDE.md) for full container setup including multi-arch builds and credential volume configuration.

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](Docs/INSTALLATION.md) | Platform-specific installation guides |
| [USER_GUIDE.md](Docs/USER_GUIDE.md) | Workflow execution and best practices |
| [WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) | Web UI configuration reference |
| [ARCHITECTURE.md](Docs/ARCHITECTURE.md) | Technical architecture deep-dive |
| [API_REFERENCE.md](Docs/API_REFERENCE.md) | REST API and internal module reference |
| [DEPLOYMENT_GUIDE.md](Docs/DEPLOYMENT_GUIDE.md) | Container deployment and registry setup |
| [SECURITY_GUIDE.md](Docs/SECURITY_GUIDE.md) | Security model and hardening |
| [PERFORMANCE_GUIDE.md](Docs/PERFORMANCE_GUIDE.md) | Tuning and optimization |
| [OPERATIONS_RUNBOOK.md](Docs/OPERATIONS_RUNBOOK.md) | Operational procedures and monitoring |
| [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [FAQ.md](Docs/FAQ.md) | Frequently asked questions |
| [CONFIGURATION_BEST_PRACTICES.md](Docs/CONFIGURATION_BEST_PRACTICES.md) | Configuration patterns and tips |
| [INTEGRATION_GUIDE.md](Docs/INTEGRATION_GUIDE.md) | Third-party integrations (webhooks, CI/CD) |

## License

Copyright 2026 Jason Anderson. All rights reserved.
