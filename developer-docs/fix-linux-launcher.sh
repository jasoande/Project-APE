#!/bin/bash
################################################################################
# DEFINITIVE FIX for Linux Desktop Launcher
# This script fixes the "opens in text editor" issue on GNOME/Linux
################################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================================================"
echo "Project APE - Desktop Launcher Fix"
echo "========================================================================"
echo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_FILE="$HOME/Desktop/project-ape-launcher.desktop"

# Check if desktop file exists
if [ ! -f "$DESKTOP_FILE" ]; then
    echo -e "${YELLOW}Desktop launcher not found. Creating it now...${NC}"

    # Create the desktop file with absolute paths
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Project APE Launcher
Comment=Account Planning Engine - Automated research using NotebookLM
Exec=${SCRIPT_DIR}/launch-project-ape.py
Icon=applications-internet
Terminal=false
Categories=Development;Office;
StartupNotify=false
Path=${SCRIPT_DIR}
EOF

    echo -e "${GREEN}✅ Desktop file created${NC}"
fi

# Step 1: Make executable
echo "Step 1: Making desktop file executable..."
chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}✅ Executable permission set${NC}"

# Step 2: Trust the file (CRITICAL for GNOME)
echo "Step 2: Marking desktop file as trusted..."

# Method 1: Using gio (GNOME 3.38+)
if command -v gio &> /dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
    echo -e "${GREEN}✅ Marked as trusted (gio)${NC}"
fi

# Method 2: Using gvfs-set-attribute (older GNOME)
if command -v gvfs-set-attribute &> /dev/null; then
    gvfs-set-attribute "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
    echo -e "${GREEN}✅ Marked as trusted (gvfs)${NC}"
fi

# Step 3: Set the executable bit in the .desktop file itself
echo "Step 3: Ensuring launch-project-ape.py is executable..."
chmod +x "${SCRIPT_DIR}/launch-project-ape.py"
chmod +x "${SCRIPT_DIR}/launch-project-ape.sh"
echo -e "${GREEN}✅ Launcher scripts are executable${NC}"

echo
echo "========================================================================"
echo -e "${GREEN}FIX COMPLETE!${NC}"
echo "========================================================================"
echo
echo "Your desktop launcher should now work with double-click."
echo
echo -e "${BLUE}If it still opens in text editor:${NC}"
echo "  1. Right-click the desktop icon"
echo "  2. Select 'Allow Launching' or 'Trust and Launch'"
echo "  3. Then double-click should work"
echo
echo -e "${BLUE}Alternative - Run directly:${NC}"
echo "  cd ${SCRIPT_DIR}"
echo "  python3 launch-project-ape.py"
echo
