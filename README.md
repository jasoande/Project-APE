# Project APE - Account Planning Engine

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="400"/>
</p>

<p align="center">
  <strong>AI-Powered Enterprise Account Planning Automation</strong><br>
  Created, Developed, and Maintained by <strong>Jason Anderson</strong>
</p>

<p align="center">
  <strong>Version 3.0.4</strong> | Powered by Claude AI & NotebookLM
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a>
</p>

---

## Overview

Project APE (Account Planning Engine) is an enterprise-grade automation system that leverages **Google NotebookLM** and **Claude AI** to generate comprehensive account planning research and analysis for enterprise clients.

### What It Does

- **Automates Company Research:** Uses NotebookLM's deep research capabilities to gather intelligence
- **Generates Comprehensive Plans:** Creates industry analysis, technical assessments, and strategic recommendations
- **Parallel Processing:** Handles multiple clients simultaneously with real-time monitoring
- **Complete NotebookLM Notebooks:** Produces 40+ sources, 6 detailed notes, and interactive mind maps per client

### Built For

Sales engineers, solutions architects, account managers, and business development professionals who need deep, accurate account intelligence quickly.

---

## Features

###  🤖 Claude AI Orchestration

- Intelligent pipeline monitoring and error recovery
- Self-healing capabilities for common failures
- Quality validation ensuring >8.5/10 output scores
- Automated artifact verification

### 📚 NotebookLM Integration

- Deep research with automatic source discovery
- PDF consolidation of company materials
- Google Drive integration for document retrieval
- Intelligent deduplication of sources

### 🚀 Multi-Client Parallel Processing

- Process up to 6 clients simultaneously
- Independent execution with isolated error handling
- Real-time dashboard monitoring
- Fast mode: 15-20 minutes | Deep mode: 35-40 minutes

### 📊 Real-Time Dashboard

- Live progress tracking for all clients
- Step-by-step execution visibility
- Direct NotebookLM notebook links
- Quality scoring and artifact verification

---

## Quick Start

### Prerequisites

- Python 3.9+
- NotebookLM CLI authenticated
- Google Gemini API key
- Google Drive API credentials (service account)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Project-APE

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Authenticate NotebookLM
notebooklm auth
```

### Run Your First Pipeline

```bash
# Fast mode (all clients)
./launch_ape.sh fast

# Deep mode (all clients)
./launch_ape.sh deep

# Specific client
./launch_ape.sh fast merck_test
```

Dashboard opens automatically at **http://localhost:8765**

---

## Architecture

```
┌──────────────────────────────────────────┐
│  Claude AI Orchestration Layer           │
│  • Pipeline monitoring                   │
│  • Error analysis & recovery             │
│  • Quality validation (>8.5 target)      │
│  • Artifact verification                 │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│  Multi-Process Orchestrator              │
│  • Parallel client execution             │
│  • Status tracking                       │
│  • Dashboard server                      │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│  NotebookLM Pipeline                     │
│  • Industry detection (Gemini AI)        │
│  • Google Drive source retrieval         │
│  • PDF consolidation                     │
│  • Deep research (2 prompts)             │
│  • Note generation (6 notes)             │
│  • Mind map creation                     │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│  NotebookLM Outputs                      │
│  • Notebooks with 40+ sources            │
│  • 6 comprehensive notes                 │
│  • Interactive mind maps                 │
│  • Quality scores >8.5/10                │
└──────────────────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| `main.py` | Multi-process orchestrator and dashboard launcher |
| `vars.py` | Configuration hub for clients and settings |
| `core/client_pipeline.py` | Main pipeline with Claude agent integration |
| `core/gemini_agent.py` | Intelligent orchestration with self-healing |
| `core/error_analyzer.py` | AI-powered error analysis |
| `core/quality_scorer.py` | Enhanced quality scoring |
| `dashboard/server.py` | Real-time monitoring dashboard |

---

## Output Structure

Each client produces a complete NotebookLM notebook:

### 📄 Sources (40+ per client)

- **Consolidated PDF:** Company materials from Google Drive
- **Research Sources:** Web sources from deep research
  - Industry reports
  - News articles
  - Company websites
  - Technical documentation

### 📝 Notes (6 per client)

1. **Industry Analysis & Future Trends**
2. **Customer Business Profile**
3. **Technical Landscape Assessment**
4. **Opportunity Assessment**
5. **Strategic Recommendations**
6. **Executive Summary**

### 🧠 Mind Map

- Visual representation of findings
- Interactive exploration of relationships
- Key insights highlighted

---

## Configuration

### Adding New Clients

Edit `vars.py`:

```python
clients = [
    "new_client_test",
    # ... existing clients
]

# Client configuration
new_client_test_name = "New Client Name"
new_client_test_folder = "https://drive.google.com/drive/folders/FOLDER_ID"
new_client_test_industry = "industry category"
new_client_test_subsegments = "subsegment 1, subsegment 2, subsegment 3"
```

### Execution Modes

**Fast Mode:**
- Research timeout: 600s (10 min)
- Optimized for speed
- Target: 15-20 min per client

**Deep Mode:**
- Research timeout: 1200s (20 min)
- Enhanced research depth
- Target: 35-40 min per client

### Quality Thresholds

```python
QUALITY_THRESHOLDS = {
    'min_sources': 15,
    'required_notes': 6,
    'min_quality_score': 8.5,
}
```

---

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup instructions
- **[GETTING-STARTED.md](GETTING-STARTED.md)** - Comprehensive guide
- **[LAUNCHER-GUIDE.md](LAUNCHER-GUIDE.md)** - Launcher script usage
- **[QUICKSTART.md](QUICKSTART.md)** - Fast track guide
- **[SERVICE-ACCOUNT-SETUP.md](SERVICE-ACCOUNT-SETUP.md)** - Google Drive setup
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## Troubleshooting

### Dashboard doesn't open

```bash
open http://localhost:8765
```

### Pipeline fails

```bash
# Check NotebookLM auth
notebooklm list

# Verify environment variables
cat .env
```

### Quality scores show 5.0

Known display bug - actual notebooks are fully populated. Verify in NotebookLM web interface.

---

## Performance

### Fast Mode Benchmarks

- **Single client:** 15-20 minutes
- **6 clients parallel:** 20-25 minutes total
- **Sources per client:** 40-68 sources
- **Success rate:** 100% (with Claude orchestration)

### Deep Mode Benchmarks

- **Single client:** 35-40 minutes
- **6 clients parallel:** 40-45 minutes total
- **Sources per client:** 40-70 sources
- **Enhanced research depth**

---

## Technology Stack

- **Python 3.9+** - Core runtime
- **NotebookLM CLI** - Research and notebook management
- **Google Gemini API** - AI-powered analysis
- **Claude AI** - Intelligent orchestration
- **Google Drive API** - Source document retrieval
- **Flask** - Real-time dashboard
- **Multiprocessing** - Parallel execution

---

## Project Structure

```
Project-APE/
├── main.py                 # Multi-process orchestrator
├── vars.py                 # Configuration hub
├── launch_ape.sh          # Launch script
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
│
├── core/                  # Core pipeline modules
│   ├── client_pipeline.py
│   ├── gemini_agent.py
│   ├── error_analyzer.py
│   ├── quality_scorer.py
│   ├── artifact_verifier.py
│   └── ...
│
├── dashboard/             # Real-time monitoring
│   ├── server.py
│   └── static/
│       └── kingkong.png   # Project logo
│
└── *.txt                  # Research and chat prompts
```

---

## Version History

**Current Version:** 3.0.4

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## Creator

**Jason Anderson**

- Created Project APE
- Developed all core components
- Maintains and evolves the system

---

## License

Created, developed, and maintained by Jason Anderson.

All rights reserved.

---

## Support

For issues, questions, or feature requests, contact Jason Anderson.

---

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE" width="200"/>
</p>

<p align="center">
  <strong>Project APE - Account Planning Engine</strong><br>
  Powered by Claude AI and NotebookLM
</p>
