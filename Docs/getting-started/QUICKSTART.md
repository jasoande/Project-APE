# Quick Start — 5-Minute Tutorial

Get your first account intelligence report in under 5 minutes.

---

## What You'll Do

1. ✅ Launch the application (30 seconds)
2. ✅ Authenticate with NotebookLM (1 minute)
3. ✅ Add your first client (1 minute)
4. ✅ Launch a workflow (30 seconds)
5. ✅ Review your results (15-20 minutes later)

**Total active time:** ~3 minutes  
**Total wait time:** 15-20 minutes (fast mode)

---

## Prerequisites

- Python 3.11+ installed ([Installation Guide](INSTALLATION.md))
- Google Account with NotebookLM access
- 2-5 client PDFs ready (or a Google Drive folder URL)

---

## Step 1: Launch (30 seconds)

**Double-click method:**

<table>
<tr>
<th>Platform</th>
<th>File to Double-Click</th>
</tr>
<tr>
<td>macOS</td>
<td><code>launch-project-ape.command</code></td>
</tr>
<tr>
<td>Linux</td>
<td><code>launch-project-ape.py</code></td>
</tr>
<tr>
<td>Windows</td>
<td><code>launch-project-ape.bat</code></td>
</tr>
</table>

**Terminal method:**

```bash
cd Project-APE
python3 launch-project-ape.py
```

**What happens:**
- Creates virtual environment (first run only, ~30 seconds)
- Installs dependencies (first run only, ~60 seconds)
- Starts dashboard server
- Opens browser to http://localhost:8765/configure

**You should see:**

```
📊 Dashboard server starting...
   URL: http://localhost:8765
   Refresh: Every 2 seconds
   ...
   Using Waitress WSGI server (production-grade)
   Max threads: 200
```

Browser opens automatically showing the configuration wizard.

---

## Step 2: Authenticate NotebookLM (1 minute)

In the web UI you'll see a **3-step wizard**:

### Step 2a: NotebookLM Auth

1. Click **"Authenticate NotebookLM"** button
2. Chrome opens to Google sign-in page
3. Sign in with your Google account
4. Click **"Allow"** when prompted
5. ✅ Green checkmark appears when complete

**What's happening:**
- OAuth2 flow generates `~/.notebooklm/credentials.json`
- Valid for 30 days
- Used by `notebooklm` CLI to access your notebooks

**Troubleshooting:**
- **"Popup blocked"?** Check your browser's popup settings, whitelist `localhost:8765`
- **"Chrome not found"?** Install Chrome or run `notebooklm login` in terminal
- **"Sign-in error"?** Make sure you have NotebookLM access at [notebooklm.google.com](https://notebooklm.google.com)

---

## Step 3: Add Your First Client (1 minute)

### Option A: Use Google Drive Folder (Recommended)

**If you have client docs in Google Drive:**

1. Open Google Drive in another tab
2. Navigate to your client folder
3. Click **"Share"** → **"Copy link"**
4. Paste URL in web UI

**Example:**
```
Name: Acme Corporation
Client ID: acme_corp (auto-generated)
Drive Folder URL: https://drive.google.com/drive/folders/1ABC123xyz
Industry: technology
Subsegments: cloud computing, AI, cybersecurity
Mode: Fast
```

5. Click **"Add Client"**
6. ✅ Green checkmark when validation passes

### Option B: Use Local PDF Files

**If you have PDFs on your computer:**

1. Create a folder in `client_data/`:
   ```bash
   mkdir -p client_data/acme_corp
   ```

2. Copy your PDFs:
   ```bash
   cp ~/Downloads/acme-*.pdf client_data/acme_corp/
   ```

3. In web UI:
   ```
   Name: Acme Corporation
   Client ID: acme_corp
   Local Folder: client_data/acme_corp
   Industry: technology
   Subsegments: cloud computing, AI, cybersecurity
   Mode: Fast
   ```

4. Click **"Add Client"**

---

## Step 4: Launch Workflow (30 seconds)

1. Click **"Save Configuration"** button
2. Click **"Launch Workflow"** button
3. Dashboard redirects to status page
4. ✅ Watch real-time progress

**You should see:**

```
📊 ACCOUNT INTELLIGENCE ENGINE — Live Status

Client: Acme Corporation
Status: RUNNING
Mode: FAST
Progress: ████████░░░░░░░░░░ 40%

Pipeline Stages:
✅ Download    (complete)
✅ Notebook    (complete)
🔄 Research    (in progress...)
⏳ Analysis    (pending)
⏳ Complete    (pending)

Log Stream:
18:56:24 | INFO | [acme_corp] Running research: ask_prompt_01.txt (fast mode)
18:56:30 | INFO | [acme_corp] ✅ Research complete: 15 sources imported
```

---

## Step 5: Review Results (after 15-20 minutes)

### When Complete

**Dashboard shows:**
```
Status: COMPLETE ✅
Quality Score: 8.5/10.0
Duration: 18m 32s
```

### Output Files

Navigate to `docs_generated/acme_corp/`:

```
docs_generated/acme_corp/
├── Acme_Corporation_Account_Plan.txt      # Main analysis (12-15 pages)
├── Quality_Score.json                      # Quality assessment
├── Summary.txt                             # Quick overview + NotebookLM link
└── Acme Corporation-Consolidated-*.pdf    # Source document
```

### Open in NotebookLM

1. Click the **NotebookLM link** in `Summary.txt`
2. Opens your notebook with all sources and research loaded
3. You can now:
   - Ask follow-up questions
   - Generate additional insights
   - Export to PDF or Google Docs
   - Share with your team

### Review Quality Score

**`Quality_Score.json` example:**

```json
{
  "overall_score": 8.5,
  "dimension_scores": {
    "industry_overview": 9.0,
    "swot_analysis": 8.0,
    "technology_landscape": 9.5,
    "competitive_positioning": 8.0,
    "pain_points": 8.0,
    "recommendations": 8.5
  },
  "analysis_timestamp": "2026-07-09T19:15:42Z"
}
```

**What the scores mean:**
- **9.0-10.0:** Excellent, comprehensive coverage
- **7.0-8.9:** Good, minor gaps
- **5.0-6.9:** Adequate, noticeable gaps
- **< 5.0:** Incomplete, re-run recommended

---

## Next Steps

### Run More Clients

1. Click **"Back to Configure"** in dashboard
2. Add more clients using the wizard
3. Launch multiple clients simultaneously (up to 5)

### Try Deep Mode

Deep mode provides 8-9x more external sources (45-90 sources per research query vs 10-25 in fast mode).

**When to use deep mode:**
- Strategic accounts (> $500K opportunity)
- Competitive bid situations
- Complex industries (healthcare, finance, government)
- When fast mode quality score < 7.0

**Example:**
```
Client ID: acme_corp_deep
Name: Acme Corporation (Deep Analysis)
Mode: Deep  ← Select this
```

**Duration:** 45-60 minutes (vs 15-20 minutes fast mode)

### Customize Prompts

Edit the research and analysis prompts to match your use case:

**Research prompts** (`ask_prompt_01.txt`, `ask_prompt_02.txt`):
- Control what external sources are imported
- Industry-specific research angles

**Analysis prompts** (`chat_prompt_consolidated_01.txt` through `06.txt`):
- Customize the final analysis structure
- Add your company's methodology
- Include specific frameworks (MEDDIC, BANT, etc.)

See [Prompt Engineering Guide](../reference/PROMPTS.md) for details.

### Integrate with Your Workflow

**Export to CRM:**
```bash
# Copy analysis to Salesforce opportunity
cp docs_generated/acme_corp/Acme_Corporation_Account_Plan.txt \
   ~/Salesforce/Opportunities/Acme-2026-Q3.txt
```

**Share with Team:**
```bash
# Send NotebookLM link via Slack
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Account plan ready for Acme Corp",
    "blocks": [{
      "type": "section",
      "text": {"type": "mrkdwn", "text": "*Acme Corporation Analysis*\n✅ Quality Score: 8.5/10\n<notebooklm-link|View in NotebookLM>"}
    }]
  }'
```

---

## Common First-Run Issues

### "No PDFs found in folder"

**Solution:** Make sure your folder contains at least one `.pdf` file:
```bash
ls -lh client_data/acme_corp/*.pdf
```

### "Drive folder is empty"

**Solution:** Check folder permissions in Google Drive:
- Folder must be shared with you
- You need at least "Viewer" access
- Folder must contain files (not just subfolders)

### "Quality score is low (< 5.0)"

**Possible causes:**
- Not enough source documents (< 3 PDFs)
- PDFs are too short (< 5 pages each)
- PDFs contain scanned images (not searchable text)
- Industry/subsegments not specified (left blank)

**Solutions:**
- Add more source documents
- Provide industry and subsegments explicitly
- Run in deep mode for more external research
- OCR scanned PDFs before uploading

### "Workflow stuck at 'Research' phase"

**Solution:** Check logs for quota errors:
```bash
tail -f logs/acme_corp.log
# Look for "quota exceeded" or "rate limit"
```

If you see quota errors, the system will automatically retry with exponential backoff. This is normal in deep mode (~30% retry rate is acceptable).

---

## What's Next?

You've completed your first workflow! Here's where to go from here:

**For End Users:**
- 📖 [Web UI Guide](../user-guide/WEB_UI.md) — Master the dashboard
- 📖 [Understanding Results](../user-guide/RESULTS.md) — Interpret output quality scores
- 📖 [Google Drive Integration](../user-guide/DRIVE_INTEGRATION.md) — Advanced Drive features

**For Administrators:**
- 📖 [Configuration Reference](../admin-guide/CONFIGURATION.md) — Full vars.py options
- 📖 [Deployment Guide](../admin-guide/DEPLOYMENT.md) — Container production setup
- 📖 [Monitoring Guide](../admin-guide/MONITORING.md) — Health checks and alerting

**For Developers:**
- 📖 [Architecture Overview](../developer-guide/ARCHITECTURE.md) — System internals
- 📖 [Contributing Guide](../developer-guide/CONTRIBUTING.md) — Submit improvements
- 📖 [API Reference](../developer-guide/API_REFERENCE.md) — Extend the platform

---

<div align="center">
  
**🎉 Congratulations!**

You've successfully generated your first AI-powered account intelligence report.

[⬅ Back to README](../../README.md) • [➡ First Workflow Guide](FIRST_WORKFLOW.md)

</div>
