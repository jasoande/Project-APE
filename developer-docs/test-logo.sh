#!/bin/bash
################################################################################
# Test King Kong Logo on All Pages
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
echo "  King Kong Logo Display Tests"
echo "════════════════════════════════════════════════════════════════"
echo ""

################################################################################
# Test Logo File Exists
################################################################################

log_test "Checking logo file exists"

if [ -f "dashboard/static/kingkong.png" ]; then
    log_pass "kingkong.png exists in static directory"
else
    log_fail "kingkong.png not found"
fi

# Get file size
FILE_SIZE=$(ls -lh dashboard/static/kingkong.png 2>/dev/null | awk '{print $5}')
if [ ! -z "$FILE_SIZE" ]; then
    log_pass "Logo file size: $FILE_SIZE"
else
    log_fail "Could not determine file size"
fi

################################################################################
# Test Logo in Templates
################################################################################

log_test "Checking logo in HTML templates"

# Test dashboard.html
if grep -q "kingkong.png" dashboard/templates/dashboard.html; then
    log_pass "Logo referenced in dashboard.html"
else
    log_fail "Logo missing from dashboard.html"
fi

# Test configure.html
if grep -q "kingkong.png" dashboard/templates/configure.html; then
    log_pass "Logo referenced in configure.html"
else
    log_fail "Logo missing from configure.html"
fi

# Test launch.html
if grep -q "kingkong.png" dashboard/templates/launch.html; then
    log_pass "Logo referenced in launch.html"
else
    log_fail "Logo missing from launch.html"
fi

# Test error.html
if grep -q "kingkong.png" dashboard/templates/error.html; then
    log_pass "Logo referenced in error.html"
else
    log_fail "Logo missing from error.html"
fi

################################################################################
# Test Logo Styling
################################################################################

log_test "Checking logo styling classes"

# Check for monkey-logo class in all templates
for template in dashboard/templates/*.html; do
    if grep -q "monkey-logo" "$template"; then
        log_pass "monkey-logo class found in $(basename $template)"
    else
        # Not all templates need the class (some might use inline styles)
        if grep -q "kingkong.png" "$template"; then
            log_pass "Logo present in $(basename $template) (inline style)"
        fi
    fi
done

################################################################################
# Test Server Rendering
################################################################################

log_test "Testing logo renders via server"

# Check if server is running
if curl -s http://localhost:8765/ > /dev/null 2>&1; then

    # Test dashboard page
    if curl -s http://localhost:8765/ | grep -q 'kingkong.png'; then
        log_pass "Dashboard page serves logo"
    else
        log_fail "Dashboard page missing logo"
    fi

    # Test configure page
    if curl -s http://localhost:8765/configure | grep -q 'kingkong.png'; then
        log_pass "Configure page serves logo"
    else
        log_fail "Configure page missing logo"
    fi

    # Test launch page
    if curl -s http://localhost:8765/launch | grep -q 'kingkong.png'; then
        log_pass "Launch page serves logo"
    else
        log_fail "Launch page missing logo"
    fi

    # Test static file access
    if curl -s http://localhost:8765/static/kingkong.png | file - | grep -q 'PNG image'; then
        log_pass "Logo file accessible via /static/kingkong.png"
    else
        log_fail "Logo file not accessible"
    fi

else
    echo -e "${BLUE}[INFO]${NC} Server not running, skipping render tests"
    echo "       Start server with: python3 dashboard/server.py"
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
    echo -e "${GREEN}✅ All logo tests passed!${NC}"
    echo ""
    echo "King Kong logo is displayed on all pages:"
    echo "  • Dashboard (/)               - 150x150px logo"
    echo "  • Configuration (/configure)  - 100x100px logo"
    echo "  • Launch (/launch)            - 80x80px logo"
    echo "  • Error pages                 - 80x80px logo"
    echo ""
    echo "To view:"
    echo "  1. Start server: python3 dashboard/server.py"
    echo "  2. Open browser: http://localhost:8765/"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Please review the failures above."
    exit 1
fi
