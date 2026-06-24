# Project APE - Python Dependencies

**Last Updated:** June 11, 2026  
**Python Version Required:** 3.10 or higher  
**Current Environment:** Python 3.13.13 ✅

---

## Quick Start

### Install All Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python3 check_dependencies.py
```

Expected output: `🎉 ALL DEPENDENCY CHECKS PASSED`

---

## Required Packages

All packages are available via PyPI and can be installed with pip.

### Google API & Authentication (7 packages)

Required for NotebookLM CLI authentication and Google API integration.

```
google-api-python-client>=2.140.0
google-api-core>=2.19.0
google-auth>=2.30.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
requests-oauthlib>=2.0.0
google-genai>=1.0.0
```

**Purpose:** 
- Authenticate with Google services for NotebookLM access
- **NEW:** `google-genai` for Gemini AI industry detection and subsegment generation

### Web Framework (2 packages)

```
flask>=3.0.0
werkzeug>=3.0.0
```

**Purpose:** Real-time dashboard at http://localhost:8765

### PDF Processing (4 packages)

```
pypdf>=4.0.0
PyPDF2>=3.0.0
reportlab>=4.0.0
Pillow>=10.0.0
```

**Purpose:** 
- Convert images/documents to PDF
- Merge multiple PDFs into single consolidated file
- Image processing and conversion

### Office Document Processing (3 packages)

```
python-docx>=1.0.0
openpyxl>=3.1.0
pandas>=2.0.0
```

**Purpose:**
- Read/convert Word documents (.docx)
- Read/convert Excel spreadsheets (.xlsx)
- Data manipulation and processing

### HTTP & Utilities (2 packages)

```
requests>=2.31.0
python-dateutil>=2.8.0
```

**Purpose:**
- HTTP requests for web operations
- Date/time parsing and manipulation

---

## Standard Library Modules

These are included with Python and require no installation:

- `json` - JSON parsing
- `logging` - Logging framework
- `pathlib` - Path operations
- `subprocess` - Shell command execution
- `time` - Time operations
- `re` - Regular expressions
- `typing` - Type hints
- `tempfile` - Temporary file handling
- `random` - Random number generation
- `multiprocessing` - Parallel processing
- `concurrent.futures` - Thread/process pools
- `sys` - System operations
- `shutil` - File operations
- `os` - Operating system interface

---

## External Dependencies

### NotebookLM CLI (Required)

**Installation:**

```bash
# Install Node.js first (required for NotebookLM CLI)
brew install node  # macOS
# OR
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs  # RHEL/Fedora

# Install NotebookLM CLI globally
npm install -g notebooklm

# Verify installation
notebooklm --version
```

**Current Version:** 0.7.1 ✅

### LibreOffice (Required for Office Documents)

**Installation:**

```bash
# macOS
brew install --cask libreoffice

# RHEL/Fedora
sudo dnf install libreoffice
```

**Purpose:** Converts Office documents (.docx, .xlsx, .pptx) to PDF

---

## Version Compatibility

### Python Version

- **Minimum:** Python 3.10
- **Recommended:** Python 3.13+
- **Current:** Python 3.13.13 ✅

**Why 3.10+?**
- Type hints: `tuple[str, bool]` syntax (not `Tuple[str, bool]`)
- Pattern matching features
- Better error messages

### Package Versions

All versions specified in `requirements.txt` use `>=` to allow compatible upgrades:

- **Exact match NOT required** - newer versions accepted
- **Minimum versions specified** - older versions may have bugs
- **Tested with:** Versions shown above

---

## Dependency Check Script

### Usage

```bash
python3 check_dependencies.py
```

### What It Checks

1. ✅ **Python Version** - Ensures 3.10+
2. ✅ **Requirements File** - Validates requirements.txt exists
3. ✅ **Package Imports** - Tests all imports work
4. ✅ **Pip Compatibility** - Checks for dependency conflicts

### Example Output

```
======================================================================
SUMMARY
======================================================================
✅ PASS: Python Version
✅ PASS: Requirements File
✅ PASS: Package Imports
✅ PASS: Pip Compatibility

======================================================================
🎉 ALL DEPENDENCY CHECKS PASSED
======================================================================
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "error: externally-managed-environment"

**Solution (use virtual environment):**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### "LibreOffice not found"

**Solution:**
```bash
# macOS
brew install --cask libreoffice

# Linux
sudo dnf install libreoffice
```

### "notebooklm: command not found"

**Solution:**
```bash
# Install Node.js first
brew install node  # macOS

# Then install NotebookLM CLI
npm install -g notebooklm
```

### Dependency Conflicts

**Check for conflicts:**
```bash
pip check
```

**Fix conflicts:**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Installation Verification

### Step-by-Step Verification

1. **Check Python version:**
   ```bash
   python3 --version
   ```
   Expected: Python 3.10+ ✅

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Expected: All packages install successfully ✅

3. **Run dependency check:**
   ```bash
   python3 check_dependencies.py
   ```
   Expected: All checks pass ✅

4. **Verify NotebookLM CLI:**
   ```bash
   notebooklm --version
   ```
   Expected: 0.7.1 or higher ✅

5. **Run validation:**
   ```bash
   python3 validate_setup.py
   ```
   Expected: All validations pass ✅

---

## Upgrade Guide

### Upgrade All Packages

```bash
pip install -r requirements.txt --upgrade
```

### Upgrade Specific Package

```bash
pip install --upgrade <package-name>
```

### Freeze Current Versions

```bash
pip freeze > requirements-locked.txt
```

---

## Docker Support

### Dockerfile (Example)

```dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install NotebookLM CLI
RUN npm install -g notebooklm

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

CMD ["python3", "main.py"]
```

---

## Development Dependencies

For development/testing, you may also want:

```bash
# Code formatting
pip install black

# Linting
pip install pylint flake8

# Type checking
pip install mypy
```

---

## Package Summary

| Category | Count | Size (approx) |
|----------|-------|---------------|
| Google API | 6 | ~50 MB |
| Web Framework | 2 | ~10 MB |
| PDF Processing | 4 | ~30 MB |
| Office Docs | 3 | ~40 MB |
| Utilities | 2 | ~5 MB |
| **Total** | **17** | **~135 MB** |

Plus standard library modules (0 MB - included with Python)

---

## Support

**Issue:** Missing dependencies  
**Solution:** Run `python3 check_dependencies.py` for diagnostics

**Issue:** Version conflicts  
**Solution:** Use virtual environment

**Issue:** System dependencies (LibreOffice, Node.js)  
**Solution:** See installation instructions above

---

## Related Documentation

- **Installation Guide:** [README.md](README.md#installation)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Validation:** `python3 validate_setup.py`
- **Testing:** `python3 check_dependencies.py`

---

**All dependencies are pip-installable and well-maintained!** ✅
