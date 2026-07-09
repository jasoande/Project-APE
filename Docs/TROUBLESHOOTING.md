<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="150"/>
  
  # Troubleshooting Guide
  **Account Intelligence - Common Issues & Solutions**
  
  Version 4.0.1
</div>

---

## Table of Contents

1. [Authentication Issues](#authentication-issues)
2. [Container Issues](#container-issues)
3. [Google Drive Issues](#google-drive-issues)
4. [Dashboard Issues](#dashboard-issues)
5. [Workflow Issues](#workflow-issues)
6. [Performance Issues](#performance-issues)
7. [Quality Score Issues](#quality-score-issues)
8. [Quick Fixes](#quick-fixes)
9. [Diagnostic Commands](#diagnostic-commands)
10. [Getting Help](#getting-help)

---

## Authentication Issues

### NotebookLM Token Refresh Failed

**Symptoms:**
```
ERROR | Token refresh failed (400 Bad Request)
ERROR | RPC returned status code 16 (Unauthenticated)
ERROR | [client] Research failed: Token refresh failed
```

**Cause:** NotebookLM session has expired (typically after 7-30 days)

**Solution:**

**Option 1: Re-authenticate on Host (Recommended)**
```bash
# Stop running containers
podman stop $(podman ps -q --filter ancestor=project-ape)

# Re-authenticate
notebooklm login

# Browser opens - sign in with Google account
# Return to terminal - should show "Login successful"

# Restart workflow
./developer-docs/ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

**Option 2: Fresh Credentials**
```bash
# Clear old credentials
rm -rf ~/.notebooklm

# Install CLI if needed
pip install notebooklm

# Fresh login
notebooklm login

# Verify authentication
notebooklm list

# Restart container
./developer-docs/ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

**Option 3: Authenticate Inside Container**
```bash
# Find container name
podman ps | grep project-ape

# Login inside container
podman exec -it <container-name> bash -c "notebooklm login"

# Note: Browser will open for Google sign-in
```

---

### NotebookLM Not Authenticated

**Symptoms:**
```
ERROR | Not authenticated. Login required!
ERROR | No credentials found at ~/.notebooklm/credentials.json
```

**Cause:** NotebookLM credentials missing or never created

**Solution:**
```bash
# Install NotebookLM CLI
pip install notebooklm

# Authenticate
notebooklm login

# Verify credentials exist
ls -la ~/.notebooklm/credentials.json

# Test authentication
notebooklm list
```

**Expected output:** List of your notebooks (may be empty)

---

### Google Drive OAuth Failed

**Symptoms:**
```
ERROR | Drive authentication failed
ERROR | Credentials not found at ~/.project-ape/drive_credentials.json
ERROR | Token has expired and cannot be refreshed
```

**Cause:** Drive OAuth credentials missing, invalid, or expired

**Solution:**

**Step 1: Verify Credentials Exist**
```bash
# Check for credentials
ls -la ~/.project-ape/drive_credentials.json
ls -la ~/.project-ape/drive_token.json
```

**Step 2: Re-run OAuth Setup**
```bash
# Delete old token (if expired)
rm ~/.project-ape/drive_token.json

# Re-run OAuth setup
python3 setup-oauth-drive-improved.py

# Follow prompts to authenticate
```

**Step 3: Verify Permissions**
```bash
# Credentials should be readable
chmod 600 ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_token.json

# Verify ownership
ls -la ~/.project-ape/*.json
```

**Step 4: Test Drive Access**
```bash
# Test Drive API
python3 -c "from core.drive_manager import DriveManager; dm = DriveManager(); print('Drive access: OK')"
```

---

### OAuth Redirect URI Mismatch

**Symptoms:**
```
ERROR | redirect_uri_mismatch
ERROR | The redirect URI in the request did not match a registered redirect URI
```

**Cause:** OAuth client type is not "Desktop app"

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth client ID
3. **Delete it** (if type is "Web application")
4. Create new OAuth credentials:
   - Click "+ Create Credentials" → "OAuth client ID"
   - Application type: **"Desktop app"**
   - Name: `Project-APE-Desktop`
   - Click "Create"
5. Download new `client_secret_*.json`
6. Re-run setup:
   ```bash
   python3 setup-oauth-drive-improved.py
   ```

---

## Container Issues

### Port Already in Use

**Symptoms:**
```
Error: preparing container ... proxy already running
Error: cannot listen on the TCP port: address already in use
```

**Cause:** Port 8765 already in use by another container or process

**Solution:**

**Option 1: Stop Existing Containers**
```bash
# Find container using port 8765
podman ps | grep 8765

# Stop all Account Intelligence containers
podman stop $(podman ps -aq --filter ancestor=project-ape)

# Clean up stopped containers
podman system prune -f

# Retry
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**Option 2: Find and Kill Process Using Port**
```bash
# Find process using port 8765
lsof -i :8765
# or
sudo netstat -tulpn | grep 8765

# Kill process
kill -9 <PID>

# Retry
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**Option 3: Use Different Port**
```bash
# Edit vars.py
DASHBOARD_PORT = 8766

# Run container with new port
podman run ... -p 8766:8766 ...
```

---

### Permission Denied on Logs

**Symptoms:**
```
ERROR | Permission denied: 'logs/client.log'
ERROR | [Errno 13] Permission denied: '/app/logs/overall.log'
```

**Cause:** Logs directory permissions incompatible with container user (UID 1000)

**Solution:**

**For Host Execution:**
```bash
# Fix permissions
chmod 755 logs/
chmod 644 logs/*.log

# Retry
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**For Container Execution:**
```bash
# Set ownership to UID 1000 (container user)
sudo chown -R 1000:1000 logs/

# Or make directory writable by all
chmod 777 logs/

# Verify
ls -ld logs/

# Retry
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

---

### Container Won't Start

**Symptoms:**
```
Error: container create failed
Error: OCI runtime error
Container exits immediately
```

**Diagnosis:**
```bash
# Check container logs
podman logs <container-name>

# Inspect container
podman inspect <container-name>

# Check exit code
podman inspect <container-name> | jq '.[0].State.ExitCode'
```

**Common Causes and Solutions:**

**1. Missing Volume Mounts**
```bash
# Verify volumes exist
podman volume ls | grep project-ape-credentials

# Recreate credentials volume if missing
podman volume create project-ape-credentials
./setup-credentials.sh
```

**2. Invalid Configuration**
```bash
# Test vars.py syntax
python3 -c "exec(open('vars.py').read()); print('Configuration valid')"
```

**3. SELinux Context Issues (RHEL/Fedora)**
```bash
# Check SELinux labels
ls -Z logs/ docs_generated/

# Relabel directories
chcon -Rt svirt_sandbox_file_t logs/
chcon -Rt svirt_sandbox_file_t docs_generated/

# Or use :z flag in volume mounts (already done in ape-run.sh)
```

---

### Credentials Volume Empty

**Symptoms:**
```
ERROR | NotebookLM credentials not found in container
ERROR | No credentials at /opt/app-root/src/.notebooklm/credentials.json
```

**Cause:** Credentials volume not properly populated

**Solution:**
```bash
# Verify credentials on host
ls -la ~/.notebooklm/credentials.json

# Recreate credentials volume
podman volume rm project-ape-credentials
podman volume create project-ape-credentials

# Copy credentials to volume
podman run --rm \
  -v ~/.notebooklm:/source:ro \
  -v project-ape-credentials:/dest \
  alpine cp -r /source/. /dest/

# Verify volume contents
podman run --rm \
  -v project-ape-credentials:/creds \
  alpine ls -la /creds/

# Should show credentials.json
```

---

## Google Drive Issues

### Drive Folder Not Accessible

**Symptoms:**
```
ERROR | Cannot access Drive folder
ERROR | File not found: <folder-id>
ERROR | Insufficient permissions
```

**Cause:** Google account doesn't have access to Drive folder, or folder doesn't exist

**Solution:**

**Step 1: Verify Folder Access**
1. Copy folder URL from `vars.py`
2. Open URL in browser
3. Verify you can see folder contents
4. Check you're signed in with correct Google account

**Step 2: Check Folder URL Format**
```python
# Correct format in vars.py
client_folder = "https://drive.google.com/drive/folders/ABC123XYZ456"

# NOT these formats:
# ❌ "https://drive.google.com/drive/u/0/folders/..."  # Remove /u/0/
# ❌ "https://docs.google.com/..."  # Wrong domain
# ❌ "ABC123XYZ456"  # Just ID, need full URL
```

**Step 3: Re-authenticate Drive**
```bash
# Delete old token
rm ~/.project-ape/drive_token.json

# Re-authenticate
python3 setup-oauth-drive-improved.py

# Ensure you sign in with the Google account that has folder access
```

---

### Google Docs Export Failed

**Symptoms:**
```
ERROR | Failed to export Google Doc to PDF
ERROR | Export request failed: 403 Forbidden
```

**Cause:** OAuth scope missing or document is too large

**Solution:**

**Verify OAuth Scopes:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Check "Scopes for Google APIs"
3. Should include: `https://www.googleapis.com/auth/drive.readonly`
4. If missing:
   - Click "Edit App"
   - Add scope: `drive.readonly`
   - Save
5. Re-run OAuth flow:
   ```bash
   rm ~/.project-ape/drive_token.json
   python3 setup-oauth-drive-improved.py
   ```

**Large Documents:**
- Google Docs > 50 pages may fail to export
- Solution: Export manually to PDF, upload to Drive folder

---

### Drive Cache Issues

**Symptoms:**
```
ERROR | Cache corruption detected
ERROR | Failed to read cached file
Unexpected: Downloaded files are older versions
```

**Cause:** Drive cache is stale or corrupted

**Solution:**

**Clear Cache:**
```bash
# Remove cache directory
rm -rf ~/.project-ape/drive_cache/

# Force fresh download
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast --refresh
```

**Disable Cache (Testing):**
```python
# In vars.py, add:
CACHE_ENABLED = False
```

---

## Dashboard Issues

### Dashboard Not Accessible

**Symptoms:**
- Browser shows "Connection refused"
- Browser shows "This site can't be reached"
- http://localhost:8765 doesn't load

**Diagnosis:**
```bash
# Check container is running
podman ps | grep project-ape

# Check port mapping
podman port <container-name>

# Test locally
curl -I http://localhost:8765

# Check if port is listening
lsof -i :8765
```

**Solutions:**

**1. Container Not Running**
```bash
# Start container
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**2. Port Not Mapped**
```bash
# Verify -p 8765:8765 flag in podman run command
# Check ape-run.sh has correct port mapping
```

**3. Firewall Blocking**
```bash
# RHEL/Fedora
sudo firewall-cmd --add-port=8765/tcp --permanent
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 8765/tcp

# macOS
# Firewall usually doesn't block localhost
```

**4. Wrong Browser**
```bash
# Try different browsers: Chrome, Firefox, Safari
# Clear browser cache: Ctrl+Shift+Delete
```

---

### Dashboard Shows Stale Data

**Symptoms:**
- Progress bars don't update
- Client status shows old information
- Logs don't stream

**Cause:** Status files not being updated or dashboard not refreshing

**Solution:**

**Verify Status Files:**
```bash
# Check status files exist
ls -la .multi_process_status/

# Watch status file updates
watch -n 1 cat .multi_process_status/client.json

# Should update every 5 seconds during execution
```

**Force Browser Refresh:**
```bash
# Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R
# Safari: Cmd+Option+R
```

**Restart Dashboard:**
```bash
# Stop container
podman stop <container-name>

# Restart
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

---

### Logs Not Streaming

**Symptoms:**
- "Real-Time Logs" section is empty
- Logs show initial messages but stop updating

**Cause:** Server-Sent Events (SSE) connection dropped

**Solution:**

**Reload Dashboard:**
```bash
# Refresh browser: F5 or Ctrl+R
```

**Check Log Files:**
```bash
# Verify logs are being written
tail -f logs/overall.log

# Check file permissions
ls -la logs/*.log
```

**Browser Console Errors:**
1. Open browser developer tools: F12
2. Check "Console" tab for errors
3. Look for SSE connection errors

---

## Workflow Issues

### Research Phase Timeout

**Symptoms:**
```
ERROR | Research timeout after 10 minutes
WARNING | Research query taking longer than expected
```

**Cause:** Large number of sources, slow API response, or API quota limits

**Solution:**

**Switch to Deep Mode:**
```bash
# Deep mode has longer timeouts
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode deep
```

**Increase Timeouts (Advanced):**
```python
# In vars.py, adjust timing
TIMINGS = {
    'ask_prompt_delay': (15.0, 20.0),  # Increase from default
    'source_processing_wait': 60,       # Increase wait time
}
```

**Reduce Research Scope:**
- Edit `ask_prompt_01.txt` and `ask_prompt_02.txt`
- Make queries more specific
- Reduce subsegments in `vars.py`

---

### Analysis Failed

**Symptoms:**
```
ERROR | Analysis phase failed
ERROR | Chat query timeout
ERROR | Failed to execute chat prompt
```

**Cause:** NotebookLM API error, timeout, or quota limit

**Solution:**

**Retry Workflow:**
```bash
# Account Intelligence has built-in retry logic (5 attempts)
# If still failing, wait 10 minutes and retry
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**Check NotebookLM Status:**
1. Go to: https://notebooklm.google.com
2. Verify service is operational
3. Check if notebooks are accessible

**Increase Delays:**
```python
# In vars.py
TIMINGS = {
    'chat_prompt_delay': (10.0, 15.0),  # Increase delays
}
```

---

### Workflow Stuck

**Symptoms:**
- Same progress percentage for > 5 minutes
- Dashboard shows "RUNNING" but no activity
- Logs show no new entries

**Diagnosis:**
```bash
# Check if container is running
podman ps | grep project-ape

# Check container resource usage
podman stats <container-name>

# Check process status
podman top <container-name>

# View logs
tail -f logs/overall.log
```

**Solutions:**

**1. Restart Workflow**
```bash
# Stop container
podman stop <container-name>

# Restart
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

**2. Check API Rate Limits**
- NotebookLM may be rate-limiting
- Wait 15-30 minutes
- Retry with deep mode (longer delays)

---

### Mind Map Generation Failed

**Symptoms:**
```
ERROR | Mind map generation failed
ERROR | NotebookLM API returned 429 (Too Many Requests)
```

**Cause:** NotebookLM API quota limit or notebook too large

**Solution:**

**Manual Generation:**
1. Open NotebookLM link from `docs_generated/{client}/NotebookLM_Link.txt`
2. Click "Mind Map" icon in UI
3. Wait for generation (can take 2-5 minutes)
4. Download manually

**Retry Later:**
```bash
# Wait 30-60 minutes for quota reset
# Then retry workflow
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

---

## Performance Issues

### Slow Execution

**Symptoms:**
- Workflow takes > 30 minutes in fast mode
- Frequent retries in logs
- High latency for API calls

**Diagnosis:**
```bash
# Check network latency
ping google.com

# Check resource usage
podman stats <container-name>

# Count retries in logs
grep -c "Retrying" logs/overall.log
```

**Solutions:**

**Increase Resource Limits:**
```bash
# Run container with more resources
podman run --cpus=4 --memory=8g ... quay.io/.../project-ape:4.0.1
```

**Adjust Timing:**
```python
# In vars.py - increase delays to reduce retries
TIMINGS = {
    'ask_prompt_delay': (15.0, 20.0),
    'chat_prompt_delay': (10.0, 12.0),
}
```

**Reduce Parallel Clients:**
```bash
# Process fewer clients at once
./developer-docs/ape-run.sh --vars ./vars.py --clients client1,client2 --mode fast
# Instead of: --clients client1,client2,client3,client4,client5
```

---

### High Retry Rate

**Symptoms:**
```
WARNING | Retry 3/5 for research query
WARNING | Retry 5/5 for chat prompt
ERROR | Max retries exceeded
```

**Cause:** API rate limits, network issues, or aggressive timing

**Solution:**

**Switch to Deep Mode:**
```bash
# Deep mode has conservative timing
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode deep
```

**Increase Retry Configuration:**
```python
# In vars.py
RETRY_CONFIG = {
    'max_attempts': 7,           # Increase from 5
    'base_delay': 15,            # Increase from 10
    'ask_max_attempts': 10,      # Increase from 7
    'ask_base_delay': 45,        # Increase from 30
}
```

**Note:** ~30% retry rate in deep mode is acceptable and expected.

---

### Memory Issues

**Symptoms:**
```
ERROR | MemoryError
ERROR | Killed (OOM)
Container exits with code 137 (OOM killed)
```

**Cause:** Container running out of memory

**Solution:**

**Increase Memory Limit:**
```bash
# Run with 8GB memory
podman run --memory=8g --memory-swap=8g ... quay.io/.../project-ape:4.0.1
```

**Reduce Parallel Clients:**
```bash
# Process 2-3 clients instead of 5+
./developer-docs/ape-run.sh --vars ./vars.py --clients client1,client2 --mode fast
```

**Check Host Memory:**
```bash
# Check available memory
free -h

# Close other applications
```

---

## Quality Score Issues

### Low Quality Score (< 7.0)

**Symptoms:**
- Quality score shows 5.0-6.9
- Validation warnings in logs
- Insufficient sources imported

**Diagnosis:**
```bash
# Check quality score
cat docs_generated/client/Quality_Score.json

# Check source count
grep "sources imported" logs/client.log
```

**Solutions:**

**1. Use Deep Mode**
```bash
# Deep mode imports 90-180 sources vs 20-50 in fast mode
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode deep
```

**2. Add More Source Documents**
```bash
# Add more PDFs to Drive folder
# Aim for 10-20 documents per client
# Include: annual reports, case studies, white papers
```

**3. Specify Industry and Subsegments**
```python
# In vars.py - help AI focus research
client_industry = "technology"
client_subsegments = "cloud, AI/ML, cybersecurity, DevOps"
```

**4. Re-run Workflow**
```bash
# Sometimes first run has lower quality
# Re-running often improves score
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode deep
```

---

### No Quality Score

**Symptoms:**
- Quality score shows `null` or missing
- `Quality_Score.json` file missing

**Cause:** Workflow failed before validation phase

**Diagnosis:**
```bash
# Check workflow status
cat .multi_process_status/client.json

# Check logs for errors
grep -i error logs/client.log
```

**Solution:**
- Fix underlying workflow errors (see sections above)
- Re-run workflow
- Quality score generates in final phase

---

## Quick Fixes

### Complete Reset

When all else fails, perform a complete reset:

```bash
# 1. Stop all containers
podman stop $(podman ps -aq)

# 2. Clean up containers and images
podman system prune -af

# 3. Remove credentials
rm -rf ~/.notebooklm
rm -rf ~/.project-ape

# 4. Re-authenticate NotebookLM
pip install notebooklm
notebooklm login

# 5. Re-setup Drive OAuth
python3 setup-oauth-drive-improved.py

# 6. Pull fresh image
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1

# 7. Verify configuration
python3 -c "exec(open('vars.py').read()); print('Configuration valid')"

# 8. Restart workflow
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast
```

---

### Re-authenticate Everything

```bash
# NotebookLM
notebooklm login

# Google Drive
rm ~/.project-ape/drive_token.json
python3 setup-oauth-drive-improved.py

# Verify both
notebooklm list
python3 -c "from core.drive_manager import DriveManager; dm = DriveManager(); print('OK')"
```

---

### Clear Cache and Logs

```bash
# Clear Drive cache
rm -rf ~/.project-ape/drive_cache/

# Clear old logs
rm -f logs/*.log

# Clear old status files
rm -f .multi_process_status/*.json

# Clear old outputs
rm -rf docs_generated/*

# Restart fresh
./developer-docs/ape-run.sh --vars ./vars.py --clients client --mode fast --refresh
```

---

## Diagnostic Commands

### System Health Check

```bash
# Python version
python3 --version  # Should be 3.10+

# Container runtime
podman --version  # or: docker --version

# NotebookLM CLI
notebooklm --version

# NotebookLM authentication
notebooklm list

# Drive authentication
ls -la ~/.project-ape/drive_credentials.json
ls -la ~/.project-ape/drive_token.json

# Virtual environment (if using)
which python  # Should show .project-ape-venv path
```

---

### Container Diagnostics

```bash
# List containers
podman ps -a

# Container logs
podman logs <container-name>

# Container resource usage
podman stats <container-name>

# Container processes
podman top <container-name>

# Container inspect
podman inspect <container-name>

# Volume list
podman volume ls

# Volume inspect
podman volume inspect project-ape-credentials
```

---

### Application Diagnostics

```bash
# Check configuration syntax
python3 -c "exec(open('vars.py').read()); print('Configuration valid')"

# Check status files
ls -la .multi_process_status/
cat .multi_process_status/client.json | jq

# Check logs
tail -f logs/overall.log
tail -f logs/client.log

# Search for errors
grep -i error logs/*.log
grep -i failed logs/*.log
grep -i warning logs/*.log

# Count retries
grep -c "Retrying" logs/*.log

# Check outputs
ls -la docs_generated/client/
cat docs_generated/client/Quality_Score.json | jq
```

---

### Network Diagnostics

```bash
# Test Google API connectivity
curl -I https://www.googleapis.com

# Test NotebookLM connectivity
curl -I https://notebooklm.google.com

# Check DNS resolution
nslookup drive.google.com

# Check firewall
sudo firewall-cmd --list-ports  # RHEL/Fedora
sudo ufw status  # Ubuntu

# Check port 8765
lsof -i :8765
```

---

## Getting Help

### Before Requesting Help

**Gather this information:**

1. **System Information**
   ```bash
   uname -a
   python3 --version
   podman --version
   ```

2. **Error Messages**
   ```bash
   # Upload complete logs
   tar -czf logs_$(date +%Y%m%d).tar.gz logs/
   ```

3. **Configuration** (sanitized)
   - `vars.py` with sensitive data removed
   - Client names anonymized

4. **Steps to Reproduce**
   - Exact commands run
   - Expected vs. actual behavior

---

### Support Channels

**Documentation:**
- [README.md](../README.md) - Overview and quick start
- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [USER_GUIDE.md](USER_GUIDE.md) - Complete usage guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [DEPLOYMENT.md](../developer-docs/DEPLOYMENT.md) - Container deployment

**GitHub:**
- **Issues**: https://github.com/yourusername/project-ape/issues
- **Discussions**: https://github.com/yourusername/project-ape/discussions

**When Opening an Issue:**
1. Search existing issues first
2. Use issue templates (bug report, feature request)
3. Include all diagnostic information above
4. Attach logs and screenshots
5. Tag with appropriate labels

---

### Self-Help Checklist

Before requesting help, try:

- ✅ **Search this troubleshooting guide** (Ctrl+F)
- ✅ **Check logs** for error messages
- ✅ **Re-authenticate** NotebookLM and Drive
- ✅ **Try complete reset** (see Quick Fixes)
- ✅ **Search GitHub issues** for similar problems
- ✅ **Review documentation** for your use case
- ✅ **Test with single client** in fast mode
- ✅ **Verify system requirements** met

---

**Still stuck? Open an issue on GitHub with diagnostic information.**

Return to: [README.md](../README.md) | See also: [USER_GUIDE.md](USER_GUIDE.md)

---

**Account Intelligence - Troubleshooting Guide**  
Version 4.0.1 | June 30, 2026
