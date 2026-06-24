# Project APE - Podman Container Guide

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="120"/>
</p>

<h3 align="center">Container Operations Guide</h3>

<p align="center">
  Jason Anderson | Project Owner & Maintainer
</p>

---

**Last Updated:** June 12, 2026  
**Container Runtime:** Podman (Docker alternative)  
**Base Image:** Python 3.13-slim

---

## Quick Start

### 1. Install Podman

```bash
# Automated installation
./podman-install.sh

# Or manual installation:
# macOS
brew install podman
podman machine init
podman machine start

# RHEL/Fedora
sudo dnf install podman podman-compose

# Debian/Ubuntu
sudo apt install podman
```

### 2. Build Container

```bash
./build-container.sh
```

### 3. Run Container

```bash
# Fast mode (all clients)
./run-container.sh --mode fast

# Deep mode (single client)
./run-container.sh --mode deep --clients merck_test

# Fast mode (multiple clients)
./run-container.sh --mode fast --clients merck_test,blue_yonder_test
```

### 4. Access Dashboard

Open browser: **http://localhost:8765**

---

## Container Architecture

### Multi-Stage Build

**Stage 1: Builder**
- Compiles Python packages with C extensions
- Creates virtual environment
- ~500 MB

**Stage 2: Runtime**
- Slim Python base image
- LibreOffice for document conversion
- Node.js + NotebookLM CLI
- Non-root user for security
- ~800 MB final size

### Included Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13-slim | Runtime |
| LibreOffice | Latest | PDF conversion |
| Node.js | 18.x | NotebookLM CLI |
| NotebookLM CLI | Latest | Google API |

---

## Volume Mounts

### Required Volumes

```bash
# Client data (read-only recommended)
-v ./Venella_2026:/app/Venella_2026:ro

# Configuration
-v ./vars.py:/app/vars.py:ro

# Logs (persistent)
-v ./logs:/app/logs

# Status files
-v ./.multi_process_status:/app/.multi_process_status

# NotebookLM credentials
-v ${HOME}/.notebooklm:/home/apeuser/.notebooklm:ro
```

### Optional Volumes

```bash
# Custom prompt files
-v ./custom_prompts:/app/custom_prompts:ro

# Alternative client data location
-v /path/to/clients:/app/client_data:ro
```

---

## Usage Examples

### Using Shell Scripts

```bash
# Fast mode - all clients
./run-container.sh --mode fast

# Deep mode - single client
./run-container.sh --mode deep --clients merck_test

# Fast mode - specific clients
./run-container.sh --mode fast --clients merck_test,organon_test
```

### Using Podman Directly

```bash
# Run interactively
podman run -it --rm \
  -p 8765:8765 \
  -v ./Venella_2026:/app/Venella_2026:ro \
  -v ./vars.py:/app/vars.py:ro \
  -v ./logs:/app/logs \
  -v ${HOME}/.notebooklm:/home/apeuser/.notebooklm:ro \
  project-ape:latest \
  python3 main.py --mode fast

# Run in background (detached)
podman run -d \
  --name project-ape \
  -p 8765:8765 \
  -v ./Venella_2026:/app/Venella_2026:ro \
  -v ./vars.py:/app/vars.py:ro \
  -v ./logs:/app/logs \
  -v ${HOME}/.notebooklm:/home/apeuser/.notebooklm:ro \
  project-ape:latest \
  python3 main.py --mode deep --clients merck_test

# View logs
podman logs -f project-ape

# Stop container
podman stop project-ape
```

### Using Podman Compose

```bash
# Start services
podman-compose up

# Start in background
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Rebuild and start
podman-compose up --build
```

---

## Management Commands

### Container Lifecycle

```bash
# List running containers
podman ps

# List all containers
podman ps -a

# Stop container
podman stop project-ape

# Remove container
podman rm project-ape

# Restart container
podman restart project-ape
```

### Image Management

```bash
# List images
podman images

# Remove image
podman rmi project-ape:latest

# Prune unused images
podman image prune

# Save image to file
podman save -o project-ape.tar project-ape:latest

# Load image from file
podman load -i project-ape.tar
```

### Debugging

```bash
# Enter running container
podman exec -it project-ape /bin/bash

# View container logs
podman logs project-ape

# Follow logs in real-time
podman logs -f project-ape

# Inspect container
podman inspect project-ape

# View resource usage
podman stats project-ape
```

---

## Authentication Setup

### NotebookLM Authentication

**Option 1: Host credentials (recommended)**

```bash
# Login on host first
notebooklm login

# Mount credentials into container
-v ${HOME}/.notebooklm:/home/apeuser/.notebooklm:ro
```

**Option 2: Interactive login in container**

```bash
# Run container interactively
podman run -it --rm project-ape:latest /bin/bash

# Inside container
notebooklm login
```

**Option 3: Environment variables**

```bash
# Set credentials as environment variables
podman run \
  -e NOTEBOOKLM_TOKEN=<your-token> \
  project-ape:latest
```

---

## Resource Limits

### Memory Limits

```bash
# Limit to 4GB RAM
podman run --memory=4g project-ape:latest

# Set memory reservation
podman run --memory=4g --memory-reservation=2g project-ape:latest
```

### CPU Limits

```bash
# Limit to 2 CPUs
podman run --cpus=2 project-ape:latest

# Set CPU shares (relative weight)
podman run --cpu-shares=512 project-ape:latest
```

### Combined Limits (in podman-compose.yml)

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '2.0'
      memory: 2G
```

---

## Networking

### Port Mapping

```bash
# Default dashboard port
-p 8765:8765

# Custom host port
-p 9000:8765

# All interfaces
-p 0.0.0.0:8765:8765

# Localhost only
-p 127.0.0.1:8765:8765
```

### Network Modes

```bash
# Bridge (default)
--network bridge

# Host (use host networking)
--network host

# None (no networking)
--network none
```

---

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/project-ape.service`:

```ini
[Unit]
Description=Project APE Container
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Project-APE
ExecStart=/usr/bin/podman run \
  --name project-ape \
  --rm \
  -p 8765:8765 \
  -v /path/to/Venella_2026:/app/Venella_2026:ro \
  -v /path/to/vars.py:/app/vars.py:ro \
  -v /path/to/logs:/app/logs \
  project-ape:latest
ExecStop=/usr/bin/podman stop project-ape
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ape
sudo systemctl start project-ape
sudo systemctl status project-ape
```

### Auto-Start on Boot (macOS)

```bash
# Start Podman machine on boot
podman machine set --rootful
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
podman logs project-ape

# Check if port is already in use
lsof -i :8765

# Check image exists
podman images project-ape
```

### Permission errors

```bash
# Check volume permissions
ls -la ./logs ./Venella_2026

# Run with correct user mapping
podman run --userns=keep-id project-ape:latest
```

### LibreOffice conversion fails

```bash
# Enter container and test
podman exec -it project-ape /bin/bash
libreoffice --headless --convert-to pdf test.docx
```

### NotebookLM authentication fails

```bash
# Verify credentials mounted correctly
podman exec -it project-ape /bin/bash
ls -la /home/apeuser/.notebooklm

# Re-login on host
notebooklm logout
notebooklm login
```

---

## Performance Tips

### 1. Use Named Volumes for Logs

```bash
# Create named volume
podman volume create ape-logs

# Use in container
-v ape-logs:/app/logs
```

### 2. Enable BuildKit

```bash
# Build with BuildKit for faster builds
podman build --format docker .
```

### 3. Layer Caching

```bash
# Rebuild without cache
podman build --no-cache .

# Use cache (faster rebuilds)
podman build .
```

### 4. Multi-CPU Builds

```bash
# Use all available CPUs during build
podman build --jobs=4 .
```

---

## Security Considerations

### 1. Non-Root User

Container runs as `apeuser` (UID 1000), not root.

### 2. Read-Only Volumes

```bash
# Mount client data read-only
-v ./Venella_2026:/app/Venella_2026:ro
```

### 3. No Privileged Mode

Never run with `--privileged` flag.

### 4. Network Isolation

```bash
# Disable network if not needed
--network none
```

### 5. Resource Limits

Always set memory/CPU limits in production.

---

## CI/CD Integration

### Build in Pipeline

```bash
# GitLab CI
script:
  - podman build -t project-ape:${CI_COMMIT_SHA} .
  - podman push project-ape:${CI_COMMIT_SHA}

# GitHub Actions
- name: Build container
  run: |
    podman build -t project-ape:latest .
    podman save -o project-ape.tar project-ape:latest
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `Containerfile` | Container build instructions |
| `.containerignore` | Files excluded from build |
| `podman-compose.yml` | Compose configuration |
| `build-container.sh` | Build automation script |
| `run-container.sh` | Run automation script |
| `podman-install.sh` | Podman installation script |
| `CONTAINER_GUIDE.md` | This file |

---

## Support

**Container Issues:**
- Check logs: `podman logs project-ape`
- Inspect: `podman inspect project-ape`
- Debug: `podman exec -it project-ape /bin/bash`

**Build Issues:**
- Clean build: `podman build --no-cache .`
- Check Containerfile syntax
- Verify base image available

**Runtime Issues:**
- Check volume mounts
- Verify port availability
- Check resource limits

---

## Why Podman vs Docker?

✅ **Daemonless** - No background daemon required  
✅ **Rootless** - Run containers as non-root user  
✅ **Pod support** - Kubernetes-style pod management  
✅ **Compatible** - Uses same Dockerfile/Containerfile format  
✅ **Systemd integration** - Native systemd support  
✅ **Security** - Better default security posture  

---

**Project APE - Container Operations Guide**  
Version 3.0.4 | Jason Anderson | 2026
