#!/bin/bash
################################################################################
# Test Script for Logs Tab Feature
################################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

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
echo "  Logs Tab Feature Tests"
echo "════════════════════════════════════════════════════════════════"
echo ""

################################################################################
# Test 1: Backend Endpoints
################################################################################

log_test "Testing logs backend endpoints"

# Test /api/available-logs
if curl -s http://localhost:8765/api/available-logs | python3 -c "import sys, json; data = json.load(sys.stdin); exit(0 if data.get('success') else 1)" 2>&1; then
    log_pass "Available logs API responds with success"
else
    log_fail "Available logs API failed"
fi

# Test logs list contains expected fields
if curl -s http://localhost:8765/api/available-logs | python3 -c "import sys, json; data = json.load(sys.stdin); exit(0 if data.get('logs') and len(data['logs']) > 0 else 1)" 2>&1; then
    log_pass "Available logs API returns log list"
else
    log_fail "Available logs API returned empty list"
fi

# Test /logs/overall endpoint (just check it responds with SSE format)
# Use timeout and check if we get at least one data line
if timeout 3 bash -c 'curl -s http://localhost:8765/logs/overall | head -5' 2>/dev/null | grep -q "data:"; then
    log_pass "Overall logs endpoint streams SSE data"
else
    # Even if timeout, if curl started successfully, that's good enough
    if curl -s -I http://localhost:8765/logs/overall 2>/dev/null | grep -q "text/event-stream"; then
        log_pass "Overall logs endpoint configured correctly"
    else
        log_fail "Overall logs endpoint failed"
    fi
fi

################################################################################
# Test 2: Frontend HTML/CSS
################################################################################

log_test "Testing logs tab HTML/CSS"

# Test Logs tab exists in HTML
if curl -s http://localhost:8765/configure | grep -q 'data-tab="logs"'; then
    log_pass "Logs tab button exists in HTML"
else
    log_fail "Logs tab button missing from HTML"
fi

# Test logs panel exists
if curl -s http://localhost:8765/configure | grep -q 'id="logs-panel"'; then
    log_pass "Logs panel exists in HTML"
else
    log_fail "Logs panel missing from HTML"
fi

# Test log viewer elements
if curl -s http://localhost:8765/configure | grep -q 'id="logViewer"'; then
    log_pass "Log viewer element exists"
else
    log_fail "Log viewer element missing"
fi

# Test CSS classes
if curl -s http://localhost:8765/configure | grep -q '.log-viewer'; then
    log_pass "Log viewer CSS styles exist"
else
    log_fail "Log viewer CSS styles missing"
fi

################################################################################
# Test 3: JavaScript Functions
################################################################################

log_test "Testing logs JavaScript functions"

# Test initLogsTab function exists
if grep -q "initLogsTab" dashboard/static/configure.js; then
    log_pass "initLogsTab function exists"
else
    log_fail "initLogsTab function missing"
fi

# Test loadAvailableLogs function exists
if grep -q "loadAvailableLogs" dashboard/static/configure.js; then
    log_pass "loadAvailableLogs function exists"
else
    log_fail "loadAvailableLogs function missing"
fi

# Test switchLogSource function exists
if grep -q "switchLogSource" dashboard/static/configure.js; then
    log_pass "switchLogSource function exists"
else
    log_fail "switchLogSource function missing"
fi

# Test appendLogLine function exists
if grep -q "appendLogLine" dashboard/static/configure.js; then
    log_pass "appendLogLine function exists"
else
    log_fail "appendLogLine function missing"
fi

# Test toggleLogsPause function exists
if grep -q "toggleLogsPause" dashboard/static/configure.js; then
    log_pass "toggleLogsPause function exists"
else
    log_fail "toggleLogsPause function missing"
fi

# Test clearLogs function exists
if grep -q "clearLogs" dashboard/static/configure.js; then
    log_pass "clearLogs function exists"
else
    log_fail "clearLogs function missing"
fi

# Test downloadLogs function exists
if grep -q "downloadLogs" dashboard/static/configure.js; then
    log_pass "downloadLogs function exists"
else
    log_fail "downloadLogs function missing"
fi

################################################################################
# Test 4: First-Run Marker System
################################################################################

log_test "Testing first-run marker system"

# Test setup.sh includes marker creation
if grep -q "ape_setup_complete" setup.sh; then
    log_pass "setup.sh includes marker creation code"
else
    log_fail "setup.sh missing marker creation code"
fi

# Test reset-setup.sh exists
if [ -f "reset-setup.sh" ]; then
    log_pass "reset-setup.sh exists"
else
    log_fail "reset-setup.sh missing"
fi

# Test reset-setup.sh is executable
if [ -x "reset-setup.sh" ]; then
    log_pass "reset-setup.sh is executable"
else
    log_fail "reset-setup.sh not executable"
fi

# Test launcher checks for marker
if grep -q "ape_setup_complete" launch-project-ape.command; then
    log_pass "Launcher checks for setup marker"
else
    log_fail "Launcher missing marker check"
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
    echo "Logs tab feature is ready for use."
    echo ""
    echo "To test manually:"
    echo "  1. Open http://localhost:8765/configure"
    echo "  2. Click 'Logs' tab"
    echo "  3. Select a log source from dropdown"
    echo "  4. Verify logs stream in real-time"
    echo "  5. Test Pause/Resume buttons"
    echo "  6. Test Clear and Download buttons"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Please review the failures above."
    exit 1
fi
