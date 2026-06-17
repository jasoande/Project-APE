# Container Image Build - Quick Reference

## Mac Build (arm64)

```bash
# Quick build
./build-mac.sh latest

# Or manual
podman build -t quay.io/jasoande/project_ape/project-ape:latest .
podman push quay.io/jasoande/project_ape/project-ape:latest
```

## Linux Build (amd64)

```bash
# Quick build
./build-linux.sh 3.0.5-amd64

# Or manual
podman build -t quay.io/jasoande/project_ape/project-ape:3.0.5-amd64 .
podman push quay.io/jasoande/project_ape/project-ape:3.0.5-amd64
```

## Version Bump Checklist

When releasing a new version (e.g., 3.0.5 → 3.0.6):

1. **Update `launch_ape.sh` line 25:**
   ```bash
   echo "3.0.6-amd64"  # Change from 3.0.5-amd64
   ```

2. **Build on Linux:**
   ```bash
   ./build-linux.sh 3.0.6-amd64
   ```

3. **Build on Mac (optional):**
   ```bash
   ./build-mac.sh latest  # Still use 'latest' for Mac
   ```

4. **Test on EC2:**
   ```bash
   git pull
   ./launch_ape.sh fast
   # Verify it pulls 3.0.6-amd64
   ```

5. **Update docs:**
   - IMAGE-BUILD-GUIDE.md
   - This file

## What Requires Rebuild?

**YES - Rebuild needed:**
- Changes to `core/*.py`
- Changes to `dashboard/` 
- Changes to `main.py`
- Changes to `requirements.txt`
- Changes to `Containerfile`

**NO - Rebuild NOT needed:**
- Changes to `launch_ape.sh`
- Changes to `vars.py`
- Changes to `.env`
- Changes to `*.md` files

## Current Versions

| Platform | Tag | Purpose |
|----------|-----|---------|
| Mac | `latest` | Development |
| Linux | `3.0.5-amd64` | Production |

Last updated: 2026-06-17
