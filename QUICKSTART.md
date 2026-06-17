# Project APE - Quick Start Guide

**Get running in 5 minutes** (assuming you have Google service account setup)

---

## Prerequisites

✅ Podman or Docker installed  
✅ Google service account JSON file  
✅ Google Drive folders with client PDFs  
✅ Gemini API key

**Don't have these?** See [GETTING-STARTED.md](GETTING-STARTED.md) for full setup.

---

## 5-Minute Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd Project-APE
```

### 2. Configure Environment
```bash
# Copy and edit .env
cp .env.template .env
nano .env  # Add GEMINI_API_KEY
```

### 3. Configure Clients
```bash
# Copy and edit vars.py
cp example-vars.py vars.py
nano vars.py  # Add Google Drive folder URLs
```

### 4. Place Service Account
```bash
cp ~/path/to/service-account.json ./jasoande-3aec1043e544.json
```

### 5. Run Pipeline
```bash
./launch_ape.sh fast merck_test
```

### 6. Open Dashboard
```
http://localhost:8765
```

---

## That's It!

Project APE will:
- Auto-detect your architecture
- Pull the correct container  
- Download from Google Drive
- Generate research
- Create NotebookLM notebooks

**Time:** 15-20 minutes for fast mode

---

## Quick Reference

### Run All Clients (Fast)
```bash
./launch_ape.sh fast
```

### Run All Clients (Deep)
```bash
./launch_ape.sh deep
```

### Run Specific Clients
```bash
./launch_ape.sh fast merck_test organon_test
```

### View Logs
```bash
tail -f logs/merck_test.log
```

### Stop Pipeline
```bash
# Press Ctrl+C in terminal
# Or:
podman stop project-ape
```

---

## Troubleshooting

### NotebookLM Auth Required

First time only:
```bash
podman exec -it project-ape bash
notebooklm login
exit
```

Then restart pipeline.

### Can't Pull Image

```bash
podman login quay.io
./launch_ape.sh fast
```

### Drive Access Denied

Verify folder is shared with service account email from your JSON file.

---

**For detailed setup:** [GETTING-STARTED.md](GETTING-STARTED.md)  
**For troubleshooting:** [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)

**All data from Google Drive - no local files needed!**
