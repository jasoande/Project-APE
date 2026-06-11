# Project APE - Quick Start Guide

Get up and running with Project APE in 15 minutes.

## Prerequisites Check

Before starting, verify you have:
- [ ] Python 3.10 or higher: `python3 --version`
- [ ] pip installed: `pip --version`
- [ ] Node.js 18+ (will be installed in Step 1)
- [ ] Google account for NotebookLM
- [ ] 2GB free disk space
- [ ] macOS or Linux (Windows may work but untested)

## 5-Minute Setup

### Step 1: Install System Dependencies (2 minutes)

**macOS:**
```bash
brew install --cask libreoffice
brew install node git
```

**Linux (RHEL/Fedora):**
```bash
sudo dnf install -y libreoffice python3-pip
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs
```

### Step 2: Clone the Repository (1 minute)

```bash
git clone https://github.com/jasoande/Project-APE
cd Project-APE
```

### Step 3: Install NotebookLM CLI (1 minute)

```bash
# Install globally
npm install -g notebooklm

# Verify installation
notebooklm --version
```

### Step 4: Install Python Dependencies (2 minutes)

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install all packages
pip install -r requirements.txt
```

### Step 5: Authenticate with Google (1 minute)

```bash
notebooklm login
```

This opens your browser for Google OAuth. Sign in and authorize.

Verify authentication:
```bash
notebooklm status
```

You should see: `✅ Authenticated as: your-email@gmail.com`

## Configure Your First Client (5 minutes)

### Step 1: Edit vars.py

Open `vars.py` and customize the example client:

```python
# List of client tokens
clients = [
    "acme_corp",  # Your first client
]

# --- ACME Corp Configuration ---
acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology and software"
acme_corp_folder = str(Path(__file__).parent / "client_data" / "ACME_Corp")
```

### Step 2: Create Client Folder

```bash
mkdir -p client_data/ACME_Corp
```

### Step 3: Add Documents (Optional)

Place client documents in the folder:
```bash
cp /path/to/documents/* client_data/ACME_Corp/
```

Supported formats: PDF, DOCX, XLSX, PPTX, TXT, images

**Note:** If you skip this step, the pipeline will still run with web research only.

## Run Your First Pipeline (3 minutes)

### Fast Mode (Recommended for first run)

```bash
python3 main.py --mode fast --clients acme_corp
```

Expected output:
```
======================================================================
  PROJECT APE - ACCOUNT PLANNING ENGINE
  AI-Powered Enterprise Account Planning Automation
======================================================================

📋 Configuration:
   Mode: FAST
   Clients: 1
   Dashboard: Enabled

📊 Starting dashboard server...
   URL: http://localhost:8765
   ✅ Dashboard opened in browser

🚀 Starting: ACME Corporation
   Mode: FAST
   Log: acme_corp.log
```

### Monitor Progress

The dashboard opens automatically at http://localhost:8765

You can also watch the log:
```bash
tail -f logs/acme_corp.log
```

### Expected Timeline (Fast Mode)
- **1 client**: 13-15 minutes
- **Stages**:
  - PDF consolidation: 1-2 min
  - Research prompts: 3-5 min
  - Chat prompts: 8-10 min
  - Mind map: 1 min

## View Results

When complete, the dashboard shows:
- ✅ Status: COMPLETE
- 📊 Quality Score: 8.0-10.0/10
- 🔗 Direct link to NotebookLM notebook

Click the notebook link to view your account plan!

## What You Get

Your NotebookLM notebook includes:

### Sources
- Consolidated PDF (all client documents)
- 10-20 web research sources (Fast mode)
- All sources deduplicated

### Notes (12 sections)
1. Industry Analysis & Technology Adoption
2. Business Objectives & IT Initiatives
3. Market & Competitive Analysis
4. Innovation & Adoption Assessment
5. Executive Summary
6. Technology Partners & Ecosystem
7. Red Hat Value Propositions
8. Solution Ideas & Recommendations
9. Team Onboarding Guide
10. Partner Briefing
11. Innovation Ideas
12. Complete Account Plan

### Visualization
- Mind map of key insights

## Troubleshooting

### "notebooklm: command not found"
```bash
# Reinstall NotebookLM CLI
npm install -g notebooklm
notebooklm --version
```

### "Authentication failed"
```bash
notebooklm login
```

### "Google API errors" or "Module not found"
```bash
# Upgrade pip and reinstall requirements
python3 -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### "Client folder not found"
- Check path in vars.py matches actual folder
- Folder name is case-sensitive
- Use absolute path or relative to Project-APE root

### "LibreOffice not found"
- Reinstall LibreOffice
- macOS: `brew install --cask libreoffice`
- Linux: `sudo dnf install libreoffice`

### "Port 8765 already in use"
- Change port in vars.py: `DASHBOARD_PORT = 8766`
- Or kill existing process: `lsof -ti:8765 | xargs kill`

### Dashboard not updating
- Hard refresh browser (Cmd+Shift+R or Ctrl+F5)
- Check status files: `ls -la .multi_process_status/`

## Next Steps

### Try Deep Mode (30-90 minutes)

For comprehensive research with 100+ sources:
```bash
python3 main.py --mode deep --clients acme_corp
```

Deep mode features:
- 45-60s delays between prompts
- 100-200 web sources imported
- Incremental deduplication
- Higher quality scores (9.0-10.0)

### Process Multiple Clients

Edit `vars.py` to add more clients, then:
```bash
python3 main.py --mode fast
```

All clients run in parallel!

### Customize Prompts

Edit prompt files to match your needs:
- `ask_prompt_01.txt` - Foundation research
- `ask_prompt_02.txt` - Industry analysis
- `chat_prompt_01.txt` through `chat_prompt_12.txt` - Specific sections

Variables available:
- `$name` - Client name
- `$industry` - Client industry

### Advanced Options

```bash
# Run without dashboard
python3 main.py --mode fast --no-dashboard

# Specific clients only
python3 main.py --mode fast --clients client1 client2 client3

# Get help
python3 main.py --help
```

## Tips for Success

1. **Start with Fast mode** to validate setup
2. **Use Deep mode** for important strategic accounts
3. **Check quality scores** - aim for 8.0+
4. **Review logs** if issues occur
5. **Keep dashboard open** for real-time monitoring
6. **Space out runs** to avoid rate limiting (5-10 min between)

## Learning Resources

- **README.md** - Complete documentation
- **ARCHITECTURE.md** - Technical deep-dive
- **CONTRIBUTING.md** - Development guide
- **Dashboard** - http://localhost:8765

## Support

- **GitHub Issues** - Bug reports and feature requests
- **Logs** - Check `logs/` directory for detailed output
- **Project Owner** - Jason Anderson

---

**You're ready to go! Run your first pipeline and explore the results.** 🚀
