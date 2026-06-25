#!/bin/bash
################################################################################
# Quick Test Script for create-service-account.sh
# Validates the service account creation and setup
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================================================"
echo "SERVICE ACCOUNT CREATION - QUICK TEST"
echo "========================================================================"
echo

# Test 1: Check prerequisites
echo "Test 1: Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ FAIL: gcloud CLI not found${NC}"
    echo
    echo "Install with:"
    echo "  macOS: brew install --cask google-cloud-sdk"
    echo "  Linux: curl https://sdk.cloud.google.com | bash"
    exit 1
fi
echo -e "${GREEN}✅ PASS: gcloud CLI installed${NC}"
gcloud --version | head -1

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ FAIL: python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PASS: python3 installed${NC}"
python3 --version

echo

# Test 2: Check authentication
echo "Test 2: Checking Google Cloud authentication..."

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Not authenticated with Google Cloud${NC}"
    echo
    echo "Authenticate with:"
    echo "  gcloud auth login"
    echo
    read -p "Authenticate now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud auth login
        ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)
    else
        echo -e "${RED}❌ FAIL: Authentication required${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ PASS: Authenticated as $ACTIVE_ACCOUNT${NC}"
echo

# Test 3: Check if create-service-account.sh exists
echo "Test 3: Checking for create-service-account.sh..."

if [ ! -f "./create-service-account.sh" ]; then
    echo -e "${RED}❌ FAIL: create-service-account.sh not found${NC}"
    echo "Run this script from the Project-APE directory"
    exit 1
fi

if [ ! -x "./create-service-account.sh" ]; then
    echo -e "${YELLOW}⚠️  WARNING: Script not executable${NC}"
    chmod +x ./create-service-account.sh
    echo -e "${GREEN}✅ Fixed: Made script executable${NC}"
fi

echo -e "${GREEN}✅ PASS: create-service-account.sh found${NC}"
echo

# Test 4: Check for existing files
echo "Test 4: Checking for existing service account files..."

if [ -f "service-account-key.json" ]; then
    echo -e "${YELLOW}⚠️  WARNING: service-account-key.json already exists${NC}"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv service-account-key.json service-account-key.json.backup.$(date +%Y%m%d-%H%M%S)
        echo "  Backed up existing key"
    fi
fi

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  WARNING: .env already exists${NC}"
    read -p "Delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv .env .env.backup.$(date +%Y%m%d-%H%M%S)
        echo "  Backed up existing .env"
    fi
fi

echo

# Ready to test
echo "========================================================================"
echo "READY TO TEST"
echo "========================================================================"
echo
echo "All prerequisites met. Ready to run service account creation."
echo
echo -e "${BLUE}Next steps:${NC}"
echo
echo "1. Run the service account creation script:"
echo "   ${GREEN}./create-service-account.sh${NC}"
echo
echo "2. Follow the prompts:"
echo "   - Choose: 1 (Create new project)"
echo "   - Enable billing when prompted"
echo "   - Wait for completion"
echo
echo "3. Verify the output files:"
echo "   ${GREEN}ls -la service-account-key.json .env${NC}"
echo
echo "4. Test Drive API access:"
echo "   ${GREEN}./test-drive-access.sh${NC}"
echo
echo -e "${YELLOW}Press Enter to run create-service-account.sh now, or Ctrl+C to exit${NC}"
read

# Run the script
./create-service-account.sh

# Post-test validation
echo
echo "========================================================================"
echo "POST-TEST VALIDATION"
echo "========================================================================"
echo

ERRORS=0

# Check service account key
echo "Validating service-account-key.json..."
if [ -f "service-account-key.json" ]; then
    # Check permissions
    PERMS=$(stat -f %Lp service-account-key.json 2>/dev/null || stat -c %a service-account-key.json 2>/dev/null)
    if [ "$PERMS" == "600" ]; then
        echo -e "${GREEN}✅ PASS: Correct permissions (600)${NC}"
    else
        echo -e "${RED}❌ FAIL: Incorrect permissions ($PERMS), should be 600${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Validate JSON
    if python3 -c "import json; json.load(open('service-account-key.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS: Valid JSON file${NC}"

        # Extract service account email
        SA_EMAIL=$(python3 -c "import json; print(json.load(open('service-account-key.json'))['client_email'])")
        echo "   Service Account: $SA_EMAIL"
    else
        echo -e "${RED}❌ FAIL: Invalid JSON${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ FAIL: service-account-key.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo

# Check .env file
echo "Validating .env file..."
if [ -f ".env" ]; then
    if grep -q "GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY" .env; then
        echo -e "${GREEN}✅ PASS: .env contains SERVICE_ACCOUNT_KEY${NC}"
    else
        echo -e "${RED}❌ FAIL: .env missing SERVICE_ACCOUNT_KEY${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -q "GCP_PROJECT_ID" .env; then
        PROJECT_ID=$(grep GCP_PROJECT_ID .env | cut -d= -f2)
        echo -e "${GREEN}✅ PASS: .env contains GCP_PROJECT_ID${NC}"
        echo "   Project ID: $PROJECT_ID"
    else
        echo -e "${RED}❌ FAIL: .env missing GCP_PROJECT_ID${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -q "SERVICE_ACCOUNT_EMAIL" .env; then
        echo -e "${GREEN}✅ PASS: .env contains SERVICE_ACCOUNT_EMAIL${NC}"
    else
        echo -e "${RED}❌ FAIL: .env missing SERVICE_ACCOUNT_EMAIL${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ FAIL: .env file not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo

# Summary
echo "========================================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo "========================================================================"
    echo
    echo "Service account setup is complete and verified!"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo
    echo "1. Share Google Drive folders with your service account:"
    echo "   ${GREEN}$SA_EMAIL${NC}"
    echo
    echo "2. Test Drive API access:"
    echo "   ${GREEN}python3 -c \"from google.oauth2 import service_account; from googleapiclient.discovery import build; credentials = service_account.Credentials.from_service_account_file('service-account-key.json', scopes=['https://www.googleapis.com/auth/drive.readonly']); service = build('drive', 'v3', credentials=credentials); results = service.files().list(pageSize=10, fields='files(id, name)').execute(); files = results.get('files', []); print('\\n✅ Drive API works!' if files else '⚠️  No files shared yet'); [print(f'  - {f[\\\"name\\\"]}') for f in files]\"${NC}"
    echo
    echo "3. Configure vars.py and run Project APE:"
    echo "   ${GREEN}cp example-vars.py vars.py${NC}"
    echo "   ${GREEN}nano vars.py${NC}"
    echo "   ${GREEN}./launch_ape.sh fast${NC}"
    echo
else
    echo -e "${RED}❌ $ERRORS TEST(S) FAILED${NC}"
    echo "========================================================================"
    echo
    echo "Please review the errors above and:"
    echo "1. Check service-account-key.json exists and is valid JSON"
    echo "2. Verify .env file contains all required variables"
    echo "3. Ensure permissions are set correctly (600 for key file)"
    echo
    echo "Re-run the test with:"
    echo "  ${GREEN}./test-service-account-quick.sh${NC}"
    echo
    exit 1
fi
