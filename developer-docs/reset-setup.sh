#!/bin/bash
################################################################################
# Reset Project APE Setup State
# Removes the first-run marker to allow setup to run again
################################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MARKER_FILE="$HOME/.ape_setup_complete"

echo "════════════════════════════════════════════════════════════════"
echo "  Project APE - Reset Setup State"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "$MARKER_FILE" ]; then
    echo -e "${BLUE}Current setup marker:${NC}"
    echo ""
    cat "$MARKER_FILE" | python3 -m json.tool 2>/dev/null || cat "$MARKER_FILE"
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    echo -e "${YELLOW}WARNING:${NC} This will remove the setup marker file."
    echo ""
    echo "What this does:"
    echo "  ✓ Removes the first-run completion marker"
    echo "  ✓ Next launch will run setup.sh again (20-30 min)"
    echo ""
    echo "What this does NOT do:"
    echo "  ✗ Does NOT uninstall Podman, gcloud, Python, etc."
    echo "  ✗ Does NOT remove NotebookLM credentials"
    echo "  ✗ Does NOT delete service account"
    echo "  ✗ Does NOT remove vars.py configuration"
    echo ""
    echo "Use this for:"
    echo "  • Testing the first-run experience"
    echo "  • Re-running setup after errors"
    echo "  • Forcing setup to run on next launch"
    echo ""
    read -p "Continue with reset? (y/n) " -n 1 -r
    echo ""
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$MARKER_FILE"
        echo -e "${GREEN}✅ Setup marker removed${NC}"
        echo ""
        echo "File removed: $MARKER_FILE"
        echo ""
        echo "Next time you run:"
        echo "  ${GREEN}./launch-project-ape.command${NC}"
        echo ""
        echo "Setup will run automatically (20-30 minutes)"
    else
        echo "Reset cancelled. Marker file preserved."
    fi
else
    echo -e "${YELLOW}ℹ️  No setup marker found${NC}"
    echo ""
    echo "Marker file does not exist: $MARKER_FILE"
    echo ""
    echo "This means either:"
    echo "  • Setup has never been completed"
    echo "  • Marker was already removed"
    echo "  • setup.sh failed to create the marker"
    echo ""
    echo "Next time you run launch-project-ape.command,"
    echo "setup will run automatically."
fi

echo ""
