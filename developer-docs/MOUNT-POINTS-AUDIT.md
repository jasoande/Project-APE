# Project APE - Container Mount Points Audit

**Complete audit of all container volume mounts to ensure nothing is missing**

---

## Current Mount Configuration

### 1. Required Configuration Files (Read-Only)

| Host Path | Container Path | Purpose | Status |
|-----------|---------------|---------|--------|
| `.env` | `/app/.env` | API keys (Gemini, Claude) | ✅ Mounted |
| `vars.py` | `/app/vars.py` | Client configuration | ✅ Mounted |
| `jasoande-*.json` | `/app/service-account.json` | Google Drive service account | ✅ Mounted |

**SELinux flags:** `:ro,z` (read-only, private label)

**Validation:**
```bash
# These files MUST exist on host
ls -la .env vars.py jasoande-*.json

# Container verifies them in container-entrypoint.sh
```

---

### 2. Required Output Directories (Read-Write)

| Host Path | Container Path | Purpose | Status |
|-----------|---------------|---------|--------|
| `logs/` | `/app/logs` | Client pipeline logs | ✅ Mounted |
| `.multi_process_status/` | `/app/.multi_process_status` | Real-time status JSON files | ✅ Mounted |

**SELinux flags:** `:z` (read-write, private label)

**Permissions:** `chmod 777` (container runs as UID 1000)

**Validation:**
```bash
# Auto-created by launch_ape.sh
mkdir -p logs .multi_process_status
chmod 777 logs .multi_process_status
```

---

### 3. Required Credentials Volume (Persistent)

| Volume Name | Container Path | Purpose | Status |
|-------------|---------------|---------|--------|
| `project-ape-credentials` | `/home/apeuser/.notebooklm` | NotebookLM auth tokens | ✅ Mounted |

**Setup:** One-time via `./setup-credentials.sh`

**Contains:**
```
/home/apeuser/.notebooklm/
└── profiles/default/
    └── storage_state.json  # Playwright auth state
```

**Validation:**
```bash
# Check volume exists
podman volume ls | grep project-ape-credentials

# View contents
podman run --rm \
  -v project-ape-credentials:/creds \
  quay.io/jasoande/project_ape/project-ape:3.0.5-amd64 \
  ls -la /creds/profiles/default/
```

**Critical:** Pipeline fails without this → all clients fail authentication

---

### 4. Optional Cache Volume (Performance)

| Volume Name | Container Path | Purpose | Status |
|-------------|---------------|---------|--------|
| `project-ape-cache` | `/home/apeuser/.project-ape` | Drive & industry cache | ✅ Mounted (if exists) |

**Setup:** Optional via `./setup-cache.sh`

**Contains:**
```
/home/apeuser/.project-ape/
├── drive_cache/
│   └── <folder-id>/        # Cached Google Drive downloads
│       └── *.pdf, *.docx
└── industry_cache/
    └── <client>.json       # Cached industry detection results
```

**Benefits:**
- ⚡ Faster subsequent runs (no re-download from Drive)
- 💰 Reduced API calls
- 🎯 Consistent industry detection

**Note:** Auto-detected by `launch_ape.sh` - only mounted if volume exists

---

## Mount Point Validation Checklist

### ✅ All Required Mounts Present

- [x] `.env` → API keys loaded
- [x] `vars.py` → Client config loaded
- [x] `service-account.json` → Google Drive auth
- [x] `logs/` → Pipeline logs written
- [x] `.multi_process_status/` → Status updates written
- [x] `project-ape-credentials` → NotebookLM auth
- [x] `project-ape-cache` → Optional performance cache

### ✅ No Missing Mounts

Checked for additional paths referenced in code:

| Path Pattern | Used By | Mount Needed? | Reason |
|-------------|---------|---------------|--------|
| `Path.home() / '.project-ape'` | `drive_manager.py`, `claude_industry_detector.py` | ✅ Yes (optional) | Cache - handled by `project-ape-cache` volume |
| `Path.home() / '.notebooklm'` | `auth_manager.py` | ✅ Yes (required) | Credentials - handled by `project-ape-credentials` volume |
| `/tmp/*` | Various (temp files) | ❌ No | Container-local temp, auto-cleaned |
| `SCRIPT_DIR / "logs"` | `main.py` | ✅ Yes | Handled by `logs/` mount |
| `SCRIPT_DIR / ".multi_process_status"` | `main.py` | ✅ Yes | Handled by `.multi_process_status/` mount |

### ✅ SELinux Compatibility

All mounts include `:z` flag for RHEL9/Fedora compatibility:

```bash
-v $(pwd)/.env:/app/.env:ro,z                # ✅ Private label, read-only
-v $(pwd)/vars.py:/app/vars.py:ro,z         # ✅ Private label, read-only
-v $(pwd)/jasoande-*.json:/app/service-account.json:ro,z  # ✅ Private label, read-only
-v $(pwd)/logs:/app/logs:z                  # ✅ Private label, read-write
-v $(pwd)/.multi_process_status:/app/.multi_process_status:z  # ✅ Private label, read-write
-v project-ape-credentials:/home/apeuser/.notebooklm        # ✅ Volume (no :z needed)
-v project-ape-cache:/home/apeuser/.project-ape            # ✅ Volume (no :z needed)
```

**Note:** Named volumes don't need `:z` flag - podman manages their labels

---

## Validation Scripts

### Check All Mounts in Running Container

```bash
# Start container
./launch_ape.sh fast

# In another terminal, check mounts
podman exec project-ape bash -c '
echo "=== Configuration Files ==="
ls -la /app/.env /app/vars.py /app/service-account.json

echo -e "\n=== Output Directories ==="
ls -la /app/logs /app/.multi_process_status

echo -e "\n=== Credentials ==="
ls -la /home/apeuser/.notebooklm/profiles/default/

echo -e "\n=== Cache (if mounted) ==="
ls -la /home/apeuser/.project-ape/
'
```

### Test Write Permissions

```bash
podman exec project-ape bash -c '
echo "Testing write to logs..."
touch /app/logs/test.log && echo "✅ logs writable" || echo "❌ logs not writable"

echo "Testing write to status..."
touch /app/.multi_process_status/test.json && echo "✅ status writable" || echo "❌ status not writable"

# Cleanup
rm /app/logs/test.log /app/.multi_process_status/test.json 2>/dev/null
'
```

---

## Common Issues & Fixes

### Issue: Permission denied writing to logs

**Cause:** Directory exists but wrong permissions

**Fix:**
```bash
./fix-permissions.sh
# OR
chmod 777 logs .multi_process_status
```

### Issue: vars.py not found or not readable

**Cause:** SELinux blocking access, missing `:z` flag

**Fix:** Already in `launch_ape.sh` - ensure using latest version:
```bash
git pull
./launch_ape.sh fast
```

### Issue: All clients fail authentication

**Cause:** Credentials volume not mounted

**Fix:**
```bash
./setup-credentials.sh  # One-time setup
./launch_ape.sh fast    # Now includes volume mount
```

### Issue: Slow on repeat runs (downloads files every time)

**Cause:** No cache volume

**Fix:**
```bash
./setup-cache.sh        # Optional setup
./launch_ape.sh fast    # Auto-detects and uses cache
```

---

## Architecture Diagram

```
Host (EC2 / Mac)
├── Project-APE/
│   ├── .env ──────────────────────────► /app/.env (ro)
│   ├── vars.py ───────────────────────► /app/vars.py (ro)
│   ├── jasoande-*.json ───────────────► /app/service-account.json (ro)
│   ├── logs/ ◄───────────────────────── /app/logs (rw)
│   └── .multi_process_status/ ◄──────── /app/.multi_process_status (rw)
│
└── Podman Volumes
    ├── project-ape-credentials ───────► /home/apeuser/.notebooklm
    │   └── profiles/default/
    │       └── storage_state.json
    │
    └── project-ape-cache (optional) ──► /home/apeuser/.project-ape
        ├── drive_cache/
        │   └── <folder-id>/
        └── industry_cache/

Container (project-ape:3.0.5-amd64)
├── /app/
│   ├── .env ◄──────────── Config mount
│   ├── vars.py ◄─────────── Config mount
│   ├── service-account.json ◄─ Config mount
│   ├── logs/ ─────────────► Output mount
│   ├── .multi_process_status/ ► Output mount
│   └── main.py ───────────── Entry point
│
└── /home/apeuser/
    ├── .notebooklm/ ◄────── Credentials volume
    └── .project-ape/ ◄───── Cache volume (optional)
```

---

## Summary

**All mount points are accounted for:**

1. ✅ **Configuration files** - Mounted read-only with SELinux labels
2. ✅ **Output directories** - Mounted read-write with proper permissions
3. ✅ **Credentials volume** - Required, setup via `setup-credentials.sh`
4. ✅ **Cache volume** - Optional, setup via `setup-cache.sh`

**No missing mounts identified.**

**All paths in Python code are covered:**
- `Path.home() / '.notebooklm'` → credentials volume
- `Path.home() / '.project-ape'` → cache volume (optional)
- `/app/logs` → logs mount
- `/app/.multi_process_status` → status mount

**Scripts updated:**
- `launch_ape.sh` - All mounts with proper flags
- `setup-credentials.sh` - Credentials volume setup
- `setup-cache.sh` - Cache volume setup (new)
- `fix-permissions.sh` - Permission fixer

---

**Last Updated:** 2026-06-17  
**Audit Status:** ✅ Complete - No missing mounts
