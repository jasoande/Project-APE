<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE" width="150"/>

  # Contributing Guide

  **Project APE - Account Planning Engine**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [Development Setup](#development-setup)
- [Running the Test Suite](#running-the-test-suite)
- [Security Checklist for New Endpoints](#security-checklist-for-new-endpoints)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)

---

## Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project-ape
```

### 2. Set Up the Virtual Environment

The launcher creates the environment automatically on first run, but you can also set it up manually:

```bash
python3 -m venv ~/.project-ape-venv
source ~/.project-ape-venv/bin/activate
pip install -r requirements.txt
```

### 3. Authenticate Services

```bash
# NotebookLM (requires Chrome)
notebooklm login

# Google Drive OAuth
python3 setup-oauth-drive.py
```

### 4. Start the Dashboard for Development

```bash
source ~/.project-ape-venv/bin/activate
python3 launch-project-ape.py
```

The dashboard runs at `http://localhost:8765/configure`.

---

## Running the Test Suite

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest --cov=core --cov=dashboard --cov-report=term-missing tests/
```

### Run a Specific Test File

```bash
pytest tests/test_retry_strategy.py -v
```

### Test Dependencies

Test dependencies are included in `requirements.txt`:

- `pytest>=8.0.0` -- test framework
- `pytest-cov>=5.0.0` -- coverage reporting
- `pytest-mock>=3.12.0` -- mock/patch utilities

All tests should pass before submitting a pull request. See [TESTING.md](TESTING.md) for the full testing guide.

---

## Security Checklist for New Endpoints

When adding a new endpoint to `dashboard/server.py`, verify each item:

### Input Validation

- [ ] URL path parameters are validated with strict regex patterns (alphanumeric, underscores, hyphens only)
- [ ] Request body fields are validated before use
- [ ] File paths are checked with `Path.is_relative_to()` to prevent traversal
- [ ] Drive URLs and folder IDs are validated with regex (no arbitrary URL fetching)
- [ ] Client IDs are validated against the configured client list where applicable

### CSRF Protection

- [ ] POST endpoints are protected by flask-wtf CSRFProtect (enabled by default)
- [ ] If CSRF exemption is required (SSE streaming), document the reason and add compensating controls
- [ ] CSRF-exempt endpoints do not perform destructive operations without additional validation

### Error Handling

- [ ] All exception handlers use `_safe_error(e, context)` to prevent information leakage
- [ ] Internal details (file paths, stack traces, internal state) are logged, not returned to clients
- [ ] Error responses use consistent JSON format: `{"success": false, "error": "..."}`

### Subprocess Execution

- [ ] Commands are passed as lists, not strings (no `shell=True`)
- [ ] Timeout is set on all subprocess calls
- [ ] Script existence is verified before execution
- [ ] Output is captured and sanitized (ANSI codes stripped) before returning to clients

### Credential Handling

- [ ] No credentials, tokens, or API keys are included in response bodies
- [ ] Credential files are saved with `0o600` permissions
- [ ] Token previews are truncated (show only first 20 characters)

### Testing

- [ ] Add tests to `tests/test_server_security.py` for input validation and error paths
- [ ] Test with malicious input (path traversal, special characters, oversized payloads)
- [ ] Verify the endpoint works with the `flask_test_client` fixture

---

## Code Style

### General Principles

- **Type hints:** Use type annotations for function parameters and return values.
- **Docstrings:** Every module, class, and public function should have a docstring. Use the established format (see existing modules).
- **Comments:** Avoid excessive inline comments. Code should be self-documenting. Use comments only for non-obvious logic or important context.
- **Imports:** Standard library first, then third-party, then project modules. Each group separated by a blank line.

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case.py` | `retry_strategy.py` |
| Classes | `PascalCase` | `CheckpointManager` |
| Functions | `snake_case` | `execute_with_retry()` |
| Constants | `UPPER_SNAKE_CASE` | `RETRYABLE_PATTERNS` |
| Client IDs | `lowercase_underscores` | `acme_corp` |
| Client Names | Proper case, spaces allowed | `Acme Corporation` |

### Project Conventions

- **Client pipeline phases:** Follow the established 8-phase order defined in `core/checkpoint_manager.py`.
- **Status updates:** Use the `update_status(step, progress, status=, **kwargs)` pattern.
- **Retry logic:** Use `core/retry_strategy.py` for any operation that may encounter transient failures. Do not implement ad-hoc retry loops.
- **Error classification:** Raise `RetryableError` for transient failures and `NonRetryableError` for permanent failures.
- **Configuration access:** Read settings from the `config` module (loaded from `vars.py`). Use `getattr(config, 'SETTING', default)` for optional settings.

---

## Pull Request Process

### Before Submitting

1. **Run the full test suite** and confirm all tests pass:
   ```bash
   pytest tests/ -v
   ```

2. **Check coverage** for your changes:
   ```bash
   pytest --cov=core --cov=dashboard --cov-report=term-missing tests/
   ```

3. **Add tests** for new functionality. Every new module should have a corresponding `tests/test_{module}.py` file.

4. **Review the security checklist** if your changes add or modify API endpoints.

5. **Test manually** with a single-client fast mode run to verify end-to-end behavior:
   ```bash
   ./run-workflow.sh fast
   ```

### PR Description

Include in your pull request description:

- **What:** Brief summary of the change
- **Why:** Motivation or issue being addressed
- **Testing:** How the change was tested (automated tests, manual verification)
- **Security:** Any security implications (new endpoints, credential handling, subprocess calls)

### Review Criteria

Pull requests are evaluated on:

- All existing tests pass
- New tests cover the added functionality
- Security checklist is satisfied for endpoint changes
- Code follows existing patterns and conventions
- No credentials, API keys, or secrets in committed code
