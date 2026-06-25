# Testing the Automated Service Account Creation Script

**Script:** `create-service-account.sh`  
**Purpose:** Automated Google Cloud service account setup for Project APE

## Prerequisites

Before testing, ensure you have:

- [ ] Google Cloud account with billing enabled
- [ ] Terminal access
- [ ] Internet connection

## Test Procedure

### Step 1: Install Google Cloud SDK (if needed)

```bash
# Check if already installed
gcloud --version

# If not installed:
# macOS:
brew install --cask google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud --version
```

**Expected output:**
```
Google Cloud SDK 495.0.0
bq 2.1.8
core 2024.06.14
gcloud-crc32c 1.0.0
```

### Step 2: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login
```

**What happens:**
1. Opens browser window
2. Prompts for Google account login
3. Asks for permission to access Google Cloud
4. Returns to terminal with success message

**Verify authentication:**
```bash
gcloud auth list
```

**Expected output:**
```
           Credentialed Accounts
ACTIVE  ACCOUNT
*       your-email@example.com

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
```

### Step 3: Run the Test Script

```bash
# Navigate to Project APE directory
cd ~/Project-APE

# Run the service account creator
./create-service-account.sh
```

### Step 4: Follow the Interactive Prompts

#### Prompt 1: Continue Setup?
```
Continue? (y/n)
```
**Action:** Type `y` and press Enter

---

#### Prompt 2: Create New or Use Existing Project?
```
Choose an option:
  1. Create new project (Recommended)
  2. Use existing project

Enter choice (1 or 2):
```

**For Testing:** Type `1` (create new project)

**What happens:**
- Script generates unique project ID: `project-ape-XXXXX`
- Creates new GCP project
- Takes 5-10 seconds

**Expected output:**
```
[STEP] Creating new project: project-ape-12345
[INFO] Project created successfully
[INFO] Active project set to: project-ape-12345
```

---

#### Prompt 3: Enable Billing

If billing is not enabled, you'll see:
```
Billing is not enabled for this project

Please enable billing:
  1. Visit: https://console.cloud.google.com/billing/linkedaccount?project=project-ape-12345
  2. Link a billing account (you can create a new one if needed)
  3. Free tier includes 10GB storage and 1 billion Drive API requests/month

Press Enter after enabling billing to continue...
```

**Action:**
1. Click the URL shown
2. In browser, link a billing account
3. Return to terminal and press Enter

**Note:** Free tier is sufficient for testing - no charges expected for normal usage.

---

#### Prompt 4: Service Account Key Overwrite (if exists)

If testing multiple times:
```
Existing key file found: service-account-key.json
Overwrite? (y/n)
```

**Action:** Type `y` to overwrite

---

#### Prompt 5: .env File Overwrite (if exists)

```
.env file already exists
Overwrite? (y/n)
```

**Action:** Type `y` to overwrite

---

### Step 5: Verify Successful Completion

If successful, you'll see:
```
========================================================================
✅ SERVICE ACCOUNT SETUP COMPLETE
========================================================================

Summary:
  📋 Project ID:             project-ape-12345
  🤖 Service Account Email:  project-ape-service@project-ape-12345.iam.gserviceaccount.com
  🔑 Key File:               service-account-key.json
  ⚙️  Environment File:       .env

IMPORTANT NEXT STEPS:
1. Share Google Drive folders with the service account:
   project-ape-service@project-ape-12345.iam.gserviceaccount.com
   ...
```

**Copy the service account email** - you'll need it for testing.

### Step 6: Verify Generated Files

```bash
# Check service account key file
ls -la service-account-key.json

# Expected output:
# -rw-------  1 you  staff  2350 Jun 22 12:00 service-account-key.json
#  ^^^ Important: 600 permissions (owner read/write only)

# Verify it's valid JSON
python3 -c "import json; data=json.load(open('service-account-key.json')); print('✅ Valid JSON'); print('Service Account:', data['client_email'])"

# Check .env file
cat .env
```

**Expected .env contents:**
```
# Project APE Environment Variables
# Generated: Mon Jun 22 12:00:00 PDT 2026

# Google Drive Service Account
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json

# Project Configuration
GCP_PROJECT_ID=project-ape-12345
SERVICE_ACCOUNT_EMAIL=project-ape-service@project-ape-12345.iam.gserviceaccount.com
```

### Step 7: Test Service Account Permissions

Create a test Google Drive folder and share it:

```bash
# Get your service account email
grep SERVICE_ACCOUNT_EMAIL .env
```

**Manual test:**
1. Go to https://drive.google.com
2. Create a test folder: "Project APE Test"
3. Right-click folder → Share
4. Paste service account email
5. Set permission to "Viewer"
6. Uncheck "Notify people"
7. Click "Share"

### Step 8: Verify Drive API Access

Test that the service account can access Drive:

```bash
# Quick Python test
python3 << 'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

try:
    # Load credentials
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=SCOPES)
    
    # Build Drive API client
    service = build('drive', 'v3', credentials=credentials)
    
    # List files shared with service account
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)").execute()
    
    files = results.get('files', [])
    
    if files:
        print("✅ Service account can access Drive API!")
        print("\nFiles/folders shared with service account:")
        for f in files:
            print(f"  - {f['name']}")
    else:
        print("⚠️  No files found. Share a Drive folder with the service account.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure you've shared a Drive folder with the service account.")
EOF
```

**Expected output (if folder shared):**
```
✅ Service account can access Drive API!

Files/folders shared with service account:
  - Project APE Test
```

### Step 9: Test with Project APE (Optional Full Integration Test)

```bash
# Create test client configuration
cat > vars.py << 'EOF'
clients = ["test_client"]

# Test client configuration
test_client_name = "Test Client Inc"
test_client_folder = "drive://YOUR_DRIVE_FOLDER_ID"  # Replace with actual Drive folder
EOF

# Activate environment
source ./activate-ape-env.sh

# Login to NotebookLM (if not already)
notebooklm login

# Setup credentials
./setup-credentials.sh

# Run fast mode test
./launch_ape.sh fast test_client
```

**Monitor for errors** - if service account setup worked, Drive downloads should succeed.

## Verification Checklist

After running the script, verify:

- [ ] `service-account-key.json` exists with 600 permissions
- [ ] JSON file is valid (can be parsed)
- [ ] `.env` file exists with correct PROJECT_ID and SERVICE_ACCOUNT_EMAIL
- [ ] Service account email format: `project-ape-service@project-ape-XXXXX.iam.gserviceaccount.com`
- [ ] Can share Drive folder with service account
- [ ] Python test can access shared Drive folder
- [ ] Google Cloud Console shows the project at https://console.cloud.google.com
- [ ] Drive API is enabled for the project

## Common Issues and Solutions

### Issue 1: "gcloud: command not found"

**Solution:**
```bash
# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

### Issue 2: "Not authenticated with Google Cloud"

**Solution:**
```bash
gcloud auth login
gcloud auth list  # Verify
```

---

### Issue 3: "Failed to create project"

**Possible causes:**
- Project ID already exists (try again - script generates random suffix)
- No billing account linked
- Insufficient permissions

**Solution:**
```bash
# Check if you have permission to create projects
gcloud projects list

# If no projects listed, you may need to:
# 1. Set up billing at https://console.cloud.google.com/billing
# 2. Verify you're using the correct Google account
```

---

### Issue 4: "Billing not enabled"

**Solution:**
1. Visit the URL provided by the script
2. Link a billing account (free tier is sufficient)
3. Return to terminal and press Enter

---

### Issue 5: "Failed to enable Drive API"

**Solution:**
```bash
# Manually enable via gcloud
gcloud services enable drive.googleapis.com --project=PROJECT_ID

# Or via web console
# Visit: https://console.cloud.google.com/apis/library/drive.googleapis.com
```

---

### Issue 6: "Service account key file appears to be invalid"

**Solution:**
```bash
# Check file contents
cat service-account-key.json | jq .

# If jq not installed, use python
python3 -c "import json; json.load(open('service-account-key.json'))"

# Re-generate key if corrupted
./create-service-account.sh
```

---

### Issue 7: Python test fails with "No module named 'google'"

**Solution:**
```bash
# Install required libraries
pip3 install google-api-python-client google-auth
# or in venv:
source ./activate-ape-env.sh
pip install google-api-python-client google-auth
```

## Cleanup Test Resources

If you want to delete the test project after verification:

```bash
# List your projects
gcloud projects list

# Delete test project (CAUTION: Irreversible!)
gcloud projects delete project-ape-XXXXX

# Confirm deletion when prompted
```

**Note:** Deleting the project also deletes:
- Service account
- API enablement
- All project resources

**Files to clean up locally:**
```bash
# Remove test files
rm service-account-key.json
rm .env
rm vars.py

# Or move to backup
mkdir -p test-backups
mv service-account-key.json test-backups/
mv .env test-backups/
```

## Success Criteria

The script works correctly if:

1. ✅ **Script completes** without errors
2. ✅ **Files created:**
   - `service-account-key.json` (600 permissions)
   - `.env` (with correct values)
3. ✅ **Google Cloud Console** shows new project
4. ✅ **Drive API** is enabled
5. ✅ **Service account** exists and is accessible
6. ✅ **Python test** can list shared Drive folders
7. ✅ **Integration test** (optional) runs without Drive errors

## Next Steps After Successful Test

1. **Keep the service account** for production use
2. **Share actual client Drive folders** with the service account
3. **Configure real clients** in `vars.py`
4. **Run production pipeline:** `./launch_ape.sh fast`

## Test Report Template

After testing, document results:

```
========================================================================
SERVICE ACCOUNT CREATION SCRIPT TEST REPORT
========================================================================

Date: _______________
Tester: _______________

ENVIRONMENT:
- OS: macOS / Linux
- gcloud version: _______________
- Python version: _______________

TEST RESULTS:
[ ] Script installed gcloud (if needed)
[ ] Authentication successful
[ ] Project created: project-ape-_______
[ ] Billing enabled
[ ] Drive API enabled
[ ] Service account created
[ ] Key file generated (600 permissions)
[ ] .env file created
[ ] Drive folder sharing works
[ ] Python test passed
[ ] Integration test passed (optional)

ISSUES ENCOUNTERED:
_________________________________________________________________
_________________________________________________________________

RESOLUTION:
_________________________________________________________________
_________________________________________________________________

OVERALL RESULT: ✅ PASS / ❌ FAIL

NOTES:
_________________________________________________________________
_________________________________________________________________
```

## Advanced Testing

### Test with Existing Project

Re-run the script and choose option 2:

```bash
./create-service-account.sh
# Choose: 2. Use existing project
# Enter project ID from first test
```

**Verify:**
- Reuses existing project
- Creates/reuses service account
- Generates new key (or keeps existing)

### Test Error Handling

Intentionally trigger errors to verify handling:

```bash
# Test 1: No internet connection
# Disconnect network, run script
# Expected: Clear error message

# Test 2: No billing
# Use project without billing
# Expected: Prompt to enable billing

# Test 3: Insufficient permissions
# Use restricted account
# Expected: Clear permission error
```

## Questions or Issues?

If you encounter problems:

1. Check this testing guide for solutions
2. Review `create-service-account.sh` output for specific errors
3. Verify Google Cloud Console shows expected resources
4. Check `service-account-key.json` is valid JSON
5. Ensure billing is enabled
6. Verify Drive API is enabled

## Summary

This testing procedure validates:
- ✅ Script execution
- ✅ Google Cloud integration
- ✅ File generation
- ✅ Service account permissions
- ✅ Drive API access
- ✅ Error handling

**Estimated testing time:** 10-15 minutes (first time)
