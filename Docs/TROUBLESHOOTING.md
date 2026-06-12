# Project APE - Troubleshooting Guide

<p align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE Logo" width="120"/>
</p>

<h3 align="center">Common Issues & Solutions</h3>

<p align="center">
  Jason Anderson | Project Owner & Maintainer
</p>

---

## Authentication Issues

### ❌ Error: Token refresh failed (400 Bad Request)

**Symptoms:**
```
ERROR | [client] Research failed: Token refresh failed
ERROR | RPC returned status code 16 (Unauthenticated)
```

**Cause:** NotebookLM session has expired (typically after 7-30 days)

**Solution:**

#### Option 1: Re-authenticate on Host (Recommended)
```bash
# Stop running container
podman stop $(podman ps -q --filter ancestor=project-ape)

# Re-authenticate on host
notebooklm login

# Restart container
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

#### Option 2: Authenticate Inside Container
```bash
# Find container name
podman ps | grep project-ape

# Login inside container
podman exec -it <container-name> bash -c "pip install notebooklm-py && notebooklm login"

# Note: Browser will open for Google sign-in
```

#### Option 3: Fresh Credentials
```bash
# Clear old credentials
rm -rf ~/.notebooklm

# Fresh login
notebooklm login

# Restart container
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

---

### ❌ Error: Not authenticated

**Symptoms:**
```
ERROR | [client] Not authenticated. Login required!
```

**Cause:** No NotebookLM credentials found

**Solution:**
```bash
# Install and authenticate
pip install notebooklm-py
notebooklm login

# Verify
notebooklm list
```

---

## Container Issues

### ❌ Error: proxy already running

**Symptoms:**
```
Error: preparing container ... proxy already running
```

**Cause:** Port 8765 already in use by another container

**Solution:**
```bash
# Stop all Project APE containers
podman stop $(podman ps -aq --filter ancestor=project-ape)

# Clean up
podman system prune -f

# Retry
./ape-run.sh --mode fast
```

---

### ❌ Error: Permission denied on logs

**Symptoms:**
```
ERROR | Permission denied: 'logs/client.log'
```

**Cause:** Logs directory permissions

**Solution:**
```bash
# Fix permissions
chmod 777 logs/

# Retry
./ape-run.sh --mode fast
```

---

## Dashboard Issues

### ❌ Dashboard Not Accessible

**Symptoms:** Cannot open http://localhost:8765

**Diagnosis:**
```bash
# Check container is running
podman ps | grep project-ape

# Check port mapping
podman port <container-name>

# Test locally
curl http://localhost:8765/status
```

**Solution:**
```bash
# Ensure container is running
./ape-run.sh --mode fast

# Check firewall
sudo firewall-cmd --add-port=8765/tcp  # RHEL/Fedora

# Try different browser
# Sometimes browser cache causes issues
```

---

## PDF Issues

### ❌ Error: PDF consolidation failed

**Symptoms:**
```
ERROR | Failed to consolidate PDFs
```

**Diagnosis:**
```bash
# Check files exist
ls -lh client_data/YourClient/

# Verify PDFs
file client_data/YourClient/*.pdf

# Check total size
du -sh client_data/YourClient/
```

**Solution:**
```bash
# Ensure PDFs are valid
# Total size must be < 50MB
# No password-protected PDFs
# No corrupted files

# Fix permissions
chmod 644 client_data/YourClient/*.pdf
```

---

## Workflow Issues

### ❌ Research Timeout

**Symptoms:** Research phase takes > 10 minutes

**Cause:** Large number of sources or slow API response

**Solution:**
```bash
# Switch to deep mode (more time allocated)
./ape-run.sh --mode deep

# Or reduce research scope in prompts
```

---

### ❌ Mind Map Generation Failed

**Symptoms:**
```
ERROR | Mind map generation failed
```

**Cause:** NotebookLM API limit or notebook too large

**Solution:**
```bash
# Retry after a few minutes
# Or manually generate in NotebookLM UI
# Visit: https://notebooklm.google.com
```

---

## Quick Fixes

### Reset Everything
```bash
# Stop all containers
podman stop $(podman ps -aq)

# Clean up
podman system prune -af

# Re-authenticate
notebooklm login

# Pull fresh image
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Restart
./ape-run.sh --vars ./vars.py --clients client --mode fast
```

---

## Getting Help

1. **Check logs:** `tail -f logs/*.log`
2. **Search this guide:** Use Ctrl+F
3. **Contact maintainer:** Jason Anderson
4. **Review documentation:** See docs/ directory

---

**Project APE - Troubleshooting Guide**  
Version 3.0.1 | Jason Anderson | 2026
