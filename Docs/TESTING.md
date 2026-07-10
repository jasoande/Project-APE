# Project-APE Testing Guide

## Overview

Project-APE includes a comprehensive automated test suite covering security, core business logic, configuration management, and error handling. The test suite uses `pytest` with coverage reporting.

## Quick Start

```bash
# Run all tests with coverage
./run-tests.sh

# Run quick unit tests only (no coverage)
./run-tests.sh --quick --no-cov

# Run security tests only
./run-tests.sh --security

# Run specific test file
./run-tests.sh tests/test_retry_strategy.py -v
```

## Test Categories

### Core Business Logic Tests

**File:** `tests/test_retry_strategy.py` (23 tests)
- Tests exponential backoff retry logic
- Validates retryable vs non-retryable error detection
- Coverage: 100%

**File:** `tests/test_checkpoint_manager.py` (10 tests)
- Tests crash recovery checkpoint system
- Validates phase skip logic
- Coverage: 88%

**File:** `tests/test_health_checks.py` (14 tests)
- Tests pre-flight validation checks
- NotebookLM CLI availability, authentication, Drive OAuth
- Coverage: 76%

**File:** `tests/test_notification_manager.py` (5 tests)
- Tests webhook notification system
- Slack payload formatting
- Coverage: 87%

### Configuration Management Tests

**File:** `tests/test_config_generator.py` (30 tests)
- Tests web UI configuration generation
- Client ID sanitization, validation
- vars.py generation

**File:** `tests/test_config_parser.py` (14 tests)
- Tests configuration file parsing
- Setting extraction and validation
- Coverage: 85%

### Security Tests

**File:** `tests/test_flask_secret_persistence.py` (2 tests)
- **NEW:** Tests Flask secret key persistence across restarts
- Validates file permissions (0o600)
- Prevents CSRF token invalidation

**File:** `tests/test_credential_permissions.py` (4 tests)
- **NEW:** Tests OAuth token file permissions
- Validates chmod(0o600) calls in code
- Prevents credential leakage to other users

**File:** `tests/test_csrf_protection.py` (23 tests)
- Tests CSRF token validation on POST endpoints
- Validates token generation and acceptance

**File:** `tests/test_server_security.py` (Multiple tests)
- Tests path traversal prevention
- Error message sanitization
- Input validation

### Integration Tests

**File:** `tests/test_client_pipeline.py` (12 tests)
- Tests prompt variable substitution
- Status update JSON format
- Pipeline phase tracking

## Test Execution Options

### Basic Usage

```bash
# All tests with coverage (default)
./run-tests.sh

# Verbose output
./run-tests.sh -v

# No coverage (faster)
./run-tests.sh --no-cov
```

### Targeted Testing

```bash
# Quick smoke test (core modules only)
./run-tests.sh --quick

# Security audit
./run-tests.sh --security

# Specific module
./run-tests.sh tests/test_retry_strategy.py

# Multiple modules
./run-tests.sh tests/test_retry_strategy.py tests/test_health_checks.py
```

### Coverage Reports

When running with coverage (default), two reports are generated:

1. **Terminal output:** Shows missing lines per file
2. **HTML report:** `htmlcov/index.html` (detailed, interactive)

View HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Current Coverage Stats

| Module | Coverage | Notes |
|--------|----------|-------|
| `core/retry_strategy.py` | 100% | ✅ Fully tested |
| `core/checkpoint_manager.py` | 88% | ✅ High coverage |
| `core/notification_manager.py` | 87% | ✅ High coverage |
| `dashboard/config_parser.py` | 85% | ✅ High coverage |
| `core/health_checks.py` | 76% | ⚠️ Some edge cases untested |
| `dashboard/config_generator.py` | 50% | ⚠️ Needs more tests |
| Overall (core + dashboard) | ~11% | ⚠️ Many modules untested |

**Note:** Low overall coverage is due to untested modules (drive_manager, client_pipeline, etc.). Core tested modules have excellent coverage (76-100%).

## Writing New Tests

### Test File Structure

```python
#!/usr/bin/env python3
"""
Brief description of what this test file covers.
"""

import pytest
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.your_module import YourClass

class TestYourFeature:
    """Group related tests together in classes."""

    def test_basic_functionality(self):
        """Test description."""
        # Arrange
        obj = YourClass()

        # Act
        result = obj.do_something()

        # Assert
        assert result == expected_value

    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            YourClass().do_invalid_thing()
```

### Test Naming Conventions

- Test files: `test_*.py` (e.g., `test_retry_strategy.py`)
- Test classes: `Test*` (e.g., `TestRetryStrategy`)
- Test functions: `test_*` (e.g., `test_success_on_first_attempt`)

### Using Fixtures

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('clients = ["test_client"]')
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()

def test_config_parsing(temp_config_file):
    """Use the fixture in a test."""
    result = parse_config(temp_config_file)
    assert result['clients'] == ["test_client"]
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock_subprocess():
    """Mock subprocess calls."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout='success')

        result = your_function_that_calls_subprocess()

        assert result == 'success'
        mock_run.assert_called_once()
```

## Continuous Integration

### GitHub Actions (Future)

Create `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: ./run-tests.sh --no-cov
```

### Pre-commit Hook (Optional)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
./run-tests.sh --quick --no-cov
if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

Make executable: `chmod +x .git/hooks/pre-commit`

## Troubleshooting

### "ModuleNotFoundError: No module named 'pytest'"

**Solution:** Virtual environment not activated or dependencies not installed.

```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "ImportError: attempted relative import with no known parent package"

**Solution:** Run tests via pytest, not directly.

```bash
# Wrong:
python tests/test_retry_strategy.py

# Correct:
pytest tests/test_retry_strategy.py
# OR
./run-tests.sh tests/test_retry_strategy.py
```

### "Permission denied" when running run-tests.sh

**Solution:** Make script executable.

```bash
chmod +x run-tests.sh
```

### Coverage report shows "Couldn't parse Python file"

**Solution:** Syntax error in source file or coverage limitation.

- Check file syntax: `python -m py_compile path/to/file.py`
- This warning doesn't affect test results, only coverage reporting

## Test Maintenance

### Running Tests Before Commits

Always run tests before committing security-critical changes:

```bash
# Before committing changes to auth, credentials, or security:
./run-tests.sh --security

# Before committing core business logic:
./run-tests.sh --quick

# Before major releases:
./run-tests.sh  # Full suite with coverage
```

### Adding Tests for New Features

1. Create test file: `tests/test_new_feature.py`
2. Write tests covering happy path and error cases
3. Run tests: `./run-tests.sh tests/test_new_feature.py -v`
4. Verify coverage: Check `htmlcov/index.html`
5. Aim for >80% coverage on new code

### Updating Tests for Bug Fixes

When fixing a bug:

1. Write a test that reproduces the bug (should fail)
2. Fix the bug
3. Verify test now passes
4. Commit both fix and test together

Example:
```python
def test_bug_123_csrf_token_invalidation():
    """Regression test for GitHub issue #123."""
    # This test failed before the fix
    secret_key = _get_or_create_secret_key()
    # Simulate server restart
    secret_key_2 = _get_or_create_secret_key()
    # Should be the same (was different before fix)
    assert secret_key == secret_key_2
```

## Security Test Checklist

When adding security features, add tests for:

- ✅ Authentication required
- ✅ Input validation (length, format, special chars)
- ✅ Path traversal prevention
- ✅ File permissions (0o600 for secrets)
- ✅ Error message sanitization (no stack traces to user)
- ✅ CSRF token validation
- ✅ Rate limiting (if applicable)
- ✅ SQL injection prevention (if applicable)
- ✅ XSS prevention (if applicable)

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## Test Results Summary

Last test run: 2026-07-10

```
79 tests passed in 0.19s
Coverage: 11% overall (core tested modules: 76-100%)
```

**Status:** ✅ All critical modules tested, security tests passing
