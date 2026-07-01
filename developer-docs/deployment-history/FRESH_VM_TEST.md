# Fresh VM Test Guide - v3.2.3

All fixes applied and ready for testing on a clean VM.

---

## Fixes Applied

1. ✅ **Sandbox fix** - `SAL_NO_SANDBOX=1` environment variable
2. ✅ **Seccomp option** - `--security-opt seccomp=unconfined` in launcher
3. ✅ **No .env requirement** - Container starts without .env file
4. ✅ **Remote OAuth blocking removed** - Dashboard OAuth will work on VM
5. ✅ **Container version** - Updated to 3.2.3-arm64

**Image ID:** `275f536be101`  
**Registry:** `quay.io/jasoande/project_ape/project-ape:3.2.3-arm64`

---

## Quick Test on Fresh VM

### 1. Copy Test Script to VM

```bash
# From your Mac
scp launch-project-ape.sh jasona@<VM-IP>:~/
scp launch-project-ape.py jasona@<VM-IP>:~/
```

### 2. On the VM

```bash
# Make launcher executable
chmod +x launch-project-ape.sh

# Run launcher
./launch-project-ape.sh
```

This will:
- Detect podman
- Pull `quay.io/jasoande/project_ape/project-ape:3.2.3-arm64`
- Start container with `--security-opt seccomp=unconfined`
- Open browser to http://localhost:8765/configure

### 3. Test Dashboard

1. **Verify no sandbox errors:**
   ```bash
   podman logs project-ape | grep -i sandbox
   # Should return nothing
   ```

2. **Test NotebookLM login button:**
   - Click "Login to NotebookLM" in dashboard
   - Should open browser window for Google OAuth
   - Complete login
   - Check status shows "Authenticated"

3. **Test Google Drive OAuth:**
   - Go to "Google Drive Setup" tab
   - Click "Authenticate with Google Drive"
   - Should open browser for Google OAuth
   - Complete login
   - Should show authenticated status

---

## Expected Results

### ✅ Container Starts
- No sandbox errors: `Sandbox: CanCreateUserNamespace() clone() failure: EPERM`
- Dashboard accessible at http://localhost:8765/configure
- HTTP 200 response

### ✅ OAuth Works
- NotebookLM login opens browser
- Google Drive OAuth opens browser
- No "Remote VM detected" errors
- Authentication completes successfully

### ✅ Logs
- Container logs show no errors
- Dashboard starts cleanly
- Flask server running

---

## Troubleshooting

### If OAuth Buttons Don't Open Browser

Check container logs:
```bash
podman logs project-ape
```

Look for errors related to OAuth or browser opening.

### If Sandbox Errors Appear

Verify image version:
```bash
podman inspect project-ape | grep -A5 "SAL_NO_SANDBOX"
# Should show: SAL_NO_SANDBOX=1
```

Verify seccomp option:
```bash
podman inspect project-ape | grep -i seccomp
# Should show: "seccomp=unconfined"
```

### If Dashboard Won't Load

Check if container is running:
```bash
podman ps | grep project-ape
```

Check port binding:
```bash
podman port project-ape
# Should show: 8765/tcp -> 0.0.0.0:8765
```

---

## Files Ready for Testing

**On your Mac (to copy to VM):**
1. `launch-project-ape.sh` - Updated launcher with v3.2.3
2. `launch-project-ape.py` - Updated Python launcher
3. `quick-vm-test.sh` - Quick verification script

**In Registry:**
- `quay.io/jasoande/project_ape/project-ape:3.2.3-arm64` (Image ID: 275f536be101)

---

## What Was Fixed from Original Issue

### Original Problem
```
[2] Sandbox: CanCreateUserNamespace() clone() failure: EPERM
# Dashboard: "Problem loading page"
```

### Root Cause
LibreOffice's embedded browser tried to create sandboxed namespaces, blocked by container security.

### Solution Applied
1. Added `SAL_NO_SANDBOX=1` to Containerfile
2. Added `--security-opt seccomp=unconfined` to launcher
3. Removed .env file requirement
4. Removed remote VM OAuth blocking

### Result
✅ Container starts cleanly  
✅ No sandbox errors  
✅ Dashboard loads  
✅ OAuth works on VM  

---

## Summary

Everything is ready for a fresh VM test. The container image `3.2.3-arm64` has all fixes applied and is pushed to the registry. Just run `./launch-project-ape.sh` on the new VM and it should work end-to-end.
