#!/bin/bash
#
# Test Script: Deep Mode Source Import Fix
# =========================================
# Validates that research sources are properly imported in deep mode
#
# Usage:
#   ./test-deep-mode-import-fix.sh [client_id]
#
# Example:
#   ./test-deep-mode-import-fix.sh merck
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
CLIENT_ID="${1:-merck}"
MODE="deep"
LOG_FILE="logs/${CLIENT_ID}.log"
STATUS_FILE=".multi_process_status/${CLIENT_ID}.json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deep Mode Source Import Fix - Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Client: $CLIENT_ID"
echo "Mode: $MODE"
echo "Log: $LOG_FILE"
echo "Status: $STATUS_FILE"
echo ""

# Function to check if sources were imported
check_sources_imported() {
    local log_file="$1"
    local min_sources="${2:-10}"

    echo -e "${YELLOW}Checking source import logs...${NC}"

    # Look for "imported X sources" messages
    imported_counts=$(grep -o "imported [0-9]* sources" "$log_file" | grep -o "[0-9]*" || echo "")

    if [ -z "$imported_counts" ]; then
        echo -e "${RED}❌ FAIL: No source import messages found${NC}"
        return 1
    fi

    # Check each import count
    fail=0
    while IFS= read -r count; do
        if [ "$count" -lt "$min_sources" ]; then
            echo -e "${RED}❌ FAIL: Only $count sources imported (expected $min_sources+)${NC}"
            fail=1
        else
            echo -e "${GREEN}✅ PASS: $count sources imported${NC}"
        fi
    done <<< "$imported_counts"

    return $fail
}

# Function to check for timeout errors
check_for_timeouts() {
    local log_file="$1"

    echo -e "${YELLOW}Checking for timeout errors...${NC}"

    if grep -q "timeout" "$log_file" 2>/dev/null; then
        echo -e "${RED}❌ FAIL: Timeout detected in logs${NC}"
        grep "timeout" "$log_file" | head -5
        return 1
    else
        echo -e "${GREEN}✅ PASS: No timeouts detected${NC}"
        return 0
    fi
}

# Function to check for zero imports
check_for_zero_imports() {
    local log_file="$1"

    echo -e "${YELLOW}Checking for zero import errors...${NC}"

    if grep -q "imported 0 sources" "$log_file" 2>/dev/null; then
        echo -e "${RED}❌ FAIL: Zero sources imported detected${NC}"
        grep "imported 0 sources" "$log_file"
        return 1
    else
        echo -e "${GREEN}✅ PASS: No zero import errors${NC}"
        return 0
    fi
}

# Function to check quality score
check_quality_score() {
    local status_file="$1"
    local min_score="${2:-8.0}"

    echo -e "${YELLOW}Checking quality score...${NC}"

    if [ ! -f "$status_file" ]; then
        echo -e "${RED}❌ FAIL: Status file not found${NC}"
        return 1
    fi

    quality_score=$(jq -r '.quality_score // 0' "$status_file")

    if (( $(echo "$quality_score < $min_score" | bc -l) )); then
        echo -e "${RED}❌ FAIL: Quality score $quality_score is below $min_score${NC}"
        return 1
    else
        echo -e "${GREEN}✅ PASS: Quality score $quality_score meets threshold${NC}"
        return 0
    fi
}

# Clean up old test artifacts
echo -e "${YELLOW}Cleaning up old test files...${NC}"
rm -f "$LOG_FILE" 2>/dev/null || true
rm -f "$STATUS_FILE" 2>/dev/null || true
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Run the pipeline
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Deep Mode Pipeline...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ -d "$HOME/.project-ape-venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source "$HOME/.project-ape-venv/bin/activate"
else
    echo -e "${RED}❌ Virtual environment not found at $HOME/.project-ape-venv${NC}"
    echo "Please run: python3 launch-project-ape.py"
    exit 1
fi

# Run pipeline with deep mode
echo ""
echo -e "${YELLOW}Starting pipeline (this may take 45-60 minutes)...${NC}"
echo "Tail logs with: tail -f $LOG_FILE"
echo ""

python3 main.py --mode "$MODE" --clients "$CLIENT_ID" --no-dashboard

# Wait for completion
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pipeline Complete - Running Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Run validation tests
TESTS_PASSED=0
TESTS_FAILED=0

echo "Test 1: Source Import Validation"
if check_sources_imported "$LOG_FILE" 30; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

echo "Test 2: Timeout Detection"
if check_for_timeouts "$LOG_FILE"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

echo "Test 3: Zero Import Detection"
if check_for_zero_imports "$LOG_FILE"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

echo "Test 4: Quality Score Threshold"
if check_quality_score "$STATUS_FILE" 8.0; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "Deep mode source import fix validated successfully!"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Review logs at: $LOG_FILE"
    echo "Review status at: $STATUS_FILE"
    exit 1
fi
