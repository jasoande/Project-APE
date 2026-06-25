# Quick Start Guide - Web UI First

**Get up and running in 15 minutes using only your browser**

---

## Prerequisites (One-Time Setup)

**You only need:**
- macOS or Linux system
- Google account
- 10 minutes

**No technical experience required!** Everything happens in your browser.

---

## Step 1: Launch the Dashboard (30 seconds)

### Option A: Double-Click Launcher (Recommended)

1. Navigate to your `project-ape` folder
2. **Double-click** `launch-project-ape.command` (macOS)
3. Browser automatically opens to `http://localhost:8765/configure`

### Option B: Manual Browser Access

If already running, just open your browser and navigate to:

```
http://localhost:8765/configure
```

**What you see:**
- Configuration page with setup wizard
- Green/red status indicators
- "Setup Environment" button

![Configuration Page](docs/screenshots/configure-page.png)

---

## Step 2: Setup Environment (2-5 minutes)

**Automated installation - just click and wait!**

1. Click the **"Setup Environment"** button
2. Watch the progress indicator:
   - ⏳ Creating Python virtual environment...
   - ⏳ Installing NotebookLM CLI...
   - ⏳ Installing dependencies...
   - ✅ **Environment Ready!**

**What's happening behind the scenes:**
- Python virtual environment created in `~/.project-ape-venv`
- NotebookLM CLI installed automatically
- All required Python packages installed
- No manual terminal commands needed!

**Success indicator:** Green checkmark ✅ next to "Environment Setup"

![Setup Environment](docs/screenshots/setup-environment.png)

**Time required:** 2-5 minutes depending on internet speed

---

## Step 3: Authenticate NotebookLM (1 minute)

**One-click authentication with Google**

1. Click **"Login to NotebookLM"** button
2. New browser tab opens → Google sign-in page
3. Sign in with your Google account
4. Click **"Allow"** when asked for NotebookLM permissions
5. Browser returns to dashboard
6. ✅ **Status shows "Authenticated"**

**What permissions are requested:**
- Read and write access to your NotebookLM notebooks
- Create new notebooks on your behalf
- This is required for Project APE to work

**Success indicator:** Green checkmark ✅ next to "NotebookLM Status"

![Auth Status](docs/screenshots/auth-status.png)

**Troubleshooting:**
- If authentication fails, click the button again
- Make sure you're signed into the correct Google account
- Clear browser cache if needed (Cmd+Shift+R)

---

## Step 4: Setup Google Drive Access (5 minutes, one-time)

**Interactive wizard walks you through OAuth setup**

### Why OAuth?
- Easier setup (no manual folder sharing)
- Uses your personal Google account
- Secure browser-based authentication
- Automatically accesses your Drive folders

### The 5-Step Wizard

Click **"Google Drive Setup"** to launch the wizard:

#### Step 1: Create Google Cloud Project

**In the wizard:**
1. Click **"Open Google Cloud Console"**
2. New tab opens to Google Cloud
3. Click **"Create Project"**
4. Name: `Project-APE` (or anything you like)
5. Click **"Create"**
6. Return to Project APE wizard
7. Click **"Next"**

**Time:** 1 minute

#### Step 2: Enable Google Drive API

**In the wizard:**
1. Click **"Enable Drive API"**
2. New tab opens to API Library
3. Search for "Google Drive API"
4. Click on it → Click **"Enable"**
5. Wait for confirmation (5-10 seconds)
6. Return to wizard → Click **"Next"**

**Time:** 1 minute

#### Step 3: Configure OAuth Consent Screen

**In the wizard:**
1. Click **"Configure OAuth"**
2. New tab opens to OAuth consent screen
3. Select **"External"** (unless you have Google Workspace)
4. Click **"Create"**
5. Fill in required fields:
   - **App name:** `Project-APE`
   - **User support email:** Your email
   - **Developer contact:** Your email
6. Click **"Save and Continue"**
7. Click **"Add or Remove Scopes"**
8. Add: `.../auth/drive.readonly`
9. Click **"Save and Continue"** (twice)
10. Return to wizard → Click **"Next"**

**Time:** 2 minutes

#### Step 4: Create OAuth Client ID

**In the wizard:**
1. Click **"Create OAuth Credentials"**
2. New tab: APIs & Services → Credentials
3. Click **"+ Create Credentials"** → **"OAuth client ID"**
4. Application type: **"Desktop app"**
5. Name: `Project-APE Desktop`
6. Click **"Create"**
7. Download JSON button appears → **Click it**
8. Save file to Downloads folder
9. Return to wizard → Click **"Next"**

**Time:** 1 minute

![OAuth Wizard](docs/screenshots/oauth-wizard.png)

#### Step 5: Upload and Authenticate

**In the wizard:**
1. Click **"Choose File"** or drag-and-drop
2. Select the JSON file you just downloaded
3. File uploads automatically
4. Click **"Authenticate"**
5. Browser opens → Google sign-in
6. Sign in → Grant Drive permissions
7. Allow read-only access to Drive
8. Browser returns → ✅ **"Drive Connected"**

**Time:** 1 minute

**Success indicator:** Green checkmark ✅ next to "Google Drive Status"

### What This Enables

✅ Automatic access to your Google Drive folders  
✅ Download client documents without manual sharing  
✅ Works with folders you own or have access to  
✅ Secure, token-based authentication (expires after 7 days of inactivity)  

**You never need to repeat this setup!** Token refreshes automatically.

---

## Step 5: Configure Your Clients (3 minutes)

**Simple web form - no coding required**

### Add Your First Client

In the configuration form:

1. **Client Name:**
   ```
   Acme Corporation
   ```

2. **Google Drive Folder URL:**
   - Go to Google Drive in another tab
   - Navigate to your client's folder
   - Copy the URL from address bar
   - Paste into form:
   ```
   https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J
   ```

3. **Industry (Optional):**
   - Leave blank for auto-detection
   - Or specify: `technology`, `healthcare`, `finance`, etc.
   ```
   
   ```

4. **Subsegments (Optional):**
   - Leave blank for auto-detection
   - Or list key areas:
   ```
   cloud computing, cybersecurity, AI/ML
   ```

5. Click **"➕ Add Client"**

### Add More Clients (Optional)

Repeat the process for additional clients:
- Click **"➕ Add Client"** for each one
- Fill in the same 4 fields
- No limit on number of clients

**Example multi-client setup:**
```
Client 1: Acme Corporation (technology)
Client 2: HealthTech Inc (healthcare)
Client 3: FinServe LLC (financial services)
```

### Configure Settings

**Persona (Who is the research for?):**
```
Solutions Architect
```
Common options: `Solutions Architect`, `Sales Executive`, `Account Manager`, `Business Development`

**Execution Mode:**
- **Fast Mode**: 15-20 minutes per account (recommended for first run)
- **Deep Mode**: 45-60 minutes per account (more thorough analysis)

Select: **Fast**

**Dashboard Port (Advanced):**
```
8765 (default - don't change unless needed)
```

---

## Step 6: Launch Your First Workflow (1 minute)

**Ready to go? Just one click!**

1. Review your configuration:
   - ✅ Environment setup complete
   - ✅ NotebookLM authenticated
   - ✅ Google Drive connected
   - ✅ At least one client configured

2. Click **"🚀 Start Workflow"** button

3. Dashboard automatically switches to **monitoring view**

**What happens next:**
- All clients process in parallel (simultaneously)
- Real-time progress updates every 2 seconds
- Each client goes through 7 phases:
  1. ⏳ Downloading files from Drive
  2. ⏳ Creating NotebookLM notebook
  3. ⏳ Uploading sources
  4. ⏳ Processing sources
  5. ⏳ Running research prompts
  6. ⏳ Quality validation
  7. ✅ Complete!

**Expected time:**
- **Fast mode:** 15-20 minutes total (all clients in parallel)
- **Deep mode:** 45-60 minutes total (all clients in parallel)

![Dashboard Monitoring](docs/screenshots/dashboard-monitoring.png)

---

## What Success Looks Like

### Dashboard Indicators

**Header Section:**
- ⏱ **Execution Timer:** Counts up from 00:00
- 📊 **Progress Bar:** Overall completion percentage
- 📈 **Client Counts:**
  - Total: 3 clients
  - Running: 2 clients
  - Complete: 1 client
  - Failed: 0 clients

**Client Cards:**

Each client shows:
- **Progress bar** (0-100%)
- **Current phase** (e.g., "Uploading sources...")
- **Quality score** when complete (e.g., "8.5/10")
- **Status badge:**
  - 🔵 RUNNING (in progress)
  - 🟢 COMPLETE (finished)
  - 🔴 FAILED (error occurred)
- **NotebookLM link** (clickable when ready)

**Logs Section (Collapsible):**
- Click **"📋 Real-Time Logs"** to expand
- Real-time streaming with auto-scroll
- Color-coded messages:
  - ✅ Green = Success
  - ⚠️ Yellow = Warning
  - ❌ Red = Error
- Controls:
  - ⏸ **Pause** - Stop auto-scroll
  - ▶️ **Resume** - Resume auto-scroll
  - 🗑 **Clear** - Clear log view
  - 📥 **Download** - Save logs to file

### Success Checklist

✅ **Dashboard loads** at `http://localhost:8765`  
✅ **Progress bars update** every 2 seconds  
✅ **No red error messages** in logs  
✅ **Quality scores appear** (e.g., "8.5/10")  
✅ **Status shows "COMPLETE"** with green badge  
✅ **NotebookLM links work** (click to open research)  
✅ **Research content visible** in NotebookLM  

![Completed Workflow](docs/screenshots/completed-workflow.png)

### Access Your Research

When status shows **COMPLETE**:

1. **Click the NotebookLM link** in the client card
2. New tab opens to your NotebookLM notebook
3. **You'll see:**
   - All uploaded sources (PDFs, docs)
   - AI-generated account plan
   - Industry analysis
   - Subsegment breakdown
   - Key insights and recommendations

**What to do with results:**
- Read the AI-generated summary
- Ask follow-up questions in NotebookLM
- Download as PDF or share with team
- Use as basis for customer meetings

---

## Troubleshooting

### Issue: Dashboard Won't Load

**Symptoms:** Browser shows "Connection refused"

**Solution:**
1. Check if launcher is running (look for terminal window)
2. If not: Double-click `launch-project-ape.command` again
3. Wait 10 seconds for server to start
4. Refresh browser

### Issue: Environment Setup Failed

**Symptoms:** Red ❌ next to "Environment Setup"

**Solution:**
1. Click **"Setup Environment"** again
2. Check internet connection
3. If still fails: Check logs (📋 section)

### Issue: NotebookLM Authentication Failed

**Symptoms:** Red ❌ next to "NotebookLM Status"

**Solution:**
1. Click **"Login to NotebookLM"** again
2. Make sure you're using correct Google account
3. Grant all requested permissions
4. Try in different browser if needed

### Issue: Google Drive Access Denied

**Symptoms:** Red ❌ next to "Google Drive Status"

**Solution:**
1. Click **"Google Drive Setup"** to restart wizard
2. Verify you completed all 5 steps
3. Check that Drive API is enabled in Google Cloud Console
4. Re-download OAuth JSON if needed

### Issue: Workflow Stuck or Not Progressing

**Symptoms:** Same progress for 5+ minutes

**Solution:**
1. Click **"📋 Real-Time Logs"** to expand
2. Look for red error messages
3. Common fixes:
   - **"Folder not found"**: Check Drive folder URL
   - **"Auth expired"**: Re-authenticate NotebookLM
   - **"Rate limit"**: Wait 2 minutes and try again
4. Download logs (📥) for detailed analysis

### Issue: Quality Score Low (< 7.0)

**Symptoms:** Complete but score is 6.5 or lower

**Possible causes:**
- Not enough source documents in Drive folder
- Sources still processing (try Deep mode)
- Documents not relevant to account

**Solution:**
1. Add more relevant documents to Drive folder
2. Re-run in Deep mode for better analysis
3. Check NotebookLM for partial results

### Still Having Issues?

1. **Download logs:** Click 📥 in Logs section
2. **Check detailed troubleshooting:** `Docs/TROUBLESHOOTING.md`
3. **Open GitHub issue:** Include logs and screenshots

---

## Next Steps

### Add More Clients

1. Return to configuration: `http://localhost:8765/configure`
2. Click **"➕ Add Client"**
3. Fill in details
4. Click **"🚀 Start Workflow"**

### Try Deep Mode

For more thorough analysis:

1. Go to configuration page
2. Change **Execution Mode** to **Deep**
3. Save and launch
4. Expect 45-60 minutes per account (higher quality)

### Enable Gemini AI (Optional)

For advanced features (error recovery, better quality validation):

1. Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. In Project APE, go to Settings
3. Add API key
4. Enable Gemini features:
   - ✅ Error analysis and recovery
   - ✅ Enhanced quality validation
   - ✅ Industry auto-detection

### Optimize Your Workflow

**Speed up processing:**
- Use Fast mode for quick overviews
- Enable Drive caching (7-day TTL)
- Limit max file size to skip large documents

**Improve quality:**
- Use Deep mode for important accounts
- Add more relevant source documents
- Enable Gemini AI validation
- Set higher quality targets (9.0+)

**Process multiple accounts:**
- Add all clients at once in configuration
- All process in parallel (simultaneously)
- Monitor progress for each in dashboard
- Fast mode: 15-20 min for all clients
- Deep mode: 45-60 min for all clients

---

## Tips for Best Results

### Source Documents

**Best practices:**
- 📄 **10-20 documents** per client (optimal)
- 📊 **Mix of types**: PDFs, presentations, docs
- 🎯 **Relevant content**: Company info, case studies, industry reports
- 📏 **File size**: Under 25MB per file

**Avoid:**
- ❌ Duplicate documents
- ❌ Irrelevant content
- ❌ Extremely large files (>50MB)
- ❌ Password-protected PDFs

### First Run Recommendations

**For your first workflow:**
1. Start with **one client** (test the system)
2. Use **Fast mode** (see results quickly)
3. Pick client with **10-15 source documents**
4. Watch the dashboard (learn the workflow)
5. Review results in NotebookLM
6. Then scale to multiple clients

**For production use:**
1. Add all clients at once
2. Use **Deep mode** for high-value accounts
3. Enable Gemini AI for best quality
4. Set quality target to 8.5+
5. Process regularly (weekly/monthly)

---

## Summary

**What you've accomplished:**

✅ Launched Project APE dashboard  
✅ Completed automated environment setup  
✅ Authenticated with NotebookLM  
✅ Configured Google Drive OAuth access  
✅ Added your first client(s)  
✅ Launched and monitored a complete workflow  
✅ Generated AI-powered account research  

**Total time:** 15-30 minutes (including setup)

**Next workflow:** 15-20 minutes (Fast) or 45-60 minutes (Deep)

---

## Learn More

- **Full Documentation:** [README.md](README.md)
- **Web Configuration Guide:** [Docs/WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md)
- **Troubleshooting:** [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)
- **Architecture Details:** See README → Architecture section

---

## Get Help

**Questions or issues?**

1. Check [Troubleshooting](Docs/TROUBLESHOOTING.md)
2. Review dashboard logs (📋 section)
3. Open [GitHub Issue](https://github.com/yourusername/project-ape/issues)

**Include in your issue:**
- Screenshot of dashboard
- Downloaded log files
- Description of what you tried

---

**Version:** 3.2.0  
**Last Updated:** June 25, 2026  
**Author:** Jason Anderson

**🎉 Happy researching!**
