# Developer Scripts Reference

**Testing, development, and troubleshooting scripts**

These scripts are used for development, testing, and debugging Project APE. They are **not required** for normal operation.

---

## Testing Scripts

### test-logo.sh
**Purpose:** Test King Kong logo display on all dashboard pages

**Usage:**
```bash
./test-logo.sh
```

**What it tests:**
- Logo appears on dashboard.html
- Logo appears on configure.html  
- Logo appears on launch.html
- Logo size is correct (150x150px)
- Logo file exists in static/

**Output:** Pass/fail for each page

---

### test-logs-feature.sh
**Purpose:** Test real-time log streaming functionality

**Usage:**
```bash
./test-logs-feature.sh
```

**What it tests:**
- Logs tab exists on dashboard
- Log viewer component present
- SSE endpoint responds
- Log controls (pause, clear, download)
- Auto-scroll behavior

---

### test-phase3.sh
**Purpose:** Integration test for complete workflow

**Usage:**
```bash
./test-phase3.sh
```

**What it tests:**
- Setup script execution
- Environment activation
- Container launch
- Dashboard accessibility
- Client process spawning
- Status file creation
- Log file generation

**Note:** This is a comprehensive test that runs the full pipeline with test data.

---

### validate_pipeline.sh
**Purpose:** Validate pipeline results after execution

**Usage:**
```bash
./validate_pipeline.sh
```

**What it validates:**
- All clients completed successfully
- Quality scores meet minimum threshold (8.5)
- NotebookLM notebooks created
- Log files contain no errors
- Status files accurate
- Output files present

**When to use:** After running a production workflow to verify results

---

## Development Scripts

### ape-run.sh
**Purpose:** Simple runner for pre-built registry images (legacy)

**Usage:**
```bash
./ape-run.sh fast
```

**Note:** This is the old runner script before `launch_ape.sh` was created. Kept for reference but superseded by `launch_ape.sh`.

**Differences from launch_ape.sh:**
- No architecture detection
- No automatic image pulling
- No credential volume mounting
- Simpler, less robust

**Use case:** Quick testing of registry images without full setup

---

### update-sources.sh
**Purpose:** Update existing NotebookLM notebooks with new Drive files

**Usage:**
```bash
# Update all clients
./update-sources.sh fast

# Update specific client
./update-sources.sh fast acme_corp

# Update and re-run research
./update-sources.sh fast acme_corp --research
```

**What it does:**
1. Downloads new files from Google Drive
2. Compares with existing sources in NotebookLM
3. Uploads only new/changed files
4. Optionally re-runs research prompts

**Use case:** When client adds new documents to Drive folder and you want to update existing notebook instead of creating new one

---

### reset-setup.sh
**Purpose:** Reset first-run setup state

**Usage:**
```bash
./reset-setup.sh
```

**What it does:**
- Removes `~/.ape_setup_complete` marker file
- Allows `setup.sh` to run again
- Does NOT remove credentials or configurations

**Use case:** 
- Testing setup script
- Troubleshooting setup issues
- Setting up on a different machine

---

### podman-install.sh
**Purpose:** Automated Podman installation (legacy)

**Usage:**
```bash
./podman-install.sh
```

**What it does:**
- Installs Podman on macOS or Linux
- Initializes Podman machine (macOS only)
- Starts Podman machine

**Note:** This functionality is now integrated into `setup-environment.sh`. Kept for manual Podman installation if needed.

---

## Utility Scripts

### share-drive-folders.py
**Purpose:** Programmatically share Drive folders with service account

**Usage:**
```bash
python3 share-drive-folders.py
```

**What it does:**
1. Reads vars.py for client folder URLs
2. Extracts folder IDs
3. Shares each folder with service account email
4. Sets "Viewer" role

**Requirements:**
- OAuth credentials with Drive write permissions
- Service account email

**Use case:** Batch sharing when setting up service account authentication for multiple clients

**Note:** Most users prefer manual sharing via Drive web UI. This is for automation/scripting.

---

## Script Categories

### Essential Scripts (in project root)
These are required for normal operation:

| Script | Purpose | Required |
|--------|---------|----------|
| `setup.sh` | First-time setup | Yes |
| `setup-environment.sh` | Install dependencies | Yes |
| `setup-credentials.sh` | Configure container auth | Yes |
| `setup-oauth-drive.py` | OAuth setup | Yes (or service account) |
| `create-service-account.sh` | Service account setup | Alternative to OAuth |
| `verify-drive-access.py` | Test authentication | Recommended |
| `launch_ape.sh` | Launch workflow | Yes |
| `launch-project-ape.command` | macOS launcher | Yes (macOS) |
| `main.py` | Main orchestrator | Yes |
| `workflow_detector.py` | Detect workflow config | Yes |
| `activate-ape-env.sh` | Activate venv | Yes |
| `example-vars.py` | Config template | Reference |
| `vars.py` | User configuration | Yes (created by user) |

### Development/Testing Scripts (in developer-docs/)
Optional - for development and troubleshooting:

| Script | Purpose | Optional |
|--------|---------|----------|
| `test-logo.sh` | Test logo display | Yes |
| `test-logs-feature.sh` | Test log streaming | Yes |
| `test-phase3.sh` | Integration test | Yes |
| `validate_pipeline.sh` | Validate results | Yes |
| `update-sources.sh` | Update notebooks | Yes |
| `reset-setup.sh` | Reset setup state | Yes |
| `ape-run.sh` | Legacy runner | Yes |
| `podman-install.sh` | Manual Podman install | Yes |
| `share-drive-folders.py` | Batch sharing | Yes |

---

## Running Tests

### Quick Test Suite
```bash
cd /Users/jasona/test/Project-APE-dev/developer-docs

# Test logo display
./test-logo.sh

# Test log streaming
./test-logs-feature.sh
```

### Full Integration Test
```bash
cd /Users/jasona/test/Project-APE-dev/developer-docs

# Run complete workflow test
./test-phase3.sh
```

### Validate Production Run
```bash
cd /Users/jasona/test/Project-APE-dev/developer-docs

# After running real workflow
./validate_pipeline.sh
```

---

## Development Workflow

### Typical Developer Flow

1. **Make changes** to code

2. **Test locally:**
   ```bash
   # Run without container
   source ~/.project-ape-venv/bin/activate
   python3 main.py --mode fast --clients test_client
   ```

3. **Run integration test:**
   ```bash
   ./developer-docs/test-phase3.sh
   ```

4. **Validate results:**
   ```bash
   ./developer-docs/validate_pipeline.sh
   ```

5. **Reset if needed:**
   ```bash
   ./developer-docs/reset-setup.sh
   ```

---

## Troubleshooting Scripts

### Reset Everything
```bash
# Reset setup state
./developer-docs/reset-setup.sh

# Re-run setup
./setup.sh
```

### Test Specific Component
```bash
# Test Drive access
python3 verify-drive-access.py

# Test logo display
./developer-docs/test-logo.sh

# Test logs
./developer-docs/test-logs-feature.sh
```

### Update Existing Notebook
```bash
# Instead of creating new notebook, update existing
./developer-docs/update-sources.sh fast client_name
```

---

## Script Maintenance

### Adding New Test Scripts

1. Create script in `developer-docs/`
2. Follow naming convention: `test-{feature}.sh`
3. Include header comment explaining purpose
4. Add to this documentation

### Deprecating Scripts

1. Mark as deprecated in this doc
2. Add comment in script header
3. Keep for 1-2 releases
4. Then remove

### Current Deprecated Scripts
- `ape-run.sh` - Use `launch_ape.sh` instead
- `podman-install.sh` - Integrated into `setup-environment.sh`

---

## Contributing

When adding new developer scripts:

1. **Name clearly**: `test-{feature}.sh` or `validate-{component}.sh`
2. **Add header**: Purpose, usage, requirements
3. **Make executable**: `chmod +x script.sh`
4. **Document here**: Add section with usage examples
5. **Add to .gitignore if needed**: Especially if it creates test artifacts

---

## Questions?

- See main documentation: `../README.md`
- Check troubleshooting: `../Docs/TROUBLESHOOTING.md`
- Open GitHub issue for script bugs

---

**Last Updated:** June 25, 2026  
**Maintainer:** Project APE Developers
