# Project APE - Container Image Build Guide

**Multi-architecture container image building for Project APE**

---

## Overview

Project APE uses **multi-architecture container images** to support both development (Mac M1/M2/M3) and production (Linux x86_64/EC2) environments.

### Architecture Strategy

| Platform | Architecture | Image Tag | Build Location |
|----------|-------------|-----------|----------------|
| **Mac** (M1/M2/M3) | arm64 | `latest` | Mac (native) |
| **Linux** (EC2, RHEL9) | amd64 | `3.0.5-amd64` | Linux (native) |

---

## Prerequisites

### On Mac (arm64 build)

```bash
# Install Podman Desktop OR Docker Desktop
brew install podman-desktop

# Verify
podman --version  # Should show 4.x+
```

### On Linux (amd64 build)

```bash
# RHEL9/Fedora
sudo dnf install podman

# Ubuntu/Debian
sudo apt-get install podman

# Verify
podman --version
```

---

## Build Instructions

### Quick Build (Single Architecture)

```bash
# On Mac (builds arm64)
podman build -t project-ape:latest .

# On Linux (builds amd64)
podman build -t project-ape:3.0.5-amd64 .
```

### Detailed Build Process

#### Step 1: Ensure Code is Up-to-Date

```bash
# Pull latest changes
git pull origin QA

# Verify critical files exist
ls -la Containerfile requirements.txt main.py core/ dashboard/
```

#### Step 2: Build the Image

**On Mac (arm64):**
```bash
# Clean build (recommended)
podman build --no-cache \
  -t localhost/project-ape:latest \
  -t quay.io/jasoande/project_ape/project-ape:latest \
  -f Containerfile .

# Verify build
podman images | grep project-ape
```

**On Linux (amd64):**
```bash
# Clean build (recommended)
podman build --no-cache \
  -t localhost/project-ape:3.0.5-amd64 \
  -t quay.io/jasoande/project_ape/project-ape:3.0.5-amd64 \
  -f Containerfile .

# Verify build
podman images | grep project-ape
```

#### Step 3: Test the Image Locally

**On Mac:**
```bash
# Test run
podman run --rm -it \
  -e HOME=/home/apeuser \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/vars.py:/app/vars.py:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro \
  localhost/project-ape:latest \
  python3 main.py --mode fast --clients merck_test

# Should initialize and attempt to run
# Ctrl+C to stop after verifying it starts
```

**On Linux:**
```bash
# Test run
podman run --rm -it \
  -e HOME=/home/apeuser \
  -v $(pwd)/.env:/app/.env:ro,z \
  -v $(pwd)/vars.py:/app/vars.py:ro,z \
  -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro,z \
  localhost/project-ape:3.0.5-amd64 \
  python3 main.py --mode fast --clients merck_test

# Should initialize and attempt to run
# Ctrl+C to stop after verifying it starts
```

#### Step 4: Push to Registry

**Login to Quay.io:**
```bash
podman login quay.io
# Username: jasoande
# Password: <your-quay-token>
```

**Push Mac (arm64) image:**
```bash
podman push quay.io/jasoande/project_ape/project-ape:latest
```

**Push Linux (amd64) image:**
```bash
podman push quay.io/jasoande/project_ape/project-ape:3.0.5-amd64
```

---

## What Gets Included in the Image

### ✅ Included (Baked into image)

```
/app/
├── core/                   # Pipeline logic
├── dashboard/              # Web dashboard
├── main.py                 # Entry point
├── example-vars.py         # Template config
├── *.txt                   # Prompt templates
└── container-entrypoint.sh # Startup script
```

### ❌ Excluded (Mounted at runtime)

```
.env                        # API keys (security)
vars.py                     # Client config (per-environment)
jasoande-*.json            # Service account (security)
logs/                      # Output logs (runtime)
.multi_process_status/     # Status files (runtime)
client_data/               # Source PDFs (too large)
```

**Why excluded?**
- **Security:** API keys and credentials never in image
- **Flexibility:** Same image works for all environments
- **Size:** Client data can be GBs, keep image small
- **Runtime:** Logs/status generated during execution

---

## Version Tagging Strategy

### Current Strategy

| Tag | Architecture | Purpose | Updated When |
|-----|-------------|---------|--------------|
| `latest` | arm64 | Mac development | Each Mac build |
| `3.0.5-amd64` | amd64 | Linux production | Bug fixes / features |
| `3.0.5-arm64` | arm64 | *(Not used)* | - |

### Version Bumping

When to bump version (currently `3.0.5`):

- **Patch** (3.0.5 → 3.0.6): Bug fixes, minor changes
- **Minor** (3.0.5 → 3.1.0): New features, significant changes
- **Major** (3.0.5 → 4.0.0): Breaking changes, major refactor

**Update these files when bumping:**
1. `launch_ape.sh` - Line 25 (`echo "3.0.5-amd64"`)
2. `setup-credentials.sh` - Image version variable
3. This guide - Update examples

---

## Build Automation

### Mac Build Script

Create `build-mac.sh`:
```bash
#!/bin/bash
set -e

VERSION="${1:-latest}"

echo "Building Project APE for arm64..."
podman build --no-cache \
  -t localhost/project-ape:${VERSION} \
  -t quay.io/jasoande/project_ape/project-ape:${VERSION} \
  -f Containerfile .

echo "Testing image..."
podman run --rm localhost/project-ape:${VERSION} python3 --version

echo "Push to registry? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    podman push quay.io/jasoande/project_ape/project-ape:${VERSION}
    echo "✅ Pushed: quay.io/jasoande/project_ape/project-ape:${VERSION}"
fi
```

### Linux Build Script

Create `build-linux.sh`:
```bash
#!/bin/bash
set -e

VERSION="${1:-3.0.5-amd64}"

echo "Building Project APE for amd64..."
podman build --no-cache \
  -t localhost/project-ape:${VERSION} \
  -t quay.io/jasoande/project_ape/project-ape:${VERSION} \
  -f Containerfile .

echo "Testing image..."
podman run --rm localhost/project-ape:${VERSION} python3 --version

echo "Push to registry? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    podman push quay.io/jasoande/project_ape/project-ape:${VERSION}
    echo "✅ Pushed: quay.io/jasoande/project_ape/project-ape:${VERSION}"
fi
```

**Usage:**
```bash
# Mac
chmod +x build-mac.sh
./build-mac.sh latest

# Linux
chmod +x build-linux.sh
./build-linux.sh 3.0.5-amd64
```

---

## Code Changes Requiring Image Rebuild

### Requires Rebuild

These changes need a new image build:

- ✅ Changes to `core/*.py` (pipeline logic)
- ✅ Changes to `dashboard/*.py` or `dashboard/templates/*.html` (dashboard)
- ✅ Changes to `main.py` (entry point)
- ✅ Changes to `requirements.txt` (dependencies)
- ✅ Changes to `Containerfile` (build process)
- ✅ Changes to `container-entrypoint.sh` (startup)
- ✅ Changes to prompt templates (`*.txt`)

### No Rebuild Needed

These changes work immediately (mounted at runtime):

- ❌ Changes to `.env` (API keys)
- ❌ Changes to `vars.py` (client config)
- ❌ Changes to `launch_ape.sh` (launcher script)
- ❌ Changes to `setup-*.sh` (setup scripts)
- ❌ Changes to `*.md` (documentation)

---

## Current Build Includes Timer Fix

**IMPORTANT:** The latest code includes the execution timer fix in `core/client_pipeline.py`.

### What was fixed:

```python
# Before (broken):
status_data = {..., **kwargs}  # kwargs with start_time=None overwrites

# After (fixed):
if 'start_time' in kwargs and kwargs['start_time'] is None:
    kwargs = {k: v for k, v in kwargs.items() if k != 'start_time'}
status_data = {..., **kwargs}
```

### To include the fix in images:

**Mac:**
```bash
git pull origin QA
./build-mac.sh latest
```

**Linux:**
```bash
git pull origin QA
./build-linux.sh 3.0.5-amd64
# OR for new version:
./build-linux.sh 3.0.6-amd64
```

---

## Troubleshooting

### Issue: Build fails with "No space left on device"

**Solution:**
```bash
# Clean up old images
podman system prune -a --volumes

# Check disk space
df -h
```

### Issue: Build fails on dependency installation

**Solution:**
```bash
# Verify requirements.txt is valid
cat requirements.txt

# Try without cache
podman build --no-cache -t project-ape:test .
```

### Issue: Image works locally but fails in registry

**Solution:**
```bash
# Check login
podman login quay.io

# Verify push permissions
podman push --help

# Check repository exists on quay.io
# https://quay.io/repository/jasoande/project_ape/project-ape
```

### Issue: Wrong architecture image pulled

**Mac pulls amd64 or Linux pulls arm64:**

**Solution:**
```bash
# Check what you built
podman images | grep project-ape

# Check architecture
podman inspect localhost/project-ape:latest | jq '.[0].Architecture'

# Rebuild for correct architecture
# (Must build on native platform)
```

---

## Multi-Architecture Manifest (Future)

Currently, we build separately for each architecture. To support true multi-arch with one tag:

```bash
# Create multi-arch manifest (requires both images built)
podman manifest create project-ape:3.0.5

# Add arm64 image (from Mac)
podman manifest add project-ape:3.0.5 \
  --arch arm64 \
  quay.io/jasoande/project_ape/project-ape:latest

# Add amd64 image (from Linux)
podman manifest add project-ape:3.0.5 \
  --arch amd64 \
  quay.io/jasoande/project_ape/project-ape:3.0.5-amd64

# Push manifest
podman manifest push project-ape:3.0.5 \
  quay.io/jasoande/project_ape/project-ape:3.0.5
```

**Not implemented yet** - current separate tag strategy works fine.

---

## Registry Information

### Quay.io Repository

- **Organization:** jasoande
- **Project:** project_ape
- **Repository:** project-ape
- **URL:** https://quay.io/repository/jasoande/project_ape/project-ape

### Available Tags

Check current tags:
```bash
podman search quay.io/jasoande/project_ape/project-ape --list-tags
```

Expected output:
```
NAME                                      TAG
quay.io/jasoande/project_ape/project-ape  latest        (arm64)
quay.io/jasoande/project_ape/project-ape  3.0.5-amd64   (amd64)
quay.io/jasoande/project_ape/project-ape  3.0.4         (old)
quay.io/jasoande/project_ape/project-ape  v3.0.4        (old)
```

---

## Summary

### Build Workflow

**Mac Developer:**
1. Make code changes
2. Test locally
3. `git push origin QA`
4. `./build-mac.sh latest`
5. Image pushed to quay.io

**Linux Operator (You):**
1. `git pull origin QA`
2. `./build-linux.sh 3.0.5-amd64`
3. Image pushed to quay.io
4. EC2 instances pull new image

**Both images in registry** → `launch_ape.sh` auto-selects correct one based on architecture

---

## Quick Reference

```bash
# Build Mac (arm64)
podman build -t quay.io/jasoande/project_ape/project-ape:latest .

# Build Linux (amd64)  
podman build -t quay.io/jasoande/project_ape/project-ape:3.0.5-amd64 .

# Test locally
podman run --rm -e HOME=/home/apeuser \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/vars.py:/app/vars.py:ro \
  localhost/project-ape:TAG \
  python3 main.py --mode fast

# Push to registry
podman login quay.io
podman push quay.io/jasoande/project_ape/project-ape:TAG

# Pull on EC2
podman pull quay.io/jasoande/project_ape/project-ape:3.0.5-amd64
```

---

**Last Updated:** 2026-06-17  
**Current Version:** 3.0.5  
**Architectures:** arm64 (Mac), amd64 (Linux)
