# Project APE - Quick Start Guide

**Get up and running in 30 minutes**

## Prerequisites Checklist

- [ ] macOS or Linux system
- [ ] Google account with NotebookLM access
- [ ] 10GB free disk space
- [ ] Terminal/command line access

---

## 5-Minute Setup

### 1. Install Dependencies (5 min)

**macOS:**
```bash
# Install Podman
brew install podman

# Install Google Cloud SDK
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
# Install Podman
sudo apt-get update && sudo apt-get install -y podman

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
```

### 2. Clone & Setup (10 min)

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Run automated setup
./setup.sh
```

This installs:
- Python virtual environment
- NotebookLM CLI
- Required Python packages
- Authenticates with Google

### 3. Configure Google Drive (10 min)

**Choose OAuth (easier):**

```bash
# Step 1: Create OAuth credentials
# Go to: https://console.cloud.google.com/apis/credentials
# Create Credentials → OAuth client ID → Desktop app
# Download JSON file

# Step 2: Save credentials
mkdir -p ~/.project-ape
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json

# Step 3: Authenticate
python3 setup-oauth-drive.py
# Browser opens → Sign in → Grant permissions → Done!
```

**Or Service Account (production):**

```bash
# Automated creation
./create-service-account.sh

# Then share Drive folders with:
# project-ape-service@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

### 4. Configure Clients (5 min)

**Option A: Web UI (Recommended)**

```bash
# Double-click: launch-project-ape.command
# Or run:
source ~/.project-ape-venv/bin/activate
python3 dashboard/server.py

# Open browser: http://localhost:8765/configure
# Add clients → Fill form → Save & Launch
```

**Option B: Manual**

```bash
# Copy template
cp example-vars.py vars.py

# Edit with your favorite editor
nano vars.py  # or vim, code, etc.
```

Minimal configuration:
```python
clients = ["acme_corp"]

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/YOUR-FOLDER-ID"
acme_corp_industry = ""  # Auto-detect
acme_corp_subsegments = ""  # Auto-detect

persona = "solutions architect"
default_mode = "fast"
```

---

## Launch Your First Workflow

```bash
# Fast mode (15-20 minutes)
./launch_ape.sh fast

# Dashboard opens automatically at:
# http://localhost:8765
```

That's it! Monitor progress in the dashboard.

---

## What Happens Next

1. **Container starts** - Downloads Docker image (first time only)
2. **Dashboard opens** - Real-time progress at http://localhost:8765
3. **Files download** - From Google Drive folders
4. **NotebookLM creates** - New notebook per client
5. **Sources upload** - PDFs, docs, etc.
6. **Research runs** - AI-powered analysis
7. **Results ready** - Click NotebookLM links in dashboard
8. **Auto-shutdown** - Container stops after 5 minutes

---

## First Run Checklist

- [ ] Dashboard opens in browser
- [ ] Client cards appear showing progress
- [ ] Progress bars update in real-time
- [ ] Quality score appears when complete
- [ ] NotebookLM link is clickable
- [ ] Logs section shows activity

---

## Common First-Run Issues

### Issue: "NotebookLM authentication expired"

**Fix:**
```bash
notebooklm auth refresh
```

### Issue: "Drive folder not accessible"

**OAuth:**
```bash
python3 setup-oauth-drive.py
```

**Service Account:**
```
Share folder with: project-ape-service@YOUR-PROJECT.iam.gserviceaccount.com
```

### Issue: "Container won't start"

**Fix:**
```bash
# Initialize Podman machine (macOS only)
podman machine init
podman machine start
```

### Issue: "Port 8765 already in use"

**Fix:**
```bash
# Find and kill process
lsof -i :8765
kill -9 <PID>

# Or change port in vars.py
DASHBOARD_PORT = 8766
```

---

## Next Steps

### Optimize Your Configuration

**Adjust timing for your needs:**

Fast mode (speed-focused):
```python
TIMINGS = {
    'source_processing_delay': 20.0,  # Faster
    'ask_prompt_delay': (5.0, 8.0),   # Faster
}
```

Deep mode (quality-focused):
```python
DEEP_TIMINGS = {
    'source_processing_delay': 60.0,  # More thorough
    'ask_prompt_delay': (20.0, 30.0), # More thorough
}
```

### Enable Gemini AI Features

```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key"

# Or add to .env file
echo "GEMINI_API_KEY=your-api-key" >> .env
```

Enable in vars.py:
```python
GEMINI_AGENT_CONFIG = {
    'enabled': True,
    'enable_error_analysis': True,
    'enable_quality_validation': True,
}
```

### Process Multiple Clients

```python
clients = [
    "acme_corp",
    "techstart_inc",
    "globalbank_llc",
]

# Add configuration for each:
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/..."

techstart_inc_name = "TechStart Inc"
techstart_inc_folder = "https://drive.google.com/..."
```

Run all in parallel:
```bash
./launch_ape.sh fast
```

---

## Useful Commands

```bash
# View logs in real-time
tail -f logs/overall.log

# Check container status
podman ps -a

# Stop container manually
podman stop project-ape

# Force refresh Drive cache
./launch_ape.sh fast --refresh

# Run specific clients only
./launch_ape.sh fast acme_corp techstart_inc

# Deep mode (slower, higher quality)
./launch_ape.sh deep
```

---

## Getting Help

1. **Check logs first:**
   ```bash
   tail -f logs/overall.log
   ```

2. **Review troubleshooting guide:**
   - See `Docs/TROUBLESHOOTING.md`

3. **Verify authentication:**
   ```bash
   notebooklm auth check
   python3 verify-drive-access.py
   ```

4. **Ask for help:**
   - GitHub Issues: https://github.com/yourusername/project-ape/issues
   - Include: error message, log snippet, system info

---

## Success Indicators

✅ **Everything is working when you see:**

1. Dashboard loads at http://localhost:8765
2. Client cards show progress bars
3. Progress updates every 2 seconds
4. Quality score appears (e.g., "8.5/10")
5. "COMPLETE" status with green color
6. NotebookLM link opens successfully
7. Logs show no errors

---

## Performance Tips

### Speed Up Execution

1. **Use Fast Mode** for initial research
2. **Enable caching** (7-day TTL):
   ```python
   DRIVE_CONFIG = {
       'cache_enabled': True,
       'cache_ttl_hours': 168,
   }
   ```
3. **Limit file size**:
   ```python
   DRIVE_CONFIG = {
       'max_file_size_mb': 25,  # Skip large files
   }
   ```
4. **Disable recursive** folder downloads:
   ```python
   DRIVE_CONFIG = {
       'recursive': False,
   }
   ```

### Improve Quality

1. **Use Deep Mode** for important accounts
2. **Increase processing delays**:
   ```python
   DEEP_TIMINGS = {
       'source_processing_delay': 60.0,
   }
   ```
3. **Enable Gemini AI**:
   ```python
   GEMINI_AGENT_CONFIG = {
       'enabled': True,
   }
   ```
4. **Set quality target**:
   ```python
   GEMINI_AGENT_CONFIG = {
       'quality_target': 9.0,
   }
   ```

---

## Ready to Learn More?

- **Full Documentation**: See `README.md`
- **Web Configuration**: See `Docs/WEB_CONFIGURATION_GUIDE.md`
- **Troubleshooting**: See `Docs/TROUBLESHOOTING.md`
- **Architecture**: See README.md → Architecture Details

---

**Questions?** Open an issue on GitHub or check existing discussions.

**Version**: 3.2.0  
**Last Updated**: June 25, 2026
