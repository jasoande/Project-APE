#!/bin/bash
################################################################################
# Project APE - Universal Setup Script
#
# Supports: RHEL 8/9/10 and macOS
# Uses virtual environments to isolate dependencies
#
# Project Owner & Maintainer: Jason Anderson
# Version: 3.0.4
################################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        OS_VERSION=$(sw_vers -productVersion)
    elif [[ -f /etc/redhat-release ]]; then
        OS="rhel"
        RHEL_VERSION=$(rpm -E %{rhel} 2>/dev/null || echo "0")
        OS_VERSION="RHEL ${RHEL_VERSION}"
    else
        log_error "Unsupported OS. This script supports RHEL 8/9/10 and macOS only."
        exit 1
    fi

    log_info "Detected OS: ${OS_VERSION}"
}

# Check if running as root (RHEL only)
check_sudo() {
    if [[ "$OS" == "rhel" ]] && [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo on RHEL systems"
        exit 1
    fi

    if [[ "$OS" == "macos" ]] && [[ $EUID -eq 0 ]]; then
        log_error "Do NOT run this script with sudo on macOS"
        exit 1
    fi
}

# Determine regular user
get_regular_user() {
    if [[ "$OS" == "rhel" ]]; then
        if [ -n "$SUDO_USER" ]; then
            REGULAR_USER=$SUDO_USER
            USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
        else
            REGULAR_USER=$(whoami)
            USER_HOME=$HOME
        fi
    else
        # macOS
        REGULAR_USER=$(whoami)
        USER_HOME=$HOME
    fi

    log_info "Setting up for user: ${REGULAR_USER}"
}

# Install system dependencies - RHEL
install_rhel_deps() {
    log_info "Step 1: Updating system packages..."
    dnf update -y
    log_success "System updated"
    echo ""

    # Install EPEL
    log_info "Step 2: Installing EPEL repository..."
    if [[ "$RHEL_VERSION" == "10" ]]; then
        log_info "RHEL 10 detected - installing EPEL from direct URL..."
        dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm || {
            log_warning "EPEL installation failed - continuing without it"
        }
    elif [[ "$RHEL_VERSION" == "9" ]]; then
        dnf install -y epel-release || {
            dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
        }
    elif [[ "$RHEL_VERSION" == "8" ]]; then
        dnf install -y epel-release || {
            dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
        }
    fi
    log_success "EPEL setup complete"
    echo ""

    # Core dependencies
    log_info "Step 3: Installing core dependencies..."
    dnf install -y \
        git \
        curl \
        wget \
        vim \
        nano \
        jq \
        unzip \
        tar \
        gcc \
        gcc-c++ \
        make \
        openssl-devel \
        bzip2-devel \
        libffi-devel \
        zlib-devel \
        sqlite-devel \
        readline-devel \
        liberation-fonts

    log_success "Core dependencies installed"
    echo ""

    # Python 3.11+
    log_info "Step 4: Installing Python 3.11+..."
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        python3-setuptools

    # python3-wheel may not be available on RHEL 10
    dnf install -y python3-wheel 2>/dev/null || pip3 install --upgrade wheel

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_success "Python ${PYTHON_VERSION} installed"
    echo ""

    # Podman
    log_info "Step 5: Installing Podman and container tools..."
    dnf install -y \
        podman \
        buildah \
        skopeo \
        containers-common

    # Start Podman
    log_info "Starting Podman for user ${REGULAR_USER}..."
    loginctl enable-linger "$REGULAR_USER" 2>/dev/null || true
    sudo -u "$REGULAR_USER" systemctl --user enable podman.socket 2>/dev/null || true
    sudo -u "$REGULAR_USER" systemctl --user start podman.socket 2>/dev/null || true

    PODMAN_VERSION=$(podman --version | awk '{print $3}')
    log_success "Podman ${PODMAN_VERSION} installed"

    if sudo -u "$REGULAR_USER" podman info >/dev/null 2>&1; then
        log_success "Podman is ready and functional"
    else
        log_warning "Podman may need manual initialization"
    fi
    echo ""

    # LibreOffice
    log_info "Step 6: Installing LibreOffice for document conversion..."
    if [[ "$RHEL_VERSION" == "10" ]]; then
        log_warning "LibreOffice packages not available in RHEL 10 base repositories"
        log_info "Project APE will work with PDF files only (Office conversion unavailable)"
    else
        dnf install -y \
            libreoffice-core \
            libreoffice-writer \
            libreoffice-calc \
            libreoffice-impress \
            libreoffice-headless 2>/dev/null || {
            log_warning "LibreOffice installation failed - PDF-only mode"
        }
        log_success "LibreOffice installed"
    fi
    echo ""

    # Google Chrome
    log_info "Step 7: Installing Google Chrome..."
    cat > /etc/yum.repos.d/google-chrome.repo <<'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF

    dnf install -y google-chrome-stable
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
    log_success "Google Chrome ${CHROME_VERSION} installed"
    echo ""

    # Configure Podman rootless
    log_info "Step 8: Configuring Podman for rootless mode..."
    if ! grep -q "^${REGULAR_USER}:" /etc/subuid; then
        echo "${REGULAR_USER}:100000:65536" >> /etc/subuid
    fi
    if ! grep -q "^${REGULAR_USER}:" /etc/subgid; then
        echo "${REGULAR_USER}:100000:65536" >> /etc/subgid
    fi
    log_success "Podman rootless mode configured"
    echo ""
}

# Install system dependencies - macOS
install_macos_deps() {
    log_info "Step 1: Checking Homebrew..."
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew not installed. Install it first:"
        log_error '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    log_success "Homebrew found"
    echo ""

    log_info "Step 2: Installing system dependencies via Homebrew..."
    brew install \
        git \
        curl \
        wget \
        jq \
        podman \
        pyenv \
        libreoffice

    log_success "System dependencies installed"
    echo ""

    log_info "Step 3: Installing Google Chrome..."
    if ! brew list --cask google-chrome &> /dev/null; then
        brew install --cask google-chrome
        log_success "Google Chrome installed"
    else
        log_success "Google Chrome already installed"
    fi
    echo ""

    log_info "Step 4: Setting up pyenv..."
    # Add pyenv to shell profile if not already there
    SHELL_PROFILE="${HOME}/.zshrc"
    if [[ ! -f "$SHELL_PROFILE" ]]; then
        SHELL_PROFILE="${HOME}/.bash_profile"
    fi

    if ! grep -q 'pyenv init' "$SHELL_PROFILE" 2>/dev/null; then
        cat >> "$SHELL_PROFILE" <<'EOF'

# pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
EOF
        log_success "Added pyenv to ${SHELL_PROFILE}"
    fi

    # Initialize pyenv for this session
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)" 2>/dev/null || true
    eval "$(pyenv init -)" 2>/dev/null || true

    log_info "Installing Python 3.11 via pyenv..."
    if ! pyenv versions | grep -q "3.11"; then
        pyenv install 3.11
    fi
    pyenv global 3.11

    PYTHON_VERSION=$(python --version | awk '{print $2}')
    log_success "Python ${PYTHON_VERSION} installed via pyenv"
    echo ""

    log_info "Step 5: Initializing Podman..."
    podman machine init 2>/dev/null || log_info "Podman machine already initialized"
    podman machine start 2>/dev/null || log_info "Podman machine already running"
    log_success "Podman ready"
    echo ""
}

# Create directory structure and clone repo
setup_project_directory() {
    log_info "Creating account_planning directory structure..."

    ACCOUNT_PLANNING_DIR="${USER_HOME}/account_planning"

    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" mkdir -p "$ACCOUNT_PLANNING_DIR"
    else
        mkdir -p "$ACCOUNT_PLANNING_DIR"
    fi

    log_success "Created directory: ${ACCOUNT_PLANNING_DIR}"
    echo ""

    log_info "Cloning Project APE repository..."
    cd "$ACCOUNT_PLANNING_DIR"

    if [ -d "Project-APE" ]; then
        log_warning "Project-APE directory already exists, pulling latest changes..."
        cd Project-APE
        if [[ "$OS" == "rhel" ]]; then
            sudo -u "$REGULAR_USER" git pull
        else
            git pull
        fi
    else
        if [[ "$OS" == "rhel" ]]; then
            sudo -u "$REGULAR_USER" git clone https://github.com/jasoande/Project-APE.git
        else
            git clone https://github.com/jasoande/Project-APE.git
        fi
        cd Project-APE
    fi

    # Switch to QA branch
    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" git checkout QA
    else
        git checkout QA
    fi

    log_success "Project APE cloned to: ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo ""
}

# Create virtual environment and install Python packages
setup_virtualenv() {
    log_info "Creating Python virtual environment..."

    cd "${ACCOUNT_PLANNING_DIR}/Project-APE"

    # Create venv
    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" python3 -m venv venv
    else
        python -m venv venv
    fi

    log_success "Virtual environment created: venv/"
    echo ""

    log_info "Installing Python packages in virtual environment..."

    # Activate and install
    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" bash -c "
            source venv/bin/activate
            pip install --upgrade pip setuptools wheel
            pip install 'notebooklm-py[browser]'
            pip install flask requests pypdf reportlab Pillow python-magic
            python -m playwright install chromium
        "
    else
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        pip install 'notebooklm-py[browser]'
        pip install flask requests pypdf reportlab Pillow python-magic
        python -m playwright install chromium
    fi

    log_success "Python packages installed in virtual environment"
    echo ""

    # Create working directories
    log_info "Creating working directories..."
    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" mkdir -p client_data logs
    else
        mkdir -p client_data logs
    fi
    log_success "Working directories created"
    echo ""
}

# Pull container image
pull_container_image() {
    log_info "Pulling Project APE container image..."

    cd "${ACCOUNT_PLANNING_DIR}/Project-APE"

    if [[ "$OS" == "rhel" ]]; then
        if sudo -u "$REGULAR_USER" podman pull quay.io/jasoande/project_ape/project-ape:latest 2>/dev/null; then
            log_success "Container image pulled"
        else
            log_warning "Failed to pull container image"
            log_info "You can build locally: podman build -t project-ape:latest -f Containerfile ."
        fi
    else
        if podman pull quay.io/jasoande/project_ape/project-ape:latest 2>/dev/null; then
            log_success "Container image pulled"
        else
            log_warning "Failed to pull container image"
            log_info "You can build locally: podman build -t project-ape:latest -f Containerfile ."
        fi
    fi
    echo ""
}

# Configure firewall (RHEL only)
configure_firewall() {
    if [[ "$OS" == "rhel" ]] && systemctl is-active --quiet firewalld; then
        log_info "Configuring firewall for dashboard..."
        firewall-cmd --permanent --add-port=8765/tcp || true
        firewall-cmd --reload || true
        log_success "Firewall configured (port 8765 opened for dashboard)"
        echo ""
    fi
}

# Create activation script
create_activation_script() {
    log_info "Creating activation script..."

    cd "${ACCOUNT_PLANNING_DIR}/Project-APE"

    cat > activate-ape.sh <<'EOF'
#!/bin/bash
# Project APE Environment Activation Script

# Activate Python virtual environment
source "$(dirname "$0")/venv/bin/activate"

# Set up environment
export PROJECT_APE_HOME="$(dirname "$0")"
export PATH="${PROJECT_APE_HOME}:${PATH}"

echo "✅ Project APE environment activated"
echo "   Python: $(python --version)"
echo "   Location: ${PROJECT_APE_HOME}"
echo ""
echo "To authenticate with NotebookLM:"
echo "  notebooklm login"
echo ""
echo "To run Project APE:"
echo "  ./ape-run.sh --vars ./vars.py --clients yourclient --mode fast"
echo ""
echo "To deactivate: deactivate"
EOF

    chmod +x activate-ape.sh

    if [[ "$OS" == "rhel" ]]; then
        chown "${REGULAR_USER}:${REGULAR_USER}" activate-ape.sh
    fi

    log_success "Created activation script: activate-ape.sh"
    echo ""
}

# Create example configuration
create_example_config() {
    log_info "Creating example configuration..."

    cd "${ACCOUNT_PLANNING_DIR}/Project-APE"

    if [[ "$OS" == "rhel" ]]; then
        sudo -u "$REGULAR_USER" cp example-container.py vars.py.example
    else
        cp example-container.py vars.py.example
    fi

    log_success "Example configuration created: vars.py.example"
    echo ""
}

# Print final instructions
print_instructions() {
    echo "========================================================================"
    echo -e "${GREEN}  ✅ PROJECT APE SETUP COMPLETE!${NC}"
    echo "========================================================================"
    echo ""
    echo "Installation Summary:"
    echo "  • OS: ${OS_VERSION}"
    echo "  • Python: $(python3 --version 2>/dev/null || echo 'See pyenv')"
    echo "  • Location: ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo "  • Virtual Environment: venv/"
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Navigate to Project APE:"
    echo "   cd ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo ""
    echo "2. Activate the virtual environment:"
    echo "   source activate-ape.sh"
    echo ""
    echo "3. Authenticate with NotebookLM:"
    if [[ "$OS" == "rhel" ]]; then
        echo "   ./notebooklm-auth.sh"
        echo "   (Requires X11 forwarding: ssh -X user@host)"
    else
        echo "   source venv/bin/activate"
        echo "   notebooklm login"
    fi
    echo ""
    echo "4. Set up credentials for container:"
    echo "   ./setup-credentials.sh"
    echo ""
    echo "5. Create your configuration:"
    echo "   cp example-container.py vars.py"
    echo "   nano vars.py  # Edit with your client details"
    echo ""
    echo "6. Add client documents:"
    echo "   mkdir -p client_data/YourClient"
    echo "   cp /path/to/documents/* client_data/YourClient/"
    echo ""
    echo "7. Run Project APE:"
    echo "   ./ape-run.sh --vars ./vars.py --clients yourclient --mode fast"
    echo ""
    echo "8. View dashboard:"
    echo "   http://localhost:8765"
    echo ""
    echo "Documentation:"
    echo "  • Quick Start: ${ACCOUNT_PLANNING_DIR}/Project-APE/QUICKSTART.md"
    echo "  • Full README: ${ACCOUNT_PLANNING_DIR}/Project-APE/README.md"
    echo "  • Testing Guide: ${ACCOUNT_PLANNING_DIR}/Project-APE/TESTING-GUIDE.md"
    echo ""
    echo "========================================================================"
    echo -e "${BLUE}Project APE v3.0.4 - Ready to revolutionize account planning!${NC}"
    echo "========================================================================"
    echo ""
}

# Main execution
main() {
    echo "========================================================================"
    echo "  PROJECT APE - UNIVERSAL SETUP"
    echo "  Account Planning Engine Installation"
    echo "  Supports: RHEL 8/9/10 and macOS"
    echo "========================================================================"
    echo ""

    detect_os
    check_sudo
    get_regular_user

    if [[ "$OS" == "rhel" ]]; then
        install_rhel_deps
    else
        install_macos_deps
    fi

    setup_project_directory
    setup_virtualenv
    pull_container_image
    configure_firewall
    create_activation_script
    create_example_config
    print_instructions
}

# Run main function
main

exit 0
