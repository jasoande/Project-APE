"""
Adapter Unit Tests
==================
Unit tests for individual adapter methods with mocked external dependencies.

Tests:
- NotebookLM adapter with mocked subprocess calls
- Claude adapter with mocked Anthropic API
- Gemini adapter with mocked Gemini API
- Error handling and retries
- Timeout behavior
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path


# ==============================================================================
# NOTEBOOKLM ADAPTER UNIT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_notebooklm_validate_auth_success():
    """Test NotebookLM auth validation with valid credentials."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter

    adapter = NotebookLMAdapter(client_id="test")

    # Mock credentials file exists
    with patch.object(Path, 'exists', return_value=True):
        # Mock subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"notebooks": []}'

        with patch('subprocess.run', return_value=mock_result):
            result = await adapter.validate_auth()

            assert result is True, "Auth validation should succeed"


@pytest.mark.asyncio
async def test_notebooklm_validate_auth_no_credentials():
    """Test NotebookLM auth validation with missing credentials."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter

    adapter = NotebookLMAdapter(client_id="test")

    # Mock credentials file does not exist
    with patch.object(Path, 'exists', return_value=False):
        result = await adapter.validate_auth()

        assert result is False, "Auth validation should fail without credentials"


@pytest.mark.asyncio
async def test_notebooklm_research_success():
    """Test NotebookLM research with successful response."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter

    adapter = NotebookLMAdapter(client_id="test", notebook_id="nb_123")

    # Mock subprocess response
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = """
Research completed successfully.
Imported 15 sources from web search.

Cloud computing trends include multi-cloud [1], AI/ML integration [2],
and edge computing [3].
"""

    with patch('subprocess.run', return_value=mock_result):
        result = await adapter.research(
            query="What are cloud computing trends?",
            mode="fast"
        )

        assert result.success is True
        assert len(result.content) > 0
        assert result.sources_imported == 15
        assert len(result.citations) == 3


@pytest.mark.asyncio
async def test_notebooklm_research_no_notebook_id():
    """Test NotebookLM research fails without notebook_id."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter

    adapter = NotebookLMAdapter(client_id="test")  # No notebook_id

    result = await adapter.research(query="Test query", mode="fast")

    assert result.success is False
    assert "notebook_id not set" in result.error


@pytest.mark.asyncio
async def test_notebooklm_analyze_success():
    """Test NotebookLM analysis with successful response."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter

    adapter = NotebookLMAdapter(client_id="test", notebook_id="nb_123")

    # Mock subprocess response
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = """
Analysis complete.

Key challenges include legacy systems [1], skills gaps [2], and budget [3].
"""

    with patch('subprocess.run', return_value=mock_result):
        result = await adapter.analyze(
            prompt="What are the key challenges?",
            context={"persona": "architect"}
        )

        assert result.success is True
        assert len(result.content) > 0
        assert len(result.citations) == 3


# ==============================================================================
# CLAUDE ADAPTER UNIT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_claude_validate_auth_success():
    """Test Claude auth validation with valid API key."""
    from skill.adapters.claude_adapter import ClaudeAdapter

    # Mock Anthropic client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hi")]

    mock_client.messages.create.return_value = mock_response

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('skill.adapters.claude_adapter.anthropic.Anthropic', return_value=mock_client):
            adapter = ClaudeAdapter(client_id="test")

            # Mock asyncio.to_thread to execute synchronously
            with patch('asyncio.to_thread', side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
                result = await adapter.validate_auth()

                assert result is True


@pytest.mark.asyncio
async def test_claude_research_success():
    """Test Claude research with successful response."""
    from skill.adapters.claude_adapter import ClaudeAdapter

    # Mock Anthropic response
    mock_response = MagicMock()
    mock_content_block = MagicMock()
    mock_content_block.text = """
Cloud computing trends for 2026:

1. Multi-cloud adoption [Source 1](https://example.com/1)
2. AI/ML integration [Source 2](https://example.com/2)
3. Edge computing [Source 3](https://example.com/3)
"""
    mock_response.content = [mock_content_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('skill.adapters.claude_adapter.anthropic.Anthropic', return_value=mock_client):
            adapter = ClaudeAdapter(client_id="test")

            # Mock asyncio.to_thread
            with patch('asyncio.to_thread', side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
                result = await adapter.research(
                    query="What are cloud computing trends?",
                    mode="fast"
                )

                assert result.success is True
                assert len(result.content) > 0
                assert len(result.citations) == 3

                # Validate citation structure
                for citation in result.citations:
                    assert 'title' in citation
                    assert 'url' in citation


@pytest.mark.asyncio
async def test_claude_retry_on_rate_limit():
    """Test Claude adapter retries on rate limit errors."""
    from skill.adapters.claude_adapter import ClaudeAdapter

    mock_client = MagicMock()

    # First call raises rate limit error, second succeeds
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Success")]

    mock_client.messages.create.side_effect = [
        Exception("rate limit exceeded"),
        mock_response
    ]

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('skill.adapters.claude_adapter.anthropic.Anthropic', return_value=mock_client):
            adapter = ClaudeAdapter(client_id="test")
            adapter.base_delay = 0.1  # Speed up test

            with patch('asyncio.to_thread', side_effect=lambda f, *args, **kwargs: f(*args, **kwargs)):
                with patch('asyncio.sleep', return_value=None):  # Skip actual sleep
                    result = await adapter.research(query="test", mode="fast")

                    assert result.success is True
                    assert mock_client.messages.create.call_count == 2


# ==============================================================================
# GEMINI ADAPTER UNIT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_gemini_validate_auth_success():
    """Test Gemini auth validation with valid API key."""
    from skill.adapters.gemini_adapter import GeminiAdapter

    # Mock Gemini client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello"

    mock_client.models.generate_content.return_value = mock_response

    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        with patch('skill.adapters.gemini_adapter.genai.Client', return_value=mock_client):
            adapter = GeminiAdapter(client_id="test")

            result = await adapter.validate_auth()

            assert result is True


@pytest.mark.asyncio
async def test_gemini_research_with_grounding():
    """Test Gemini research with grounding metadata."""
    from skill.adapters.gemini_adapter import GeminiAdapter

    # Mock Gemini response with grounding
    mock_response = MagicMock()
    mock_response.text = "Cloud computing trends include multi-cloud and AI/ML."

    # Mock grounding metadata
    mock_chunk1 = MagicMock()
    mock_chunk1.web.uri = "https://example.com/1"
    mock_chunk1.web.title = "Cloud Trends 2026"

    mock_chunk2 = MagicMock()
    mock_chunk2.web.uri = "https://example.com/2"
    mock_chunk2.web.title = "AI Integration Guide"

    mock_candidate = MagicMock()
    mock_candidate.grounding_metadata.grounding_chunks = [mock_chunk1, mock_chunk2]

    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        with patch('skill.adapters.gemini_adapter.genai.Client', return_value=mock_client):
            adapter = GeminiAdapter(client_id="test")

            result = await adapter.research(
                query="What are cloud trends?",
                mode="fast"
            )

            assert result.success is True
            assert result.sources_imported == 2
            assert len(result.citations) == 2

            # Validate grounding metadata
            assert 'grounded' in result.metadata
            assert result.metadata['grounded'] is True


@pytest.mark.asyncio
async def test_gemini_analysis_with_footnotes():
    """Test Gemini analysis with footnote citations."""
    from skill.adapters.gemini_adapter import GeminiAdapter

    # Mock response with footnote citations
    mock_response = MagicMock()
    mock_response.text = """
Key challenges include:
- Legacy systems [^1]
- Skills gaps [^2]
- Budget constraints [^3]
"""

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        with patch('skill.adapters.gemini_adapter.genai.Client', return_value=mock_client):
            adapter = GeminiAdapter(client_id="test")

            # Add sources first
            await adapter.add_source(
                "https://example.com/1",
                source_type="url",
                title="Legacy Systems Guide"
            )
            await adapter.add_source(
                "https://example.com/2",
                source_type="url",
                title="Skills Gap Report"
            )
            await adapter.add_source(
                "https://example.com/3",
                source_type="url",
                title="Budget Analysis"
            )

            result = await adapter.analyze(prompt="What are the challenges?")

            assert result.success is True
            assert len(result.citations) == 3


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_adapter_timeout_handling():
    """Test adapter handles timeout correctly."""
    from skill.adapters.notebooklm_adapter import NotebookLMAdapter
    import subprocess

    adapter = NotebookLMAdapter(client_id="test", notebook_id="nb_123")

    # Mock subprocess timeout
    with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 10)):
        result = await adapter.research(query="test", mode="fast", timeout=10)

        assert result.success is False
        assert "timeout" in result.error.lower()


@pytest.mark.asyncio
async def test_adapter_cleanup():
    """Test adapter cleanup releases resources."""
    from skill.adapters.claude_adapter import ClaudeAdapter

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('skill.adapters.claude_adapter.anthropic.Anthropic'):
            adapter = ClaudeAdapter(client_id="test")

            # Add some sources
            await adapter.add_source("https://example.com/1", title="Source 1")
            await adapter.add_source("https://example.com/2", title="Source 2")

            sources = await adapter.list_sources()
            assert len(sources) == 2

            # Cleanup
            await adapter.cleanup()

            sources = await adapter.list_sources()
            assert len(sources) == 0, "Sources should be cleared after cleanup"
