#!/bin/bash
# Project APE - Podman Installation Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "PROJECT APE - PODMAN INSTALLATION"
echo "========================================================================"
echo

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ -f /etc/redhat-release ]]; then
    OS="RHEL/Fedora"
elif [[ -f /etc/debian_version ]]; then
    OS="Debian/Ubuntu"
else
    OS="Unknown"
fi

echo "Detected OS: ${OS}"
echo

# Check if already installed
if command -v podman &> /dev/null; then
    echo -e "${GREEN}✅ Podman is already installed${NC}"
    podman --version
    echo
    echo "To reinstall, run:"
    echo "  brew reinstall podman  # macOS"
    echo "  sudo dnf reinstall podman  # RHEL/Fedora"
    echo "  sudo apt reinstall podman  # Debian/Ubuntu"
    exit 0
fi

# Installation based on OS
case $OS in
    macOS)
        echo "Installing Podman on macOS..."
        echo

        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}ERROR: Homebrew is not installed${NC}"
            echo
            echo "Install Homebrew first:"
            echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            exit 1
        fi

        echo "Installing podman via Homebrew..."
        brew install podman

        echo
        echo "Initializing Podman machine..."
        podman machine init

        echo "Starting Podman machine..."
        podman machine start

        echo
        echo -e "${GREEN}✅ Podman installed successfully${NC}"
        podman --version
        ;;

    RHEL/Fedora)
        echo "Installing Podman on RHEL/Fedora..."
        echo

        sudo dnf install -y podman podman-compose

        echo
        echo -e "${GREEN}✅ Podman installed successfully${NC}"
        podman --version
        ;;

    Debian/Ubuntu)
        echo "Installing Podman on Debian/Ubuntu..."
        echo

        sudo apt-get update
        sudo apt-get install -y podman

        # Install podman-compose separately
        echo
        echo "Installing podman-compose..."
        sudo pip3 install podman-compose

        echo
        echo -e "${GREEN}✅ Podman installed successfully${NC}"
        podman --version
        ;;

    *)
        echo -e "${RED}ERROR: Unsupported OS${NC}"
        echo
        echo "Please install Podman manually:"
        echo "  https://podman.io/getting-started/installation"
        exit 1
        ;;
esac

echo
echo "========================================================================"
echo "PODMAN SETUP COMPLETE"
echo "========================================================================"
echo
echo "Next steps:"
echo "  1. Build container: ./build-container.sh"
echo "  2. Run container: ./run-container.sh"
echo "  3. Or use compose: podman-compose up"
echo
echo "Useful commands:"
echo "  podman images          # List images"
echo "  podman ps              # List running containers"
echo "  podman logs <name>     # View container logs"
echo "  podman exec -it <name> /bin/bash  # Enter container"
echo
