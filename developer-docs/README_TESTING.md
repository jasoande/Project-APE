# Project APE - Automated Testing

**Complete test suite for validating OAuth setup, container deployment, integrations, and security.**

---

## Quick Start

```bash
# Run all tests (recommended first time)
./run-tests.sh

# View results
# ✅ PASS - Test passed
# ❌ FAIL - Test failed (see error)
# ⏭️  SKIP - Test skipped (manual test)
```

**Expected output:**
- Total Tests: 17
- Automated: 13 (76%)
- Manual: 4 (24%)
- Execution Time: 5-10 minutes

---

## What's Tested

### ✅ OAuth Authentication (5 tests)
- Fresh installation workflow
- Re-running with existing credentials
- Billing error handling
- Expired token detection
- Client type validation

### ✅ Container Deployment (5 tests)
- Image builds successfully
- Container starts and stays healthy
- Dashboard web server accessible
- No root processes (security)
- File permissions correct

### ✅ Integration Workflows (3 tests)
- setup.sh end-to-end execution
- OAuth wizard browser flow
- Google Drive API access verification

### ✅ Security Validation (4 tests)
- No secrets leaked in logs
- Credential files have 600/700 permissions
- Container runs as non-root user
- No .env file mounts

---

## Common Commands

```bash
# Development
./run-tests.sh oauth              # Test OAuth only
./run-tests.sh security           # Quick security check
./run-tests.sh --parallel         # Faster execution

# CI/CD
./run-tests.sh --junit --no-backup

# Before release
./run-tests.sh --junit
# Then run manual tests (see guide)
```

---

## Safety Features

**Automatic State Backup:**
- Your current credentials are backed up before tests
- Podman volumes are exported
- Configuration files are saved

**Automatic Restore:**
- State is restored after tests complete
- State is restored if tests fail
- State is restored if you press Ctrl+C

**No Data Loss:**
- All tests are designed to be non-destructive
- Backup is enabled by default
- Manual override: `--no-backup` (CI/CD only)

---

## Test Results

### Pass/Fail Output

```
✅ PASS - OAuth credentials file is valid JSON
✅ PASS - Container image built successfully
❌ FAIL - Dashboard accessibility
   Error: Cannot reach dashboard on port 8765
⏭️  SKIP - OAuth Fresh Install
   Reason: Requires browser interaction

Summary:
Total Tests:   17
Passed:        15
Failed:        1
Skipped:       1
Pass Rate:     93.8%
```

---

## Documentation

| File | Purpose |
|------|---------|
| `README_TESTING.md` | This file - quick start |
| `TESTING_QUICK_REFERENCE.md` | Command cheat sheet |
| `TEST_EXECUTION_GUIDE.md` | Complete testing guide |
| `TEST_ARCHITECTURE.md` | Technical architecture |
| `TESTING_SUMMARY.md` | Project summary |

**Start here:** `TESTING_QUICK_REFERENCE.md` (1-page reference)  
**Full details:** `TEST_EXECUTION_GUIDE.md` (comprehensive guide)

---

## Manual Tests

Some tests require browser interaction and must be run manually:

### 1. OAuth Fresh Install
```bash
mv ~/.project-ape ~/.project-ape.bak
python3 setup-oauth-drive.py
# Follow browser prompts
```

### 2. setup.sh End-to-End
```bash
./setup.sh
# Complete all 9 setup steps
```

### 3. OAuth Wizard
```bash
python3 dashboard/server.py &
open http://localhost:8765/configure
# Complete 5-step wizard
```

**See:** `TEST_EXECUTION_GUIDE.md` section "Manual Test Procedures"

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run Tests
  run: ./run-tests.sh --junit --no-backup

- name: Publish Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: test-results-*.xml
```

### GitLab CI

```yaml
test:
  script:
    - ./run-tests.sh --junit --no-backup
  artifacts:
    reports:
      junit: test-results-*.xml
```

**See:** `TEST_EXECUTION_GUIDE.md` section "CI/CD Integration"

---

## Troubleshooting

### "Permission denied"
```bash
chmod +x run-tests.sh
```

### "Podman command not found"
```bash
# macOS
brew install podman
podman machine init && podman machine start

# Linux
sudo apt-get install podman  # or dnf install podman
```

### "Container build fails"
```bash
cat /tmp/build-test.log  # Review errors
```

### "Drive access fails"
```bash
python3 setup-oauth-drive.py  # Re-authenticate
```

**See:** `TEST_EXECUTION_GUIDE.md` section "Troubleshooting"

---

## Test Categories

Run specific test categories for faster iteration:

```bash
./run-tests.sh oauth        # ~1 minute
./run-tests.sh container    # ~3-4 minutes
./run-tests.sh integration  # ~1 minute
./run-tests.sh security     # ~30 seconds
```

---

## Performance

| Mode | Time | Use Case |
|------|------|----------|
| Standard | 5-10 min | First run, release validation |
| Parallel | 3-5 min | Development iteration |
| Category | 30s-4min | Focused testing |
| Security | 15-20s | Pre-commit check |

---

## Coverage

```
OAuth:        5 tests (60% automated)
Container:    5 tests (100% automated)
Integration:  3 tests (33% automated)
Security:     4 tests (100% automated)

Total:        17 tests (76% automated)
```

**Target:** >75% automation ✅ Achieved

---

## Options

```bash
--parallel       # Run tests concurrently (faster)
--junit          # Generate JUnit XML for CI/CD
--no-backup      # Skip state backup (CI/CD only)
-h, --help       # Show usage information
```

---

## Before Release Checklist

- [ ] Run full test suite: `./run-tests.sh --junit`
- [ ] All automated tests pass (13/13)
- [ ] Run manual test 1: OAuth fresh install
- [ ] Run manual test 11: setup.sh end-to-end
- [ ] Run manual test 12: OAuth wizard
- [ ] Review test output for warnings
- [ ] Verify pass rate is 100%
- [ ] Update CHANGELOG with test results

---

## Support

**Quick help:**
```bash
./run-tests.sh --help
```

**Documentation:**
- Quick reference: `TESTING_QUICK_REFERENCE.md`
- Full guide: `TEST_EXECUTION_GUIDE.md`
- Architecture: `TEST_ARCHITECTURE.md`

**Common issues:**
- All documented in "Troubleshooting" sections
- Check error messages (they're detailed)
- Review backup directory if state corrupted

---

## Files

```
run-tests.sh                    # Main test script ⭐
README_TESTING.md               # This file
TESTING_QUICK_REFERENCE.md      # One-page cheat sheet
TEST_EXECUTION_GUIDE.md         # Complete guide
TEST_ARCHITECTURE.md            # Technical details
TESTING_SUMMARY.md              # Project summary
test-results-*.xml              # Generated by --junit
```

---

## Example Session

```bash
$ ./run-tests.sh

========================================================================
PROJECT APE - AUTOMATED TEST SUITE
========================================================================

Configuration:
  Test Category: all
  Parallel Mode: false
  JUnit Output:  false
  Backup State:  Yes

▶ Creating backup of current state
ℹ Backed up: ~/.project-ape
ℹ Backed up: ~/.notebooklm
ℹ Backup created at: /tmp/project-ape-test-backup-1719763200

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

$ echo $?
0
```

---

**Ready to test:** `./run-tests.sh`

**Questions?** See `TEST_EXECUTION_GUIDE.md`

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-30  
**Status:** ✅ Production Ready
