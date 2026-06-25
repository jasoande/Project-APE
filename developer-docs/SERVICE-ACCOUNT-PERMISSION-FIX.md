# Service Account Permission Error - Fix

**Error:** `PermissionError: [Errno 13] Permission denied: '/app/service-account.json'`

**Status:** ✅ FIXED

---

## Problem

Container failed to read service-account-key.json with error:
```
PermissionError: [Errno 13] Permission denied: '/app/service-account.json'
```

### Root Cause

**UID Mismatch:**
- Host file owned by: UID 501 (jasona on macOS)
- Container runs as: UID 1000 (apeuser)
- File permissions: 600 (owner read/write only)

**Result:** UID 1000 inside container cannot read file owned by UID 501

This is a common container issue where:
1. File created on host with host user's UID
2. Container runs with different UID
3. Mounted file not accessible to container user

---

## Solution

Added `--userns=keep-id` flag to Podman runs.

### What --userns=keep-id Does

**Podman-specific flag** that:
- Maps host UID → container UID
- Keeps file ownership intact
- Container user can read host user's files
- Only applies to Podman (not Docker)

**Example:**
```bash
# Host: jasona (UID 501)
# Container normally: apeuser (UID 1000)

# With --userns=keep-id:
# Container: apeuser (UID 501) ← Maps to host UID!
```

### Code Change

**File:** launch_ape.sh

**Before:**
```bash
$runtime run -it --rm \
    --name project-ape \
    -p ${DASHBOARD_PORT}:8765 \
    -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
    ...
```

**After:**
```bash
# Detect if we need --userns=keep-id for Podman
userns_flag=""
if [[ "$runtime" == "podman" ]]; then
    userns_flag="--userns=keep-id"
fi

$runtime run -it --rm \
    --name project-ape \
    ${userns_flag} \
    -p ${DASHBOARD_PORT}:8765 \
    -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
    ...
```

---

## Why Not Other Solutions?

### ❌ chmod 644 (world-readable)
```bash
chmod 644 service-account-key.json
```

**Problems:**
- Less secure (anyone on system can read)
- Google recommends 600 for service account keys
- Against security best practices

### ❌ Change file ownership to UID 1000
```bash
sudo chown 1000:1000 service-account-key.json
```

**Problems:**
- Requires sudo
- Breaks if container UID changes
- Not portable across systems
- User can't edit file anymore

### ❌ Run container as root
```bash
podman run --user=0:0 ...
```

**Problems:**
- Major security risk
- Defeats purpose of running as non-root
- Container can modify anything on host

### ✅ --userns=keep-id (CHOSEN)

**Benefits:**
- ✅ Secure (maintains 600 permissions)
- ✅ Portable (works on all systems)
- ✅ No sudo required
- ✅ Podman best practice
- ✅ No manual file changes needed

---

## Docker Compatibility

Docker doesn't support `--userns=keep-id` directly, but Docker Desktop handles UID mapping automatically on macOS/Windows.

**Detection logic:**
```bash
if [[ "$runtime" == "podman" ]]; then
    userns_flag="--userns=keep-id"
else
    userns_flag=""  # Docker doesn't need it
fi
```

---

## Testing

### Verify Fix
```bash
# 1. Check file permissions (should be 600)
ls -la service-account-key.json
# -rw-------  1 jasona  staff  2356 Jun 22 13:06 service-account-key.json

# 2. Run container
./launch_ape.sh fast

# 3. Check logs - should NOT see permission error
tail -f logs/*.log
```

### Expected Result
```
20:01:37 | INFO | [client] 🔄 Initializing Google Drive download...
20:01:37 | INFO | [client]    Folder ID: 1GnoQMM8ZK-0PSZElLIWa2z_3fy1TpoBK
20:01:38 | INFO | [client] ✅ Authenticated with service account
20:01:38 | INFO | [client] 📥 Downloading files from Google Drive...
```

### Verify UID Mapping (Optional)
```bash
# Start container in background
podman run -d --name test-ape --userns=keep-id \
    -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
    quay.io/jasona/project-ape:latest sleep 3600

# Check UID inside container
podman exec test-ape id
# Should show: uid=501(apeuser) ← Matches host UID!

# Check file access
podman exec test-ape ls -la /app/service-account.json
# Should show: -rw------- 1 apeuser apeuser 2356 ...

# Cleanup
podman rm -f test-ape
```

---

## Affected Files

Only one file changed:
- ✅ launch_ape.sh (added --userns=keep-id detection)

No changes needed to:
- ❌ Containerfile (user remains UID 1000)
- ❌ service-account-key.json (permissions stay 600)
- ❌ create-service-account.sh (no changes)
- ❌ setup-credentials.sh (no changes)

---

## Platform Support

### macOS
- ✅ Podman: Uses --userns=keep-id
- ✅ Docker Desktop: Auto UID mapping (no flag needed)

### Linux (RHEL, Fedora, Ubuntu, Debian)
- ✅ Podman: Uses --userns=keep-id
- ✅ Docker: No flag needed (native UID)

---

## Security Considerations

### Before Fix
```
File: -rw------- (600) owned by UID 501
Container: Runs as UID 1000
Result: DENIED ✅ (secure but broken)
```

### After Fix
```
File: -rw------- (600) owned by UID 501
Container: Runs as UID 501 (mapped)
Result: ALLOWED ✅ (secure AND works)
```

**Security maintained:**
- File still 600 (owner only)
- No other users can read
- Container user = host user
- SELinux still enforced (z flag)

---

## Common Questions

### Q: Why not fix the Containerfile?
**A:** The Containerfile uses UID 1000 which is standard for containers. The issue is host-container UID mismatch, which is environment-specific.

### Q: Will this break on other systems?
**A:** No. --userns=keep-id works on all Podman installations. Docker systems don't need it.

### Q: Does this affect performance?
**A:** No. User namespace mapping is handled by the kernel with negligible overhead.

### Q: Can I still use sudo inside the container?
**A:** Yes. The container user still has the same privileges, just with a mapped UID.

### Q: What if I change the service account key?
**A:** No changes needed. The fix applies to the mount, not the file.

---

## Related Issues

This fix also resolves potential permission errors for:
- .env file mount
- vars.py file mount
- Any other host files mounted with :ro flag

All benefit from the UID mapping.

---

## Conclusion

**Before:** Permission denied errors on service account file  
**After:** Clean authentication, no errors

**Impact:**
- ✅ Fixes launch_ape.sh on all platforms
- ✅ Maintains security (600 permissions)
- ✅ No manual user intervention needed
- ✅ Podman best practice implemented

**Status:** Production ready

---

**Date:** 2026-06-22  
**Priority:** CRITICAL  
**Affects:** All users running Podman on macOS/Linux
