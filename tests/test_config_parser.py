"""Tests for dashboard/config_parser.py - configuration parsing."""

import pytest
from pathlib import Path

from dashboard.config_parser import (
    extract_client_configs,
    extract_global_settings,
    parse_vars_file,
    validate_settings,
)


class TestParseVarsFile:
    """Test parsing of vars.py into structured data."""

    def test_parse_valid_config(self, tmp_vars_py):
        result = parse_vars_file(tmp_vars_py)
        assert "clients" in result
        assert "settings" in result
        assert len(result["clients"]) == 1

    def test_client_data_extracted(self, tmp_vars_py):
        result = parse_vars_file(tmp_vars_py)
        client = result["clients"][0]
        assert client["id"] == "test_client"
        assert client["name"] == "Test Client Corp"
        assert "drive.google.com" in client["folder"]
        assert client["industry"] == "technology"
        assert client["subsegments"] == "cloud, AI, enterprise software"

    def test_settings_extracted(self, tmp_vars_py):
        result = parse_vars_file(tmp_vars_py)
        settings = result["settings"]
        assert settings["persona"] == "Red Hat solutions architect"
        assert settings["default_mode"] == "fast"
        assert settings["DASHBOARD_PORT"] == 8765

    def test_timing_settings_extracted(self, tmp_vars_py):
        result = parse_vars_file(tmp_vars_py)
        settings = result["settings"]
        assert "TIMINGS" in settings
        assert "DEEP_TIMINGS" in settings
        assert "RETRY_CONFIG" in settings
        assert settings["TIMINGS"]["notebook_creation_delay"] == 3.0

    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "nonexistent.py"
        with pytest.raises(FileNotFoundError):
            parse_vars_file(missing)


class TestExtractClientConfigs:
    """Test client configuration extraction from module."""

    def test_extracts_all_client_fields(self, tmp_vars_py):
        import importlib.util

        spec = importlib.util.spec_from_file_location("config", tmp_vars_py)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        clients = extract_client_configs(config)
        assert len(clients) == 1
        client = clients[0]
        assert set(client.keys()) == {"id", "name", "folder", "industry", "subsegments"}

    def test_empty_clients_list(self, tmp_path):
        import importlib.util

        empty_config = tmp_path / "empty_vars.py"
        empty_config.write_text("clients = []\n")

        spec = importlib.util.spec_from_file_location("config", empty_config)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        clients = extract_client_configs(config)
        assert clients == []

    def test_no_clients_attribute(self, tmp_path):
        import importlib.util

        no_clients = tmp_path / "no_clients.py"
        no_clients.write_text("persona = 'test'\n")

        spec = importlib.util.spec_from_file_location("config", no_clients)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        clients = extract_client_configs(config)
        assert clients == []


class TestExtractGlobalSettings:
    """Test global settings extraction."""

    def test_default_values_when_missing(self, tmp_path):
        import importlib.util

        minimal = tmp_path / "minimal.py"
        minimal.write_text("x = 1\n")

        spec = importlib.util.spec_from_file_location("config", minimal)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        settings = extract_global_settings(config)
        assert settings["persona"] == "Red Hat solutions architect"
        assert settings["default_mode"] == "fast"
        assert settings["DASHBOARD_PORT"] == 8765


class TestValidateSettings:
    """Test settings validation."""

    def test_valid_settings(self):
        valid, errors = validate_settings({
            "persona": "solutions architect",
            "default_mode": "fast",
            "DASHBOARD_PORT": 8765,
        })
        assert valid is True
        assert errors == []

    def test_invalid_mode(self):
        valid, errors = validate_settings({"default_mode": "turbo"})
        assert valid is False
        assert any("default_mode" in e for e in errors)

    def test_invalid_port_range(self):
        valid, errors = validate_settings({"DASHBOARD_PORT": 80})
        assert valid is False
        assert any("DASHBOARD_PORT" in e for e in errors)

    def test_empty_persona_rejected(self):
        valid, errors = validate_settings({"persona": ""})
        assert valid is False
        assert any("persona" in e for e in errors)
