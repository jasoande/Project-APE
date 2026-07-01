# Project APE - Quick Reference Guide

## Common Commands

### First Time Setup
```bash
# Setup credentials (one time)
./setup-credentials.sh

# Run first pipeline
./launch_ape.sh fast merck_test
```

### Daily Operations

#### Run Pipeline
```bash
# Single client, fast mode
./launch_ape.sh fast merck_test

# All clients, fast mode
./launch_ape.sh fast

# Deep research mode
./launch_ape.sh deep merck_test

# Force fresh download from Drive
./launch_ape.sh fast --refresh merck_test
```

#### Update Existing Notebooks
```bash
# Update one client (recommended when files change)
./update-sources.sh fast merck_test

# Update multiple clients
./update-sources.sh fast merck_test blue_yonder_test

# Update all clients
./update-sources.sh fast --all

# Update with research re-run
./update-sources.sh fast merck_test --research
```

## When To Use What

| Scenario | Command | Why |
|----------|---------|-----|
| First run for a client | `./launch_ape.sh fast CLIENT` | Creates new notebook |
| Added files to Drive | `./update-sources.sh fast CLIENT` | Only adds new files (fast) |
| Cache seems stale | `./launch_ape.sh fast --refresh CLIENT` | Forces fresh download |
| Want latest web research | `./update-sources.sh fast CLIENT --research` | Updates sources + research |
| Running all clients | `./launch_ape.sh fast` | Batch processing |

## File Locations

```
/Users/jasona/test/Project-APE-dev/
├── launch_ape.sh          # Main launcher
├── update-sources.sh      # Update existing notebooks
├── setup-credentials.sh   # One-time credential setup
├── vars.py               # Client configuration
├── .env                  # Service account config
├── logs/                 # Execution logs
│   └── CLIENT.log        # Per-client logs
├── core/
│   ├── update_manager.py # Incremental update logic
│   ├── drive_manager.py  # Google Drive integration
│   └── client_pipeline.py # Main pipeline
└── .multi_process_status/ # Dashboard status files
```

## Troubleshooting

### Authentication Errors
```bash
# Re-setup credentials
./setup-credentials.sh

# Or manually login
source ./activate-ape-env.sh
notebooklm login
```

### Drive Permission Errors
```bash
# Check service account file permissions
ls -la service-account-key.json
# Should be: -rw-r--r-- (644)

# Fix if needed
chmod 644 service-account-key.json
```

### Container Issues
```bash
# Stop all containers
podman stop $(podman ps -aq)
podman rm $(podman ps -aq)

# Clean up system
podman system prune -f
```

### Cache Issues
```bash
# Force refresh to bypass cache
./launch_ape.sh fast --refresh CLIENT

# Or clear cache manually
rm -rf ~/.project-ape/drive_cache/
```

## Log Analysis

### Check Last Run
```bash
# View full log
tail -100 logs/merck_test.log

# Check for errors
grep ERROR logs/merck_test.log

# Check completion
grep "completed successfully" logs/merck_test.log

# Check quality score
grep "Quality Score" logs/merck_test.log
```

### Common Log Messages

| Message | Meaning |
|---------|---------|
| `🔄 Force refresh enabled` | Using --refresh flag |
| `✅ Using cached Drive files` | Cache is valid and used |
| `New files detected: N` | Found N new files to add |
| `No new files to add` | All files already in notebook |
| `✅ Pipeline completed successfully!` | Run finished OK |
| `Quality Score: 8.0/10` | Final quality rating |

## Configuration

### Add New Client
Edit `vars.py`:
```python
clients = [
    "existing_client",
    "new_client_test"  # Add here
]

# Configure new client
new_client_test_name = "New Client"
new_client_test_folder = "https://drive.google.com/drive/folders/FOLDER_ID"
new_client_test_industry = "industry name"
new_client_test_subsegments = "segment1, segment2"
```

### Change Drive Cache TTL
Edit `vars.py`:
```python
DRIVE_CONFIG = {
    'cache_enabled': True,
    'cache_ttl_hours': 24,  # Change this (default: 24)
    # ...
}
```

## Dashboard

Access at: `http://localhost:8765`

Shows:
- Real-time progress per client
- Current step
- Quality scores
- Links to logs
- Notebook IDs

## Quick Checks

### Verify Setup
```bash
# Check credentials volume exists
podman volume ls | grep project-ape-credentials

# Check service account file
ls -la service-account-key.json

# Check vars.py
head -20 vars.py
```

### Test Single Client
```bash
# Quick test run
./launch_ape.sh fast merck_test

# Should see:
# - Download from Drive
# - Add files to notebook
# - Run research
# - Generate notes
# - Create mind map
# - Quality score
```

## Performance Tips

1. **Use update mode for changes**
   ```bash
   ./update-sources.sh fast CLIENT  # Faster than full run
   ```

2. **Skip refresh when possible**
   ```bash
   ./launch_ape.sh fast CLIENT  # Uses cache (faster)
   # vs
   ./launch_ape.sh fast --refresh CLIENT  # Fresh download (slower)
   ```

3. **Run clients in parallel**
   ```bash
   ./launch_ape.sh fast  # All clients run in parallel
   ```

## Support Files

- `PHASE1_CHANGES.md` - Force refresh implementation
- `PHASE2_CHANGES.md` - Update system implementation  
- `PDF_CONSOLIDATION_REMOVAL.md` - Optimization details
- `FINAL_SUMMARY.md` - Complete overview
- `QUICK_REFERENCE.md` - This file

## Version Info

- **Version:** 3.2.1
- **Python:** 3.13/3.14
- **Container:** RHEL UBI 9
- **Features:** Phase 1 ✅ | Phase 2 ✅ | Optimization ✅
