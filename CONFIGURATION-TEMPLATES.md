# Project APE - Configuration Templates

**Project APE uses container-based execution exclusively.** All configuration templates are designed for containerized deployment.

---

## Two Templates, Two Use Cases

### 📄 example-container.py - Single Client

**Use this when:** Processing one client at a time

```bash
# 1. Copy template
cp example-container.py vars.py

# 2. Edit configuration
nano vars.py  # Update client name, industry, subsegments

# 3. Add client data
mkdir -p client_data/YourClient
cp /path/to/documents/* client_data/YourClient/

# 4. Run
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

**Configuration example:**
```python
persona = "Red Hat solutions architect"

clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_subsegments = "cloud infrastructure, SaaS, cybersecurity"
acme_corp_folder = "/app/client_data/ACME_Corp"
```

---

### 📄 example-multi-client-vars.py - Multiple Clients

**Use this when:** Processing multiple clients in parallel

```bash
# 1. Copy template
cp example-multi-client-vars.py vars.py

# 2. Edit configuration (add all clients)
nano vars.py

# 3. Add client data for each
mkdir -p client_data/{Client1,Client2,Client3}
cp /path/to/client1/* client_data/Client1/
cp /path/to/client2/* client_data/Client2/
cp /path/to/client3/* client_data/Client3/

# 4. Run all clients in parallel
./ape-run.sh --vars ./vars.py --mode fast

# Or run specific clients only
./ape-run.sh --vars ./vars.py --clients client1 client3 --mode fast
```

**Configuration example:**
```python
persona = "Red Hat solutions architect"

clients = ["acme_corp", "globex_inc", "initech_llc"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_subsegments = "cloud infrastructure, SaaS"
acme_corp_folder = "/app/client_data/ACME_Corp"

globex_inc_name = "Globex Inc"
globex_inc_industry = "manufacturing"
globex_inc_subsegments = "robotics, automation, IoT"
globex_inc_folder = "/app/client_data/Globex_Inc"

initech_llc_name = "Initech LLC"
initech_llc_industry = "financial services"
initech_llc_subsegments = "banking, payments, fintech"
initech_llc_folder = "/app/client_data/Initech_LLC"
```

---

## Quick Decision Guide

**Choose your template:**

| I need to... | Use this template | Clients | Runtime |
|--------------|------------------|---------|---------|
| Process one account | `example-container.py` | 1 | ~10-12 min |
| Process multiple accounts | `example-multi-client-vars.py` | 2-6 | ~10-12 min (parallel) |
| Test with one account first | `example-container.py` | 1 | ~10-12 min |
| Batch process my territory | `example-multi-client-vars.py` | Many | Efficient |

---

## Configuration Fields

### Required for Each Client

```python
# Client ID (lowercase, underscores)
clients = ["client_id"]

# Client Details
client_id_name = "Full Company Name"              # Display name
client_id_industry = "technology"                 # Industry category
client_id_subsegments = "cloud, SaaS, security"   # Specific segments (comma-separated)
client_id_folder = "/app/client_data/ClientName"  # Container path to documents
```

### Global Settings (Usually Unchanged)

```python
persona = "Red Hat solutions architect"  # AI perspective/role
default_mode = "fast"                     # Default execution mode
DASHBOARD_PORT = 8765                     # Web dashboard port
```

### Industry Examples

Choose from common industries or create your own:

- `technology` - Software, cloud, SaaS
- `financial services` - Banking, insurance, fintech
- `healthcare` - Hospitals, pharma, medical devices
- `manufacturing` - Automotive, aerospace, industrial
- `retail` - E-commerce, consumer goods
- `energy` - Oil & gas, renewables, utilities
- `telecommunications` - Telco, ISPs, networking
- `pharmaceuticals` - Drug development, biotech

### Subsegment Examples

Be specific with comma-separated subsegments:

```python
# Good examples:
"cloud infrastructure, SaaS platforms, DevOps automation, cybersecurity"
"retail banking, investment banking, wealth management, digital payments"
"hospital networks, electronic health records, medical devices, telehealth"
"automotive manufacturing, supply chain automation, IoT sensors, robotics"
```

---

## Common Workflow

### 1. First-Time Setup
```bash
# Install everything
./setup-environment.sh

# Setup credentials
./setup-credentials.sh

# Pull container
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

### 2. Single Client Workflow
```bash
# Copy template
cp example-container.py vars.py

# Edit vars.py with client details
nano vars.py

# Create and populate client data
mkdir -p client_data/ClientName
cp /path/to/docs/* client_data/ClientName/

# Run
./ape-run.sh --vars ./vars.py --clients clientname --mode fast

# View results at http://localhost:8765
```

### 3. Multi-Client Workflow
```bash
# Copy template
cp example-multi-client-vars.py vars.py

# Edit vars.py with all client details
nano vars.py

# Create and populate all client directories
mkdir -p client_data/{Client1,Client2,Client3}
# ... add documents to each ...

# Run all in parallel
./ape-run.sh --vars ./vars.py --mode fast

# View progress at http://localhost:8765
```

---

## Tips

### ✅ Best Practices
- Start with `example-container.py` for first client
- Move to `example-multi-client-vars.py` for batch processing
- Use meaningful client IDs (lowercase, underscores)
- Keep vars.py in version control (no sensitive data)
- Organize client data: `client_data/Company_Name/`

### ⚠️ Common Mistakes
- Don't change paths (already configured for containers)
- Don't forget to create client_data directories
- Don't use special characters in client IDs
- Don't commit actual client data to git

---

## Need Help?

- **Quick Start:** See `README.md`
- **Installation:** See `INSTALLATION.md`
- **Troubleshooting:** See `Docs/TROUBLESHOOTING.md`
- **Dashboard:** http://localhost:8765 (while running)

---

**That's it!** Pick your template, configure your clients, and run. Project APE handles the rest.
