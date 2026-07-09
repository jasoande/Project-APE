"""Tests for core/checkpoint_manager.py - pipeline checkpoint/resume."""

import json

import pytest

from core.checkpoint_manager import CheckpointManager, PipelineCheckpoint


@pytest.fixture
def ckpt_manager(tmp_path):
    """Create a CheckpointManager with a temporary logs directory."""
    return CheckpointManager(
        logs_dir=tmp_path, client_id="test_client", run_id="run_001"
    )


@pytest.fixture
def sample_checkpoint():
    """Create a sample PipelineCheckpoint for testing."""
    return PipelineCheckpoint(
        client_id="test_client",
        run_id="run_001",
        mode="fast",
        phase="run_research",
        phase_number=5,
        completed_phases=["setup_folder", "determine_industry", "check_auth"],
        notebook_id="nb_abc123",
        industry="technology",
        subsegments="cloud, AI",
    )


class TestSaveAndLoad:
    """Test checkpoint save/load round-trip."""

    def test_save_and_load_roundtrip(self, ckpt_manager, sample_checkpoint):
        ckpt_manager.save(sample_checkpoint)
        loaded = ckpt_manager.load()

        assert loaded is not None
        assert loaded.client_id == "test_client"
        assert loaded.run_id == "run_001"
        assert loaded.mode == "fast"
        assert loaded.phase == "run_research"
        assert loaded.phase_number == 5
        assert loaded.notebook_id == "nb_abc123"
        assert loaded.industry == "technology"
        assert loaded.subsegments == "cloud, AI"
        assert "setup_folder" in loaded.completed_phases
        assert "determine_industry" in loaded.completed_phases
        assert "check_auth" in loaded.completed_phases

    def test_save_updates_last_update(self, ckpt_manager, sample_checkpoint):
        sample_checkpoint.last_update = 0.0
        ckpt_manager.save(sample_checkpoint)
        assert sample_checkpoint.last_update > 0.0

    def test_load_returns_none_when_no_checkpoint(self, ckpt_manager):
        result = ckpt_manager.load()
        assert result is None


class TestShouldSkipPhase:
    """Test phase-skip logic."""

    def test_skip_completed_phases(self, ckpt_manager, sample_checkpoint):
        assert ckpt_manager.should_skip_phase("setup_folder", sample_checkpoint) is True
        assert ckpt_manager.should_skip_phase("determine_industry", sample_checkpoint) is True
        assert ckpt_manager.should_skip_phase("check_auth", sample_checkpoint) is True

    def test_do_not_skip_pending_phases(self, ckpt_manager, sample_checkpoint):
        assert ckpt_manager.should_skip_phase("run_research", sample_checkpoint) is False
        assert ckpt_manager.should_skip_phase("run_chat", sample_checkpoint) is False
        assert ckpt_manager.should_skip_phase("generate_mindmap", sample_checkpoint) is False


class TestClear:
    """Test checkpoint clearing."""

    def test_clear_removes_file(self, ckpt_manager, sample_checkpoint):
        ckpt_manager.save(sample_checkpoint)
        # Verify file exists
        assert ckpt_manager.checkpoint_file.exists()
        ckpt_manager.clear()
        # Verify file is gone
        assert not ckpt_manager.checkpoint_file.exists()

    def test_clear_when_no_file(self, ckpt_manager):
        # Should not raise when file does not exist
        ckpt_manager.clear()


class TestCorruptedCheckpoint:
    """Test handling of corrupted checkpoint files."""

    def test_corrupted_json_returns_none(self, ckpt_manager):
        # Write invalid JSON directly to checkpoint file
        ckpt_manager.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        ckpt_manager.checkpoint_file.write_text("{invalid json content")
        result = ckpt_manager.load()
        assert result is None

    def test_empty_file_returns_none(self, ckpt_manager):
        ckpt_manager.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        ckpt_manager.checkpoint_file.write_text("")
        result = ckpt_manager.load()
        assert result is None

    def test_missing_keys_returns_none(self, ckpt_manager):
        # Write valid JSON but with missing required keys
        ckpt_manager.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        ckpt_manager.checkpoint_file.write_text(json.dumps({"client_id": "test"}))
        result = ckpt_manager.load()
        assert result is None
