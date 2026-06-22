#!/bin/bash
################################################################################
# Project APE - Unified Setup Workflow
# Runs all setup steps in the correct order
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STEP_NUM=0
TOTAL_STEPS=8

log_step() {
    STEP_NUM=$((STEP_NUM + 1))
    echo
    echo "========================================================================"
    echo -e "${BLUE}STEP ${STEP_NUM}/${TOTAL_STEPS}: $1${NC}"
    echo "========================================================================"
    echo
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "========================================================================"
echo "PROJECT APE - COMPLETE SETUP"
echo "========================================================================"
echo
echo "This will set up Project APE from scratch:"
echo "  1. Install environment (Podman, Google Cloud SDK, Python, NotebookLM CLI)"
echo "  2. Activate virtual environment"
echo "  3. Authenticate with NotebookLM"
echo "  4. Create Google Cloud service account"
echo "  5. Configure container credentials"
echo "  6. Configure client list"
echo "  7. Share Google Drive folders"
echo
echo "Time required: ~20-30 minutes"
echo
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

################################################################################
# Step 1: Environment Setup
################################################################################

log_step "Environment Setup"

if [ ! -f "./setup-environment.sh" ]; then
    log_error "setup-environment.sh not found"
    echo "Run this script from the Project-APE directory"
    exit 1
fi

log_info "Running setup-environment.sh..."
./setup-environment.sh

# Verify venv was created
if [ ! -f "./activate-ape-env.sh" ]; then
    log_error "Virtual environment activation script not found"
    exit 1
fi

log_info "Environment setup complete"

################################################################################
# Step 2: Activate Virtual Environment
################################################################################

log_step "Activate Virtual Environment"

log_info "Activating Python virtual environment..."

# Source the activation script
source ./activate-ape-env.sh

# Verify notebooklm is available
if ! command -v notebooklm &> /dev/null; then
    log_error "notebooklm command not found after activation"
    echo "Virtual environment may not be properly activated"
    exit 1
fi

log_info "Virtual environment activated"
log_info "NotebookLM CLI: $(notebooklm --version 2>&1 | head -1)"

################################################################################
# Step 3: Google Cloud Authentication (Done in setup-environment.sh)
################################################################################

# Note: gcloud auth login is handled in setup-environment.sh during install
# This step is a placeholder to keep numbering consistent

################################################################################
# Step 4: NotebookLM Authentication
################################################################################

log_step "NotebookLM Authentication"

# Check if already authenticated
if [ -f "$HOME/.notebooklm/profiles/default/storage_state.json" ]; then
    log_info "NotebookLM credentials already exist"
    read -p "Re-authenticate? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping NotebookLM login"
    else
        log_info "Opening browser for NotebookLM authentication..."
        notebooklm login
    fi
else
    log_info "Opening browser for NotebookLM authentication..."
    notebooklm login
fi

# Verify authentication worked
if [ ! -f "$HOME/.notebooklm/profiles/default/storage_state.json" ]; then
    log_error "NotebookLM authentication failed"
    echo "Storage state file not found"
    exit 1
fi

log_info "NotebookLM authentication complete"

################################################################################
# Step 5: Google Cloud Service Account
################################################################################

log_step "Google Cloud Service Account"

if [ ! -f "./create-service-account.sh" ]; then
    log_error "create-service-account.sh not found"
    exit 1
fi

# Check if service account already exists
if [ -f "./service-account-key.json" ]; then
    log_info "Service account key already exists"
    read -p "Create new service account? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping service account creation"
    else
        ./create-service-account.sh
    fi
else
    log_info "Creating Google Cloud service account..."
    ./create-service-account.sh
fi

# Verify service account key exists
if [ ! -f "./service-account-key.json" ]; then
    log_error "Service account key not found"
    echo "create-service-account.sh may have failed"
    exit 1
fi

log_info "Service account ready"

################################################################################
# Step 6: Container Credentials
################################################################################

log_step "Container Credentials Setup"

if [ ! -f "./setup-credentials.sh" ]; then
    log_error "setup-credentials.sh not found"
    exit 1
fi

# Remove old credentials volume if it exists (may have wrong UID from pre-fix version)
CREDS_VOLUME="project-ape-credentials"
if podman volume exists ${CREDS_VOLUME} 2>/dev/null; then
    log_info "Removing old credentials volume to ensure UID compatibility..."
    podman volume rm ${CREDS_VOLUME}
fi

log_info "Copying NotebookLM credentials to container volume..."
./setup-credentials.sh

log_info "Container credentials configured"

################################################################################
# Step 7: Client Configuration
################################################################################

log_step "Client Configuration"

# Check if vars.py already has clients configured
if [ -f "./vars.py" ] && grep -q "clients = \[" vars.py 2>/dev/null; then
    # Check if it has more than just empty array
    CLIENT_COUNT=$(grep -o "clients = \[" vars.py | wc -l)
    if [ "$CLIENT_COUNT" -gt 0 ]; then
        log_info "vars.py already configured with clients"
        log_info "Skipping client configuration step"
    fi
else
    # vars.py doesn't exist or isn't configured
    if [ ! -f "./vars.py" ]; then
        if [ -f "./example-vars.py" ]; then
            log_info "Creating vars.py from example..."
            cp example-vars.py vars.py
            log_info "vars.py created"
        else
            log_warn "example-vars.py not found"
        fi
    fi

    echo
    echo "⚠️  You need to configure your clients in vars.py"
    echo
    echo "To configure now:"
    echo "  1. Edit vars.py: ${GREEN}nano vars.py${NC}"
    echo "  2. Add your clients and Google Drive folder URLs"
    echo "  3. Share Drive folders with your service account:"

    if [ -f "./service-account-key.json" ]; then
        SA_EMAIL=$(python3 -c "import json; print(json.load(open('service-account-key.json'))['client_email'])" 2>/dev/null || echo "")
        if [ -n "$SA_EMAIL" ]; then
            echo "     ${BLUE}$SA_EMAIL${NC}"
        fi
    fi

    echo
    echo "Or configure later and skip this step."
    echo
    read -p "Configure vars.py now? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} vars.py

        # Verify vars.py has clients
        if ! grep -q "clients = \[" vars.py 2>/dev/null; then
            log_warn "vars.py may not be properly configured"
            echo "Make sure it has: clients = ['client1', 'client2', ...]"
        else
            log_info "vars.py configured"
        fi
    else
        log_warn "Skipping vars.py configuration"
        echo "You can configure it later by editing vars.py"
    fi
fi

log_info "Client configuration step complete"

################################################################################
# Step 8: Share Google Drive Folders
################################################################################

log_step "Share Google Drive Folders with Service Account"

# Get service account email
SA_EMAIL=""
if [ -f "./service-account-key.json" ]; then
    SA_EMAIL=$(python3 -c "import json; print(json.load(open('service-account-key.json'))['client_email'])" 2>/dev/null || echo "")
fi

if [ -z "$SA_EMAIL" ]; then
    log_warn "Could not read service account email"
else
    echo
    echo "To allow Project APE to access your Google Drive folders,"
    echo "you must share each folder with the service account."
    echo
    echo -e "${BLUE}Service Account Email:${NC}"
    echo "  ${GREEN}$SA_EMAIL${NC}"
    echo
    echo -e "${BLUE}How to share:${NC}"
    echo "  1. Go to https://drive.google.com"
    echo "  2. Right-click each client folder → Share"
    echo "  3. Paste the service account email above"
    echo "  4. Set permission to 'Viewer'"
    echo "  5. Uncheck 'Notify people'"
    echo "  6. Click 'Share'"
    echo

    # Copy service account email to clipboard if possible
    if command -v pbcopy &> /dev/null; then
        echo "$SA_EMAIL" | pbcopy
        log_info "Service account email copied to clipboard!"
    elif command -v xclip &> /dev/null; then
        echo "$SA_EMAIL" | xclip -selection clipboard
        log_info "Service account email copied to clipboard!"
    fi

    echo
    read -p "Press Enter after sharing all Drive folders..."
    echo
fi

log_info "Drive folder sharing step complete"

################################################################################
# Setup Complete
################################################################################

echo
echo "========================================================================"
echo -e "${GREEN}✅ SETUP COMPLETE - READY TO RUN${NC}"
echo "========================================================================"
echo
echo -e "${BLUE}What was installed:${NC}"
echo "  ✅ Podman, Google Cloud SDK, Python 3.14, NotebookLM CLI"
echo "  ✅ Google Cloud authenticated"
echo "  ✅ NotebookLM authenticated"
echo "  ✅ Service account created"
echo "  ✅ Container credentials configured"
echo "  ✅ Client configuration ready"
echo "  ✅ Drive folders shared"
echo
echo -e "${GREEN}▶ Launch Project APE:${NC}"
echo
echo "  ${GREEN}./launch_ape.sh fast${NC}     # Fast mode (15-20 min/client)"
echo "  ${GREEN}./launch_ape.sh deep${NC}     # Deep mode (35-40 min/client)"
echo
echo -e "${BLUE}Monitor & View Results:${NC}"
echo
echo "  Dashboard:  ${BLUE}http://localhost:8765${NC}"
echo "  NotebookLM: ${BLUE}https://notebooklm.google.com${NC}"
echo
echo -e "${YELLOW}📝 Note for future terminal sessions:${NC}"
echo "  To use NotebookLM CLI: ${GREEN}source ./activate-ape-env.sh${NC}"
echo
echo "For help, see: README-NEW.md or QUICKSTART-NEW.md"
echo
