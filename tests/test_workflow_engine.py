"""
Workflow Engine Tests
=====================
Tests for the platform-agnostic workflow engine.

Tests:
- 5-phase pipeline execution
- Status callbacks
- Error recovery
- Mode-specific timing (fast vs deep)
- Context substitution
- Quality score calculation
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock


# ==============================================================================
# WORKFLOW ENGINE UNIT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_engine_initialization(test_client_config):
    """Test workflow engine initializes correctly."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter

    # Create mock adapter
    mock_adapter = Mock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"

    # Initialize engine
    engine = WorkflowEngine(
        adapter=mock_adapter,
        config=test_client_config
    )

    assert engine.adapter == mock_adapter
    assert engine.config == test_client_config
    assert engine.industry == test_client_config.industry
    assert engine.subsegments == test_client_config.subsegments


@pytest.mark.asyncio
async def test_workflow_status_callback():
    """Test workflow engine calls status callback."""
    from skill.engine.workflow_engine import WorkflowEngine, ClientConfig
    from skill.adapters.base_adapter import BasePlatformAdapter

    # Track status updates
    status_updates = []

    def status_callback(step, progress, status, **kwargs):
        status_updates.append({
            'step': step,
            'progress': progress,
            'status': status,
            'kwargs': kwargs
        })

    # Create mock adapter
    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"
    mock_adapter.validate_auth = AsyncMock(return_value=True)

    # Create minimal config
    config = ClientConfig(
        client_id="test",
        client_name="Test Corp",
        folder_spec="/tmp/test",
        industry="technology",
        subsegments="cloud"
    )

    # Initialize engine with callback
    engine = WorkflowEngine(
        adapter=mock_adapter,
        config=config,
        status_callback=status_callback
    )

    # Trigger status update
    engine._update_status("Test Step", 50, "RUNNING")

    # Verify callback was called
    assert len(status_updates) == 1
    assert status_updates[0]['step'] == "Test Step"
    assert status_updates[0]['progress'] == 50
    assert status_updates[0]['status'] == "RUNNING"


@pytest.mark.asyncio
async def test_variable_substitution(test_client_config):
    """Test prompt variable substitution."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = Mock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"

    engine = WorkflowEngine(adapter=mock_adapter, config=test_client_config)

    # Test prompt with variables
    prompt = """
Analyze $name in the $industry industry.
Focus on $subsegments segments.
Perspective: $persona
"""

    result = engine._substitute_variables(prompt)

    assert test_client_config.client_name in result
    assert test_client_config.industry in result
    assert test_client_config.subsegments in result
    assert test_client_config.persona in result

    # Verify variables replaced
    assert "$name" not in result
    assert "$industry" not in result
    assert "$subsegments" not in result
    assert "$persona" not in result


@pytest.mark.asyncio
async def test_quality_score_calculation():
    """Test quality score calculation logic."""
    from skill.engine.workflow_engine import WorkflowEngine, ClientConfig
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"

    # Mock source list
    mock_sources = [
        {'type': 'pdf', 'title': 'Client Doc'},
        {'type': 'web', 'title': 'Source 1'},
        {'type': 'web', 'title': 'Source 2'},
        {'type': 'web', 'title': 'Source 3'},
        {'type': 'web', 'title': 'Source 4'},
        {'type': 'web', 'title': 'Source 5'},
        {'type': 'web', 'title': 'Source 6'},
        {'type': 'web', 'title': 'Source 7'},
        {'type': 'web', 'title': 'Source 8'},
        {'type': 'web', 'title': 'Source 9'},
        {'type': 'web', 'title': 'Source 10'},
        {'type': 'url', 'title': 'Source 11'},
        {'type': 'url', 'title': 'Source 12'},
    ]

    mock_adapter.list_sources = AsyncMock(return_value=mock_sources)

    config = ClientConfig(
        client_id="test",
        client_name="Test",
        folder_spec="/tmp/test",
        industry="tech",
        subsegments="cloud"
    )

    engine = WorkflowEngine(adapter=mock_adapter, config=config)

    # Calculate quality score
    score = await engine._calculate_quality_score()

    # Validate score
    assert score >= 0.0, "Score should be >= 0"
    assert score <= 10.0, "Score should be <= 10"

    # With 13 sources (1 PDF, 12 web), we expect:
    # - Source count: (13/15) * 3 = 2.6
    # - Has PDF: 1.0
    # - Research sources (12 web >= 10): 1.0
    # Total: ~4.6
    assert score >= 4.0, f"Expected score ~4.6, got {score}"
    assert score <= 5.5, f"Expected score ~4.6, got {score}"


@pytest.mark.asyncio
async def test_workflow_timing_fast_mode(test_client_config):
    """Test workflow uses fast mode timing."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = Mock(spec=BasePlatformAdapter)

    # Set fast mode
    test_client_config.mode = "fast"

    engine = WorkflowEngine(adapter=mock_adapter, config=test_client_config)

    # Verify fast mode timings loaded
    assert 'ask_prompt_delay' in engine.config.timings
    ask_delay = engine.config.timings['ask_prompt_delay']

    # Fast mode: (8.0, 12.0)
    assert ask_delay[0] >= 5.0, "Fast mode min delay should be ~8s"
    assert ask_delay[1] <= 15.0, "Fast mode max delay should be ~12s"


@pytest.mark.asyncio
async def test_workflow_timing_deep_mode(test_client_config):
    """Test workflow uses deep mode timing."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = Mock(spec=BasPlatformAdapter)

    # Set deep mode
    test_client_config.mode = "deep"
    test_client_config.timings = {}  # Reset to trigger defaults

    # Reinitialize config to apply deep mode defaults
    test_client_config.__post_init__()

    engine = WorkflowEngine(adapter=mock_adapter, config=test_client_config)

    # Verify deep mode timings loaded
    ask_delay = engine.config.timings['ask_prompt_delay']

    # Deep mode: (15.0, 25.0)
    assert ask_delay[0] >= 12.0, "Deep mode min delay should be ~15s"
    assert ask_delay[1] <= 30.0, "Deep mode max delay should be ~25s"


# ==============================================================================
# PHASE EXECUTION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_phase_setup_validation():
    """Test phase 1 (setup) validates authentication."""
    from skill.engine.workflow_engine import WorkflowEngine, ClientConfig
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"
    mock_adapter.validate_auth = AsyncMock(return_value=False)

    config = ClientConfig(
        client_id="test",
        client_name="Test",
        folder_spec="/tmp/test",
        industry="tech",
        subsegments="cloud"
    )

    engine = WorkflowEngine(adapter=mock_adapter, config=config)

    # Phase setup should fail if auth invalid
    with pytest.raises(RuntimeError, match="Authentication validation failed"):
        await engine._phase_setup()


@pytest.mark.asyncio
async def test_workflow_result_success():
    """Test workflow returns success result."""
    from skill.engine.workflow_engine import WorkflowResult

    result = WorkflowResult(
        client_id="test",
        success=True,
        quality_score=8.5,
        outputs={'industry': 'technology'},
        duration=120.0,
        phases_completed=['setup', 'consolidation', 'research', 'analysis', 'artifacts']
    )

    assert result.success is True
    assert result.quality_score == 8.5
    assert result.error is None
    assert len(result.phases_completed) == 5


@pytest.mark.asyncio
async def test_workflow_result_failure():
    """Test workflow returns failure result with error."""
    from skill.engine.workflow_engine import WorkflowResult

    result = WorkflowResult(
        client_id="test",
        success=False,
        quality_score=0.0,
        duration=30.0,
        phases_completed=['setup'],
        error="Authentication failed",
        error_phase="consolidation"
    )

    assert result.success is False
    assert result.error == "Authentication failed"
    assert result.error_phase == "consolidation"


@pytest.mark.asyncio
async def test_workflow_handles_missing_prompts(test_client_config):
    """Test workflow handles missing prompt files gracefully."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"

    engine = WorkflowEngine(adapter=mock_adapter, config=test_client_config)

    # Mock project_root to non-existent directory
    engine.project_root = Path("/tmp/nonexistent")

    # Phase research should skip if no prompts found
    await engine._phase_research()

    # Should complete without error
    assert 'research' in engine.phases_completed


# ==============================================================================
# ERROR RECOVERY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_tracks_failed_phase():
    """Test workflow tracks which phase failed."""
    from skill.engine.workflow_engine import WorkflowEngine, ClientConfig
    from skill.adapters.base_adapter import BasePlatformAdapter

    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"
    mock_adapter.validate_auth = AsyncMock(return_value=True)

    # Mock research to fail
    from skill.adapters.base_adapter import ResearchResult
    mock_adapter.research = AsyncMock(return_value=ResearchResult(
        success=False,
        content="",
        error="Research failed"
    ))

    config = ClientConfig(
        client_id="test",
        client_name="Test",
        folder_spec="/tmp/test",
        industry="tech",
        subsegments="cloud"
    )

    # Create test prompt files
    test_prompts_dir = Path("/tmp/project_ape_test_prompts")
    test_prompts_dir.mkdir(parents=True, exist_ok=True)
    (test_prompts_dir / "ask_prompt_01.txt").write_text("Test query")

    engine = WorkflowEngine(adapter=mock_adapter, config=config)
    engine.project_root = test_prompts_dir

    # Mock consolidation phase to succeed
    engine.consolidated_pdf = Path("/tmp/test.pdf")
    engine.client_folder = Path("/tmp/test")

    with patch.object(engine, '_phase_setup', return_value=None):
        with patch.object(engine, '_phase_consolidation', return_value=None):
            result = await engine.execute()

            # Should fail at research phase
            assert result.success is False
            assert result.error_phase == "research"
            assert "setup" in result.phases_completed
            assert "consolidation" in result.phases_completed
            assert "research" not in result.phases_completed

    # Cleanup
    import shutil
    shutil.rmtree(test_prompts_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_workflow_config_validation():
    """Test workflow config validates required fields."""
    from skill.engine.workflow_engine import ClientConfig

    # Missing client_id should raise error
    with pytest.raises(ValueError, match="client_id and client_name are required"):
        ClientConfig(
            client_id="",
            client_name="Test",
            folder_spec="/tmp/test"
        )

    # Missing client_name should raise error
    with pytest.raises(ValueError, match="client_id and client_name are required"):
        ClientConfig(
            client_id="test",
            client_name="",
            folder_spec="/tmp/test"
        )
