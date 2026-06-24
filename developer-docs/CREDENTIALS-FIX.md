# NotebookLM Credentials Fix

## Issue
The pipeline was failing with authentication errors because `launch_ape.sh` wasn't mounting the credentials volume that `setup-credentials.sh` created.

## Root Cause
1. `setup-credentials.sh` creates a podman volume: `project-ape-credentials`
2. The volume contains NotebookLM credentials at: `~/.notebooklm/profiles/default/storage_state.json`
3. `launch_ape.sh` was **NOT mounting this volume** into the container
4. Result: Container couldn't find credentials → all clients failed authentication

## The Fix

Updated `launch_ape.sh` to:
1. Check if `project-ape-credentials` volume exists
2. Mount it to `/home/apeuser/.notebooklm` in the container
3. Warn if volume doesn't exist

## On EC2 Instance - Run This:

Since you already ran `./setup-credentials.sh` successfully, the volume exists. You just need to re-run the pipeline with the updated script:

```bash
# 1. Get the updated launch_ape.sh from your repo
git pull

# 2. Run the pipeline
./launch_ape.sh fast

# The credentials will now be mounted and auth will succeed!
```

## Verification

After starting, you should see:
```
[INFO] Using credentials volume: project-ape-credentials
```

And in the logs (instead of auth failures):
```
18:19:23 | INFO | [blue_yonder_test] Checking authentication status...
18:19:24 | INFO | [blue_yonder_test] ✅ Already authenticated
```

## How It Works Now

### setup-credentials.sh (one-time setup)
1. Copies `~/.notebooklm` from host to podman volume
2. Volume persists across container runs
3. Credentials are available to all future containers

### launch_ape.sh (every run)
1. Checks if `project-ape-credentials` volume exists
2. Mounts it to `/home/apeuser/.notebooklm` in container
3. NotebookLM CLI finds credentials automatically
4. All clients authenticate successfully

## Volume Details

```bash
# List volumes
podman volume ls

# Inspect credentials volume
podman volume inspect project-ape-credentials

# Location on host (podman manages this)
podman volume inspect project-ape-credentials | grep Mountpoint
```

## Manual Testing

To verify credentials are accessible in container:

```bash
# Start container with credentials
./launch_ape.sh fast

# In another terminal, enter container
podman exec -it project-ape bash

# Check if credentials exist
ls -la /home/apeuser/.notebooklm/profiles/default/

# Should show:
# storage_state.json  <-- This is the auth token
```

## Troubleshooting

### If auth still fails:

1. **Verify volume exists:**
   ```bash
   podman volume ls | grep project-ape-credentials
   ```

2. **Recreate credentials:**
   ```bash
   ./setup-credentials.sh
   # Answer 'y' to overwrite
   ```

3. **Check credentials in volume:**
   ```bash
   podman run --rm \
     -v project-ape-credentials:/creds \
     quay.io/jasoande/project_ape/project-ape:3.0.5-amd64 \
     ls -la /creds/profiles/default/
   ```

4. **Fresh login (if credentials corrupted):**
   ```bash
   # Remove old volume
   podman volume rm project-ape-credentials
   
   # Login on host
   notebooklm login
   
   # Setup credentials again
   ./setup-credentials.sh
   ```

## Architecture

```
Host Machine (EC2)
├── ~/.notebooklm/                    # Your NotebookLM credentials
│   └── profiles/default/
│       └── storage_state.json        # Auth token
│
└── Podman Volume
    └── project-ape-credentials       # Persistent volume
        └── (copy of ~/.notebooklm)

Container (project-ape)
├── /home/apeuser/.notebooklm/        # Mounted from volume
│   └── profiles/default/
│       └── storage_state.json        # Same token, accessible
│
└── /opt/venv/bin/notebooklm          # CLI finds credentials here
```

## Why Use a Volume Instead of Bind Mount?

### Option 1: Bind Mount (what we DON'T do)
```bash
-v ~/.notebooklm:/home/apeuser/.notebooklm
```
**Problems:**
- SELinux blocks access (permission denied)
- UID/GID mismatch between host and container
- Credentials at `~/.notebooklm` might not exist on all systems

### Option 2: Podman Volume (what we DO)
```bash
-v project-ape-credentials:/home/apeuser/.notebooklm
```
**Benefits:**
- ✅ Podman manages permissions automatically
- ✅ Survives container restarts
- ✅ Same credentials for all containers
- ✅ SELinux compatible
- ✅ No UID/GID issues

## Summary

**Before fix:**
```bash
./setup-credentials.sh  # ✅ Creates volume
./launch_ape.sh fast    # ❌ Doesn't mount it → auth fails
```

**After fix:**
```bash
./setup-credentials.sh  # ✅ Creates volume (one-time)
./launch_ape.sh fast    # ✅ Mounts volume → auth succeeds!
```

---

**Updated:** 2026-06-17
**File:** `launch_ape.sh`
**Lines Changed:** Added credentials volume mount check and mount
