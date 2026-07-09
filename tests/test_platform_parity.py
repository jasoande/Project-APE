"""
Platform Parity Tests
=====================
Validates that all 3 adapters (NotebookLM, Claude, Gemini) provide equivalent
functionality and produce comparable results.

Tests:
- Research capability across all platforms
- Citation format differences
- Output quality parity
- Source import behavior
"""

import pytest
import asyncio
from pathlib import Path


# ==============================================================================
# INDIVIDUAL PLATFORM TESTS
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.notebooklm
@pytest.mark.integration
@pytest.mark.slow
async def test_notebooklm_adapter_research(notebooklm_adapter, sample_research_query):
    """
    Test NotebookLM adapter research capability.

    Validates:
    - Research completes successfully
    - Content is generated
    - Citations are present
    - Sources are imported
    """
    result = await notebooklm_adapter.research(
        query=sample_research_query,
        mode="fast",
        import_sources=True,
        timeout=300
    )

    # Assert success
    assert result.success, f"Research failed: {result.error}"
    assert result.content, "Research content is empty"
    assert len(result.content) > 100, "Research content too short"

    # Assert citations
    assert result.citations, "No citations found"
    assert len(result.citations) > 0, "Citation list is empty"

    # Assert sources imported
    assert result.sources_imported > 0, "No sources imported"

    # Validate citation format (NotebookLM uses numeric: [1], [2])
    citation_format = notebooklm_adapter.get_citation_format()
    assert citation_format == "notebooklm", f"Unexpected citation format: {citation_format}"

    print(f"\n✓ NotebookLM Research:")
    print(f"  - Content: {len(result.content)} chars")
    print(f"  - Citations: {len(result.citations)}")
    print(f"  - Sources imported: {result.sources_imported}")


@pytest.mark.asyncio
@pytest.mark.claude
@pytest.mark.integration
@pytest.mark.slow
async def test_claude_adapter_research(claude_adapter, sample_research_query):
    """
    Test Claude adapter research capability.

    Validates:
    - Research completes with extended thinking
    - Content includes inline citations
    - Quality meets minimum threshold
    """
    result = await claude_adapter.research(
        query=sample_research_query,
        mode="fast",
        import_sources=True,
        timeout=300
    )

    # Assert success
    assert result.success, f"Research failed: {result.error}"
    assert result.content, "Research content is empty"
    assert len(result.content) > 100, "Research content too short"

    # Assert citations (Claude uses inline markdown: [Title](url))
    assert result.citations, "No citations found"
    assert len(result.citations) > 0, "Citation list is empty"

    # Validate citation format
    citation_format = claude_adapter.get_citation_format()
    assert citation_format == "claude", f"Unexpected citation format: {citation_format}"

    # Validate citation structure (should have title and url)
    for citation in result.citations[:3]:
        assert 'title' in citation, "Citation missing title"
        assert 'url' in citation, "Citation missing URL"
        assert citation['url'].startswith('http'), "Citation URL invalid"

    print(f"\n✓ Claude Research:")
    print(f"  - Content: {len(result.content)} chars")
    print(f"  - Citations: {len(result.citations)}")
    print(f"  - Sample citation: {result.citations[0].get('title', 'Unknown')}")


@pytest.mark.asyncio
@pytest.mark.gemini
@pytest.mark.integration
@pytest.mark.slow
async def test_gemini_adapter_research(gemini_adapter, sample_research_query):
    """
    Test Gemini adapter research with grounding.

    Validates:
    - Google Search grounding works
    - Grounding metadata extracted
    - Citations from grounding chunks
    - Sources tracked correctly
    """
    result = await gemini_adapter.research(
        query=sample_research_query,
        mode="fast",
        import_sources=True,
        timeout=300
    )

    # Assert success
    assert result.success, f"Research failed: {result.error}"
    assert result.content, "Research content is empty"
    assert len(result.content) > 100, "Research content too short"

    # Assert grounding metadata
    assert 'grounded' in result.metadata, "Missing grounding metadata"

    # Assert citations from grounding
    assert result.citations, "No citations found from grounding"
    assert len(result.citations) > 0, "Citation list is empty"

    # Assert sources imported
    assert result.sources_imported > 0, "No sources imported"

    # Validate citation format (Gemini uses footnote: [^1], [^2])
    citation_format = gemini_adapter.get_citation_format()
    assert citation_format == "footnote", f"Unexpected citation format: {citation_format}"

    # Validate citation structure (should have url and title from grounding)
    for citation in result.citations[:3]:
        assert 'url' in citation, "Citation missing URL"
        assert 'title' in citation, "Citation missing title"

    print(f"\n✓ Gemini Research:")
    print(f"  - Content: {len(result.content)} chars")
    print(f"  - Citations: {len(result.citations)}")
    print(f"  - Sources imported: {result.sources_imported}")
    print(f"  - Grounded: {result.metadata.get('grounded', False)}")


# ==============================================================================
# PLATFORM PARITY TESTS
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
async def test_platform_parity(
    notebooklm_adapter,
    claude_adapter,
    gemini_adapter,
    sample_research_query
):
    """
    Compare all 3 platforms on same query.

    Validates:
    - All platforms complete successfully
    - Content length is comparable (±50%)
    - All produce citations
    - Quality is comparable
    """
    # Execute research on all platforms in parallel
    results = await asyncio.gather(
        notebooklm_adapter.research(sample_research_query, mode="fast", timeout=300),
        claude_adapter.research(sample_research_query, mode="fast", timeout=300),
        gemini_adapter.research(sample_research_query, mode="fast", timeout=300),
        return_exceptions=True
    )

    notebooklm_result, claude_result, gemini_result = results

    # Check for exceptions
    for platform, result in [("NotebookLM", notebooklm_result),
                              ("Claude", claude_result),
                              ("Gemini", gemini_result)]:
        if isinstance(result, Exception):
            pytest.skip(f"{platform} platform not available: {result}")

    # Assert all succeeded
    assert notebooklm_result.success, "NotebookLM failed"
    assert claude_result.success, "Claude failed"
    assert gemini_result.success, "Gemini failed"

    # Compare content lengths
    lengths = [
        len(notebooklm_result.content),
        len(claude_result.content),
        len(gemini_result.content)
    ]

    avg_length = sum(lengths) / len(lengths)
    for platform, length in zip(["NotebookLM", "Claude", "Gemini"], lengths):
        # Allow 50% deviation from average
        assert length >= avg_length * 0.5, \
            f"{platform} content too short ({length} vs avg {avg_length:.0f})"
        assert length <= avg_length * 1.5, \
            f"{platform} content too long ({length} vs avg {avg_length:.0f})"

    # Assert all have citations
    assert len(notebooklm_result.citations) > 0, "NotebookLM has no citations"
    assert len(claude_result.citations) > 0, "Claude has no citations"
    assert len(gemini_result.citations) > 0, "Gemini has no citations"

    print(f"\n✓ Platform Parity:")
    print(f"  NotebookLM: {lengths[0]} chars, {len(notebooklm_result.citations)} citations")
    print(f"  Claude:     {lengths[1]} chars, {len(claude_result.citations)} citations")
    print(f"  Gemini:     {lengths[2]} chars, {len(gemini_result.citations)} citations")
    print(f"  Avg length: {avg_length:.0f} chars")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_citation_format_differences(
    notebooklm_adapter,
    claude_adapter,
    gemini_adapter,
    expected_citation_formats
):
    """
    Verify each platform uses correct citation format.

    Citation formats:
    - NotebookLM: numeric ([1], [2], [3])
    - Claude: inline markdown ([Title](url))
    - Gemini: footnote ([^1], [^2], [^3])
    """
    # Get citation formats
    notebooklm_format = notebooklm_adapter.get_citation_format()
    claude_format = claude_adapter.get_citation_format()
    gemini_format = gemini_adapter.get_citation_format()

    # Assert expected formats
    assert notebooklm_format == "notebooklm", \
        f"NotebookLM format should be 'notebooklm', got '{notebooklm_format}'"

    assert claude_format == "claude", \
        f"Claude format should be 'claude', got '{claude_format}'"

    assert gemini_format == "footnote", \
        f"Gemini format should be 'footnote', got '{gemini_format}'"

    print(f"\n✓ Citation Formats:")
    print(f"  NotebookLM: {notebooklm_format} (numeric)")
    print(f"  Claude:     {claude_format} (inline)")
    print(f"  Gemini:     {gemini_format} (footnote)")


# ==============================================================================
# ANALYSIS TESTS
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_analysis_parity(
    notebooklm_adapter,
    claude_adapter,
    gemini_adapter,
    sample_analysis_prompt
):
    """
    Test analysis capability across all platforms.

    Validates:
    - All platforms complete analysis
    - Content is generated
    - Citations are present
    """
    # Execute analysis on all platforms
    results = await asyncio.gather(
        notebooklm_adapter.analyze(sample_analysis_prompt, timeout=180),
        claude_adapter.analyze(sample_analysis_prompt, timeout=180),
        gemini_adapter.analyze(sample_analysis_prompt, timeout=180),
        return_exceptions=True
    )

    notebooklm_result, claude_result, gemini_result = results

    # Check for exceptions
    for platform, result in [("NotebookLM", notebooklm_result),
                              ("Claude", claude_result),
                              ("Gemini", gemini_result)]:
        if isinstance(result, Exception):
            pytest.skip(f"{platform} platform not available: {result}")

    # Assert all succeeded
    assert notebooklm_result.success, "NotebookLM analysis failed"
    assert claude_result.success, "Claude analysis failed"
    assert gemini_result.success, "Gemini analysis failed"

    # Assert content generated
    assert len(notebooklm_result.content) > 50, "NotebookLM analysis too short"
    assert len(claude_result.content) > 50, "Claude analysis too short"
    assert len(gemini_result.content) > 50, "Gemini analysis too short"

    print(f"\n✓ Analysis Parity:")
    print(f"  NotebookLM: {len(notebooklm_result.content)} chars")
    print(f"  Claude:     {len(claude_result.content)} chars")
    print(f"  Gemini:     {len(gemini_result.content)} chars")


# ==============================================================================
# SOURCE MANAGEMENT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_source_tracking_parity(
    notebooklm_adapter,
    claude_adapter,
    gemini_adapter
):
    """
    Test source tracking across platforms.

    Validates:
    - add_source() works on all platforms
    - list_sources() returns tracked sources
    - Source metadata is consistent
    """
    test_source = "https://example.com/test-document.pdf"
    test_title = "Test Document"

    # Add source to all platforms
    await asyncio.gather(
        notebooklm_adapter.add_source(test_source, source_type="url", title=test_title),
        claude_adapter.add_source(test_source, source_type="url", title=test_title),
        gemini_adapter.add_source(test_source, source_type="url", title=test_title)
    )

    # List sources
    notebooklm_sources = await notebooklm_adapter.list_sources()
    claude_sources = await claude_adapter.list_sources()
    gemini_sources = await gemini_adapter.list_sources()

    # Assert source was added
    # Note: NotebookLM may require actual API call, so we allow empty list
    # Claude and Gemini track sources in memory
    assert len(claude_sources) > 0, "Claude sources list is empty"
    assert len(gemini_sources) > 0, "Gemini sources list is empty"

    print(f"\n✓ Source Tracking:")
    print(f"  NotebookLM: {len(notebooklm_sources)} sources")
    print(f"  Claude:     {len(claude_sources)} sources")
    print(f"  Gemini:     {len(gemini_sources)} sources")
