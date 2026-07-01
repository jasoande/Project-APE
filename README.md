<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="200"/>
  
  # Project APE
  **Account Planning Engine**
  
  *AI-Powered Enterprise Account Research & Intelligence Automation*
  
  [![Version](https://img.shields.io/badge/version-4.0.1-ee0000?style=for-the-badge&logo=github)](https://github.com/yourusername/Project-APE-dev)
  [![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/yourusername/Project-APE-dev)
  [![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
  
  **🎯 100% GUI-Driven Workflow | No Terminal Required**
</div>

---

## 📖 Overview

**Project APE** (Account Planning Engine) is an enterprise-grade AI automation platform that transforms account research from a multi-day manual process into a 15-minute automated workflow. Built on Google's NotebookLM platform, Project APE generates comprehensive account intelligence, competitive analysis, and strategic recommendations for enterprise sales teams.

**Key Innovation:** Fully GUI-driven workflow — double-click to launch, configure everything in your web browser, monitor real-time progress through an intuitive dashboard. No command-line knowledge required.

---

## ✨ Key Features

- **🖱️ Zero Terminal Interface** — Double-click launcher, configure in web browser, monitor via dashboard
- **🤖 AI-Powered Research** — Automated web research importing 20-180 external sources per client
- **📊 Multi-Client Parallel Execution** — Process up to 5 clients simultaneously (15-60 min total)
- **🔄 Real-Time Progress Monitoring** — Live dashboard with progress bars, logs, and execution metrics
- **☁️ Google Drive Integration** — Direct upload from Drive folders (PDFs, Google Docs, Sheets)
- **🎨 Beautiful Web Interface** — Modern dark/light theme UI with live status updates
- **📈 Quality Validation** — AI-generated quality scores (1-10) with completeness checks
- **🚀 Two Execution Modes** — Fast mode (15-20 min) vs. Deep mode (45-60 min, 8-9x more sources)

---

## 🚀 Getting Started

### Prerequisites

Before launching Project APE, ensure you have:

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **Google Chrome browser** (required for NotebookLM authentication)
- **Google account** with access to NotebookLM ([notebooklm.google.com](https://notebooklm.google.com))
- **Internet connection** (for AI research and web scraping)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Project-APE-dev.git
cd Project-APE-dev
```

---

### Step 2: Launch Project APE

**🖱️ No terminal commands needed for normal usage!**

#### On macOS:
1. Double-click `launch-project-ape.command` in Finder
2. Browser opens automatically to configuration page

#### On Windows:
1. Double-click `launch-project-ape.py`
2. Browser opens automatically to configuration page

#### On Linux:
1. Double-click `launch-project-ape.py` (or run: `./launch-project-ape.py`)
2. Browser opens automatically to configuration page

**What happens automatically:**
- ✅ Checks if virtual environment exists
- ✅ Runs automated setup if needed (2-5 minutes first time)
- ✅ Starts dashboard server in background
- ✅ Opens browser to configuration page

---

### Step 3: Follow Web Setup Wizard

The launcher opens **http://localhost:8765/configure** where you'll complete setup:

#### **Setup Page Tasks:**

1. **NotebookLM Authentication**
   - Click "Authenticate NotebookLM" button
   - Follow OAuth flow in browser
   - Status changes to ✅ when complete

2. **Google Drive OAuth**
   - Click "Setup Drive OAuth" button
   - Follow OAuth flow in browser
   - Upload credentials.json file
   - Generate token
   - Status changes to ✅ when complete

3. **Configuration Review**
   - System automatically validates all components
   - Green checkmarks indicate ready status
   - Red X indicators show what needs attention

**See [Docs/WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) for detailed setup walkthrough.**

---

### Step 4: Configure Clients

In the web configuration interface:

1. **Add Client Button** — Click to create new client entry

2. **Fill Client Details:**
   - **Client Name**: "Acme Corporation"
   - **Client ID**: `acme_corp` (lowercase, underscores only)
   - **Google Drive Folder URL**: `https://drive.google.com/drive/folders/1ABC123XYZ`
   - **Industry** (optional): "technology" or leave blank for auto-detection
   - **Industry Subsegments**: "cloud, AI/ML, DevOps, cybersecurity"

3. **Global Settings:**
   - **Persona**: "Red Hat solutions architect" (AI role/perspective)
   - **Execution Mode**: Fast (15-20 min) or Deep (45-60 min)
   - **Dashboard Port**: 8765 (default)

4. **Save Configuration** — Changes auto-save to `vars.py`

---

### Step 5: Launch Workflows

**From the Dashboard:**

1. Navigate to **Dashboard** tab (top navigation)
2. Click **"Launch Workflows"** button
3. Select clients to process (checkboxes)
4. Click **"Start Execution"**

**Real-time monitoring:**
- Progress bars for each client
- Live log streaming
- Phase indicators (PDF download → Notebook creation → Research → Analysis → Quality)
- Estimated time remaining
- Quality scores upon completion

**Completion:** Outputs saved to `docs_generated/<client_id>/`

---

## 📚 Documentation

Comprehensive guides available in the `Docs/` directory:

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start guide |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Technical architecture and overview |
| [INSTALLATION.md](Docs/INSTALLATION.md) | Complete installation & setup guide |
| [WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) | Web UI configuration walkthrough |
| [USER_GUIDE.md](Docs/USER_GUIDE.md) | Detailed usage guide with best practices |
| [ARCHITECTURE.md](Docs/ARCHITECTURE.md) | Technical architecture documentation |
| [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Developer contribution guide |

---

## 🔧 Troubleshooting

### Dashboard Won't Open

**Symptoms:** Browser doesn't open, or shows "Connection refused"

**Solutions:**
1. Check if server is running: Navigate to http://localhost:8765 manually
2. Port conflict: Another app using port 8765
   - Change port in `vars.py`: `DASHBOARD_PORT = 8766`
   - Re-launch
3. Firewall blocking: Allow Python through firewall

---

### Authentication Failed

**Symptoms:** "NotebookLM authentication failed" or "Drive OAuth failed"

**Solutions:**
1. **NotebookLM:**
   - Re-run authentication from web UI
   - Ensure Chrome browser is default
   - Check credentials: `~/.notebooklm/credentials.json` exists
   
2. **Google Drive:**
   - Re-upload `credentials.json` in web UI
   - Regenerate token
   - Verify Drive folder permissions (must be accessible by your Google account)

---

### Workflow Stuck/Timeout

**Symptoms:** Progress bar frozen, phase not advancing

**Solutions:**
1. Check logs in dashboard (real-time log viewer)
2. Look for quota errors (NotebookLM API limits)
3. Verify internet connection
4. Restart workflow from dashboard

---

**See [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) for comprehensive troubleshooting guide.**

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick summary:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Test using GUI launcher (`python3 launch-project-ape.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

**Built with:**
- [NotebookLM](https://notebooklm.google.com) — Google's AI research platform
- [Flask](https://flask.palletsprojects.com/) — Web dashboard framework
- [Google Drive API](https://developers.google.com/drive) — Document management

**Developed by:** Jason Anderson  
**Version:** 4.0.1  
**Release Date:** July 2026

---

<div align="center">
  
  **🎯 Project APE — Transforming Account Research from Days to Minutes**
  
  *Enterprise AI Automation for Sales Intelligence*
  
  ---
  
  **Questions? Issues? Feature Requests?**  
  [Open an issue](https://github.com/yourusername/Project-APE-dev/issues) | [View documentation](Docs/) | [Watch demo video](Docs/videos/)
  
</div>
