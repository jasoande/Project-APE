<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="180"/>
  
  # Account Intelligence Quick Start Guide
  
  **5 Minutes to Your First Account Intelligence Report**
  
  No terminal commands. No configuration files. Just point and click.
  
  *Version 4.0.1 | July 2026*
</div>

---

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

✅ **Required (5-minute setup):**
- [ ] **Python 3.10 or higher** installed ([Download](https://www.python.org/downloads/))
- [ ] **Google account** with NotebookLM access ([Sign up](https://notebooklm.google.com))
- [ ] **Google Chrome browser** installed ([Download](https://www.google.com/chrome/))
- [ ] **Client documents** uploaded to a Google Drive folder

✅ **Optional (for advanced features):**
- [ ] Gemini API key for quality scoring ([Get free key](https://ai.google.dev/))
- [ ] Multiple client folders prepared for parallel execution

**Estimated Total Setup Time:** 5-7 minutes (first-time users)

---

## ⚡ Installation (1 Minute)

### Step 1: Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE-dev.git
cd Project-APE-dev
```

**That's it!** No `pip install`, `npm install`, or manual dependency setup required.

The first time you launch, dependencies install automatically (2-5 minutes).

---

## 🚀 Launch (1 Click)

### Step 2: Start Account Intelligence

**Choose your platform:**

<details>
<summary><b>🍎 macOS Users</b></summary>

1. Open **Finder** → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.command`
3. Browser opens automatically to http://localhost:8765/configure ✨

**What you'll see:**
```
✅ Checking virtual environment...
✅ Installing dependencies (first time: 2-5 minutes)...
✅ Starting dashboard server...
✅ Dashboard ready at http://localhost:8765
🌐 Opening browser...
```

</details>

<details>
<summary><b>🪟 Windows Users</b></summary>

1. Open **File Explorer** → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.py`
3. Browser opens automatically to http://localhost:8765/configure ✨

**Troubleshooting:** If browser doesn't open, manually visit: http://localhost:8765

</details>

<details>
<summary><b>🐧 Linux Users</b></summary>

1. **File manager** → Navigate to `Project-APE-dev` folder
2. **Double-click** `launch-project-ape.py` (or run `./launch-project-ape.py` in terminal)
3. Browser opens automatically to http://localhost:8765/configure ✨

**Desktop integration:** Double-click `project-ape-launcher.desktop` to add to application menu

</details>

---

## 🎯 First-Time Setup (3 Minutes)

The browser shows **3 setup tasks** with visual progress indicators.

---

### ✅ Task 1: NotebookLM Authentication (60 seconds)

**What You'll See:**
```
[ ] NotebookLM Authentication
    Status: Not configured
    [Authenticate NotebookLM] button
```

**What To Do:**
1. Click **"Authenticate NotebookLM"** button
2. Chrome opens → Google login screen
3. Choose your Google account
4. Grant NotebookLM permissions:
   - ✅ Create and manage notebooks
   - ✅ Add sources to notebooks
   - ✅ Generate AI content
5. **Close Chrome tab** → Return to dashboard

**Success Indicator:**
```
[✓] NotebookLM Authentication
    Status: ✅ Authenticated as user@example.com
```

**⚠️ Important:** Use **Chrome or Firefox** - Safari is not supported for OAuth.

---

### ✅ Task 2: Google Drive OAuth (90 seconds)

**What You'll See:**
```
[ ] Google Drive OAuth
    Status: Not configured
    [Setup Drive OAuth] button
```

**What To Do:**

**First Time? Create OAuth Credentials:**
1. Click **"Setup Drive OAuth"** button
2. Dashboard shows step-by-step wizard
3. Follow Google Cloud Console link
4. Create OAuth 2.0 client ID (Desktop app)
5. Download `credentials.json` file

**Setup OAuth Token:**
1. Click **"Upload credentials.json"** button in dashboard
2. Select the downloaded `credentials.json` file
3. Click **"Generate Token"** button
4. Browser opens → Google Drive permissions
5. Grant Drive access:
   - ✅ View and download files
   - ✅ View file metadata
6. **Close browser tab** → Return to dashboard

**Success Indicator:**
```
[✓] Google Drive OAuth
    Status: ✅ Token generated, Drive access granted
    Expiry: 90 days
```

**📝 Note:** See [WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) for detailed OAuth setup with screenshots.

---

### ✅ Task 3: Environment Validation (Automatic)

**What You'll See:**
```
[✓] Environment Validation
    ✅ Python 3.11.4 detected
    ✅ Flask 2.3.2 installed
    ✅ NotebookLM CLI v1.2.0 installed
    ✅ Filesystem permissions OK
    ✅ Port 8765 available
```

**No action needed** - this runs automatically during launch.

---

## 🏢 Configure Your First Client (2 Minutes)

Scroll down to the **"Add New Client"** form.

---

### Field 1: Client Name

```
Example: Acme Corporation
```

**Purpose:** How you want the client referred to in reports  
**Tips:** Use full legal name or common name

---

### Field 2: Client ID (Auto-Generated)

```
Example: acme_corp
```

**Purpose:** Used for file naming and folder structure  
**Format:** Lowercase, underscores only, no spaces  
**Auto-filled** from Client Name, but you can customize

---

### Field 3: Google Drive Folder URL

```
Example: https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J
```

**How to get this:**
1. Open **Google Drive** in browser
2. Navigate to folder containing client documents
3. Right-click folder → **"Get link"**
4. Copy URL and paste here

**Supported file types:**
- ✅ **PDFs** (preferred, best quality)
- ✅ Google Docs (auto-converted)
- ✅ Google Sheets (auto-converted)
- ❌ Images, videos, archives

**Recommended:** 5-15 substantive PDFs per client (annual reports, 10-Ks, white papers, case studies)

---

### Field 4: Industry (Optional - Auto-Detect)

```
Example: pharmaceuticals and life sciences
```

**Options:**
- **Leave blank** for AI auto-detection (analyzes documents)
- **Or specify:** Technology, Financial Services, Healthcare, Manufacturing, Retail, Energy, etc.

**Why specify?** Focuses research prompts and analysis perspective

---

### Field 5: Industry Subsegments

```
Example: drug discovery, clinical trials, manufacturing operations
```

**Purpose:** Focuses AI research on specific areas within the industry  
**Format:** Comma-separated list, 3-5 subsegments works best

**Examples by industry:**
- **Technology:** "cloud infrastructure, SaaS platforms, cybersecurity, AI/ML"
- **Financial:** "banking, wealth management, fintech, payments"
- **Healthcare:** "hospitals, pharmaceuticals, medical devices, telehealth"
- **Manufacturing:** "automotive, aerospace, supply chain, IoT"

**Tips:**
- Be specific: "cloud infrastructure" > "technology"
- Avoid overly broad: "healthcare" is too general
- Avoid overly narrow: "Phase 3 oncology trials" is too specific

---

### Field 6: Execution Mode

Choose one:

#### ⚡ Fast Mode (Recommended for first run)
- **Duration:** 15-20 minutes
- **External Sources:** 40-80 sources automatically imported
- **Quality Target:** 8.0+
- **Best for:** Quick turnaround, initial research, time-sensitive

#### 🔬 Deep Mode
- **Duration:** 45-60 minutes  
- **External Sources:** 90-180 sources automatically imported
- **Quality Target:** 8.5+
- **Best for:** Comprehensive analysis, critical deals, final deliverables

**Recommendation:** Start with **Fast mode**. If quality score < 8.0, re-run in Deep mode.

---

### Field 7: Persona (Global Setting)

```
Example: Red Hat solutions architect
```

**Purpose:** AI adopts this perspective for all analyses

**Good examples:**
- "Enterprise sales consultant specializing in financial services"
- "Technology solutions architect focused on cloud migration"
- "Strategic account manager for Fortune 500 healthcare"

**Tips:**
- Include role AND industry/focus area
- Be specific to get targeted insights
- Applies to all clients (can be changed later)

---

### Save & Launch

1. Click **"Add Client"** button at bottom of form
2. Client card appears showing configuration summary
3. Review your settings
4. Click **"Save Configuration"** button
5. Click **"Launch Workflow"** button

**Confirmation Dialog:**
```
Launch workflow for Acme Corporation?

Mode: Fast (15-20 minutes)
Industry: Auto-detect
Sources: Expect 40-80 external sources

[Cancel] [Start Workflow]
```

Click **"Start Workflow"** to begin!

---

## 📊 Watch Real-Time Progress (15 Minutes)

Dashboard automatically switches to **Progress View** with live updates every 2 seconds.

---

### Progress Bars & Status

```
Acme Corporation                                    [Mode: Fast]

Phase 1: Downloading PDFs from Drive               ████████████ 100%
         ✅ Complete (45 seconds)
         • Downloaded 8 PDFs (42 MB total)

Phase 2: Creating NotebookLM Notebook              ████████████ 100%
         ✅ Complete (12 seconds)
         • Notebook ID: abc123xyz
         • Sources uploaded successfully

Phase 3: Research Queries                          ██████░░░░░░  50%
         🔄 In Progress (3 min 24 sec elapsed)
         • Query 1/2 complete (42 sources imported)
         • Query 2/2 in progress...

Phase 4: Analysis Prompts                          ░░░░░░░░░░░░   0%
         ⏳ Pending (starts after Phase 3)

Phase 5: Quality Validation                        ░░░░░░░░░░░░   0%
         ⏳ Pending

Elapsed Time: 4 min 21 sec | Estimated Remaining: 11 min 39 sec
```

---

### Live Log Stream

```
[14:23:45] Starting workflow for Acme Corporation (Fast Mode)
[14:24:12] ✓ Downloaded 8 PDFs from Drive (42 MB total)
[14:24:30] ✓ Notebook created: notebook_id_abc123
[14:24:45] ✓ Uploaded 8 sources to notebook
[14:25:15] ✓ Research query 1/2 complete (42 external sources)
[14:26:30] ✓ Research query 2/2 complete (38 external sources)
[14:27:00] ✓ Analysis prompt 1/6 complete (Industry Overview)
[14:28:15] ✓ Analysis prompt 2/6 complete (SWOT Analysis)
[14:29:30] ✓ Analysis prompt 3/6 complete (Technology Landscape)
[14:30:45] ✓ Analysis prompt 4/6 complete (Competitive Positioning)
[14:32:00] ✓ Analysis prompt 5/6 complete (Pain Points)
[14:33:15] ✓ Analysis prompt 6/6 complete (Strategic Recommendations)
[14:34:00] ✓ Quality validation complete (Score: 8.5/10)
[14:34:15] ✅ Workflow complete - outputs saved
```

---

### Phase Timings

| Phase | Fast Mode | Deep Mode |
|-------|-----------|-----------|
| Phase 1: PDF Download | 30-60 sec | 30-60 sec |
| Phase 2: Notebook Creation | 10-15 sec | 10-15 sec |
| Phase 3: Research | 3-5 min | 12-18 min |
| Phase 4: Analysis | 8-12 min | 25-35 min |
| Phase 5: Validation | 1-2 min | 2-3 min |
| **Total** | **15-20 min** | **45-60 min** |

---

### Completion Message

```
🎉 Workflow Complete - Acme Corporation

Total Time: 18 min 43 sec
External Sources Imported: 80
Quality Score: 8.5/10 ⭐
Documents Generated: 6 files

📂 Output Location: docs_generated/acme_corp/

[Download All as ZIP] [View in NotebookLM] [Launch New Workflow]
```

---

## 📄 Understanding Your Outputs

Generated files are in: `docs_generated/acme_corp/`

---

### 1. `Acme Corporation_Analysis.txt` (Main Report)

**Content:**
- Executive summary
- Industry analysis (trends, disruptions, regulations)
- SWOT analysis
- Competitive landscape  
- Technology trends
- Strategic insights

**Length:** 8,000-15,000 words (25-40 pages formatted)  
**Sources:** 80+ citations  
**Format:** Plain text (import to Word/Google Docs for formatting)

---

### 2. `NotebookLM_Link.txt`

**Content:**
```
https://notebooklm.google.com/notebook/abc123xyz
```

**Purpose:** Direct link to interactive NotebookLM notebook  
**Use:** Click to ask follow-up questions, explore sources, generate more content

---

### 3. `Quality_Score.json`

**Content:**
```json
{
  "client_name": "Acme Corporation",
  "overall_score": 8.5,
  "completeness": {
    "industry_analysis": "complete",
    "swot_analysis": "complete",
    "technology_trends": "complete",
    "competitive_analysis": "complete",
    "pain_points": "complete",
    "recommendations": "complete"
  },
  "sources": {
    "pdf_uploads": 8,
    "external_imports": 80,
    "total": 88
  },
  "execution_time": "18m 43s",
  "mode": "fast"
}
```

**Purpose:** Workflow validation and quality metrics

---

## 🎯 Next Steps

### For First-Time Users

1. **✅ Review outputs** - Open text files in `docs_generated/`
2. **✅ Check quality** - Open `Quality_Score.json`
3. **✅ Explore NotebookLM** - Click link to ask follow-up questions
4. **✅ Test with second client** - Add another client, compare quality
5. **✅ Try Deep Mode** - Re-run same client in Deep mode to see difference

---

### For Power Users

1. **Parallel Execution** - Add 3-5 clients, run simultaneously
2. **Customize Prompts** - Edit `ask_prompt_*.txt` and `chat_prompt_*.txt` in root directory
3. **Tune Timing** - Adjust retry and delay settings in `vars.py`
4. **Container Deployment** - See [INSTALLATION.md](Docs/INSTALLATION.md) for Podman/Docker setup

---

### Learn More

- [USER_GUIDE.md](Docs/USER_GUIDE.md) - Workflow best practices, quality optimization
- [ARCHITECTURE.md](Docs/ARCHITECTURE.md) - How it works under the hood
- [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) - Common issues and solutions
- [CONTRIBUTING.md](CONTRIBUTING.md) - Customize and extend Account Intelligence

---

## 🔧 Troubleshooting Quick Tips

### Dashboard Won't Open

**Symptom:** Browser shows "Connection refused" or "This site can't be reached"

**Quick Fix:**
1. Check port 8765: `lsof -ti :8765` (macOS/Linux) or `netstat -an | findstr :8765` (Windows)
2. If port in use, kill process or change `DASHBOARD_PORT` in settings
3. If still fails, run manually: `python3 launch-project-ape.py` and check terminal output

**See:** [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md#dashboard-issues)

---

### Authentication Failed

**Symptom:** "NotebookLM authentication failed" or "Drive OAuth failed"

**Quick Fix:**
1. Click "Authenticate" button again in dashboard
2. Use **Chrome browser** (Safari not supported)
3. Verify Google account has NotebookLM access
4. Check credentials file exists: `ls -la ~/.notebooklm/credentials.json`

**See:** [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md#authentication-issues)

---

### Workflow Stuck or Slow

**Symptom:** Progress bar frozen, no log updates for 2+ minutes

**Quick Fix:**
1. Check live logs in dashboard for specific error
2. Verify Google Drive folder URL is correct and accessible
3. Check internet connection speed
4. Wait 2-3 minutes - some phases have normal delays (API processing)
5. If truly stuck (5+ min no movement), refresh dashboard

**See:** [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md#workflow-issues)

---

### Low Quality Score (< 6.0)

**Symptom:** Quality score below 6.0 in `Quality_Score.json`

**Quick Fix:**
1. Ensure Drive folder has 5+ substantive PDFs (not just brochures)
2. Try **Deep Mode** for more comprehensive analysis
3. Verify industry and subsegments are accurate
4. Check NotebookLM imported at least 20+ sources (view logs)
5. Re-run workflow - first run sometimes lower quality

**See:** [USER_GUIDE.md](Docs/USER_GUIDE.md#quality-optimization)

---

## 💡 Tips for Best Results

### Document Preparation

✅ **Do:**
- Upload 5-15 PDFs per client (sweet spot for quality)
- Include: Annual reports, 10-Ks, white papers, case studies, earnings transcripts
- Ensure PDFs are text-searchable (not scanned images)

❌ **Avoid:**
- Marketing brochures (low information density)
- Single-page PDFs or press releases
- Files > 50 MB (split large documents)
- Scanned/image-only PDFs (use OCR first)

---

### Industry Configuration

✅ **Do:**
- Let AI auto-detect industry (usually accurate from documents)
- Specify 3-5 specific subsegments (e.g., "oncology, vaccines, rare diseases")
- Balance specificity: not too broad, not too narrow

❌ **Avoid:**
- Too broad: "healthcare" → Better: "pharmaceuticals"
- Too narrow: "Phase 3 oncology clinical trials" → Better: "oncology, clinical trials"

---

### Execution Mode Selection

**Use Fast Mode when:**
- Initial research or exploratory analysis
- Time-sensitive (need results in 15-20 min)
- Running 3+ clients in parallel
- Budget-conscious (fewer API calls)

**Use Deep Mode when:**
- Final deliverables for critical deals
- Comprehensive analysis required
- Quality score < 8.0 in Fast mode
- Single client or max 2 parallel

---

### Parallel Execution

**Recommended:**
- **Fast Mode:** 3-5 clients simultaneously (20 min total)
- **Deep Mode:** 1-2 clients simultaneously (60 min total)

**Maximum:**
- System supports up to 5 parallel clients
- More than 5 may cause resource exhaustion or API throttling

---

## 🚀 Advanced Features

### Custom Prompts

Edit prompt files in repository root:
- `ask_prompt_01.txt` - Industry research query
- `ask_prompt_02.txt` - Competitive landscape query
- `chat_prompt_consolidated_01.txt` through `06.txt` - Analysis prompts

Variables available: `$name`, `$industry`, `$subsegments`, `$persona`

**See:** [USER_GUIDE.md](Docs/USER_GUIDE.md#custom-prompts)

---

### Timing Optimization

Edit `vars.py` to tune execution speed vs quality:

```python
# Faster execution, higher retry rate
TIMINGS = {
    'ask_prompt_delay': (5.0, 8.0),   # Reduce delays
    'chat_prompt_delay': (3.0, 5.0),
}

# Slower execution, lower retry rate  
TIMINGS = {
    'ask_prompt_delay': (12.0, 18.0), # Increase delays
    'chat_prompt_delay': (8.0, 12.0),
}
```

**See:** [USER_GUIDE.md](Docs/USER_GUIDE.md#performance-tuning)

---

### Container Deployment

For production environments:

```bash
# Pull container
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1

# Run workflow
./ape-run.sh --vars ./vars.py --clients acme_corp --mode fast
```

**See:** [INSTALLATION.md](Docs/INSTALLATION.md#container-deployment)

---

<div align="center">
  
  **Ready to automate your account research?**
  
  ---
  
  [📖 Full Documentation](README.md) | [🐛 Report Issues](https://github.com/jasoande/Project-APE-dev/issues) | [💡 Feature Requests](https://github.com/jasoande/Project-APE-dev/discussions)
  
  **Questions?** See [TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) or [open an issue](https://github.com/jasoande/Project-APE-dev/issues)
  
  ---
  
  Made with ☕ by Jason Anderson | Version 4.0.1 | July 2026
  
</div>
