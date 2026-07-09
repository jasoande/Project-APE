#!/bin/bash
# Test Runner Script for Project APE Integration Tests
# =====================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Project APE Integration Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}ERROR: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-asyncio pytest-mock"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d ' ' -f 2)
echo "Python version: $python_version"

# Check API credentials
echo ""
echo "Checking credentials..."

has_notebooklm=false
has_claude=false
has_gemini=false

if [ -f "$HOME/.notebooklm/credentials.json" ]; then
    echo -e "${GREEN}✓${NC} NotebookLM credentials found"
    has_notebooklm=true
else
    echo -e "${YELLOW}⚠${NC} NotebookLM credentials not found (tests will skip)"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY set"
    has_claude=true
else
    echo -e "${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set (tests will skip)"
fi

if [ -n "$GEMINI_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} GEMINI_API_KEY set"
    has_gemini=true
else
    echo -e "${YELLOW}⚠${NC} GEMINI_API_KEY not set (tests will skip)"
fi

echo ""

# Parse command line arguments
TEST_SUITE="${1:-all}"
VERBOSE="${2:--v}"

case "$TEST_SUITE" in
    "unit")
        echo "Running unit tests (fast, mocked)..."
        pytest tests/test_adapters.py tests/test_workflow_engine.py $VERBOSE
        ;;

    "integration")
        echo "Running integration tests (requires APIs)..."
        pytest tests/test_platform_parity.py tests/test_backward_compat.py $VERBOSE -m integration
        ;;

    "fast")
        echo "Running fast tests only (no slow tests)..."
        pytest tests/ $VERBOSE -m "not slow"
        ;;

    "notebooklm")
        if [ "$has_notebooklm" = false ]; then
            echo -e "${RED}ERROR: NotebookLM credentials not found${NC}"
            exit 1
        fi
        echo "Running NotebookLM tests..."
        pytest tests/ $VERBOSE -m notebooklm
        ;;

    "claude")
        if [ "$has_claude" = false ]; then
            echo -e "${RED}ERROR: ANTHROPIC_API_KEY not set${NC}"
            exit 1
        fi
        echo "Running Claude tests..."
        pytest tests/ $VERBOSE -m claude
        ;;

    "gemini")
        if [ "$has_gemini" = false ]; then
            echo -e "${RED}ERROR: GEMINI_API_KEY not set${NC}"
            exit 1
        fi
        echo "Running Gemini tests..."
        pytest tests/ $VERBOSE -m gemini
        ;;

    "parity")
        echo "Running platform parity tests..."
        pytest tests/test_platform_parity.py $VERBOSE
        ;;

    "compat")
        echo "Running backward compatibility tests..."
        pytest tests/test_backward_compat.py $VERBOSE
        ;;

    "all")
        echo "Running all tests..."
        pytest tests/ $VERBOSE
        ;;

    "coverage")
        echo "Running tests with coverage..."
        if ! command -v pytest-cov &> /dev/null; then
            echo -e "${YELLOW}⚠${NC} pytest-cov not installed, running without coverage"
            pytest tests/ $VERBOSE
        else
            pytest tests/ $VERBOSE --cov=skill --cov-report=html --cov-report=term-missing
            echo ""
            echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        fi
        ;;

    "help"|"-h"|"--help")
        echo "Usage: ./run_tests.sh [suite] [verbose]"
        echo ""
        echo "Test suites:"
        echo "  unit         - Fast unit tests with mocks (no API calls)"
        echo "  integration  - Integration tests with real APIs"
        echo "  fast         - All fast tests (excludes slow tests)"
        echo "  notebooklm   - NotebookLM adapter tests only"
        echo "  claude       - Claude adapter tests only"
        echo "  gemini       - Gemini adapter tests only"
        echo "  parity       - Platform parity comparison tests"
        echo "  compat       - Backward compatibility tests"
        echo "  all          - All tests (default)"
        echo "  coverage     - All tests with coverage report"
        echo ""
        echo "Verbose options:"
        echo "  -v           - Verbose (default)"
        echo "  -vv          - Very verbose"
        echo "  -q           - Quiet"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests"
        echo "  ./run_tests.sh unit               # Run unit tests only"
        echo "  ./run_tests.sh integration -vv    # Run integration tests, very verbose"
        echo "  ./run_tests.sh fast               # Run fast tests only"
        echo "  ./run_tests.sh coverage           # Run with coverage report"
        exit 0
        ;;

    *)
        echo -e "${RED}ERROR: Unknown test suite: $TEST_SUITE${NC}"
        echo "Run './run_tests.sh help' for usage"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}Test run complete!${NC}"
echo "=========================================="
