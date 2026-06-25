# Project APE v3.0.4 - Testing Guide

![King Kong Logo](dashboard/static/kingkong.png)

**Project Owner & Maintainer:** Jason Anderson  
**Version:** 3.0.4  
**Date:** 2026-06-12  

---

## 🔍 Recent Test Analysis

### Test Failure Investigation

**Reported Issue:** "Last run failed almost immediately"

**Root Cause Found:**
- Old container image (pre-v3.0.4) was being used
- Container had pypdf import error due to incorrect Python path
- Error: `ModuleNotFoundError: No module named 'pypdf'`

**Resolution:**
- v3.0.4 container fixes the Python path issue
- Container now uses explicit `/opt/venv/bin/python3`
- **All import errors resolved**

**Validation:**
- ✅ Container builds successfully
- ✅ Python imports work (pypdf, notebooklm-py, etc.)
- ✅ Pipeline starts correctly
- ✅ Only blocks on NotebookLM authentication (expected)

---

## ✅ Pre-Test Checklist

Before running Project APE, ensure:

### 1. NotebookLM Authentication

```bash
# Check authentication status
notebooklm whoami

# If not authenticated, login:
notebooklm login

# Follow the browser prompts to authenticate with Google
```

### 2. Client Data Preparation

Ensure your client data is in the correct location:

```bash
# For containerized version, data should be in:
./client_data/[Client_Name]/

# Example structure:
client_data/
├── Merck/
│   ├── document1.pdf
│   ├── presentation.pptx
│   └── overview.docx
├── Blue_Yonder/
│   └── files...
└── Hershey/
    └── files...
```

### 3. Configuration File

Verify your `container-vars.py` matches your clients:

```python
clients = [
    "merck_test",
    "blue_yonder_test",
    # ... other clients
]

merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_subsegments = "oncology, vaccines, rare diseases"
merck_test_folder = "/app/client_data/Merck"
```

---

## 🚀 Running Tests

### Single Client Test (Recommended First)

```bash
# Test with one client to validate everything works
./ape-run.sh --mode fast --clients merck_test

# Expected output:
# - Container starts
# - Dashboard opens at http://localhost:8765
# - Pipeline runs for 15-20 minutes
# - PDF consolidation, research, chat prompts execute
# - Mind map generated
# - Pipeline completes successfully
```

### Multi-Client Test

```bash
# Run all 6 clients
./ape-run.sh --mode fast --clients merck_test,blue_yonder_test,organon_test,panasonic_avionics_test,hershey_test,lord_abbett_test

# Expected runtime: ~21-22 minutes (down from 28:09 baseline)
```

### Deep Research Mode

```bash
# For comprehensive analysis (slower but more thorough)
./ape-run.sh --mode deep --clients merck_test

# Expected runtime: 30-90 minutes per client
```

---

## 📊 Monitoring Test Progress

### Dashboard

Open http://localhost:8765 in your browser to see:
- Real-time status for each client
- Progress bars showing completion %
- Current phase (PDF, Research, Chat, Mind Map)
- Quality scores upon completion

### Logs

```bash
# Monitor all clients
tail -f logs/*.log

# Monitor specific client
tail -f logs/merck_test.log

# Check for errors
grep -i "error\|failed" logs/*.log
```

---

## 🎯 Success Criteria

### For Single Client Test:

1. **Container Starts Successfully**
   - No import errors
   - Dashboard launches
   - Authentication succeeds

2. **Pipeline Phases Complete:**
   - ✅ PDF Consolidation (~2 minutes)
   - ✅ Research Prompts (~3-4 minutes)
   - ✅ Chat Prompts (~8-10 minutes with 6 consolidated prompts)
   - ✅ Mind Map Generation (~30 seconds)

3. **Output Generated:**
   - `[Client]-One.pdf` in logs directory
   - NotebookLM notebook created
   - 6 chat prompt notes generated
   - Mind map artifact created
   - Quality score displayed

4. **Runtime:**
   - Fast mode: 15-20 minutes per client
   - Expected for 6 clients: ~21-22 minutes (parallel execution)

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pypdf'"

**Cause:** Using old container image  
**Solution:**
```bash
# Pull latest container
podman pull quay.io/jasoande/project_ape/project-ape:v3.0.4

# Or rebuild locally
podman build -t project-ape:v3.0.4 .

# Verify it's using the correct image
podman images | grep project-ape
# Look for image created recently (within last hour)
```

### Issue: "❌ Not authenticated"

**Cause:** NotebookLM credentials not set up  
**Solution:**
```bash
# Login to NotebookLM
notebooklm login

# Verify authentication
notebooklm whoami
```

### Issue: "No files to consolidate"

**Cause:** Client data folder is empty or path is incorrect  
**Solution:**
```bash
# Check client data exists
ls -la client_data/Merck/

# Verify vars.py configuration
grep "merck_test_folder" container-vars.py
# Should show: merck_test_folder = "/app/client_data/Merck"
```

### Issue: Rate limit errors

**Cause:** Too many concurrent API calls  
**Solution:**
```bash
# Reduce number of parallel clients
./ape-run.sh --mode fast --clients merck_test,blue_yonder_test

# Or use deep mode with longer delays
./ape-run.sh --mode deep --clients merck_test
```

---

## 📈 Performance Validation

### v3.0.4 Performance Targets:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Single client (fast) | 15-20 min | Check dashboard or logs |
| 6 clients (fast) | ~21-22 min | Total pipeline duration |
| Chat prompts executed | 6 (not 12) | `grep "Running.*chat prompts" logs/*.log` |
| Chat API savings | ~6 minutes | Compare to baseline 28:09 |

### Measuring Runtime:

```bash
# Start time is logged at the beginning
grep "Started:" logs/merck_test.log

# Completion time
grep "Pipeline completed" logs/merck_test.log

# Calculate duration or check dashboard
```

---

## 🔍 Verifying Optimizations

### Check Chat Prompts Used:

```bash
# Should show "Running 6 chat prompts" (not 12)
grep "Running.*chat prompts" logs/*.log

# Verify consolidated prompts executed
grep "chat_prompt_consolidated" logs/*.log | wc -l
# Should show 6 per client
```

### Check Timing Improvements:

```bash
# Compare delay timings
grep "delay\|jitter" logs/*.log

# Should see:
# - Anti-collision jitter: 1-3s (or 5-15s for first)
# - Minimal delays: 2-3s between prompts
```

---

## 📝 Test Report Template

After completing your test, document the results:

```markdown
## Test Results - Project APE v3.0.4

**Date:** YYYY-MM-DD
**Tester:** Jason Anderson
**Clients Tested:** [list]
**Mode:** fast / deep

### Results:

**Runtime:**
- Expected: [time]
- Actual: [time]
- Improvement: [% vs baseline]

**Success Rate:**
- Clients successful: X/Y
- Clients failed: X/Y

**Issues Encountered:**
- [None] or [describe]

**Output Quality:**
- ✅ / ❌ PDFs generated
- ✅ / ❌ Notebooks created
- ✅ / ❌ Chat prompts complete
- ✅ / ❌ Mind maps generated

**Performance:**
- Chat prompts used: 6 or 12?
- API latency: reasonable or slow?
- Rate limits hit: yes/no

**Recommendation:**
- ✅ Ready for production
- ⚠️ Needs adjustments (describe)
```

---

## 🎓 Understanding the Pipeline

### Phase 1: PDF Consolidation (~2 minutes)
- Scans client data folder
- Converts Office documents to PDF (LibreOffice)
- Merges all PDFs into single file
- Output: `[Client]-One.pdf`

### Phase 2: Research Prompts (~3-4 minutes)
- Uploads consolidated PDF to NotebookLM
- Runs 2 research prompts
- Imports web sources (10-20 per prompt)
- Deduplicates sources

### Phase 3: Chat Prompts (~8-10 minutes)
- **6 consolidated strategic prompts** (v3.0.4)
  1. Industry Analysis & Customer Profile
  2. Innovation Assessment & Executive Summary
  3. Technology Partners & Value Propositions
  4. Strategic Ideas & HMW Statements
  5. Account Team & Partner Onboarding
  6. Comprehensive Account Plan
- Each saved as NotebookLM note
- Anti-collision jitter prevents rate limits

### Phase 4: Mind Map Generation (~30 seconds)
- Generates visual mind map
- Saved as artifact in NotebookLM

---

## 🔐 Security Notes

### Credentials Management:
- Never commit `vars.py` to git (gitignored)
- NotebookLM credentials stored in volume: `project-ape-credentials`
- Client data excluded from git (gitignored)

### Container Security:
- Runs as non-root user (apeuser, UID 1000)
- Based on Red Hat UBI 9 (minimal attack surface)
- No hardcoded credentials
- Health checks enabled

---

## 📞 Getting Help

### Issues During Testing:

1. **Check logs first:**
   ```bash
   grep -i "error\|exception\|failed" logs/*.log
   ```

2. **Verify container:**
   ```bash
   podman logs [container-name]
   ```

3. **Check authentication:**
   ```bash
   notebooklm whoami
   ```

### Contact:
- **Project Owner:** Jason Anderson
- **Repository:** https://github.com/jasoande/Project-APE
- **Documentation:** See README.md, QUICKSTART.md, CONTAINER_GUIDE.md

---

## ✅ Post-Test Actions

After successful test:

1. **Document Results**
   - Update test report
   - Note any issues or improvements needed

2. **Validate Outputs**
   - Review generated PDFs
   - Check NotebookLM notebooks
   - Verify mind maps

3. **Performance Analysis**
   - Compare runtime to baseline
   - Verify 6 prompts used (not 12)
   - Confirm no rate limit errors

4. **Production Readiness**
   - If test successful: Ready for team use
   - If issues found: Report and re-test after fixes

---

**Ready to test!** Run `./ape-run.sh --mode fast --clients merck_test` to start.

---

**Version 3.0.4 - Optimized & Validated**
