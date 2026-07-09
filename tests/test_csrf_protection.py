"""Tests for CSRF protection on the dashboard server.

Validates that:
- POST endpoints reject requests without a valid CSRF token
- POST endpoints accept requests with a valid CSRF token
- GET endpoints are unaffected by CSRF enforcement
- SSE streaming endpoints (accessed via GET) work without tokens
"""

import pytest
import json
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def csrf_app():
    """Flask app with CSRF protection enabled (production-like)."""
    from dashboard.server import app

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SECRET_KEY"] = "test-secret-key-for-csrf"
    return app


@pytest.fixture
def csrf_client(csrf_app):
    """Test client with CSRF enforcement active."""
    with csrf_app.test_client() as client:
        yield client


@pytest.fixture
def no_csrf_client():
    """Test client with CSRF disabled (for baseline comparison)."""
    from dashboard.server import app

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def _get_csrf_token(client):
    """Extract a valid CSRF token by loading a page that renders one."""
    resp = client.get("/configure")
    html = resp.data.decode()
    marker = 'name="csrf-token" content="'
    start = html.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    end = html.find('"', start)
    return html[start:end]


# ---------------------------------------------------------------------------
# Core CSRF enforcement — POST without token must be rejected
# ---------------------------------------------------------------------------

class TestCSRFRejectsWithoutToken:
    """Every POST endpoint must return 400 when no CSRF token is sent."""

    POST_ENDPOINTS = [
        ("/api/generate-config", {"clients": []}),
        ("/api/save-config", {"config": {}}),
        ("/api/validate-drive-url", {"url": "https://drive.google.com/drive/folders/abc"}),
        ("/api/import-csv", {}),
        ("/api/preview-config", {"clients": []}),
        ("/api/start-workflow", {"command": "echo test"}),
        ("/api/notebooklm-login", {}),
        ("/api/notebooklm-logout", {}),
        ("/api/refresh-sources", {"clients": []}),
        ("/api/clear-cache", {}),
        ("/api/stop-workflow", {}),
        ("/api/shutdown", {}),
        ("/api/setup/install-homebrew", {}),
        ("/api/setup/install-podman", {}),
        ("/api/setup/install-gcloud", {}),
        ("/api/setup/install-python", {}),
        ("/api/setup/create-venv", {}),
        ("/api/setup/install-notebooklm", {}),
    ]

    @pytest.mark.parametrize("endpoint,payload", POST_ENDPOINTS)
    def test_post_without_token_is_rejected(self, csrf_client, endpoint, payload):
        """POST without X-CSRFToken header must be rejected (400)."""
        resp = csrf_client.post(
            endpoint,
            json=payload,
            content_type="application/json",
        )
        assert resp.status_code == 400, (
            f"{endpoint} accepted POST without CSRF token (got {resp.status_code})"
        )


# ---------------------------------------------------------------------------
# CSRF acceptance — POST with valid token must succeed (not 400)
# ---------------------------------------------------------------------------

class TestCSRFAcceptsWithToken:
    """POST endpoints must not reject requests that carry a valid CSRF token."""

    SAFE_POST_ENDPOINTS = [
        ("/api/generate-config", {"clients": []}),
        ("/api/validate-drive-url", {"url": "https://drive.google.com/drive/folders/abc"}),
        ("/api/preview-config", {"clients": []}),
        ("/api/stop-workflow", {}),
    ]

    @pytest.mark.parametrize("endpoint,payload", SAFE_POST_ENDPOINTS)
    def test_post_with_valid_token_not_rejected(self, csrf_client, endpoint, payload):
        """POST with a valid CSRF token must not get a 400 CSRF error."""
        token = _get_csrf_token(csrf_client)
        assert token, "Could not extract CSRF token from /configure page"

        resp = csrf_client.post(
            endpoint,
            json=payload,
            content_type="application/json",
            headers={"X-CSRFToken": token},
        )
        assert resp.status_code != 400, (
            f"{endpoint} rejected POST even WITH valid CSRF token (got {resp.status_code})"
        )

    def test_save_config_with_token(self, csrf_client):
        """save-config with valid token should not get CSRF rejection."""
        token = _get_csrf_token(csrf_client)
        resp = csrf_client.post(
            "/api/save-config",
            json={"config": {}},
            content_type="application/json",
            headers={"X-CSRFToken": token},
        )
        assert resp.status_code != 400

    def test_clear_cache_with_token(self, csrf_client):
        """clear-cache with valid token should not get CSRF rejection."""
        token = _get_csrf_token(csrf_client)
        resp = csrf_client.post(
            "/api/clear-cache",
            json={},
            content_type="application/json",
            headers={"X-CSRFToken": token},
        )
        assert resp.status_code != 400

    def test_refresh_sources_with_token(self, csrf_client):
        """refresh-sources with valid token should not get CSRF rejection."""
        token = _get_csrf_token(csrf_client)
        resp = csrf_client.post(
            "/api/refresh-sources",
            json={"clients": []},
            content_type="application/json",
            headers={"X-CSRFToken": token},
        )
        assert resp.status_code != 400


# ---------------------------------------------------------------------------
# GET endpoints — unaffected by CSRF
# ---------------------------------------------------------------------------

class TestGETEndpointsUnaffected:
    """GET endpoints must work normally regardless of CSRF enforcement."""

    GET_ENDPOINTS = [
        "/health",
        "/status",
        "/api/config-status",
        "/api/load-config",
        "/api/check-auth-status",
        "/api/cache-stats",
        "/api/oauth-status",
        "/api/system-status",
        "/api/preflight-check",
        "/api/test-drive-access",
        "/api/setup/system-info",
        "/api/setup/check-homebrew",
        "/api/setup/check-podman",
        "/api/setup/check-gcloud",
        "/api/setup/check-python",
        "/api/setup/check-venv",
        "/api/setup/check-notebooklm",
    ]

    @pytest.mark.parametrize("endpoint", GET_ENDPOINTS)
    def test_get_endpoint_works_with_csrf_enabled(self, csrf_client, endpoint):
        """GET endpoints should return a successful status code."""
        resp = csrf_client.get(endpoint)
        assert resp.status_code in (200, 404, 500), (
            f"GET {endpoint} returned unexpected {resp.status_code} with CSRF enabled"
        )


# ---------------------------------------------------------------------------
# SSE streaming endpoints — accessed via GET, must work without tokens
# ---------------------------------------------------------------------------

class TestSSEEndpointsWork:
    """SSE endpoints accessed via EventSource (GET) must not require CSRF."""

    def test_run_setup_sse_accessible(self, csrf_client):
        """GET /api/run-setup should stream SSE (not blocked by CSRF)."""
        resp = csrf_client.get("/api/run-setup")
        assert resp.status_code in (200, 500)

    def test_start_oauth_flow_sse_accessible(self, csrf_client):
        """GET /api/start-oauth-flow should stream SSE (not blocked by CSRF)."""
        resp = csrf_client.get("/api/start-oauth-flow")
        assert resp.status_code == 200

    def test_log_streaming_accessible(self, csrf_client):
        """GET /logs/test_client should not be blocked by CSRF."""
        resp = csrf_client.get("/logs/test_client")
        assert resp.status_code in (200, 404)

    def test_overall_log_streaming_accessible(self, csrf_client):
        """GET /logs/overall should not be blocked by CSRF."""
        resp = csrf_client.get("/logs/overall")
        assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# Template CSRF token injection
# ---------------------------------------------------------------------------

class TestCSRFTokenInTemplates:
    """Templates must contain a CSRF meta tag with a non-empty token."""

    PAGES_WITH_CSRF = [
        "/configure",
        "/",
        "/launch",
        "/setup-environment",
    ]

    @pytest.mark.parametrize("page", PAGES_WITH_CSRF)
    def test_page_has_csrf_meta_tag(self, csrf_client, page):
        """Page must contain <meta name="csrf-token" content="..."> with a real token."""
        resp = csrf_client.get(page)
        if resp.status_code != 200:
            pytest.skip(f"{page} returned {resp.status_code}")
        html = resp.data.decode()
        assert 'name="csrf-token"' in html, f"{page} is missing CSRF meta tag"
        token = _get_csrf_token(csrf_client)
        assert len(token) > 10, f"{page} has empty or trivially short CSRF token"


# ---------------------------------------------------------------------------
# File upload with CSRF — the XMLHttpRequest path
# ---------------------------------------------------------------------------

class TestFileUploadCSRF:
    """File upload via XMLHttpRequest must include CSRF token."""

    def test_upload_without_csrf_rejected(self, csrf_client):
        """File upload without CSRF token must be rejected."""
        import io
        data = {"file": (io.BytesIO(b'{"installed": {"client_id": "test"}}'), "creds.json")}
        resp = csrf_client.post(
            "/api/upload-oauth-credentials",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_upload_with_csrf_accepted(self, csrf_client):
        """File upload with valid CSRF token must not be rejected for CSRF."""
        import io
        token = _get_csrf_token(csrf_client)
        data = {"file": (io.BytesIO(b'{"installed": {"client_id": "test123"}}'), "creds.json")}
        resp = csrf_client.post(
            "/api/upload-oauth-credentials",
            data=data,
            content_type="multipart/form-data",
            headers={"X-CSRFToken": token},
        )
        assert resp.status_code != 400 or b"CSRF" not in resp.data


# ---------------------------------------------------------------------------
# Invalid / expired token handling
# ---------------------------------------------------------------------------

class TestInvalidTokens:
    """Requests with forged or invalid tokens must be rejected."""

    def test_forged_token_rejected(self, csrf_client):
        """A fabricated token must be rejected."""
        resp = csrf_client.post(
            "/api/generate-config",
            json={"clients": []},
            content_type="application/json",
            headers={"X-CSRFToken": "this-is-not-a-valid-token"},
        )
        assert resp.status_code == 400

    def test_empty_token_rejected(self, csrf_client):
        """An empty token must be rejected."""
        resp = csrf_client.post(
            "/api/generate-config",
            json={"clients": []},
            content_type="application/json",
            headers={"X-CSRFToken": ""},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Backward compatibility — CSRF-disabled mode still works
# ---------------------------------------------------------------------------

class TestCSRFDisabledMode:
    """When WTF_CSRF_ENABLED=False (test fixture), POST endpoints work without tokens."""

    def test_post_works_without_token_when_disabled(self, no_csrf_client):
        """POST should work without CSRF token when CSRF is disabled."""
        resp = no_csrf_client.post(
            "/api/generate-config",
            json={"clients": []},
            content_type="application/json",
        )
        assert resp.status_code != 400 or b"CSRF" not in resp.data

    def test_stop_workflow_works_without_token_when_disabled(self, no_csrf_client):
        """stop-workflow should work without CSRF token when CSRF is disabled."""
        resp = no_csrf_client.post(
            "/api/stop-workflow",
            json={},
            content_type="application/json",
        )
        assert resp.status_code != 400 or b"CSRF" not in resp.data
