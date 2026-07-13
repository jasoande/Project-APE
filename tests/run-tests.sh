#!/bin/bash
#
# Project-APE Test Runner
# Runs automated test suite with coverage reporting
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Project-APE Automated Test Suite${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}Installing test dependencies...${NC}"
pip install -q -U pytest pytest-cov pytest-mock 2>/dev/null || true
echo -e "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Parse command line arguments
COVERAGE=true
VERBOSE=""
TEST_PATH="tests/"
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --quick)
            # Run only fast unit tests
            TEST_PATH="tests/test_retry_strategy.py tests/test_checkpoint_manager.py tests/test_config_generator.py tests/test_config_parser.py tests/test_flask_secret_persistence.py tests/test_credential_permissions.py"
            shift
            ;;
        --security)
            # Run only security tests
            TEST_PATH="tests/test_flask_secret_persistence.py tests/test_credential_permissions.py tests/test_csrf_protection.py tests/test_server_security.py"
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo ""

if [ "$COVERAGE" = true ]; then
    python -m pytest $TEST_PATH $VERBOSE \
        --cov=core \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html \
        --no-cov-on-fail \
        -W ignore::coverage.exceptions.CoverageWarning

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ All tests passed!${NC}"
        echo ""
        echo -e "${BLUE}Coverage report generated: htmlcov/index.html${NC}"
        echo -e "${BLUE}To view: open htmlcov/index.html${NC}"
    else
        echo ""
        echo -e "${RED}❌ Some tests failed (exit code: $EXIT_CODE)${NC}"
    fi
else
    python -m pytest $TEST_PATH $VERBOSE
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ All tests passed!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Some tests failed (exit code: $EXIT_CODE)${NC}"
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit $EXIT_CODE
