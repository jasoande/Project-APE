#!/bin/bash
################################################################################
# Phase 3 Integration Test Script
# Tests the complete unified launcher workflow
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED=$((FAILED + 1))
}

echo "════════════════════════════════════════════════════════════════"
echo "  Phase 3 Integration Tests"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd "$SCRIPT_DIR"

################################################################################
# Test 1: Workflow Detector
################################################################################

log_test "Testing workflow detector with current vars.py"

if python3 workflow_detector.py > /dev/null 2>&1; then
    log_pass "Workflow detector runs without errors"
else
    log_fail "Workflow detector failed"
fi

# Test JSON output
if python3 workflow_detector.py --json | python3 -m json.tool > /dev/null 2>&1; then
    log_pass "Workflow detector JSON output is valid"
else
    log_fail "Workflow detector JSON output is invalid"
fi

# Check required fields in JSON output
JSON_OUTPUT=$(python3 workflow_detector.py --json)
if echo "$JSON_OUTPUT" | grep -q '"mode"' && \
   echo "$JSON_OUTPUT" | grep -q '"clients"' && \
   echo "$JSON_OUTPUT" | grep -q '"command"'; then
    log_pass "Workflow detector includes required fields"
else
    log_fail "Workflow detector missing required fields"
fi

################################################################################
# Test 2: Launcher Script
################################################################################

log_test "Testing unified launcher script"

if [ -f "launch-project-ape.command" ]; then
    log_pass "Launcher script exists"
else
    log_fail "Launcher script not found"
fi

if [ -x "launch-project-ape.command" ]; then
    log_pass "Launcher script is executable"
else
    log_fail "Launcher script is not executable"
fi

################################################################################
# Test 3: Dashboard Server
################################################################################

log_test "Testing dashboard server endpoints"

# Start server if not running
if ! curl -s http://localhost:8765/ > /dev/null 2>&1; then
    echo "Starting dashboard server..."
    python3 dashboard/server.py > /tmp/test-server.log 2>&1 &
    SERVER_PID=$!
    sleep 3
    STARTED_SERVER=true
else
    STARTED_SERVER=false
fi

# Test /configure endpoint
if curl -s http://localhost:8765/configure | grep -q "Project APE Configuration"; then
    log_pass "Configuration page loads"
else
    log_fail "Configuration page failed to load"
fi

# Test /api/load-config endpoint
if curl -s http://localhost:8765/api/load-config | python3 -c "import sys, json; json.load(sys.stdin)" > /dev/null 2>&1; then
    log_pass "Load configuration API works"
else
    log_fail "Load configuration API failed"
fi

# Test /api/preview-config endpoint
if curl -s -X POST http://localhost:8765/api/preview-config \
    -H "Content-Type: application/json" \
    -d '{"clients": [{"id": "test", "name": "Test", "folder": "/test", "industry": "", "subsegments": ""}], "settings": {}}' \
    | python3 -c "import sys, json; data = json.load(sys.stdin); exit(0 if data.get('success') else 1)" 2>&1; then
    log_pass "Preview configuration API works"
else
    log_fail "Preview configuration API failed"
fi

# Test /launch endpoint
if curl -s http://localhost:8765/launch | grep -q "Launching Project APE"; then
    log_pass "Launch page loads"
else
    log_fail "Launch page failed to load"
fi

# Clean up server if we started it
if [ "$STARTED_SERVER" = true ]; then
    kill $SERVER_PID 2>/dev/null || true
fi

################################################################################
# Test 4: Configuration Files
################################################################################

log_test "Testing configuration files"

if [ -f "vars.py" ]; then
    log_pass "vars.py exists"

    # Test syntax
    if python3 -m py_compile vars.py 2>/dev/null; then
        log_pass "vars.py has valid Python syntax"
    else
        log_fail "vars.py has syntax errors"
    fi

    # Test imports
    if python3 -c "import sys; sys.path.insert(0, '.'); import vars" 2>/dev/null; then
        log_pass "vars.py imports successfully"
    else
        log_fail "vars.py failed to import"
    fi
else
    log_fail "vars.py not found"
fi

################################################################################
# Test 5: Templates
################################################################################

log_test "Testing HTML templates"

TEMPLATES=(
    "dashboard/templates/configure.html"
    "dashboard/templates/launch.html"
    "dashboard/templates/error.html"
    "dashboard/templates/dashboard.html"
)

for template in "${TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        log_pass "Template exists: $(basename $template)"
    else
        log_fail "Template missing: $(basename $template)"
    fi
done

################################################################################
# Test 6: Static Assets
################################################################################

log_test "Testing static assets"

if [ -f "dashboard/static/configure.js" ]; then
    log_pass "configure.js exists"

    # Check for key functions
    if grep -q "saveAndLaunch" dashboard/static/configure.js; then
        log_pass "configure.js includes saveAndLaunch function"
    else
        log_fail "configure.js missing saveAndLaunch function"
    fi
else
    log_fail "configure.js not found"
fi

################################################################################
# Test Summary
################################################################################

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Test Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Phase 3 is ready for end-to-end testing."
    echo ""
    echo "Next steps:"
    echo "  1. Test configuration UI: open http://localhost:8765/configure"
    echo "  2. Load existing config with 'Load Existing Configuration' button"
    echo "  3. Make changes and preview in Preview tab"
    echo "  4. Click 'Save & Launch' to trigger workflow"
    echo "  5. Verify workflow starts and dashboard shows progress"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Please review the failures above and fix before proceeding."
    exit 1
fi
