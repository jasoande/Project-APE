<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # User Guide
  **Project APE - Account Planning Engine**
</div>

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Workflow Overview](#workflow-overview)
3. [Configuration](#configuration)
4. [Running Workflows](#running-workflows)
5. [Monitoring Progress](#monitoring-progress)
6. [Understanding Outputs](#understanding-outputs)
7. [Quality Scores](#quality-scores)
8. [Execution Modes](#execution-modes)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites Checklist

Before running your first workflow, ensure you have completed:

- ✅ **Installation**: Python 3.10+, NotebookLM CLI installed
- ✅ **NotebookLM Authentication**: `notebooklm login` completed
- ✅ **Google Drive OAuth**: Credentials configured, token generated
- ✅ **Client Data**: PDFs uploaded to Google Drive folders
- ✅ **Configuration**: `vars.py` file created and configured

If any item is incomplete, see [INSTALLATION.md](INSTALLATION.md) for setup instructions.

### Quick Start Checklist

1. **Prepare client data** - Upload PDFs to Google Drive folder
2. **Configure client** - Add client details to `vars.py`
3. **Launch workflow** - Run `ape-run.sh` with client name
4. **Monitor progress** - Watch dashboard at http://localhost:8765
5. **Review outputs** - Check `docs_generated/<client_id>/` for results

**Total time**: 15-60 minutes depending on mode

---

## Workflow Overview

Project APE executes a five-phase workflow for each client:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PROJECT APE WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

Phase 1: Document Download (30-60 seconds)
         ↓
         • Connect to Google Drive via OAuth
         • Download PDFs from client folder
         • Convert Google Docs to PDF
         • Cache files locally (7-day TTL)

Phase 2: Notebook Creation (10-15 seconds)
         ↓
         • Create NotebookLM notebook
         • Upload consolidated sources
         • Wait for source processing

Phase 3: Research Phase (3-8 minutes)
         ↓
         • Execute 2 research queries
         • Import 20-180 external sources
         • Analyze industry & competitive landscape

Phase 4: Analysis Phase (8-12 minutes)
         ↓
         • Run 6 consolidated analysis prompts
         • Generate strategic insights
         • Identify opportunities and risks

Phase 5: Quality Validation (1-2 minutes)
         ↓
         • Validate completeness
         • Generate quality score (1-10)
         • Create summary outputs

         ↓
    ✅ COMPLETE
```

### Total Execution Time

- **Fast Mode**: 15-20 minutes (all clients in parallel)
- **Deep Mode**: 45-60 minutes (all clients in parallel)

---

## Configuration

### Configuration File (vars.py)

The `vars.py` file contains all client and system configuration.

#### Creating Your Configuration

```bash
# Copy example configuration
cp developer-docs/example-vars.py vars.py

# Edit with your preferred editor
vi vars.py
# or
nano vars.py
# or
code vars.py  # VS Code
```

#### Basic Configuration Template

```python
# ============================================================
# Project APE Configuration
# ============================================================

# List of client IDs to process
clients = ["acme_corp", "techstart_inc"]

# ============================================================
# Client 1: Acme Corporation
# ============================================================

acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/1ABC123XYZ456"
acme_corp_industry = ""  # Leave empty for auto-detection
acme_corp_subsegments = "cloud, AI/ML, enterprise software"

# ============================================================
# Client 2: TechStart Inc
# ============================================================

techstart_inc_name = "TechStart Inc"
techstart_inc_folder = "https://drive.google.com/drive/folders/2DEF789UVW012"
techstart_inc_industry = "technology"
techstart_inc_subsegments = "SaaS, DevOps, cybersecurity"

# ============================================================
# Global Settings
# ============================================================

# Persona for analysis (solutions architect, account executive, etc.)
persona = "solutions architect"

# Default execution mode (fast or deep)
default_mode = "fast"

# Dashboard port
DASHBOARD_PORT = 8765
```

### Configuration Parameters

#### Per-Client Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `{client_id}_name` | Yes | Full company name | `"Acme Corporation"` |
| `{client_id}_folder` | Yes | Google Drive folder URL | `"https://drive.google.com/..."` |
| `{client_id}_industry` | No | Industry (or "" for auto-detect) | `"technology"` |
| `{client_id}_subsegments` | No | Industry subsegments | `"cloud, AI, SaaS"` |

#### Global Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `persona` | `"solutions architect"` | AI analysis perspective |
| `default_mode` | `"fast"` | Default execution mode |
| `DASHBOARD_PORT` | `8765` | Web dashboard port |

### Getting Google Drive Folder URLs

1. Open Google Drive in browser
2. Navigate to your client folder
3. Click "Share" button
4. Copy the link (format: `https://drive.google.com/drive/folders/FOLDER_ID`)
5. Paste into `{client_id}_folder` parameter

**Important**: Ensure your Google account has access to the folder.

### Industry Auto-Detection

Leave `{client_id}_industry` as empty string `""` for automatic industry detection:

```python
acme_corp_industry = ""  # AI will detect industry from documents
```

Or specify manually:

```python
acme_corp_industry = "technology"  # Skip auto-detection
```

Supported industries:
- `technology`
- `financial_services`
- `healthcare`
- `manufacturing`
- `retail`
- `energy`
- `telecommunications`
- `education`
- `government`

### Subsegments

Subsegments provide targeted research focus. Examples:

**Technology:**
```python
subsegments = "cloud services, SaaS platforms, cybersecurity, AI/ML, DevOps"
```

**Financial Services:**
```python
subsegments = "banking, insurance, wealth management, fintech, payments"
```

**Healthcare:**
```python
subsegments = "hospitals, pharmaceuticals, medical devices, health IT, telehealth"
```

**Manufacturing:**
```python
subsegments = "automotive, aerospace, electronics, supply chain, IoT"
```

---

## Running Workflows

### Container-Based Execution (Recommended)

#### Single Client - Fast Mode

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast
```

#### Single Client - Deep Mode

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode deep
```

#### Multiple Clients (Parallel Execution)

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp,techstart_inc,globalbank --mode fast
```

Project APE processes all clients **in parallel**, so 3 clients take the same time as 1 client.

#### Force Cache Refresh

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast --refresh
```

Use `--refresh` to force re-download of all Drive files (ignores 7-day cache).

### Native Python Execution

```bash
# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Run workflow
python3 main.py --mode fast --clients acme_corp

# Multiple clients
python3 main.py --mode fast --clients acme_corp,techstart_inc

# Deep mode
python3 main.py --mode deep --clients acme_corp
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--vars` | Path to configuration file | `--vars ./vars.py` |
| `--clients` | Comma-separated client IDs | `--clients acme_corp,techstart_inc` |
| `--mode` | Execution mode (fast/deep) | `--mode fast` |
| `--refresh` | Force cache refresh | `--refresh` |

---

## Monitoring Progress

### Web Dashboard

Open the dashboard in your browser:

```
http://localhost:8765
```

The dashboard auto-opens when using `ape-run.sh`.

### Dashboard Layout

#### Header Section

- **Logo**: Project APE King Kong logo
- **Timer**: Total execution time
- **Counts**: Total/Running/Complete/Failed clients
- **Progress Bar**: Overall workflow progress

#### Client Cards

Each client shows:

- **Client Name**: Full company name
- **Status**: RUNNING, COMPLETE, or FAILED
- **Phase**: Current pipeline phase
- **Progress**: Phase-specific progress percentage
- **Quality Score**: 1-10 score (when complete)
- **NotebookLM Link**: Direct link to notebook (clickable)
- **Timing**: Phase and total elapsed time

#### Logs Section (Collapsible)

- **Real-Time Logs**: Live log streaming
- **Controls**: Pause, Resume, Clear, Download
- **Auto-Scroll**: Automatically scrolls to latest logs
- **Visual Indicators**: Color-coded log levels

### Dashboard Features

**Auto-Refresh:**
- Updates every 2 seconds
- Continues for 5 minutes after all clients complete
- Graceful shutdown when finished

**Log Controls:**
- **⏸ Pause**: Stop log auto-scroll
- **▶ Resume**: Resume auto-scroll
- **🗑 Clear**: Clear log display (doesn't delete files)
- **📥 Download**: Download complete log file

### Monitoring from Terminal

If you prefer terminal monitoring:

```bash
# Watch overall log
tail -f logs/overall.log

# Watch specific client
tail -f logs/acme_corp.log

# Monitor all clients
tail -f logs/*.log

# Search for errors
grep -i error logs/*.log
grep -i failed logs/*.log
```

### Status Files

Real-time status files are stored in `.multi_process_status/`:

```bash
# View client status (JSON)
cat .multi_process_status/acme_corp.json

# Watch status updates
watch -n 2 cat .multi_process_status/acme_corp.json
```

Example status file:

```json
{
  "client_id": "acme_corp",
  "client_name": "Acme Corporation",
  "status": "RUNNING",
  "current_phase": "Research Phase",
  "progress": 45,
  "quality_score": null,
  "notebook_url": "https://notebooklm.google.com/notebook/abc123",
  "start_time": "2026-06-30T10:15:00",
  "phase_timings": {
    "download": 42,
    "notebook_creation": 12,
    "research": 187
  }
}
```

---

## Understanding Outputs

### Output Directory Structure

```
docs_generated/
├── acme_corp/
│   ├── Acme_Corporation_Research.txt
│   ├── Acme_Corporation_Analysis.txt
│   ├── Quality_Score.json
│   ├── NotebookLM_Link.txt
│   └── Execution_Summary.json
├── techstart_inc/
│   └── ...
└── ...
```

### Generated Files

#### 1. Research Output (`{Client_Name}_Research.txt`)

Contains research query responses:

- Industry analysis and trends
- Competitive landscape overview
- Market positioning insights
- Technology adoption patterns

**Example excerpt:**

```
=== RESEARCH QUERY 1: Industry Analysis ===

Industry: Technology - Cloud Services

Key Trends:
- Multi-cloud adoption accelerating (65% of enterprises)
- Hybrid cloud architectures becoming standard
- Edge computing integration with cloud platforms
- AI/ML workload optimization focus

Market Dynamics:
...
```

#### 2. Analysis Output (`{Client_Name}_Analysis.txt`)

Contains analysis prompt responses:

- Strategic challenges and opportunities
- Decision maker profiles
- Buying process insights
- Value proposition recommendations
- Risk factors and mitigation strategies

**Example excerpt:**

```
=== ANALYSIS: Strategic Challenges ===

Current Challenges:
1. Legacy system modernization
   - Aging infrastructure (10+ year old systems)
   - Technical debt accumulation
   - Limited cloud integration
   
2. Skills gap in emerging technologies
   - Container orchestration expertise
   - Cloud-native architecture knowledge
   
...
```

#### 3. Quality Score (`Quality_Score.json`)

Automated quality validation:

```json
{
  "overall_score": 8.5,
  "metrics": {
    "source_count": 127,
    "source_quality": 9.0,
    "content_completeness": 8.5,
    "research_depth": 8.0,
    "analysis_coverage": 9.0
  },
  "validation_timestamp": "2026-06-30T10:45:32",
  "mode": "fast"
}
```

#### 4. NotebookLM Link (`NotebookLM_Link.txt`)

Direct link to NotebookLM notebook:

```
https://notebooklm.google.com/notebook/abc123xyz456
```

Open this link to:
- View all imported sources
- Ask additional questions
- Generate mind maps
- Export notes and insights

#### 5. Execution Summary (`Execution_Summary.json`)

Workflow execution details:

```json
{
  "client_id": "acme_corp",
  "client_name": "Acme Corporation",
  "execution_mode": "fast",
  "total_duration_seconds": 1247,
  "phase_timings": {
    "download": 42,
    "notebook_creation": 12,
    "research": 187,
    "analysis": 623,
    "validation": 89
  },
  "sources_imported": 127,
  "queries_executed": 8,
  "completion_timestamp": "2026-06-30T10:45:32"
}
```

---

## Quality Scores

### Scoring Scale

Quality scores range from **1 to 10**:

| Score | Quality | Description |
|-------|---------|-------------|
| 9-10 | Excellent | Comprehensive research, high source quality |
| 8-8.9 | Very Good | Strong coverage, good source diversity |
| 7-7.9 | Good | Adequate research, acceptable sources |
| 6-6.9 | Fair | Limited coverage, some gaps |
| Below 6 | Poor | Insufficient research, re-run recommended |

### Score Components

Quality scores are calculated from five metrics:

1. **Source Count** (weight: 20%)
   - Fast mode target: 50+ sources
   - Deep mode target: 120+ sources

2. **Source Quality** (weight: 25%)
   - Authoritative domains (e.g., company websites, industry publications)
   - Recent publications (within 2 years)
   - Diverse source types

3. **Content Completeness** (weight: 25%)
   - All analysis prompts answered
   - Sufficient detail in responses
   - No missing sections

4. **Research Depth** (weight: 15%)
   - Research query quality
   - Citation coverage
   - External source integration

5. **Analysis Coverage** (weight: 15%)
   - All strategic dimensions addressed
   - Actionable insights provided
   - Risk assessment included

### Interpreting Scores

**Score: 8.5+** ✅
- High-quality output, ready for use
- Comprehensive research coverage
- Strong source diversity
- No action needed

**Score: 7.0-8.4** ⚠️
- Good quality, usable output
- Consider deep mode for critical accounts
- Review for any gaps

**Score: Below 7.0** ❌
- Insufficient quality
- Re-run in deep mode
- Check client folder for adequate source documents
- Verify NotebookLM research completed successfully

### Improving Quality Scores

**Low source count:**
- Add more PDFs to client Drive folder
- Use deep mode for more web research
- Ensure Drive folder is accessible

**Low content completeness:**
- Verify all prompts executed successfully
- Check logs for errors
- Re-run workflow if failures occurred

**Low research depth:**
- Switch to deep mode
- Add industry subsegments to `vars.py`
- Provide more detailed source documents

---

## Execution Modes

### Fast Mode

**Duration**: 15-20 minutes (all clients)

**Characteristics:**
- Aggressive timing (shorter delays)
- 20-50 sources per client
- ~5% retry rate
- Quality target: 8.0+

**Best for:**
- Quick account overviews
- Initial research scoping
- Time-sensitive situations
- Multiple account batches

**When to use:**
- First-time account research
- Pre-meeting preparation
- Quarterly account reviews
- Pipeline research

### Deep Mode

**Duration**: 45-60 minutes (all clients)

**Characteristics:**
- Conservative timing (longer delays)
- 90-180 sources per client
- ~30% retry rate (acceptable)
- Quality target: 8.5+

**Best for:**
- High-value accounts
- Strategic planning
- Comprehensive analysis
- Critical opportunities

**When to use:**
- Strategic account planning
- Major deal preparation
- Executive briefings
- Competitive analysis

### Mode Comparison

| Aspect | Fast Mode | Deep Mode |
|--------|-----------|-----------|
| Duration | 15-20 min | 45-60 min |
| Sources | 20-50 | 90-180 |
| Research queries | 2 | 2 |
| Analysis prompts | 6 | 6 |
| Query delays | 8-12s | 15-25s |
| Prompt delays | 5-8s | 10-15s |
| Quality target | 8.0+ | 8.5+ |

### Choosing a Mode

**Use Fast Mode when:**
- ✅ You need results quickly (< 30 minutes)
- ✅ Processing multiple accounts
- ✅ Initial research phase
- ✅ Score 8.0+ is acceptable

**Use Deep Mode when:**
- ✅ Account is high-value or strategic
- ✅ You need maximum source coverage
- ✅ Preparing for executive meetings
- ✅ Score 8.5+ is required
- ✅ Time is not critical

---

## Advanced Features

### Cache Management

Project APE caches Drive files for 7 days to improve performance.

**View cache status:**

```bash
# Check cache directory
ls -lah ~/.project-ape/drive_cache/

# View cache metadata
cat ~/.project-ape/drive_cache/cache_metadata.json
```

**Force cache refresh:**

```bash
./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast --refresh
```

Use `--refresh` when:
- Client added new documents to Drive
- You need latest versions of files
- Cache may be stale

### Parallel Processing

Project APE processes multiple clients simultaneously:

```bash
# Process 5 clients in parallel (recommended maximum)
./developer-docs/ape-run.sh --vars ./vars.py --clients client1,client2,client3,client4,client5 --mode fast
```

**Anti-Thundering-Herd Protection:**
- Random initial offset (0-30s) per client
- Prevents synchronized API calls
- Improves success rate

**Resource Considerations:**
- Recommended: 1-5 clients
- Maximum tested: 6 clients
- Each client uses ~500MB RAM

### Custom Personas

Customize the AI analysis perspective:

```python
# vars.py
persona = "Red Hat solutions architect specializing in OpenShift"
```

Examples:
- `"solutions architect"`
- `"account executive"`
- `"sales engineer"`
- `"business development manager"`
- `"enterprise architect"`

The persona influences analysis tone and focus.

### Custom Timing

Adjust timing for your environment:

```python
# vars.py - Custom fast mode timing
TIMINGS = {
    'ask_prompt_delay': (10.0, 15.0),     # Slower research queries
    'chat_prompt_delay': (6.0, 9.0),      # Slightly slower prompts
    'source_processing_wait': 35,          # Longer source wait
}

# Custom deep mode timing
DEEP_TIMINGS = {
    'ask_prompt_delay': (20.0, 30.0),     # Very conservative
    'chat_prompt_delay': (12.0, 18.0),    # Extra safe
    'source_processing_wait': 50,          # Extended wait
}
```

**When to adjust:**
- Experiencing high retry rates (> 10% in fast mode)
- API quota limitations
- Network latency issues

---

## Best Practices

### Before Running Workflows

**✅ Organize Client Data**
- Create dedicated Drive folders per client
- Upload relevant PDFs (annual reports, presentations, case studies)
- Ensure your Google account has access
- Aim for 5-20 documents per client

**✅ Test Authentication**
```bash
# Verify NotebookLM
notebooklm list

# Verify Drive access
python3 -c "from core.drive_manager import DriveManager; dm = DriveManager(); print('OK')"
```

**✅ Start Small**
- First run: 1 client, fast mode
- Verify outputs and quality
- Then scale to multiple clients

### During Execution

**✅ Monitor Dashboard**
- Keep dashboard open: http://localhost:8765
- Watch for errors or stalled progress
- Review logs for warnings

**✅ Don't Interrupt**
- Let workflows complete fully
- Interrupting can create partial outputs
- Use Ctrl+C only if necessary

**❌ Avoid**
- Running multiple workflows simultaneously
- Closing terminal/browser mid-execution
- Modifying `vars.py` during execution

### After Completion

**✅ Review Quality Scores**
- Target: 8.0+ (fast), 8.5+ (deep)
- Re-run if score < 7.0

**✅ Access NotebookLM**
- Open link from `NotebookLM_Link.txt`
- Ask follow-up questions
- Generate mind maps

**✅ Archive Outputs**
```bash
# Create timestamped backup
tar -czf outputs_$(date +%Y%m%d).tar.gz docs_generated/
```

### Workflow Optimization

**For Regular Use:**

1. **Batch Processing**
   ```bash
   # Process all clients weekly
   ./developer-docs/ape-run.sh --vars ./vars.py --clients all --mode fast
   ```

2. **Incremental Updates**
   ```bash
   # Refresh specific client with new data
   ./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast --refresh
   ```

3. **Quality-First Approach**
   - Start with fast mode
   - If score < 8.0, re-run in deep mode
   - Archive high-quality outputs

**For High-Value Accounts:**

1. Always use deep mode
2. Review outputs manually before use
3. Ask follow-up questions in NotebookLM
4. Generate multiple perspectives (re-run with different personas)

### Troubleshooting Workflow

If workflow fails:

1. **Check logs**
   ```bash
   tail -f logs/overall.log
   grep -i error logs/*.log
   ```

2. **Verify authentication**
   ```bash
   notebooklm list
   ls -la ~/.project-ape/*.json
   ```

3. **Check Drive access**
   - Open Drive folder URL in browser
   - Verify PDFs are accessible

4. **Re-run with verbose logging**
   ```bash
   # Add debug logging
   export LOG_LEVEL=DEBUG
   ./developer-docs/ape-run.sh --vars ./vars.py --clients acme_corp --mode fast
   ```

5. **Consult troubleshooting guide**
   - See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Getting Help

### Documentation

- **Installation Issues**: [INSTALLATION.md](INSTALLATION.md)
- **Technical Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Container Deployment**: [developer-docs/DEPLOYMENT.md](../developer-docs/DEPLOYMENT.md)
- **Common Problems**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Support Channels

- **GitHub Issues**: https://github.com/yourusername/project-ape/issues
- **GitHub Discussions**: https://github.com/yourusername/project-ape/discussions

### Reporting Issues

When reporting issues, include:

1. **System Information**
   ```bash
   python3 --version
   podman --version  # or docker --version
   uname -a
   ```

2. **Error Logs**
   ```bash
   # Upload complete logs
   tar -czf logs_$(date +%Y%m%d).tar.gz logs/
   ```

3. **Configuration** (sanitized)
   - `vars.py` with sensitive data removed
   - Execution command used

4. **Steps to Reproduce**
   - Exact commands run
   - Expected vs. actual behavior

---

## Next Steps

**You're now ready to use Project APE effectively!**

1. **Configure your first client** - Edit `vars.py`
2. **Run a test workflow** - Fast mode, single client
3. **Review outputs** - Check quality score and outputs
4. **Scale up** - Add more clients, try deep mode
5. **Integrate into workflow** - Weekly/monthly account research

Return to: [README.md](../README.md) | See also: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Happy researching with Project APE! 🦍**
