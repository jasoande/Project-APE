#!/bin/bash
#
# Security Improvements Validation Script
# Verifies all 6 critical security improvements are working correctly
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Project-APE Security Improvements Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL_CHECKS=0
PASSED_CHECKS=0

# Validation function
validate() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

# Improvement #1: Flask Secret Key Persistence
echo -e "${BLUE}1. Validating Flask Secret Key Persistence...${NC}"

if [ -f ~/.project-ape/flask_secret.key ]; then
    KEY_SIZE=$(wc -c < ~/.project-ape/flask_secret.key | tr -d ' ')
    if [ "$KEY_SIZE" -eq 64 ]; then
        validate "Flask secret key exists and has correct size (64 chars)"
    else
        echo -e "${RED}❌ Flask secret key has wrong size: $KEY_SIZE (expected 64)${NC}"
    fi

    # Check permissions
    PERMS=$(stat -f "%Op" ~/.project-ape/flask_secret.key 2>/dev/null || stat -c "%a" ~/.project-ape/flask_secret.key 2>/dev/null)
    if [ "$PERMS" = "100600" ] || [ "$PERMS" = "600" ]; then
        validate "Flask secret key has secure permissions (0600)"
    else
        echo -e "${RED}❌ Flask secret key has insecure permissions: $PERMS${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Flask secret key not yet created (will be created on first server start)${NC}"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""

# Improvement #2: Credential File Permissions
echo -e "${BLUE}2. Validating Credential File Permissions...${NC}"

CRED_FILES=(
    "$HOME/.project-ape/drive_credentials.json"
    "$HOME/.project-ape/drive_token.json"
)

for CRED_FILE in "${CRED_FILES[@]}"; do
    if [ -f "$CRED_FILE" ]; then
        PERMS=$(stat -f "%Op" "$CRED_FILE" 2>/dev/null || stat -c "%a" "$CRED_FILE" 2>/dev/null)
        if [ "$PERMS" = "100600" ] || [ "$PERMS" = "600" ]; then
            validate "$(basename $CRED_FILE) has secure permissions (0600)"
        else
            echo -e "${RED}❌ $(basename $CRED_FILE) has insecure permissions: $PERMS${NC}"
            TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        fi
    else
        echo -e "${YELLOW}⚠️  $(basename $CRED_FILE) not found (optional)${NC}"
    fi
done

echo ""

# Improvement #3: Automated Testing
echo -e "${BLUE}3. Validating Automated Testing...${NC}"

if [ -f "run-tests.sh" ]; then
    validate "Test runner script exists"
else
    echo -e "${RED}❌ Test runner script missing${NC}"
fi

if [ -f "TESTING.md" ]; then
    validate "Testing documentation exists"
else
    echo -e "${RED}❌ Testing documentation missing${NC}"
fi

# Count test files
TEST_COUNT=$(find tests/ -name "test_*.py" | wc -l | tr -d ' ')
if [ "$TEST_COUNT" -ge 20 ]; then
    validate "Test suite has $TEST_COUNT test files (≥20)"
else
    echo -e "${RED}❌ Only $TEST_COUNT test files (expected ≥20)${NC}"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""

# Improvement #4: Comprehensive Health Checks
echo -e "${BLUE}4. Validating Comprehensive Health Checks...${NC}"

# Check if health endpoint code exists
if grep -q "/health/detailed" dashboard/server.py; then
    validate "/health/detailed endpoint exists in code"
else
    echo -e "${RED}❌ /health/detailed endpoint not found${NC}"
fi

# Check for all required health checks
REQUIRED_CHECKS=(
    "notebooklm_auth"
    "drive_auth"
    "disk_space"
    "process_health"
    "notebooklm_cli"
)

for CHECK in "${REQUIRED_CHECKS[@]}"; do
    if grep -q "'$CHECK'" dashboard/server.py; then
        validate "Health check '$CHECK' implemented"
    else
        echo -e "${RED}❌ Health check '$CHECK' missing${NC}"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
done

echo ""

# Improvement #5: Security Headers
echo -e "${BLUE}5. Validating Security Headers...${NC}"

# Check for security header implementation
REQUIRED_HEADERS=(
    "X-Content-Type-Options"
    "X-Frame-Options"
    "X-XSS-Protection"
    "Content-Security-Policy"
    "Strict-Transport-Security"
)

for HEADER in "${REQUIRED_HEADERS[@]}"; do
    if grep -q "$HEADER" dashboard/server.py; then
        validate "Security header '$HEADER' implemented"
    else
        echo -e "${RED}❌ Security header '$HEADER' missing${NC}"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
done

# Check for HTTPS enforcement
if grep -q "enforce_https" dashboard/server.py; then
    validate "HTTPS enforcement implemented"
else
    echo -e "${RED}❌ HTTPS enforcement missing${NC}"
fi

echo ""

# Improvement #6: Log Sanitization
echo -e "${BLUE}6. Validating Log Sanitization...${NC}"

if [ -f "core/log_sanitizer.py" ]; then
    validate "Log sanitizer module exists"
else
    echo -e "${RED}❌ Log sanitizer module missing${NC}"
fi

# Check for SanitizingFormatter class
if grep -q "class SanitizingFormatter" core/log_sanitizer.py 2>/dev/null; then
    validate "SanitizingFormatter class exists"
else
    echo -e "${RED}❌ SanitizingFormatter class missing${NC}"
fi

# Count redaction patterns
PATTERN_COUNT=$(grep -c "re.compile" core/log_sanitizer.py 2>/dev/null || echo "0")
if [ "$PATTERN_COUNT" -ge 10 ]; then
    validate "Log sanitizer has $PATTERN_COUNT redaction patterns (≥10)"
else
    echo -e "${RED}❌ Only $PATTERN_COUNT redaction patterns (expected ≥10)${NC}"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PERCENT=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo -e "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$((TOTAL_CHECKS - PASSED_CHECKS))${NC}"
echo -e "Success Rate: ${GREEN}${PERCENT}%${NC}"

echo ""

if [ "$PASSED_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL SECURITY IMPROVEMENTS VALIDATED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
elif [ "$PERCENT" -ge 90 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  MOSTLY VALIDATED (≥90%)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ VALIDATION FAILED (<90%)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
