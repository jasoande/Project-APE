<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="200"/>
  
  # Project APE
  **Account Planning Engine**
  
  *AI-Powered Enterprise Account Research & Intelligence Automation*
  
  [![Version](https://img.shields.io/badge/version-4.0.1-ee0000?style=for-the-badge&logo=github)](https://github.com/jasoande/Project-APE-dev)
  [![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/jasoande/Project-APE-dev)
  [![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
  
  **🎯 100% GUI-Driven Workflow | No Terminal Required**
</div>

---

## Overview

Project APE transforms enterprise account research from multi-day manual processes into **15-minute automated workflows**. Built on Google's NotebookLM platform, it leverages AI to automatically research companies, analyze industries, and generate comprehensive intelligence reports—all through an intuitive web interface.

**Key Value Proposition:**
- **95% Time Reduction** - Days of research compressed to minutes
- **180+ Sources Automatically** - AI imports and analyzes external research
- **Zero Technical Skills Required** - Double-click launcher, browser-based configuration
- **Enterprise-Grade Security** - OAuth 2.0 authentication, no embedded credentials
- **Production-Ready** - Containerized deployment, real-time monitoring, quality validation

---

## ✨ Key Features

### 🖱️ **Zero Terminal Interface**
Double-click launcher, browser-based configuration, no command-line experience needed.

### 🤖 **AI-Powered Research**
- Automatically imports 20-180 external sources per client
- Web research with NotebookLM's advanced AI
- Industry analysis, competitive intelligence, SWOT generation

### ⚡ **Multi-Client Parallel Execution**
- Process up to 5 clients simultaneously
- Fast mode: 15-20 minutes per client
- Deep mode: 45-60 minutes (8-9x more sources)

### 📊 **Real-Time Monitoring Dashboard**
- Live progress bars for each execution phase
- Streaming logs with color-coded status
- Quality scores (1-10) with completeness validation

### 📁 **Google Drive Integration**
- Direct upload from Drive folders (PDFs, Docs, Sheets)
- Automatic file format conversion
- 7-day intelligent caching

### 🎨 **Beautiful Web UI**
- Modern dark/light theme toggle
- Responsive design for mobile/tablet
- Live server-sent events for real-time updates

### ✅ **Quality Validation**
- AI-generated quality scores (1.0-10.0)
- Completeness checks across 12 analysis dimensions
- Source coverage validation

### 🚀 **Dual Execution Modes**
- **Fast Mode:** 15-20 min, 40-80 sources, quality target 8.0+
- **Deep Mode:** 45-60 min, 90-180 sources, quality target 8.5+

### 🔒 **Enterprise OAuth Security**
- No embedded API keys or credentials
- OAuth 2.0 for NotebookLM and Google Drive
- Containerized credential isolation

### 💻 **Cross-Platform Support**
- **Windows:** Native Python or Docker Desktop
- **macOS:** Native Python or Podman containers
- **Linux:** Native Python or Podman/Docker

---

## 🚀 Quick Start (3 Steps)

### Prerequisites

✅ **Required:**
- Python 3.10 or higher ([Download](https://www.python.org/downloads/))
- Google account with NotebookLM access ([Sign up](https://notebooklm.google.com))
- Google Chrome browser ([Download](https://www.google.com/chrome/))

✅ **Optional:**
- Gemini API key for quality scoring ([Get free key](https://ai.google.dev/))

---

### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE-dev.git
cd Project-APE-dev
```

**That's it!** No `pip install`, no `npm install`, no manual setup.

---

### Step 2: Launch (No Terminal Required!)

**Choose your platform:**

#### 🍎 macOS Users
1. Open Finder → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.command`
3. Browser opens automatically to http://localhost:8765/configure ✨

#### 🪟 Windows Users
1. Open File Explorer → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.py`
3. Browser opens automatically to http://localhost:8765/configure ✨

#### 🐧 Linux Users
1. File manager → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.py` (or `./launch-project-ape.py`)
3. Browser opens automatically to http://localhost:8765/configure ✨

**What happens automatically:**
- ✅ Virtual environment setup (first time: 2-5 min)
- ✅ Dependency installation (Flask, NotebookLM CLI, etc.)
- ✅ Dashboard server starts on port 8765
- ✅ Browser opens to configuration page

---

### Step 3: Configure in Browser

The dashboard opens at **http://localhost:8765/configure** with 3 setup tasks:

#### Task 1: NotebookLM Authentication (60 seconds)
1. Click **"Authenticate NotebookLM"** button
2. Chrome opens → Google login → Grant permissions
3. Return to dashboard (status updates automatically)

#### Task 2: Google Drive OAuth (90 seconds)
1. Click **"Setup Drive OAuth"** button
2. Follow OAuth setup wizard (create credentials if first time)
3. Upload `credentials.json` → Generate token
4. Grant Drive permissions in browser popup

#### Task 3: Add Your First Client (2 minutes)
1. **Client Name:** e.g., "Acme Corporation"
2. **Google Drive Folder URL:** Paste folder link with client PDFs
3. **Industry:** e.g., "pharmaceuticals" (or leave blank for auto-detect)
4. **Subsegments:** e.g., "drug discovery, clinical trials" (focuses research)
5. **Mode:** Fast (recommended first run)
6. Click **"Save Configuration"** → **"Launch Workflow"**

**Done!** Watch real-time progress in the dashboard.

**See:** [QUICKSTART.md](QUICKSTART.md) for detailed 5-minute walkthrough with screenshots.

---

## 📋 What You Get

### Generated Intelligence Reports

After 15-20 minutes (Fast mode), you'll find in `docs_generated/{client_id}/`:

1. **Account Research Report** (8-15 pages)
   - Executive summary
   - Industry analysis with trends and disruptions
   - SWOT analysis
   - Competitive landscape
   - Strategic insights
   - 80+ source citations

2. **Strategic Recommendations** (5-8 pages)
   - Product-market fit assessment
   - Deployment recommendations
   - ROI scenarios
   - Risk assessment

3. **Technology Landscape** (4-6 pages)
   - Current tech stack (inferred from documents)
   - Digital transformation initiatives
   - Pain point mapping

4. **Decision Maker Mapping** (3-5 pages)
   - Organizational chart (inferred)
   - Key decision makers
   - Buying process analysis

5. **Mind Map Visualization** (PNG)
   - Visual relationship diagram
   - Key themes and connections

6. **Quality Report** (JSON)
   - Quality score (1.0-10.0)
   - Completeness metrics
   - Source count and coverage

---

## 🏗️ Architecture Overview

Project APE uses a **multi-process orchestration architecture** with five core components:

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Web Dashboard** | Real-time monitoring, configuration | Flask, JavaScript, SSE |
| **Process Orchestrator** | Multi-client parallel execution | Python multiprocessing |
| **NotebookLM Integration** | AI research & analysis | NotebookLM CLI SDK |
| **Drive Manager** | Document downloads, caching | Google Drive API v3 |
| **Quality Validator** | Completeness scoring | Gemini AI (optional) |

### Pipeline Workflow

```
Phase 1: Download PDFs from Drive (30-60s)
    ↓
Phase 2: Create NotebookLM Notebook (10-15s)
    ↓
Phase 3: Research Queries (3-8 min, AI imports 40-80 sources)
    ↓
Phase 4: Analysis Prompts (8-12 min, 6 comprehensive analyses)
    ↓
Phase 5: Quality Validation (1-2 min, score 1-10)
    ↓
Complete: Outputs saved to docs_generated/
```

**See:** [ARCHITECTURE.md](Docs/ARCHITECTURE.md) for technical deep-dive.

---

## 💼 Use Cases

### Enterprise Sales Teams
**Scenario:** Research Fortune 500 prospects before account planning meetings

**Output:**
- Industry analysis with trends and disruptions
- SWOT analysis with competitive positioning
- Technology fit assessment
- Decision-maker mapping
- Strategic recommendations

**Time Saved:** 16 hours → 15 minutes per account

---

### Solution Architects
**Scenario:** Pre-sales technical discovery for complex deals

**Output:**
- Technology landscape analysis
- Digital transformation initiatives
- Pain point identification
- Product-market fit validation
- Risk assessment

**Benefit:** Data-driven technical positioning

---

### Account Managers
**Scenario:** Quarterly business reviews preparation

**Output:**
- Industry trends affecting client
- Competitive intelligence
- Opportunity mapping
- Success metrics alignment
- Strategic growth recommendations

**Benefit:** Executive-ready insights in minutes

---

## 🖥️ Platform Support Matrix

| Platform | Version | Installation Method | Status |
|----------|---------|---------------------|--------|
| **macOS** | 10.15+ (Catalina+) | Native Python | ✅ Fully Supported |
| **macOS** | 10.15+ | Podman Container | ✅ Fully Supported |
| **Linux** | Ubuntu 20.04+ | Native Python | ✅ Fully Supported |
| **Linux** | RHEL 8+, Fedora 35+ | Podman Container | ✅ Fully Supported |
| **Windows** | 10/11 | Native Python | ✅ Fully Supported |
| **Windows** | 10/11 | Docker Desktop | ✅ Fully Supported |

**Python Requirements:** 3.10+ (3.11+ recommended)  
**Browser Requirements:** Chrome or Firefox (Safari not supported for OAuth)

---

## 📚 Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup walkthrough | New users |
| [INSTALLATION.md](Docs/INSTALLATION.md) | Platform-specific installation guides | All users |
| [USER_GUIDE.md](Docs/USER_GUIDE.md) | Workflow execution & best practices | All users |
| [WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) | Web UI configuration reference | All users |
| [ARCHITECTURE.md](Docs/ARCHITECTURE.md) | Technical architecture deep-dive | Developers |
| [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) | Common issues & solutions | All users |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Developer contribution guidelines | Contributors |
| [CLAUDE.md](CLAUDE.md) | Claude Code developer guidance | Claude Code users |

---

## ⚡ Execution Modes Comparison

| Metric | Fast Mode | Deep Mode |
|--------|-----------|-----------|
| **Duration** | 15-20 minutes | 45-60 minutes |
| **External Sources** | 40-80 sources | 90-180 sources |
| **Research Queries** | 2 queries | 2 queries (longer processing) |
| **Analysis Prompts** | 6 prompts | 6 prompts (deeper reasoning) |
| **Best For** | Quick turnaround, initial research | Comprehensive analysis, critical deals |
| **Parallel Clients** | Up to 5 simultaneously | Up to 3 simultaneously |
| **Quality Target** | 8.0+ | 8.5+ |
| **Retry Rate** | ~5% | ~30% (acceptable) |

**Recommendation:** Start with Fast mode for first run, upgrade to Deep for final deliverables.

---

## 🛠️ Troubleshooting Quick Tips

### Dashboard Won't Open
```bash
# Check port 8765 not in use
lsof -ti :8765

# Verify Python version
python3 --version  # Should be 3.10+

# Run manual setup
./setup-environment.sh
```

### Authentication Failed
- Re-run NotebookLM auth: Click "Authenticate" button in web UI
- Use Chrome browser (Safari unsupported)
- Check credentials: `ls -la ~/.notebooklm/credentials.json`

### Workflow Timeout
- Check internet connection
- View real-time logs in dashboard
- Verify Drive folder permissions (must be accessible)
- See [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) for comprehensive guide

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup (5 steps)
- Code standards (Python, JavaScript, Shell)
- Testing procedures
- Pull request guidelines

**Quick contribution workflow:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Copyright © 2026 Jason Anderson**

---

## 🙏 Credits

**Built With:**
- [Google NotebookLM](https://notebooklm.google.com) - AI research platform
- [Flask](https://flask.palletsprojects.com/) - Web dashboard framework
- [Google Drive API](https://developers.google.com/drive) - Document management
- [Gemini AI](https://ai.google.dev/) - Quality validation (optional)

**Developed by:** Jason Anderson  
**Version:** 4.0.1  
**Release Date:** July 2026  
**Repository:** [github.com/jasoande/Project-APE-dev](https://github.com/jasoande/Project-APE-dev)

---

<div align="center">
  
  **Project APE - Transforming Account Research from Days to Minutes**
  
  *Enterprise AI Automation for Sales Intelligence*
  
  ---
  
  **Questions? Issues? Feature Requests?**  
  [Open an Issue](https://github.com/jasoande/Project-APE-dev/issues) | [View Documentation](Docs/) | [Discussions](https://github.com/jasoande/Project-APE-dev/discussions)
  
  ⭐ **Star this repo** if Project APE saves you time!
  
</div>
