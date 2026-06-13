# Project APE - Quick Start Guide

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="150"/>
</p>

<h2 align="center">Account Planning Engine</h2>
<h3 align="center">From Zero to Intelligence in 15 Minutes</h3>

<p align="center">
  <strong>Jason Anderson</strong> | Project Owner & Maintainer
</p>

---

## What is Project APE?

**Project APE** (Account Planning Engine) automatically generates comprehensive account intelligence by:
- 📄 **Consolidating** all client documents into a single PDF
- 🔍 **Researching** with NotebookLM's AI-powered deep analysis  
- 📝 **Creating** 6 comprehensive intelligence notes (consolidated)
- 🗺️ **Generating** interactive mind maps
- ⚡ **Fast Mode**: 10-12 minutes for 6 clients (62% faster!)
- 🔬 **Deep Mode**: 30-35 minutes for 6 clients with 90-180 sources/client

**Perfect for:** Sales engineers, account managers, solution architects preparing for customer meetings.

---

## Prerequisites (5 minutes)

### 1. Install Podman

**macOS:**
```bash
brew install podman
podman machine init
podman machine start
```

**RHEL/Fedora/CentOS:**
```bash
sudo dnf install podman
```

**Verify:**
```bash
podman --version
# Should show: podman version 4.0.0 or higher
```

### 2. Authenticate with NotebookLM

```bash
# Install NotebookLM Python SDK
pip install notebooklm-py

# Login (opens browser for Google sign-in)
notebooklm login
```

**You're ready!** 🎉

---

## Quick Start (10 minutes)

### Step 1: Get Project APE (1 minute)

```bash
git clone https://github.com/your-org/Project-APE.git
cd Project-APE
```

### Step 2: Setup Credentials (One-time, 2 minutes)

```bash
./setup-credentials.sh
```

**What this does:**
- Copies your NotebookLM credentials to a persistent volume
- Credentials work across all container runs
- Only needed once!

### Step 3: Prepare Your Client Data (2 minutes)

```bash
# Create client data directory
mkdir -p client_data/YourClient

# Add documents (PDFs, Word, Excel, PowerPoint, images, text files)
cp /path/to/client/documents/* client_data/YourClient/
```

### Step 4: Configure (3 minutes)

```bash
# Copy single-client example configuration
cp example-container.py vars.py

# Edit configuration
nano vars.py  # or use your favorite editor
```

**Minimal configuration:**
```python
# Set your role/perspective
persona = "Red Hat solutions architect"  # or account executive, marketing specialist, etc.

# Define your client
clients = ["yourclient"]

yourclient_name = "Your Client Name"
yourclient_industry = "their industry"
yourclient_subsegments = "key business areas"
yourclient_folder = "/app/client_data/YourClient"
```

**Persona Options:**
- `"Red Hat account executive"` - Sales-focused output
- `"Red Hat solutions architect"` - Technical depth (default)
- `"Red Hat marketing specialist"` - Campaign/messaging angles
- `"Red Hat customer success manager"` - Post-sale focus

### Step 5: Run! (2 minutes to start, 12-16 min to complete)

```bash
./ape-run.sh --vars ./vars.py --client-data ./client_data --clients yourclient --mode fast
```

**Watch the magic:**
```
✅ Already authenticated
✅ Created notebook: DEV_YourClient-TEST
✅ Consolidated PDF: YourClient-One.pdf
✅ Research complete, imported 24 sources
✅ Created note: Executive Summary
✅ Created note: SWOT Analysis
... (12 notes total)
✅ Mind map generated
Pipeline complete!
```

### Step 6: View Results

**Dashboard:** http://localhost:8765

**Files Generated:**
```
logs/
├── YourClient-One.pdf        # Consolidated document
└── yourclient.log             # Detailed execution log
```

**NotebookLM:** Open notebook `DEV_YourClient-TEST` at https://notebooklm.google.com

---

## What You Get

### 12 Intelligence Notes

1. **Executive Summary** - Key findings and trends
2. **PESTLE Analysis** - Political, Economic, Social, Technological, Legal, Environmental factors
3. **SWOT Analysis** - Strengths, Weaknesses, Opportunities, Threats
4. **Strategic Insights** - Market positioning and competitor analysis
5. **Product Fit** - RHEL, OpenShift, Ansible, Red Hat AI alignment
6. **Industry Analysis** - Sector trends and dynamics
7. **Technology Stack** - Current infrastructure and tools
8. **Business Challenges** - Pain points and opportunities
9. **Decision Makers** - Key stakeholders and influencers
10. **Competitive Landscape** - Alternatives and positioning
11. **Watchpoints** - Risks and unknowns to monitor
12. **Action Items** - Next steps and recommendations

### Interactive Mind Map

Visual representation of all intelligence, downloadable and shareable.

### Consolidated PDF

All client documents merged into one searchable PDF for easy reference.

---

## Next Steps

### Run Multiple Clients

```bash
./ape-run.sh \
    --vars ./vars.py \
    --client-data ./client_data \
    --clients client1,client2,client3 \
    --mode fast
```

Clients run **in parallel** for maximum speed!

### Use Deep Mode

For comprehensive research with 100+ sources:

```bash
./ape-run.sh --vars ./vars.py --clients important_client --mode deep
```

**Deep mode:**
- 2 research prompts with extensive sourcing (90-180 sources/client)
- Incremental deduplication after each prompt
- 30-35 minutes for 6 clients parallel
- Quality score: 8.0/10 (vs 5-6/10 in fast mode)
- Best for: High-volume days, maximum research depth

### Rerun with Fresh Data

If you add more documents:

```bash
# Just run again - it reuses the existing notebook and adds new research
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

---

## Common Tasks

### View Logs

```bash
tail -f logs/yourclient.log
```

### Stop a Running Pipeline

```bash
podman stop $(podman ps -q --filter ancestor=quay.io/jasoande/project_ape/project-ape)
```

### Re-authenticate NotebookLM

```bash
notebooklm auth logout
notebooklm login
./setup-credentials.sh  # Copy new credentials to volume
```

### Update to Latest Version

```bash
git pull
# Container automatically pulls latest image on next run
```

---

## Modes Comparison

| Feature | Fast Mode | Deep Mode |
|---------|-----------|-----------|
| **6 Clients (Parallel)** | 10-12 min | 30-35 min |
| **Single Client** | ~10 min | ~25-30 min |
| **Research Prompts** | 2 | 2 (extensive) |
| **Sources Imported** | ~20 | 90-180 |
| **Quality Score** | 5-6/10 | 8.0/10 |
| **Deduplication** | Final only | After each prompt |
| **Retry Rate** | <5% | ~30% (acceptable) |
| **Best For** | Daily operations | Maximum depth analysis |

---

## Troubleshooting

### "Not authenticated" Error

```bash
# Re-run credential setup
./setup-credentials.sh
```

### "Client folder not found"

Check that `client_data/YourClient` exists and matches your vars.py folder path.

### "Quota exceeded" in Deep Mode

This is normal with heavy usage. Solutions:
- Use fast mode for multiple clients
- Stagger deep mode runs (one at a time)
- Wait 30-60 minutes between deep runs

See [QUOTA-MANAGEMENT.md](QUOTA-MANAGEMENT.md) for details.

### Container Won't Start

```bash
# Check Podman is running
podman machine start

# Check for port conflicts
lsof -i :8765
```

---

## File Structure

```
Project-APE/
├── 📄 README.md                    # Full documentation
├── 🚀 QUICKSTART.md                # This file
├── 📋 CHANGELOG.md                 # Version history
├── 📖 QUOTA-MANAGEMENT.md          # Quota handling guide
│
├── 🔧 container-vars.py            # Example configuration
├── 📝 example-vars.py              # Alternative template
│
├── 🎯 ape-run.sh                   # Main runner script
├── 🔐 setup-credentials.sh         # One-time credential setup
├── 📦 Containerfile.debian         # Container build file
├── 🚪 container-entrypoint.sh      # Container startup script
│
├── 📂 core/                        # Python modules
│   ├── auth_manager.py
│   ├── client_pipeline.py
│   ├── notebook_manager.py
│   ├── source_manager.py
│   └── pdf_consolidator_fast.py
│
├── 🎨 dashboard/                   # Web UI
│   ├── server.py
│   ├── static/
│   └── templates/
│
├── 💬 ask_prompt_01.txt            # Research prompts
├── 💬 ask_prompt_02.txt
├── 📝 chat_prompt_01-12.txt        # Chat prompts (12 notes)
│
└── 📊 client_data/                 # Your client documents
    ├── Client1/
    ├── Client2/
    └── Client3/
```

---

## Advanced Usage

### Environment Variables

```bash
# Override image registry
./ape-run.sh --registry your-registry.io --namespace your-org

# Specify image tag
./ape-run.sh --tag 3.0.4
```

### Custom Prompts

Edit prompt files to customize intelligence output:
- `ask_prompt_01.txt` - Company deep-dive research
- `ask_prompt_02.txt` - Industry subsegment analysis
- `chat_prompt_01-12.txt` - 12 intelligence notes

Variables available: `$name`, `$industry`, `$subsegments`

### Container-less Execution

For development or local testing:

```bash
python main.py --mode fast --clients yourclient
```

**Requirements:**
- Python 3.10+
- `pip install -r requirements.txt`
- LibreOffice (for document conversion)
- Authenticated with `notebooklm login`

---

## Getting Help

### Documentation

- **Full Guide:** [README.md](README.md)
- **Container Operations:** [CONTAINER_GUIDE.md](CONTAINER_GUIDE.md)
- **Quota Management:** [QUOTA-MANAGEMENT.md](QUOTA-MANAGEMENT.md)
- **Production Deployment:** [PRODUCTION-READINESS.md](PRODUCTION-READINESS.md)
- **All Docs:** [DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md)

### Support

- **Issues:** https://github.com/anthropics/claude-code/issues
- **Contact:** Jason Anderson (project maintainer)

---

## What's Next?

1. **Add more clients** - Scale to your entire account portfolio
2. **Customize prompts** - Tailor intelligence to your needs
3. **Schedule runs** - Automate weekly/monthly updates
4. **Share with team** - Distribute container image via registry
5. **Integrate** - Connect to CRM, Slack, or other tools

---

<p align="center">
  <strong>Project APE</strong> - Turn documents into intelligence, automatically.
</p>

<p align="center">
  Version 3.0.4 | Jason Anderson | 2026
</p>

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="80"/>
</p>
