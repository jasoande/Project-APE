# Project APE - RHEL 9 UBI Container Guide

**Base Image:** Red Hat Universal Base Image 9 (UBI9)  
**Registry:** `registry.access.redhat.com/ubi9/ubi:latest`  
**Target Users:** Non-Mac users (Linux, Windows WSL, OpenShift, Podman)

---

## Quick Start

### Prerequisites

**For Podman (Recommended for RHEL/Fedora):**
```bash
# RHEL 9 / Fedora
sudo dnf install podman podman-compose

# Verify
podman --version
```

**For Docker (Alternative):**
```bash
# Install Docker Engine
# See: https://docs.docker.com/engine/install/

# Verify
docker --version
```

---

## Build Container

### Using Podman (Red Hat/Fedora)

```bash
# Build the container
podman build -t project-ape:latest -f Containerfile .

# Verify build
podman images | grep project-ape
```

### Using Docker (Alternative)

```bash
# Build the container
docker build -t project-ape:latest -f Containerfile .

# Verify build
docker images | grep project-ape
```

---

## Run Container

### Basic Run (Fast Mode)

**Podman:**
```bash
podman run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/opt/project-ape/.env:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro \
  -v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro \
  -v $(pwd)/logs:/opt/project-ape/logs:rw \
  project-ape:latest main.py --mode fast
```

**Docker:**
```bash
docker run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/opt/project-ape/.env:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro \
  -v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro \
  -v $(pwd)/logs:/opt/project-ape/logs:rw \
  project-ape:latest main.py --mode fast
```

### Deep Mode

```bash
podman run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/opt/project-ape/.env:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro \
  -v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro \
  -v $(pwd)/logs:/opt/project-ape/logs:rw \
  project-ape:latest main.py --mode deep
```

### Update Mode

```bash
podman run -it --rm \
  -p 8765:8765 \
  -v $(pwd)/.env:/opt/project-ape/.env:ro \
  -v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro \
  -v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro \
  -v $(pwd)/logs:/opt/project-ape/logs:rw \
  project-ape:latest main.py --mode update
```

---

## Volume Mounts Explained

### Required Volumes

**1. Environment Variables (`.env`)**
```bash
-v $(pwd)/.env:/opt/project-ape/.env:ro
```
- Contains API keys (GEMINI_API_KEY, ANTHROPIC_VERTEX_PROJECT_ID)
- Read-only (`:ro`) for security
- **REQUIRED**

**2. Service Account Key (`jasoande-3aec1043e544.json`)**
```bash
-v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro
```
- Google Drive service account credentials
- Read-only for security
- **REQUIRED** if using Google Drive integration

**3. Client Data (`test_client_data/`)**
```bash
-v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro
```
- Client PDFs and documents
- Read-only (source files shouldn't be modified)
- **REQUIRED**

**4. Logs (`logs/`)**
```bash
-v $(pwd)/logs:/opt/project-ape/logs:rw
```
- Pipeline execution logs
- Read-write (`:rw`) to write log files
- **OPTIONAL** but recommended for debugging

### Optional Volumes

**5. Status Files (`.multi_process_status/`)**
```bash
-v $(pwd)/.multi_process_status:/opt/project-ape/.multi_process_status:rw
```
- Real-time pipeline status
- Read-write for dashboard updates
- Optional (created automatically if not mounted)

**6. NotebookLM Config**
```bash
-v ${HOME}/.config/notebooklm:/home/apeuser/.config/notebooklm:rw
```
- NotebookLM authentication tokens
- Persists authentication across runs
- Optional but recommended

---

## Port Mapping

```bash
-p 8765:8765
```

- **8765**: Dashboard web interface
- Access at: http://localhost:8765
- Shows real-time pipeline progress
- Timer persists across page refresh

---

## Environment Variables

### Required in `.env` file:

```bash
# Gemini API (for agent orchestration)
GEMINI_API_KEY=your_gemini_key_here

# Claude AI via Vertex AI (for industry auto-detection)
CLAUDE_CODE_USE_VERTEX=1
ANTHROPIC_VERTEX_PROJECT_ID=your-gcp-project-id
ANTHROPIC_VERTEX_REGION=us-east5

# Google Drive (for downloading client data)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/opt/project-ape/service-account.json
```

---

## Running on OpenShift

### Create Project

```bash
oc new-project project-ape
```

### Create Secrets

```bash
# API keys
oc create secret generic ape-env \
  --from-file=.env=.env

# Service account
oc create secret generic ape-service-account \
  --from-file=service-account.json=jasoande-3aec1043e544.json
```

### Create ConfigMap for Client Data

```bash
# If client data is small enough for ConfigMap
oc create configmap ape-client-data \
  --from-file=test_client_data/

# For larger data, use PersistentVolumeClaim instead
```

### Deploy

```bash
# Create deployment
oc new-app project-ape:latest \
  --name=project-ape

# Mount secrets
oc set volume deployment/project-ape \
  --add --type=secret \
  --secret-name=ape-env \
  --mount-path=/opt/project-ape/.env \
  --sub-path=.env

oc set volume deployment/project-ape \
  --add --type=secret \
  --secret-name=ape-service-account \
  --mount-path=/opt/project-ape/service-account.json \
  --sub-path=service-account.json

# Expose dashboard
oc expose service/project-ape --port=8765

# Get route
oc get route project-ape
```

---

## Podman Compose (Alternative)

### Create `compose.yaml`

```yaml
version: '3.8'

services:
  project-ape:
    image: project-ape:latest
    container_name: project-ape
    ports:
      - "8765:8765"
    volumes:
      - ./.env:/opt/project-ape/.env:ro
      - ./jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro
      - ./test_client_data:/opt/project-ape/test_client_data:ro
      - ./logs:/opt/project-ape/logs:rw
      - ./.multi_process_status:/opt/project-ape/.multi_process_status:rw
    environment:
      - PYTHONUNBUFFERED=1
    command: ["main.py", "--mode", "fast"]
    restart: unless-stopped
```

### Run with Compose

```bash
# Start
podman-compose up

# Stop
podman-compose down

# View logs
podman-compose logs -f
```

---

## Container Features

### Security

✅ **Non-root user** (UID 1001)
- Runs as `apeuser` for security
- OpenShift-compatible

✅ **Read-only mounts** for secrets
- `.env` and service account are `:ro`
- Prevents accidental modification

✅ **Minimal attack surface**
- Only essential packages installed
- No unnecessary services

### Performance

✅ **Layer caching**
- `requirements.txt` copied separately
- Python deps cached for faster rebuilds

✅ **Headless LibreOffice**
- No GUI overhead
- PDF conversion optimized

✅ **Multi-process support**
- Runs 6 clients in parallel
- Dashboard updates in real-time

### Monitoring

✅ **Health check**
- Automatically checks dashboard endpoint
- Restart on failure

✅ **Real-time logs**
```bash
# Podman
podman logs -f project-ape

# Docker
docker logs -f project-ape
```

✅ **Dashboard access**
- http://localhost:8765
- Real-time progress tracking
- Timer persists across refresh

---

## Troubleshooting

### Container won't start

**Check logs:**
```bash
podman logs project-ape
```

**Common issues:**
- Missing `.env` file
- Invalid API keys
- Service account not mounted

### Can't access dashboard

**Verify port mapping:**
```bash
podman port project-ape
```

**Check if dashboard is running:**
```bash
podman exec project-ape curl -f http://localhost:8765/status
```

### Permission denied errors

**Verify file permissions:**
```bash
ls -la .env jasoande-3aec1043e544.json
```

**Should be readable:**
```bash
chmod 644 .env
chmod 644 jasoande-3aec1043e544.json
```

### NotebookLM authentication fails

**Run interactive shell:**
```bash
podman run -it --rm \
  -v $(pwd)/.env:/opt/project-ape/.env:ro \
  project-ape:latest /bin/bash

# Inside container:
notebooklm login
```

### LibreOffice PDF conversion fails

**Check LibreOffice installation:**
```bash
podman exec project-ape libreoffice --version
```

**Test conversion:**
```bash
podman exec project-ape libreoffice --headless --convert-to pdf test.docx
```

---

## Building for Production

### Multi-arch Build (amd64 + arm64)

```bash
# Using buildah (RHEL/Fedora)
buildah build --platform linux/amd64,linux/arm64 \
  -t project-ape:latest \
  -f Containerfile .

# Push to registry
podman tag project-ape:latest quay.io/yourorg/project-ape:latest
podman push quay.io/yourorg/project-ape:latest
```

### Using Red Hat Registry

```bash
# Login to Red Hat registry
podman login registry.redhat.io

# Build with Red Hat UBI
podman build -t project-ape:rhel9 -f Containerfile .

# Tag for internal registry
podman tag project-ape:rhel9 registry.redhat.io/yourorg/project-ape:rhel9

# Push
podman push registry.redhat.io/yourorg/project-ape:rhel9
```

---

## Container Size Optimization

Current size: ~800MB (includes LibreOffice + Python deps)

### To reduce size:

1. **Use slim Python image** (if LibreOffice not needed)
2. **Multi-stage build** (build deps in one stage, copy to minimal runtime)
3. **Clean DNF cache** (already done: `dnf clean all`)

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Container

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build container
        run: |
          podman build -t project-ape:${{ github.sha }} -f Containerfile .
          
      - name: Push to registry
        run: |
          podman push project-ape:${{ github.sha }} quay.io/yourorg/project-ape:${{ github.sha }}
```

### GitLab CI

```yaml
build-container:
  stage: build
  image: registry.access.redhat.com/ubi9/ubi:latest
  script:
    - dnf install -y podman
    - podman build -t project-ape:$CI_COMMIT_SHA -f Containerfile .
    - podman push project-ape:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

---

## Comparison: Container vs Native

| Feature | Container | Native (Mac) |
|---------|-----------|--------------|
| **Platform** | Any Linux, OpenShift | macOS only |
| **Setup** | `podman build` | Install Python, LibreOffice |
| **Isolation** | Full | Shared system |
| **Portability** | ✅ High | ❌ Mac-only |
| **Performance** | ~5% overhead | Native |
| **Scaling** | Kubernetes/OpenShift | Manual |
| **Security** | Non-root, isolated | User account |

---

## Support Matrix

| Platform | Podman | Docker | OpenShift |
|----------|--------|--------|-----------|
| **RHEL 9** | ✅ Native | ✅ Supported | ✅ Native |
| **Fedora** | ✅ Native | ✅ Supported | ✅ Via Podman |
| **Ubuntu** | ✅ Available | ✅ Native | ✅ Via K8s |
| **Windows WSL** | ✅ Available | ✅ Native | ✅ Via Docker Desktop |
| **macOS** | ✅ Podman Desktop | ✅ Docker Desktop | N/A |

---

## Production Checklist

- [ ] `.env` file configured with production API keys
- [ ] Service account JSON has proper permissions
- [ ] Client data volume mounted correctly
- [ ] Logs volume mounted for persistence
- [ ] Dashboard port (8765) accessible
- [ ] Health check passing
- [ ] Resource limits set (CPU/memory)
- [ ] Secrets managed securely (not in image)
- [ ] Container scanned for vulnerabilities
- [ ] Monitoring/alerting configured

---

**Created By:** Jason Anderson  
**Base Image:** RHEL 9 UBI (registry.access.redhat.com/ubi9/ubi:latest)  
**Version:** 3.0.5  
**Date:** June 16, 2026  
**Status:** Production Ready
