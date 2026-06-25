# Project APE - Setup Environment Improvements

**Date:** 2026-06-22  
**Author:** Principal Software Engineer Analysis  
**Focus:** Mac Installation Only

---

## Executive Summary

The `setup-environment.sh` script has been comprehensively enhanced with two major improvements:

1. **Homebrew Installation & Validation** - Automatic package manager setup (macOS)
2. **Python Virtual Environments** - Isolated dependency management

These changes follow industry best practices and ensure reliable, conflict-free installations.

### Key Changes

1. **STEP 0: Homebrew Verification** (NEW) - Checks for and installs Homebrew if needed
2. **Virtual Environment Creation** - Isolated Python environment at `~/.project-ape-venv`
3. **Proper Dependency Isolation** - NotebookLM CLI and dependencies contained
4. **Version Control** - Ensures Python 3.10+ before creating venv
5. **Activation Helper** - Simple script for future sessions
6. **Updated Workflow** - Clear instructions for venv usage

### Related Documentation

- **HOMEBREW-SETUP.md** - Comprehensive Homebrew integration details
- This document - Virtual environment and workflow changes
- README.md - Complete user guide

---

## Why Virtual Environments?

### Problems with Global Installation (Previous Approach)

```bash
# OLD METHOD - NOT RECOMMENDED
python3 -m pip install --user notebooklm-py[browser]
```

**Issues:**
- ❌ Pollutes user's global Python environment
- ❌ Can conflict with other projects using different versions
- ❌ Hard to track what Project APE installed vs. other tools
- ❌ Difficult to cleanly uninstall
- ❌ Breaks when switching Python versions

### Benefits of Virtual Environment (New Approach)

```bash
# NEW METHOD - RECOMMENDED
python3 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate
pip install notebooklm-py[browser]
```

**Benefits:**
- ✅ Complete isolation from system Python
- ✅ Clean dependency management
- ✅ Easy to recreate or remove entirely
- ✅ Standard Python best practice
- ✅ Won't interfere with other projects
- ✅ Survives Python version updates

---

## Technical Architecture

### Project APE Dual Python Strategy

Project APE uses Python in **two distinct contexts**:

#### 1. Host Machine (Mac) - NotebookLM CLI Only
```
Purpose: Authenticate with Google NotebookLM
Location: ~/.project-ape-venv/
Python Version: 3.10+ (uses your system Python 3)
Dependencies: notebooklm-py[browser], playwright
Usage: One-time authentication, credential management
```

#### 2. Container (Podman) - Full Application
```
Purpose: Run the entire Project APE pipeline
Location: Inside container (quay.io/jasoande/project_ape/project-ape:latest)
Python Version: 3.13 (fixed in container)
Dependencies: All application deps (Flask, PyPDF, Google APIs, etc.)
Usage: Execute the actual account planning pipeline
```

### Why This Separation?

**NotebookLM Authentication Flow:**
1. Host machine runs `notebooklm login` (opens browser)
2. User authenticates via Google OAuth
3. Credentials saved to `~/.notebooklm/` on host
4. Credentials copied to Podman volume via `setup-credentials.sh`
5. Container uses credentials from volume (no browser needed)

**Key Insight:** The container can't open a browser for OAuth, so authentication must happen on the host first.

---

## Updated Setup Workflow

### Previous Workflow (Global Install)
```bash
# OLD - Multiple issues
./setup-environment.sh      # Installs globally
notebooklm login            # Works, but uses global install
./setup-credentials.sh      # Copy credentials
./launch_ape.sh fast        # Run pipeline
```

### New Workflow (Homebrew + Virtual Environment)
```bash
# STEP 1: Setup (one-time)
./setup-environment.sh
# STEP 0: Homebrew (macOS only)
#   - Checks if Homebrew installed
#   - Installs if missing (with user consent)
#   - Updates if present
#   - Verifies health
# STEP 1: Podman
#   - Installs via Homebrew (macOS)
# STEP 2: Python 3.10+
#   - Verifies or installs via Homebrew
# STEP 3: Virtual Environment
#   - Creates ~/.project-ape-venv/
# STEP 4: NotebookLM CLI
#   - Installs in venv (isolated)
# STEP 5: Activation Helper
#   - Creates activate-ape-env.sh script

# STEP 2: Activate environment (each session)
source ./activate-ape-env.sh
# - Activates ~/.project-ape-venv/
# - Adds notebooklm command to PATH
# - Shows confirmation with versions

# STEP 3: Authenticate (one-time)
notebooklm login
# - Opens browser for Google OAuth
# - Saves credentials to ~/.notebooklm/

# STEP 4: Setup container credentials (one-time)
./setup-credentials.sh
# - Copies ~/.notebooklm/ to Podman volume
# - Container will use these credentials

# STEP 5: Run pipeline (anytime)
./launch_ape.sh fast
# - No venv needed (runs in container)
# - Container has its own Python environment

# STEP 6: Deactivate when done (optional)
deactivate
# - Returns to system Python
# - Clean terminal state
```

---

## Files Modified

### 1. `setup-environment.sh`

**Changes:**
- Renamed STEP 3 to create virtual environment before installing anything
- Added STEP 4 for NotebookLM CLI installation (inside venv)
- Added STEP 5 to create `activate-ape-env.sh` helper script
- Updated final output to emphasize venv usage
- Removed direct pip install to `~/.local/bin`

**Key Sections:**
```bash
# Create venv at ~/.project-ape-venv
python3 -m venv "$VENV_DIR"

# Activate for this session
source "$VENV_DIR/bin/activate"

# Install inside venv (not globally)
pip install notebooklm-py[browser]

# Create helper for future sessions
cat > activate-ape-env.sh << 'EOF'
source ~/.project-ape-venv/bin/activate
EOF
```

### 2. `setup-credentials.sh`

**Changes:**
- Added virtual environment path detection
- Enhanced error messages to guide users through venv activation
- Updated instructions to use `source ./activate-ape-env.sh`

**Key Logic:**
```bash
# Check venv exists before looking for credentials
if [ ! -d "${VENV_DIR}" ]; then
    echo "Run setup-environment.sh first"
    exit 1
fi

# Guide user if credentials missing
if [ ! -d "${HOST_CREDS}" ]; then
    echo "Step 1: source ./activate-ape-env.sh"
    echo "Step 2: notebooklm login"
    exit 1
fi
```

### 3. `activate-ape-env.sh` (NEW)

**Purpose:** Convenience script for activating the virtual environment

**Usage:**
```bash
source ./activate-ape-env.sh
```

**Features:**
- Checks if venv exists
- Activates `~/.project-ape-venv`
- Shows Python and NotebookLM versions
- Provides deactivation instructions

**Contents:**
```bash
#!/bin/bash
VENV_DIR="$HOME/.project-ape-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found"
    echo "Run ./setup-environment.sh first"
    return 1
fi

source "$VENV_DIR/bin/activate"

echo "✅ Project APE virtual environment activated"
echo "   Python: $(python3 --version)"
echo "   NotebookLM CLI: $(notebooklm --version)"
echo ""
echo "To deactivate, run: deactivate"
```

---

## Testing the Changes

### Test 1: Fresh Installation
```bash
# Start with no venv
rm -rf ~/.project-ape-venv

# Run setup
./setup-environment.sh

# Verify venv created
ls -la ~/.project-ape-venv/bin/python3  # Should exist

# Verify helper created
ls -la activate-ape-env.sh  # Should exist

# Activate
source ./activate-ape-env.sh

# Verify notebooklm available
which notebooklm  # Should show ~/.project-ape-venv/bin/notebooklm

# Test version
notebooklm --version  # Should show NotebookLM CLI 0.7.x
```

### Test 2: Virtual Environment Isolation
```bash
# Activate venv
source ./activate-ape-env.sh

# Check Python location
which python3  # Should be ~/.project-ape-venv/bin/python3

# List installed packages
pip list  # Should show ONLY Project APE dependencies

# Deactivate
deactivate

# Check system Python
which python3  # Should be system Python (/opt/homebrew/bin/python3)

# Verify notebooklm not in PATH when deactivated
which notebooklm  # Should fail (command not found)
```

### Test 3: Credential Setup
```bash
# Activate venv
source ./activate-ape-env.sh

# Authenticate
notebooklm login  # Opens browser, authenticate

# Verify credentials exist
ls -la ~/.notebooklm/profiles/default/storage_state.json

# Setup container credentials
./setup-credentials.sh  # Should succeed

# Verify volume created
podman volume ls | grep project-ape-credentials
```

### Test 4: Full Pipeline
```bash
# Configure client
cp example-vars.py vars.py
nano vars.py  # Add real client data

# Run pipeline (no venv needed for this step)
./launch_ape.sh fast

# Container should start successfully
# Dashboard should open at http://localhost:8765
```

---

## Troubleshooting

### Issue: "notebooklm: command not found"

**Cause:** Virtual environment not activated

**Solution:**
```bash
source ./activate-ape-env.sh
```

**Verification:**
```bash
echo $VIRTUAL_ENV
# Should show: /Users/[username]/.project-ape-venv
```

---

### Issue: "Virtual environment not found"

**Cause:** `setup-environment.sh` didn't complete successfully

**Solution:**
```bash
# Check if venv exists
ls -la ~/.project-ape-venv/

# If not, re-run setup
./setup-environment.sh

# If it fails, check Python version
python3 --version  # Must be 3.10 or higher

# Check venv module availability
python3 -m venv --help
```

---

### Issue: Python version too old in venv

**Cause:** System Python was upgraded after venv creation

**Solution:**
```bash
# Remove old venv
rm -rf ~/.project-ape-venv

# Re-create with new Python version
./setup-environment.sh

# Verify new version
source ./activate-ape-env.sh
python3 --version
```

---

### Issue: "Permission denied" when installing packages

**Cause:** Trying to install system-wide or venv permissions wrong

**Solution:**
```bash
# Always activate venv first
source ./activate-ape-env.sh

# Then install (no sudo needed)
pip install some-package

# If venv permissions broken, recreate it
rm -rf ~/.project-ape-venv
./setup-environment.sh
```

---

## Migration Guide

### For Existing Installations

If you previously installed Project APE with the old global method:

```bash
# STEP 1: Uninstall global packages (optional but recommended)
pip3 uninstall -y notebooklm-py playwright

# STEP 2: Remove old global binaries
rm -f ~/.local/bin/notebooklm
rm -f ~/.local/bin/playwright

# STEP 3: Backup credentials (if already authenticated)
# NotebookLM credentials are in ~/.notebooklm/ - leave these alone

# STEP 4: Run new setup script
./setup-environment.sh
# This creates venv and installs everything cleanly

# STEP 5: No need to re-authenticate if ~/.notebooklm/ exists
# Just run setup-credentials.sh to copy to container

# STEP 6: Test
source ./activate-ape-env.sh
notebooklm --version
```

### Credentials Are Preserved

**Important:** The `~/.notebooklm/` directory is separate from the Python environment. Your existing Google authentication credentials will work with the new venv installation.

```bash
# Credentials location (unchanged)
~/.notebooklm/profiles/default/storage_state.json

# Python environment (new)
~/.project-ape-venv/
```

---

## Advanced Usage

### Updating NotebookLM CLI

```bash
# Activate venv
source ./activate-ape-env.sh

# Update to latest version
pip install --upgrade notebooklm-py[browser]

# Verify new version
notebooklm --version
```

### Installing Additional Tools in Venv

```bash
# Activate venv
source ./activate-ape-env.sh

# Install additional package
pip install some-other-package

# List all installed packages
pip list

# Freeze for documentation
pip freeze > venv-requirements.txt
```

### Completely Removing Project APE Environment

```bash
# Remove virtual environment
rm -rf ~/.project-ape-venv

# Remove credentials (if desired)
rm -rf ~/.notebooklm

# Remove Podman volumes
podman volume rm project-ape-credentials
podman volume rm project-ape-cache

# Remove container images
podman rmi quay.io/jasoande/project_ape/project-ape:latest

# Remove activation helper
rm -f activate-ape-env.sh
```

---

## Best Practices

### 1. Always Activate Before Using NotebookLM CLI

```bash
# WRONG - won't work
notebooklm login

# RIGHT - activate first
source ./activate-ape-env.sh
notebooklm login
```

### 2. Deactivate When Done

```bash
# After using NotebookLM
deactivate

# Returns to clean system state
# Prevents confusion in other projects
```

### 3. Document Your Workflow

```bash
# Add to your notes or scripts
# Project APE Workflow:
# 1. source ./activate-ape-env.sh
# 2. notebooklm login (if needed)
# 3. ./launch_ape.sh fast
# 4. deactivate (when done)
```

### 4. Shell Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Project APE shortcuts
alias ape-activate='cd /path/to/Project-APE && source ./activate-ape-env.sh'
alias ape-fast='cd /path/to/Project-APE && ./launch_ape.sh fast'
alias ape-deep='cd /path/to/Project-APE && ./launch_ape.sh deep'
```

---

## Python Version Compatibility

### Required Versions

| Component | Minimum | Recommended | Container |
|-----------|---------|-------------|-----------|
| System Python 3 | 3.10 | 3.14 | N/A |
| Venv Python | 3.10 | 3.14 | N/A |
| Container Python | N/A | N/A | 3.13 (fixed) |
| NotebookLM CLI | 3.10+ | 3.14+ | N/A |

### Checking Versions

```bash
# System Python
python3 --version

# Venv Python (after activation)
source ./activate-ape-env.sh
python3 --version
which python3

# Container Python
podman run --rm quay.io/jasoande/project_ape/project-ape:latest python3 --version
```

---

## Security Considerations

### Virtual Environment Isolation

✅ **Benefits:**
- Limits blast radius of compromised packages
- Can't affect system Python or other projects
- Easy to audit with `pip list`
- Can be deleted entirely without affecting system

### Credential Storage

🔒 **Security:**
- `~/.notebooklm/` permissions: 700 (user-only access)
- `storage_state.json` contains OAuth tokens
- Volume-mounted read-only to container where possible
- Never committed to git (in `.gitignore`)

### Recommendations

```bash
# Verify credential permissions
ls -la ~/.notebooklm
# Should show: drwx------

# Check venv is user-owned
ls -la ~/.project-ape-venv
# Should show your user, not root

# Review installed packages
source ./activate-ape-env.sh
pip list
# Should only show Project APE dependencies
```

---

## Summary

The updated `setup-environment.sh` script provides:

✅ **Proper Isolation** - Virtual environment at `~/.project-ape-venv`  
✅ **Best Practices** - Follows Python packaging standards  
✅ **Easy Management** - Simple activation/deactivation workflow  
✅ **Clear Instructions** - User-friendly output with next steps  
✅ **Backward Compatible** - Existing credentials still work  
✅ **Mac-Optimized** - Tested on macOS with Homebrew Python  

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ Project APE - Quick Reference (Mac)                     │
├─────────────────────────────────────────────────────────┤
│ Setup (one-time):                                       │
│   ./setup-environment.sh                                │
│                                                         │
│ Activate venv (each session):                          │
│   source ./activate-ape-env.sh                          │
│                                                         │
│ Authenticate (one-time):                               │
│   notebooklm login                                      │
│                                                         │
│ Setup credentials (one-time):                          │
│   ./setup-credentials.sh                                │
│                                                         │
│ Run pipeline (anytime):                                │
│   ./launch_ape.sh fast                                  │
│                                                         │
│ Deactivate venv:                                       │
│   deactivate                                            │
└─────────────────────────────────────────────────────────┘
```

---

**For questions or issues, refer to:**
- README.md - Complete user guide
- QUICKSTART.md - 5-minute quick start
- This document - Setup improvements and venv usage
