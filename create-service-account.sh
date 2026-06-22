#!/bin/bash
################################################################################
# Project APE - Automated Google Cloud Service Account Setup
# Creates GCP project, service account, enables APIs, downloads key
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID_PREFIX="project-ape"
SERVICE_ACCOUNT_NAME="project-ape-service"
SERVICE_ACCOUNT_DISPLAY="Project APE Service Account"
SERVICE_ACCOUNT_DESC="Service account for Project APE Google Drive access"
KEY_FILE="service-account-key.json"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================================================"
echo "PROJECT APE - GOOGLE CLOUD SERVICE ACCOUNT CREATOR"
echo "========================================================================"
echo
echo "This will create a service account for Google Drive access."
echo

################################################################################
# Step 1: Check gcloud CLI
################################################################################

log_step "Checking for gcloud CLI..."

if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI not found"
    echo
    echo "Please install Google Cloud SDK first:"
    echo
    echo "macOS:"
    echo "  brew install --cask google-cloud-sdk"
    echo
    echo "Linux:"
    echo "  curl https://sdk.cloud.google.com | bash"
    echo "  exec -l \$SHELL"
    echo
    echo "Or visit: https://cloud.google.com/sdk/docs/install"
    echo
    echo "After installing, run:"
    echo "  gcloud init"
    echo "  gcloud auth login"
    echo
    echo "Then run this script again."
    exit 1
fi

log_info "gcloud CLI is installed: $(gcloud --version | head -1)"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    log_warn "Not authenticated with Google Cloud"
    echo
    echo "Authenticating with Google Cloud..."
    gcloud auth login
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    log_error "Authentication failed"
    exit 1
fi

log_info "Authenticated as: $ACTIVE_ACCOUNT"
echo

################################################################################
# Step 2: Create or Select Project
################################################################################

log_step "Setting up Google Cloud project..."

# Check if we have a default project configured
DEFAULT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -n "$DEFAULT_PROJECT" ]; then
    PROJECT_ID="$DEFAULT_PROJECT"
    log_info "Using default project: $PROJECT_ID"
else
    echo
    echo "Find your Project ID at: https://console.cloud.google.com"
    echo
    read -p "Enter project ID: " PROJECT_ID

    # Verify project exists
    set +e
    gcloud projects describe $PROJECT_ID &>/dev/null
    DESCRIBE_RESULT=$?
    set -e

    if [ $DESCRIBE_RESULT -ne 0 ]; then
        log_error "Cannot access project '$PROJECT_ID'"
        echo "Make sure the project exists and you have access"
        exit 1
    fi

    log_info "Using project: $PROJECT_ID"
fi

# Set active project
gcloud config set project $PROJECT_ID
log_info "Active project set to: $PROJECT_ID"
echo

################################################################################
# Step 3: Link Billing Account (Required for API access)
################################################################################

log_step "Checking billing status..."

# Try billing check with timeout (org accounts may hang)
set +e
BILLING_ENABLED=$(timeout 10s gcloud beta billing projects describe $PROJECT_ID --format="value(billingEnabled)" 2>/dev/null || echo "unknown")
set -e

if [[ "$BILLING_ENABLED" == "True" ]]; then
    log_info "Billing is enabled"
elif [[ "$BILLING_ENABLED" == "unknown" ]]; then
    log_warn "Could not check billing status (timeout/error)"
    echo
    echo "Skipping billing check for organization account."
    echo "If APIs fail to enable, check billing at:"
    echo "  https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
    echo
else
    log_warn "Billing may not be enabled"
    echo
    echo "Google Drive API requires an active billing account."
    echo "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
    echo
    read -p "Press Enter to continue anyway (or Ctrl+C to abort)..."
    echo
fi

echo

################################################################################
# Step 4: Enable Required APIs
################################################################################

log_step "Enabling Google Drive API..."

# Enable Drive API
if gcloud services enable drive.googleapis.com --project=$PROJECT_ID 2>/dev/null; then
    log_info "Google Drive API enabled"
else
    log_error "Failed to enable Google Drive API"
    exit 1
fi

# Enable IAM API (needed for service account creation)
log_step "Enabling IAM Service Account Credentials API..."
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID 2>/dev/null

log_info "Required APIs enabled"
echo

################################################################################
# Step 5: Create Service Account
################################################################################

log_step "Creating service account..."

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account already exists
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID &>/dev/null; then
    log_info "Using existing service account: $SERVICE_ACCOUNT_EMAIL"
else
    # Create service account
    if gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="$SERVICE_ACCOUNT_DISPLAY" \
        --description="$SERVICE_ACCOUNT_DESC" \
        --project=$PROJECT_ID; then
        log_info "Service account created: $SERVICE_ACCOUNT_EMAIL"

        # Wait for IAM propagation (can take a few seconds)
        log_info "Waiting for IAM propagation..."
        sleep 10
    else
        log_error "Failed to create service account"
        exit 1
    fi
fi

echo

################################################################################
# Step 6: Generate Service Account Key
################################################################################

log_step "Generating service account key..."

# Remove old key file if exists
if [ -f "$KEY_FILE" ]; then
    log_warn "Overwriting existing key file: $KEY_FILE"
    rm -f "$KEY_FILE"
fi

# Create and download key
if gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID; then
    log_info "Service account key created: $KEY_FILE"
else
    log_error "Failed to create service account key"
    exit 1
fi

# Secure the key file
chmod 600 $KEY_FILE
log_info "Key file permissions set to 600 (read/write owner only)"

# Verify key file
if python3 -c "import json; json.load(open('$KEY_FILE'))" 2>/dev/null; then
    log_info "Key file is valid JSON"
else
    log_error "Key file appears to be invalid"
    exit 1
fi

echo

################################################################################
# Step 7: Create .env file
################################################################################

log_step "Creating .env configuration..."

cat > .env << EOF
# Project APE Environment Variables
# Generated: $(date)

# Google Drive Service Account
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json

# Project Configuration
GCP_PROJECT_ID=$PROJECT_ID
SERVICE_ACCOUNT_EMAIL=$SERVICE_ACCOUNT_EMAIL
EOF

log_info ".env file created"

echo

################################################################################
# Setup Complete
################################################################################

echo "========================================================================"
echo -e "${GREEN}✅ SERVICE ACCOUNT SETUP COMPLETE${NC}"
echo "========================================================================"
echo
echo -e "${BLUE}Summary:${NC}"
echo "  📋 Project ID:             $PROJECT_ID"
echo "  🤖 Service Account Email:  $SERVICE_ACCOUNT_EMAIL"
echo "  🔑 Key File:               $KEY_FILE"
echo "  ⚙️  Environment File:       .env"
echo
echo -e "${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo
echo "1. Share Google Drive folders with the service account:"
echo "   ${BLUE}$SERVICE_ACCOUNT_EMAIL${NC}"
echo
echo "   For each client folder in vars.py:"
echo "   - Open https://drive.google.com"
echo "   - Right-click the folder → Share"
echo "   - Add the service account email above"
echo "   - Set permission to 'Viewer'"
echo "   - Uncheck 'Notify people'"
echo "   - Click 'Share'"
echo
echo "2. Verify the key file:"
echo "   ${GREEN}ls -la $KEY_FILE${NC}"
echo "   ${GREEN}python3 -c \"import json; json.load(open('$KEY_FILE'))\"${NC}"
echo
echo "3. Configure your clients:"
echo "   ${GREEN}cp example-vars.py vars.py${NC}"
echo "   ${GREEN}nano vars.py${NC}"
echo
echo "4. Continue with Project APE setup:"
echo "   ${GREEN}source ./activate-ape-env.sh${NC}"
echo "   ${GREEN}notebooklm login${NC}"
echo "   ${GREEN}./setup-credentials.sh${NC}"
echo "   ${GREEN}./launch_ape.sh fast${NC}"
echo
echo -e "${YELLOW}SECURITY REMINDER:${NC}"
echo "  ⚠️  Never commit $KEY_FILE to git"
echo "  ⚠️  Never share the key file publicly"
echo "  ⚠️  Store it securely (it's already in .gitignore)"
echo
echo "For detailed instructions, see: SERVICE-ACCOUNT-SETUP.md"
echo
