"""Tests for core/health_checks.py - preflight health checks."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.health_checks import (
    check_config_valid,
    check_drive_auth,
    check_notebooklm_auth,
    check_notebooklm_available,
    run_preflight_checks,
)


class TestCheckNotebookLMAvailable:
    """Test notebooklm CLI availability check."""

    def test_success_when_cli_found(self, mocker):
        mock_run = mocker.patch("core.health_checks.subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stdout='[]', stderr='')
        result = check_notebooklm_available()
        assert result["passed"] is True
        assert result["check"] == "notebooklm_cli"

    def test_failure_when_cli_not_found(self, mocker):
        mock_run = mocker.patch("core.health_checks.subprocess.run")
        mock_run.side_effect = FileNotFoundError("notebooklm not found")
        result = check_notebooklm_available()
        assert result["passed"] is False
        assert "not found" in result["message"].lower()

    def test_failure_on_nonzero_return(self, mocker):
        mock_run = mocker.patch("core.health_checks.subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stderr="some error")
        result = check_notebooklm_available()
        assert result["passed"] is False


class TestCheckNotebookLMAuth:
    """Test NotebookLM authentication check.

    AuthManager is imported inside the function body, so we patch
    it at the source module (core.auth_manager.AuthManager).
    """

    def test_authenticated(self, mocker):
        mock_auth_cls = mocker.patch("core.auth_manager.AuthManager")
        mock_auth_cls.return_value.is_authenticated.return_value = True
        result = check_notebooklm_auth()
        assert result["passed"] is True

    def test_not_authenticated(self, mocker):
        mock_auth_cls = mocker.patch("core.auth_manager.AuthManager")
        mock_auth_cls.return_value.is_authenticated.return_value = False
        result = check_notebooklm_auth()
        assert result["passed"] is False


class TestCheckDriveAuth:
    """Test Google Drive token existence check.

    check_drive_auth() reads from a hardcoded path
    (~/.project-ape/drive_token.json). We mock Path.home() to point at
    a temp directory so we can control file existence.
    """

    def test_token_exists(self, mocker, tmp_path):
        mocker.patch("core.health_checks.Path.home", return_value=tmp_path)
        token_dir = tmp_path / ".project-ape"
        token_dir.mkdir()
        token_file = token_dir / "drive_token.json"
        token_file.write_text('{"token": "abc123"}')

        result = check_drive_auth()
        assert result["passed"] is True

    def test_token_missing(self, mocker, tmp_path):
        mocker.patch("core.health_checks.Path.home", return_value=tmp_path)
        # Do NOT create the token file
        result = check_drive_auth()
        assert result["passed"] is False

    def test_token_missing_token_key(self, mocker, tmp_path):
        mocker.patch("core.health_checks.Path.home", return_value=tmp_path)
        token_dir = tmp_path / ".project-ape"
        token_dir.mkdir()
        token_file = token_dir / "drive_token.json"
        token_file.write_text('{"no_token": true}')

        result = check_drive_auth()
        assert result["passed"] is False


class TestCheckConfigValid:
    """Test configuration file validation."""

    def test_valid_config(self, tmp_vars_py):
        result = check_config_valid(vars_path=tmp_vars_py)
        assert result["passed"] is True

    def test_missing_config(self, tmp_path):
        missing = tmp_path / "nonexistent_vars.py"
        result = check_config_valid(vars_path=missing)
        assert result["passed"] is False
        assert "not found" in result["message"].lower()

    def test_config_without_clients(self, tmp_path):
        empty_conf = tmp_path / "empty.py"
        empty_conf.write_text("x = 1\n")
        result = check_config_valid(vars_path=empty_conf)
        assert result["passed"] is False


class TestRunPreflightChecks:
    """Test aggregated preflight check runner."""

    def test_all_pass(self, mocker, tmp_vars_py):
        mocker.patch("core.health_checks.check_notebooklm_available",
                      return_value={"check": "notebooklm_cli", "passed": True, "message": "ok"})
        mocker.patch("core.health_checks.check_notebooklm_auth",
                      return_value={"check": "notebooklm_auth", "passed": True, "message": "ok"})
        mocker.patch("core.health_checks.check_drive_auth",
                      return_value={"check": "drive_auth", "passed": True, "message": "ok"})
        mocker.patch("core.health_checks.check_config_valid",
                      return_value={"check": "config_valid", "passed": True, "message": "ok"})

        results = run_preflight_checks(vars_path=tmp_vars_py)
        assert results["all_passed"] is True

    def test_partial_failure(self, mocker, tmp_vars_py):
        mocker.patch("core.health_checks.check_notebooklm_available",
                      return_value={"check": "notebooklm_cli", "passed": True, "message": "ok"})
        mocker.patch("core.health_checks.check_notebooklm_auth",
                      return_value={"check": "notebooklm_auth", "passed": False, "message": "fail"})
        mocker.patch("core.health_checks.check_drive_auth",
                      return_value={"check": "drive_auth", "passed": True, "message": "ok"})
        mocker.patch("core.health_checks.check_config_valid",
                      return_value={"check": "config_valid", "passed": True, "message": "ok"})

        results = run_preflight_checks(vars_path=tmp_vars_py)
        assert results["all_passed"] is False
        failed_checks = [c["check"] for c in results["checks"] if not c["passed"]]
        assert "notebooklm_auth" in failed_checks
