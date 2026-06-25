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
TOTAL_STEPS=9

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
echo "  4. Configure Google Drive authentication (OAuth or Service Account)"
echo "  5. Configure container credentials"
echo "  6. Configure client list"
echo "  7. Verify Google Drive folder access"
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
# Step 5: Google Drive Authentication Setup
################################################################################

log_step "Google Drive Authentication Setup"

echo
echo "Project APE supports two authentication methods for Google Drive:"
echo
echo "  1. OAuth (Browser) - Recommended for personal use"
echo "     ✅ No manual folder sharing needed"
echo "     ✅ Automatic access to all your Drive files"
echo "     ✅ One-time browser login"
echo
echo "  2. Service Account - For automation/servers"
echo "     ⚠️  Requires manual folder sharing for each client"
echo "     ✅ No browser login needed"
echo "     ✅ Good for headless servers"
echo
read -p "Choose authentication method (1 for OAuth, 2 for Service Account): " -n 1 -r
echo
echo

if [[ $REPLY =~ ^[1]$ ]]; then
    # OAuth Setup
    log_info "Setting up OAuth authentication..."

    echo
    echo "OAuth Setup Instructions:"
    echo
    echo "1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "2. Click 'Create Credentials' → 'OAuth client ID'"
    echo "3. Application type: 'Desktop app'"
    echo "4. Name: 'Project APE Desktop'"
    echo "5. Click 'Create' and download the JSON file"
    echo "6. Save it as: ~/.project-ape/drive_credentials.json"
    echo
    echo "Press Enter when you have downloaded the credentials..."
    read

    # Create directory
    mkdir -p ~/.project-ape

    # Check if credentials exist
    if [ -f "$HOME/.project-ape/drive_credentials.json" ]; then
        log_info "✅ Found OAuth credentials"

        # Run OAuth setup script
        if [ -f "./setup-oauth-drive.py" ]; then
            log_info "Running OAuth authentication..."
            python3 ./setup-oauth-drive.py

            if [ $? -eq 0 ]; then
                log_info "✅ OAuth setup complete"
            else
                log_warn "OAuth setup encountered errors"
                echo "You can run it manually later: python3 setup-oauth-drive.py"
            fi
        else
            log_warn "setup-oauth-drive.py not found"
            echo "You can set up OAuth manually later with: python3 setup-oauth-drive.py"
        fi
    else
        log_warn "OAuth credentials not found at: ~/.project-ape/drive_credentials.json"
        echo
        echo "Please complete OAuth setup manually:"
        echo "  1. Download credentials from Google Cloud Console"
        echo "  2. Save to: ~/.project-ape/drive_credentials.json"
        echo "  3. Run: python3 setup-oauth-drive.py"
        echo
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Update vars.py to use OAuth (if it exists)
    if [ -f "./vars.py" ]; then
        log_info "Verifying vars.py uses OAuth..."
        if grep -q "auth_method.*oauth" vars.py; then
            log_info "✅ vars.py already configured for OAuth"
        else
            log_warn "vars.py may need to be updated to use OAuth"
            echo "Ensure vars.py has: auth_method: 'oauth'"
        fi
    fi

    log_info "OAuth authentication configured"

else
    # Service Account Setup
    log_info "Setting up service account authentication..."

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

    # Fix permissions for container access
    log_info "Fixing service account key permissions for container access..."
    chmod 644 ./service-account-key.json

    # Update vars.py to use service account (if it exists)
    if [ -f "./vars.py" ]; then
        log_info "Verifying vars.py uses service account..."
        if grep -q "auth_method.*service_account" vars.py; then
            log_info "✅ vars.py already configured for service account"
        else
            log_warn "vars.py may need to be updated to use service_account"
            echo "Ensure vars.py has: auth_method: 'service_account'"
        fi
    fi

    log_info "Service account ready"
    log_warn "Remember: You must manually share Drive folders with the service account!"
fi

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
# Step 8: Google Drive Folder Access Verification
################################################################################

log_step "Google Drive Folder Access Verification"

# Check authentication method from vars.py
AUTH_METHOD="unknown"
if [ -f "./vars.py" ]; then
    if grep -q "auth_method.*oauth" vars.py; then
        AUTH_METHOD="oauth"
    elif grep -q "auth_method.*service_account" vars.py; then
        AUTH_METHOD="service_account"
    fi
fi

if [ "$AUTH_METHOD" = "service_account" ]; then
    # Service account requires manual folder sharing
    log_info "Service Account authentication detected"
    echo
    echo "⚠️  Important: Service accounts require manual folder sharing"
    echo

    # Try automated sharing (but it will likely fail)
    if [ -f "./share-drive-folders.py" ] && [ -f "./vars.py" ]; then
        log_info "Attempting automated folder sharing via Drive API..."
        echo

        # Activate venv if not already active
        if [ -z "$VIRTUAL_ENV" ]; then
            source ./activate-ape-env.sh
        fi

        python3 ./share-drive-folders.py

        if [ $? -eq 0 ]; then
            log_info "✅ All Drive folders shared successfully"
        else
            log_warn "Automated sharing failed (expected)"
            echo
            echo "Please manually share folders with the service account:"
            echo

            # Get service account email
            if [ -f "./service-account-key.json" ]; then
                SA_EMAIL=$(python3 -c "import json; print(json.load(open('service-account-key.json'))['client_email'])" 2>/dev/null || echo "")
                if [ -n "$SA_EMAIL" ]; then
                    echo "  Service Account: ${BLUE}$SA_EMAIL${NC}"
                fi
            fi

            echo
            echo "  1. Go to https://drive.google.com"
            echo "  2. Right-click each client folder → Share"
            echo "  3. Add the service account email above"
            echo "  4. Set permission: Viewer"
            echo "  5. Uncheck 'Notify people'"
            echo
            echo "See: DRIVE_PERMISSIONS_FIX.md for detailed instructions"
            echo

            read -p "Continue setup? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo
                echo "Setup paused. When ready to continue:"
                echo "  1. Manually share folders with service account"
                echo "  2. Verify: python3 verify-drive-access.py"
                echo "  3. Continue: ./launch-project-ape.command"
                exit 0
            fi
        fi
    else
        log_warn "Skipping folder sharing - missing vars.py or share script"
    fi

elif [ "$AUTH_METHOD" = "oauth" ]; then
    # OAuth has automatic access to user's files
    log_info "OAuth authentication detected"
    log_info "✅ No manual folder sharing needed!"
    echo
    echo "OAuth automatically grants access to all your Drive files."
    echo "No additional setup required for folder access."
    echo

    # Verify OAuth token exists
    if [ -f "$HOME/.project-ape/drive_token.json" ]; then
        log_info "✅ OAuth token found"
    else
        log_warn "OAuth token not found"
        echo "You may need to run: python3 setup-oauth-drive.py"
    fi

else
    log_warn "Could not detect authentication method from vars.py"
    echo "Skipping folder access verification"
fi

log_info "Drive folder access step complete"

################################################################################
# Step 9: Create Setup Completion Marker
################################################################################

log_step "Creating Setup Completion Marker"

MARKER_FILE="$HOME/.ape_setup_complete"
SCRIPT_DIR_ABS="$(cd "$(dirname "$0")" && pwd)"

cat > "$MARKER_FILE" <<EOF
{
  "setup_completed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "setup_version": "3.3.0",
  "platform": "$(uname -s)",
  "script_dir": "$SCRIPT_DIR_ABS",
  "components_installed": {
    "podman": true,
    "gcloud": true,
    "python": true,
    "notebooklm_cli": true,
    "service_account": true,
    "container_credentials": true
  }
}
EOF

if [ -f "$MARKER_FILE" ]; then
    log_info "✅ Setup marker created: $MARKER_FILE"
    log_info "   To reset setup state: rm $MARKER_FILE"
else
    log_warn "Failed to create setup marker file"
fi

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
echo "  ✅ Google Drive authentication configured"
echo "  ✅ Container credentials configured"
echo "  ✅ Client configuration ready"
echo "  ✅ Drive folder access verified"
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
