<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE Logo" width="150"/>
  
  # Deployment Guide
  **Project APE - Container Deployment**
  
  Version 4.0.1 | Production Ready
</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Building Containers](#building-containers)
4. [Multi-Architecture Builds](#multi-architecture-builds)
5. [Registry Management](#registry-management)
6. [Production Deployment](#production-deployment)
7. [Credential Management](#credential-management)
8. [Scaling Considerations](#scaling-considerations)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Project APE is designed for **container-first deployment** using Podman or Docker. This guide covers building, publishing, and deploying containerized workflows.

### Deployment Models

| Model | Best For | Complexity |
|-------|----------|-----------|
| **Single Container** | Development, single-user | Low |
| **Multi-Host** | Production, multiple users | Medium |
| **Kubernetes** | Enterprise, auto-scaling | High |

This guide focuses on **single container** and **multi-host** deployments.

---

## Prerequisites

### System Requirements

**Build Host:**
- Podman 4.0+ or Docker 20.10+
- 8GB RAM (for multi-arch builds)
- 20GB disk space
- Linux, macOS, or Windows

**Deployment Host:**
- Podman 4.0+ or Docker 20.10+
- 4GB RAM minimum
- 10GB disk space
- Linux (recommended) or macOS

### Accounts and Access

- **Quay.io Account** (or alternative registry)
- **NotebookLM Credentials** (OAuth)
- **Google Drive OAuth Credentials**

---

## Building Containers

### Local Build (Current Architecture)

```bash
# Clone repository
git clone https://github.com/yourusername/project-ape.git
cd project-ape

# Build for current platform
podman build -t project-ape:latest -f Containerfile.debian .

# Verify build
podman images | grep project-ape
```

**Expected output:**
```
project-ape   latest   abc123def456   2 minutes ago   1.2 GB
```

### Build Process Breakdown

The build executes these layers:

1. **Base Image** (`ubi9/python-311`)
   - Red Hat Universal Base Image 9
   - Python 3.11 pre-installed
   - Minimal attack surface

2. **System Dependencies**
   ```dockerfile
   RUN dnf install -y git gcc python3-devel && dnf clean all
   ```

3. **Python Dependencies**
   ```dockerfile
   COPY requirements.txt /tmp/
   RUN pip install --no-cache-dir -r /tmp/requirements.txt
   ```

4. **NotebookLM CLI**
   ```dockerfile
   RUN pip install --no-cache-dir notebooklm
   ```

5. **Application Code**
   ```dockerfile
   COPY core/ /app/core/
   COPY dashboard/ /app/dashboard/
   COPY *.py /app/
   ```

6. **User Setup** (Non-root)
   ```dockerfile
   RUN useradd -u 1000 -r -g 0 -m -d /opt/app-root -s /sbin/nologin apeuser
   USER 1000
   ```

7. **Entrypoint**
   ```dockerfile
   ENTRYPOINT ["/app/container-entrypoint.sh"]
   ```

**Build Time**: 5-10 minutes (first build), 1-2 minutes (cached)

---

## Multi-Architecture Builds

### Supported Architectures

- **linux/amd64** (x86_64) - Intel/AMD servers, most cloud VMs
- **linux/arm64** (aarch64) - Apple Silicon, ARM servers, AWS Graviton

### Building Multi-Arch Images

**Using Podman:**

```bash
# Install QEMU (for cross-platform emulation)
sudo dnf install -y qemu-user-static  # RHEL/Fedora
sudo apt-get install -y qemu-user-static  # Ubuntu/Debian

# Build for multiple architectures
podman build \
  --platform linux/amd64,linux/arm64 \
  -t project-ape:4.0.1 \
  -t project-ape:latest \
  -f Containerfile.debian .
```

**Using Docker (with buildx):**

```bash
# Create buildx builder
docker buildx create --name multiarch --use

# Build and push
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:4.0.1 \
  -t quay.io/jasoande/project_ape/project-ape:latest \
  --push \
  -f Containerfile.debian .
```

**Build Time**: 15-25 minutes (multi-arch)

### Automated Build Script

Use the provided build script for consistent builds:

```bash
# Build multi-arch and push to registry
./developer-docs/build-and-push-containers.sh

# The script will:
# 1. Prompt for version tag
# 2. Build for linux/amd64 and linux/arm64
# 3. Tag with version and 'latest'
# 4. Push to quay.io registry
# 5. Verify manifest
```

**Script features:**
- Version validation
- Multi-arch build support
- Automatic tagging
- Push to registry
- Manifest verification
- Build logging

---

## Registry Management

### Quay.io (Recommended)

**Advantages:**
- Free public repositories
- Multi-arch manifest support
- Vulnerability scanning
- Web UI for management

**Setup:**

1. **Create Quay.io Account**
   - Visit: https://quay.io/signin
   - Sign up or login

2. **Create Repository**
   - Click "Create New Repository"
   - Name: `project_ape/project-ape`
   - Visibility: Public or Private
   - Click "Create Public Repository"

3. **Login to Registry**
   ```bash
   # Login with username and password
   podman login quay.io
   ```

4. **Tag Image**
   ```bash
   podman tag project-ape:latest quay.io/jasoande/project_ape/project-ape:4.0.1
   podman tag project-ape:latest quay.io/jasoande/project_ape/project-ape:latest
   ```

5. **Push to Registry**
   ```bash
   podman push quay.io/jasoande/project_ape/project-ape:4.0.1
   podman push quay.io/jasoande/project_ape/project-ape:latest
   ```

**Verify in Quay.io:**
- Navigate to: https://quay.io/repository/jasoande/project_ape/project-ape
- Check "Tags" tab for `4.0.1` and `latest`
- Verify "Manifest List" shows both architectures

### Alternative Registries

**Docker Hub:**
```bash
docker login
docker tag project-ape:latest username/project-ape:4.0.1
docker push username/project-ape:4.0.1
```

**GitHub Container Registry:**
```bash
echo $GITHUB_TOKEN | podman login ghcr.io -u USERNAME --password-stdin
podman tag project-ape:latest ghcr.io/username/project-ape:4.0.1
podman push ghcr.io/username/project-ape:4.0.1
```

**Private Registry:**
```bash
podman login registry.example.com
podman tag project-ape:latest registry.example.com/project-ape:4.0.1
podman push registry.example.com/project-ape:4.0.1
```

---

## Production Deployment

### Deployment Workflow

```
1. Prepare Host
   ├─> Install Podman/Docker
   ├─> Create directories
   └─> Set permissions

2. Configure Credentials
   ├─> Setup NotebookLM auth
   ├─> Setup Drive OAuth
   └─> Create credentials volume

3. Configure Application
   ├─> Create vars.py
   └─> Validate configuration

4. Pull Image
   └─> podman pull quay.io/.../project-ape:4.0.1

5. Run Container
   └─> Execute with volume mounts

6. Monitor Execution
   ├─> Dashboard: http://localhost:8765
   └─> Logs: tail -f logs/overall.log
```

### Step-by-Step Deployment

#### 1. Prepare Host

```bash
# Install Podman (RHEL/Fedora)
sudo dnf install -y podman

# Install Podman (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y podman

# Verify installation
podman --version
```

#### 2. Create Directory Structure

```bash
# Create project directory
mkdir -p ~/project-ape-prod
cd ~/project-ape-prod

# Create subdirectories
mkdir -p logs docs_generated client_data

# Set permissions (if running as non-root)
chmod 755 logs docs_generated client_data
```

#### 3. Setup Credentials

**NotebookLM Authentication:**

```bash
# Install NotebookLM CLI on host
pip install notebooklm

# Login (requires Chrome browser)
notebooklm login

# Verify credentials
ls -la ~/.notebooklm/credentials.json

# Create credentials volume
podman volume create project-ape-credentials

# Copy credentials to volume
podman run --rm \
  -v ~/.notebooklm:/source:ro \
  -v project-ape-credentials:/dest \
  alpine cp -r /source/. /dest/

# Verify volume
podman volume inspect project-ape-credentials
```

**Google Drive OAuth:**

```bash
# Download setup script
wget https://raw.githubusercontent.com/yourusername/project-ape/main/setup-oauth-drive-improved.py

# Run OAuth setup
python3 setup-oauth-drive-improved.py

# Verify credentials
ls -la ~/.project-ape/drive_credentials.json
ls -la ~/.project-ape/drive_token.json

# Copy to project directory (for container mount)
cp ~/.project-ape/drive_credentials.json ~/project-ape-prod/
cp ~/.project-ape/drive_token.json ~/project-ape-prod/
chmod 600 ~/project-ape-prod/drive_*.json
```

#### 4. Create Configuration

```bash
# Download example configuration
wget https://raw.githubusercontent.com/yourusername/project-ape/main/developer-docs/example-vars.py -O vars.py

# Edit configuration
vi vars.py
```

**Production vars.py example:**

```python
# Production Configuration
clients = ["acme_corp", "techstart_inc", "globalbank"]

# Acme Corporation
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/ABC123"
acme_corp_industry = ""
acme_corp_subsegments = "cloud, AI, cybersecurity"

# TechStart Inc
techstart_inc_name = "TechStart Inc"
techstart_inc_folder = "https://drive.google.com/drive/folders/DEF456"
techstart_inc_industry = "technology"
techstart_inc_subsegments = "SaaS, DevOps"

# GlobalBank
globalbank_name = "GlobalBank LLC"
globalbank_folder = "https://drive.google.com/drive/folders/GHI789"
globalbank_industry = "financial_services"
globalbank_subsegments = "banking, fintech"

# Global Settings
persona = "solutions architect"
default_mode = "fast"
DASHBOARD_PORT = 8765
```

#### 5. Pull Image

```bash
# Pull specific version
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1

# Verify image
podman images | grep project-ape
```

#### 6. Run Production Container

**Single Execution:**

```bash
podman run -it --rm \
  --name project-ape-run \
  -v ~/project-ape-prod/vars.py:/app/vars.py:ro,z \
  -v ~/project-ape-prod/drive_credentials.json:/app/drive_credentials.json:ro,z \
  -v ~/project-ape-prod/drive_token.json:/app/drive_token.json:ro,z \
  -v ~/project-ape-prod/logs:/app/logs:z \
  -v ~/project-ape-prod/docs_generated:/app/docs_generated:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -p 8765:8765 \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients acme_corp,techstart_inc --mode fast
```

**Background Execution:**

```bash
podman run -d \
  --name project-ape-run \
  -v ~/project-ape-prod/vars.py:/app/vars.py:ro,z \
  -v ~/project-ape-prod/drive_credentials.json:/app/drive_credentials.json:ro,z \
  -v ~/project-ape-prod/drive_token.json:/app/drive_token.json:ro,z \
  -v ~/project-ape-prod/logs:/app/logs:z \
  -v ~/project-ape-prod/docs_generated:/app/docs_generated:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  -p 8765:8765 \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients acme_corp,techstart_inc --mode fast

# Monitor logs
podman logs -f project-ape-run

# Check status
podman ps | grep project-ape
```

### Volume Mount Explanations

| Volume | Source (Host) | Target (Container) | Flags | Purpose |
|--------|--------------|-------------------|-------|---------|
| Configuration | `~/project-ape-prod/vars.py` | `/app/vars.py` | `ro,z` | Read-only config |
| Drive Credentials | `~/project-ape-prod/drive_credentials.json` | `/app/drive_credentials.json` | `ro,z` | OAuth client secrets |
| Drive Token | `~/project-ape-prod/drive_token.json` | `/app/drive_token.json` | `ro,z` | OAuth access token |
| Logs | `~/project-ape-prod/logs` | `/app/logs` | `z` | Execution logs |
| Outputs | `~/project-ape-prod/docs_generated` | `/app/docs_generated` | `z` | Generated documents |
| NotebookLM Creds | `project-ape-credentials` (volume) | `/opt/app-root/src/.notebooklm` | `z` | NotebookLM credentials |

**Flags:**
- `ro` - Read-only mount
- `z` - SELinux private label (required on RHEL/Fedora)

---

## Credential Management

### Production Credential Storage

**Best Practices:**

1. **Never commit credentials to version control**
   ```bash
   # Verify .gitignore
   cat .gitignore | grep -E "(credentials|token)"
   ```

2. **Use environment-specific credential directories**
   ```bash
   # Development
   ~/.project-ape/drive_credentials.json
   
   # Production
   /opt/project-ape/credentials/drive_credentials.json
   ```

3. **Set restrictive permissions**
   ```bash
   chmod 600 /opt/project-ape/credentials/*.json
   chown apeuser:apeuser /opt/project-ape/credentials/*.json
   ```

4. **Rotate credentials regularly**
   - OAuth tokens: Auto-refresh (90-day expiry)
   - Client secrets: Rotate annually
   - Delete unused credentials

### Credential Backup

```bash
# Backup credentials (encrypted)
tar -czf credentials-backup-$(date +%Y%m%d).tar.gz \
  ~/.notebooklm/credentials.json \
  ~/.project-ape/drive_credentials.json \
  ~/.project-ape/drive_token.json

# Encrypt backup
gpg --symmetric credentials-backup-$(date +%Y%m%d).tar.gz

# Store securely (delete unencrypted version)
rm credentials-backup-$(date +%Y%m%d).tar.gz
```

### Multi-User Deployments

**Scenario**: Multiple users running Project APE on shared host

**Solution**: User-specific credential volumes

```bash
# User 1
podman volume create user1-ape-credentials
podman run ... -v user1-ape-credentials:/opt/app-root/src/.notebooklm ...

# User 2
podman volume create user2-ape-credentials
podman run ... -v user2-ape-credentials:/opt/app-root/src/.notebooklm ...
```

---

## Scaling Considerations

### Horizontal Scaling

**Scenario**: Process 20+ clients across multiple hosts

**Approach**: Distribute clients across hosts

**Host 1** (clients 1-5):
```bash
podman run ... --clients client1,client2,client3,client4,client5 --mode fast
```

**Host 2** (clients 6-10):
```bash
podman run ... --clients client6,client7,client8,client9,client10 --mode fast
```

**Benefits:**
- Parallel execution across hosts
- Reduced API quota impact per host
- Fault isolation (host failure affects only subset)

### Resource Limits

**Set CPU and memory limits:**

```bash
podman run -it --rm \
  --cpus=4 \
  --memory=8g \
  --memory-swap=8g \
  -v ~/project-ape-prod/vars.py:/app/vars.py:ro,z \
  ... \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients acme_corp --mode fast
```

**Recommended Limits:**

| Clients | CPUs | Memory | Swap |
|---------|------|--------|------|
| 1-2 | 2 | 4GB | 4GB |
| 3-5 | 4 | 8GB | 8GB |
| 6+ | 6+ | 12GB+ | 12GB+ |

### API Quota Management

**NotebookLM API Quotas:**
- Default: ~100 requests/minute
- Deep mode: Higher retry rate (~30%)

**Mitigation:**
1. **Stagger executions** (don't start all at once)
2. **Use fast mode** for most accounts
3. **Increase delays** in `TIMINGS` configuration
4. **Distribute across multiple Google accounts** (enterprise)

---

## Monitoring and Logging

### Dashboard Access

**Local Access:**
```
http://localhost:8765
```

**Remote Access** (via SSH tunnel):
```bash
# On local machine
ssh -L 8765:localhost:8765 user@remote-host

# Open in browser
http://localhost:8765
```

**Firewall Access** (production):
```bash
# Open port 8765 (use with caution)
sudo firewall-cmd --add-port=8765/tcp --permanent
sudo firewall-cmd --reload

# Access from network
http://<host-ip>:8765
```

### Log Management

**Real-Time Logs:**
```bash
# Overall log
tail -f ~/project-ape-prod/logs/overall.log

# Specific client
tail -f ~/project-ape-prod/logs/acme_corp.log

# All clients
tail -f ~/project-ape-prod/logs/*.log
```

**Container Logs:**
```bash
# View container stdout/stderr
podman logs project-ape-run

# Follow logs
podman logs -f project-ape-run

# Last 100 lines
podman logs --tail 100 project-ape-run
```

**Log Rotation:**

```bash
# Install logrotate configuration
cat > /etc/logrotate.d/project-ape <<EOF
/home/user/project-ape-prod/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 user user
}
EOF

# Test rotation
sudo logrotate -f /etc/logrotate.d/project-ape
```

### Health Checks

**Container Health:**
```bash
# Check if container is running
podman ps | grep project-ape

# Check container status
podman inspect project-ape-run | jq '.[0].State'

# Verify resource usage
podman stats project-ape-run
```

**Application Health:**
```bash
# Check dashboard availability
curl -I http://localhost:8765

# Check status endpoint
curl http://localhost:8765/status | jq
```

---

## Troubleshooting

### Container Won't Start

**Issue**: Container exits immediately

**Diagnosis:**
```bash
# Check container logs
podman logs project-ape-run

# Inspect container
podman inspect project-ape-run

# Check exit code
podman inspect project-ape-run | jq '.[0].State.ExitCode'
```

**Common Causes:**

1. **Missing credentials**
   ```bash
   # Verify volume mounts
   podman run --rm -v project-ape-credentials:/creds alpine ls -la /creds
   ```

2. **Invalid configuration**
   ```bash
   # Test vars.py syntax
   python3 -c "exec(open('vars.py').read()); print('Configuration valid')"
   ```

3. **Permission errors**
   ```bash
   # Check SELinux context
   ls -Z ~/project-ape-prod/
   
   # Relabel if needed
   chcon -Rt svirt_sandbox_file_t ~/project-ape-prod/
   ```

### Credential Issues

**Issue**: "Authentication failed" error

**Solution:**

```bash
# Re-authenticate NotebookLM
notebooklm login

# Recreate credentials volume
podman volume rm project-ape-credentials
podman volume create project-ape-credentials

# Copy credentials
podman run --rm \
  -v ~/.notebooklm:/source:ro \
  -v project-ape-credentials:/dest \
  alpine cp -r /source/. /dest/
```

### Network Issues

**Issue**: Dashboard not accessible

**Solution:**

```bash
# Check port binding
podman port project-ape-run

# Verify firewall
sudo firewall-cmd --list-ports

# Check if port is in use
lsof -i :8765
```

### Performance Issues

**Issue**: Slow execution or high retry rate

**Solution:**

1. **Increase resource limits**
   ```bash
   podman update --cpus=6 --memory=12g project-ape-run
   ```

2. **Adjust timing configuration** (in `vars.py`)
   ```python
   TIMINGS = {
       'ask_prompt_delay': (15.0, 20.0),  # Increase delays
       'chat_prompt_delay': (10.0, 12.0),
   }
   ```

3. **Reduce parallel clients**
   ```bash
   # Process fewer clients at once
   podman run ... --clients client1,client2 --mode fast
   ```

### Multi-Architecture Issues

**Issue**: "Platform mismatch" error

**Solution:**

```bash
# Pull specific architecture
podman pull --platform linux/amd64 quay.io/.../project-ape:4.0.1

# Or build locally for current arch
podman build -t project-ape:latest -f Containerfile.debian .
```

---

## Production Checklist

Before deploying to production:

- ✅ **Build and tag** container with version number
- ✅ **Push to registry** (Quay.io or private registry)
- ✅ **Setup credentials** (NotebookLM + Drive OAuth)
- ✅ **Create vars.py** with production client configuration
- ✅ **Test run** single client in fast mode
- ✅ **Verify outputs** in `docs_generated/`
- ✅ **Setup log rotation** for long-term logging
- ✅ **Document** credential locations and access procedures
- ✅ **Backup credentials** (encrypted)
- ✅ **Setup monitoring** (dashboard access, health checks)

---

## Automation

### Scheduled Runs (Cron)

**Weekly account research:**

```bash
# Create cron script
cat > /opt/project-ape/scripts/weekly-run.sh <<'EOF'
#!/bin/bash
cd /opt/project-ape/prod

podman run -it --rm \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./drive_credentials.json:/app/drive_credentials.json:ro,z \
  -v ./drive_token.json:/app/drive_token.json:ro,z \
  -v ./logs:/app/logs:z \
  -v ./docs_generated:/app/docs_generated:z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:z \
  quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --clients all --mode fast

# Archive outputs
tar -czf outputs-$(date +%Y%m%d).tar.gz docs_generated/
EOF

chmod +x /opt/project-ape/scripts/weekly-run.sh
```

**Add to crontab:**

```bash
# Run every Monday at 6 AM
crontab -e

# Add line:
0 6 * * 1 /opt/project-ape/scripts/weekly-run.sh >> /var/log/project-ape-cron.log 2>&1
```

---

**For additional deployment strategies and advanced configurations, consult the development team.**

Return to: [README.md](../README.md) | See also: [ARCHITECTURE.md](../Docs/ARCHITECTURE.md)
