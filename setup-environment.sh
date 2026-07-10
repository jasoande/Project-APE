#!/bin/bash
# project ape Account Intelligence - Environment Setup Script
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
echo "This script will install the required tools for running project ape Account Intelligence:"
echo
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  0. Homebrew (package manager for macOS, if not installed)"
fi
echo "  1. Podman (container runtime)"
echo "  2. Python 3.10+ (required for NotebookLM CLI)"
echo "  3. Virtual Environment (isolated Python environment)"
echo "  4. NotebookLM CLI (notebooklm-py with browser support)"
echo
echo "NOTE: project ape Account Intelligence pipeline runs in a pre-built container."
echo "      Only NotebookLM CLI runs on your host machine."
echo

# Skip prompt if running in auto-setup mode (called from launcher)
if [[ -z "$AUTO_SETUP" ]]; then
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    echo
else
    echo "Running in automatic mode..."
    echo
fi

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
# STEP 0: Homebrew Installation (macOS only)
# ==============================================================================

if [[ "$OS" == "macOS" ]]; then
    echo "========================================================================"
    echo "STEP 0: HOMEBREW VERIFICATION (macOS)"
    echo "========================================================================"
    echo
    echo "Homebrew is the package manager for macOS and is required for:"
    echo "  - Podman (container runtime)"
    echo "  - Python 3 (if not already installed)"
    echo

    if command -v brew &> /dev/null; then
        echo -e "${GREEN}✅ Homebrew is already installed${NC}"
        BREW_VERSION=$(brew --version | head -1)
        echo "   ${BREW_VERSION}"
        echo "   Location: $(which brew)"

        # Check if brew is in PATH properly
        if [[ "$(which brew)" == "/opt/homebrew/bin/brew" ]] || [[ "$(which brew)" == "/usr/local/bin/brew" ]]; then
            echo -e "${GREEN}✅ Homebrew is properly configured in PATH${NC}"
        else
            echo -e "${YELLOW}⚠️  Homebrew found at unusual location: $(which brew)${NC}"
        fi

        # Update Homebrew to latest version
        echo
        echo "Updating Homebrew to latest version..."
        brew update || {
            echo -e "${YELLOW}⚠️  Homebrew update failed, but continuing...${NC}"
            echo "   You may want to run 'brew doctor' later to check for issues"
        }

    else
        echo -e "${YELLOW}⚠️  Homebrew is not installed${NC}"
        echo
        echo "Homebrew must be installed before continuing."
        echo

        # In auto-setup mode, proceed with installation automatically
        if [[ -n "$AUTO_SETUP" ]]; then
            echo "Automatic mode: Installing Homebrew..."
            echo
            INSTALL_BREW=true
        else
            echo "Would you like to install Homebrew now? (Recommended)"
            echo
            read -p "Install Homebrew? (y/n) " -n 1 -r
            echo
            INSTALL_BREW=false
            [[ $REPLY =~ ^[Yy]$ ]] && INSTALL_BREW=true
        fi

        if $INSTALL_BREW; then
            echo
            echo "========================================================================"
            echo "INSTALLING HOMEBREW"
            echo "========================================================================"
            echo
            echo "The Homebrew installation script will:"
            echo "  1. Download and install Homebrew"
            echo "  2. Install Command Line Tools for Xcode (if needed)"
            echo "  3. Configure your shell environment"
            echo
            echo "This may take 5-10 minutes and will require your password."
            echo

            # In auto-setup mode, skip the second confirmation
            if [[ -z "$AUTO_SETUP" ]]; then
                read -p "Continue with Homebrew installation? (y/n) " -n 1 -r
                echo

                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo
                    echo -e "${RED}ERROR: Homebrew is required for project ape Account Intelligence on macOS${NC}"
                    echo
                    echo "To install Homebrew manually, run:"
                    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                    echo
                    echo "Then run this setup script again."
                    exit 1
                fi
            fi

            echo
            echo "Installing Homebrew..."
            echo

            # Run official Homebrew installation script
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

            if [ $? -ne 0 ]; then
                echo
                echo -e "${RED}ERROR: Homebrew installation failed${NC}"
                echo
                echo "Please install Homebrew manually:"
                echo "  1. Visit: https://brew.sh"
                echo "  2. Follow the installation instructions"
                echo "  3. Run this setup script again"
                exit 1
            fi

            echo
            echo -e "${GREEN}✅ Homebrew installed successfully${NC}"
            echo

            # Detect architecture for proper brew path
            ARCH=$(uname -m)
            if [[ "$ARCH" == "arm64" ]]; then
                # Apple Silicon (M1/M2/M3/M4)
                BREW_PREFIX="/opt/homebrew"
                BREW_BIN="${BREW_PREFIX}/bin/brew"
            else
                # Intel Mac
                BREW_PREFIX="/usr/local"
                BREW_BIN="${BREW_PREFIX}/bin/brew"
            fi

            # Add Homebrew to PATH for this session
            if [ -f "$BREW_BIN" ]; then
                echo "Configuring Homebrew in current session..."
                eval "$($BREW_BIN shellenv)"

                # Verify brew is now available
                if command -v brew &> /dev/null; then
                    echo -e "${GREEN}✅ Homebrew is now available in PATH${NC}"
                    echo "   Location: $(which brew)"
                else
                    echo -e "${RED}ERROR: Homebrew installed but not in PATH${NC}"
                    echo
                    echo "Please add Homebrew to your PATH manually:"
                    if [[ "$ARCH" == "arm64" ]]; then
                        echo '  echo '\''eval "$(/opt/homebrew/bin/brew shellenv)"'\'' >> ~/.zprofile'
                        echo '  eval "$(/opt/homebrew/bin/brew shellenv)"'
                    else
                        echo '  echo '\''eval "$(/usr/local/bin/brew shellenv)"'\'' >> ~/.zprofile'
                        echo '  eval "$(/usr/local/bin/brew shellenv)"'
                    fi
                    exit 1
                fi

                # Configure shell profile for future sessions
                echo
                echo "Configuring shell profile for future sessions..."

                # Determine which shell profile to use
                if [[ -f "$HOME/.zprofile" ]] || [[ "$SHELL" == *"zsh"* ]]; then
                    PROFILE_FILE="$HOME/.zprofile"
                    SHELL_NAME="zsh"
                elif [[ -f "$HOME/.bash_profile" ]]; then
                    PROFILE_FILE="$HOME/.bash_profile"
                    SHELL_NAME="bash"
                else
                    PROFILE_FILE="$HOME/.profile"
                    SHELL_NAME="sh"
                fi

                # Add brew shellenv to profile if not already present
                BREW_SHELLENV_CMD="eval \"\$($BREW_BIN shellenv)\""
                if ! grep -q "brew shellenv" "$PROFILE_FILE" 2>/dev/null; then
                    echo
                    echo "Adding Homebrew to $PROFILE_FILE..."
                    echo "" >> "$PROFILE_FILE"
                    echo "# Homebrew" >> "$PROFILE_FILE"
                    echo "$BREW_SHELLENV_CMD" >> "$PROFILE_FILE"
                    echo -e "${GREEN}✅ Homebrew added to $PROFILE_FILE${NC}"
                else
                    echo -e "${GREEN}✅ Homebrew already configured in $PROFILE_FILE${NC}"
                fi

                echo
                echo -e "${BLUE}NOTE:${NC} For Homebrew to work in new terminal sessions, either:"
                echo "  1. Close and reopen your terminal, OR"
                echo "  2. Run: source $PROFILE_FILE"
                echo

            else
                echo -e "${RED}ERROR: Homebrew binary not found at expected location${NC}"
                echo "   Expected: $BREW_BIN"
                echo
                echo "Please check your Homebrew installation:"
                echo "  brew doctor"
                exit 1
            fi

        else
            echo
            echo -e "${RED}ERROR: Homebrew is required for project ape Account Intelligence on macOS${NC}"
            echo
            echo "To install Homebrew manually later:"
            echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            echo
            echo "Then run this setup script again."
            exit 1
        fi
    fi

    # Verify Homebrew is working properly
    echo
    echo "Verifying Homebrew installation..."
    if brew --version &> /dev/null; then
        echo -e "${GREEN}✅ Homebrew is working correctly${NC}"

        # Optional: Run brew doctor for diagnostics (non-blocking)
        echo
        echo "Running Homebrew diagnostics..."
        if brew doctor &> /tmp/brew-doctor.log; then
            echo -e "${GREEN}✅ Homebrew health check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Homebrew has some warnings (non-critical)${NC}"
            echo "   See /tmp/brew-doctor.log for details"
            echo "   You can run 'brew doctor' manually to review"
        fi
    else
        echo -e "${RED}ERROR: Homebrew is not functioning properly${NC}"
        echo
        echo "Please run 'brew doctor' to diagnose issues"
        exit 1
    fi

    echo
fi

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
    PODMAN_INSTALLED=true
else
    PODMAN_INSTALLED=false
    case $OS in
        macOS)
            echo "Installing Podman on macOS..."
            echo
            echo "Please download and install Podman Desktop from:"
            echo "  https://podman-desktop.io/downloads"
            echo
            echo "Download the macOS .dmg installer, open it, and drag Podman Desktop to Applications."
            echo "Then run Podman Desktop to complete setup."
            echo
            read -p "Press Enter after installing Podman Desktop..."

            # Verify installation
            if command -v podman &> /dev/null; then
                PODMAN_INSTALLED=true
                echo -e "${GREEN}✅ Podman installed successfully${NC}"
                podman --version
            else
                echo -e "${RED}❌ Podman not found. Please install from https://podman-desktop.io/downloads${NC}"
                exit 1
            fi
            ;;

        RHEL/Fedora)
            echo "Installing Podman on RHEL/Fedora..."
            echo

            sudo dnf install -y podman

            PODMAN_INSTALLED=true
            echo -e "${GREEN}✅ Podman installed successfully${NC}"
            podman --version
            ;;

        Debian/Ubuntu)
            echo "Installing Podman on Debian/Ubuntu..."
            echo

            sudo apt-get update
            sudo apt-get install -y podman

            PODMAN_INSTALLED=true
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

# macOS: Ensure Podman machine is initialized and running
if [[ "$OS" == "macOS" ]] && [[ "$PODMAN_INSTALLED" == "true" ]]; then
    echo
    echo "Checking Podman machine status..."

    # Check if any machine exists
    if ! podman machine list --format "{{.Name}}" 2>/dev/null | grep -q .; then
        echo "No Podman machine found. Initializing..."
        podman machine init
        echo -e "${GREEN}✅ Podman machine initialized${NC}"
    else
        echo -e "${GREEN}✅ Podman machine exists${NC}"
    fi

    # Check if machine is running
    MACHINE_RUNNING=$(podman machine list --format "{{.Running}}" 2>/dev/null | head -1)
    if [[ "$MACHINE_RUNNING" != "true" ]]; then
        echo "Starting Podman machine..."
        podman machine start
        echo -e "${GREEN}✅ Podman machine started${NC}"
    else
        echo -e "${GREEN}✅ Podman machine is running${NC}"
    fi

    # Verify Podman is responsive
    echo "Verifying Podman connection..."
    if podman ps &>/dev/null; then
        echo -e "${GREEN}✅ Podman is working correctly${NC}"
    else
        echo -e "${YELLOW}⚠️  Podman connection test failed${NC}"
        echo "   Try running: podman machine stop && podman machine start"
    fi
fi

echo

# ==============================================================================
# STEP 2: Install Google Cloud SDK
# ==============================================================================

echo "========================================================================"
echo "STEP 2: GOOGLE CLOUD SDK INSTALLATION"
echo "========================================================================"
echo

if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✅ Google Cloud SDK is already installed${NC}"
    gcloud --version | head -1
    GCLOUD_INSTALLED=true
else
    GCLOUD_INSTALLED=false
    case $OS in
        macOS)
            echo "Installing Google Cloud SDK on macOS via Homebrew..."
            echo

            # Install google-cloud-sdk cask
            brew install --cask google-cloud-sdk

            GCLOUD_INSTALLED=true
            echo -e "${GREEN}✅ Google Cloud SDK installed successfully${NC}"

            # Add gcloud to PATH for current session
            if [ -f "/opt/homebrew/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc" ]; then
                source "/opt/homebrew/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
            elif [ -f "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc" ]; then
                source "/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/path.bash.inc"
            fi

            gcloud --version | head -1
            ;;

        RHEL/Fedora)
            echo "Installing Google Cloud SDK on RHEL/Fedora..."
            echo

            # Detect architecture
            ARCH=$(uname -m)

            if [[ "$ARCH" == "x86_64" ]]; then
                # x86_64: Use official repo
                sudo tee /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM

                sudo dnf install -y google-cloud-cli
            else
                # ARM or other: Install from tarball
                echo "Detected $ARCH architecture - installing from tarball..."

                cd /tmp
                curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-arm.tar.gz
                tar -xf google-cloud-cli-linux-arm.tar.gz

                # Install to /opt and create symlinks
                sudo mkdir -p /opt
                sudo mv google-cloud-sdk /opt/
                sudo ln -sf /opt/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud
                sudo ln -sf /opt/google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil

                # Run install script (non-interactive)
                /opt/google-cloud-sdk/install.sh --quiet --usage-reporting=false --path-update=false

                cd -
            fi

            GCLOUD_INSTALLED=true
            echo -e "${GREEN}✅ Google Cloud SDK installed successfully${NC}"
            gcloud --version | head -1
            ;;

        Debian/Ubuntu)
            echo "Installing Google Cloud SDK on Debian/Ubuntu..."
            echo

            # Install dependencies
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates gnupg curl

            # Add Google Cloud SDK repo
            curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
            echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

            sudo apt-get update
            sudo apt-get install -y google-cloud-cli

            GCLOUD_INSTALLED=true
            echo -e "${GREEN}✅ Google Cloud SDK installed successfully${NC}"
            gcloud --version | head -1
            ;;

        *)
            echo -e "${YELLOW}⚠️  Unsupported OS for automatic Google Cloud SDK installation${NC}"
            echo
            echo "Please install Google Cloud SDK manually:"
            echo "  https://cloud.google.com/sdk/docs/install"
            echo
            echo "After installing, run this script again."
            exit 1
            ;;
    esac
fi

# Authenticate with gcloud
echo
echo "Checking Google Cloud authentication..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q "@"; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
    echo -e "${GREEN}✅ Already authenticated as: $ACTIVE_ACCOUNT${NC}"
else
    echo -e "${YELLOW}⚠️  Not authenticated with Google Cloud${NC}"
    echo
    echo "Opening browser for Google Cloud authentication..."
    echo "This will allow project ape Account Intelligence to create service accounts."
    echo

    gcloud auth login

    if [ $? -eq 0 ]; then
        ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
        echo -e "${GREEN}✅ Successfully authenticated as: $ACTIVE_ACCOUNT${NC}"
    else
        echo -e "${RED}❌ Google Cloud authentication failed${NC}"
        echo
        echo "You can authenticate later by running:"
        echo "  gcloud auth login"
        echo
        echo "Continuing setup..."
    fi
fi

echo

# ==============================================================================
# STEP 3: Install Python 3 (required for NotebookLM CLI)
# ==============================================================================

echo "========================================================================"
echo "STEP 3: PYTHON 3.10+ INSTALLATION"
echo "========================================================================"
echo
echo "NotebookLM CLI requires Python 3.10+ (Python 3.14 recommended)"
echo

# macOS: Prioritize Homebrew Python over system Python
if [[ "$OS" == "macOS" ]]; then
    # Check if Homebrew Python 3 is installed
    if [ -x "/opt/homebrew/bin/python3" ]; then
        PYTHON_CMD="/opt/homebrew/bin/python3"
    elif [ -x "/usr/local/bin/python3" ]; then
        PYTHON_CMD="/usr/local/bin/python3"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD=""
    fi
else
    # Linux: Use system python3
    PYTHON_CMD="python3"
fi

if [[ -n "$PYTHON_CMD" ]] && command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    echo "Current Python 3: ${PYTHON_VERSION}"
    echo "Using: $(which $PYTHON_CMD)"

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
            echo "Installing Python 3.14 via Homebrew..."
            brew install python@3.14

            # Update PYTHON_CMD to use newly installed Homebrew Python
            if [ -x "/opt/homebrew/bin/python3" ]; then
                PYTHON_CMD="/opt/homebrew/bin/python3"
            elif [ -x "/usr/local/bin/python3" ]; then
                PYTHON_CMD="/usr/local/bin/python3"
            else
                PYTHON_CMD="python3"
            fi

            echo -e "${GREEN}✅ Python 3.14 installed${NC}"
            $PYTHON_CMD --version
            echo "Using: $(which $PYTHON_CMD)"
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

            PYTHON_CMD="python3"
            echo -e "${GREEN}✅ Python 3.14 installed${NC}"
            $PYTHON_CMD --version
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

            PYTHON_CMD="python3"
            echo -e "${GREEN}✅ Python 3.14 installed${NC}"
            $PYTHON_CMD --version
            ;;

        *)
            echo -e "${RED}ERROR: Cannot install Python 3 automatically${NC}"
            echo "Please install Python 3.14+ manually"
            exit 1
            ;;
    esac
fi

# Verify pip is working with selected Python
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip module not found for $PYTHON_CMD, installing via ensurepip...${NC}"
    $PYTHON_CMD -m ensurepip --user
    $PYTHON_CMD -m pip install --upgrade pip --user
fi

echo

# ==============================================================================
# STEP 4: Create Virtual Environment for NotebookLM CLI
# ==============================================================================

echo "========================================================================"
echo "STEP 4: VIRTUAL ENVIRONMENT SETUP"
echo "========================================================================"
echo
echo "Creating isolated Python virtual environment for project ape Account Intelligence..."
echo

# Define virtual environment path
VENV_DIR="$HOME/.project-ape-venv"

# Check if virtual environment already exists and is valid
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python3" ]; then
    echo -e "${GREEN}✅ Virtual environment already exists: ${VENV_DIR}${NC}"

    # Verify Python version in venv is compatible
    VENV_PYTHON_VERSION=$("$VENV_DIR/bin/python3" --version 2>&1 | awk '{print $2}')
    VENV_PYTHON_MAJOR=$(echo $VENV_PYTHON_VERSION | cut -d. -f1)
    VENV_PYTHON_MINOR=$(echo $VENV_PYTHON_VERSION | cut -d. -f2)

    echo "Virtual environment Python: ${VENV_PYTHON_VERSION}"

    # Check if version is at least 3.10
    if [[ "$VENV_PYTHON_MAJOR" -lt 3 ]] || [[ "$VENV_PYTHON_MAJOR" -eq 3 && "$VENV_PYTHON_MINOR" -lt 10 ]]; then
        echo -e "${YELLOW}⚠️  Virtual environment Python ${VENV_PYTHON_VERSION} is too old${NC}"
        echo "Removing old virtual environment and recreating with Python $(${PYTHON_CMD} --version | awk '{print $2}')..."
        rm -rf "$VENV_DIR"
        NEED_CREATE_VENV=true
    else
        echo -e "${GREEN}✅ Virtual environment Python version is compatible${NC}"
        NEED_CREATE_VENV=false
    fi
else
    echo "Virtual environment not found. Creating new one..."
    NEED_CREATE_VENV=true
fi

# Create virtual environment if needed
if [[ "$NEED_CREATE_VENV" == "true" ]]; then
    echo "Creating virtual environment at: ${VENV_DIR}"
    echo "Using Python: $($PYTHON_CMD --version)"

    # Verify python has venv module
    if ! $PYTHON_CMD -m venv --help &> /dev/null; then
        echo -e "${YELLOW}⚠️  Python venv module not available${NC}"
        echo "Installing python venv..."

        case $OS in
            macOS)
                # macOS python3 from Homebrew includes venv by default
                echo "Python from Homebrew should include venv. Checking installation..."
                brew reinstall python@3.14
                ;;
            RHEL/Fedora)
                PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
                sudo dnf install -y python${PYTHON_VERSION}-venv || sudo dnf install -y python3-venv
                ;;
            Debian/Ubuntu)
                sudo apt-get install -y python3-venv
                ;;
        esac
    fi

    # Create the virtual environment using the selected Python
    $PYTHON_CMD -m venv "$VENV_DIR"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Virtual environment created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment for this script
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" == "$VENV_DIR" ]]; then
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    echo "   Python: $(which python3)"
    echo "   Version: $(python3 --version)"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Upgrade pip in virtual environment
echo "Upgrading pip in virtual environment..."
"$VENV_DIR/bin/python3" -m pip install --upgrade pip

echo

# ==============================================================================
# STEP 5: Install NotebookLM CLI in Virtual Environment
# ==============================================================================

echo "========================================================================"
echo "STEP 5: NOTEBOOKLM CLI INSTALLATION"
echo "========================================================================"
echo

# Check if notebooklm is already installed in venv
if [ -x "$VENV_DIR/bin/notebooklm" ]; then
    NOTEBOOKLM_VERSION=$("$VENV_DIR/bin/notebooklm" --version 2>&1 | head -1)
    if [[ "$NOTEBOOKLM_VERSION" == *"0.7"* ]] || [[ "$NOTEBOOKLM_VERSION" == *"NotebookLM CLI"* ]]; then
        echo -e "${GREEN}✅ NotebookLM CLI is already installed in virtual environment${NC}"
        "$VENV_DIR/bin/notebooklm" --version
        NEED_INSTALL_NOTEBOOKLM=false
    else
        echo -e "${YELLOW}⚠️  Found different notebooklm version, reinstalling...${NC}"
        "$VENV_DIR/bin/python3" -m pip uninstall -y notebooklm notebooklm-py 2>/dev/null || true
        NEED_INSTALL_NOTEBOOKLM=true
    fi
else
    NEED_INSTALL_NOTEBOOKLM=true
fi

if [[ "$NEED_INSTALL_NOTEBOOKLM" == "true" ]]; then
    echo "Installing NotebookLM CLI with browser support in virtual environment..."
    echo
    VENV_PYTHON_VERSION=$("$VENV_DIR/bin/python3" --version 2>&1 | awk '{print $2}')
    echo "Using Python ${VENV_PYTHON_VERSION}"
    echo

    # Install notebooklm-py with browser support in virtual environment
    "$VENV_DIR/bin/python3" -m pip install notebooklm-py[browser]

    # Install Google API libraries for Drive folder sharing automation
    echo
    echo "Installing Google Drive API libraries..."
    "$VENV_DIR/bin/python3" -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

    echo
    echo "Installing Playwright browser (Chromium)..."

    # Install Playwright browsers using venv's playwright command
    if [[ "$OS" == "macOS" ]]; then
        # macOS: Install chromium directly
        "$VENV_DIR/bin/playwright" install chromium
    else
        # Linux: Install chromium
        "$VENV_DIR/bin/playwright" install chromium

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
    echo -e "${GREEN}✅ NotebookLM CLI installed in virtual environment${NC}"
    "$VENV_DIR/bin/notebooklm" --version
fi

# ==============================================================================
# Install Flask, dashboard, and core dependencies (ALWAYS, even if NotebookLM exists)
# ==============================================================================

echo
echo "Installing web dashboard and core dependencies..."
"$VENV_DIR/bin/python3" -m pip install \
    flask>=3.0.0 \
    werkzeug>=3.0.0 \
    waitress>=3.0.0 \
    gevent>=24.0.0 \
    greenlet>=3.0.0 \
    python-dotenv>=1.0.0 \
    pypdf>=4.0.0 \
    Pillow>=10.0.0 \
    reportlab>=4.0.0

# ==============================================================================
# STEP 5: Create Activation Helper Script
# ==============================================================================

echo
echo "========================================================================"
echo "STEP 5: CREATING ACTIVATION HELPER"
echo "========================================================================"
echo

# Create activation helper script in project directory
ACTIVATION_SCRIPT="$(pwd)/activate-ape-env.sh"

cat > "$ACTIVATION_SCRIPT" << 'ACTIVATION_EOF'
#!/bin/bash
# project ape Account Intelligence - Virtual Environment Activation Script
# Source this script to activate the project ape Account Intelligence virtual environment

VENV_DIR="$HOME/.project-ape-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Run ./setup-environment.sh first"
    return 1 2>/dev/null || exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

if [[ "$VIRTUAL_ENV" == "$VENV_DIR" ]]; then
    echo "✅ project ape Account Intelligence virtual environment activated"
    echo "   Python: $(python3 --version)"
    echo "   NotebookLM CLI: $(notebooklm --version 2>&1 | head -1)"
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Failed to activate virtual environment"
    return 1 2>/dev/null || exit 1
fi
ACTIVATION_EOF

chmod +x "$ACTIVATION_SCRIPT"

echo -e "${GREEN}✅ Created activation helper script: activate-ape-env.sh${NC}"
echo "   Use 'source ./activate-ape-env.sh' to activate the environment in future sessions"

echo

# ==============================================================================
# SETUP COMPLETE
# ==============================================================================

echo
echo "========================================================================"
echo "ENVIRONMENT SETUP COMPLETE"
echo "========================================================================"
echo
echo -e "${GREEN}Installed Components:${NC}"
echo "  ✅ Podman: $(podman --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ System Python 3: $($PYTHON_CMD --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ Virtual Environment: $VENV_DIR"
echo "  ✅ Venv Python: $($VENV_DIR/bin/python3 --version 2>/dev/null || echo 'Not installed')"
echo "  ✅ NotebookLM CLI: $($VENV_DIR/bin/notebooklm --version 2>/dev/null | head -1 || echo 'Not installed')"
echo "  ✅ Playwright: $($VENV_DIR/bin/playwright --version 2>/dev/null || echo 'Installed with notebooklm')"
echo

echo -e "${BLUE}Virtual Environment Information:${NC}"
echo "  📁 Location: $VENV_DIR"
echo "  🔧 Activation: source ./activate-ape-env.sh"
echo "  ℹ️  Currently Active: YES (for this session only)"
echo

echo -e "${YELLOW}IMPORTANT - Virtual Environment Usage:${NC}"
echo "  The NotebookLM CLI is installed in an isolated virtual environment."
echo "  This keeps project ape Account Intelligence dependencies separate from your system Python."
echo
echo "  To use NotebookLM CLI in future terminal sessions:"
echo "    ${GREEN}source ./activate-ape-env.sh${NC}"
echo
echo "  To deactivate when done:"
echo "    ${GREEN}deactivate${NC}"
echo

echo -e "${BLUE}Next Steps:${NC}"
echo
echo "  1. Create Google service account:"
echo
echo "     ${GREEN}Option A (Automated):${NC} ./create-service-account.sh"
echo "     ${BLUE}Option B (Manual):${NC}    See SERVICE-ACCOUNT-SETUP.md"
echo
echo "  2. Configure vars.py with your clients:"
echo "     cp example-vars.py vars.py"
echo "     nano vars.py"
echo
echo "  3. ${YELLOW}ACTIVATE the virtual environment (important!):${NC}"
echo "     ${GREEN}source ./activate-ape-env.sh${NC}"
echo
echo "  4. Authenticate with NotebookLM:"
echo "     notebooklm login"
echo
if [[ "$OS" == "RHEL/Fedora" ]] || [[ "$OS" == "Debian/Ubuntu" ]]; then
    echo -e "${YELLOW}     NOTE (Linux/SSH users):${NC}"
    echo "     If connecting via SSH, use: ssh -X -Y user@host"
    echo "     Or use xvfb-run: xvfb-run notebooklm login"
    echo
fi
echo "  5. Setup credentials for container:"
echo "     ./setup-credentials.sh"
echo
echo "  6. Launch project ape Account Intelligence:"
echo "     ./launch_ape.sh fast     # Fast mode (15-20 min)"
echo "     ./launch_ape.sh deep     # Deep mode (35-40 min)"
echo
echo "  7. Monitor progress:"
echo "     http://localhost:8765"
echo
echo "  8. View results in your NotebookLM account:"
echo "     https://notebooklm.google.com"
echo

echo -e "${BLUE}Useful Commands (after activating venv):${NC}"
echo "  source ./activate-ape-env.sh       # Activate project ape Account Intelligence environment"
echo "  notebooklm login                   # Authenticate with NotebookLM"
echo "  notebooklm list                    # List your notebooks"
echo "  deactivate                         # Exit virtual environment"
echo "  podman images                      # List container images"
echo "  podman ps                          # List running containers"
echo

echo "For detailed documentation, see:"
echo "  README.md                          # Complete user guide"
echo "  EXECUTIVE-SUMMARY.md               # Why project ape Account Intelligence?"
echo "  SERVICE-ACCOUNT-SETUP.md           # Service account creation"
echo "  QUICKSTART.md                      # Quick reference"
echo
