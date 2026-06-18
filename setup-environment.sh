#!/bin/bash
# Project APE - Environment Setup Script
# Installs Podman and NotebookLM CLI for end users

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "PROJECT APE - ENVIRONMENT SETUP"
echo "========================================================================"
echo
echo "This script will install the required tools for running Project APE:"
echo
echo "  1. Podman (container runtime)"
echo "  2. Node.js (required for NotebookLM CLI)"
echo "  3. NotebookLM CLI (notebooklm-py)"
echo
echo "NOTE: Python is NOT required - Project APE runs in a pre-built container."
echo
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi
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

# ==============================================================================
# STEP 1: Install Podman
# ==============================================================================

echo "========================================================================"
echo "STEP 1: PODMAN INSTALLATION"
echo "========================================================================"
echo

if command -v podman &> /dev/null; then
    echo -e "${GREEN}✅ Podman is already installed${NC}"
    podman --version
else
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

            sudo dnf install -y podman

            echo
            echo -e "${GREEN}✅ Podman installed successfully${NC}"
            podman --version
            ;;

        Debian/Ubuntu)
            echo "Installing Podman on Debian/Ubuntu..."
            echo

            sudo apt-get update
            sudo apt-get install -y podman

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
fi

echo

# ==============================================================================
# STEP 2: Install Node.js (required for NotebookLM CLI)
# ==============================================================================

echo "========================================================================"
echo "STEP 2: NODE.JS INSTALLATION"
echo "========================================================================"
echo

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js is already installed: ${NODE_VERSION}${NC}"

    # Check if version is >= 18
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$MAJOR_VERSION" -lt 18 ]; then
        echo -e "${YELLOW}⚠️  Warning: Node.js 18+ recommended (current: ${NODE_VERSION})${NC}"
        echo "Consider upgrading Node.js"
    fi
else
    echo "Node.js not found. Installing..."
    echo

    case $OS in
        macOS)
            echo "Installing Node.js via Homebrew..."
            brew install node@20

            # Add to PATH if not already there
            if ! grep -q "/opt/homebrew/opt/node@20/bin" ~/.zshrc 2>/dev/null; then
                echo 'export PATH="/opt/homebrew/opt/node@20/bin:$PATH"' >> ~/.zshrc
                echo "Added Node.js to PATH in ~/.zshrc"
                echo "Run: source ~/.zshrc"
            fi

            echo -e "${GREEN}✅ Node.js installed${NC}"
            /opt/homebrew/opt/node@20/bin/node --version
            ;;

        RHEL/Fedora)
            echo "Installing Node.js 20 on RHEL/Fedora..."

            # Install from NodeSource repository
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            sudo dnf install -y nodejs

            echo -e "${GREEN}✅ Node.js installed${NC}"
            node --version
            ;;

        Debian/Ubuntu)
            echo "Installing Node.js 20 on Debian/Ubuntu..."

            # Install from NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs

            echo -e "${GREEN}✅ Node.js installed${NC}"
            node --version
            ;;

        *)
            echo -e "${RED}ERROR: Cannot install Node.js automatically${NC}"
            echo "Please install Node.js 18+ manually:"
            echo "  https://nodejs.org/"
            exit 1
            ;;
    esac
fi

echo

# ==============================================================================
# STEP 3: Install NotebookLM CLI
# ==============================================================================

echo "========================================================================"
echo "STEP 3: NOTEBOOKLM CLI INSTALLATION"
echo "========================================================================"
echo

if command -v notebooklm &> /dev/null; then
    echo -e "${GREEN}✅ NotebookLM CLI is already installed${NC}"
    notebooklm --version 2>/dev/null || echo "notebooklm-py $(npm list -g notebooklm 2>/dev/null | grep notebooklm | awk '{print $2}')"
else
    echo "Installing NotebookLM CLI via npm..."
    echo

    # Install globally
    if [[ "$OS" == "macOS" ]]; then
        npm install -g notebooklm
    else
        sudo npm install -g notebooklm
    fi

    echo
    echo -e "${GREEN}✅ NotebookLM CLI installed${NC}"
    notebooklm --version 2>/dev/null || echo "Installation complete"
fi

echo

# ==============================================================================
# SETUP COMPLETE
# ==============================================================================

echo "========================================================================"
echo "ENVIRONMENT SETUP COMPLETE"
echo "========================================================================"
echo
echo -e "${GREEN}Installed Components:${NC}"
echo "  ✅ Podman: $(podman --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ NotebookLM CLI: $(command -v notebooklm &>/dev/null && echo 'Installed' || echo 'Not installed')"
echo

echo -e "${BLUE}Next Steps:${NC}"
echo
echo "  1. Create Google service account (see SERVICE-ACCOUNT-SETUP.md)"
echo
echo "  2. Configure vars.py with your clients:"
echo "     cp example-vars.py vars.py"
echo "     nano vars.py"
echo
echo "  3. Authenticate with NotebookLM:"
echo "     notebooklm login"
echo
echo "  4. Setup credentials for container:"
echo "     ./setup-credentials.sh"
echo
echo "  5. Launch Project APE:"
echo "     ./launch_ape.sh fast     # Fast mode (15-20 min)"
echo "     ./launch_ape.sh deep     # Deep mode (35-40 min)"
echo
echo "  6. Monitor progress:"
echo "     http://localhost:8765"
echo
echo "  7. View results in your NotebookLM account:"
echo "     https://notebooklm.google.com"
echo

echo -e "${BLUE}Useful Commands:${NC}"
echo "  notebooklm login                   # Authenticate with NotebookLM"
echo "  notebooklm list                    # List your notebooks"
echo "  podman images                      # List container images"
echo "  podman ps                          # List running containers"
echo

echo "For detailed documentation, see:"
echo "  README.md                          # Complete user guide"
echo "  EXECUTIVE-SUMMARY.md               # Why Project APE?"
echo "  SERVICE-ACCOUNT-SETUP.md           # Service account creation"
echo "  GETTING-STARTED.md                 # Step-by-step walkthrough"
echo
