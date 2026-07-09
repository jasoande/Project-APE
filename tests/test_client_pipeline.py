"""Tests for core/client_pipeline.py - variable substitution and status updates."""

import importlib.util
import json
import time
from pathlib import Path

import pytest


def _load_config(vars_path: Path):
    """Load a vars.py file as a module."""
    spec = importlib.util.spec_from_file_location("config", vars_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


class TestVariableSubstitution:
    """Test the variable substitution logic used in chat prompts.

    The ClientPipeline._run_chat_prompts method performs:
        prompt_text.replace('$name', self.client_name)
        prompt_text.replace('$industry', self.industry)
        prompt_text.replace('$subsegments', self.subsegments or 'various segments')
        prompt_text.replace('$persona', self.persona)
    """

    def test_name_substitution(self):
        template = "Analyze $name market position"
        result = template.replace("$name", "Test Client Corp")
        assert result == "Analyze Test Client Corp market position"

    def test_industry_substitution(self):
        template = "The $industry sector overview"
        result = template.replace("$industry", "technology")
        assert result == "The technology sector overview"

    def test_subsegments_substitution(self):
        template = "Focus on $subsegments"
        result = template.replace("$subsegments", "cloud, AI, enterprise software")
        assert result == "Focus on cloud, AI, enterprise software"

    def test_subsegments_fallback(self):
        """When subsegments is None/empty, should use fallback."""
        template = "Focus on $subsegments"
        subsegments = None
        result = template.replace("$subsegments", subsegments or "various segments")
        assert result == "Focus on various segments"

    def test_persona_substitution(self):
        template = "As a $persona, recommend..."
        result = template.replace("$persona", "Red Hat solutions architect")
        assert result == "As a Red Hat solutions architect, recommend..."

    def test_all_variables_substituted(self):
        template = (
            "As a $persona, analyze $name in the $industry industry, "
            "focusing on $subsegments."
        )
        result = template.replace("$name", "Acme Corp")
        result = result.replace("$industry", "manufacturing")
        result = result.replace("$subsegments", "automotive, aerospace")
        result = result.replace("$persona", "solutions engineer")
        assert "$" not in result
        assert "Acme Corp" in result
        assert "manufacturing" in result
        assert "automotive, aerospace" in result
        assert "solutions engineer" in result

    def test_no_variables_in_template(self):
        """Template without variables should be unchanged."""
        template = "A plain prompt with no substitution markers."
        result = template.replace("$name", "Test")
        result = result.replace("$industry", "tech")
        assert result == "A plain prompt with no substitution markers."


class TestStatusUpdate:
    """Test the status update JSON structure produced by ClientPipeline.update_status."""

    @pytest.fixture
    def pipeline(self, tmp_vars_py, tmp_status_dir):
        """Create a ClientPipeline with mocked dependencies."""
        config = _load_config(tmp_vars_py)

        # Patch heavy imports that ClientPipeline.__init__ triggers
        from unittest.mock import patch, MagicMock

        with patch("core.client_pipeline.AuthManager"), \
             patch("core.client_pipeline.NotebookManager"), \
             patch("core.client_pipeline.DriveManager", create=True):
            from core.client_pipeline import ClientPipeline

            status_file = tmp_status_dir / "test_client.json"
            p = ClientPipeline(
                client_id="test_client",
                config=config,
                status_file=status_file,
                mode="fast",
            )
            yield p

    def test_status_json_format(self, pipeline):
        """update_status should write valid JSON with required fields."""
        pipeline.update_status("Testing phase", 50, status="RUNNING")

        assert pipeline.status_file.exists()
        with open(pipeline.status_file) as f:
            data = json.load(f)

        assert data["name"] == "Test Client Corp"
        assert data["token"] == "test_client"
        assert data["step"] == "Testing phase"
        assert data["progress"] == 50
        assert data["status"] == "RUNNING"
        assert data["mode"] == "fast"
        assert "last_update" in data

    def test_status_preserves_start_time(self, pipeline):
        """Subsequent updates should preserve the original start_time."""
        pipeline.update_status("Phase 1", 10, status="RUNNING")

        with open(pipeline.status_file) as f:
            first_data = json.load(f)
        first_start = first_data["start_time"]

        # Small sleep so timestamps differ
        time.sleep(0.01)

        pipeline.update_status("Phase 2", 50, status="RUNNING")
        with open(pipeline.status_file) as f:
            second_data = json.load(f)

        assert second_data["start_time"] == first_start

    def test_status_complete(self, pipeline):
        """COMPLETE status should set progress to 100."""
        pipeline.update_status("Done", 100, status="COMPLETE", quality_score=8.5)

        with open(pipeline.status_file) as f:
            data = json.load(f)

        assert data["status"] == "COMPLETE"
        assert data["progress"] == 100
        assert data["quality_score"] == 8.5

    def test_status_failed(self, pipeline):
        """FAILED status should include error message."""
        pipeline.update_status(
            "Failed: Auth error", 0, status="FAILED", error="Auth timeout"
        )

        with open(pipeline.status_file) as f:
            data = json.load(f)

        assert data["status"] == "FAILED"
        assert data["progress"] == 0
        assert data["error"] == "Auth timeout"

    def test_kwargs_forwarded(self, pipeline):
        """Extra kwargs should be included in the status JSON."""
        pipeline.notebook_id = "nb_123"
        pipeline.update_status("Custom", 42, status="RUNNING", custom_field="value")

        with open(pipeline.status_file) as f:
            data = json.load(f)

        assert data["custom_field"] == "value"
        assert data["notebook_id"] == "nb_123"
