#!/bin/bash
################################################################################
# NotebookLM Authentication Helper
#
# Handles browser-based authentication with proper X11 forwarding
#
# Project Owner & Maintainer: Jason Anderson
################################################################################

# Check if DISPLAY is set (X11 forwarding active)
if [ -z "$DISPLAY" ]; then
    echo "❌ ERROR: No X11 display available"
    echo ""
    echo "To authenticate, you need X11 forwarding enabled."
    echo ""
    echo "Reconnect with:"
    echo "  ssh -X user@host"
    echo ""
    echo "Or use -Y for trusted X11 forwarding:"
    echo "  ssh -Y user@host"
    echo ""
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo ""
    echo "Activating virtual environment..."
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    if [ -f "${SCRIPT_DIR}/venv/bin/activate" ]; then
        source "${SCRIPT_DIR}/venv/bin/activate"
        echo "✅ Virtual environment activated"
    else
        echo "❌ ERROR: Virtual environment not found at ${SCRIPT_DIR}/venv"
        echo ""
        echo "Run setup first:"
        echo "  sudo ./setup.sh"
        echo ""
        exit 1
    fi
fi

echo "=========================================================================="
echo "  NotebookLM Authentication"
echo "=========================================================================="
echo ""
echo "DISPLAY: $DISPLAY"
echo "Virtual Env: $VIRTUAL_ENV"
echo ""
echo "A Chrome window will open for Google authentication."
echo "Authenticate, then return to this terminal."
echo ""
echo "Starting authentication..."
echo ""

# Run notebooklm login
notebooklm login

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================================================="
    echo "✅ Authentication successful!"
    echo "=========================================================================="
    echo ""
    echo "Credentials saved to: ~/.notebooklm/credentials.json"
    echo ""
    echo "Next steps:"
    echo "  1. Set up container credentials: ./setup-credentials.sh"
    echo "  2. Create your config: cp example-container.py vars.py"
    echo "  3. Run Project APE: ./ape-run.sh --vars ./vars.py --mode fast"
    echo ""
else
    echo ""
    echo "=========================================================================="
    echo "❌ Authentication failed"
    echo "=========================================================================="
    echo ""
    echo "Troubleshooting:"
    echo "  • Ensure you're connected with: ssh -X user@host (or ssh -Y)"
    echo "  • Check DISPLAY is set: echo \$DISPLAY"
    echo "  • Try reconnecting with X11 forwarding enabled"
    echo ""
    exit 1
fi
