#!/bin/bash
################################################################################
# project ape Account Intelligence - Local Workflow Runner
# Runs workflows using the virtual environment Python interpreter
#
# Usage:
#   ./run-workflow.sh fast                      # All clients, fast mode
#   ./run-workflow.sh deep                      # All clients, deep mode
#   ./run-workflow.sh fast merck organon        # Specific clients
#   ./run-workflow.sh fast --refresh            # Force refresh Drive cache
################################################################################

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
VENV_DIR="$HOME/.project-ape-venv"
PYTHON_BIN="$VENV_DIR/bin/python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ -z "$1" ]; then
    echo "project ape Account Intelligence - Account Planning Engine v3.2.0"
    echo ""
    echo "Usage:"
    echo "  ./run-workflow.sh fast                      # All clients, fast mode (15-20 min)"
    echo "  ./run-workflow.sh deep                      # All clients, deep mode (35-40 min)"
    echo "  ./run-workflow.sh update                    # Update mode (refresh existing notebooks)"
    echo "  ./run-workflow.sh fast --refresh            # Force refresh Drive cache"
    echo "  ./run-workflow.sh fast merck organon        # Specific clients only"
    echo ""
    echo "Modes:"
    echo "  fast     Quick research (15-20 minutes per client)"
    echo "  deep     Thorough research (35-40 minutes per client)"
    echo "  update   Refresh existing notebooks (5-10 minutes per client)"
    echo ""
    echo "Options:"
    echo "  --refresh       Force refresh Google Drive cache (ignore 24hr TTL)"
    echo "  --no-dashboard  Don't launch the web dashboard"
    echo ""
    echo "Examples:"
    echo "  ./run-workflow.sh fast                      # Run all clients in vars.py"
    echo "  ./run-workflow.sh fast merck                # Run one client"
    echo "  ./run-workflow.sh deep merck organon        # Multiple clients, deep mode"
    echo "  ./run-workflow.sh fast --refresh            # Force fresh download from Drive"
    echo ""
    echo "Dashboard:"
    echo "  Automatically opens at http://localhost:8765"
    echo "  Shows real-time progress, quality scores, and logs"
    echo ""
    exit 0
fi

# Validate virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_DIR${NC}"
    echo ""
    echo "Please run the setup script first:"
    echo "  ./setup-environment.sh"
    echo ""
    exit 1
fi

# Validate Python binary exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}❌ Python binary not found at: $PYTHON_BIN${NC}"
    echo ""
    echo "Virtual environment appears corrupted. Please run:"
    echo "  ./setup-environment.sh"
    echo ""
    exit 1
fi

# Validate vars.py exists
if [ ! -f "$SCRIPT_DIR/vars.py" ]; then
    echo -e "${RED}❌ Configuration file not found: vars.py${NC}"
    echo ""
    echo "Please configure your clients first:"
    echo "  1. Copy template:    cp example-vars.py vars.py"
    echo "  2. Edit config:      nano vars.py"
    echo "  3. Or use web UI:    python3 dashboard/server.py"
    echo "     Then open:        http://localhost:8765/configure"
    echo ""
    exit 1
fi

# Check if dotenv is installed
if ! "$PYTHON_BIN" -c "import dotenv" 2>/dev/null; then
    echo -e "${RED}❌ Missing dependency: python-dotenv${NC}"
    echo ""
    echo "Please install dependencies:"
    echo "  source $VENV_DIR/bin/activate"
    echo "  pip3 install -r developer-docs/requirements.txt"
    echo ""
    exit 1
fi

# Print banner
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  PROJECT APE - ACCOUNT PLANNING ENGINE"
echo "  AI-Powered Enterprise Account Planning Automation"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✓${NC} Virtual Environment: $VENV_DIR"
echo -e "  ${GREEN}✓${NC} Python: $($PYTHON_BIN --version 2>&1)"
echo -e "  ${GREEN}✓${NC} Configuration: vars.py"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Run main.py with all arguments
echo -e "${YELLOW}▶${NC} Starting workflow..."
echo ""

# Parse arguments and convert to main.py format
MODE=""
CLIENTS=()
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        fast|deep|update)
            MODE="$1"
            shift
            ;;
        --refresh|--no-dashboard)
            EXTRA_ARGS+=("$1")
            shift
            ;;
        *)
            # Assume it's a client name
            CLIENTS+=("$1")
            shift
            ;;
    esac
done

# Add venv bin to PATH so notebooklm CLI is accessible from subprocesses
export PATH="$VENV_DIR/bin:$PATH"

# Build command
CMD=("$PYTHON_BIN" "$SCRIPT_DIR/main.py")

if [ -n "$MODE" ]; then
    CMD+=(--mode "$MODE")
fi

if [ ${#CLIENTS[@]} -gt 0 ]; then
    CMD+=(--clients "${CLIENTS[@]}")
fi

if [ ${#EXTRA_ARGS[@]} -gt 0 ]; then
    CMD+=("${EXTRA_ARGS[@]}")
fi

# Execute
exec "${CMD[@]}"
