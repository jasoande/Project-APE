# Project APE - Linux Deployment Guide

**Complete guide for deploying Project APE on RHEL9/Fedora/CentOS**

---

## Overview

This guide addresses Linux-specific issues when running Project APE in containers, particularly on RHEL9 with SELinux and podman.

---

## Common Issues on Linux

### 1. SELinux File Access Issues

**Symptom:**
```
❌ ERROR: vars.py not found or not readable
```

**Root Cause:** SELinux prevents container from reading host files without proper labels.

**Solution:** The `launch_ape.sh` script now automatically adds `:z` flags to volume mounts.

**Verify SELinux status:**
```bash
getenforce  # Should show: Enforcing
```

**Check file labels:**
```bash
ls -lZ vars.py
```

---

### 2. Directory Permission Issues

**Symptom:**
```
❌ Fatal error: [Errno 13] Permission denied: '/app/.multi_process_status/merck_test.json'
```

**Root Cause:** Container runs as non-root user (UID 1000, username: apeuser) but host directories are owned by your user (ec2-user, etc).

**Solution 1 - Use the fix script (Recommended):**
```bash
./fix-permissions.sh
```

**Solution 2 - Manual fix:**
```bash
# Remove old directories
rm -rf logs .multi_process_status

# Recreate with proper permissions
mkdir -p logs .multi_process_status
chmod 777 logs .multi_process_status

# Verify
ls -la | grep -E "(logs|multi_process_status)"
```

**Note:** The `launch_ape.sh` script automatically creates these directories with proper permissions, but if they existed before the script update, you need to fix them manually.

---

### 3. Architecture Detection

**Issue:** Script pulls wrong image (arm64 vs amd64)

**Solution:** The `launch_ape.sh` script now auto-detects architecture and pulls the correct image:
- x86_64/amd64 → `project-ape:3.0.5-amd64`
- aarch64/arm64 → `project-ape:3.0.5-arm64`

**Verify:**
```bash
uname -m  # Shows your architecture
```

---

## Updated Scripts

### launch_ape.sh

**New features:**
- ✅ Auto-detects architecture (amd64/arm64)
- ✅ Auto-detects runtime (podman/docker)
- ✅ Adds SELinux labels (`:z` flags) to volume mounts
- ✅ Creates directories with proper permissions (chmod 777)
- ✅ Supports both positional and flag-based arguments

**Usage:**
```bash
# Positional syntax
./launch_ape.sh fast                              # All clients
./launch_ape.sh fast merck_test blue_yonder_test  # Specific clients
./launch_ape.sh deep                              # Deep mode, all clients

# Flag syntax (also works)
./launch_ape.sh --mode fast
./launch_ape.sh --mode fast --clients merck_test
```

### setup-credentials.sh

**New features:**
- ✅ Auto-detects architecture
- ✅ Uses versioned, architecture-specific images
- ✅ Adds SELinux labels for credential copying

**Usage:**
```bash
# First-time setup
./setup-credentials.sh

# This creates a persistent volume with your NotebookLM credentials
```

---

## First-Time Setup on RHEL9/Linux

### 1. Install Prerequisites

```bash
# RHEL9/Fedora
sudo dnf install -y podman git

# Verify
podman --version
```

### 2. Clone Repository

```bash
cd ~
git clone <repository-url>
cd Project-APE
```

### 3. Configure Environment

```bash
# Copy templates
cp .env.template .env
cp example-vars.py vars.py

# Edit with your values
nano .env
nano vars.py

# Place service account file
cp ~/Downloads/service-account.json ./jasoande-3aec1043e544.json
```

### 4. Fix Permissions (Important!)

```bash
# Run the fix script
./fix-permissions.sh

# Or manually
chmod 777 logs .multi_process_status
```

### 5. Run Pipeline

```bash
# First run
./launch_ape.sh fast merck_test

# Dashboard will be at:
# http://localhost:8765
```

---

## Understanding Container User Mapping

### The Problem

- **Container user:** `apeuser` (UID 1000, GID 1000)
- **Host user:** `ec2-user` (UID varies, typically 1000)
- **Mounted directories:** Owned by host user

When container user tries to write to mounted directories owned by a different UID, permission is denied.

### The Solution

**Option 1: World-writable directories (Simple)**
```bash
chmod 777 logs .multi_process_status
```
- ✅ Simple, works immediately
- ⚠️ Less secure (any user can write)

**Option 2: User namespace mapping (Advanced)**
```bash
podman run --userns=keep-id ...
```
- ✅ More secure
- ⚠️ Requires container rebuild with matching UIDs

**We use Option 1** because it's simple and these directories only contain logs/status files (no sensitive data).

---

## SELinux Volume Mount Flags

### The `:z` Flag

When mounting volumes on SELinux systems, you need the `:z` or `:Z` flag:

```bash
-v $(pwd)/vars.py:/app/vars.py:ro,z
```

**What it does:**
- Relabels the file with a **private unshared** label
- Allows the container to read/write based on `ro`/`rw` flag
- Automatically handles SELinux context switching

**Flags explained:**
- `:z` - Private label (use for files/dirs used by one container)
- `:Z` - Shared label (use for files/dirs shared by multiple containers)
- `ro` - Read-only mount
- `rw` - Read-write mount (default)

**Example:**
```bash
-v $(pwd)/.env:/app/.env:ro,z              # Read-only, private
-v $(pwd)/logs:/app/logs:z                 # Read-write, private
```

---

## Troubleshooting Commands

### Check SELinux status
```bash
getenforce                    # Should show: Enforcing
sestatus                      # Detailed status
```

### Check file/directory permissions
```bash
ls -la vars.py               # Unix permissions
ls -lZ vars.py               # SELinux labels
```

### Check container logs
```bash
podman logs project-ape
```

### Check for permission denials
```bash
# Check SELinux audit log
sudo ausearch -m AVC -ts recent

# Or check system log
sudo journalctl -xe | grep -i denied
```

### Verify container is running
```bash
podman ps                    # List running containers
podman ps -a                 # List all containers
```

### Enter running container
```bash
podman exec -it project-ape bash
```

### Check mounted volumes inside container
```bash
podman exec project-ape ls -la /app
podman exec project-ape cat /app/vars.py
```

---

## Architecture-Specific Images

### Image Naming Convention

```
quay.io/jasoande/project_ape/project-ape:3.0.5-amd64
quay.io/jasoande/project_ape/project-ape:3.0.5-arm64
```

### Pull Specific Architecture

```bash
# For x86_64/AMD64 servers (EC2, most cloud VMs)
podman pull quay.io/jasoande/project_ape/project-ape:3.0.5-amd64

# For ARM64 servers (Graviton, M1/M2/M3 Macs)
podman pull quay.io/jasoande/project_ape/project-ape:3.0.5-arm64
```

### List Local Images

```bash
podman images | grep project-ape
```

---

## Quick Reference

### Essential Commands

```bash
# Fix permissions
./fix-permissions.sh

# Run pipeline
./launch_ape.sh fast

# Check logs
tail -f logs/merck_test.log

# Stop container
podman stop project-ape

# Remove container
podman rm project-ape

# Remove image
podman rmi quay.io/jasoande/project_ape/project-ape:3.0.5-amd64
```

### Essential Files

```
Project-APE/
├── .env                          # API keys (required)
├── vars.py                       # Client config (required)
├── jasoande-*.json              # Service account (required)
├── logs/                        # Output logs (auto-created)
├── .multi_process_status/       # Status files (auto-created)
├── launch_ape.sh               # Main launcher
├── setup-credentials.sh        # NotebookLM auth setup
└── fix-permissions.sh          # Permission fixer
```

---

## Summary

**Key fixes for Linux deployment:**
1. ✅ SELinux labels (`:z` flags) - **handled by launch script**
2. ✅ Directory permissions (chmod 777) - **run fix-permissions.sh**
3. ✅ Architecture detection - **automatic**
4. ✅ Proper image tagging - **automatic**

**After applying these fixes, Project APE works identically on:**
- ✅ macOS (M1/M2/M3)
- ✅ Linux x86_64 (RHEL9, Fedora, Ubuntu, Debian)
- ✅ Linux ARM64 (Graviton, other ARM servers)

---

**Questions?** Contact Jason Anderson
