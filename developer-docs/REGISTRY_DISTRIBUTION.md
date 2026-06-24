# Project APE - Container Registry Distribution Guide

**For Account Teams - No Dependencies Required!**

---

## Overview

Project APE is distributed as a **pre-built container image** via container registry. This means:

✅ **NO Python installation required**  
✅ **NO pip install required**  
✅ **NO LibreOffice installation required**  
✅ **NO Node.js/npm required**  
✅ **NO build process required**

Just install Podman, pull the image, and run!

---

## Architecture

### What's IN the Container Image (Pre-Built)

- ✅ Python 3.13
- ✅ All Python dependencies (17 packages)
- ✅ LibreOffice (for PDF conversion)
- ✅ Node.js + NotebookLM CLI
- ✅ Project APE application code

### What's PROVIDED at Runtime (You Provide)

- 📁 Your client data (mounted as volume)
- ⚙️ Your `vars.py` configuration (mounted as volume)
- 🔐 NotebookLM authentication (mounted from host)
- 📝 Logs directory (mounted for persistence)

---

## Quick Start (5 Minutes)

### Step 1: Install Podman (One-Time)

```bash
# macOS
brew install podman
podman machine init
podman machine start

# RHEL/Fedora
sudo dnf install podman

# Ubuntu/Debian
sudo apt install podman
```

### Step 2: Authenticate with NotebookLM (One-Time)

```bash
# Install NotebookLM CLI
npm install -g notebooklm

# Login
notebooklm login
```

### Step 3: Prepare Your Configuration

```bash
# Create vars.py with your clients
cat > vars.py << 'EOF'
clients = ["client1", "client2"]

client1_name = "Acme Corp"
client1_industry = "technology"
client1_folder = "/app/client_data/Acme"

client2_name = "Beta Inc"
client2_industry = "finance"
client2_folder = "/app/client_data/Beta"
EOF

# Organize your client data
mkdir -p client_data/Acme
mkdir -p client_data/Beta
# Copy your client files into these directories
```

### Step 4: Download and Run

```bash
# Download the runner script (distributed by your team)
curl -O https://your-server/ape-run.sh
chmod +x ape-run.sh

# Edit the script to set your registry details (one-time)
# Update: DEFAULT_NAMESPACE="your-org"

# Run!
./ape-run.sh --mode fast
```

**That's it!** Dashboard opens at http://localhost:8765

---

## Registry Setup (For Image Publisher)

### Publishing to Quay.io (Red Hat)

```bash
# 1. Build the image
./build-container.sh

# 2. Push to registry
./registry-push.sh --registry quay.io --namespace your-org

# Image available at:
# quay.io/your-org/project-ape:latest
# quay.io/your-org/project-ape:2.0.0
```

### Publishing to Docker Hub

```bash
./registry-push.sh --registry docker.io --namespace your-username
```

### Publishing to GitHub Container Registry

```bash
./registry-push.sh --registry ghcr.io --namespace your-org
```

### Publishing to Private Registry

```bash
./registry-push.sh --registry registry.company.com --namespace team
```

---

## For End Users (Account Teams)

### Simple Runner Script Usage

```bash
# Fast mode - all clients
./ape-run.sh --mode fast

# Deep mode - specific client
./ape-run.sh --mode deep --clients merck_test

# Custom paths
./ape-run.sh \
  --mode fast \
  --client-data /path/to/clients \
  --vars /path/to/vars.py \
  --logs /path/to/logs
```

### Manual Podman Commands

```bash
# Pull the image
podman pull quay.io/your-org/project-ape:latest

# Run with your data
podman run -it --rm \
  -p 8765:8765 \
  -v ./client_data:/app/client_data:ro \
  -v ./vars.py:/app/vars.py:ro \
  -v ./logs:/app/logs \
  -v ~/.notebooklm:/home/apeuser/.notebooklm:ro \
  quay.io/your-org/project-ape:latest \
  python3 main.py --mode fast
```

---

## Directory Structure for End Users

```
your-project-directory/
├── ape-run.sh              # Runner script (provided by you)
├── vars.py                 # Your configuration
├── client_data/            # Your client files
│   ├── Acme/
│   │   ├── doc1.pdf
│   │   ├── presentation.pptx
│   │   └── data.xlsx
│   └── Beta/
│       └── report.docx
└── logs/                   # Generated at runtime
    ├── client1.log
    └── client2.log
```

**No Python files, no requirements.txt, no build process!**

---

## NotebookLM Authentication (The Tricky Part)

### Option 1: Host Credentials (Recommended - Easiest)

```bash
# One-time setup on host
npm install -g notebooklm
notebooklm login

# Credentials automatically mounted
~/.notebooklm → /home/apeuser/.notebooklm (read-only)
```

**Pros:**
- ✅ Simple - login once on host
- ✅ Credentials persist across runs
- ✅ No container rebuild needed

**Cons:**
- ⚠️ Requires npm/notebooklm on host (one-time install)

### Option 2: Interactive Container Login (Alternative)

```bash
# Run container interactively
podman run -it --rm \
  -v ~/.notebooklm:/home/apeuser/.notebooklm \
  quay.io/your-org/project-ape:latest \
  /bin/bash

# Inside container
notebooklm login
exit

# Now run normally
./ape-run.sh --mode fast
```

**Pros:**
- ✅ No host dependencies

**Cons:**
- ⚠️ More complex first-time setup

### Option 3: Service Account (Advanced)

If your organization has a shared NotebookLM service account:

```bash
# Mount service account credentials
podman run -it --rm \
  -v /path/to/service-account/.notebooklm:/home/apeuser/.notebooklm:ro \
  quay.io/your-org/project-ape:latest
```

---

## Updating to New Versions

### For End Users

```bash
# Pull latest version
podman pull quay.io/your-org/project-ape:latest

# Or specific version
podman pull quay.io/your-org/project-ape:2.1.0

# Run as normal
./ape-run.sh --mode fast
```

**No rebuild, no dependency updates, just pull and run!**

### For Image Publisher

```bash
# Build new version
./build-container.sh

# Tag with new version
podman tag project-ape:latest project-ape:2.1.0

# Push to registry
./registry-push.sh \
  --namespace your-org \
  --tag 2.1.0

# Also push as latest
./registry-push.sh \
  --namespace your-org \
  --tag latest
```

---

## Distribution Workflow

### 1. Image Publisher (Your Team)

```bash
# Build generic image
./build-container.sh

# Push to registry
./registry-push.sh --namespace your-org

# Distribute runner script
# Share ape-run.sh with account teams
```

### 2. Account Teams (End Users)

```bash
# One-time setup
brew install podman && podman machine init && podman machine start
npm install -g notebooklm && notebooklm login

# Get runner script
curl -O https://your-server/ape-run.sh
chmod +x ape-run.sh

# Edit registry details in ape-run.sh
# DEFAULT_NAMESPACE="your-org"

# Create vars.py and add client data

# Run!
./ape-run.sh --mode fast
```

---

## Benefits of Registry Distribution

### For Image Publisher (You)

✅ **Build once, distribute many times**  
✅ **Version control** - Tag releases (v2.0.0, v2.1.0)  
✅ **Easy updates** - Just push new image  
✅ **Consistent environment** - Everyone uses same image  

### For Account Teams (End Users)

✅ **Zero dependency installation** - Just Podman  
✅ **No Python/pip/LibreOffice** hassle  
✅ **Fast setup** - 5 minutes from zero to running  
✅ **Easy updates** - Just pull new image  
✅ **No build failures** - Image pre-built and tested  

---

## Registry Options

### Public Registries (Free)

| Registry | URL | Best For |
|----------|-----|----------|
| Quay.io | quay.io | Open source, Red Hat backed |
| Docker Hub | docker.io | Most popular, familiar |
| GitHub | ghcr.io | GitHub integration |

### Private Registries

| Registry | Best For |
|----------|----------|
| Quay.io Private | Enterprise, RBAC |
| Harbor | Self-hosted, air-gapped |
| Artifactory | Enterprise, multi-format |
| AWS ECR | AWS deployments |
| Azure ACR | Azure deployments |

---

## Security Considerations

### Image Security

- ✅ **Non-root user** - Container runs as apeuser (UID 1000)
- ✅ **Read-only volumes** - Client data mounted read-only
- ✅ **Minimal base** - Python slim image
- ✅ **No secrets in image** - All auth at runtime
- ✅ **Signed images** - Can use Cosign for signing

### Credential Security

- ✅ **Host credentials** - Never baked into image
- ✅ **Read-only mount** - Credentials mounted read-only
- ✅ **Per-user auth** - Each user has own NotebookLM login
- ✅ **No shared secrets** - No hardcoded tokens

---

## Troubleshooting

### "Image not found"

```bash
# Check registry details
podman login quay.io
podman pull quay.io/your-org/project-ape:latest

# Verify image name
podman search quay.io/your-org/project-ape
```

### "NotebookLM authentication failed"

```bash
# Re-login on host
notebooklm logout
notebooklm login

# Verify credentials
ls -la ~/.notebooklm

# Check mount
podman run -it --rm \
  -v ~/.notebooklm:/home/apeuser/.notebooklm:ro \
  quay.io/your-org/project-ape:latest \
  ls -la /home/apeuser/.notebooklm
```

### "vars.py not found"

```bash
# Check file exists
ls -l vars.py

# Check permissions
chmod 644 vars.py

# Use absolute path
./ape-run.sh --vars /full/path/to/vars.py
```

### "Client data not found"

```bash
# Check directory structure
ls -la client_data/

# Use absolute path
./ape-run.sh --client-data /full/path/to/client_data
```

---

## Example: Enterprise Deployment

### Central IT Team

```bash
# Build and push image to internal registry
./build-container.sh
./registry-push.sh \
  --registry registry.company.com \
  --namespace sales-engineering

# Create distribution package
tar -czf project-ape-dist.tar.gz \
  ape-run.sh \
  example-vars.py \
  REGISTRY_DISTRIBUTION.md

# Distribute to account teams
# Upload to internal wiki/portal
```

### Account Team 1 (West Coast Sales)

```bash
# One-time setup
curl -O https://internal-wiki/project-ape-dist.tar.gz
tar -xzf project-ape-dist.tar.gz
podman machine init && podman machine start

# Configure for their clients
cp example-vars.py vars.py
# Edit vars.py for west coast clients

# Run
./ape-run.sh --mode fast
```

### Account Team 2 (East Coast Sales)

```bash
# Same setup, different clients
# No coordination needed, fully isolated
./ape-run.sh --mode deep --clients acme_corp
```

---

## Files Reference

| File | Purpose | Who Uses |
|------|---------|----------|
| `Containerfile` | Build definition | Image publisher |
| `build-container.sh` | Build automation | Image publisher |
| `registry-push.sh` | Registry push | Image publisher |
| `ape-run.sh` | **Simple runner** | **End users** |
| `vars.py` | Client config | End users |
| `client_data/` | Client files | End users |

---

## Summary

**For Image Publisher:**
1. Build once: `./build-container.sh`
2. Push: `./registry-push.sh --namespace your-org`
3. Distribute: Share `ape-run.sh` with teams

**For End Users:**
1. Install Podman (one-time)
2. Login to NotebookLM (one-time)
3. Edit `ape-run.sh` registry details (one-time)
4. Create `vars.py` and add client data
5. Run: `./ape-run.sh --mode fast`

**No dependencies, no builds, no hassle!** 🚀

---

**Registry distribution makes Project APE accessible to everyone!**
