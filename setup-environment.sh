#!/bin/bash
# Project APE - Complete Environment Setup Script
# Installs Podman, Node.js, and NotebookLM CLI

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
echo "This script will install:"
echo "  1. Podman (container runtime)"
echo "  2. Node.js (required for NotebookLM CLI)"
echo "  3. NotebookLM CLI (notebooklm-py)"
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
# STEP 4: Python Dependencies (optional - for local execution)
# ==============================================================================

echo "========================================================================"
echo "STEP 4: PYTHON DEPENDENCIES (OPTIONAL)"
echo "========================================================================"
echo

if [ -f "requirements.txt" ]; then
    echo "Found requirements.txt"
    echo
    read -p "Install Python dependencies for local execution? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Python dependencies..."
        pip3 install -r requirements.txt
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo "Skipped Python dependencies (can install later with: pip3 install -r requirements.txt)"
    fi
else
    echo "No requirements.txt found - skipping Python dependencies"
fi

echo

# ==============================================================================
# STEP 5: Authenticate with NotebookLM
# ==============================================================================

echo "========================================================================"
echo "STEP 5: NOTEBOOKLM AUTHENTICATION"
echo "========================================================================"
echo

if [ -f "$HOME/.notebooklm/credentials.json" ]; then
    echo -e "${GREEN}✅ NotebookLM credentials found${NC}"
    echo "Credentials: $HOME/.notebooklm/credentials.json"
    echo
    read -p "Re-authenticate? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing credentials"
    else
        echo "Opening browser for authentication..."
        notebooklm login
    fi
else
    echo "NotebookLM authentication required"
    echo
    echo "This will open a browser for Google authentication..."
    echo
    read -p "Continue? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        notebooklm login
        echo
        echo -e "${GREEN}✅ NotebookLM authentication complete${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipped authentication${NC}"
        echo "Run 'notebooklm login' later to authenticate"
    fi
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
echo "  1. Configure vars.py with your client details:"
echo "     cp example-container.py vars.py"
echo "     nano vars.py"
echo
echo "  2. Add client data:"
echo "     mkdir -p client_data/YourClient"
echo "     cp /path/to/documents/* client_data/YourClient/"
echo
echo "  3a. Run locally (direct execution):"
echo "      python3 main.py --mode fast --clients yourclient"
echo
echo "  3b. Or run in container:"
echo "      ./ape-run.sh --vars ./vars.py --clients yourclient --mode fast"
echo
echo "  4. Access dashboard:"
echo "      http://localhost:8765"
echo
echo -e "${BLUE}Useful Commands:${NC}"
echo "  notebooklm login                   # Authenticate with NotebookLM"
echo "  notebooklm list                    # List your notebooks"
echo "  podman images                      # List container images"
echo "  podman ps                          # List running containers"
echo "  python3 main.py --help             # Show main.py options"
echo

echo "For detailed documentation, see:"
echo "  README.md - Complete user guide"
echo "  INSTALLATION.md - Installation troubleshooting"
echo "  QUICKSTART.md - 5-minute quick start"
echo
