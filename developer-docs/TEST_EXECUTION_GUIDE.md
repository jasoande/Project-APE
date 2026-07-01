# Project APE - Test Execution Guide

**Created:** 2026-06-30  
**Script:** `run-tests.sh`  
**Coverage:** 17 automated test scenarios across 4 categories

---

## Quick Start

```bash
# Run all tests
./run-tests.sh

# Run specific category
./run-tests.sh oauth
./run-tests.sh container
./run-tests.sh integration
./run-tests.sh security

# Run with options
./run-tests.sh --parallel        # Parallel execution
./run-tests.sh --junit           # Generate JUnit XML
./run-tests.sh --no-backup       # Skip state backup
```

---

## Test Categories

### 1. OAuth Setup Tests (5 scenarios)

Tests the Google Drive OAuth authentication workflow.

**Test 1: Fresh Install**
- **Description:** Simulates first-time OAuth setup
- **Status:** Manual (requires browser interaction)
- **Coverage:** End-to-end OAuth credential creation and authentication

**Test 2: Re-run with Existing Credentials**
- **Description:** Validates behavior when credentials already exist
- **Automated:** Yes
- **Checks:**
  - Credentials file exists
  - Valid JSON format
  - Token file exists

**Test 3: Billing Error Scenario**
- **Description:** Handles GCP project creation without billing account
- **Status:** Manual (requires specific GCP account state)
- **Expected:** Graceful fallback to existing project

**Test 4: Expired Token**
- **Description:** Detects and handles expired OAuth tokens (7+ days)
- **Automated:** Yes
- **Checks:**
  - Token file age
  - Expiration detection

**Test 5: Wrong Client Type Detection**
- **Description:** Validates OAuth credentials are Desktop app (not Web app)
- **Automated:** Yes
- **Checks:**
  - Credentials contain "installed" key
  - Correct client type format

---

### 2. Container Tests (5 scenarios)

Tests containerized deployment and execution.

**Test 6: Image Builds Successfully**
- **Description:** Builds Project APE container from Containerfile
- **Automated:** Yes
- **Checks:**
  - Containerfile exists
  - Build completes without errors
  - Image appears in registry

**Test 7: Container Starts and Stays Healthy**
- **Description:** Verifies container lifecycle and stability
- **Automated:** Yes
- **Checks:**
  - Container starts successfully
  - Remains running for 5+ seconds
  - No crashes or exits

**Test 8: Dashboard Accessible**
- **Description:** Tests dashboard web server on port 8765
- **Automated:** Yes
- **Checks:**
  - Dashboard container starts
  - HTTP server responds on localhost:8765
  - No connection errors

**Test 9: No Root Processes Running**
- **Description:** Security check for rootless execution
- **Automated:** Yes
- **Checks:**
  - No processes running as UID 0 (root)
  - Container user is non-root

**Test 10: File Permissions Correct**
- **Description:** Validates container filesystem permissions
- **Automated:** Yes
- **Checks:**
  - /app directory is writable
  - /app/logs is writable
  - Correct ownership for container user

---

### 3. Integration Tests (3 scenarios)

Tests end-to-end workflows and component integration.

**Test 11: setup.sh Runs End-to-End**
- **Description:** Complete setup workflow from scratch
- **Status:** Manual (requires user interaction)
- **Coverage:**
  - Environment setup
  - NotebookLM authentication
  - OAuth configuration
  - Container credentials

**Test 12: OAuth Wizard Completes**
- **Description:** Browser-based OAuth setup wizard
- **Status:** Manual (requires browser)
- **Coverage:**
  - 5-step wizard completion
  - Credential upload
  - Browser authentication

**Test 13: Drive Access Verified**
- **Description:** Tests actual Google Drive API access
- **Automated:** Yes
- **Checks:**
  - OAuth token is valid
  - Drive API responds
  - Can list files
  - No authentication errors

---

### 4. Security Tests (4 scenarios)

Tests security best practices and vulnerability prevention.

**Test 14: No Secrets in Logs**
- **Description:** Scans log files for leaked credentials
- **Automated:** Yes
- **Patterns Checked:**
  - Google API keys (AIza...)
  - OAuth tokens (ya29...)
  - Private keys
  - Client secrets

**Test 15: File Permissions are 600/700**
- **Description:** Validates secure permissions on credential files
- **Automated:** Yes
- **Files Checked:**
  - `~/.project-ape/drive_credentials.json` (600)
  - `~/.project-ape/drive_token.json` (600)
  - `~/.notebooklm/` directory (700)

**Test 16: Container Non-Root User**
- **Description:** Verifies container doesn't run as root
- **Automated:** Yes
- **Checks:**
  - Default user is not root
  - Processes run as non-root UID

**Test 17: No .env Mounts**
- **Description:** Ensures no .env files exposed to containers
- **Automated:** Yes
- **Checks:**
  - Launch scripts don't mount .env
  - No environment file references

---

## Test Execution Modes

### Standard Mode (Sequential)

```bash
./run-tests.sh
```

- Tests run one after another
- Safest for state management
- Full cleanup between tests
- **Time:** ~5-10 minutes

### Parallel Mode

```bash
./run-tests.sh --parallel
```

- Safe tests run concurrently
- Container tests remain sequential (require cleanup)
- **Time:** ~3-5 minutes
- **Speedup:** ~40-50%

### Category-Specific

```bash
# OAuth tests only (~1 minute)
./run-tests.sh oauth

# Container tests only (~3-4 minutes)
./run-tests.sh container

# Integration tests (~1 minute)
./run-tests.sh integration

# Security tests (~30 seconds)
./run-tests.sh security
```

---

## State Management

### Automatic Backup

By default, the test suite backs up your current state before running:

**Backed Up:**
- `~/.project-ape/` (OAuth credentials)
- `~/.notebooklm/` (NotebookLM credentials)
- `~/.config/gcloud/` (GCP configuration)
- Podman volume `project-ape-credentials`
- `vars.py` configuration

**Backup Location:** `/tmp/project-ape-test-backup-[timestamp]`

### Restore on Failure

State is automatically restored if:
- Tests fail
- Script is interrupted (Ctrl+C)
- Any error occurs

### Skip Backup

```bash
./run-tests.sh --no-backup
```

Use when:
- Testing in isolated environment
- You have external backups
- Speed is critical

---

## Output Formats

### Console Output (Default)

Color-coded results with detailed error messages:

```
✅ PASS - OAuth credentials file is valid JSON
❌ FAIL - Container build
   Error: Build failed - see /tmp/build-test.log
⏭️  SKIP - OAuth Fresh Install
   Reason: Requires browser interaction
```

### JUnit XML

```bash
./run-tests.sh --junit
```

Generates: `test-results-[timestamp].xml`

Compatible with:
- Jenkins
- GitHub Actions
- GitLab CI
- CircleCI
- TeamCity

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Project APE

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman

      - name: Run Tests
        run: ./run-tests.sh --junit --no-backup

      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results-*.xml
```

### GitLab CI

```yaml
test:
  stage: test
  image: quay.io/podman/stable
  script:
    - ./run-tests.sh --junit --no-backup
  artifacts:
    reports:
      junit: test-results-*.xml
```

---

## Troubleshooting

### Test Failures

**Container build fails:**
```bash
# Check build log
cat /tmp/build-test.log

# Verify Podman is installed
podman --version

# Check Containerfile exists
ls -la developer-docs/Containerfile.debian
```

**Drive access test fails:**
```bash
# Check OAuth token exists
ls -la ~/.project-ape/drive_token.json

# Verify token is valid
python3 -c "
from google.oauth2.credentials import Credentials
creds = Credentials.from_authorized_user_file('~/.project-ape/drive_token.json')
print('Token valid:', creds.valid)
"

# Re-run OAuth setup
python3 setup-oauth-drive.py
```

**Permission errors:**
```bash
# Fix credential permissions
chmod 600 ~/.project-ape/drive_*.json
chmod 700 ~/.notebooklm

# Fix script permissions
chmod +x run-tests.sh
```

### State Restoration Issues

If automatic restore fails:

```bash
# List backups
ls -la /tmp/project-ape-test-backup-*

# Manual restore (replace [timestamp])
BACKUP=/tmp/project-ape-test-backup-[timestamp]

# Restore OAuth
rm -rf ~/.project-ape
cp -r $BACKUP/.project-ape ~/

# Restore NotebookLM
rm -rf ~/.notebooklm
cp -r $BACKUP/.notebooklm ~/

# Restore gcloud
rm -rf ~/.config/gcloud
cp -r $BACKUP/.config-gcloud ~/.config/gcloud

# Restore vars.py
cp $BACKUP/vars.py ./
```

---

## Test Coverage Metrics

### Current Coverage

| Category | Tests | Automated | Manual |
|----------|-------|-----------|--------|
| OAuth | 5 | 3 (60%) | 2 (40%) |
| Container | 5 | 5 (100%) | 0 (0%) |
| Integration | 3 | 1 (33%) | 2 (67%) |
| Security | 4 | 4 (100%) | 0 (0%) |
| **Total** | **17** | **13 (76%)** | **4 (24%)** |

### Target Goals

- **Pass Rate:** > 95%
- **Execution Time:** < 10 minutes (standard mode)
- **Failed Tests:** 0 for release
- **Automation Rate:** > 75% ✅ (currently 76%)

---

## Adding New Tests

### Test Template

```bash
test_my_new_feature() {
    start_test "My New Feature Description"

    # Setup
    # ...

    # Check conditions
    if [ condition ]; then
        log_skip "My Feature" "Reason for skipping"
        return
    fi

    # Execute test
    RESULT=$(command_to_test)

    # Validate
    if [ "$RESULT" = "expected" ]; then
        log_pass "Feature works correctly"
    else
        log_fail "Feature test" "Expected 'expected', got '$RESULT'"
    fi

    # Cleanup
    # ...
}
```

### Add to Category

Edit `run-tests.sh`:

```bash
run_oauth_tests() {
    # ... existing tests ...
    test_my_new_feature
}
```

---

## Manual Test Procedures

For tests marked as "Manual", follow these procedures:

### OAuth Fresh Install (Test 1)

1. **Prepare clean state:**
   ```bash
   rm -rf ~/.project-ape
   gcloud auth revoke --all
   ```

2. **Run setup:**
   ```bash
   python3 setup-oauth-drive.py
   ```

3. **Verify steps:**
   - [ ] gcloud authentication opens browser
   - [ ] GCP project created (or existing selected)
   - [ ] Drive API enabled
   - [ ] OAuth credentials created
   - [ ] Browser opens for consent
   - [ ] Token saved successfully

4. **Validate:**
   ```bash
   ls -la ~/.project-ape/drive_*.json
   python3 verify-drive-access.py
   ```

### setup.sh End-to-End (Test 11)

1. **Clean environment:**
   ```bash
   # Backup current state
   mv ~/.project-ape ~/.project-ape.bak
   mv ~/.notebooklm ~/.notebooklm.bak
   ```

2. **Run setup:**
   ```bash
   ./setup.sh
   ```

3. **Verify all 9 steps complete:**
   - [ ] Environment setup
   - [ ] Virtual environment activated
   - [ ] NotebookLM login
   - [ ] Google Drive auth configured
   - [ ] Container credentials setup
   - [ ] Client configuration
   - [ ] Drive folder access verified
   - [ ] Setup marker created

4. **Validate:**
   ```bash
   ls -la ~/.ape_setup_complete
   cat ~/.ape_setup_complete | jq
   ```

### OAuth Wizard (Test 12)

1. **Start dashboard:**
   ```bash
   python3 dashboard/server.py
   ```

2. **Open browser:**
   ```
   http://localhost:8765/configure
   ```

3. **Complete wizard:**
   - [ ] Step 1: Status check
   - [ ] Step 2: Create credentials (GCP Console)
   - [ ] Step 3: Upload client_secret JSON
   - [ ] Step 4: Authenticate (browser opens)
   - [ ] Step 5: Verify access

4. **Validate:**
   - [ ] Green checkmarks in Step 1
   - [ ] Sample files displayed in Step 5
   - [ ] No JavaScript errors in console

---

## Performance Benchmarks

### Execution Times

**Standard Mode:**
- OAuth tests: 45-60 seconds
- Container tests: 180-240 seconds
- Integration tests: 30-45 seconds
- Security tests: 15-20 seconds
- **Total:** 270-365 seconds (4.5-6 minutes)

**Parallel Mode:**
- Parallel phase: 45-60 seconds
- Sequential phase: 180-240 seconds
- **Total:** 225-300 seconds (3.5-5 minutes)

**Category-Specific:**
- `oauth`: 45-60 seconds
- `container`: 180-240 seconds
- `integration`: 30-45 seconds
- `security`: 15-20 seconds

---

## Maintenance

### Weekly

- [ ] Run full test suite on development branch
- [ ] Review skipped tests - can they be automated?
- [ ] Check for new log patterns in secret detection

### Before Release

- [ ] Run full test suite: `./run-tests.sh --junit`
- [ ] Run manual tests (Tests 1, 11, 12)
- [ ] Verify all automated tests pass
- [ ] Review and update test documentation

### Quarterly

- [ ] Review test coverage metrics
- [ ] Add tests for new features
- [ ] Update security patterns
- [ ] Optimize parallel execution

---

## Support and Debugging

### Verbose Output

```bash
# Add debugging to test script
bash -x ./run-tests.sh
```

### Check Specific Test

Edit `run-tests.sh` and comment out other tests:

```bash
run_oauth_tests() {
    # test_oauth_fresh_install
    test_oauth_rerun_existing  # Only run this one
    # test_oauth_billing_error
    # test_oauth_expired_token
    # test_oauth_wrong_client_type
}
```

### Preserve Test State

```bash
# Run without automatic restore
./run-tests.sh --no-backup

# Inspect state after failure
ls -la ~/.project-ape/
podman ps -a
podman logs <container-id>
```

---

## FAQ

**Q: Can I run tests without destroying my current setup?**  
A: Yes, tests automatically backup and restore your state. Use `--no-backup` only if you're in a test environment.

**Q: Why are some tests skipped?**  
A: Tests requiring browser interaction or specific account states are marked as manual. Run these following the Manual Test Procedures section.

**Q: How do I run just one test?**  
A: Edit `run-tests.sh` and comment out the tests you don't want to run.

**Q: Can I run tests in CI/CD?**  
A: Yes, use `--junit --no-backup` flags. See CI/CD Integration section.

**Q: What if container tests fail?**  
A: Ensure Podman is installed and running. Check `/tmp/build-test.log` for build errors.

**Q: How do I interpret the summary?**  
A: Pass rate should be 100% for release. Failed tests show detailed error messages. Skipped tests are expected for manual scenarios.

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-30  
**Maintainer:** Project APE Team  
**License:** Internal Use
