#!/usr/bin/env python3
"""
Quick End-to-End Test
=====================
Tests the skill system components work together
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill.adapters.notebooklm_adapter import NotebookLMAdapter
from skill.engine.workflow_engine import ClientConfig, WorkflowEngine
from skill.core.prompt_manager import PromptManager
from skill.core.universal_source_manager import UniversalSourceManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_notebooklm_adapter():
    """Test NotebookLM adapter basic functionality."""
    logger.info("=== Testing NotebookLM Adapter ===")

    adapter = NotebookLMAdapter(client_id="quick_test")

    # Test auth validation
    logger.info("Testing auth validation...")
    auth_valid = await adapter.validate_auth()
    logger.info(f"Auth valid: {auth_valid}")

    # Test citation format
    logger.info(f"Citation format: {adapter.get_citation_format()}")

    # Test capabilities
    capabilities = adapter.get_capabilities()
    logger.info(f"Capabilities: {capabilities}")

    logger.info("✓ NotebookLM adapter basic tests passed\n")
    return True


async def test_prompt_manager():
    """Test prompt manager functionality."""
    logger.info("=== Testing Prompt Manager ===")

    pm = PromptManager(citation_format="notebooklm")

    # Create a simple test template
    test_template = "Company: $name\nIndustry: $industry\nFocus: $subsegments"
    test_file = Path("/tmp/test_prompt.txt")
    test_file.write_text(test_template)

    # Test variable substitution
    result = pm.load_and_substitute(
        str(test_file),
        name="Test Company",
        industry="Technology",
        subsegments="Cloud, AI"
    )

    logger.info(f"Substituted prompt:\n{result}")

    assert "Test Company" in result
    assert "Technology" in result
    assert "Cloud, AI" in result

    logger.info("✓ Prompt manager tests passed\n")
    return True


async def test_source_manager():
    """Test universal source manager."""
    logger.info("=== Testing Universal Source Manager ===")

    from skill.core.universal_source_manager import UniversalSourceManager, Source

    manager = UniversalSourceManager()

    # Add some test sources
    source1 = Source(
        url="https://example.com/page1",
        title="Test Page 1",
        content_hash=manager._hash_url("https://example.com/page1")
    )

    source2 = Source(
        url="https://example.com/page2",
        title="Test Page 2",
        content_hash=manager._hash_url("https://example.com/page2")
    )

    manager.sources[source1.content_hash] = source1
    manager.sources[source2.content_hash] = source2

    # Test deduplication
    duplicate_hash = manager._hash_url("https://example.com/page1/")  # Trailing slash
    assert duplicate_hash == source1.content_hash, "URL normalization failed"

    logger.info(f"Sources tracked: {len(manager.sources)}")
    logger.info(f"Statistics: {manager.get_statistics()}")

    logger.info("✓ Source manager tests passed\n")
    return True


async def test_client_config():
    """Test ClientConfig creation."""
    logger.info("=== Testing ClientConfig ===")

    config = ClientConfig(
        client_id="test_client",
        client_name="Test Corporation",
        folder_spec="/tmp/test_data",
        industry="technology",
        subsegments="cloud, AI",
        persona="Solutions Architect",
        mode="fast",
        output_dir=Path("/tmp/output")
    )

    logger.info(f"Config created: {config.client_name}")
    logger.info(f"Mode: {config.mode}")
    logger.info(f"Persona: {config.persona}")

    logger.info("✓ ClientConfig tests passed\n")
    return True


async def main():
    """Run all quick tests."""
    logger.info("Starting Quick Test Suite\n")

    results = []

    try:
        results.append(await test_notebooklm_adapter())
    except Exception as e:
        logger.error(f"NotebookLM adapter test failed: {e}")
        results.append(False)

    try:
        results.append(await test_prompt_manager())
    except Exception as e:
        logger.error(f"Prompt manager test failed: {e}")
        results.append(False)

    try:
        results.append(await test_source_manager())
    except Exception as e:
        logger.error(f"Source manager test failed: {e}")
        results.append(False)

    try:
        results.append(await test_client_config())
    except Exception as e:
        logger.error(f"ClientConfig test failed: {e}")
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    logger.info("=" * 60)
    logger.info(f"Quick Test Summary: {passed}/{total} tests passed")
    logger.info("=" * 60)

    if passed == total:
        logger.info("✓ All quick tests PASSED!")
        return 0
    else:
        logger.error(f"✗ {total - passed} tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
