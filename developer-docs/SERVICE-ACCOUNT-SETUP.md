# Google Service Account Setup Guide

![King Kong Logo](dashboard/static/kingkong.png)

**Project APE - Complete Service Account Configuration**

**Version:** 3.0.6  
**Last Updated:** June 17, 2026

---

## 📋 Overview

This guide walks you through creating a Google Cloud service account for Project APE's Google Drive integration. The service account allows Project APE to automatically download client documents from Google Drive folders without requiring manual authentication.

### What You'll Create

1. **Google Cloud Project** - Container for your service account
2. **Service Account** - Non-human identity for automated API access
3. **Service Account Key** - JSON credentials file
4. **Drive API Access** - Enable Google Drive API for the project

### Time Required

**~15-20 minutes** (one-time setup)

### What You'll Need

- ✅ Google account with access to Google Cloud Console
- ✅ Google Drive folders containing client documents to share
- ✅ Project APE cloned to your machine

**Cost:** Google Cloud free tier is sufficient for typical Project APE usage (minimal API calls)

---

## 📖 Quick Navigation

1. [Create Google Cloud Project](#step-1-create-google-cloud-project)
2. [Enable Google Drive API](#step-2-enable-google-drive-api)
3. [Create Service Account](#step-3-create-service-account)
4. [Generate Service Account Key](#step-4-generate-service-account-key)
5. [Configure Project APE](#step-5-configure-project-ape)
6. [Share Drive Folders](#step-6-share-drive-folders-with-service-account)
7. [Verify Setup](#step-7-verify-setup)
8. [Troubleshooting](#troubleshooting)

---

## Step 1: Create Google Cloud Project

### 1.1 Access Google Cloud Console

1. Open your browser and navigate to: [https://console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account
3. Click **Console** in the top-right if you're on the landing page

### 1.2 Create New Project

1. **Click the project dropdown** in the top navigation bar
   - Located next to the "Google Cloud" logo
   - Shows current project name or "Select a project"

   ![Screenshot: Project dropdown location]
   ```
   ┌─────────────────────────────────────────┐
   │ ☰  Google Cloud  [▼ Select Project]    │
   └─────────────────────────────────────────┘
   ```

2. **Click "NEW PROJECT"** button
   - Located in the top-right of the project selector dialog

   ![Screenshot: New Project button]

3. **Fill in project details:**
   - **Project name:** `project-ape` (or your preferred name)
   - **Organization:** Leave as default (usually "No organization" for personal accounts)
   - **Location:** Leave as default

   ![Screenshot: New project form]
   ```
   Project name: [project-ape        ]
   
   Organization: [No organization ▼   ]
   
   Location:     [No organization      ]
   
   [CANCEL]  [CREATE]
   ```

4. **Click "CREATE"**
   - Wait 5-10 seconds for project creation

5. **Select your new project**
   - Click the project dropdown again
   - Select `project-ape` from the list
   - Verify the project name appears in the top navigation

**✅ Checkpoint:** Project name "project-ape" is visible in the top navigation bar

---

## Step 2: Enable Google Drive API

### 2.1 Navigate to APIs & Services

1. **Click the hamburger menu** (☰) in the top-left corner
2. Scroll down to **"APIs & Services"**
3. Click **"Library"**

   ![Screenshot: Navigation menu with APIs & Services highlighted]
   ```
   ☰ Navigation Menu
   ├── Home
   ├── ...
   ├── 📚 APIs & Services
   │   ├── Dashboard
   │   ├── Library       ← Click here
   │   ├── Credentials
   │   └── ...
   ```

### 2.2 Search for Google Drive API

1. In the API Library search box, type: **`Google Drive API`**
2. Click on **"Google Drive API"** from the search results
   - Look for the official Google API (usually first result)

   ![Screenshot: API Library search results]

### 2.3 Enable the API

1. Click the **"ENABLE"** button
2. Wait 5-10 seconds for the API to be enabled
3. You'll be redirected to the API dashboard

**✅ Checkpoint:** Google Drive API page shows "API enabled" with a green checkmark

---

## Step 3: Create Service Account

### 3.1 Navigate to Service Accounts

1. **Click the hamburger menu** (☰) again
2. Go to **"IAM & Admin"**
3. Click **"Service Accounts"**

   ![Screenshot: Navigation to Service Accounts]
   ```
   ☰ Navigation Menu
   ├── ...
   ├── 🔐 IAM & Admin
   │   ├── IAM
   │   ├── Service Accounts  ← Click here
   │   ├── ...
   ```

### 3.2 Create New Service Account

1. Click **"+ CREATE SERVICE ACCOUNT"** at the top of the page

   ![Screenshot: Create Service Account button]

2. **Fill in service account details:**

   **Service account details (Step 1 of 3):**
   - **Service account name:** `project-ape-service`
   - **Service account ID:** `project-ape-service` (auto-filled)
   - **Description:** `Service account for Project APE Google Drive access`

   ![Screenshot: Service account creation form]
   ```
   Service account name: [project-ape-service            ]
   
   Service account ID:   [project-ape-service            ]
   (Auto-generated from name)
   
   Description:          [Service account for Project... ]
   
   [CANCEL]  [CREATE AND CONTINUE]
   ```

3. **Click "CREATE AND CONTINUE"**

### 3.3 Grant Permissions (Step 2 of 3)

**Important:** Skip this step - no project-level roles are needed.

1. **Click "CONTINUE"** without selecting any roles
   - Project APE only needs access to specific Drive folders (granted later via sharing)
   - No project-level permissions required

   ![Screenshot: Grant access step with no roles selected]

### 3.4 Grant User Access (Step 3 of 3)

**Optional:** Skip this step unless you want other users to manage this service account.

1. **Click "DONE"** to finish

### 3.5 Note Your Service Account Email

After creation, you'll see your service account in the list:

```
project-ape-service@project-ape.iam.gserviceaccount.com
```

**Copy this email address** - you'll need it to share Google Drive folders in Step 6.

![Screenshot: Service accounts list showing the new service account]

**✅ Checkpoint:** Service account created and email address copied

---

## Step 4: Generate Service Account Key

### 4.1 Open Service Account Details

1. From the Service Accounts list, **click on your service account email:**
   ```
   project-ape-service@project-ape.iam.gserviceaccount.com
   ```

   ![Screenshot: Clicking on service account email]

### 4.2 Create New Key

1. Click the **"KEYS"** tab at the top
2. Click **"ADD KEY"** dropdown button
3. Select **"Create new key"**

   ![Screenshot: Keys tab with ADD KEY button]
   ```
   ┌─────────────────────────────────────────┐
   │ DETAILS  PERMISSIONS  [KEYS]            │
   ├─────────────────────────────────────────┤
   │                                          │
   │  [+ ADD KEY ▼]                          │
   │     ├─ Create new key                   │
   │     └─ Upload existing key              │
   └─────────────────────────────────────────┘
   ```

### 4.3 Select Key Type

1. In the dialog, select **"JSON"** as the key type
2. Click **"CREATE"**

   ![Screenshot: Key type selection dialog]
   ```
   Create private key
   
   Key type:
   ● JSON       (Recommended)
   ○ P12
   
   [CANCEL]  [CREATE]
   ```

### 4.4 Save the Key File

1. Your browser will automatically download a JSON file named:
   ```
   project-ape-xxxxxx.json
   ```
   (where `xxxxxx` is your project ID)

2. **Move this file to your Project APE directory:**
   
   ```bash
   # Example: Move from Downloads to Project APE folder
   mv ~/Downloads/project-ape-*.json ~/Project-APE/project-ape-service-key.json
   ```

3. **Secure the file permissions:**
   
   ```bash
   chmod 600 ~/Project-APE/project-ape-service-key.json
   ```

4. **⚠️ IMPORTANT:** This file contains sensitive credentials
   - Never commit it to git
   - Never share it publicly
   - Store it securely
   - Only Project APE on your machine needs access

**✅ Checkpoint:** Service account key JSON file saved in Project APE directory with 600 permissions

---

## Step 5: Configure Project APE

### 5.1 Locate Your Service Account Key

```bash
cd ~/Project-APE
ls -la project-ape-service-key.json
```

Expected output:
```
-rw-------  1 yourusername  staff  2350 Jun 17 10:30 project-ape-service-key.json
```

Verify permissions show `-rw-------` (only you can read/write).

### 5.2 Create .env File

```bash
# Copy the template
cp .env.template .env
```

The `.env.template` file already has the correct configuration:
```bash
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

**You don't need to modify .env** - the `launch_ape.sh` script automatically mounts your service account key file into the container at `/app/service-account.json`.

### 5.3 Verify Configuration

```bash
# Check that .env exists
cat .env

# Output should show:
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

**✅ Checkpoint:** `.env` file created with correct container path

---

## Step 6: Share Drive Folders with Service Account

**⚠️ CRITICAL STEP:** The service account needs "Viewer" access to each Google Drive folder before Project APE can download files.

### 6.1 Get Your Service Account Email

From Step 3.5, your service account email is:
```
project-ape-service@project-ape.iam.gserviceaccount.com
```

**Keep this email handy** - you'll paste it multiple times.

### 6.2 Share Each Client Folder

**Repeat these steps for EACH client folder** you configured in `vars.py`:

#### Open Google Drive

1. Navigate to [drive.google.com](https://drive.google.com) in your browser
2. Sign in with your Google account

#### Locate the Client Folder

1. Find the folder containing your client's documents
   - Example: "Acme Corp Documents", "TechCo Files", etc.
2. These are the folders whose URLs you put in `vars.py`

#### Share the Folder

1. **Right-click on the folder** → Click **"Share"**
   
   Or:
   - Click the folder to select it
   - Click the **Share icon** (person with +) in the toolbar

   ![Screenshot: Right-click menu with Share option]
   ![Screenshot: Share icon in toolbar]

2. **Add the service account:**
   - In the "Add people and groups" field, **paste your service account email:**
     ```
     project-ape-service@project-ape.iam.gserviceaccount.com
     ```
   - Press **Enter** or **Tab**

   ![Screenshot: Share dialog with service account email entered]
   ```
   Share "Acme Corp Documents"
   
   Add people and groups
   ┌─────────────────────────────────────┐
   │ project-ape-service@project-ape...  │
   └─────────────────────────────────────┘
   
   project-ape-service@...  [Viewer ▼]
   
   ☐ Notify people
   
   [Cancel]  [Share]
   ```

3. **Set permission level:**
   - Click the dropdown next to the service account email
   - Select **"Viewer"**
   - **Do NOT grant "Editor" or "Owner"** - Viewer is sufficient and more secure

4. **Disable notification:**
   - **Uncheck** "Notify people"
   - Service accounts don't receive emails anyway

5. **Click "Share"** to finalize

#### Verify Sharing

1. Open the folder's sharing settings again
2. Verify the service account appears in "People with access"
3. Permission should show "Viewer"

   ![Screenshot: Sharing settings showing service account with Viewer access]
   ```
   People with access
   
   👤 you@gmail.com (Owner)
   🤖 project-ape-service@... (Viewer)  ← Should see this
   ```

### 6.3 Track Your Shared Folders

Create a reference file to document which folders are shared:

```bash
cat > drive-folders-shared.txt << 'EOF'
# Project APE - Google Drive Folders
# Service Account: project-ape-service@project-ape.iam.gserviceaccount.com

# Client 1
https://drive.google.com/drive/folders/YOUR_FOLDER_ID_1
Shared: ✅ 2026-06-17

# Client 2
https://drive.google.com/drive/folders/YOUR_FOLDER_ID_2
Shared: ✅ 2026-06-17

# [Add all your client folders here]
EOF
```

**✅ Checkpoint:** All Google Drive folders shared with service account email, permission set to "Viewer"

---

## Step 7: Verify Setup

### 7.1 Verify Service Account Key File

```bash
cd ~/Project-APE

# Check file exists
ls -la project-ape-service-key.json

# Verify it's valid JSON
python3 -c "import json; print('✅ Valid JSON' if json.load(open('project-ape-service-key.json')) else '❌ Invalid')"

# Check service account email in JSON
grep -o '"client_email": "[^"]*"' project-ape-service-key.json
```

Expected output:
```
"client_email": "project-ape-service@project-ape.iam.gserviceaccount.com"
```

### 7.2 Verify Environment Configuration

```bash
# Check .env exists
ls -la .env

# View contents
cat .env
```

Expected output:
```
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

### 7.3 Test Download (Optional)

Create a simple test to verify the service account can access a shared folder:

```bash
# Install google-api-python-client for testing
pip3 install google-api-python-client google-auth

# Test Drive API access
python3 << 'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load service account credentials
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_file(
    'project-ape-service-key.json', scopes=SCOPES)

# Build Drive API client
service = build('drive', 'v3', credentials=credentials)

# List files shared with this service account
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
    print("⚠️  No files found. Make sure you shared folders with the service account.")
EOF
```

Expected output:
```
✅ Service account can access Drive API!

Files/folders shared with service account:
  - Acme Corp Documents
  - TechCo Files
  - Client ABC Folder
  ...
```

**✅ Checkpoint:** Service account successfully authenticates and can list shared folders

---

## Troubleshooting

### Issue: "403 Forbidden" when accessing Drive

**Cause:** Service account doesn't have access to the folder

**Solution:**
1. Verify you shared the folder with the correct service account email
2. Check the permission level is "Viewer" or higher
3. Try removing and re-sharing the folder
4. Wait 1-2 minutes after sharing for permissions to propagate

### Issue: "Service account key file not found"

**Cause:** File path in `.env` is incorrect or file doesn't exist

**Solution:**
```bash
# Verify file exists
ls -la ~/Project-APE/project-ape-service-key.json

# Check .env has correct container path
cat .env
# Should show: GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

### Issue: "Invalid JSON" error

**Cause:** Service account key file is corrupted or incomplete

**Solution:**
1. Re-download the key from Google Cloud Console (Step 4)
2. Verify the downloaded file is valid JSON:
   ```bash
   python3 -c "import json; json.load(open('project-ape-service-key.json'))"
   ```

### Issue: Cannot find service account email

**Solution:**
```bash
# Extract email from JSON key file
grep '"client_email"' project-ape-service-key.json
```

Output:
```
"client_email": "project-ape-service@project-ape.iam.gserviceaccount.com"
```

### Issue: "API not enabled" error

**Cause:** Google Drive API not enabled for the project

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to **APIs & Services** → **Library**
4. Search for "Google Drive API"
5. Click **ENABLE**

---

## Security Best Practices

### Protecting Your Service Account Key

**✅ DO:**
- Store the key file in your Project APE directory only
- Use `chmod 600` to restrict file permissions
- Add `*.json` to `.gitignore` to prevent accidental commits
- Keep backups in a secure location (password manager, encrypted drive)
- Rotate keys periodically (every 90 days)

**❌ DO NOT:**
- Commit the key file to git repositories
- Share the key file via email or messaging
- Upload the key to public cloud storage
- Copy the key to multiple directories unnecessarily
- Store the key in plain text notes or documentation

### Principle of Least Privilege

- ✅ Grant service account **"Viewer"** access only (read-only)
- ❌ Avoid granting "Editor" or "Owner" unless absolutely required
- ✅ Share only specific folders, not entire Drive
- ✅ Regularly audit which folders are shared with the service account

### Monitoring Access

Periodically review service account activity:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click your service account
4. Check **"Activity"** tab for recent API calls

---

## Next Steps

Now that your service account is configured:

1. **Configure `vars.py`** with your client information
   ```bash
   cp example-vars.py vars.py
   nano vars.py
   ```

2. **Authenticate with NotebookLM**
   ```bash
   notebooklm login
   ```

3. **Setup credentials in container**
   ```bash
   ./setup-credentials.sh
   ```

4. **Launch Project APE**
   ```bash
   ./launch_ape.sh fast
   ```

5. **Monitor progress**
   - Dashboard: [http://localhost:8765](http://localhost:8765)

See [README.md](README.md) for complete usage documentation.

---

## Additional Resources

- **Google Cloud Service Accounts Overview:**  
  https://cloud.google.com/iam/docs/service-accounts

- **Google Drive API Documentation:**  
  https://developers.google.com/drive/api

- **Project APE Documentation:**
  - [README.md](README.md) - Main documentation
  - [EXECUTIVE-SUMMARY.md](EXECUTIVE-SUMMARY.md) - Why Project APE?
  - [README.md](README.md) - Step-by-step guide

---

**Questions or issues?** Open an issue in the Project APE repository.

**Last Updated:** June 17, 2026
