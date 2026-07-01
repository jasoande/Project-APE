<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="200"/>
  
  # Project APE - Account Planning Engine
  
  **AI-Powered Enterprise Account Research Automation**
  
  [![Version](https://img.shields.io/badge/version-4.0.1-blue.svg)](https://github.com/yourusername/project-ape)
  [![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
  [![Container](https://img.shields.io/badge/container-podman%20%7C%20docker-blueviolet.svg)](https://quay.io/repository/jasoande/project_ape/project-ape)
</div>

---

## Overview

Project APE (Account Planning Engine) transforms enterprise account research from a manual, time-intensive process into an automated, AI-driven workflow. Leveraging Google NotebookLM's advanced research capabilities, Project APE generates comprehensive account intelligence in minutes, not days.

### What It Does

- **Automated Research**: Processes client documents and conducts deep web research
- **Industry Analysis**: AI-powered industry detection and competitive landscape mapping
- **Intelligence Generation**: Creates structured account plans with actionable insights
- **Quality Validation**: Automated scoring and validation of research outputs
- **Real-Time Monitoring**: Web dashboard with live progress tracking

### Who It's For

- **Sales Teams** preparing for enterprise account meetings
- **Solutions Architects** developing technical account strategies
- **Account Executives** building strategic engagement plans
- **Business Development** teams researching new prospects

---

## Key Features

### Core Capabilities

- **Multi-Client Parallel Processing**: Process up to 5 accounts simultaneously
- **Dual Execution Modes**: 
  - Fast mode: 15-20 minutes per account
  - Deep mode: 45-60 minutes with 8-9x more sources
- **Google Drive Integration**: Automatic document download and synchronization
- **NotebookLM Orchestration**: Leverages Google's AI research platform
- **Quality Scoring**: Automated 1-10 scale validation of research outputs
- **Smart Caching**: 7-day Drive cache with selective refresh

### Dashboard Features

- Real-time progress tracking per client
- Live log streaming with pause/resume
- Quality score visualization
- Direct NotebookLM links
- Execution metrics and timing
- Auto-refresh every 2 seconds

### Container Support

- Multi-architecture: linux/amd64, linux/arm64
- Non-root container execution
- Volume-based credential management
- Registry: `quay.io/jasoande/project_ape/project-ape`

---

## Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.11+ recommended)
- **Chrome browser** (for NotebookLM authentication)
- **Google Account** with access to:
  - Google Drive
  - Google NotebookLM (free at notebooklm.google.com)
- **Podman or Docker** (for containerized execution)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/project-ape.git
cd project-ape
```

2. **Authenticate with NotebookLM**

```bash
# Install NotebookLM CLI
pip install notebooklm

# Login (opens Chrome browser)
notebooklm login
```

3. **Setup Google Drive OAuth**

```bash
# Run OAuth setup wizard
python3 setup-oauth-drive-improved.py

# Follow prompts to:
# - Create Google Cloud project (or select existing)
# - Enable Drive API
# - Create OAuth credentials
# - Download and configure credentials
# - Complete authentication flow
```

4. **Configure your clients**

```bash
# Copy example configuration
cp developer-docs/example-vars.py vars.py

# Edit with your client details
vi vars.py
```

Example configuration:

```python
clients = ["acme_corp"]

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
acme_corp_industry = ""  # Auto-detect
acme_corp_subsegments = ""

persona = "solutions architect"
default_mode = "fast"
```

5. **Launch the workflow**

```bash
# Fast mode (15-20 minutes)
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast

# Deep mode (45-60 minutes)
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode deep
```

6. **Monitor progress**

Open the dashboard at: `http://localhost:8765`

---

## Usage

### Running Workflows

**Single Client:**

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast
```

**Multiple Clients (Parallel):**

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp,techstart_inc,globalbank --mode fast
```

**Force Cache Refresh:**

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast --refresh
```

### Execution Modes

| Mode | Duration | Sources | Use Case |
|------|----------|---------|----------|
| **Fast** | 15-20 min | 20-50 | Quick account overviews |
| **Deep** | 45-60 min | 90-180 | Comprehensive analysis for high-value accounts |

Both modes process all configured clients in parallel.

### Dashboard

The web dashboard provides real-time monitoring at `http://localhost:8765`:

- **Header**: Overall progress, execution timer, client counts
- **Client Cards**: Individual progress, quality scores, NotebookLM links
- **Logs Section**: Real-time log streaming with controls
- **Auto-Refresh**: Updates every 2 seconds

### Output Structure

```
docs_generated/
├── acme_corp/
│   ├── Acme_Corporation_Account_Plan.pdf
│   ├── Research_Summary.txt
│   ├── Quality_Score.json
│   └── NotebookLM_Link.txt
└── ...
```

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Project APE Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Interface Layer                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Web Dashboard (Flask)                                │  │
│  │  - Real-time progress                                 │  │
│  │  - Live logs                                          │  │
│  │  - Quality scores                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  Orchestration Layer                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py (Multi-Process Manager)                      │  │
│  │  - Process spawning                                   │  │
│  │  - Status aggregation                                 │  │
│  │  - Resource management                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  Execution Layer (Parallel Processes)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │  │
│  │ Pipeline │  │ Pipeline │  │ Pipeline │  │ Pipeline │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       ↓              ↓              ↓              ↓        │
│  Core Components Layer                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • DriveManager (Download files)                      │  │
│  │  • NotebookManager (NotebookLM API)                   │  │
│  │  • SourceManager (Upload & process)                   │  │
│  │  • GeminiAgent (AI orchestration)                     │  │
│  │  • QualityScorer (Result validation)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  External Services                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Google Drive API                                   │  │
│  │  • Google NotebookLM                                  │  │
│  │  • Google Gemini API (optional)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Workflow

Each client executes through five sequential phases:

1. **Document Download** (30-60 seconds)
   - Connects to Google Drive via OAuth
   - Downloads PDFs and documents from client folder
   - Converts Google Docs to PDF
   - Implements smart caching (7-day TTL)

2. **Notebook Creation** (10-15 seconds)
   - Creates NotebookLM notebook
   - Uploads consolidated sources
   - Waits for source processing

3. **Research Phase** (3-8 minutes)
   - Executes AI-powered research queries
   - Imports 20-180 external sources (mode-dependent)
   - Analyzes industry trends and competitive landscape

4. **Analysis Phase** (8-12 minutes)
   - Runs 6 consolidated analysis prompts
   - Generates strategic insights
   - Identifies opportunities and risks

5. **Quality Validation** (1-2 minutes)
   - Validates source count and completeness
   - Generates 1-10 quality score
   - Creates summary outputs

---

## Configuration

### Client Configuration (vars.py)

```python
# Client list
clients = ["acme_corp", "techstart_inc"]

# Client 1 configuration
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/ABC123XYZ"
acme_corp_industry = ""  # Leave empty for auto-detection
acme_corp_subsegments = "cloud, AI/ML, enterprise software"

# Client 2 configuration
techstart_inc_name = "TechStart Inc"
techstart_inc_folder = "https://drive.google.com/drive/folders/DEF456UVW"
techstart_inc_industry = "technology"
techstart_inc_subsegments = ""

# Global settings
persona = "solutions architect"
default_mode = "fast"
DASHBOARD_PORT = 8765
```

### Timing Configuration

**Fast Mode** (optimized for speed):

```python
TIMINGS = {
    'ask_prompt_delay': (8.0, 12.0),      # Research query delays
    'chat_prompt_delay': (5.0, 8.0),      # Analysis prompt delays
    'source_processing_wait': 30,          # Source upload wait
}
```

**Deep Mode** (optimized for coverage):

```python
DEEP_TIMINGS = {
    'ask_prompt_delay': (15.0, 25.0),     # Longer delays for more sources
    'chat_prompt_delay': (10.0, 15.0),    # Conservative timing
    'source_processing_wait': 45,          # Extended wait
}
```

---

## Container Deployment

### Building Containers

```bash
# Build for current architecture
podman build -t project-ape:latest -f Containerfile.debian .

# Build multi-architecture (requires buildx)
podman build --platform linux/amd64,linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:4.0.1 \
  -f Containerfile.debian .
```

### Running Containers

```bash
# Run with ape-run.sh (recommended)
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast

# Manual container run
podman run -it --rm \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:z \
  -v ./docs_generated:/app/docs_generated:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -p 8765:8765 \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients acme_corp --mode fast
```

### Registry

Official images: `quay.io/jasoande/project_ape/project-ape`

- `latest` - Latest stable release
- `4.0.1` - Specific version tag
- `4.0` - Minor version tag

---

## Documentation

- **[Installation Guide](Docs/INSTALLATION.md)** - Detailed setup instructions
- **[User Guide](Docs/USER_GUIDE.md)** - Complete usage documentation
- **[Architecture](Docs/ARCHITECTURE.md)** - Technical architecture details
- **[Deployment Guide](developer-docs/DEPLOYMENT.md)** - Container deployment
- **[Troubleshooting](Docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## Troubleshooting

### Common Issues

**NotebookLM Authentication Failed**

```bash
# Re-authenticate
notebooklm login

# Verify credentials
ls -la ~/.notebooklm/credentials.json
```

**Google Drive Access Denied**

```bash
# Re-run OAuth setup
python3 setup-oauth-drive-improved.py

# Delete old token
rm ~/.project-ape/token.json
```

**Container Won't Start**

```bash
# Check credentials volume
podman volume exists project-ape-credentials

# Recreate volume
podman volume rm project-ape-credentials
./setup-credentials.sh
```

**Dashboard Not Accessible**

```bash
# Verify port 8765 is not in use
lsof -i :8765

# Check container logs
podman logs -f <container-name>
```

For comprehensive troubleshooting, see **[Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)**

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Create virtual environment
python3 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate

# Install dependencies
pip install -r developer-docs/requirements.txt
```

### Running Tests

```bash
# Single client test
./developer-docs/ape-run.sh --vars ./developer-docs/example-vars.py --clients example_client --mode fast

# Verify outputs
ls -la docs_generated/example_client/
cat logs/example_client.log
```

### Code Structure

```
project-ape/
├── core/                     # Core pipeline components
│   ├── client_pipeline.py    # Single client workflow
│   ├── drive_manager.py      # Google Drive integration
│   ├── notebook_manager.py   # NotebookLM API wrapper
│   ├── source_manager.py     # Source upload manager
│   └── quality_scorer.py     # Result validation
│
├── dashboard/                # Web interface
│   ├── server.py             # Flask application
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, images
│
├── developer-docs/           # Development documentation
│   ├── ape-run.sh            # Container launcher
│   ├── requirements.txt      # Python dependencies
│   └── example-vars.py       # Configuration template
│
└── Docs/                     # User documentation
    ├── INSTALLATION.md
    ├── USER_GUIDE.md
    └── TROUBLESHOOTING.md
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, no jQuery
- **Shell**: ShellCheck compliant
- **Documentation**: Markdown, clear examples

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Google NotebookLM** team for the AI research platform
- **Google Gemini** team for AI orchestration capabilities
- **Open Source Community** for dependencies and tools

---

## Support

- **Documentation**: [Docs/](Docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/project-ape/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/project-ape/discussions)

---

**Version**: 4.0.1  
**Last Updated**: June 30, 2026  
**Author**: Jason Anderson

---

## Quick Reference

```bash
# Initial Setup
notebooklm login
python3 setup-oauth-drive-improved.py
cp developer-docs/example-vars.py vars.py

# Run Workflow
./developer-docs/ape-run.sh --vars ./vars.py --clients yourclient --mode fast

# Monitor
# → Dashboard: http://localhost:8765

# Container Operations
podman build -t project-ape:latest -f Containerfile.debian .
podman push quay.io/jasoande/project_ape/project-ape:4.0.1

# Troubleshooting
tail -f logs/overall.log
cat .multi_process_status/yourclient.json
```

---

<div align="center">
  <strong>Built with AI. Powered by NotebookLM.</strong>
</div>
