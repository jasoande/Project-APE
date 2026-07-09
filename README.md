<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="250"/>
  
  # Account Intelligence
  ### AI-Powered Enterprise Account Planning Engine
  
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Podman Compatible](https://img.shields.io/badge/podman-compatible-purple.svg)](https://podman.io/)
  
  **Automate days of account research into minutes using Google NotebookLM**
  
  [Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation) • [Support](#support)
</div>

---

## What is Account Intelligence?

Account Intelligence transforms enterprise account planning by automating research, analysis, and intelligence generation. Upload client documents or connect a Google Drive folder, and the AI conducts deep web research, imports external sources, and generates comprehensive account plans — reducing manual effort from days to minutes.

**Perfect for:**
- Sales Operations Teams
- Account Executives
- Customer Success Managers
- Partner Managers
- Business Development Teams

---

## ✨ Key Features

### 🚀 Zero-Configuration Launch
- **Double-click to start** — No terminal commands required
- **Web-based setup wizard** — NotebookLM auth, Drive integration, client config
- **Auto-installs dependencies** — Flask, notebooklm-py, pypdf, and more

### 📊 Real-Time Dashboard
- **Live progress tracking** with color-coded pipeline stages
- **Server-Sent Events (SSE)** log streaming
- **Stop/Resume workflows** with checkpoint recovery
- **Quality scoring** via Gemini AI (1.0-10.0 across 6 dimensions)

### ☁️ Google Drive Integration
- **Direct folder URL support** — Point to Drive folder, auto-download PDFs
- **7-day intelligent caching** — Skip redundant downloads
- **Auto-convert Docs/Sheets** to PDF automatically
- **50MB file size limit** with skip warnings

### ⚡ Multi-Client Parallel Processing
- **Process 5 clients simultaneously** in deep mode
- **Fast mode:** 15-20 minutes (10-25 external sources per query)
- **Deep mode:** 45-60 minutes (45-90 external sources, 8-9x coverage)
- **Anti-thundering-herd protection** to prevent API quota exhaustion

### 🔒 Enterprise Security
- **CSRF protection** on all POST endpoints
- **Path traversal prevention** with regex validation
- **No embedded secrets** — OAuth2 flow for all credentials
- **Non-root containers** — UID 1000 in Podman/Docker
- **Error sanitization** — Generic messages to users, full logs server-side

### 🐳 Containerized Deployment
- **Multi-arch support:** linux/amd64, linux/arm64
- **Podman/Docker compatible** with SELinux labels
- **Volume mounts** for credentials, logs, config
- **Registry:** quay.io/jasoande/project_ape/project-ape:latest

---

## 🎯 Quick Start

### Prerequisites

- **Python 3.11+** (check: `python3 --version`)
- **Google Chrome** (for NotebookLM OAuth login)
- **Google Account** with NotebookLM access
- **Google Drive** (optional, for folder-based document input)

### Installation (3 minutes)

**1. Clone the repository**

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
```

**2. Launch the application**

```bash
python3 launch-project-ape.py
```

This automatically:
- Creates a virtual environment at `~/.project-ape-venv`
- Installs all dependencies (Flask, notebooklm-py, pypdf, google-api-python-client, etc.)
- Starts the dashboard server
- Opens your browser to http://localhost:8765/configure

**3. Follow the setup wizard**

The web UI walks you through:
1. **NotebookLM Authentication** — One-click OAuth login (opens Chrome)
2. **Google Drive Setup** (optional) — Upload credentials.json, generate token
3. **Add Your First Client** — Name, Drive folder URL, industry, mode

**4. Launch your first workflow**

Click **"Launch Workflow"** and watch real-time progress in the dashboard.

---

## 📖 Documentation

### Getting Started
- **[Installation Guide](docs/getting-started/INSTALLATION.md)** — Detailed setup for macOS, Linux, Windows
- **[Quick Start Tutorial](docs/getting-started/QUICKSTART.md)** — 5-minute walkthrough
- **[First Workflow Guide](docs/getting-started/FIRST_WORKFLOW.md)** — End-to-end example

### User Guides
- **[Web UI Guide](docs/user-guide/WEB_UI.md)** — Dashboard and configuration wizard
- **[Google Drive Integration](docs/user-guide/DRIVE_INTEGRATION.md)** — Connect folders and manage files
- **[Running Workflows](docs/user-guide/WORKFLOWS.md)** — Fast vs Deep mode, parallel execution
- **[Understanding Results](docs/user-guide/RESULTS.md)** — Output formats, quality scores, next steps

### Administrator Guides
- **[Deployment Guide](docs/admin-guide/DEPLOYMENT.md)** — Container deployment (Podman/Docker)
- **[Authentication Setup](docs/admin-guide/AUTHENTICATION.md)** — NotebookLM + Drive OAuth
- **[Configuration Reference](docs/admin-guide/CONFIGURATION.md)** — Complete vars.py options
- **[Monitoring & Logs](docs/admin-guide/MONITORING.md)** — Health checks, metrics, debugging
- **[Troubleshooting](docs/admin-guide/TROUBLESHOOTING.md)** — Common issues and solutions

### Developer Guides
- **[Architecture Overview](docs/developer-guide/ARCHITECTURE.md)** — System design and components
- **[API Reference](docs/developer-guide/API_REFERENCE.md)** — Module and function docs
- **[Contributing](docs/developer-guide/CONTRIBUTING.md)** — How to contribute code
- **[Testing Guide](docs/developer-guide/TESTING.md)** — Running and writing tests
- **[Extending the Platform](docs/developer-guide/EXTENDING.md)** — Custom integrations

### Reference
- **[CLI Commands](docs/reference/CLI_COMMANDS.md)** — All command-line options
- **[Configuration Schema](docs/reference/CONFIGURATION.md)** — vars.py complete reference
- **[REST API Endpoints](docs/reference/API_ENDPOINTS.md)** — Dashboard API documentation
- **[Prompt Engineering](docs/reference/PROMPTS.md)** — Customizing research prompts

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (Port 8765)                  │
│              Dashboard UI + Configuration Wizard            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Flask Dashboard Server                     │
│    • Real-time SSE log streaming (200 threads)             │
│    • CSRF protection + rate limiting                        │
│    • Status file polling (2s refresh)                       │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Process Orchestrator (main.py)           │
│    • Spawns 1 process per client (max 5 parallel)          │
│    • Stagger delays to prevent API collisions              │
│    • Monitors health, handles signals                       │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           Client Pipeline Process (per client)              │
│  Phase 1: Download/consolidate PDFs from Drive             │
│  Phase 2: Create NotebookLM notebook + upload              │
│  Phase 3: Execute research queries (Ask prompts)           │
│  Phase 4: Run analysis prompts (Chat prompts)              │
│  Phase 5: Generate quality score via Gemini                │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services                         │
│  • Google NotebookLM API (via notebooklm CLI)              │
│  • Google Drive API v3 (OAuth2)                            │
│  • Gemini API (quality scoring)                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

- **`main.py`**: Multi-process orchestrator, spawns dashboard + client processes
- **`dashboard/server.py`**: Flask app with SSE streaming, 200-thread Waitress server
- **`core/client_pipeline.py`**: Single-client 5-phase pipeline executor
- **`core/drive_manager.py`**: Google Drive download with 7-day caching
- **`core/source_manager.py`**: NotebookLM source upload and research queries
- **`core/quality_scorer.py`**: Gemini-powered completeness validation

---

## 🛠️ Usage Examples

### Example 1: Single Client, Fast Mode (GUI)

1. Launch: `python3 launch-project-ape.py`
2. Add client: Name="Acme Corp", Drive URL="https://drive.google.com/...", Mode="Fast"
3. Click "Launch Workflow"
4. **Result:** 15-20 minutes, 20-50 external sources imported

### Example 2: Multiple Clients, Deep Mode (CLI)

```bash
# Create configuration file
cat > vars.py <<EOF
clients = ["client1", "client2", "client3"]

client1_name = "Acme Corp"
client1_folder = "https://drive.google.com/drive/folders/ABC123"
client1_industry = "technology"
client1_subsegments = "cloud, AI, enterprise software"

client2_name = "Beta Industries"
client2_folder = "https://drive.google.com/drive/folders/DEF456"
client2_industry = "manufacturing"
client2_subsegments = "automotive, supply chain, IoT"

client3_name = "Gamma Enterprises"
client3_folder = "https://drive.google.com/drive/folders/GHI789"
client3_industry = ""  # Auto-detect via Claude
client3_subsegments = ""
EOF

# Run workflow
python3 main.py --mode deep --clients client1 client2 client3
```

**Result:** 45-60 minutes, 135-270 external sources across 3 clients

### Example 3: Container Deployment

```bash
# Pull latest image
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Setup credentials volume
./setup-credentials.sh

# Run single client
./ape-run.sh --vars ./vars.py --clients example_client --mode fast

# View dashboard
open http://localhost:8765
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=core --cov=dashboard --cov-report=term-missing

# Run specific test suite
pytest tests/test_client_pipeline.py -v

# Skip slow integration tests
pytest tests/ -m "not slow and not integration"
```

**Test Coverage:**
- Unit tests: `test_retry_strategy.py`, `test_checkpoint_manager.py`, `test_health_checks.py`
- Integration tests: `test_client_pipeline.py`, `test_server_security.py`
- Functional tests: `test_webui_comprehensive.py`, `test_final_fixes.py`

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/developer-guide/CONTRIBUTING.md) for:

- Code of Conduct
- Development workflow (fork, branch, PR)
- Coding standards (PEP 8, type hints, docstrings)
- Testing requirements (pytest, 80%+ coverage)
- Documentation guidelines

**Quick Start for Contributors:**

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/Project-APE.git
cd Project-APE

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, add tests
pytest tests/ -v

# Commit and push
git add .
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Open Pull Request on GitHub
```

---

## 🔧 Troubleshooting

### "Authentication failed"

**Solution:** Run NotebookLM login in terminal with Chrome available:

```bash
notebooklm login
```

Or copy credentials from another machine:

```bash
scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/
```

### "Dashboard won't start"

**Solution:** Kill stale process and restart:

```bash
lsof -ti :8765 | xargs kill -9
python3 launch-project-ape.py
```

### "Too many retries / Quota exceeded"

**Solution:** Increase delays in vars.py for deep mode:

```python
DEEP_TIMINGS = {
    'ask_prompt_delay': (20.0, 30.0),  # Increase from (15.0, 25.0)
    'chat_prompt_delay': (12.0, 18.0),  # Increase from (10.0, 15.0)
}
```

**More help:** See [Troubleshooting Guide](docs/admin-guide/TROUBLESHOOTING.md)

---

## 📊 Performance & Scaling

### Benchmarks

| Scenario | Clients | Mode | Duration | Sources Imported | CPU (avg) | Memory (peak) |
|----------|---------|------|----------|------------------|-----------|---------------|
| Single client | 1 | Fast | 15-20 min | 20-50 | 15% | 250 MB |
| Single client | 1 | Deep | 45-60 min | 90-180 | 18% | 400 MB |
| Multi-client | 5 | Fast | 20-25 min | 100-250 | 35% | 800 MB |
| Multi-client | 5 | Deep | 50-65 min | 450-900 | 45% | 1.5 GB |

### Scaling Recommendations

- **1-3 clients:** Run on laptop (8GB RAM, 4 cores)
- **4-10 clients:** Run on server (16GB RAM, 8 cores)
- **10+ clients:** Deploy multiple containers, partition clients across instances

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Google NotebookLM** — AI research platform
- **notebooklm-py** — Python SDK by [author]
- **Flask** — Web framework
- **Waitress** — Production WSGI server
- **pypdf** — PDF manipulation

---

## 📬 Support

- **Issues:** https://github.com/jasoande/Project-APE/issues
- **Discussions:** https://github.com/jasoande/Project-APE/discussions
- **Email:** jason.anderson@redhat.com
- **Documentation:** [docs/](docs/)

---

## 🗺️ Roadmap

### Version 5.0 (Q3 2026)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Azure OpenAI integration (alternative to Gemini)
- [ ] Slack bot interface for workflow triggers
- [ ] PDF export of final account plans
- [ ] Custom prompt template library

### Version 4.2 (Q2 2026)
- [x] Dashboard SSE thread exhaustion fix
- [x] Wizard banner dismissal with localStorage
- [x] Real-time Drive URL validation
- [x] Visual pipeline stages
- [ ] Notebook deduplication by similarity
- [ ] Automatic industry detection via Claude

### Version 4.1 (Released)
- [x] Security hardening (CSRF, path traversal prevention)
- [x] Checkpoint/resume for crash recovery
- [x] Pre-flight health checks
- [x] Workflow stop button
- [x] Gemini quality scorer integration

---

<div align="center">
  
  **Built with ❤️ by the Account Intelligence Team**
  
  King Kong in a Red Fedora — Crushing complexity since 2026
  
  [⬆ Back to Top](#account-intelligence)
</div>
