<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="150"/>
  
  # Frequently Asked Questions
  **Common Questions and Answers**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Getting Started](#getting-started)
3. [Usage Questions](#usage-questions)
4. [Quality and Outputs](#quality-and-outputs)
5. [Authentication](#authentication)
6. [Performance](#performance)
7. [Troubleshooting](#troubleshooting)
8. [Configuration](#configuration)
9. [Container and Deployment](#container-and-deployment)
10. [Security and Compliance](#security-and-compliance)
11. [Integration](#integration)
12. [Costs and Licensing](#costs-and-licensing)

---

## General Questions

### What is Account Intelligence?

**Account Intelligence (Account Planning Engine)** is an AI-powered automation platform that transforms enterprise account research from multi-day manual processes into 15-20 minute automated workflows. It uses Google's NotebookLM platform to automatically research companies, analyze industries, and generate comprehensive intelligence reports.

**Key capabilities:**
- Automatically imports 40-180 external sources per client
- Generates 8,000-15,000 word analysis reports
- Provides SWOT analysis, competitive intelligence, technology trends
- Quality validation with 1-10 scoring
- Zero terminal interface (GUI-driven)

---

### Who uses Account Intelligence?

**Primary users:**
- **Enterprise sales teams** - Account planning and prospect research
- **Solution architects** - Pre-sales technical discovery
- **Account managers** - Quarterly business review preparation
- **Strategic consultants** - Client research and competitive analysis
- **Presales engineers** - Technical positioning and fit assessment

**Organization types:**
- Technology vendors (SaaS, cloud, enterprise software)
- Consulting firms (strategy, technology, business)
- Financial services (investment research, M&A due diligence)

---

### What makes Account Intelligence different from manual research?

| Manual Research | Account Intelligence |
|-----------------|-------------|
| 16-24 hours per account | 15-20 minutes (Fast mode) |
| 10-20 sources reviewed | 40-180 sources automatically imported |
| Inconsistent quality | AI-validated quality scores (1-10) |
| No audit trail | Full source citations and logging |
| Human bias | AI-powered objective analysis |
| Not scalable | Process 3-5 accounts in parallel |

---

## Getting Started

### How long does setup take?

**First-time setup: 5-7 minutes total**

- **Step 1 - Installation:** 1 minute (clone repo, auto-setup on first launch)
- **Step 2 - NotebookLM Auth:** 60 seconds (OAuth consent flow)
- **Step 3 - Drive OAuth:** 90 seconds (upload credentials.json, generate token)
- **Step 4 - First Client:** 2 minutes (fill web form)

After initial setup, adding new clients takes ~2 minutes via web UI.

---

### What accounts do I need?

**Required:**
1. **Google account** with NotebookLM access (free at notebooklm.google.com)
2. **Google Cloud project** with Drive API enabled (free tier available)

**Optional:**
3. **Gemini API key** for quality scoring (free tier: 15 requests/minute)

**Important:** You need TWO Google authentications:
- NotebookLM OAuth (for AI research)
- Drive OAuth (for document downloads)

---

### Do I need to know how to code?

**No.** Account Intelligence is designed for zero-terminal operation.

**What you DO:**
- Double-click launcher file
- Fill out web forms
- Click "Launch Workflow" button
- Download generated reports

**What you DON'T need:**
- Terminal/command line knowledge
- Python programming
- Container/Docker expertise
- Configuration file editing

---

### Can I use it on Windows/Mac/Linux?

**Yes, all platforms supported:**

| Platform | Status | Launcher |
|----------|--------|----------|
| **macOS** 10.15+ | ✅ Fully supported | Double-click `launch-project-ape.command` |
| **Windows** 10/11 | ✅ Fully supported | Double-click `launch-project-ape.py` |
| **Linux** Ubuntu 20.04+ | ✅ Fully supported | Double-click `launch-project-ape.py` or `.desktop` file |

**Requirements:**
- Python 3.10+ (installer prompts if missing)
- Chrome or Firefox browser (Safari not supported for OAuth)
- 2 GB RAM minimum, 4 GB recommended

---

## Usage Questions

### How long does a workflow take?

**Fast Mode (Recommended for first run):**
- Duration: 15-20 minutes
- External sources: 40-80 automatically imported
- Quality target: 8.0+
- Best for: Quick turnaround, initial research, time-sensitive

**Deep Mode (Comprehensive analysis):**
- Duration: 45-60 minutes
- External sources: 90-180 automatically imported
- Quality target: 8.5+
- Best for: Final deliverables, critical deals, thorough analysis

**Recommendation:** Start with Fast mode. If quality score < 8.0, re-run in Deep mode.

---

### How many clients can I process simultaneously?

**Parallel execution limits:**
- **Fast Mode:** 3-5 clients simultaneously (20 min total)
- **Deep Mode:** 1-2 clients simultaneously (60 min total)
- **Maximum:** 5 parallel clients (system-enforced limit)

**Why limited?**
- API quota management (NotebookLM rate limits)
- Resource constraints (memory, CPU)
- Quality maintenance (too many parallel = higher retry rate)

**Best practice:** Process 3 clients in Fast mode for optimal throughput vs quality.

---

### What file formats are supported?

**Supported input formats:**
- ✅ **PDFs** (preferred, best quality) - text-searchable only
- ✅ **Google Docs** (auto-converted to PDF)
- ✅ **Google Sheets** (auto-converted to PDF)
- ✅ **Microsoft Word** (.docx, upload to Drive first)

**NOT supported:**
- ❌ Images (JPEG, PNG) - no text extraction
- ❌ Scanned PDFs without OCR - run through OCR first
- ❌ Videos or audio files
- ❌ Compressed archives (ZIP, RAR)
- ❌ Email files (.eml, .msg)

**Recommendation:** 5-15 substantive PDFs per client (annual reports, 10-Ks, white papers, case studies, earnings transcripts).

---

### Can I use local files or do I need Google Drive?

**Both supported:**

**Google Drive (Recommended for v4.0+):**
- Paste Drive folder URL in web UI
- Automatic downloads with 7-day caching
- No manual file management
- Works from any machine

**Local Files (Legacy support):**
- Upload PDFs to `client_data/{client_name}/` folder
- Specify local path in `vars.py`
- Requires filesystem access
- Useful for air-gapped environments

**90% of users use Drive URLs** - it's simpler and more flexible.

---

## Quality and Outputs

### What is a quality score?

**Quality Score = 1.0 to 10.0 rating** generated by AI (Gemini) that evaluates completeness and depth of analysis.

**Scoring dimensions (6 total):**
1. Industry analysis completeness
2. SWOT analysis depth
3. Technology trends coverage
4. Competitive positioning accuracy
5. Pain points identification
6. Strategic recommendations quality

**Interpreting scores:**
- **9.0-10.0:** Exceptional - Comprehensive, executive-ready
- **8.0-8.9:** Strong - High quality, minor gaps
- **7.0-7.9:** Good - Solid foundation, some areas need depth
- **6.0-6.9:** Acceptable - Usable but needs supplementation
- **< 6.0:** Weak - Re-run in Deep mode or add more source documents

**Note:** Requires `GEMINI_API_KEY` environment variable (optional feature).

---

### How can I improve quality scores?

**1. Add more substantive documents (5-20 PDFs ideal):**
- Annual reports, 10-Ks, investor presentations
- Industry white papers and case studies
- Competitive analysis reports
- Earnings call transcripts

**2. Use Deep Mode instead of Fast:**
- 90-180 sources vs 40-80
- Deeper AI reasoning
- More comprehensive research

**3. Specify accurate industry and subsegments:**
- "pharmaceuticals" > "healthcare" (too broad)
- "drug discovery, clinical trials, manufacturing" (targeted subsegments)

**4. Provide better source quality:**
- Avoid marketing brochures (low information density)
- Include recent documents (last 2 years)
- Ensure PDFs are text-searchable (not scanned images)

**5. Re-run workflow:**
- First run sometimes lower quality (AI warming up)
- Second run typically improves by 0.5-1.0 points

---

### What outputs do I get?

**Generated files in `docs_generated/{client_id}/`:**

**1. Main Analysis Report (`{Client_Name}_Analysis.txt`):**
- 8,000-15,000 words (25-40 pages formatted)
- Executive summary
- Industry analysis with trends and disruptions
- SWOT analysis
- Competitive landscape
- Technology trends
- Strategic insights and recommendations
- 80+ source citations

**2. NotebookLM Link (`NotebookLM_Link.txt`):**
- Direct URL to interactive NotebookLM notebook
- Ask follow-up questions
- Explore all imported sources
- Generate additional content

**3. Quality Report (`Quality_Score.json`):**
```json
{
  "client_name": "Acme Corporation",
  "overall_score": 8.5,
  "completeness": { ... },
  "sources": {
    "pdf_uploads": 8,
    "external_imports": 80,
    "total": 88
  },
  "execution_time": "18m 43s",
  "mode": "fast"
}
```

**Format:** Plain text (import to Word/Google Docs for formatting)

---

## Authentication

### Why do I need to authenticate twice?

**Two separate Google services, two separate OAuth flows:**

**1. NotebookLM OAuth:**
- **Purpose:** Create notebooks, add sources, generate AI content
- **Scopes:** `notebooklm`, `notebooklm.readonly`
- **Credential file:** `~/.notebooklm/credentials.json`
- **Expiry:** Refresh token long-lived (revocable by user)

**2. Google Drive OAuth:**
- **Purpose:** Download PDFs from Drive folders
- **Scopes:** `drive.readonly`, `drive.metadata.readonly`
- **Credential file:** `credentials/token_drive.json`
- **Expiry:** 90 days (requires re-authentication)

**They cannot be combined** because NotebookLM and Drive are separate Google APIs with different permission models.

---

### How long do OAuth tokens last?

**NotebookLM:**
- **Access token:** 1 hour (auto-refreshes)
- **Refresh token:** No expiry (until manually revoked)
- **Re-auth needed:** Only if user revokes access or changes Google password

**Google Drive:**
- **Access token:** 1 hour (auto-refreshes)
- **Refresh token:** 90 days
- **Re-auth needed:** Every 90 days or if revoked

**Best practice:** If you see "Token expired" errors, just re-run OAuth setup via web UI (60 seconds).

---

### Can I use service accounts instead of OAuth?

**Not recommended for v4.0.1** - OAuth 2.0 is the supported authentication method.

**Why OAuth is preferred:**
- User-delegated permissions (more secure)
- Easier to revoke access
- No service account key management
- Works with consumer Google accounts

**Service account limitations:**
- Requires Google Workspace (not personal accounts)
- Complex key file management
- Harder to troubleshoot
- NotebookLM doesn't officially support service accounts

**Future:** Service account support may be added for enterprise deployments.

---

## Performance

### Why is my workflow slow?

**Expected timing (baseline):**
- Fast mode: 15-20 minutes
- Deep mode: 45-60 minutes

**If significantly slower (30+ min for Fast), check:**

**1. Internet speed:**
- Minimum: 10 Mbps sustained
- Recommended: 50+ Mbps
- Test: `speedtest-cli` or fast.com

**2. API rate limiting:**
- NotebookLM quota: 60 requests/minute
- High retry rate in logs (>20% in Fast mode)
- Solution: Increase delays in `vars.py` TIMINGS

**3. Drive download bottleneck:**
- Large PDFs (>50 MB each)
- Many files (>20 PDFs)
- Solution: Reduce PDF count or split large files

**4. System resources:**
- Check CPU: `top` (should be <80% sustained)
- Check memory: `free -h` (should have 2+ GB available)
- Check disk I/O: `iostat`

**5. Parallel execution overload:**
- Running 5+ clients simultaneously
- Solution: Reduce to 3 clients max

---

### What's a normal retry rate?

**Acceptable retry rates:**
- **Fast mode:** 5-10% retries (aggressive timing)
- **Deep mode:** 20-30% retries (expected, acceptable)

**Retries happen due to:**
- API quota exceeded (wait and retry)
- Network transient errors (automatic retry)
- NotebookLM processing delays (normal)

**High retry rate (>40%) indicates:**
- Too many parallel clients (reduce to 2-3)
- Timing too aggressive (increase delays)
- Network instability (check connection)
- API outage (check Google status page)

**Check logs:**
```bash
grep "Retry" logs/clientname.log | wc -l
grep "SUCCESS" logs/clientname.log | wc -l
# Retry count / Success count = retry rate
```

---

### How can I make it faster?

**1. Use Fast Mode:**
- 15-20 min vs 45-60 min (Deep)
- 40-80 sources vs 90-180

**2. Reduce document count:**
- 5-10 PDFs (sweet spot for speed)
- Remove marketing brochures (low value)

**3. Use Drive caching:**
- 7-day cache avoids re-downloads
- First run: full download
- Subsequent runs (same folder): instant

**4. Tune timing (advanced):**
```python
# Edit vars.py - more aggressive timing
TIMINGS = {
    'ask_prompt_delay': (5.0, 8.0),   # Default: (8.0, 12.0)
    'chat_prompt_delay': (3.0, 5.0),  # Default: (5.0, 8.0)
}
```
**Warning:** Lower delays = higher retry rate.

**5. Parallel execution:**
- Run 3 clients simultaneously
- Total time: ~20 min for all 3 (vs 60 min sequential)

---

## Troubleshooting

### Dashboard won't open

**Symptom:** Browser shows "Connection refused" or "This site can't be reached"

**Quick fixes:**

**1. Check if dashboard running:**
```bash
# macOS/Linux
lsof -i :8765

# Windows
netstat -an | findstr :8765
```

**2. Restart dashboard:**
```bash
pkill -f "dashboard/server.py"
python3 launch-project-ape.py
```

**3. Check port availability:**
```bash
# If port 8765 in use, change in vars.py
DASHBOARD_PORT = 8766  # Use different port
```

**4. Check firewall:**
```bash
# macOS
sudo pfctl -sr | grep 8765

# Linux
sudo ufw status

# Windows
netsh advfirewall firewall show rule name=all | findstr 8765
```

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md#dashboard-issues) for detailed diagnosis.

---

### Authentication failed

**Symptom:** "NotebookLM authentication failed" or "Drive OAuth failed"

**Quick fixes:**

**1. Re-authenticate via web UI:**
- Navigate to http://localhost:8765/configure
- Click "Authenticate NotebookLM" or "Setup Drive OAuth"
- Follow prompts (use Chrome, not Safari)

**2. Check credential files exist:**
```bash
ls -la ~/.notebooklm/credentials.json
ls -la credentials/token_drive.json
```

**3. Verify permissions:**
```bash
chmod 600 ~/.notebooklm/credentials.json
chmod 600 credentials/token_drive.json
```

**4. Clear and re-auth:**
```bash
rm ~/.notebooklm/credentials.json
rm credentials/token_drive.json
# Then re-run OAuth setup via web UI
```

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md#authentication-issues)

---

### Workflow stuck or frozen

**Symptom:** Progress bar frozen, no log updates for 2+ minutes

**Quick diagnosis:**

**1. Check live logs in dashboard:**
- Look for specific error message
- Check last timestamp

**2. Verify Google Drive folder accessible:**
```bash
# Test Drive API
curl -H "Authorization: Bearer $(grep access_token credentials/token_drive.json | cut -d'"' -f4)" \
  "https://www.googleapis.com/drive/v3/files?q='YOUR_FOLDER_ID'+in+parents"
```

**3. Wait for normal delays:**
- Phase 3 (Research): 3-5 min normal processing time
- Phase 4 (Analysis): 8-12 min normal
- Some phases have intentional delays (API processing)

**4. If truly stuck (5+ min no movement):**
```bash
# Check process
ps aux | grep "client_pipeline.py"

# Kill and restart
pkill -f "client_pipeline.py"
# Re-launch workflow via dashboard
```

**See:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md#workflow-issues)

---

## Configuration

### What is vars.py?

**`vars.py` is the Python configuration file** that defines:
- Client list and attributes
- Global settings (persona, mode, timing)
- Retry configuration
- Dashboard port

**Two ways to create it:**
1. **Web UI (recommended):** Auto-generated from form input
2. **Manual editing:** Copy from template, edit in text editor

**Example structure:**
```python
# Client list
clients = ["acme_corp", "techco"]

# Client 1 configuration
acme_corp_name = "Acme Corporation"
acme_corp_folder = "https://drive.google.com/drive/folders/1A2B3C..."
acme_corp_industry = "pharmaceuticals"
acme_corp_subsegments = "drug discovery, clinical trials"

# Global settings
persona = "Red Hat solutions architect"
MODE = "fast"
DASHBOARD_PORT = 8765
```

---

### Can I edit vars.py while a workflow is running?

**No - changes won't take effect until next launch.**

**Workflow execution:**
1. Reads `vars.py` at startup
2. Loads configuration into memory
3. Runs with in-memory config (ignores file changes)

**To apply changes:**
1. Wait for current workflow to complete
2. Edit `vars.py` (via web UI or text editor)
3. Launch new workflow

**Exception:** You can add NEW clients to `vars.py` without affecting running workflows (they use separate processes).

---

### How do I run multiple clients?

**Via Web UI:**
1. Add Client 1 via form → Save
2. Add Client 2 via form → Save
3. Add Client 3 via form → Save
4. Click "Launch Workflow" → All 3 run in parallel

**Via vars.py:**
```python
clients = ["client1", "client2", "client3"]

client1_name = "Client One"
client1_folder = "https://drive.google.com/..."
# ... other attributes

client2_name = "Client Two"
client2_folder = "https://drive.google.com/..."
# ... other attributes

# etc.
```

**Via command line:**
```bash
./ape-run.sh --vars ./vars.py --clients client1,client2,client3 --mode fast
```

---

## Container and Deployment

### Podman vs Docker - which should I use?

**Recommendation: Podman (if available)**

**Podman advantages:**
- Rootless containers (more secure)
- No daemon (lighter weight)
- Better SELinux integration (RHEL/Fedora)
- Open source, Red Hat supported

**Docker advantages:**
- More widely known
- Slightly better Windows/Mac support
- Docker Desktop GUI

**Compatibility:**
- Commands are 99% identical (`podman run` ≈ `docker run`)
- Use `alias docker=podman` for seamless switching
- Both work with same container images

**When to use Docker:**
- Windows/Mac development (Docker Desktop)
- CI/CD pipelines already using Docker
- Team familiarity with Docker

**When to use Podman:**
- Linux production servers
- Rootless security requirement
- RHEL/Fedora environments

---

### Can I deploy to Kubernetes?

**Yes, full Kubernetes support.**

**Requirements:**
- Kubernetes 1.24+
- Persistent volumes (ReadWriteMany for multi-replica)
- Secrets for OAuth tokens
- ConfigMap for vars.py

**Quick deploy:**
```bash
# Create namespace
kubectl create namespace project-ape

# Create secrets
kubectl create secret generic notebooklm-credentials \
  --from-file=credentials.json=~/.notebooklm/credentials.json

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

**See:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#kubernetes-deployment) for complete YAML manifests.

---

### How do I scale horizontally?

**Current limitations (v4.0.1):**
- **Single dashboard instance recommended** (status files are file-based)
- **Shared filesystem required** for multi-replica (NFS, EFS, Azure Files)

**Scaling strategy:**
1. **Vertical scaling (easier):**
   - Increase CPU/memory for single instance
   - Run more parallel clients (3-5)

2. **Horizontal scaling (requires shared storage):**
   - Deploy multiple replicas
   - Mount shared NFS/EFS for logs and outputs
   - Use load balancer with session affinity

**Future enhancement (roadmap):**
- PostgreSQL for status tracking (instead of JSON files)
- Redis for caching
- Stateless dashboard (easy horizontal scaling)

---

## Security and Compliance

### Is my data secure?

**Yes, multiple security layers:**

**1. Authentication:**
- OAuth 2.0 (industry standard)
- No embedded API keys
- MFA supported (Google account level)

**2. Network:**
- Dashboard localhost-only by default (127.0.0.1:8765)
- All external APIs use HTTPS/TLS 1.2+
- Certificate validation enforced

**3. Data at rest:**
- OAuth tokens stored with 0600 permissions
- OS-level filesystem encryption (FileVault, BitLocker, LUKS)
- No sensitive data in logs (auto-redaction)

**4. Container isolation:**
- Non-root user (UID 1000)
- Read-only mounts for config/data
- Capabilities dropped

**5. Data in transit:**
- TLS 1.2+ for all API calls
- No plaintext credential transmission

**See:** [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for comprehensive security architecture.

---

### Can I use it in regulated industries?

**Yes, with proper configuration:**

**GDPR Compliance:**
- Right to erasure: Delete client data (`rm -rf docs_generated/client_id/`)
- Data minimization: Only download necessary PDFs
- Audit trail: Full logging of API calls and data access

**SOC 2 / ISO 27001:**
- Access controls: OAuth 2.0, MFA
- Encryption: TLS 1.2+ in transit
- Logging: Security event audit logs
- Secrets management: Integration with Vault, AWS Secrets Manager

**HIPAA (with care):**
- **Warning:** NotebookLM is NOT a HIPAA BAA-covered service
- Do NOT upload PHI/PII documents
- Use only publicly available company information
- Sanitize documents before upload

**Financial Services (FINRA, etc.):**
- Audit logging enabled
- Data retention policies configurable
- OAuth token rotation procedures

**See:** [SECURITY_GUIDE.md](SECURITY_GUIDE.md#compliance)

---

## Integration

### Can I integrate with Salesforce?

**Yes (custom integration required):**

**Example workflow:**
1. Trigger Account Intelligence workflow from Salesforce Opportunity
2. Upload analysis to Opportunity notes
3. Update custom field with quality score

**Sample code:**
```python
from simple_salesforce import Salesforce

def upload_to_salesforce(client_id, opportunity_id):
    # Read generated analysis
    with open(f'docs_generated/{client_id}/Analysis.txt') as f:
        analysis = f.read()
    
    # Read quality score
    with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
        quality = json.load(f)
    
    # Upload to Salesforce
    sf = Salesforce(username='...', password='...', security_token='...')
    sf.Opportunity.update(opportunity_id, {
        'Project_APE_Analysis__c': analysis,
        'Quality_Score__c': quality['overall_score']
    })
```

**See:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md#crm-integrations) for more examples.

---

### Can I export to PowerPoint?

**Not directly, but easy workaround:**

**Option 1: Manual copy-paste**
1. Open `docs_generated/{client}/Analysis.txt`
2. Copy sections
3. Paste into PowerPoint slides

**Option 2: Markdown conversion (future)**
- Generate Markdown format
- Use Pandoc: `pandoc analysis.md -o slides.pptx`

**Option 3: Custom script**
```python
from pptx import Presentation

def create_ppt_from_analysis(client_id):
    prs = Presentation()
    
    # Read analysis
    with open(f'docs_generated/{client_id}/Analysis.txt') as f:
        analysis = f.read()
    
    # Add slides for each section
    for section in analysis.split('\n\n'):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = section.split('\n')[0]
        slide.placeholders[1].text = '\n'.join(section.split('\n')[1:])
    
    prs.save(f'{client_id}_Analysis.pptx')
```

---

## Costs and Licensing

### Is Account Intelligence free?

**Account Intelligence itself: Yes, MIT License (free and open source)**

**API usage costs (Google):**
- **NotebookLM API:** Free (as of July 2026)
- **Google Drive API:** Free (within quota: 1000 requests/100 sec)
- **Gemini API (optional):** Free tier 15 requests/min, paid plans available

**Typical monthly costs for 100 clients/month:**
- NotebookLM: $0 (free)
- Drive API: $0 (within quota)
- Gemini API: $0 (free tier sufficient)
- **Total: $0/month**

**Paid tier needed only if:**
- Processing 500+ clients/month (exceed free quotas)
- Require higher Gemini rate limits

---

### Can I use it commercially?

**Yes, MIT License allows commercial use.**

**Permissions:**
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Conditions:**
- Include original license and copyright notice
- No warranty provided (AS-IS)

**You can:**
- Sell services using Account Intelligence
- Include in commercial products
- Customize for internal use
- Deploy for clients

**You cannot:**
- Hold authors liable
- Use Account Intelligence trademark without permission

**See:** [LICENSE](../LICENSE) file for full terms.

---

<div align="center">
  
  **More questions?**
  
  See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | [USER_GUIDE.md](USER_GUIDE.md) | [Report Issues](https://github.com/jasoande/Project-APE-dev/issues)
  
  ---
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
