# Project APE - Account Planning Engine

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="200"/>
</p>

<h3 align="center">AI-Powered Enterprise Account Planning Automation</h3>

<p align="center">
  <strong>Version 3.0.4</strong> | <strong>Containerized Edition</strong><br>
  Project Owner & Maintainer: <strong>Jason Anderson</strong>
</p>

---

## 🎯 Overview

Project APE revolutionizes enterprise account planning by automating research, analysis, and intelligence generation. Leveraging Google's NotebookLM AI platform, Project APE transforms hours of manual research into 15-20 minutes of automated analysis.

### What Problem Does It Solve?

**Traditional Account Planning:**
- ⏱️ **4-6 hours** of manual research per account
- 📚 Reviewing dozens of documents manually
- 🔍 Searching for industry trends and competitive intelligence
- 📝 Compiling findings into coherent reports
- 🤔 Risk of missing critical insights

**With Project APE:**
- ⚡ **10-12 minutes** fully automated (Fast mode)
- 🔬 **30-35 minutes** for deep research (Deep mode, 8-9x more sources)
- 🤖 AI analyzes all documents simultaneously
- 🌐 Automated web research for industry context
- 📊 Structured, consistent output every time
- 🎯 Comprehensive coverage with zero oversight

---

## 🚀 Quick Start

### Prerequisites

- Git
- Google Chrome (for NotebookLM authentication)

All other dependencies (Podman, Node.js, NotebookLM CLI) can be installed via the setup script.

### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
git checkout QA
```

### Step 2: Run Environment Setup (One-Time)

```bash
./setup-environment.sh
```

This interactive script installs:
- ✅ Podman (container runtime)
- ✅ Node.js 20+ (required for NotebookLM CLI)
- ✅ NotebookLM CLI (notebooklm)
- ✅ Python dependencies (for container builds)
- ✅ NotebookLM authentication

### Step 3: Set Up Container Credentials

```bash
./setup-credentials.sh
```

### Step 4: Pull Container Image

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

### Step 5: Configure Client

```bash
# Create client data directory
mkdir -p client_data/YourClient
cp /path/to/documents/* client_data/YourClient/

# Create configuration
cp example-container.py vars.py
nano vars.py  # Edit with your client details
```

### Step 6: Run

```bash
# Fast mode (10-12 minutes)
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast

# Deep mode (30-35 minutes)
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep
```

### Step 7: Monitor

**Dashboard:** http://localhost:8765  
**Logs:** `tail -f logs/yourclient.log`

---

## ✨ Key Features

### 🎯 **AI-Powered Analysis**
- Automated industry research
- Competitive intelligence gathering  
- Pain point identification
- Opportunity mapping
- Stakeholder analysis

### ⚡ **Two Execution Modes**

| Feature | Fast Mode | Deep Mode |
|---------|-----------|-----------|
| Duration | 15-20 min | 30-45 min |
| Research Depth | ~20 sources | ~50+ sources |
| Best For | Quick prep | Strategic planning |

### 📊 **Real-Time Dashboard**
- Live progress tracking
- Multi-client monitoring
- Log streaming
- Status indicators
- Execution metrics

### 📦 **Containerized Deployment**
- ✅ Zero dependency installation
- ✅ Consistent execution environment
- ✅ Cross-platform (macOS, Linux, Windows WSL)
- ✅ Registry distribution ready
- ✅ 808 MB optimized image

### 🔄 **Parallel Processing**
- Run multiple clients simultaneously
- Independent workflows
- Efficient resource utilization
- Up to 5 clients in parallel

---

## 🏗️ How It Works

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       PROJECT APE                             │
│                   Container (808 MB)                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐     │
│  │    Flask     │  │    Client     │  │  NotebookLM  │     │
│  │  Dashboard   │  │   Pipeline    │  │  Python SDK  │     │
│  │   :8765      │  │   Manager     │  │   (0.7.1)    │     │
│  └──────────────┘  └───────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐     │
│  │     PDF      │  │    Source     │  │     Auth     │     │
│  │ Consolidator │  │   Manager     │  │   Manager    │     │
│  └──────────────┘  └───────────────┘  └──────────────┘     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    Host Volumes         NotebookLM API       Google OAuth
  (read-only mounts)   (AI Research Engine)  (Authentication)
```

### Workflow Phases

#### Phase 1: PDF Consolidation (30 seconds)
```
1. Scan client data directory
2. Merge all PDFs into single document
3. Add metadata and table of contents
4. Optimize for upload
```

#### Phase 2: Notebook Creation (10 seconds)
```
1. Create NotebookLM notebook
2. Upload consolidated PDF
3. Initialize AI context
4. Verify source processing
```

#### Phase 3: Research (3-5 minutes)
```
1. Execute 2 research prompts:
   - Industry analysis
   - Competitive landscape
2. AI conducts web research
3. Import 10-25 external sources per prompt
4. Build comprehensive knowledge base
```

#### Phase 4: Chat Analysis (8-12 minutes)
```
Execute 12 structured analysis prompts:
1. Industry overview
2. Key challenges
3. Technology trends
4. Competitive positioning
5. Pain points
6. Opportunity areas
7. Decision makers
8. Buying process
9. Value proposition
10. Success metrics
11. Risk factors
12. Strategic recommendations
```

#### Phase 5: Mind Map Generation (1-2 minutes)
```
1. Request visual mind map
2. Download generated content
3. Save to docs_generated/
4. Create summary document
```

---

## 📋 Configuration

### Basic Configuration (vars.py)

**Configuration Templates:**
- `example-container.py` - Single client template (recommended starting point)
- `example-multi-client-vars.py` - Multiple clients template (for batch processing)

```python
# Project APE - Container Configuration
# Use example-container.py as your starting template

from pathlib import Path

# ============================================================
# PERSONA CONFIGURATION
# ============================================================

# Define the role/perspective for AI-generated content
# Customize based on your department and use case:
persona = "Red Hat solutions architect"

# Other persona examples:
#   - "Red Hat account executive" (sales focus)
#   - "Red Hat marketing specialist" (campaigns/messaging)
#   - "Red Hat customer success manager" (post-sale)
#   - "senior industry analyst" (research focus)

# ============================================================
# CLIENT CONFIGURATION
# ============================================================

clients = ["example_client"]

# Example Client Configuration
example_client_name = "Example Corporation"
example_client_industry = "technology"
example_client_subsegments = "cloud computing, enterprise software, cybersecurity"
example_client_folder = "/app/client_data/Example_Corporation"

# ============================================================
# WORKFLOW SETTINGS
# ============================================================

MODE = "fast"  # "fast" or "deep"
ENABLE_DASHBOARD = True
DASHBOARD_PORT = 8765

# ============================================================
# PATHS (Auto-configured for containers)
# ============================================================

STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs_generated"
```

### Industry Subsegments

Subsegments help AI provide more targeted research:

```python
# Technology & Software
"cloud services, SaaS platforms, cybersecurity, AI/ML, DevOps"

# Financial Services
"banking, insurance, wealth management, fintech, payments"

# Healthcare
"hospitals, pharmaceuticals, medical devices, health IT, telehealth"

# Manufacturing
"automotive, aerospace, electronics, supply chain, IoT"

# Retail
"e-commerce, omnichannel, supply chain, customer experience"

# Energy
"oil and gas, renewables, utilities, smart grid, energy storage"
```

---

## 📁 Directory Structure

```
Project-APE/
├── 📄 README.md                    # This file
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # Contribution guidelines
│
├── 🐳 Containerfile.debian         # Container build definition
├── 📜 container-entrypoint.sh      # Container startup script
├── 🔧 ape-run.sh                   # Container runner script
├── 📋 requirements.txt             # Python dependencies
│
├── 🔧 container-vars.py            # Configuration template
├── 📝 example-vars.py              # Example configuration
│
├── 🐍 main.py                      # Application entry point
│
├── 📦 core/                        # Core application modules
│   ├── auth_manager.py             # NotebookLM authentication
│   ├── client_pipeline.py          # Workflow orchestration
│   ├── notebook_manager.py         # NotebookLM API wrapper
│   ├── source_manager.py           # Document & research management
│   ├── pdf_consolidator_fast.py   # PDF processing (fast mode)
│   └── pdf_consolidator_deep.py   # PDF processing (deep mode)
│
├── 🌐 dashboard/                   # Web dashboard
│   ├── server.py                   # Flask application
│   ├── templates/                  # HTML templates
│   │   └── dashboard.html
│   └── static/                     # Static assets
│       ├── kingkong.png            # Project APE logo
│       ├── style.css
│       └── script.js
│
├── 📝 Prompts/                     # AI prompts
│   ├── ask_prompt_01.txt           # Industry research
│   ├── ask_prompt_02.txt           # Competitive analysis
│   ├── chat_prompt_01.txt          # Industry overview
│   ├── chat_prompt_02.txt          # Key challenges
│   └── ... (12 total chat prompts)
│
└── 📚 docs/                        # Documentation
    ├── ARCHITECTURE.md             # Technical architecture
    ├── API.md                      # API reference
    ├── TROUBLESHOOTING.md          # Common issues
    ├── CONTAINER_GUIDE.md          # Container guide
    └── DEPLOYMENT.md               # Deployment guide
```

---

## 🎯 Use Cases

### 1. Pre-Call Research
**Scenario:** Meeting with Fortune 500 CIO tomorrow  
**Action:** Run Project APE on available documents  
**Result:** Comprehensive brief on their technology stack, challenges, and strategic initiatives

### 2. Territory Planning
**Scenario:** New accounts assigned, need quick assessment  
**Action:** Batch process all accounts overnight  
**Result:** Complete account profiles for strategic prioritization

### 3. Competitive Analysis
**Scenario:** Competitor making moves in your accounts  
**Action:** Deep mode analysis on market dynamics  
**Result:** Competitive positioning and differentiation strategies

### 4. Quarterly Business Reviews
**Scenario:** Preparing QBR presentations  
**Action:** Refresh account intelligence with latest data  
**Result:** Data-driven insights and recommendations

---

## 🔧 Technical Specifications

### Container Details

| Specification | Value |
|--------------|-------|
| Base Image | python:3.13-slim (Debian) |
| Image Size | 808 MB |
| Build Time | ~4 minutes |
| Platforms | linux/arm64, linux/amd64 |
| User | apeuser (UID 1000, non-root) |
| Exposed Ports | 8765 (dashboard) |

### Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13 | Runtime |
| notebooklm-py | 0.7.1 | NotebookLM SDK |
| Flask | 3.1.3 | Web dashboard |
| pypdf | 6.13.2 | PDF reading |
| reportlab | 4.5.1 | PDF generation |
| Pillow | 12.2.0 | Image processing |

### Performance Metrics

| Metric | Fast Mode | Deep Mode |
|--------|-----------|-----------|
| Single Client | ~10-12 min | ~25-30 min |
| 6 Clients Parallel | ~10-12 min | ~30-35 min |
| Research Sources | ~20 | ~90-180 |
| Chat Prompts | 6 (consolidated) | 6 (consolidated) |
| Quality Score | 5-6/10 | 8-9/10 |
| Use Case | Daily operations | High-volume, max depth |
| Retry Rate | <5% | ~30% (acceptable) |

---

## 🔒 Security & Privacy

### Security Features

✅ **Non-root Execution** - Container runs as unprivileged user (apeuser, UID 1000)  
✅ **Read-Only Mounts** - Configuration and client data mounted read-only  
✅ **Credential Isolation** - NotebookLM credentials copied, never shared  
✅ **No Data Persistence** - Container ephemeral, dies after execution  
✅ **SELinux Compatible** - Full support for RHEL/Fedora/CentOS  
✅ **Network Isolation** - Only dashboard port exposed  

### Privacy Considerations

- Client data stays in your environment
- NotebookLM processes data in Google Cloud (per Google's privacy policy)
- No data retention after workflow completion
- Container logs contain client names but no sensitive content
- Generated documents stored locally only

---

## 📊 Monitoring & Observability

### Dashboard

Access: **http://localhost:8765**

Features:
- Real-time progress tracking
- Client status indicators
- Live log streaming
- Execution metrics
- Multi-client overview

### Logs

```bash
# Follow logs for specific client
tail -f logs/clientname.log

# Monitor all logs
tail -f logs/*.log

# Container logs
podman logs -f <container-name>

# Search logs
grep "ERROR" logs/*.log
```

### Status Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 RUNNING | Workflow in progress | Monitor dashboard |
| 🟢 COMPLETE | Successfully finished | Review output |
| 🟡 PENDING | Queued for execution | Wait for start |
| 🔴 FAILED | Error occurred | Check logs |
| 🟠 DEGRADED | Partial completion | Review logs |

---

## 🆘 Troubleshooting

### Common Issues

#### ❌ Authentication Failed

```bash
# Re-authenticate
notebooklm login

# Or copy credentials from another machine
scp ~/.notebooklm/credentials.json user@remote-host:~/.notebooklm/

# Verify credentials exist
ls -la ~/.notebooklm/credentials.json

# Check permissions
chmod -R 700 ~/.notebooklm
```

#### ❌ Container Won't Start

```bash
# Stop all Project APE containers
podman stop $(podman ps -aq --filter ancestor=project-ape)

# Clean up resources
podman system prune -f

# Retry
./ape-run.sh --mode fast --clients yourclient
```

#### ❌ Dashboard Not Accessible

```bash
# Verify container running
podman ps | grep project-ape

# Check port mapping
podman port <container-name>

# Test connectivity
curl http://localhost:8765/status

# Access from browser
open http://localhost:8765
```

#### ❌ PDF Consolidation Fails

```bash
# Check file permissions
ls -la client_data/YourClient/

# Verify PDF files
file client_data/YourClient/*.pdf

# Check size (max 50MB total)
du -sh client_data/YourClient/
```

#### ❌ Research Timeout

```bash
# Normal for large accounts - wait longer
# Or switch to deep mode for better handling
./ape-run.sh --mode deep --clients largeclient
```

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for comprehensive troubleshooting.

---

## 📚 Documentation

### Getting Started
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide (RHEL 8/9/10 & macOS)
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configuration reference

### Advanced Usage
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture
- **[docs/API.md](docs/API.md)** - API reference
- **[docs/WORKFLOWS.md](docs/WORKFLOWS.md)** - Workflow deep dive
- **[docs/PROMPTS.md](docs/PROMPTS.md)** - Prompt engineering guide

### Operations
- **[docs/CONTAINER_GUIDE.md](docs/CONTAINER_GUIDE.md)** - Container operations
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment strategies
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Problem resolution
- **[docs/FAQ.md](docs/FAQ.md)** - Frequently asked questions

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide

---

## 🤝 Support

**Project Owner & Maintainer:** Jason Anderson

### Getting Help

1. **Check Documentation** - See docs/ directory
2. **Review Logs** - Check logs/*.log files
3. **Search Issues** - Review common troubleshooting
4. **Contact Maintainer** - Reach out to Jason Anderson

### Reporting Issues

When reporting issues, include:
- Project APE version
- Container image tag
- Operating system
- Error messages from logs
- Steps to reproduce
- vars.py configuration (sanitized)

---

## 📜 License

**Internal Red Hat Use Only**

This software is proprietary to Red Hat, Inc. and is intended for internal use by Red Hat account teams only. Unauthorized distribution, modification, or use outside of Red Hat is prohibited.

---

## 🙏 Acknowledgments

- **NotebookLM Team** - Google's AI research platform
- **Red Hat Account Teams** - Valuable feedback and testing
- **Python Community** - Excellent open source ecosystem
- **Container Community** - Podman and container technologies

---

## 📈 Roadmap

### Version 3.1 (Planned)
- Multi-language support
- Enhanced mind map customization
- Slack integration for notifications
- Batch export to PowerPoint

### Version 3.2 (Planned)
- CRM integration (Salesforce)
- Custom prompt templates
- Advanced analytics dashboard
- Historical trend analysis

---

## 🎓 Best Practices

### Preparation
1. **Organize client data** - Use consistent folder structure
2. **Quality over quantity** - Relevant documents yield better results
3. **Update regularly** - Fresh data produces fresh insights
4. **Name consistently** - Use standard client naming conventions

### Execution
1. **Start with fast mode** - Quick initial assessment
2. **Use deep mode strategically** - For strategic accounts
3. **Batch similar clients** - Process accounts in parallel
4. **Monitor progress** - Watch dashboard for issues

### Post-Processing
1. **Review generated content** - Validate AI insights
2. **Customize for audience** - Adapt output for stakeholders
3. **Archive results** - Save for future reference
4. **Share learnings** - Distribute to team members

---

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE" width="100"/>
</p>

<h3 align="center">Project APE - Automating Account Planning Excellence</h3>

<p align="center">
  <strong>Version 3.0.1 (Containerized Edition)</strong><br>
  Maintained by Jason Anderson | 2026
</p>

---

**Questions?** Check the [documentation](docs/) or contact Jason Anderson.
