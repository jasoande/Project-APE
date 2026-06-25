# Python 3.14 and NotebookLM Installation Fix

## Problem

On Linux (RHEL/Amazon Linux), users encountered two issues when trying to set up NotebookLM:

1. **Playwright not installed error** - Despite setup-environment.sh installing notebooklm-py[browser], the playwright command wasn't found
2. **Python version mismatch** - After upgrading to Python 3.14, notebooklm-py was still installed under Python 3.9, causing type hint errors:
   ```
   TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
   ```

## Root Causes

1. **Playwright path issue**: The setup script called `playwright` without the full path, but it's installed to `~/.local/bin/playwright` which may not be in PATH yet during script execution

2. **pip module missing**: Python 3.14 was installed without the pip module (`python3.14-pip` package not installed)

3. **Wrong pip used**: Using `pip3` instead of `python3 -m pip` meant the package was installed for the system Python (3.9) instead of the upgraded Python (3.14)

## Solutions Implemented

### 1. Automatic Python 3.14 Installation

Updated `setup-environment.sh` to automatically install Python 3.14 and set it as the default `python3`:

**RHEL/Fedora:**
```bash
sudo dnf install -y python3.14 python3.14-pip
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1
sudo alternatives --set python3 /usr/bin/python3.14
```

**Debian/Ubuntu:**
```bash
sudo apt-get install -y python3.14 python3.14-pip python3.14-venv
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1
sudo update-alternatives --set python3 /usr/bin/python3.14
```

### 2. Enhanced pip Installation

Added multiple fallback methods for pip installation:

```bash
# Try version-specific pip (e.g., python3.14-pip)
sudo dnf install -y python${PYTHON_VERSION}-pip

# Fall back to generic python3-pip
sudo dnf install -y python3-pip

# If still no pip, use ensurepip
python3 -m ensurepip --user
python3 -m pip install --upgrade pip --user
```

### 3. Use `python3 -m pip` Instead of `pip3`

Changed all pip commands to use `python3 -m pip` to ensure packages are installed for the correct Python version:

**Before:**
```bash
pip3 install --user notebooklm-py[browser]
```

**After:**
```bash
python3 -m pip install --user notebooklm-py[browser]
```

### 4. Full Path for Playwright

Updated playwright installation to use full path since it was just installed and may not be in PATH yet:

**Before:**
```bash
playwright install chromium
```

**After:**
```bash
$HOME/.local/bin/playwright install chromium
```

### 5. Python Version Check

Added version detection to automatically upgrade old Python versions:

```bash
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Check if version is at least 3.10
if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ]]; then
    echo "Python ${PYTHON_VERSION} is too old (need 3.10+)"
    echo "Upgrading to Python 3.14..."
    NEED_UPGRADE=true
fi
```

## Manual Fix (If Needed)

If you already have Python 3.14 but need to fix NotebookLM:

```bash
# 1. Install pip for Python 3.14 (choose one method)
sudo dnf install -y python3.14-pip                    # Preferred
# OR
python3.14 -m ensurepip --user
python3.14 -m pip install --upgrade pip --user

# 2. Uninstall old notebooklm from Python 3.9
rm -rf ~/.local/lib/python3.9/site-packages/notebooklm*

# 3. Install notebooklm-py for Python 3.14
python3 -m pip install notebooklm-py[browser] --user

# 4. Install Playwright Chromium
~/.local/bin/playwright install chromium

# 5. Install X11 dependencies (RHEL/Fedora)
sudo dnf install -y \
    xorg-x11-server-Xvfb \
    libX11 libXcomposite libXdamage libXext \
    libXrandr nss cups-libs libdrm \
    mesa-libgbm pango alsa-lib \
    at-spi2-atk gtk3

# 6. Verify
notebooklm --version
# Should show: NotebookLM CLI, version 0.7.x

# 7. Test login
xvfb-run notebooklm login
```

## Testing Instructions

### Fresh VM Test

```bash
# Clone repo
git clone <repository-url>
cd Project-APE

# Run setup (should install Python 3.14 automatically)
./setup-environment.sh

# Verify Python version
python3 --version
# Should show: Python 3.14.x

# Verify NotebookLM
notebooklm --version
# Should show: NotebookLM CLI, version 0.7.x

# Test login
xvfb-run notebooklm login
```

### Upgrade Existing Installation

```bash
# Pull latest changes
git pull

# Re-run setup (will upgrade Python if needed)
./setup-environment.sh

# Verify
python3 --version
notebooklm --version
```

## Files Modified

1. **setup-environment.sh**
   - Changed "Python 3" to "Python 3.14+" in all messages
   - Added automatic Python 3.14 installation for RHEL/Fedora and Debian/Ubuntu
   - Added version check to detect old Python versions
   - Enhanced pip installation with multiple fallback methods
   - Changed all `pip3` commands to `python3 -m pip`
   - Added full path to playwright command: `$HOME/.local/bin/playwright`
   - Added PYTHON_VERSION display during NotebookLM installation

## Platform Support

### macOS
- ✅ Python 3 via Homebrew (usually latest)
- ✅ No changes needed (Homebrew installs recent Python)

### RHEL/Fedora/Amazon Linux
- ✅ Python 3.14 via dnf
- ✅ python3.14-pip automatic installation
- ✅ alternatives system sets python3 → python3.14
- ✅ Full ensurepip fallback

### Debian/Ubuntu
- ✅ Python 3.14 via apt
- ✅ python3.14-pip automatic installation
- ✅ update-alternatives sets python3 → python3.14
- ✅ Full ensurepip fallback

## Why Python 3.14?

1. **Type hints compatibility**: notebooklm-py uses modern type hints (`str | None`) that require Python 3.10+
2. **Future-proofing**: Python 3.14 is the latest stable release
3. **Performance**: Newer Python versions have better performance
4. **Security**: Latest security patches and updates

## Key Takeaways

1. **Always use `python3 -m pip`** instead of `pip3` to ensure correct Python version
2. **Check pip module availability** after installing new Python versions
3. **Use full paths** for commands that were just installed and may not be in PATH yet
4. **Verify Python version** before installing packages with modern syntax requirements
5. **Use alternatives/update-alternatives** to manage multiple Python versions

---

**Status:** ✅ Fixed and ready for testing on fresh VM  
**Date:** 2026-06-18  
**Version:** 3.0.7
