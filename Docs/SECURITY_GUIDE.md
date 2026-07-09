<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence" width="150"/>

  # Security Guide

  **Enterprise Security Architecture and Best Practices**

  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

- [Overview](#overview)
- [CSRF Protection](#csrf-protection)
- [Path Traversal Prevention](#path-traversal-prevention)
- [Subprocess Security](#subprocess-security)
- [Error Message Sanitization](#error-message-sanitization)
- [Authentication Security](#authentication-security)
- [Credential Storage](#credential-storage)
- [Container Security](#container-security)
- [Input Validation](#input-validation)
- [Configuration File Safety](#configuration-file-safety)

---

## Overview

Account Intelligence follows defense-in-depth security principles across its web dashboard, subprocess execution, credential management, and container deployment. This guide documents the security controls in place and the rationale behind each.

---

## CSRF Protection

The dashboard uses `flask-wtf` (`CSRFProtect`) to guard against Cross-Site Request Forgery attacks on all POST endpoints.

**Implementation:** `CSRFProtect` is initialized in `dashboard/server.py` with a randomly generated `SECRET_KEY`.

**CSRF-exempt endpoints:** A small number of endpoints are exempt because they use Server-Sent Events (SSE) streaming, which is incompatible with CSRF token submission:

| Endpoint | Reason for Exemption |
|----------|----------------------|
| `POST /api/run-setup` | SSE streaming of setup script output |
| `POST /api/refresh-sources` | SSE streaming of Drive cache refresh progress |
| `POST /api/update-notebook-sources` | SSE streaming of source update progress |
| `GET/POST /api/start-oauth-flow` | SSE streaming of OAuth flow progress |

These endpoints mitigate the CSRF exemption risk through input validation and controlled execution scope.

---

## Path Traversal Prevention

The `/logs/<client_token>` endpoint streams log files for a given client. Without validation, an attacker could craft a URL like `/logs/../../../etc/passwd` to read arbitrary files.

**Controls:**

1. **Token validation:** The `_validate_client_token()` function enforces a strict regex pattern `^[a-zA-Z0-9_-]+$` with a maximum length of 128 characters. Any token containing path separators, dots, spaces, or other special characters is rejected with HTTP 400.

2. **Path containment:** After constructing the log file path, `Path.is_relative_to()` verifies the resolved path falls within the designated `LOGS_DIR`. This prevents bypasses via URL encoding or other techniques.

3. **Test coverage:** `tests/test_server_security.py` includes specific test cases for directory traversal via `../`, URL-encoded traversal (`..%2f`), and special characters.

---

## Subprocess Security

All external process execution uses `subprocess.Popen` or `subprocess.run` with explicit argument lists. The `shell=True` pattern has been eliminated to prevent shell injection attacks.

**Controls:**

- Commands are constructed as Python lists, not strings: `["notebooklm", "list", "--json"]`
- Timeout enforcement on all subprocess calls (10s for quick operations, 300s for long-running scripts)
- PATH is explicitly set for spawned processes to use the virtual environment
- Script existence is verified before execution
- `capture_output=True` prevents subprocess output from leaking to unexpected destinations

---

## Error Message Sanitization

The `_safe_error(e, context)` helper function prevents information leakage through error responses. Internal exception details (stack traces, file paths, internal state) are logged to stderr for debugging but never returned to the client.

**Pattern:**

```python
def _safe_error(e, context="operation"):
    """Return a generic error message; log the real error to stderr."""
    logger.error(f"{context} failed: {e}")
    return f"An error occurred during {context}. Check server logs for details."
```

This function is used consistently across all API endpoints that handle exceptions.

---

## Authentication Security

### NotebookLM OAuth2

- Credentials stored at `~/.notebooklm/profiles/default/storage_state.json`
- `AuthManager` validates JSON structure and required `cookies` field
- Authentication checks are cached for 1 minute to avoid excessive file I/O
- Anti-collision delays prevent multiple client processes from triggering simultaneous auth checks
- Retry logic with exponential backoff for file access issues (max 3 attempts)

### Google Drive OAuth2

- Credentials file: `~/.project-ape/drive_credentials.json`
- Token file: `~/.project-ape/drive_token.json`
- Tokens have approximately 90-day expiry and are auto-refreshed
- Token files are saved with `0o600` permissions (owner read/write only)
- The upload endpoint validates JSON structure before saving (requires `installed.client_id` keys)
- Credential preview in API responses is truncated (first 20 characters only)

### Gemini API

- API key provided via `GEMINI_API_KEY` environment variable (optional feature)
- No API keys are embedded in code or configuration files

---

## Credential Storage

| Credential | Location | Permissions |
|------------|----------|-------------|
| NotebookLM OAuth state | `~/.notebooklm/credentials.json` | User directory |
| Drive OAuth credentials | `~/.project-ape/drive_credentials.json` | `0o600` |
| Drive OAuth token | `~/.project-ape/drive_token.json` | `0o600` |
| Gemini API key | `GEMINI_API_KEY` env var | Process environment |

No credentials are stored in the repository, configuration files, or container images. Container deployments use volume mounts to share host credentials.

---

## Container Security

- **Non-root execution:** Container runs as `apeuser` (UID 1000), not root.
- **Read-only mounts:** Client data and configuration files are mounted read-only (`:ro`).
- **SELinux compatibility:** Host directories use `:z` label for RHEL/Fedora environments.
- **No embedded secrets:** Credentials are injected via volume mounts at runtime.
- **Minimal image:** Debian-based image with only required dependencies.

---

## Input Validation

### Client ID Sanitization

The `sanitize_client_id()` function in `dashboard/config_generator.py` converts user-provided client names into safe Python identifiers:

- Spaces and hyphens replaced with underscores
- Special characters removed
- Leading digits prefixed with underscore
- Length capped at 64 characters
- Forced to lowercase

### Drive URL Validation

Google Drive URLs are validated with regex pattern matching. The `/api/validate-drive-url` endpoint checks URL format without making API calls, preventing SSRF-style attacks.

### CSV Import Validation

Uploaded CSV files are validated row-by-row. Each row passes through `validate_client_data()` with per-line error tracking. Validation failures are reported per row without cascading to other rows.

### API Request Validation

- `POST /api/generate-config` rejects empty payloads
- `POST /api/save-config` validates Python syntax before writing to disk
- Client tokens in URL paths are validated against strict character allowlists

---

## Configuration File Safety

When saving configuration through the web UI:

1. **Automatic backup:** A timestamped backup of the existing `vars.py` is created before any write.
2. **Syntax validation:** The generated Python code is compiled (`compile()`) before being written to disk.
3. **Rollback on failure:** If syntax validation fails, the backup is restored automatically.
4. **No code execution during validation:** Configuration is compiled but not executed during the validation step.
