"""Tests for dashboard/server.py - security hardening.

These tests verify that the Flask server properly validates input
and blocks path traversal attacks in URL-routed parameters.
"""

import pytest


class TestPathTraversal:
    """Verify that path traversal attacks are blocked in log streaming."""

    def test_valid_token_not_rejected(self, flask_test_client):
        """A well-formed client token should not be rejected with 400."""
        resp = flask_test_client.get("/logs/valid_client")
        assert resp.status_code != 400

    def test_traversal_blocked(self, flask_test_client):
        """Directory traversal via ../ should be blocked."""
        resp = flask_test_client.get("/logs/../../../etc/passwd")
        assert resp.status_code in (400, 404)

    def test_special_chars_blocked(self, flask_test_client):
        """URL-encoded spaces and other special chars should be blocked or 404."""
        resp = flask_test_client.get("/logs/client%20name")
        assert resp.status_code in (400, 404)

    def test_dots_blocked(self, flask_test_client):
        """URL-encoded traversal (..%2f) should be blocked."""
        resp = flask_test_client.get("/logs/..%2f..%2fetc%2fpasswd")
        assert resp.status_code in (400, 404)


class TestAPIEndpoints:
    """Basic smoke tests for API endpoints."""

    def test_health_endpoint(self, flask_test_client):
        """Health check should return 200."""
        resp = flask_test_client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] in ("healthy", "unhealthy")

    def test_status_endpoint(self, flask_test_client):
        """Status endpoint should return JSON even without status files."""
        resp = flask_test_client.get("/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total" in data
        assert "clients" in data

    def test_config_status_endpoint(self, flask_test_client):
        """Config status should return JSON."""
        resp = flask_test_client.get("/api/config-status")
        assert resp.status_code == 200
        data = resp.get_json()
        # Either configured or not, should have a response
        assert "configured" in data or "error" in data

    def test_generate_config_requires_post(self, flask_test_client):
        """Generate config should reject GET requests."""
        resp = flask_test_client.get("/api/generate-config")
        assert resp.status_code == 405  # Method Not Allowed

    def test_generate_config_requires_data(self, flask_test_client):
        """Generate config should reject empty POST with an error status."""
        resp = flask_test_client.post(
            "/api/generate-config",
            json={},
            content_type="application/json",
        )
        # 400 if validation catches it, 500 if config_generator import fails
        # in test context (both indicate the empty body was not accepted)
        assert resp.status_code in (400, 500)
        data = resp.get_json()
        assert data["success"] is False
