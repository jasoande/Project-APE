<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence" width="150"/>

  # Testing Guide

  **Account Intelligence - Account Planning Engine**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Test Structure](#test-structure)
- [Test Files Reference](#test-files-reference)
- [Shared Fixtures](#shared-fixtures)
- [Writing New Tests](#writing-new-tests)

---

## Running Tests

### Full Test Suite

```bash
pytest tests/ -v
```

### Single Test File

```bash
pytest tests/test_retry_strategy.py -v
```

### Single Test Class or Method

```bash
pytest tests/test_retry_strategy.py::TestCalculateDelay -v
pytest tests/test_retry_strategy.py::TestCalculateDelay::test_exponential_growth -v
```

### With Output Displayed

```bash
pytest tests/ -v -s
```

---

## Test Coverage

### Generate Coverage Report

```bash
pytest --cov=core --cov=dashboard --cov-report=term-missing tests/
```

### HTML Coverage Report

```bash
pytest --cov=core --cov=dashboard --cov-report=html tests/
open htmlcov/index.html
```

### Dependencies

Test dependencies are listed in `requirements.txt`:

- `pytest>=8.0.0`
- `pytest-cov>=5.0.0`
- `pytest-mock>=3.12.0`

---

## Test Structure

```
tests/
  __init__.py
  conftest.py                    # Shared fixtures (see below)
  test_checkpoint_manager.py     # Pipeline checkpoint/resume
  test_client_pipeline.py        # Variable substitution, status updates
  test_config_generator.py       # Configuration generation and validation
  test_config_parser.py          # Configuration parsing and extraction
  test_health_checks.py          # Pre-flight validation checks
  test_notification_manager.py   # Webhook notification delivery
  test_retry_strategy.py         # Retry logic and exponential backoff
  test_server_security.py        # Path traversal prevention, API smoke tests
```

All test files follow the pattern `test_{module_name}.py` and use class-based organization with descriptive docstrings.

---

## Test Files Reference

### test_retry_strategy.py

Tests `core/retry_strategy.py` -- shared retry logic with exponential backoff.

| Class | Tests |
|-------|-------|
| `TestIsRetryableError` | Pattern matching for known retryable errors (rate limits, quota, RPC codes, auth failures). Parametrized with 12 retryable patterns. Verifies case insensitivity and custom pattern support. |
| `TestCalculateDelay` | Exponential backoff calculation. Verifies base delay on first attempt, exponential growth factor, and max delay capping. |
| `TestExecuteWithRetry` | Retry orchestration. Tests success on first attempt, recovery after transient failures, immediate stop on non-retryable errors, exhaustion after max attempts, and on_retry callback invocation. |

### test_checkpoint_manager.py

Tests `core/checkpoint_manager.py` -- pipeline checkpoint/resume capability.

| Class | Tests |
|-------|-------|
| `TestSaveAndLoad` | Save/load round-trip fidelity (all fields preserved), timestamp update on save, None return when no checkpoint exists. |
| `TestShouldSkipPhase` | Phase-skip logic for completed and pending phases. |
| `TestClear` | Checkpoint file deletion and safe handling when no file exists. |
| `TestCorruptedCheckpoint` | Graceful handling of corrupted JSON, empty files, and missing required keys (all return None). |

### test_client_pipeline.py

Tests `core/client_pipeline.py` -- variable substitution and status update logic.

| Class | Tests |
|-------|-------|
| `TestVariableSubstitution` | Template variable replacement for `$name`, `$industry`, `$subsegments`, `$persona`. Tests individual substitution, fallback for None subsegments, all variables combined, and templates without variables. |
| `TestStatusUpdate` | JSON status file structure. Tests required fields (name, token, step, progress, status, mode), start_time preservation across updates, COMPLETE status with quality score, FAILED status with error message, and extra kwargs forwarding. |

### test_config_generator.py

Tests `dashboard/config_generator.py` -- configuration generation and validation.

| Class | Tests |
|-------|-------|
| `TestSanitizeClientId` | Client name to Python identifier conversion: spaces, hyphens, special chars, leading digits, length cap (64), lowercase. |
| `TestValidateClientData` | Single client validation: required fields, empty field rejection, empty industry/subsegments allowed, invalid ID format, invalid Drive URL, local folder paths. |
| `TestGenerateVarsPy` | Full vars.py generation: produces valid Python (compiles), contains client list and variables, rejects duplicates and invalid data, handles multiple clients. |
| `TestEscapePythonString` | Safe escaping of quotes and backslashes for Python code generation. |

### test_config_parser.py

Tests `dashboard/config_parser.py` -- configuration parsing and extraction.

| Class | Tests |
|-------|-------|
| `TestParseVarsFile` | Round-trip parsing of vars.py: clients list, client data fields, global settings, timing configurations. FileNotFoundError on missing file. |
| `TestExtractClientConfigs` | Client field extraction from loaded module. Handles empty client lists and missing clients attribute. |
| `TestExtractGlobalSettings` | Default values when settings are missing (persona, mode, port). |
| `TestValidateSettings` | Validation of mode values, port range, and empty persona. |

### test_health_checks.py

Tests `core/health_checks.py` -- pre-flight validation checks.

| Class | Tests |
|-------|-------|
| `TestCheckNotebookLMAvailable` | CLI detection: success, FileNotFoundError, nonzero return code. |
| `TestCheckNotebookLMAuth` | Authentication via AuthManager mock: authenticated and not-authenticated states. |
| `TestCheckDriveAuth` | Drive token validation: file exists with token key, file missing, token key missing. |
| `TestCheckConfigValid` | Configuration validation: valid config, missing file, config without clients list. |
| `TestRunPreflightChecks` | Aggregated runner: all pass, partial failure with correct failed check identification. |

### test_notification_manager.py

Tests `core/notification_manager.py` -- webhook notification delivery.

| Class | Tests |
|-------|-------|
| `TestSendWebhook` | HTTP POST delivery: success (200 status), failure (exception). |
| `TestFormatSlackPayload` | Slack Block Kit structure: produces dict with blocks, contains "Workflow Complete" header. |
| `TestNotifyCompletion` | Conditional delivery: sends when NOTIFICATION_WEBHOOK_URL is set, skips when not configured. |

### test_server_security.py

Tests `dashboard/server.py` -- security hardening.

| Class | Tests |
|-------|-------|
| `TestPathTraversal` | Path traversal attack prevention: valid tokens accepted, `../` traversal blocked, URL-encoded spaces blocked, `..%2f` encoded traversal blocked. |
| `TestAPIEndpoints` | Smoke tests: /health returns 200 with status field, /status returns JSON with total and clients, /api/config-status returns configured status, /api/generate-config rejects GET and empty POST. |

---

## Shared Fixtures

Defined in `tests/conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `tmp_vars_py` | function | Creates a temporary `vars.py` with complete configuration (clients, timings, retry config, Drive config, Gemini agent config, quality thresholds). Returns the file path. |
| `mock_subprocess` | function | Patches `subprocess.run` to prevent real process execution. Returns the mock object. |
| `flask_test_client` | function | Creates a Flask test client from `dashboard.server.app` with `TESTING=True` and `WTF_CSRF_ENABLED=False`. |
| `tmp_logs_dir` | function | Creates a temporary `logs/` directory. Returns the path. |
| `tmp_status_dir` | function | Creates a temporary `.multi_process_status/` directory. Returns the path. |

---

## Writing New Tests

### Guidelines

1. **File naming:** Create `tests/test_{module_name}.py` matching the module under test.

2. **Class organization:** Group related tests into classes with descriptive names (`TestFeatureName`). Add a docstring to each class explaining what aspect is being tested.

3. **Use existing fixtures:** Import shared fixtures from `conftest.py` rather than duplicating setup code. Add new shared fixtures to `conftest.py` when they apply to multiple test files.

4. **Mock external dependencies:** Use `pytest-mock` (the `mocker` fixture) to patch subprocess calls, file I/O, and external APIs. Never make real API calls in tests.

5. **Parametrize repetitive cases:** Use `@pytest.mark.parametrize` for testing multiple inputs against the same logic (see `test_retry_strategy.py` for an example).

6. **Test error paths:** Every module should have tests for both success and failure cases, including edge cases like empty input, missing files, corrupted data, and invalid formats.

7. **Assertions:** Prefer specific assertions (`assert result["status"] == "RUNNING"`) over broad ones (`assert result is not None`).

### Example Test Structure

```python
"""Tests for core/new_module.py - brief description."""

import pytest

from core.new_module import SomeClass, some_function


class TestSomeFunction:
    """Test the some_function behavior."""

    def test_success_case(self):
        result = some_function("valid_input")
        assert result["success"] is True

    def test_invalid_input(self):
        with pytest.raises(ValueError, match="Invalid"):
            some_function("")

    @pytest.mark.parametrize("input_val,expected", [
        ("a", 1),
        ("b", 2),
    ])
    def test_parametrized(self, input_val, expected):
        assert some_function(input_val) == expected
```

### Running a Single New Test

```bash
pytest tests/test_new_module.py -v -s
```
