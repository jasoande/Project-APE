# Project APE - Marriage Edition

![Project APE Logo](dashboard/static/kingkong.png)

**Account Planning Engine - AI-Powered Enterprise Account Planning Automation**

**Author & Project Owner:** Jason Anderson  
**Version:** 2.0.0  
**Last Updated:** June 10, 2026

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![NotebookLM](https://img.shields.io/badge/notebooklm-cli-orange.svg)](https://pypi.org/project/notebooklm/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [What's New](#-whats-new)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Execution Modes](#-execution-modes)
- [Dashboard](#-dashboard)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Performance](#-expected-performance)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Support](#-support)

---

## 🎯 Overview

Project APE (Account Planning Engine) automates the creation of comprehensive, AI-powered account plans for enterprise clients. Built on Google NotebookLM, it combines web research, document analysis, and AI-generated insights to produce professional account plans in minutes instead of hours.

### Built For
- **Sales Engineers** - Technical account planning and solution mapping
- **Solution Architects** - Customer environment analysis and recommendations
- **Account Managers** - Strategic account planning and relationship mapping

### What It Does
1. **Consolidates** all client documents into a single searchable PDF
2. **Researches** the client using deep web search (100+ sources)
3. **Analyzes** industry trends, competitors, and business objectives
4. **Generates** 12 comprehensive notes covering strategy, solutions, and recommendations
5. **Creates** visual mind maps for executive summaries
6. **Delivers** a complete NotebookLM notebook ready for collaboration

---

## ✨ Key Features

### 🚀 Dual-Mode Execution

#### Fast Mode (<16 minutes)
- Optimized for speed and testing
- Web research with quick source import
- 6 clients in parallel: **15 minutes total**
- Production validated

#### Deep Mode (30-90 minutes)
- Comprehensive deep research (100+ sources per client)
- Incremental deduplication after each research prompt
- Conservative timing for rate limiting
- Automatic retry logic with exponential backoff

### 🎯 Core Capabilities

- ✅ **True Multi-Process Execution** - Up to 6 clients in parallel
- ✅ **Real-Time Dashboard** - Red Hat-themed web UI at http://localhost:8765
- ✅ **Universal PDF Conversion** - Handles ANY file type (Office, images, text)
- ✅ **Smart Notebook Management** - DEV_{client}-TEST naming, deduplication
- ✅ **Intelligent Source Management** - Parallel conversion, auto-deduplication, retry logic
- ✅ **Quality Scoring** - 0-10 scale based on sources, notes, completeness
- ✅ **Descriptive Note Titles** - Professional naming, no generic labels
- ✅ **Fresh Authentication** - Forced check every run prevents stale sessions

### 📊 Dashboard Features (http://localhost:8765)

- **Live Progress Tracking** - Updates every 2 seconds
- **Execution Timer** - Persistent across page refreshes
- **Mode Indicator** - Dynamic display (Fast/Deep Mode)
- **Quality Scores** - 0-10 rating for each notebook
- **Color-Coded Status** - PENDING (blue), RUNNING (orange), COMPLETE (green), FAILED (red)
- **Direct NotebookLM Links** - One-click access to notebooks
- **Clean Status Management** - Auto-cleanup of stale files

---

## 🆕 What's New (v2.0.0)

**Deep Mode Implementation:**
- Deep research with conservative timing (45-60s delays)
- Incremental deduplication after each research prompt
- Handles 100+ sources per prompt
- 5-attempt retry logic (30s→480s exponential backoff)

**Source Management:**
- Fixed JSON parsing for dict format `{"sources": [...]}`
- Fixed None value handling (`url: null` for PDFs)
- Parallel PDF conversion using ProcessPoolExecutor
- Single `{Client}-One.pdf` consolidation

**Dashboard Improvements:**
- Dynamic mode display (Fast/Deep)
- Timer persistence across refreshes
- Quality score calculation (0-10)
- Status file cleanup before runs

**Quality & Reliability:**
- Descriptive note titles (12 professional titles)
- Smart rerun (reuse PDFs, fresh research)
- Chat retry logic (RPC errors 3, 9)
- Variable substitution ($name, $industry)

---

## 📦 Installation

### System Requirements

- **Operating System:** macOS or Linux
- **Python:** 3.8+
- **Disk Space:** 500MB+ for dependencies
- **RAM:** 2GB minimum (4GB recommended)

### System Dependencies

**macOS:**
```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install LibreOffice (for Office document conversion)
brew install --cask libreoffice

# Install Python 3
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
# Update packages
sudo apt-get update

# Install Python and pip
sudo apt-get install python3 python3-pip

# Install LibreOffice
sudo apt-get install libreoffice

# Install image processing libraries
sudo apt-get install libjpeg-dev zlib1g-dev
```

### Python Dependencies

**Install all packages:**
```bash
cd /Users/jasona/test/marriage
pip install -r requirements.txt
```

**Required packages (from requirements.txt):**
- `notebooklm>=0.7.1` - NotebookLM CLI
- `flask>=3.0.0` - Web framework
- `werkzeug>=3.0.0` - WSGI utilities
- `pypdf>=4.0.0` - PDF processing
- `PyPDF2>=3.0.0` - PDF library
- `reportlab>=4.0.0` - PDF generation
- `Pillow>=10.0.0` - Image processing
- `python-docx>=1.0.0` - Word documents
- `openpyxl>=3.1.0` - Excel files
- `pandas>=2.0.0` - Data processing
- `requests>=2.31.0` - HTTP library
- `python-dateutil>=2.8.0` - Date utilities

### NotebookLM CLI Setup

```bash
# Install CLI
pip install notebooklm-py

# Authenticate
notebooklm login

# Verify
notebooklm status
```

---

## ⚡ Quick Start

### 1. Configure Clients

Edit `vars.py`:

```python
clients = ["merck_test", "blue_yonder_test", ...]

merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_folder = str(Path(__file__).parent / "Venella_2026" / "Merck")
```

### 2. Run Pipeline

**Single client test:**
```bash
python3 main.py --mode fast --clients merck_test
```

**All clients:**
```bash
python3 main.py --mode fast
```

### 3. Monitor

**Dashboard:** http://localhost:8765  
**Logs:** `tail -f logs/merck_test.log`

---

## 🎯 Execution Modes

### Fast Mode

**Performance:** 13-15 min/client, 15-16 min for 6 parallel

**Characteristics:**
- Research delay: 8-12s
- Chat delay: 5-8s
- Sources: ~10-20 per prompt
- Deduplication: Once at end
- Quality: 8.0-8.5/10

```bash
python3 main.py --mode fast
```

### Deep Mode

**Performance:** 30-90 min/client

**Characteristics:**
- Research delay: 45-60s
- Chat delay: 60-90s
- Sources: 100-200 per prompt
- Deduplication: After EACH prompt
- Retry: 5 attempts, exponential backoff
- Quality: 9.0-10.0/10

```bash
python3 main.py --mode deep --clients merck_test
```

| Feature | Fast | Deep |
|---------|------|------|
| Research Delay | 8-12s | 45-60s |
| Chat Delay | 5-8s | 60-90s |
| Sources/Prompt | 10-20 | 100-200 |
| Deduplication | End | Incremental |
| Time (1 client) | 13-15 min | 30-90 min |
| Quality Score | 8.0-8.5 | 9.0-10.0 |

---

## 📊 Dashboard

**URL:** http://localhost:8765

### Features

**Header:**
- King Kong logo
- Mode indicator (Fast/Deep Mode - updates dynamically)
- Execution timer (persists across page refreshes)

**Stats Bar:**
- Total Clients
- Running (orange count)
- Complete (green count)
- Failed (red count)

**Overall Progress:**
- Aggregate progress bar
- "X of Y clients" completion

**Client Cards:**
- Client name
- Status pill (PENDING/RUNNING/COMPLETE/FAILED)
- Progress bar (0-100%)
- Current step
- Notebook ID
- Quality Score (0-10)
- Direct NotebookLM link

**Auto-Refresh:** Every 2 seconds

---

## ⚙️ Configuration

### Timing (vars.py)

**Fast Mode:**
```python
TIMINGS = {
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'source_import_wait': 15.0,
}
```

**Deep Mode:**
```python
DEEP_TIMINGS = {
    'ask_prompt_delay': (45.0, 60.0),
    'chat_prompt_delay': (60.0, 90.0),
    'source_import_wait': 30.0,
}
```

### Dashboard

```python
DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds
```

---

## 📈 Expected Performance

### Fast Mode
- 1 client: 13-15 minutes
- 6 clients (parallel): 15-16 minutes
- **Validated:** 15:11 for 6 clients (June 2026)
- Quality: 8.0-8.5/10

### Deep Mode
- 1 client: 30-90 minutes
- Sources: 100-200 imported
- Duplicates: 40-60% removed
- Quality: 9.0-10.0/10

---

## 🔧 Troubleshooting

### Authentication
```bash
# Fresh login
notebooklm auth logout
notebooklm login
notebooklm status
```

### Rate Limiting
- Use Deep Mode (conservative timing)
- Reduce parallel clients
- Wait 5-10 minutes between runs

### PDF Conversion
```bash
# Install LibreOffice
brew install --cask libreoffice  # macOS
sudo apt-get install libreoffice  # Linux
```

### Dashboard Issues
- Check port: `lsof -i :8765`
- Restart: `python3 main.py --mode fast`

---

## 📚 Documentation

**Project Files:**
- README.md (this file)
- docs/ARCHITECTURE.md

**Configuration:**
- vars.py - Client and timing configuration
- requirements.txt - Python dependencies
- main.py - Entry point

---

## 📞 Support

**Project Owner:** Jason Anderson

**Resources:**
- Dashboard: http://localhost:8765
- Logs: `logs/` directory
- GitHub Issues: For bug reports

**Response Time:**
- Bug reports: 24-48 hours
- Questions: 24-48 hours

---

## 📄 License

MIT License

Copyright (c) 2026 Jason Anderson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🙏 Acknowledgments

**Project Owner:** Jason Anderson

**Built With:**
- Google NotebookLM
- Flask
- PyPDF, ReportLab, Pillow
- Python multiprocessing

---

**Made with ❤️ for Account Managers and Solution Architects**

**Project APE - Automating Excellence in Account Planning**

**© 2026 Jason Anderson. All rights reserved.**

---

*README.md v2.0.0 - Last updated June 10, 2026*
