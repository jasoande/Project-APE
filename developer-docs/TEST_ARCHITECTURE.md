# Project APE - Test Architecture

## Test Suite Structure

```
run-tests.sh
├── OAuth Tests (5)
│   ├── Fresh Install (manual)
│   ├── Re-run Existing ✓
│   ├── Billing Error (manual)
│   ├── Expired Token ✓
│   └── Wrong Client Type ✓
│
├── Container Tests (5)
│   ├── Image Build ✓
│   ├── Health Check ✓
│   ├── Dashboard Access ✓
│   ├── No Root Processes ✓
│   └── File Permissions ✓
│
├── Integration Tests (3)
│   ├── setup.sh E2E (manual)
│   ├── OAuth Wizard (manual)
│   └── Drive Access ✓
│
└── Security Tests (4)
    ├── No Secrets in Logs ✓
    ├── Credential Permissions ✓
    ├── Non-Root User ✓
    └── No .env Mounts ✓

Legend: ✓ = Automated, (manual) = Requires user interaction
```

## Test Execution Flow

### Standard Mode (Sequential)

```
┌─────────────────┐
│  Start Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backup State   │  ← Saves current credentials, config, volumes
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  OAuth Tests                                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ T1   │→ │ T2   │→ │ T3   │→ │ T4   │ → T5  │
│  └──────┘  └──────┘  └──────┘  └──────┘       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  Container Tests                                │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ T6   │→ │ T7   │→ │ T8   │→ │ T9   │ → T10 │
│  └──────┘  └──────┘  └──────┘  └──────┘       │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────┐
│  Integration Tests              │
│  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ T11  │→ │ T12  │→ │ T13  │  │
│  └──────┘  └──────┘  └──────┘  │
└─────────────────────┬───────────┘
                      │
                      ▼
┌───────────────────────────────────────┐
│  Security Tests                       │
│  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ T14  │→ │ T15  │→ │ T16  │ → T17 │
│  └──────┘  └──────┘  └──────┘       │
└─────────────────────┬─────────────────┘
                      │
                      ▼
┌─────────────────┐
│ Generate Report │  ← Summary, JUnit XML (optional)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Restore State   │  ← Returns to original state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Exit (0/1)     │  ← 0 = all pass, 1 = failures
└─────────────────┘
```

### Parallel Mode

```
┌─────────────────┐
│  Start Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backup State   │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Parallel Phase (Independent Tests)       │
│                                            │
│  ┌──────────────┐  ┌──────────────┐       │
│  │  OAuth T2-T5 │  │ Security T14 │       │
│  │              │  │    T15, T17  │       │
│  └──────────────┘  └──────────────┘       │
│                                            │
│  ┌──────────────┐                         │
│  │ Integration  │                         │
│  │     T13      │                         │
│  └──────────────┘                         │
│                                            │
│  All run simultaneously ↓                 │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│  Sequential Phase (Require Cleanup)       │
│                                            │
│  Container Tests (T6-T10)                 │
│  Each test cleans up before next          │
│  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │ T6   │→ │ T7   │→ │ T8   │ → T9 → T10 │
│  └──────┘  └──────┘  └──────┘            │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌─────────────────┐
│ Generate Report │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Restore State   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Exit (0/1)     │
└─────────────────┘

Time Savings: ~40-50% reduction
```

## State Management

### Backup Process

```
┌──────────────────────────────────┐
│  Detect Existing State           │
├──────────────────────────────────┤
│  • ~/.project-ape/               │
│  • ~/.notebooklm/                │
│  • ~/.config/gcloud/             │
│  • Podman volumes                │
│  • vars.py                       │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Copy to Backup Directory        │
│  /tmp/project-ape-test-backup-*  │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Set Trap for Cleanup            │
│  (EXIT, ERR, INT signals)        │
└──────────────────────────────────┘
```

### Restore Process

```
┌──────────────────────────────────┐
│  Trigger: Test failure, Ctrl+C,  │
│          normal completion       │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Remove Modified State           │
│  rm -rf ~/.project-ape, etc.     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Copy from Backup Directory      │
│  Restore exact original state    │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Verify Restoration              │
│  Check files exist               │
└──────────────────────────────────┘
```

## Test Categories in Detail

### 1. OAuth Tests

**Purpose:** Validate Google Drive OAuth authentication  
**Dependencies:** Python, google-auth-oauthlib, Google Cloud SDK  
**State Impact:** Modifies `~/.project-ape/`  

```
Test Flow:
1. Fresh Install → Creates new credentials (manual)
2. Re-run Existing → Validates existing setup ✓
3. Billing Error → Handles GCP billing issues (manual)
4. Expired Token → Detects old tokens ✓
5. Wrong Client Type → Validates credential format ✓

Pass Criteria:
- Credentials file exists and is valid JSON
- Token file exists (if previously authenticated)
- Client type is "installed" (Desktop app)
- File permissions are 600
```

### 2. Container Tests

**Purpose:** Verify containerized deployment  
**Dependencies:** Podman, Containerfile  
**State Impact:** Creates temporary containers and images  

```
Test Flow:
1. Image Build → podman build ✓
2. Health Check → Container stays running ✓
3. Dashboard → HTTP server responds ✓
4. No Root → ps aux shows non-root ✓
5. Permissions → File system is writable ✓

Pass Criteria:
- Image builds without errors
- Container runs for 5+ seconds
- Dashboard responds on port 8765
- No processes as UID 0
- /app and /app/logs are writable

Cleanup:
- podman rm -f <container>
- podman rmi project-ape-test (optional)
```

### 3. Integration Tests

**Purpose:** End-to-end workflow validation  
**Dependencies:** All components  
**State Impact:** Full system state  

```
Test Flow:
1. setup.sh E2E → Complete setup (manual)
2. OAuth Wizard → Browser-based setup (manual)
3. Drive Access → API call ✓

Pass Criteria:
- setup.sh completes all 9 steps
- OAuth wizard creates valid credentials
- Drive API lists files successfully
- No authentication errors
```

### 4. Security Tests

**Purpose:** Prevent credential leaks and vulnerabilities  
**Dependencies:** Log files, credential files  
**State Impact:** Read-only  

```
Test Flow:
1. Secrets in Logs → grep for patterns ✓
2. File Permissions → stat credentials ✓
3. Non-Root User → whoami in container ✓
4. No .env Mounts → grep launch scripts ✓

Pass Criteria:
- No API keys, tokens, or secrets in logs
- Credential files are mode 600
- Directories are mode 700
- Container user is not root
- No .env file references

Patterns Checked:
- Google API keys: AIza[0-9A-Za-z-_]{35}
- OAuth tokens: ya29\.[0-9A-Za-z-_]+
- Private keys: -----BEGIN PRIVATE KEY-----
- Client secrets: "client_secret"
```

## Output Formats

### Console Output

```
========================================================================
PROJECT APE - AUTOMATED TEST SUITE
========================================================================

Configuration:
  Test Category: all
  Parallel Mode: false
  JUnit Output:  false
  Backup State:  Yes

========================================================================
▶ OAuth Setup Tests (5 scenarios)
------------------------------------------------------------------------

TEST 1: OAuth Fresh Install
⏭️  SKIP - OAuth Fresh Install
   Reason: Requires browser interaction

TEST 2: OAuth Re-run with Existing Credentials
ℹ drive_credentials.json is valid JSON
✅ PASS - OAuth credentials file is valid JSON
✅ PASS - OAuth token file exists

[... more tests ...]

========================================================================
TEST SUMMARY
========================================================================

Total Tests:   17
Passed:        13
Failed:        0
Skipped:       4

Pass Rate:     76.5%
```

### JUnit XML Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Project APE Test Suite" tests="17" failures="0" skipped="4">
  <testsuite name="ProjectAPE" tests="17" failures="0" skipped="4">
    <testcase name="OAuth Fresh Install">
      <skipped message="Requires browser interaction" />
    </testcase>
    <testcase name="OAuth Re-run with Existing Credentials" />
    <testcase name="Container Image Build" />
    <!-- ... more test cases ... -->
  </testsuite>
</testsuites>
```

## CI/CD Integration Points

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
./run-tests.sh security --no-backup
```

### GitHub Actions Workflow

```yaml
on:
  push:
    branches: [main, dev, qa]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman
      - name: Run Tests
        run: ./run-tests.sh --junit --no-backup
      - name: Publish Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results-*.xml
```

### GitLab CI Pipeline

```yaml
stages:
  - test

test:security:
  stage: test
  image: quay.io/podman/stable
  script:
    - ./run-tests.sh security --junit --no-backup
  artifacts:
    reports:
      junit: test-results-*.xml

test:full:
  stage: test
  image: quay.io/podman/stable
  script:
    - ./run-tests.sh --junit --no-backup
  artifacts:
    reports:
      junit: test-results-*.xml
  only:
    - main
    - production
```

## Failure Scenarios and Recovery

### Test Failure Recovery

```
Failure Detected
       │
       ▼
┌──────────────────┐
│ Log Error        │ → Capture error message
└────────┬─────────┘   Add to TEST_RESULTS[]
         │
         ▼
┌──────────────────┐
│ Cleanup          │ → Remove test containers
└────────┬─────────┘   Delete temporary files
         │
         ▼
┌──────────────────┐
│ Continue/Abort?  │ → set -e → abort
└────────┬─────────┘   (can be changed)
         │
         ▼
┌──────────────────┐
│ Restore State    │ → Run on EXIT trap
└────────┬─────────┘   Guaranteed to execute
         │
         ▼
┌──────────────────┐
│ Exit with 1      │ → CI/CD detects failure
└──────────────────┘
```

### Interrupted Execution

```
User presses Ctrl+C
       │
       ▼
┌──────────────────┐
│ INT Signal       │ → Trap catches
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Stop Current     │ → Kill running container
│ Test             │   Abort API calls
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Run EXIT Trap    │ → Restore state
└────────┬─────────┘   Cleanup backup
         │
         ▼
┌──────────────────┐
│ Exit             │ → Safe exit
└──────────────────┘
```

## Performance Optimization

### Parallel Execution Strategy

```
Safe to Parallelize (no state conflicts):
├── OAuth T2 (reads credentials)
├── OAuth T4 (reads token file)
├── OAuth T5 (reads credentials)
├── Security T14 (reads logs)
├── Security T15 (reads credentials)
├── Security T17 (reads scripts)
└── Integration T13 (Drive API call)

Must Run Sequentially:
├── Container T6-T10 (share podman state)
└── OAuth T1, T3, T11, T12 (manual)
```

### Resource Usage

```
Memory:
- Base: ~100 MB (script)
- Container tests: +2-4 GB (Podman)
- Parallel mode: +500 MB (simultaneous tests)

Disk:
- Backup: ~50-200 MB (credentials, config)
- Container images: ~1-2 GB
- Logs: ~10-50 MB

Network:
- Drive API test: ~1 KB
- Container pulls: 0 (uses local image)
```

## Maintenance Schedule

### Daily (CI/CD)
- Run security tests on every commit
- Run full suite on main/production branches

### Weekly (Developer)
- Run full suite locally before release
- Review skipped tests

### Monthly (Team)
- Review test coverage
- Update security patterns
- Add tests for new features

### Quarterly (Architect)
- Performance optimization
- Parallel execution improvements
- Test architecture review

---

**Last Updated:** 2026-06-30  
**Version:** 1.0.0  
**Maintainer:** Project APE Team
