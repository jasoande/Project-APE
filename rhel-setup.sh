#!/bin/bash
################################################################################
# Project APE - RHEL 10 Setup Script
#
# Prepares a fresh RHEL 10 system to run Project APE
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

# Check if running as root or with sudo
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo or as root"
        exit 1
    fi
}

# Main setup function
main() {
    echo "========================================================================"
    echo "  PROJECT APE - RHEL 10 SETUP"
    echo "  Account Planning Engine Installation"
    echo "========================================================================"
    echo ""

    log_info "Starting RHEL 10 setup for Project APE..."
    echo ""

    # Step 1: Update system
    log_info "Step 1: Updating system packages..."
    dnf update -y
    log_success "System updated"
    echo ""

    # Step 2: Install EPEL repository (if needed)
    log_info "Step 2: Installing EPEL repository..."

    # Detect RHEL version
    RHEL_VERSION=$(rpm -E %{rhel} 2>/dev/null || echo "0")

    if [[ "$RHEL_VERSION" == "10" ]]; then
        log_info "RHEL 10 detected - installing EPEL from direct URL..."
        dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm || {
            log_warning "EPEL installation failed - continuing without it (RHEL 10 may not need it)"
        }
    elif [[ "$RHEL_VERSION" == "9" ]]; then
        dnf install -y epel-release || {
            log_info "Trying direct EPEL 9 installation..."
            dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
        }
    elif [[ "$RHEL_VERSION" == "8" ]]; then
        dnf install -y epel-release || {
            log_info "Trying direct EPEL 8 installation..."
            dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
        }
    else
        log_warning "Unknown RHEL version - skipping EPEL installation"
    fi

    log_success "EPEL setup complete"
    echo ""

    # Step 3: Install core dependencies
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

    # Install Xvfb for headless browser automation (optional)
    log_info "Attempting to install Xvfb for headless browser automation..."
    dnf install -y xorg-x11-server-Xvfb 2>/dev/null || \
    dnf install -y xvfb 2>/dev/null || \
    log_warning "Xvfb not available in this RHEL version - browser auth will require X11 forwarding (ssh -X)"

    log_success "Core dependencies installed"
    echo ""

    # Step 4: Install Python 3.11+ (RHEL 10 should have Python 3.11 or newer)
    log_info "Step 4: Installing Python 3.11+..."
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        python3-setuptools

    # python3-wheel may not be available on RHEL 10, install via pip if needed
    if [[ "$RHEL_VERSION" == "10" ]]; then
        pip3 install --upgrade wheel || true
    else
        dnf install -y python3-wheel || pip3 install --upgrade wheel
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_success "Python ${PYTHON_VERSION} installed"
    echo ""

    # Step 5: Install Podman and container tools
    log_info "Step 5: Installing Podman and container tools..."
    dnf install -y \
        podman \
        podman-compose \
        buildah \
        skopeo \
        containers-common

    # Determine the regular user (will be used throughout script)
    if [ -n "$SUDO_USER" ]; then
        REGULAR_USER=$SUDO_USER
        USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    else
        REGULAR_USER=$(whoami)
        USER_HOME=$HOME
    fi

    # Start and enable Podman socket for rootless mode
    log_info "Starting Podman for user ${REGULAR_USER}..."

    # Enable lingering first (allows user services to run without login)
    loginctl enable-linger "$REGULAR_USER" 2>/dev/null || true

    # Start podman socket as the regular user
    sudo -u "$REGULAR_USER" systemctl --user enable podman.socket 2>/dev/null || true
    sudo -u "$REGULAR_USER" systemctl --user start podman.socket 2>/dev/null || true

    # Verify Podman is working
    PODMAN_VERSION=$(podman --version | awk '{print $3}')
    log_success "Podman ${PODMAN_VERSION} installed"

    # Test Podman functionality
    log_info "Testing Podman functionality..."
    if sudo -u "$REGULAR_USER" podman info >/dev/null 2>&1; then
        log_success "Podman is ready and functional"
    else
        log_warning "Podman installed but initializing storage..."
        # Initialize podman for user
        sudo -u "$REGULAR_USER" podman system reset --force 2>/dev/null || true
        sudo -u "$REGULAR_USER" podman info >/dev/null 2>&1 && log_success "Podman ready" || log_warning "Podman may need manual initialization"
    fi
    echo ""

    # Step 6: Install LibreOffice for PDF conversion
    log_info "Step 6: Installing LibreOffice for document conversion..."

    if [[ "$RHEL_VERSION" == "10" ]]; then
        log_warning "LibreOffice packages not available in RHEL 10 repositories"
        log_info "Installing via Flatpak..."

        # Install Flatpak if not already installed
        dnf install -y flatpak || true

        # Add Flathub repository
        flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true

        # Install LibreOffice via Flatpak
        flatpak install -y flathub org.libreoffice.LibreOffice 2>/dev/null || {
            log_warning "LibreOffice Flatpak installation failed or skipped"
            log_warning "You may need to install LibreOffice manually for Office document conversion"
            log_info "Project APE will work with PDF files only"
        }

        log_success "LibreOffice setup attempted (Flatpak)"
    else
        # RHEL 8/9 - use traditional packages
        dnf install -y \
            libreoffice-core \
            libreoffice-writer \
            libreoffice-calc \
            libreoffice-impress \
            libreoffice-headless || {
            log_warning "LibreOffice installation failed"
            log_info "Project APE will work with PDF files only"
        }
        log_success "LibreOffice installed"
    fi
    echo ""

    # Step 7: Install Google Chrome for NotebookLM authentication
    log_info "Step 7: Installing Google Chrome..."

    # Add Google Chrome repository
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

    # Step 8: Install Project APE Python dependencies
    log_info "Step 8: Installing Python packages..."

    pip3 install --upgrade pip setuptools wheel

    # Install NotebookLM Python SDK with browser support
    log_info "Installing NotebookLM SDK with browser automation..."
    pip3 install "notebooklm-py[browser]"

    # Install Playwright browser (as regular user to avoid permission issues)
    log_info "Installing Playwright Chromium browser..."
    sudo -u "$REGULAR_USER" python3 -m playwright install chromium

    # Install other Python dependencies
    pip3 install \
        flask \
        requests \
        pypdf \
        reportlab \
        Pillow \
        python-magic

    log_success "Python packages installed"
    echo ""

    # Step 9: Create account_planning directory structure
    log_info "Step 9: Creating directory structure..."

    # User variables already set in Step 5
    ACCOUNT_PLANNING_DIR="${USER_HOME}/account_planning"

    # Create directory as the regular user
    sudo -u "$REGULAR_USER" mkdir -p "$ACCOUNT_PLANNING_DIR"

    log_success "Created directory: ${ACCOUNT_PLANNING_DIR}"
    echo ""

    # Step 10: Clone Project APE repository
    log_info "Step 10: Cloning Project APE repository..."

    cd "$ACCOUNT_PLANNING_DIR"

    # Clone as the regular user
    if [ -d "Project-APE" ]; then
        log_warning "Project-APE directory already exists, pulling latest changes..."
        cd Project-APE
        sudo -u "$REGULAR_USER" git pull
    else
        sudo -u "$REGULAR_USER" git clone https://github.com/jasoande/Project-APE.git
        cd Project-APE
    fi

    # Switch to QA branch (latest stable)
    sudo -u "$REGULAR_USER" git checkout QA

    log_success "Project APE cloned to: ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo ""

    # Step 11: Create client_data and logs directories
    log_info "Step 11: Creating working directories..."

    sudo -u "$REGULAR_USER" mkdir -p client_data
    sudo -u "$REGULAR_USER" mkdir -p logs

    log_success "Working directories created"
    echo ""

    # Step 12: Set up Podman for rootless mode
    log_info "Step 12: Configuring Podman for rootless mode..."

    # Enable lingering for the user (allows services to run when not logged in)
    loginctl enable-linger "$REGULAR_USER" || true

    # Set up subuid/subgid for rootless containers
    if ! grep -q "^${REGULAR_USER}:" /etc/subuid; then
        echo "${REGULAR_USER}:100000:65536" >> /etc/subuid
    fi

    if ! grep -q "^${REGULAR_USER}:" /etc/subgid; then
        echo "${REGULAR_USER}:100000:65536" >> /etc/subgid
    fi

    log_success "Podman rootless mode configured"
    echo ""

    # Step 13: Pull Project APE container image
    log_info "Step 13: Pulling Project APE container image..."

    if sudo -u "$REGULAR_USER" podman pull quay.io/jasoande/project_ape/project-ape:latest 2>/dev/null; then
        log_success "Container image pulled"
    else
        log_warning "Failed to pull container image (may require authentication or build locally)"
        log_info "You can build the image locally after setup with:"
        log_info "  cd ${ACCOUNT_PLANNING_DIR}/Project-APE"
        log_info "  podman build -t project-ape:latest -f Containerfile ."
    fi
    echo ""

    # Step 14: Configure firewall (if firewalld is running)
    if systemctl is-active --quiet firewalld; then
        log_info "Step 14: Configuring firewall for dashboard..."

        firewall-cmd --permanent --add-port=8765/tcp || true
        firewall-cmd --reload || true

        log_success "Firewall configured (port 8765 opened for dashboard)"
        echo ""
    else
        log_info "Step 14: Firewall not running, skipping configuration"
        echo ""
    fi

    # Step 15: Create example configuration
    log_info "Step 15: Creating example configuration..."

    PROJECT_DIR="${ACCOUNT_PLANNING_DIR}/Project-APE"

    sudo -u "$REGULAR_USER" cp "${PROJECT_DIR}/example-container.py" "${PROJECT_DIR}/vars.py.example"

    log_success "Example configuration created: vars.py.example"
    echo ""

    # Final summary
    echo "========================================================================"
    echo -e "${GREEN}  ✅ PROJECT APE SETUP COMPLETE!${NC}"
    echo "========================================================================"
    echo ""
    echo "Installation Summary:"
    echo "  • Python ${PYTHON_VERSION}"
    echo "  • Podman ${PODMAN_VERSION}"
    echo "  • Google Chrome ${CHROME_VERSION}"
    echo "  • LibreOffice installed"
    echo "  • NotebookLM SDK installed"
    echo "  • Project directory: ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Switch to your user account:"
    echo "   sudo -i -u ${REGULAR_USER}"
    echo ""
    echo "2. Navigate to Project APE:"
    echo "   cd ${ACCOUNT_PLANNING_DIR}/Project-APE"
    echo ""
    echo "3. Authenticate with NotebookLM:"
    echo "   notebooklm login"
    echo "   (Note: If over SSH without X11, reconnect with: ssh -X user@host)"
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

# Run main function
check_sudo
main

exit 0
