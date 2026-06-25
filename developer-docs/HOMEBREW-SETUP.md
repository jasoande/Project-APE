# Project APE - Homebrew Setup Documentation

**Date:** 2026-06-22  
**Author:** Principal Software Engineer Analysis  
**Focus:** macOS Installation - Homebrew Integration

---

## Executive Summary

The `setup-environment.sh` script now includes **comprehensive Homebrew installation and validation** as STEP 0 (before any package installations). This ensures all macOS users have the required package manager before attempting to install Podman, Python, or other dependencies.

---

## Why Homebrew Is Critical for Project APE on macOS

### What is Homebrew?

Homebrew is the de facto standard package manager for macOS, similar to `apt` on Ubuntu or `dnf` on RHEL/Fedora.

**Official Site:** https://brew.sh

### Project APE Dependencies Requiring Homebrew

| Package | Purpose | Alternative? |
|---------|---------|--------------|
| **Podman** | Container runtime for running Project APE | ❌ No easy alternative on macOS |
| **Python 3** | Runtime for NotebookLM CLI | ⚠️ System Python often outdated |
| **Build Tools** | Xcode Command Line Tools (installed with Homebrew) | ⚠️ Can install separately |

**Bottom Line:** Without Homebrew, Project APE cannot be easily installed on macOS.

---

## What Changed in setup-environment.sh

### NEW: STEP 0 - Homebrew Verification and Installation

Located immediately after OS detection, before any package installations.

#### Features

1. **Detection** - Checks if `brew` command exists
2. **Validation** - Verifies Homebrew is properly configured
3. **Update** - Updates Homebrew to latest version if already installed
4. **Interactive Installation** - Prompts user to install if missing
5. **Architecture Detection** - Handles Apple Silicon (ARM64) vs Intel (x86_64) paths
6. **PATH Configuration** - Adds Homebrew to shell profile automatically
7. **Health Check** - Runs `brew doctor` diagnostics
8. **Error Handling** - Gracefully handles installation failures

---

## Installation Flow

### Scenario 1: Homebrew Already Installed

```bash
./setup-environment.sh
```

**Output:**
```
======================================================================
PROJECT APE - ENVIRONMENT SETUP
======================================================================

Detected OS: macOS

======================================================================
STEP 0: HOMEBREW VERIFICATION (macOS)
======================================================================

Homebrew is the package manager for macOS and is required for:
  - Podman (container runtime)
  - Python 3 (if not already installed)

✅ Homebrew is already installed
   Homebrew 4.3.5
   Location: /opt/homebrew/bin/brew
✅ Homebrew is properly configured in PATH

Updating Homebrew to latest version...
Already up-to-date.

Verifying Homebrew installation...
✅ Homebrew is working correctly

Running Homebrew diagnostics...
✅ Homebrew health check passed
```

**Then continues to STEP 1 (Podman installation)...**

---

### Scenario 2: Homebrew Not Installed (Interactive)

```bash
./setup-environment.sh
```

**Output:**
```
======================================================================
STEP 0: HOMEBREW VERIFICATION (macOS)
======================================================================

⚠️  Homebrew is not installed

Homebrew must be installed before continuing.

Would you like to install Homebrew now? (Recommended)

Install Homebrew? (y/n) y

======================================================================
INSTALLING HOMEBREW
======================================================================

The Homebrew installation script will:
  1. Download and install Homebrew
  2. Install Command Line Tools for Xcode (if needed)
  3. Configure your shell environment

This may take 5-10 minutes and will require your password.

Continue with Homebrew installation? (y/n) y

Installing Homebrew...

==> Checking for `sudo` access (which may request your password)...
Password: ********

[Homebrew installation output...]

✅ Homebrew installed successfully

Configuring Homebrew in current session...
✅ Homebrew is now available in PATH
   Location: /opt/homebrew/bin/brew

Configuring shell profile for future sessions...
Adding Homebrew to /Users/username/.zprofile...
✅ Homebrew added to /Users/username/.zprofile

NOTE: For Homebrew to work in new terminal sessions, either:
  1. Close and reopen your terminal, OR
  2. Run: source /Users/username/.zprofile

Verifying Homebrew installation...
✅ Homebrew is working correctly

Running Homebrew diagnostics...
✅ Homebrew health check passed
```

**Then continues to STEP 1 (Podman installation)...**

---

### Scenario 3: User Declines Homebrew Installation

```bash
./setup-environment.sh
```

**Output:**
```
======================================================================
STEP 0: HOMEBREW VERIFICATION (macOS)
======================================================================

⚠️  Homebrew is not installed

Would you like to install Homebrew now? (Recommended)

Install Homebrew? (y/n) n

ERROR: Homebrew is required for Project APE on macOS

To install Homebrew manually later:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Then run this setup script again.

[Script exits]
```

---

## Technical Details

### Architecture Detection

The script automatically detects Mac architecture and uses the correct Homebrew paths:

#### Apple Silicon (M1/M2/M3/M4)

```bash
Architecture: arm64
Homebrew Prefix: /opt/homebrew
Brew Binary: /opt/homebrew/bin/brew
```

#### Intel Mac

```bash
Architecture: x86_64
Homebrew Prefix: /usr/local
Brew Binary: /usr/local/bin/brew
```

### Shell Profile Configuration

The script intelligently selects the appropriate shell profile:

| Shell | Profile File | Priority |
|-------|-------------|----------|
| zsh (default on macOS 10.15+) | `~/.zprofile` | 1st choice |
| bash | `~/.bash_profile` | 2nd choice |
| sh | `~/.profile` | Fallback |

**What gets added:**
```bash
# Homebrew
eval "$(/opt/homebrew/bin/brew shellenv)"
```

This ensures `brew` is available in all future terminal sessions.

---

## Homebrew Installation Process

### What Happens When Installing Homebrew

1. **Downloads** - Fetches official Homebrew installer from GitHub
2. **Xcode Command Line Tools** - Installs if not already present
3. **Creates Directories** - Sets up `/opt/homebrew` (ARM64) or `/usr/local` (Intel)
4. **Configures Permissions** - Sets up correct ownership and permissions
5. **Initializes Git** - Homebrew uses Git for package management
6. **Updates PATH** - Adds Homebrew binaries to shell environment

### Time Requirements

| Step | Duration | Notes |
|------|----------|-------|
| Initial download | 10-30 sec | Depends on internet speed |
| Xcode CLT install | 5-10 min | Only if not already installed |
| Homebrew setup | 1-2 min | Installing Homebrew itself |
| **Total** | **5-15 min** | First-time installation |

### Disk Space Requirements

- **Homebrew Core:** ~400 MB
- **Xcode Command Line Tools:** ~1.5 GB
- **Total:** ~2 GB for first installation

---

## Verification and Health Checks

### Checks Performed by STEP 0

#### 1. Command Availability
```bash
if command -v brew &> /dev/null; then
    # Homebrew is installed
fi
```

#### 2. Version Check
```bash
brew --version
# Output: Homebrew 4.3.5
```

#### 3. Location Validation
```bash
which brew
# Expected (ARM64): /opt/homebrew/bin/brew
# Expected (Intel): /usr/local/bin/brew
```

#### 4. PATH Configuration
```bash
# Verifies brew is accessible via $PATH
# Checks shell profile has shellenv configured
```

#### 5. Health Diagnostics
```bash
brew doctor
# Checks for common issues:
# - Outdated Xcode CLT
# - Permission problems
# - PATH conflicts
# - Broken symlinks
```

---

## Troubleshooting

### Issue: Homebrew Installation Fails

**Error Message:**
```
ERROR: Homebrew installation failed

Please install Homebrew manually:
  1. Visit: https://brew.sh
  2. Follow the installation instructions
  3. Run this setup script again
```

**Common Causes:**
1. **No internet connection** - Homebrew downloads from GitHub
2. **Insufficient disk space** - Need ~2 GB free
3. **Xcode license not accepted** - Run `sudo xcodebuild -license accept`
4. **Partial previous installation** - Remove `/opt/homebrew` and retry

**Manual Fix:**
```bash
# Clean up partial installation (if needed)
sudo rm -rf /opt/homebrew

# Install Homebrew manually
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation
brew --version

# Re-run Project APE setup
./setup-environment.sh
```

---

### Issue: Homebrew Not in PATH After Installation

**Error Message:**
```
ERROR: Homebrew installed but not in PATH
```

**Cause:** Shell profile not properly configured

**Fix:**
```bash
# For Apple Silicon Mac (ARM64)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Intel Mac (x86_64)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# Verify
which brew
# Should show: /opt/homebrew/bin/brew (ARM64) or /usr/local/bin/brew (Intel)

# Re-run setup
./setup-environment.sh
```

---

### Issue: Homebrew Doctor Warnings

**Message:**
```
⚠️  Homebrew has some warnings (non-critical)
   See /tmp/brew-doctor.log for details
```

**This is NOT a blocking error.** The setup continues successfully.

**To review warnings:**
```bash
brew doctor
```

**Common warnings (usually safe to ignore):**
- "You have unlinked kegs in your Cellar" - Old package versions
- "You have broken symlinks" - Leftover from removed packages
- "Your Xcode is outdated" - Only matters for development
- "config scripts exist outside PATH" - Usually harmless

**When to act on warnings:**
- If `brew install` commands fail later
- If Podman installation fails
- If Python installation fails

**Fix common issues:**
```bash
# Clean up Homebrew
brew cleanup

# Fix permissions
sudo chown -R $(whoami) /opt/homebrew/*

# Update Homebrew
brew update
brew upgrade
```

---

### Issue: Multiple Homebrew Installations

**Symptom:** `which brew` shows unexpected location like `/usr/bin/brew`

**Cause:** System has both old (Intel) and new (ARM64) Homebrew installed

**Check for multiple installations:**
```bash
# Check all brew locations
which -a brew

# Expected output (ARM64 Mac):
/opt/homebrew/bin/brew

# Problematic output:
/opt/homebrew/bin/brew
/usr/local/bin/brew
```

**Fix - Use ARM64 Homebrew (recommended):**
```bash
# Remove old Homebrew from PATH in shell profile
nano ~/.zprofile

# Ensure ONLY this line exists:
eval "$(/opt/homebrew/bin/brew shellenv)"

# Remove any lines referencing /usr/local/bin/brew

# Reload shell
source ~/.zprofile

# Verify correct brew
which brew
# Should show: /opt/homebrew/bin/brew
```

---

### Issue: Permission Denied Errors

**Error:**
```
Error: Permission denied @ apply2files
```

**Cause:** Homebrew directories owned by wrong user (often after `sudo brew install`)

**Fix:**
```bash
# Fix ownership of Homebrew directories
sudo chown -R $(whoami):admin /opt/homebrew/*

# Never use sudo with brew
# ❌ WRONG: sudo brew install podman
# ✅ RIGHT: brew install podman
```

---

## Best Practices

### 1. Never Use `sudo` with Homebrew

```bash
# ❌ WRONG - Breaks permissions
sudo brew install podman

# ✅ RIGHT - Homebrew manages permissions
brew install podman
```

**Why?** Using `sudo` makes Homebrew files owned by `root`, causing permission errors later.

---

### 2. Keep Homebrew Updated

```bash
# Update Homebrew itself
brew update

# Upgrade installed packages
brew upgrade

# Check for issues
brew doctor

# Clean up old versions
brew cleanup
```

**Recommendation:** Update monthly or before installing new packages.

---

### 3. Use Homebrew for All macOS Package Management

```bash
# ✅ GOOD - Use Homebrew
brew install python3
brew install podman
brew install node

# ❌ AVOID - Manual downloads/installers
# - Harder to update
# - May conflict with Homebrew versions
# - No dependency management
```

---

### 4. Understand Homebrew Directories

| Directory | Purpose | Example |
|-----------|---------|---------|
| `/opt/homebrew/bin` | Executable binaries | `brew`, `python3`, `podman` |
| `/opt/homebrew/Cellar` | Installed packages | Package versions |
| `/opt/homebrew/opt` | Symlinks to current versions | `python@3.14` |
| `/opt/homebrew/etc` | Configuration files | Service configs |
| `/opt/homebrew/var` | Variable data | Logs, caches |

---

## Integration with Project APE Workflow

### Full Installation Sequence with Homebrew

```bash
# STEP 0: Homebrew (automatic in setup-environment.sh)
# - Checks if installed
# - Installs if missing
# - Updates if present
# - Verifies health

# STEP 1: Podman (via Homebrew)
brew install podman
podman machine init
podman machine start

# STEP 2: Python 3 (via Homebrew if needed)
brew install python3

# STEP 3: Virtual Environment
python3 -m venv ~/.project-ape-venv

# STEP 4: NotebookLM CLI (in venv)
source ~/.project-ape-venv/bin/activate
pip install notebooklm-py[browser]

# STEP 5: Authenticate
notebooklm login

# STEP 6: Setup credentials
./setup-credentials.sh

# STEP 7: Run pipeline
./launch_ape.sh fast
```

All of this is automated by `./setup-environment.sh` - the user just needs to respond to prompts.

---

## Advanced: Homebrew Architecture

### Package Resolution on ARM64 Macs

Apple Silicon Macs can run both ARM64 and x86_64 (Intel) binaries via Rosetta 2.

**Homebrew Architecture Strategy:**
```bash
# Check architecture
uname -m
# Output: arm64 (Apple Silicon) or x86_64 (Intel)

# Homebrew installs native packages by default
arch
# Output: arm64

# ARM64 Homebrew location
/opt/homebrew/

# Intel Homebrew location (if installed)
/usr/local/
```

**Project APE uses native ARM64 wherever possible:**
- Homebrew: ARM64
- Python: ARM64
- Podman: ARM64
- Container image: `quay.io/jasoande/project_ape/project-ape:latest` (ARM64)

---

## Security Considerations

### Homebrew Installation Script

The official installer is downloaded via HTTPS from GitHub:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Security Features:**
- ✅ HTTPS (encrypted download)
- ✅ Official GitHub repository
- ✅ Open source (auditable)
- ✅ No `sudo` required for normal use
- ✅ User-owned directories (not system-wide)

### Verification

**Manually verify installer before running:**
```bash
# Download installer to review
curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh > /tmp/brew-install.sh

# Review contents
less /tmp/brew-install.sh

# Run if satisfied
bash /tmp/brew-install.sh
```

---

## Performance Considerations

### Homebrew Download Cache

Homebrew caches downloaded packages to speed up reinstallation:

```bash
# Cache location
~/Library/Caches/Homebrew/

# View cache size
du -sh ~/Library/Caches/Homebrew/

# Clear cache to free space
brew cleanup -s

# Clear all downloads
rm -rf ~/Library/Caches/Homebrew/downloads
```

### Package Installation Speed

| Package | Download Size | Install Time | Notes |
|---------|---------------|--------------|-------|
| Podman | ~50 MB | 1-2 min | Includes QEMU dependencies |
| Python 3.14 | ~30 MB | 1-2 min | Includes standard library |
| Build tools | ~1.5 GB | 5-10 min | Xcode Command Line Tools |

---

## Comparison: Manual vs Automated Homebrew Setup

### Before (Manual User Setup)

```bash
# User must:
1. Visit brew.sh in browser
2. Copy installation command
3. Paste into terminal
4. Wait for installation
5. Configure shell profile manually
6. Restart terminal
7. Verify installation
8. Then run Project APE setup
```

**Issues:**
- ❌ Easy to skip or forget
- ❌ No validation
- ❌ Errors not caught early
- ❌ User needs to understand Homebrew

---

### After (Automated in setup-environment.sh)

```bash
# User just runs:
./setup-environment.sh

# Script handles:
1. ✅ Detects if Homebrew is missing
2. ✅ Offers to install automatically
3. ✅ Runs installation with error handling
4. ✅ Configures shell profile
5. ✅ Verifies installation
6. ✅ Runs health checks
7. ✅ Continues to package installation
```

**Benefits:**
- ✅ One-command setup
- ✅ Automatic validation
- ✅ Early error detection
- ✅ User-friendly prompts
- ✅ No Homebrew knowledge required

---

## Summary

The enhanced `setup-environment.sh` script now includes:

✅ **Automatic Homebrew Detection** - Checks if installed before any package operations  
✅ **Interactive Installation** - Offers to install Homebrew if missing  
✅ **Architecture Awareness** - Handles Apple Silicon and Intel Macs correctly  
✅ **PATH Configuration** - Automatically adds Homebrew to shell profile  
✅ **Health Validation** - Runs diagnostics to catch issues early  
✅ **Graceful Error Handling** - Clear messages guide users through problems  
✅ **Zero User Expertise Required** - Works for users who've never heard of Homebrew  

### Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ Homebrew + Project APE - Quick Reference (macOS)         │
├──────────────────────────────────────────────────────────┤
│ AUTOMATIC SETUP (Recommended):                           │
│   ./setup-environment.sh                                 │
│   - Installs Homebrew if missing                         │
│   - Installs all dependencies                            │
│   - Configures virtual environment                       │
│                                                          │
│ MANUAL HOMEBREW CHECK:                                   │
│   brew --version                                         │
│   which brew                                             │
│   brew doctor                                            │
│                                                          │
│ MANUAL HOMEBREW INSTALL:                                 │
│   /bin/bash -c "$(curl -fsSL https://...)"              │
│   See: https://brew.sh                                   │
│                                                          │
│ TROUBLESHOOTING:                                         │
│   brew doctor        # Diagnose issues                   │
│   brew cleanup       # Fix common problems               │
│   brew update        # Update Homebrew                   │
│   brew upgrade       # Upgrade packages                  │
└──────────────────────────────────────────────────────────┘
```

---

**For questions or issues, refer to:**
- This document - Homebrew setup details
- SETUP-IMPROVEMENTS.md - Virtual environment changes
- README.md - Complete Project APE guide
- https://brew.sh - Official Homebrew documentation
