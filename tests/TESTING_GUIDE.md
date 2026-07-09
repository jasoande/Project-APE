# Quick Testing Guide

## Installation

First, install test dependencies:

```bash
pip install pytest pytest-asyncio pytest-mock
```

Optional for coverage:

```bash
pip install pytest-cov
```

## Quick Start

```bash
# From project root
cd /Users/jasona/test/Project-APE-dev

# Run all tests (uses test runner script)
./tests/run_tests.sh

# Or use pytest directly
pytest tests/ -v
```

## Common Test Scenarios

### 1. Fast Validation (30 seconds)

Run unit tests only (no API calls):

```bash
./tests/run_tests.sh unit
```

### 2. Full Integration Tests (10-15 minutes)

Requires API credentials:

```bash
# Set API keys
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Authenticate NotebookLM
notebooklm login

# Run all tests
./tests/run_tests.sh all
```

### 3. Test Specific Platform

```bash
# Test NotebookLM only
./tests/run_tests.sh notebooklm

# Test Claude only
./tests/run_tests.sh claude

# Test Gemini only
./tests/run_tests.sh gemini
```

### 4. Platform Parity Tests

Compare all 3 platforms:

```bash
./tests/run_tests.sh parity
```

### 5. Backward Compatibility

Ensure NotebookLM adapter matches original:

```bash
./tests/run_tests.sh compat
```

## Test Structure

```
tests/
├── test_platform_parity.py     # Compare all 3 platforms
├── test_backward_compat.py     # NotebookLM compatibility
├── test_adapters.py            # Unit tests (mocked)
├── test_workflow_engine.py     # Workflow orchestration
├── conftest.py                 # Pytest fixtures
├── fixtures/                   # Test data
│   └── test_client/
│       ├── sample_doc_01.txt
│       └── sample_doc_02.txt
└── README.md                   # Full documentation
```

## Test Markers

Filter tests by marker:

```bash
# Only integration tests
pytest tests/ -v -m integration

# Exclude slow tests
pytest tests/ -v -m "not slow"

# Only NotebookLM tests
pytest tests/ -v -m notebooklm

# Only Claude tests
pytest tests/ -v -m claude

# Only Gemini tests
pytest tests/ -v -m gemini
```

## Expected Results

### Unit Tests (test_adapters.py, test_workflow_engine.py)

- **Execution time**: ~15 seconds
- **No API calls**: All external calls mocked
- **Expected failures**: 0
- **Expected skips**: 0

### Integration Tests (test_platform_parity.py, test_backward_compat.py)

- **Execution time**: ~10-15 minutes
- **Requires APIs**: NotebookLM, Claude, Gemini
- **Expected failures**: 0
- **Expected skips**: Tests skip if credentials missing

Example output:

```
tests/test_platform_parity.py::test_notebooklm_adapter_research PASSED
tests/test_platform_parity.py::test_claude_adapter_research PASSED
tests/test_platform_parity.py::test_gemini_adapter_research SKIPPED (GEMINI_API_KEY not set)
tests/test_platform_parity.py::test_platform_parity SKIPPED (Gemini not available)
```

## Troubleshooting

### Missing Credentials

If tests skip due to missing credentials:

```bash
# NotebookLM
notebooklm login

# Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Gemini
export GEMINI_API_KEY="AI..."
```

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Ensure you're in project root
cd /Users/jasona/test/Project-APE-dev

# Check PYTHONPATH
export PYTHONPATH=/Users/jasona/test/Project-APE-dev:$PYTHONPATH
```

### Async Warnings

If you see `RuntimeWarning: coroutine was never awaited`:

- Ensure all async functions have `@pytest.mark.asyncio` decorator
- Ensure all async calls use `await`

## Coverage Report

Generate HTML coverage report:

```bash
./tests/run_tests.sh coverage

# View report
open htmlcov/index.html
```

## CI/CD Integration

For GitHub Actions or similar:

```yaml
- name: Run Tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    pip install pytest pytest-asyncio pytest-mock
    pytest tests/ -v -m "not slow"
```

## Next Steps

After running tests successfully:

1. Review coverage report
2. Add tests for new features
3. Update fixtures for new test scenarios
4. Document any new test patterns

See `tests/README.md` for comprehensive documentation.
