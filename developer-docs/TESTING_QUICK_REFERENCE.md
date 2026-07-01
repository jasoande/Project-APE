# Testing Quick Reference

## Run Tests

```bash
# All tests (recommended)
./run-tests.sh

# Specific category
./run-tests.sh oauth
./run-tests.sh container
./run-tests.sh integration
./run-tests.sh security

# Fast parallel execution
./run-tests.sh --parallel

# Generate CI/CD report
./run-tests.sh --junit
```

## Test Categories

### OAuth (5 tests)
1. ✅ Fresh install (manual)
2. ✅ Re-run with existing credentials
3. ✅ Billing error handling (manual)
4. ✅ Expired token detection
5. ✅ Wrong client type detection

### Container (5 tests)
6. ✅ Image builds successfully
7. ✅ Container starts and stays healthy
8. ✅ Dashboard accessible on port 8765
9. ✅ No root processes running
10. ✅ File permissions correct

### Integration (3 tests)
11. ✅ setup.sh runs end-to-end (manual)
12. ✅ OAuth wizard completes (manual)
13. ✅ Google Drive access verified

### Security (4 tests)
14. ✅ No secrets in logs
15. ✅ File permissions are 600/700
16. ✅ Container runs as non-root user
17. ✅ No .env file mounts

## Output

```
✅ PASS - Test passed successfully
❌ FAIL - Test failed (see error message)
⏭️  SKIP - Test skipped (manual or not applicable)
```

## Backup Safety

Tests automatically backup and restore:
- OAuth credentials (`~/.project-ape/`)
- NotebookLM credentials (`~/.notebooklm/`)
- GCP config (`~/.config/gcloud/`)
- Container volumes
- Configuration files

Skip backup: `--no-backup` (use in CI/CD only)

## Troubleshooting

**Container tests fail:**
```bash
# Install/start Podman
podman --version
```

**Drive access fails:**
```bash
# Re-authenticate
python3 setup-oauth-drive.py
```

**Permission errors:**
```bash
chmod +x run-tests.sh
chmod 600 ~/.project-ape/drive_*.json
```

## CI/CD Integration

```yaml
# GitHub Actions
- name: Run Tests
  run: ./run-tests.sh --junit --no-backup

# GitLab CI
script:
  - ./run-tests.sh --junit --no-backup
artifacts:
  reports:
    junit: test-results-*.xml
```

## Expected Results

- **Total Tests:** 17
- **Automated:** 13 (76%)
- **Manual:** 4 (24%)
- **Pass Rate:** >95% for release
- **Execution Time:** 5-10 minutes (standard), 3-5 minutes (parallel)

## Manual Tests

Run these before each release:

1. **OAuth Fresh Install** - Delete `~/.project-ape`, run `setup-oauth-drive.py`
2. **setup.sh End-to-End** - Clean environment, run `./setup.sh`
3. **OAuth Wizard** - Test browser-based wizard at `http://localhost:8765/configure`

## Support

- Full documentation: `TEST_EXECUTION_GUIDE.md`
- Test scenarios: `OAUTH_TESTING.md`
- Development guide: `CLAUDE.md`
