"""Tests for /api/start-workflow command allowlisting.

Validates that:
- Arbitrary command strings are rejected
- Only valid modes (fast, deep, update) are accepted
- Client IDs are validated against the allowlist regex
- Flags are restricted to the known set
- Command injection payloads are blocked
- The structured API constructs the correct subprocess command
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root so we can import dashboard.server
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def client():
    """Flask test client with CSRF disabled for unit testing."""
    from dashboard.server import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Reject raw command strings
# ---------------------------------------------------------------------------

class TestRejectRawCommands:
    """The old API accepted a 'command' string — that must now be rejected."""

    def test_raw_command_string_rejected(self, client):
        """Sending a raw command string without mode should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "command": "python3 main.py --mode fast --clients test"
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert "Raw command strings are not accepted" in data["error"]

    def test_command_with_shell_injection_rejected(self, client):
        """Shell metacharacters in a raw command should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "command": "python3 main.py; rm -rf /"
        })
        assert resp.status_code == 400

    def test_command_with_pipe_rejected(self, client):
        """Pipe characters in a raw command should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "command": "python3 main.py | cat /etc/passwd"
        })
        assert resp.status_code == 400

    def test_empty_request_rejected(self, client):
        """Empty JSON body should be rejected."""
        resp = client.post("/api/start-workflow", json={})
        assert resp.status_code == 400

    def test_no_json_rejected(self, client):
        """Request without JSON content should be rejected."""
        resp = client.post("/api/start-workflow", data="not json")
        assert resp.status_code in (400, 415, 500)


# ---------------------------------------------------------------------------
# Mode validation
# ---------------------------------------------------------------------------

class TestModeValidation:
    """Only 'fast', 'deep', and 'update' are valid modes."""

    @pytest.mark.parametrize("mode", ["fast", "deep", "update"])
    @patch("subprocess.Popen")
    def test_valid_modes_accepted(self, mock_popen, client, mode):
        """Valid modes should not produce a 400 error."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        resp = client.post("/api/start-workflow", json={
            "mode": mode,
            "clients": ["test_client"],
            "flags": ["--skip-preflight"]
        })
        assert resp.status_code != 400, f"Mode {mode!r} was rejected"

    @pytest.mark.parametrize("mode", [
        "fast; rm -rf /",
        "shell",
        "production",
        "",
        "FAST",
        "../etc/passwd",
        "fast --extra-flag",
    ])
    def test_invalid_modes_rejected(self, client, mode):
        """Invalid or malicious mode values should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "mode": mode,
            "clients": ["test_client"]
        })
        assert resp.status_code == 400
        assert "Invalid mode" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# Client ID validation
# ---------------------------------------------------------------------------

class TestClientIDValidation:
    """Client IDs must match ^[a-zA-Z0-9_]+$ and be <= 128 chars."""

    @pytest.mark.parametrize("client_id", [
        "test_client",
        "merck",
        "blue_yonder",
        "Client123",
        "a",
    ])
    @patch("subprocess.Popen")
    def test_valid_client_ids_accepted(self, mock_popen, client, client_id):
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": [client_id],
            "flags": ["--skip-preflight"]
        })
        assert resp.status_code != 400, f"Client ID {client_id!r} was rejected"

    @pytest.mark.parametrize("client_id", [
        "../etc/passwd",
        "test; rm -rf /",
        "client name with spaces",
        "client|pipe",
        "client&background",
        "client$(whoami)",
        "client`whoami`",
        "",
        "-flag-injection",
        "client\ninjection",
        "client\x00null",
    ])
    def test_invalid_client_ids_rejected(self, client, client_id):
        """Malicious or malformed client IDs should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": [client_id]
        })
        assert resp.status_code == 400
        assert "Invalid client ID" in resp.get_json()["error"]

    def test_overly_long_client_id_rejected(self, client):
        """Client IDs longer than 128 characters should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["a" * 129]
        })
        assert resp.status_code == 400
        assert "too long" in resp.get_json()["error"]

    def test_clients_not_a_list_rejected(self, client):
        """clients must be a list, not a string."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": "not_a_list"
        })
        assert resp.status_code == 400
        assert "must be a list" in resp.get_json()["error"]

    def test_client_id_not_a_string_rejected(self, client):
        """Each client ID must be a string."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": [123]
        })
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Flag validation
# ---------------------------------------------------------------------------

class TestFlagValidation:
    """Only allowlisted flags are accepted."""

    @pytest.mark.parametrize("flag", [
        "--refresh",
        "--skip-preflight",
        "--resume",
        "--no-dashboard",
    ])
    @patch("subprocess.Popen")
    def test_valid_flags_accepted(self, mock_popen, client, flag):
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["test_client"],
            "flags": [flag]
        })
        assert resp.status_code != 400, f"Flag {flag!r} was rejected"

    @pytest.mark.parametrize("flag", [
        "--exec=rm -rf /",
        "-v",
        "--shell",
        "--arbitrary-flag",
        "; echo pwned",
        "--mode",
        "fast",
    ])
    def test_invalid_flags_rejected(self, client, flag):
        """Flags not in the allowlist should be rejected."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["test_client"],
            "flags": [flag]
        })
        assert resp.status_code == 400
        assert "Invalid flag" in resp.get_json()["error"]

    def test_flags_not_a_list_rejected(self, client):
        """flags must be a list."""
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["test_client"],
            "flags": "--refresh"
        })
        assert resp.status_code == 400
        assert "must be a list" in resp.get_json()["error"]


# ---------------------------------------------------------------------------
# Command construction validation
# ---------------------------------------------------------------------------

class TestCommandConstruction:
    """Verify the internal command builder produces correct argument lists."""

    def test_basic_command_structure(self):
        from dashboard.server import _build_workflow_command, PROJECT_ROOT

        cmd = _build_workflow_command({
            "mode": "fast",
            "clients": ["merck", "hershey"],
            "flags": ["--skip-preflight"]
        })

        assert cmd[0] == sys.executable
        assert cmd[1] == str(PROJECT_ROOT / "main.py")
        assert cmd[2:4] == ["--mode", "fast"]
        assert "--clients" in cmd
        clients_idx = cmd.index("--clients")
        assert cmd[clients_idx + 1] == "merck"
        assert cmd[clients_idx + 2] == "hershey"
        assert "--skip-preflight" in cmd

    def test_no_clients_omits_flag(self):
        from dashboard.server import _build_workflow_command

        cmd = _build_workflow_command({"mode": "fast", "clients": []})
        assert "--clients" not in cmd

    def test_no_flags_omits_flags(self):
        from dashboard.server import _build_workflow_command

        cmd = _build_workflow_command({
            "mode": "deep",
            "clients": ["test"],
        })
        assert "--refresh" not in cmd
        assert "--skip-preflight" not in cmd

    def test_multiple_flags(self):
        from dashboard.server import _build_workflow_command

        cmd = _build_workflow_command({
            "mode": "fast",
            "clients": ["c1"],
            "flags": ["--refresh", "--skip-preflight", "--resume"]
        })
        assert "--refresh" in cmd
        assert "--skip-preflight" in cmd
        assert "--resume" in cmd

    def test_default_mode_is_fast(self):
        from dashboard.server import _build_workflow_command

        cmd = _build_workflow_command({"clients": ["test"]})
        assert cmd[3] == "fast"


# ---------------------------------------------------------------------------
# Command injection via structured fields
# ---------------------------------------------------------------------------

class TestInjectionViaStructuredFields:
    """Even with structured params, verify no injection is possible."""

    def test_mode_with_embedded_flag(self, client):
        resp = client.post("/api/start-workflow", json={
            "mode": "fast --exec=malicious",
            "clients": ["test"]
        })
        assert resp.status_code == 400

    def test_client_id_with_flag_prefix(self, client):
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["--exec=rm"]
        })
        assert resp.status_code == 400

    def test_client_with_semicolon(self, client):
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["test;whoami"]
        })
        assert resp.status_code == 400

    def test_client_with_backtick(self, client):
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["test`whoami`"]
        })
        assert resp.status_code == 400

    def test_client_with_dollar_paren(self, client):
        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": ["$(cat /etc/passwd)"]
        })
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Integration: workflow_detector compatibility
# ---------------------------------------------------------------------------

class TestWorkflowDetectorCompatibility:
    """The workflow dict from workflow_detector should work with the new API."""

    @patch("subprocess.Popen")
    def test_detector_output_accepted(self, mock_popen, client):
        """A workflow dict shaped like workflow_detector output should be accepted."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process

        workflow = {
            "mode": "fast",
            "clients": ["merck", "hershey", "blue_yonder"],
            "client_count": 3,
            "flags": ["--skip-preflight"],
            "command": "python3 main.py --mode fast --clients merck hershey blue_yonder --skip-preflight",
            "dashboard_url": "http://localhost:8765",
            "drive_enabled": True,
        }

        resp = client.post("/api/start-workflow", json=workflow)
        assert resp.status_code != 400, (
            f"Workflow detector output was rejected: {resp.get_json()}"
        )

    @patch("subprocess.Popen")
    def test_six_client_fast_mode(self, mock_popen, client):
        """Simulate launching 6 clients in fast mode (matches user's test plan)."""
        mock_process = MagicMock()
        mock_process.pid = 99999
        mock_popen.return_value = mock_process

        resp = client.post("/api/start-workflow", json={
            "mode": "fast",
            "clients": [
                "blue_yonder", "hershey", "lord_abbett",
                "merck", "s_and_p_global", "toyota"
            ],
            "flags": ["--skip-preflight"]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["pid"] == 99999
