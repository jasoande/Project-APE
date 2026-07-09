# Project APE Integration Test Suite

Comprehensive test suite for the multi-platform skill system.

## Overview

This test suite validates:
- **Platform Adapters**: NotebookLM, Claude, Gemini adapters
- **Platform Parity**: Equivalent functionality across all platforms
- **Backward Compatibility**: NotebookLM adapter matches original implementation
- **Workflow Engine**: 5-phase pipeline orchestration
- **End-to-End Workflows**: Complete account planning workflows

## Test Structure

```
tests/
├── __init__.py                      # Package initialization
├── conftest.py                      # Pytest fixtures and configuration
├── test_platform_parity.py          # Platform comparison tests
├── test_backward_compat.py          # NotebookLM compatibility tests
├── test_adapters.py                 # Unit tests with mocks
├── test_workflow_engine.py          # Workflow engine tests
├── fixtures/                        # Test data
│   └── test_client/                 # Sample client data
│       ├── sample_doc_01.txt        # Test document 1
│       └── sample_doc_02.txt        # Test document 2
└── README.md                        # This file
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-asyncio pytest-mock
```

Optional (for integration tests):

- **NotebookLM**: `~/.notebooklm/credentials.json` must exist
- **Claude**: Set `ANTHROPIC_API_KEY` environment variable
- **Gemini**: Set `GEMINI_API_KEY` environment variable

### Run All Tests

```bash
# From project root
pytest tests/

# With verbose output
pytest tests/ -v

# With output capture disabled (see print statements)
pytest tests/ -v -s
```

### Run Specific Test Files

```bash
# Platform parity tests
pytest tests/test_platform_parity.py -v

# Backward compatibility tests
pytest tests/test_backward_compat.py -v

# Adapter unit tests (fast, no API calls)
pytest tests/test_adapters.py -v

# Workflow engine tests
pytest tests/test_workflow_engine.py -v
```

### Run by Marker

```bash
# Only integration tests (requires real APIs)
pytest tests/ -v -m integration

# Only fast tests (no slow integration tests)
pytest tests/ -v -m "not slow"

# Only NotebookLM tests
pytest tests/ -v -m notebooklm

# Only Claude tests
pytest tests/ -v -m claude

# Only Gemini tests
pytest tests/ -v -m gemini
```

### Skip Tests Without API Keys

Tests automatically skip if required credentials are not available:

```bash
# Run all tests, skipping those without credentials
pytest tests/ -v
```

Output example:
```
test_notebooklm_adapter_research ... SKIPPED (NotebookLM credentials not found)
test_claude_adapter_research ... PASSED
test_gemini_adapter_research ... SKIPPED (GEMINI_API_KEY not set)
```

## Test Categories

### 1. Platform Parity Tests (`test_platform_parity.py`)

**Purpose**: Validate all 3 adapters provide equivalent functionality

**Tests**:
- `test_notebooklm_adapter_research` - NotebookLM research capability
- `test_claude_adapter_research` - Claude research with extended thinking
- `test_gemini_adapter_research` - Gemini research with grounding
- `test_platform_parity` - Compare all 3 platforms on same query
- `test_citation_format_differences` - Verify citation formats
- `test_analysis_parity` - Compare analysis across platforms
- `test_source_tracking_parity` - Verify source management

**Expected Results**:
- All platforms complete successfully
- Content length comparable (±50%)
- All produce citations
- Quality scores in acceptable range (7.0-10.0)

**Markers**: `@pytest.mark.integration`, `@pytest.mark.slow`

### 2. Backward Compatibility Tests (`test_backward_compat.py`)

**Purpose**: Ensure NotebookLM adapter maintains compatibility with original `core/source_manager.py`

**Tests**:
- `test_notebooklm_adapter_vs_original` - Compare adapter output with original CLI calls
- `test_citation_extraction_parity` - Validate citation parsing ([1], [2], [3])
- `test_source_count_extraction` - Verify source count parsing
- `test_file_path_extraction` - Validate artifact path extraction
- `test_quality_score_parity` - Quality scores match within ±5%
- `test_source_count_parity` - Source counts match within ±10%
- `test_adapter_interface_compatibility` - Verify all required methods implemented

**Expected Results**:
- Adapter produces equivalent results to original implementation
- Citation format consistent (numeric: [1], [2], [3])
- Quality scores within ±5%
- Source import counts within ±10%

**Markers**: `@pytest.mark.notebooklm`, `@pytest.mark.integration`

### 3. Adapter Unit Tests (`test_adapters.py`)

**Purpose**: Test individual adapter methods with mocked dependencies

**Tests**:
- NotebookLM adapter with mocked subprocess calls
- Claude adapter with mocked Anthropic API
- Gemini adapter with mocked Gemini API
- Error handling and retries
- Timeout behavior
- Cleanup operations

**Expected Results**:
- All methods handle success and failure cases
- Retry logic works correctly
- Timeouts handled gracefully
- Resources cleaned up properly

**Markers**: None (fast unit tests, no API calls)

### 4. Workflow Engine Tests (`test_workflow_engine.py`)

**Purpose**: Test 5-phase pipeline orchestration

**Tests**:
- Workflow initialization
- Status callbacks
- Variable substitution ($name, $industry, etc.)
- Quality score calculation
- Timing configuration (fast vs deep)
- Phase execution
- Error recovery

**Expected Results**:
- Workflow executes all 5 phases
- Status callbacks triggered correctly
- Variables substituted in prompts
- Quality scores calculated correctly
- Errors tracked to specific phase

**Markers**: None (mostly mocked)

## Test Fixtures

### Shared Fixtures (`conftest.py`)

**Adapter Fixtures**:
- `notebooklm_adapter` - Authenticated NotebookLM adapter
- `claude_adapter` - Authenticated Claude adapter
- `gemini_adapter` - Authenticated Gemini adapter

**Configuration Fixtures**:
- `test_client_config` - Minimal ClientConfig for testing
- `sample_research_query` - Sample research prompt
- `sample_analysis_prompt` - Sample analysis prompt
- `expected_citation_formats` - Expected citation formats per platform

**Utility Fixtures**:
- `create_test_pdf` - Factory to create test PDF files
- `assert_quality_score` - Utility to validate quality scores
- `assert_has_citations` - Utility to validate citations

### Test Data (`fixtures/test_client/`)

Sample client documents for testing:

- `sample_doc_01.txt` - Technology industry overview
- `sample_doc_02.txt` - Cloud computing trends

## Writing New Tests

### Example: Add New Adapter Test

```python
import pytest
from skill.adapters.new_adapter import NewAdapter

@pytest.mark.asyncio
@pytest.mark.integration
async def test_new_adapter_research(sample_research_query):
    """Test new adapter research capability."""
    
    # Skip if credentials not available
    if not check_credentials():
        pytest.skip("New adapter credentials not found")
    
    adapter = NewAdapter(client_id="test")
    
    result = await adapter.research(
        query=sample_research_query,
        mode="fast"
    )
    
    assert result.success, f"Research failed: {result.error}"
    assert result.content, "Research content is empty"
    assert len(result.citations) > 0, "No citations found"
    
    await adapter.cleanup()
```

### Example: Add New Workflow Test

```python
@pytest.mark.asyncio
async def test_workflow_custom_phase(test_client_config):
    """Test custom workflow phase."""
    from skill.engine.workflow_engine import WorkflowEngine
    from skill.adapters.base_adapter import BasePlatformAdapter
    
    mock_adapter = AsyncMock(spec=BasePlatformAdapter)
    mock_adapter.get_citation_format.return_value = "test"
    
    engine = WorkflowEngine(
        adapter=mock_adapter,
        config=test_client_config
    )
    
    # Test custom phase logic
    result = await engine._phase_custom()
    
    assert result is not None
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock
      
      - name: Run unit tests
        run: pytest tests/test_adapters.py -v
      
      - name: Run integration tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: pytest tests/ -v -m "not slow"
```

## Troubleshooting

### Tests Skip Due to Missing Credentials

**Issue**: `SKIPPED (NotebookLM credentials not found)`

**Solution**:
```bash
# Authenticate NotebookLM
notebooklm login

# Or copy credentials from another machine
scp ~/.notebooklm/credentials.json user@remote:~/.notebooklm/
```

### Tests Skip Due to Missing API Keys

**Issue**: `SKIPPED (ANTHROPIC_API_KEY not set)`

**Solution**:
```bash
# Set API keys in environment
export ANTHROPIC_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
```

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'skill'`

**Solution**:
```bash
# Run from project root
cd /path/to/Project-APE-dev

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/Project-APE-dev:$PYTHONPATH
```

### Async Warnings

**Issue**: `RuntimeWarning: coroutine was never awaited`

**Solution**: Ensure all async functions use `await` and have `@pytest.mark.asyncio` decorator

```python
@pytest.mark.asyncio  # Required decorator
async def test_async_function():
    result = await some_async_call()  # Must use await
    assert result is not None
```

## Performance

### Test Execution Times

**Fast Tests** (unit tests with mocks):
- `test_adapters.py`: ~5 seconds
- `test_workflow_engine.py`: ~10 seconds
- **Total**: ~15 seconds

**Integration Tests** (real API calls):
- `test_platform_parity.py`: ~5-10 minutes (research queries)
- `test_backward_compat.py`: ~3-5 minutes
- **Total**: ~10-15 minutes

**Optimization**:
- Run unit tests first for fast feedback
- Run integration tests before commits
- Use `-m "not slow"` for quick validation

```bash
# Quick validation (30 seconds)
pytest tests/test_adapters.py tests/test_workflow_engine.py -v

# Full validation (15 minutes)
pytest tests/ -v
```

## Coverage

### Generate Coverage Report

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=skill --cov-report=html

# View report
open htmlcov/index.html
```

### Current Coverage Targets

- **Adapters**: >80% coverage
- **Workflow Engine**: >85% coverage
- **Platform Parity**: >70% coverage (integration-heavy)

## Contributing

When adding new features:

1. **Add unit tests** in `test_adapters.py` or new file
2. **Add integration tests** in `test_platform_parity.py`
3. **Update fixtures** in `conftest.py` if needed
4. **Run full test suite** before submitting PR
5. **Document new tests** in this README

## Questions?

See:
- `CLAUDE.md` - Project architecture and development guide
- `Docs/TROUBLESHOOTING.md` - Common issues and solutions
- `Docs/ARCHITECTURE.md` - System design and components
