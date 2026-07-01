#!/bin/bash
################################################################################
# Project APE - macOS Command Testing Script
# Tests all macOS-specific commands and verifies functionality
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results file
RESULTS_FILE="test-results-$(date +%Y%m%d-%H%M%S).txt"

echo "======================================================================="
echo "Project APE - macOS Command Testing"
echo "======================================================================="
echo ""
echo "Test Results will be saved to: $RESULTS_FILE"
echo ""

# Helper functions
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
    echo "[TEST] $1" >> "$RESULTS_FILE"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    echo "[PASS] $1" >> "$RESULTS_FILE"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    echo "[FAIL] $1" >> "$RESULTS_FILE"
    ((FAILED_TESTS++))
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[WARN] $1" >> "$RESULTS_FILE"
}

run_test() {
    ((TOTAL_TESTS++))
    print_test "$1"
}

# Initialize results file
echo "Project APE - macOS Testing Results" > "$RESULTS_FILE"
echo "Test Date: $(date)" >> "$RESULTS_FILE"
echo "Platform: $(uname -s)" >> "$RESULTS_FILE"
echo "Python: $(python3 --version)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

################################################################################
# TEST CATEGORY 1: File Permissions
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 1: File Permissions"
echo "======================================================================="
echo ""

run_test "Launcher scripts are executable"
if [[ -x launch-project-ape.command ]] && [[ -x launch-project-ape.sh ]] && [[ -x launch-project-ape.py ]]; then
    print_pass "All launcher scripts are executable"
else
    print_fail "Some launcher scripts are not executable"
    ls -la launch-project-ape.* >> "$RESULTS_FILE"
fi

run_test "Setup scripts are executable"
if [[ -x setup-environment.sh ]] && [[ -x setup-credentials.sh ]] && [[ -x setup-oauth-drive.py ]]; then
    print_pass "All setup scripts are executable"
else
    print_fail "Some setup scripts are not executable"
    ls -la setup*.sh setup*.py >> "$RESULTS_FILE"
fi

run_test "Workflow scripts are executable"
if [[ -x run-workflow.sh ]] && [[ -x launch_ape.sh ]]; then
    print_pass "All workflow scripts are executable"
else
    print_fail "Some workflow scripts are not executable"
    ls -la run-workflow.sh launch_ape.sh >> "$RESULTS_FILE"
fi

################################################################################
# TEST CATEGORY 2: Python Environment
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 2: Python Environment"
echo "======================================================================="
echo ""

run_test "Python version is 3.10 or higher"
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $PYTHON_MAJOR -ge 3 ]] && [[ $PYTHON_MINOR -ge 10 ]]; then
    print_pass "Python version $PYTHON_VERSION is compatible"
else
    print_fail "Python version $PYTHON_VERSION is too old (need 3.10+)"
fi

run_test "Virtual environment exists"
if [[ -d ~/.project-ape-venv ]]; then
    print_pass "Virtual environment found at ~/.project-ape-venv"
else
    print_fail "Virtual environment not found at ~/.project-ape-venv"
fi

run_test "Virtual environment Python version"
source ~/.project-ape-venv/bin/activate
VENV_PYTHON_VERSION=$(python3 --version | awk '{print $2}')
if [[ ! -z "$VENV_PYTHON_VERSION" ]]; then
    print_pass "Venv Python version: $VENV_PYTHON_VERSION"
else
    print_fail "Could not determine venv Python version"
fi

################################################################################
# TEST CATEGORY 3: Python Dependencies
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 3: Python Dependencies"
echo "======================================================================="
echo ""

run_test "Flask is installed"
if pip list | grep -qi "flask"; then
    FLASK_VERSION=$(pip list | grep -i flask | awk '{print $2}')
    print_pass "Flask $FLASK_VERSION is installed"
else
    print_fail "Flask is not installed"
fi

run_test "Google API clients are installed"
if pip list | grep -qi "google-api-python-client"; then
    print_pass "Google API Python client is installed"
else
    print_fail "Google API Python client is not installed"
fi

run_test "NotebookLM CLI is installed"
if pip list | grep -qi "notebooklm"; then
    NB_VERSION=$(pip list | grep -i notebooklm | awk '{print $2}')
    print_pass "NotebookLM CLI $NB_VERSION is installed"
else
    print_fail "NotebookLM CLI is not installed"
fi

run_test "Google Gemini AI is installed"
if pip list | grep -qi "google-genai"; then
    GENAI_VERSION=$(pip list | grep -i google-genai | awk '{print $2}')
    print_pass "Google Gemini AI $GENAI_VERSION is installed"
else
    print_warn "Google Gemini AI is not installed (optional)"
fi

run_test "Python-dotenv is installed"
if pip list | grep -qi "python-dotenv"; then
    print_pass "python-dotenv is installed"
else
    print_fail "python-dotenv is not installed"
fi

################################################################################
# TEST CATEGORY 4: Python Module Imports
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 4: Python Module Imports"
echo "======================================================================="
echo ""

run_test "Import core.client_pipeline"
if python3 -c "import core.client_pipeline" 2>/dev/null; then
    print_pass "core.client_pipeline imports successfully"
else
    print_fail "core.client_pipeline import failed"
fi

run_test "Import core.drive_manager"
if python3 -c "import core.drive_manager" 2>/dev/null; then
    print_pass "core.drive_manager imports successfully"
else
    print_fail "core.drive_manager import failed"
fi

run_test "Import core.notebook_manager"
if python3 -c "import core.notebook_manager" 2>/dev/null; then
    print_pass "core.notebook_manager imports successfully"
else
    print_fail "core.notebook_manager import failed"
fi

run_test "Import core.source_manager"
if python3 -c "import core.source_manager" 2>/dev/null; then
    print_pass "core.source_manager imports successfully"
else
    print_fail "core.source_manager import failed"
fi

run_test "Import core.gemini_agent"
if python3 -c "import core.gemini_agent" 2>/dev/null; then
    print_pass "core.gemini_agent imports successfully"
else
    print_warn "core.gemini_agent import failed (optional - requires google-genai)"
fi

run_test "Import core.quality_scorer"
if python3 -c "import core.quality_scorer" 2>/dev/null; then
    print_pass "core.quality_scorer imports successfully"
else
    print_fail "core.quality_scorer import failed"
fi

run_test "Import dashboard.server"
if python3 -c "import dashboard.server" 2>/dev/null; then
    print_pass "dashboard.server imports successfully"
else
    print_fail "dashboard.server import failed"
fi

run_test "Import dashboard.config_generator"
if python3 -c "import dashboard.config_generator" 2>/dev/null; then
    print_pass "dashboard.config_generator imports successfully"
else
    print_fail "dashboard.config_generator import failed"
fi

run_test "Import dashboard.config_parser"
if python3 -c "import dashboard.config_parser" 2>/dev/null; then
    print_pass "dashboard.config_parser imports successfully"
else
    print_fail "dashboard.config_parser import failed"
fi

################################################################################
# TEST CATEGORY 5: Main Entry Point
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 5: Main Entry Point"
echo "======================================================================="
echo ""

run_test "main.py --help executes"
if python3 main.py --help > /dev/null 2>&1; then
    print_pass "main.py --help works"
else
    print_fail "main.py --help failed"
fi

run_test "main.py shows usage"
if python3 main.py --help | grep -q "usage:"; then
    print_pass "main.py displays usage information"
else
    print_fail "main.py does not display usage information"
fi

run_test "main.py supports --mode option"
if python3 main.py --help | grep -q "\-\-mode"; then
    print_pass "main.py supports --mode option"
else
    print_fail "main.py missing --mode option"
fi

run_test "main.py supports --clients option"
if python3 main.py --help | grep -q "\-\-clients"; then
    print_pass "main.py supports --clients option"
else
    print_fail "main.py missing --clients option"
fi

################################################################################
# TEST CATEGORY 6: File Structure
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 6: File Structure"
echo "======================================================================="
echo ""

run_test "Core directory exists"
if [[ -d core ]]; then
    print_pass "core/ directory exists"
else
    print_fail "core/ directory missing"
fi

run_test "Dashboard directory exists"
if [[ -d dashboard ]]; then
    print_pass "dashboard/ directory exists"
else
    print_fail "dashboard/ directory missing"
fi

run_test "Logs directory exists or can be created"
if [[ -d logs ]] || mkdir -p logs 2>/dev/null; then
    print_pass "logs/ directory exists or was created"
else
    print_fail "logs/ directory cannot be created"
fi

run_test "Documentation exists"
if [[ -f README.md ]] && [[ -f QUICK_START.md ]]; then
    print_pass "Main documentation files exist"
else
    print_fail "Missing main documentation files"
fi

run_test "vars.py exists or can be created"
if [[ -f vars.py ]]; then
    print_pass "vars.py configuration file exists"
else
    print_warn "vars.py does not exist (needs to be created from example-vars.py)"
fi

################################################################################
# TEST CATEGORY 7: Launcher Script Syntax
################################################################################
echo ""
echo "======================================================================="
echo "TEST CATEGORY 7: Launcher Script Syntax"
echo "======================================================================="
echo ""

run_test "launch-project-ape.command has correct shebang"
if head -1 launch-project-ape.command | grep -q "^#!/bin/bash"; then
    print_pass "launch-project-ape.command has correct shebang"
else
    print_fail "launch-project-ape.command has incorrect shebang"
fi

run_test "launch-project-ape.sh has correct shebang"
if head -1 launch-project-ape.sh | grep -q "^#!/bin/bash"; then
    print_pass "launch-project-ape.sh has correct shebang"
else
    print_fail "launch-project-ape.sh has incorrect shebang"
fi

run_test "launch-project-ape.py has correct shebang"
if head -1 launch-project-ape.py | grep -q "^#!/usr/bin/env python3"; then
    print_pass "launch-project-ape.py has correct shebang"
else
    print_fail "launch-project-ape.py has incorrect shebang"
fi

run_test "launch-project-ape.py is valid Python"
if python3 -m py_compile launch-project-ape.py 2>/dev/null; then
    print_pass "launch-project-ape.py is valid Python syntax"
else
    print_fail "launch-project-ape.py has Python syntax errors"
fi

################################################################################
# SUMMARY
################################################################################
echo ""
echo "======================================================================="
echo "TEST SUMMARY"
echo "======================================================================="
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo "Passed:      $PASSED_TESTS ($(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")%)"
echo "Failed:      $FAILED_TESTS ($(awk "BEGIN {printf \"%.1f\", ($FAILED_TESTS/$TOTAL_TESTS)*100}")%)"
echo ""

# Write summary to file
echo "" >> "$RESULTS_FILE"
echo "=======================================================================" >> "$RESULTS_FILE"
echo "TEST SUMMARY" >> "$RESULTS_FILE"
echo "=======================================================================" >> "$RESULTS_FILE"
echo "Total Tests: $TOTAL_TESTS" >> "$RESULTS_FILE"
echo "Passed:      $PASSED_TESTS" >> "$RESULTS_FILE"
echo "Failed:      $FAILED_TESTS" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo "✅ All tests passed!" >> "$RESULTS_FILE"
    exit 0
else
    echo -e "${RED}❌ $FAILED_TESTS test(s) failed${NC}"
    echo "❌ $FAILED_TESTS test(s) failed" >> "$RESULTS_FILE"
    exit 1
fi
