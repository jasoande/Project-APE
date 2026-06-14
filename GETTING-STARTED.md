# Getting Started with Project APE

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="120"/>
</p>

<h3 align="center">Deployment Guide</h3>

<p align="center">
  Jason Anderson | Project Owner & Maintainer
</p>

---

**Choose your deployment method** - Container (recommended) or Local installation.

---

## Which Method Should I Use?

### Use Container If...

✅ You just want to **run Project APE**  
✅ You're an **account team member**  
✅ You **don't need to modify the code**  
✅ You want **automatic updates**  
✅ You want **no dependency hassles**  

**→ Go to:** [Container Quick Start](#container-quick-start-5-minutes)

---

### Use Local Install If...

✅ You're **developing Project APE**  
✅ You need to **customize the code**  
✅ You want to **contribute to the project**  
✅ You're **debugging issues**  
✅ You prefer **traditional Python workflow**  

**→ Go to:** [Local Installation](#local-installation-15-minutes)

---

## Container Quick Start (5 minutes)

### Prerequisites

- **Podman** installed
- **Google account** (for NotebookLM)
- **Client data files**

### Steps

#### 1. Install Podman (one-time)

**macOS:**
```bash
brew install podman
podman machine init
podman machine start
```

**RHEL/Fedora:**
```bash
sudo dnf install podman
```

**Ubuntu:**
```bash
sudo apt-get install podman
```

#### 2. Get Project APE

```bash
# Clone repo (for config files and scripts)
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
```

#### 3. Configure Your Clients

```bash
# Copy single-client template (recommended for first time)
cp example-container.py vars.py

# Or use multi-client template
# cp container-vars.py vars.py

# Edit with your clients
nano vars.py
```

**Example:**
```python
# Set your role/perspective
persona = "Red Hat solutions architect"

# Define your client
clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_subsegments = "cloud computing, enterprise software"
acme_corp_folder = "/app/client_data/ACME"
```

**Persona options:** account executive, solutions architect, marketing specialist, customer success manager

#### 4. Add Client Data

```bash
mkdir -p client_data/ACME
cp ~/Documents/ACME/*.pdf client_data/ACME/
```

#### 5. Login to NotebookLM (one-time)

```bash
npm install -g notebooklm
notebooklm login
```

#### 6. Run!

```bash
./ape-run.sh --mode fast
```

**That's it!** Results in `logs/` directory.

### Full Guide

See **[QUICKSTART.md](QUICKSTART.md)** for detailed instructions.

---

## Local Installation (15 minutes)

### Prerequisites

- **Python 3.10+**
- **pip**
- **LibreOffice** (for PDF conversion)
- **Node.js 18+** (for NotebookLM CLI)

### Steps

#### 1. Install System Dependencies

**macOS:**
```bash
brew install --cask libreoffice
brew install node git
```

**RHEL/Fedora:**
```bash
sudo dnf install -y libreoffice python3-pip
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs
```

**Ubuntu:**
```bash
sudo apt-get install -y libreoffice python3-pip nodejs npm
```

#### 2. Clone Repository

```bash
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
```

#### 3. Install Python Dependencies

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install NotebookLM CLI

```bash
npm install -g notebooklm
notebooklm login
```

#### 5. Configure Clients

```bash
cp example-vars.py vars.py
nano vars.py  # Edit with your clients
```

**Example (with Gemini AI auto-detection):**
```python
# Enable Gemini AI
GEMINI_API_KEY="your-gemini-api-key"  # Add to .env file

GEMINI_CONFIG = {
    'enabled': True,
    'model': 'gemini-2.5-flash',
}

clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_folder = str(Path(__file__).parent / "client_data" / "ACME")
# Industry & subsegments auto-detected by Gemini AI
```

**Example (manual configuration):**
```python
clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_subsegments = "cloud infrastructure, enterprise software"
acme_corp_folder = str(Path(__file__).parent / "client_data" / "ACME")
```

> **NEW:** Gemini AI can automatically detect industry and subsegments!  
> See [GEMINI-INTEGRATION.md](GEMINI-INTEGRATION.md) for setup guide.

#### 6. Add Client Data

```bash
mkdir -p client_data/ACME
cp ~/Documents/ACME/*.pdf client_data/ACME/
```

#### 7. Run!

```bash
python3 main.py --mode fast --clients acme_corp
```

### Full Guide

See **Installation** section in [README.md](README.md) for detailed instructions.

---

## Comparison

| Feature | Container | Local Install |
|---------|-----------|---------------|
| **Setup Time** | 5 minutes | 15 minutes |
| **Dependencies** | None (in container) | Python, LibreOffice, Node.js |
| **Updates** | `podman pull` | `git pull` + `pip install` |
| **Portability** | ✅ Works anywhere | ⚠️ Depends on system |
| **Customization** | ❌ Code in container | ✅ Full access |
| **Development** | ❌ Not ideal | ✅ Perfect |
| **Production** | ✅ Recommended | ✅ Works |
| **Team Distribution** | ✅ Easy (pull image) | ⚠️ Each installs deps |

---

## What Happens When You Run

### Pipeline Flow

```
1. PDF Consolidation (1-2 min)
   └─→ Converts all docs to single PDF

2. Notebook Creation (5s)
   └─→ Creates NotebookLM notebook

3. Source Upload (1-2 min)
   └─→ Uploads consolidated PDF

4. Research Phase (3-5 min in fast mode)
   └─→ Runs 20 strategic research questions
   └─→ Adds 10-20 web sources

5. Analysis Phase (8-10 min)
   └─→ Generates 12 strategic notes:
       • Executive Summary
       • Industry Analysis
       • Technology Recommendations
       • Solution Ideas
       • Account Plan
       • ... and 7 more

6. Mind Map (1 min)
   └─→ Creates visual summary

7. Complete! (13-15 min total)
   └─→ Output in logs/ directory
```

### Output Files

```
logs/
├── project_ape_YYYYMMDD_HHMMSS.log
└── ACME/
    ├── ACME-Executive-Brief.pdf
    ├── ACME-Mind-Map.pdf
    ├── ACME-Research.txt
    └── ACME-One.pdf  ← Complete consolidated output
```

### Dashboard

Open browser to **http://localhost:8765** to watch progress in real-time.

---

## Common Workflows

### First-Time Setup (Container)

```bash
# Day 1: Setup
brew install podman
podman machine init && podman machine start
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
npm install -g notebooklm
notebooklm login

# Day 1: First run
cp container-vars.py vars.py
nano vars.py  # Configure
mkdir -p client_data/Client1
cp ~/docs/*.pdf client_data/Client1/
./ape-run.sh --mode fast

# Day 2+: Regular use
./ape-run.sh --mode fast
```

### First-Time Setup (Local)

```bash
# Day 1: Setup
brew install --cask libreoffice
brew install node git
git clone https://github.com/jasoande/Project-APE.git
cd Project-APE
pip install -r requirements.txt
npm install -g notebooklm
notebooklm login

# Day 1: First run
cp example-vars.py vars.py
nano vars.py  # Configure
mkdir -p client_data/Client1
cp ~/docs/*.pdf client_data/Client1/
python3 main.py --mode fast --clients client1

# Day 2+: Regular use
python3 main.py --mode fast
```

### Weekly Account Planning Run

```bash
# Update client data
cp ~/new-docs/*.pdf client_data/ACME/

# Run analysis
./ape-run.sh --mode fast --clients acme_corp

# Review output
open logs/ACME/ACME-One.pdf
```

### Multiple Clients (Parallel)

```bash
# Update vars.py with all clients
clients = ["acme", "globex", "initech"]

# Run all in parallel (fast mode)
./ape-run.sh --mode fast

# Or specific clients
./ape-run.sh --mode fast --clients acme,globex
```

---

## Next Steps

### After Your First Run

1. ✅ **Review output** - Open the `-One.pdf` file
2. ✅ **Check NotebookLM** - Click link in dashboard
3. ✅ **Adjust timing** - Edit `vars.py` if needed
4. ✅ **Add more clients** - Scale to your accounts
5. ✅ **Try deep mode** - For critical accounts

### Customization

**Container users:**
- Edit `vars.py` for clients and settings
- Client data in `client_data/`
- Can't modify code (it's in container)

**Local users:**
- Edit `vars.py` for clients and settings
- Edit prompt templates in project root
- Modify Python code as needed

### Getting Help

- **Container:** [QUICKSTART.md](QUICKSTART.md), [README-CONTAINER.md](README-CONTAINER.md)
- **Local:** [README.md](README.md)
- **Auth:** [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)
- **Issues:** GitHub Issues

---

## Troubleshooting

### Container Issues

```bash
# Podman not running (Mac)
podman machine start

# Image pull failed
podman login quay.io
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Volume mount errors
realpath ./vars.py  # Must be absolute paths
```

### Local Issues

```bash
# LibreOffice not found
brew install --cask libreoffice  # macOS
sudo dnf install libreoffice     # RHEL

# Python package errors
pip install -r requirements.txt --force-reinstall

# NotebookLM auth
notebooklm logout
notebooklm login
```

### Common to Both

```bash
# Check NotebookLM auth
notebooklm status

# View logs
tail -f logs/*.log

# Check dashboard
open http://localhost:8765
```

---

## Summary

### Container (Recommended)

```bash
# 3 commands to get started
podman pull quay.io/jasoande/project_ape/project-ape:latest
cp container-vars.py vars.py && nano vars.py
./ape-run.sh --mode fast
```

✅ **Best for:** Account teams, production use  
✅ **Setup:** 5 minutes  
✅ **Maintenance:** Zero  

---

### Local Install

```bash
# Setup and run
pip install -r requirements.txt
notebooklm login
python3 main.py --mode fast
```

✅ **Best for:** Development, customization  
✅ **Setup:** 15 minutes  
✅ **Maintenance:** Manual updates  

---

**Project APE - Getting Started Guide**  
Version 3.0.4 | Jason Anderson | 2026
