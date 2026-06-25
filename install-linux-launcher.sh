#!/bin/bash
################################################################################
# Install Project APE Desktop Launcher for Linux
# Creates a desktop icon and application menu entry
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "Project APE - Linux Desktop Launcher Installer"
echo "========================================================================"
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_FILE="${SCRIPT_DIR}/project-ape-launcher.desktop"

# Check if desktop file exists
if [ ! -f "$DESKTOP_FILE" ]; then
    echo -e "${RED}Error: Desktop file not found at ${DESKTOP_FILE}${NC}"
    exit 1
fi

# Create a proper desktop file with absolute path
TEMP_DESKTOP="/tmp/project-ape-launcher.desktop"
cat > "$TEMP_DESKTOP" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Project APE
Comment=Account Planning Engine - Automated research using NotebookLM
Exec=python3 "${SCRIPT_DIR}/launch-project-ape.py"
Icon=applications-internet
Terminal=true
Categories=Development;Office;
StartupNotify=true
Path=${SCRIPT_DIR}
EOF

echo -e "${BLUE}Installation Options:${NC}"
echo
echo "1. Install to Desktop (creates clickable icon on your desktop)"
echo "2. Install to Applications Menu (appears in your app launcher)"
echo "3. Install to both"
echo "4. Show manual instructions"
echo

read -p "Choose option (1-4): " choice

case $choice in
    1)
        # Install to Desktop
        DESKTOP_DIR="$HOME/Desktop"
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$HOME/Escritorio"  # Spanish
        fi
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
        fi

        if [ ! -d "$DESKTOP_DIR" ]; then
            echo -e "${RED}Error: Could not find Desktop directory${NC}"
            echo "Please create ~/Desktop and try again"
            exit 1
        fi

        cp "$TEMP_DESKTOP" "$DESKTOP_DIR/project-ape-launcher.desktop"
        chmod +x "$DESKTOP_DIR/project-ape-launcher.desktop"

        # Mark as trusted (required for some desktop environments)
        if command -v gio &> /dev/null; then
            gio set "$DESKTOP_DIR/project-ape-launcher.desktop" metadata::trusted true 2>/dev/null || true
        fi

        echo -e "${GREEN}✅ Desktop icon created!${NC}"
        echo "   Location: $DESKTOP_DIR/project-ape-launcher.desktop"
        echo
        echo "If the icon doesn't work immediately:"
        echo "  1. Right-click the icon"
        echo "  2. Select 'Allow Launching' or 'Trust and Launch'"
        ;;

    2)
        # Install to Applications Menu
        APPS_DIR="$HOME/.local/share/applications"
        mkdir -p "$APPS_DIR"
        cp "$TEMP_DESKTOP" "$APPS_DIR/project-ape-launcher.desktop"
        chmod +x "$APPS_DIR/project-ape-launcher.desktop"

        # Update desktop database
        if command -v update-desktop-database &> /dev/null; then
            update-desktop-database "$APPS_DIR" 2>/dev/null || true
        fi

        echo -e "${GREEN}✅ Application menu entry created!${NC}"
        echo "   Location: $APPS_DIR/project-ape-launcher.desktop"
        echo
        echo "Search for 'Project APE' in your application launcher"
        ;;

    3)
        # Install to both
        # Desktop
        DESKTOP_DIR="$HOME/Desktop"
        if [ ! -d "$DESKTOP_DIR" ]; then
            DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
        fi

        if [ -d "$DESKTOP_DIR" ]; then
            cp "$TEMP_DESKTOP" "$DESKTOP_DIR/project-ape-launcher.desktop"
            chmod +x "$DESKTOP_DIR/project-ape-launcher.desktop"
            if command -v gio &> /dev/null; then
                gio set "$DESKTOP_DIR/project-ape-launcher.desktop" metadata::trusted true 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ Desktop icon created!${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not find Desktop directory, skipping...${NC}"
        fi

        # Applications
        APPS_DIR="$HOME/.local/share/applications"
        mkdir -p "$APPS_DIR"
        cp "$TEMP_DESKTOP" "$APPS_DIR/project-ape-launcher.desktop"
        chmod +x "$APPS_DIR/project-ape-launcher.desktop"
        if command -v update-desktop-database &> /dev/null; then
            update-desktop-database "$APPS_DIR" 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ Application menu entry created!${NC}"
        echo
        echo "You can now launch Project APE from:"
        echo "  - Desktop icon (double-click)"
        echo "  - Application menu (search 'Project APE')"
        ;;

    4)
        # Show manual instructions
        echo
        echo -e "${BLUE}Manual Installation Instructions:${NC}"
        echo
        echo "Option A - Desktop Icon:"
        echo "  cp $TEMP_DESKTOP ~/Desktop/"
        echo "  chmod +x ~/Desktop/project-ape-launcher.desktop"
        echo
        echo "Option B - Application Menu:"
        echo "  mkdir -p ~/.local/share/applications"
        echo "  cp $TEMP_DESKTOP ~/.local/share/applications/"
        echo "  chmod +x ~/.local/share/applications/project-ape-launcher.desktop"
        echo "  update-desktop-database ~/.local/share/applications"
        echo
        echo "Option C - Direct Execution:"
        echo "  cd $SCRIPT_DIR"
        echo "  python3 launch-project-ape.py"
        echo
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

# Clean up
rm -f "$TEMP_DESKTOP"

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo -e "${BLUE}Alternative launch methods:${NC}"
echo "  1. From terminal: cd $SCRIPT_DIR && python3 launch-project-ape.py"
echo "  2. From terminal: cd $SCRIPT_DIR && ./launch-project-ape.sh"
echo
echo -e "${YELLOW}File Manager Settings:${NC}"
echo "If you prefer to double-click shell scripts directly, configure your file manager:"
echo
echo "  GNOME (Nautilus):"
echo "    Files → Preferences → Behavior → Executable Text Files"
echo "    → Select 'Run them' or 'Ask what to do'"
echo
echo "  KDE (Dolphin):"
echo "    Settings → Configure Dolphin → General → Confirmations"
echo "    → Check 'Confirm execution of files'"
echo
echo "  XFCE (Thunar):"
echo "    Edit → Preferences → Advanced → Execute shell scripts"
echo "    → Check 'Execute shell scripts when they are opened'"
echo
