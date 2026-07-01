<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="200"/>
  
  # Project APE Quick Start
  
  **5 Minutes to Your First Account Plan**
  
  No terminal commands. No configuration files. Just point and click.
</div>

---

## Prerequisites

Before you start, ensure you have:

- **Python 3.10 or higher** installed ([Download Python](https://www.python.org/downloads/))
- **Google Account** with access to NotebookLM ([notebooklm.google.com](https://notebooklm.google.com))
- **Google Drive** with client documents uploaded
- **Chrome or Firefox browser** (required for OAuth authentication)

---

## Instant Start - 7 Easy Steps

### Step 1: Clone the Repository

Open your terminal and run this single command:

```bash
git clone https://github.com/yourusername/Project-APE.git
cd Project-APE
```

That's the only terminal command you need. Everything else is in the browser.

---

### Step 2: Launch Project APE

**Double-click** `launch-project-ape.py` in your file browser, or run:

```bash
python3 launch-project-ape.py
```

The launcher will:
- Check for required dependencies
- Automatically install missing packages (first-time setup takes 2-5 minutes)
- Start the dashboard server in the background
- Open your browser to the configuration page

You'll see:
```
✅ Dashboard server is ready
🌐 Opening browser: http://localhost:8765/configure
```

---

### Step 3: Web Browser Opens Automatically

Your default browser opens to the **Project APE Configuration Dashboard**.

If the browser doesn't open automatically, navigate to: [http://localhost:8765/configure](http://localhost:8765/configure)

---

### Step 4: Follow the On-Screen Setup Wizard

The dashboard guides you through a 3-step setup process:

#### **4a. NotebookLM Authentication**

1. Click **"Authenticate NotebookLM"** button
2. Chrome browser window opens automatically
3. Log in to your Google account
4. Grant permission to NotebookLM
5. Return to dashboard - you'll see ✅ **NotebookLM Ready**

#### **4b. Google Drive OAuth**

1. Click **"Authenticate Google Drive"** button
2. Browser opens to Google OAuth consent screen
3. Select your Google account
4. Grant permission to access Google Drive
5. Return to dashboard - you'll see ✅ **Google Drive Connected**

#### **4c. Environment Check**

The dashboard automatically validates:
- Python dependencies ✓
- Authentication status ✓
- Filesystem permissions ✓

All green checkmarks = ready to go!

---

### Step 5: Add Your First Client

In the **"Configure Clients"** section:

1. **Client Name** (text input):
   ```
   Acme Corporation
   ```

2. **Google Drive Folder URL** (paste the full URL):
   ```
   https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J
   ```
   
   Right-click your Drive folder → "Get link" → Paste here

3. **Industry** (select from dropdown or type custom):
   - Auto-detect from folder contents (recommended), or
   - Choose: Technology, Financial Services, Healthcare, Manufacturing, etc.
   - Or type your own: "Cloud Infrastructure", "Fintech", "Medical Devices"

4. **Research Mode** (radio buttons):
   - ⚡ **Fast Mode**: 15-20 minutes, 40-60 sources (recommended for first run)
   - 🔬 **Deep Mode**: 45-60 minutes, 200-400 sources (comprehensive research)

5. Click **"+ Add Client"** button

Your client appears in the list below with status "Ready to Launch".

---

### Step 6: Start the Workflow

1. Review your client configuration in the summary card
2. Click the big blue **"Start Workflow"** button
3. Confirm when prompted: "Launch workflow for Acme Corporation?"

The dashboard switches to **Real-Time Progress View**.

---

### Step 7: Watch Real-Time Progress

The dashboard shows live updates every 2 seconds:

**Progress Bars:**
- 📄 **Phase 1**: Consolidating PDFs (30 seconds)
- 📚 **Phase 2**: Creating Notebook (45 seconds)
- 🔍 **Phase 3**: Research Queries (3-5 minutes)
- 💡 **Phase 4**: Analysis & Insights (8-12 minutes)
- 🗺️ **Phase 5**: Mind Map Generation (2 minutes)

**Live Log Stream:**
```
[12:34:56] Starting workflow for Acme Corporation
[12:35:12] ✓ Consolidated 12 PDFs into Acme Corporation-One.pdf
[12:35:45] ✓ Notebook created: Acme Corporation
[12:36:30] ✓ Research query 1/2 complete (45 sources imported)
[12:38:15] ✓ Analysis prompt 3/6 complete
...
```

**Completion Message:**
```
🎉 Workflow Complete - Acme Corporation
Total time: 18 minutes 43 seconds
Documents ready in: docs_generated/acme_corporation/
```

---

## What to Expect

### Fast Mode (15-20 minutes)

- **PDF Consolidation**: 30 seconds
- **Notebook Setup**: 45 seconds  
- **Research Phase**: 3-5 minutes (40-60 external sources)
- **Analysis Phase**: 8-12 minutes (6 comprehensive prompts)
- **Mind Map Generation**: 2 minutes

**Total Sources**: 40-80 web sources + your uploaded documents

### Deep Mode (45-60 minutes)

- **Research Phase**: 12-18 minutes (200-400 external sources)
- **Analysis Phase**: 25-35 minutes (deeper AI reasoning)

**Total Sources**: 200-500 web sources + your uploaded documents

### Output Files

All generated documents appear in: `docs_generated/{client_name}/`

You'll get:
- **Account Research Report** (comprehensive analysis)
- **Industry Analysis** (trends, competitive landscape)
- **Strategic Recommendations** (actionable insights)
- **Mind Map Visualization** (relationship diagram)
- **Executive Summary** (1-page overview)

---

## Next Steps

### Add More Clients

1. Click **"Configure New Client"** in the dashboard
2. Repeat Steps 5-7 for each client
3. Run up to 5 clients in parallel

### Full Documentation

- [README.md](README.md) - Complete feature overview
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical architecture
- [Docs/](Docs/) - User guides, API reference, best practices
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide

---

## Need Help?

**Dashboard Not Opening?**
- Verify Python 3.10+ installed: `python3 --version`
- Check port 8765 is not in use
- Run setup manually: `./setup-environment.sh`

**Authentication Failed?**
- Use Chrome or Firefox (Safari not supported for OAuth)
- Check firewall isn't blocking localhost:8765
- Try incognito/private browsing mode

**Workflow Stuck?**
- Check live logs in dashboard for error messages
- Verify Google Drive folder URL is correct and accessible
- See [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)

---

<div align="center">
  
  **Ready to automate your account research?**
  
  [⬆ Back to Top](#project-ape-quick-start) | [📖 Full Documentation](README.md) | [🐛 Report Issues](https://github.com/yourusername/project-ape/issues)
  
</div>
