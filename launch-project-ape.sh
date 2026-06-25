#!/bin/bash
################################################################################
# Project APE - Linux/Unix Launcher
# Double-click or run this script to launch Project APE dashboard
################################################################################

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.10+ first:"
    echo "  - Debian/Ubuntu: sudo apt install python3"
    echo "  - RHEL/Fedora: sudo dnf install python3"
    echo "  - macOS: brew install python3"
    exit 1
fi

# Run the Python launcher
python3 "$SCRIPT_DIR/launch-project-ape.py"
