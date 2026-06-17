# Project APE - Container Quick Start

**Image Name:** `project-ape-rhel9`  
**Base:** RHEL 9 UBI with Python 3.14  
**Architectures:** amd64 (x86_64), arm64 (aarch64)

---

## TL;DR

```bash
# Build for your architecture
./build-multiarch.sh

# Run fast mode
./run-container.sh

# Dashboard: http://localhost:8765
```

---

## Architecture Detection

The scripts **automatically detect your architecture** and use the correct image:

- **x86_64 / amd64**: Full RHEL image with LibreOffice
- **arm64 / aarch64**: RHEL image (LibreOffice not available on ARM in RHEL repos)

### Image Naming Convention

```
project-ape-rhel9:3.0.5-amd64    # x86_64 / Intel/AMD
project-ape-rhel9:3.0.5-arm64    # ARM64 / Apple Silicon
project-ape-rhel9:latest         # Multi-arch manifest (auto-selects)
```

---

## Quick Commands

### Build

```bash
# Auto-detect and build for current arch
./build-multiarch.sh

# Build and push to registry
./build-multiarch.sh --push quay.io/yourorg
```

### Run

```bash
# Fast mode (all clients)
./run-container.sh

# Deep mode
./run-container.sh --mode deep

# Specific clients
./run-container.sh --mode fast --clients "merck_test organon_test"

# Build locally first
./run-container.sh --build
```

---

## Manual Usage

### Podman (Recommended for RHEL/Fedora)

```bash
# Build
podman build -t project-ape-rhel9:latest -f Containerfile .

# Run
podman run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/vars.py:/app/vars.py:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro \
  -v $(pwd)/test_client_data:/app/client_data:ro \
  -v $(pwd)/logs:/app/logs:rw \
  project-ape-rhel9:latest
```

### Docker (Alternative)

```bash
# Build
docker build -t project-ape-rhel9:latest -f Containerfile .

# Run
docker run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/vars.py:/app/vars.py:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro \
  -v $(pwd)/test_client_data:/app/client_data:ro \
  -v $(pwd)/logs:/app/logs:rw \
  project-ape-rhel9:latest
```

---

## Architecture-Specific Notes

### x86_64 (amd64) - Full Features
✅ LibreOffice included  
✅ PDF conversion works  
✅ All features available  

### ARM64 (aarch64) - Limited
⚠️ LibreOffice NOT available in RHEL repos for ARM  
⚠️ PDF conversion may fail  
ℹ️ Use pre-consolidated PDFs or run on x86_64  

---

## Files Created

1. **Containerfile** - RHEL 9 UBI multi-stage build
2. **run-container.sh** - Auto-detects architecture and runs
3. **build-multiarch.sh** - Builds for amd64 and/or arm64
4. **.containerignore** - Excludes unnecessary files

---

**Created:** June 16, 2026  
**Version:** 3.0.5  
**Status:** Production Ready
