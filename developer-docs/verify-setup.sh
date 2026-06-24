#!/bin/bash
# Verification script for Project APE setup
# Run this AFTER setup-environment.sh completes

set +e  # Don't exit on error, we're checking

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================================================"
echo "PROJECT APE - SETUP VERIFICATION"
echo "========================================================================"
echo

ERRORS=0
WARNINGS=0

# Check 1: Homebrew Python version
echo "1. Checking Homebrew Python..."
if [ -x "/opt/homebrew/bin/python3" ]; then
    BREW_PYTHON_VERSION=$(/opt/homebrew/bin/python3 --version 2>&1 | awk '{print $2}')
    BREW_MAJOR=$(echo $BREW_PYTHON_VERSION | cut -d. -f1)
    BREW_MINOR=$(echo $BREW_PYTHON_VERSION | cut -d. -f2)

    if [[ "$BREW_MAJOR" -eq 3 && "$BREW_MINOR" -ge 10 ]]; then
        echo -e "   ${GREEN}✅ Homebrew Python: $BREW_PYTHON_VERSION${NC}"
    else
        echo -e "   ${RED}❌ Homebrew Python too old: $BREW_PYTHON_VERSION (need 3.10+)${NC}"
        ERRORS=$((ERRORS + 1))
    fi
elif [ -x "/usr/local/bin/python3" ]; then
    BREW_PYTHON_VERSION=$(/usr/local/bin/python3 --version 2>&1 | awk '{print $2}')
    echo -e "   ${GREEN}✅ Homebrew Python (Intel): $BREW_PYTHON_VERSION${NC}"
else
    echo -e "   ${RED}❌ Homebrew Python not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: System Python (for comparison)
echo "2. Checking System Python..."
SYSTEM_PYTHON_VERSION=$(/usr/bin/python3 --version 2>&1 | awk '{print $2}')
echo -e "   ${BLUE}ℹ️  System Python: $SYSTEM_PYTHON_VERSION (will NOT be used)${NC}"

# Check 3: Virtual environment exists
echo "3. Checking virtual environment..."
VENV_DIR="$HOME/.project-ape-venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "   ${GREEN}✅ Virtual environment exists: $VENV_DIR${NC}"
else
    echo -e "   ${RED}❌ Virtual environment not found${NC}"
    echo "      Run: ./setup-environment.sh"
    ERRORS=$((ERRORS + 1))
    exit 1  # Can't continue without venv
fi

# Check 4: Virtual environment Python version
echo "4. Checking venv Python version..."
if [ -x "$VENV_DIR/bin/python3" ]; then
    VENV_PYTHON_VERSION=$("$VENV_DIR/bin/python3" --version 2>&1 | awk '{print $2}')
    VENV_MAJOR=$(echo $VENV_PYTHON_VERSION | cut -d. -f1)
    VENV_MINOR=$(echo $VENV_PYTHON_VERSION | cut -d. -f2)

    if [[ "$VENV_MAJOR" -eq 3 && "$VENV_MINOR" -ge 10 ]]; then
        echo -e "   ${GREEN}✅ Venv Python: $VENV_PYTHON_VERSION${NC}"
    else
        echo -e "   ${RED}❌ Venv Python too old: $VENV_PYTHON_VERSION (need 3.10+)${NC}"
        echo "      Delete venv and rerun setup: rm -rf $VENV_DIR && ./setup-environment.sh"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "   ${RED}❌ Venv Python binary missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: NotebookLM CLI installed
echo "5. Checking NotebookLM CLI..."
if [ -x "$VENV_DIR/bin/notebooklm" ]; then
    echo -e "   ${GREEN}✅ NotebookLM CLI binary exists${NC}"

    # Try to import (test for the type union syntax error)
    "$VENV_DIR/bin/python3" -c "from notebooklm.notebooklm_cli import main" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✅ NotebookLM imports successfully${NC}"
    else
        echo -e "   ${RED}❌ NotebookLM import failed (likely Python < 3.10)${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "   ${RED}❌ NotebookLM CLI not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: Playwright installed
echo "6. Checking Playwright..."
if [ -x "$VENV_DIR/bin/playwright" ]; then
    PLAYWRIGHT_VERSION=$("$VENV_DIR/bin/playwright" --version 2>&1)
    echo -e "   ${GREEN}✅ Playwright: $PLAYWRIGHT_VERSION${NC}"
else
    echo -e "   ${YELLOW}⚠️  Playwright binary not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 7: Playwright browsers installed
echo "7. Checking Playwright browsers..."
CHROMIUM_DIR="$HOME/Library/Caches/ms-playwright"
if [ -d "$CHROMIUM_DIR" ] && ls "$CHROMIUM_DIR"/chromium-* &>/dev/null; then
    echo -e "   ${GREEN}✅ Chromium browser installed${NC}"
else
    echo -e "   ${YELLOW}⚠️  Chromium not found - run: $VENV_DIR/bin/playwright install chromium${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 8: Activation script exists
echo "8. Checking activation helper..."
if [ -f "./activate-ape-env.sh" ]; then
    echo -e "   ${GREEN}✅ Activation script exists${NC}"
else
    echo -e "   ${YELLOW}⚠️  Activation script not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo
echo "========================================================================"
echo "VERIFICATION SUMMARY"
echo "========================================================================"
echo

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo
    echo "Setup is complete and working correctly!"
    echo
    echo "Next steps:"
    echo "  1. Activate environment: source ./activate-ape-env.sh"
    echo "  2. Login to NotebookLM: notebooklm login"
    echo "  3. Setup credentials: ./setup-credentials.sh"
    echo "  4. Launch Project APE: ./launch_ape.sh fast"
    echo
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
    echo
    echo "Setup is mostly working but has minor issues (see above)."
    echo "You can probably continue, but some features might not work."
    echo
elif [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ ERRORS: $ERRORS${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
    fi
    echo
    echo "Setup has critical errors that must be fixed."
    echo "Please review the issues above and rerun: ./setup-environment.sh"
    echo
    exit 1
fi

exit 0
