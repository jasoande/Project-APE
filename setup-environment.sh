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
echo "  2. Python 3.14+ (required for NotebookLM CLI)"
echo "  3. NotebookLM CLI (notebooklm-py with browser support)"
echo
echo "NOTE: Project APE runs in a pre-built container - no other dependencies needed."
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
# STEP 2: Install Python 3 (required for NotebookLM CLI)
# ==============================================================================

echo "========================================================================"
echo "STEP 2: PYTHON 3.14+ INSTALLATION"
echo "========================================================================"
echo
echo "NotebookLM CLI requires Python 3.10+ (Python 3.14 recommended)"
echo

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    echo "Current Python 3: ${PYTHON_VERSION}"

    # Check if version is at least 3.10
    if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 10 ]]; then
        echo -e "${YELLOW}⚠️  Python ${PYTHON_VERSION} is too old (need 3.10+)${NC}"
        echo "Upgrading to Python 3.14..."
        NEED_UPGRADE=true
    else
        echo -e "${GREEN}✅ Python version is compatible${NC}"
        NEED_UPGRADE=false
    fi
else
    echo "Python 3 not found. Installing Python 3.14..."
    NEED_UPGRADE=true
fi

if [[ "$NEED_UPGRADE" == "true" ]]; then
    case $OS in
        macOS)
            echo "Installing Python 3 via Homebrew..."
            brew install python3

            echo -e "${GREEN}✅ Python 3 installed${NC}"
            python3 --version
            ;;

        RHEL/Fedora)
            echo "Installing Python 3.14 on RHEL/Fedora..."
            sudo dnf install -y python3.14 python3.14-pip

            # Update alternatives to make python3 point to 3.14
            if command -v python3.14 &> /dev/null; then
                echo "Setting python3 to use Python 3.14..."
                sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1
                sudo alternatives --set python3 /usr/bin/python3.14
            fi

            echo -e "${GREEN}✅ Python 3.14 installed${NC}"
            python3 --version
            ;;

        Debian/Ubuntu)
            echo "Installing Python 3.14 on Debian/Ubuntu..."
            sudo apt-get update
            sudo apt-get install -y python3.14 python3.14-pip python3.14-venv

            # Update alternatives to make python3 point to 3.14
            if command -v python3.14 &> /dev/null; then
                echo "Setting python3 to use Python 3.14..."
                sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1
                sudo update-alternatives --set python3 /usr/bin/python3.14
            fi

            echo -e "${GREEN}✅ Python 3.14 installed${NC}"
            python3 --version
            ;;

        *)
            echo -e "${RED}ERROR: Cannot install Python 3 automatically${NC}"
            echo "Please install Python 3.14+ manually"
            exit 1
            ;;
    esac
fi

# Check for pip3 and ensure it's installed for the current Python 3 version
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 not found, installing...${NC}"
    case $OS in
        macOS)
            brew install python3
            ;;
        RHEL/Fedora)
            # Try to install pip for the current python3 version
            PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
            echo "Installing pip for Python ${PYTHON_VERSION}..."

            # Try version-specific pip first (e.g., python3.14-pip)
            if ! sudo dnf install -y python${PYTHON_VERSION}-pip 2>/dev/null; then
                # Fall back to generic python3-pip
                sudo dnf install -y python3-pip
            fi

            # If still no pip, use ensurepip
            if ! command -v pip3 &> /dev/null; then
                echo "Using ensurepip as fallback..."
                python3 -m ensurepip --user
                python3 -m pip install --upgrade pip --user
            fi
            ;;
        Debian/Ubuntu)
            sudo apt-get install -y python3-pip
            ;;
    esac
fi

# Verify pip3 is working
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip module not found for python3, installing via ensurepip...${NC}"
    python3 -m ensurepip --user
    python3 -m pip install --upgrade pip --user
fi

echo

# ==============================================================================
# STEP 3: Install NotebookLM CLI (Python version with browser support)
# ==============================================================================

echo "========================================================================"
echo "STEP 3: NOTEBOOKLM CLI INSTALLATION"
echo "========================================================================"
echo

if command -v notebooklm &> /dev/null; then
    NOTEBOOKLM_VERSION=$(notebooklm --version 2>&1 | head -1)
    if [[ "$NOTEBOOKLM_VERSION" == *"0.7"* ]] || [[ "$NOTEBOOKLM_VERSION" == *"NotebookLM CLI"* ]]; then
        echo -e "${GREEN}✅ NotebookLM CLI is already installed${NC}"
        notebooklm --version
    else
        echo -e "${YELLOW}⚠️  Found different notebooklm version, reinstalling...${NC}"
        python3 -m pip uninstall -y notebooklm notebooklm-py 2>/dev/null || true
    fi
fi

if ! command -v notebooklm &> /dev/null || ! notebooklm --version 2>&1 | grep -q "NotebookLM CLI"; then
    echo "Installing NotebookLM CLI (Python) with browser support..."
    echo
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Using Python ${PYTHON_VERSION}"
    echo

    # Install notebooklm-py with browser support using python3 -m pip
    # This ensures it's installed for the correct Python version
    python3 -m pip install --user notebooklm-py[browser]

    # Ensure ~/.local/bin is in PATH
    if [[ "$OS" == "macOS" ]]; then
        if ! grep -q '$HOME/.local/bin' ~/.zshrc 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            echo "Added ~/.local/bin to PATH in ~/.zshrc"
        fi
        export PATH="$HOME/.local/bin:$PATH"
    else
        if ! grep -q '$HOME/.local/bin' ~/.bashrc 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            echo "Added ~/.local/bin to PATH in ~/.bashrc"
        fi
        export PATH="$HOME/.local/bin:$PATH"
    fi

    echo
    echo "Installing Playwright browser (Chromium)..."

    # Install Playwright browsers (use full path since it was just installed)
    if [[ "$OS" == "macOS" ]]; then
        # macOS: Install chromium directly
        $HOME/.local/bin/playwright install chromium
    else
        # Linux: Install chromium
        $HOME/.local/bin/playwright install chromium

        # Install X11 and system dependencies for browser on Linux
        echo
        echo "Installing X11 and browser system dependencies..."
        case $OS in
            RHEL/Fedora)
                sudo dnf install -y \
                    libX11 libXcomposite libXdamage libXext \
                    libXrandr nss cups-libs libdrm \
                    mesa-libgbm pango alsa-lib \
                    at-spi2-atk gtk3
                ;;
            Debian/Ubuntu)
                sudo apt-get install -y \
                    xvfb \
                    libx11-6 libxcomposite1 libxdamage1 \
                    libxext6 libxrandr2 libnss3 \
                    libcups2 libdrm2 libgbm1 \
                    libpango-1.0-0 libasound2 \
                    libatk-bridge2.0-0 libgtk-3-0
                ;;
        esac
    fi

    echo
    echo -e "${GREEN}✅ NotebookLM CLI installed${NC}"
    notebooklm --version
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
echo "  ✅ Python 3: $(python3 --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ NotebookLM CLI: $(notebooklm --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ Playwright: $(playwright --version 2>/dev/null || echo 'Installed with notebooklm')"
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
if [[ "$OS" == "RHEL/Fedora" ]] || [[ "$OS" == "Debian/Ubuntu" ]]; then
    echo -e "${YELLOW}     NOTE (Linux/SSH users):${NC}"
    echo "     If connecting via SSH, use: ssh -X -Y user@host"
    echo "     Or use xvfb-run: xvfb-run notebooklm login"
    echo
fi
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
