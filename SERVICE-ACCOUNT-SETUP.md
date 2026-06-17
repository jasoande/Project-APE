# Service Account Setup Guide

![King Kong Logo](dashboard/static/kingkong.png)

**Project APE - Complete Service Account Configuration**

**Project Owner & Maintainer:** Jason Anderson  
**Version:** 3.1.0  
**Last Updated:** 2026-06-15

---

## 📋 Overview

This guide walks you through creating a Google Cloud service account configured for **both** Gemini AI and Google Drive access in Project APE. By using a single service account for both services, you simplify authentication and credential management.

### What You'll Set Up

1. **Google Cloud Project** - Container for your resources
2. **Service Account** - Non-human identity for API access
3. **Gemini API Key** - For AI-powered industry/subsegment detection
4. **Drive API Access** - For automatic folder downloads
5. **Environment Configuration** - Credentials in `.env` file
6. **Folder Sharing** - Grant service account access to Drive folders

### Time Required

**~15-20 minutes** (one-time setup)

---

## 🎯 Prerequisites

Before starting, ensure you have:

- ✅ Google account with access to Google Cloud Console
- ✅ Project APE repository cloned locally
- ✅ Google Drive folders containing client documents
- ✅ Basic understanding of Google Cloud Console navigation

**Cost:** Free tier sufficient for typical Project APE usage

---

## 📖 Table of Contents

1. [Create Google Cloud Project](#1-create-google-cloud-project)
2. [Create Service Account](#2-create-service-account)
3. [Enable Gemini API](#3-enable-gemini-api)
4. [Create Gemini API Key](#4-create-gemini-api-key)
5. [Enable Google Drive API](#5-enable-google-drive-api)
6. [Generate Service Account Key](#6-generate-service-account-key)
7. [Configure Environment Variables](#7-configure-environment-variables)
8. [Share Drive Folders](#8-share-drive-folders)
9. [Verify Setup](#9-verify-setup)
10. [Troubleshooting](#troubleshooting)

---

## 1. Create Google Cloud Project

### Step 1.1: Access Google Cloud Console

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **Console** in the top-right if not already there

### Step 1.2: Create New Project

1. Click the **project dropdown** in the top navigation bar
   - Located next to "Google Cloud" logo
   - Shows current project name or "Select a project"

2. Click **"NEW PROJECT"** in the top-right of the dialog

3. Fill in project details:
   - **Project name:** `project-ape` (or your preferred name)
   - **Organization:** Leave as-is (your organization or "No organization")
   - **Location:** Leave default or select your organization

4. Click **"CREATE"**

5. Wait for project creation (~10 seconds)

### Step 1.3: Select Your Project

1. Click the **project dropdown** again
2. Select your newly created project (`project-ape`)
3. Verify project name appears in top navigation bar

**✅ Checkpoint:** Project name "project-ape" visible in top navigation

---

## 2. Create Service Account

### Step 2.1: Navigate to IAM & Admin

1. Click **☰ (hamburger menu)** in top-left
2. Scroll down to **"IAM & Admin"**
3. Click **"Service Accounts"**

Or use direct link: `https://console.cloud.google.com/iam-admin/serviceaccounts`

### Step 2.2: Create Service Account

1. Click **"+ CREATE SERVICE ACCOUNT"** at the top

2. **Service account details:**
   - **Service account name:** `project-ape-service`
   - **Service account ID:** `project-ape-service` (auto-filled)
   - **Description:** `Service account for Project APE - Gemini AI and Google Drive access`
   
3. Click **"CREATE AND CONTINUE"**

4. **Grant this service account access to project (Optional):**
   - **Select a role:** Click the dropdown
   - Search for: `Generative Language User`
   - Select: **Generative Language User**
   - This grants Gemini API access at project level
   
5. Click **"CONTINUE"**

6. **Grant users access to this service account (Optional):**
   - Leave blank (not needed)
   
7. Click **"DONE"**

### Step 2.3: Note Service Account Email

You should see your new service account in the list:

```
project-ape-service@your-project-id.iam.gserviceaccount.com
```

**📝 IMPORTANT:** Copy this email address - you'll need it later for Drive folder sharing.

**Example:**
```
project-ape-service@project-ape-123456.iam.gserviceaccount.com
```

**✅ Checkpoint:** Service account appears in list with email address

---

## 3. Enable Gemini API

### Step 3.1: Navigate to API Library

1. Click **☰ (hamburger menu)** in top-left
2. Click **"APIs & Services"**
3. Click **"Library"**

Or use direct link: `https://console.cloud.google.com/apis/library`

### Step 3.2: Enable Generative Language API

1. In the search bar, type: `Generative Language API`

2. Click on **"Generative Language API"** (by Google)
   - Description: "API for Gemini models"

3. Click **"ENABLE"** button

4. Wait for API to enable (~10 seconds)

5. You'll be redirected to the API dashboard

**✅ Checkpoint:** "Generative Language API" shows as "Enabled" in APIs list

---

## 4. Create Gemini API Key

### Step 4.1: Navigate to Credentials

1. From the API dashboard, click **"Credentials"** in left sidebar

Or:
1. Click **☰ (hamburger menu)** in top-left
2. Click **"APIs & Services"**
3. Click **"Credentials"**

### Step 4.2: Create API Key

1. Click **"+ CREATE CREDENTIALS"** at the top

2. Select **"API key"** from the dropdown

3. API key will be generated immediately - a dialog appears showing:
   ```
   API key created
   Your new API key: AIzaSyA...
   ```

4. **📝 IMPORTANT:** Click **"COPY"** to copy the API key

5. **Save this key securely** - you'll add it to `.env` file later

### Step 4.3: Restrict API Key (Recommended)

1. Click **"EDIT API KEY"** in the dialog (or click the key in credentials list)

2. **API restrictions:**
   - Click **"Restrict key"**
   - Select **"Generative Language API"** from the dropdown
   - This prevents the key from being used for other APIs

3. **Application restrictions (Optional):**
   - For enhanced security, restrict to specific IP addresses
   - For development: Leave as "None"

4. Click **"SAVE"**

**✅ Checkpoint:** API key copied and saved securely

**Example API Key Format:**
```
AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567
```

---

## 5. Enable Google Drive API

### Step 5.1: Navigate to API Library

1. Click **☰ (hamburger menu)** in top-left
2. Click **"APIs & Services"**
3. Click **"Library"**

### Step 5.2: Enable Google Drive API

1. In the search bar, type: `Google Drive API`

2. Click on **"Google Drive API"** (by Google)
   - Description: "The Google Drive API allows clients to access resources from Google Drive."

3. Click **"ENABLE"** button

4. Wait for API to enable (~10 seconds)

**✅ Checkpoint:** "Google Drive API" shows as "Enabled" in APIs list

---

## 6. Generate Service Account Key

### Step 6.1: Navigate to Service Accounts

1. Click **☰ (hamburger menu)** in top-left
2. Click **"IAM & Admin"**
3. Click **"Service Accounts"**

### Step 6.2: Create JSON Key

1. Find your service account in the list:
   ```
   project-ape-service@your-project-id.iam.gserviceaccount.com
   ```

2. Click the **⋮ (three dots)** on the right side of the service account row

3. Click **"Manage keys"**

4. Click **"ADD KEY"** dropdown button

5. Select **"Create new key"**

6. **Key type:**
   - Select **"JSON"** (should be selected by default)

7. Click **"CREATE"**

8. JSON key file will download automatically:
   ```
   your-project-id-1a2b3c4d5e6f.json
   ```

### Step 6.3: Secure the Key File

1. **Move the file to your Project APE directory:**
   ```bash
   cd ~/Downloads
   mv your-project-id-*.json ~/dev/Project-APE/
   cd ~/dev/Project-APE/
   ```

2. **Rename for clarity (optional but recommended):**
   ```bash
   mv your-project-id-1a2b3c4d5e6f.json project-ape-service-key.json
   ```

3. **Set restrictive permissions:**
   ```bash
   chmod 600 project-ape-service-key.json
   ```

4. **Verify the file contents:**
   ```bash
   cat project-ape-service-key.json
   ```
   
   Should see JSON with fields like:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "project-ape-service@your-project-id.iam.gserviceaccount.com",
     "client_id": "...",
     ...
   }
   ```

**⚠️ SECURITY WARNING:**
- **Never commit this file to git**
- **Never share this file publicly**
- Store securely with restricted permissions (chmod 600)
- Add to `.gitignore`

**✅ Checkpoint:** JSON key file downloaded and secured in Project APE directory

---

## 7. Configure Environment Variables

### Step 7.1: Create/Update .env File

1. Navigate to Project APE directory:
   ```bash
   cd ~/dev/Project-APE/
   ```

2. Create or edit `.env` file:
   ```bash
   nano .env
   ```
   
   Or use your preferred editor:
   ```bash
   code .env    # VS Code
   vim .env     # Vim
   ```

### Step 7.2: Add Credentials

Add the following lines to `.env`:

```bash
# Gemini AI API Key (for industry/subsegment detection)
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567

# Google Drive Service Account Key (for Drive folder access)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/yourusername/dev/Project-APE/project-ape-service-key.json
```

**Replace with your actual values:**
- `GEMINI_API_KEY`: Your API key from Step 4
- `GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY`: Full absolute path to your JSON key file

**Example:**
```bash
GEMINI_API_KEY=AIzaSyB8RN6IV86r68TlVZTjZF34HxmqjwRzzLg
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/jasona/dev/Project-APE/project-ape-service-key.json
```

### Step 7.3: Verify File Permissions

```bash
# Secure .env file
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (only you can read/write)

ls -la project-ape-service-key.json
# Should show: -rw------- (only you can read/write)
```

### Step 7.4: Add to .gitignore

Ensure these files are never committed to git:

```bash
# Check if .gitignore exists
cat .gitignore
```

Verify these lines are present:
```
.env
*.json
project-ape-service-key.json
```

If not, add them:
```bash
echo ".env" >> .gitignore
echo "*.json" >> .gitignore
echo "project-ape-service-key.json" >> .gitignore
```

**✅ Checkpoint:** `.env` file created with both credentials, secured with chmod 600

---

## 8. Share Drive Folders

**⚠️ CRITICAL STEP:** The service account needs "Viewer" access to each Google Drive folder before Project APE can download files.

### Step 8.1: Get Service Account Email

From Step 2.3, your service account email is:
```
project-ape-service@your-project-id.iam.gserviceaccount.com
```

**Copy this email address** - you'll use it multiple times.

### Step 8.2: Share Each Client Folder

**Repeat for EACH client folder in vars.py:**

1. **Open Google Drive** in your browser:
   - Navigate to [drive.google.com](https://drive.google.com)
   
2. **Locate the client folder:**
   - Find the folder containing client documents
   - Example: "Merck Test Documents", "Blue Yonder Files", etc.

3. **Open sharing settings:**
   - **Right-click** on the folder
   - Click **"Share"**
   
   Or:
   - Click the folder to select it
   - Click the **Share icon** (person with +) in the top-right

4. **Add service account:**
   - In the "Add people and groups" field
   - **Paste the service account email:**
     ```
     project-ape-service@your-project-id.iam.gserviceaccount.com
     ```
   - Press Enter or Tab

5. **Set permissions:**
   - Click the dropdown next to the service account email
   - Select **"Viewer"**
   - ⚠️ **Important:** Do NOT grant "Editor" or "Owner" - Viewer is sufficient and more secure

6. **Disable notification:**
   - **Uncheck** "Notify people" (service accounts don't receive emails)

7. **Share the folder:**
   - Click **"Share"** or **"Send"** button

8. **Verify sharing:**
   - Service account email should appear in "People with access" section
   - Permission should show "Viewer"

### Step 8.3: Document Your Folders

Create a reference file tracking which folders are shared:

```bash
cat > drive-folders.txt << 'EOF'
# Project APE - Google Drive Folders
# Service Account: project-ape-service@your-project-id.iam.gserviceaccount.com

# Merck Test
https://drive.google.com/drive/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen
Shared: ✅ 2026-06-15

# Blue Yonder Test  
https://drive.google.com/drive/folders/1GnoQMM8ZK-0PSZElLIWa2z_3fy1TpoBK
Shared: ✅ 2026-06-15

# Organon Test
https://drive.google.com/drive/folders/1nOX6hkDDRhKUEvtllTNte-XbTsk24hsg
Shared: ✅ 2026-06-15

# [Add all your client folders here]
EOF
```

**✅ Checkpoint:** All Drive folders shared with service account email, permissions set to "Viewer"

---

## 9. Verify Setup

### Step 9.1: Verify Environment Variables

```bash
cd ~/dev/Project-APE/

# Check .env file exists and is readable
ls -la .env

# Verify contents (be careful - contains secrets!)
cat .env
```

Expected output:
```bash
GEMINI_API_KEY=AIzaSy...
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/jasona/dev/Project-APE/project-ape-service-key.json
```

### Step 9.2: Verify Service Account Key File

```bash
# Check file exists
ls -la project-ape-service-key.json

# Verify it's valid JSON
python3 -c "import json; print('✅ Valid JSON' if json.load(open('project-ape-service-key.json')) else '❌ Invalid')"

# Check service account email in JSON
grep -o '"client_email": "[^"]*"' project-ape-service-key.json
```

Expected output:
```
"client_email": "project-ape-service@your-project-id.iam.gserviceaccount.com"
```

### Step 9.3: Test Gemini API Access

```bash
# Quick test of Gemini API
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key and api_key.startswith('AIza'):
    print("✅ Gemini API key configured correctly")
    print(f"   Key: {api_key[:20]}...")
else:
    print("❌ Gemini API key not found or invalid")
EOF
```

### Step 9.4: Test Google Drive Access

Create a quick test script:

```bash
cat > test_drive_access.py << 'EOF'
#!/usr/bin/env python3
"""Quick test of Google Drive service account access."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment
load_dotenv()

# Get service account key path
key_file = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY')

if not key_file:
    print("❌ GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY not set in .env")
    sys.exit(1)

if not Path(key_file).exists():
    print(f"❌ Service account key file not found: {key_file}")
    sys.exit(1)

print(f"✅ Service account key file exists: {key_file}")

try:
    # Authenticate
    creds = service_account.Credentials.from_service_account_file(
        key_file,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    print(f"✅ Service account authenticated: {creds.service_account_email}")
    
    # Test Drive API access
    service = build('drive', 'v3', credentials=creds)
    print("✅ Google Drive API service created successfully")
    
    # List accessible files (should be empty or show shared folders)
    results = service.files().list(pageSize=10).execute()
    files = results.get('files', [])
    
    if files:
        print(f"✅ Can access {len(files)} files/folders")
        for f in files[:3]:
            print(f"   - {f['name']}")
    else:
        print("⚠️  No files accessible (share folders with service account)")
    
    print("\n✅ Google Drive setup is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

chmod +x test_drive_access.py
python3 test_drive_access.py
```

Expected output:
```
✅ Service account key file exists: /Users/jasona/dev/Project-APE/project-ape-service-key.json
✅ Service account authenticated: project-ape-service@project-ape-123456.iam.gserviceaccount.com
✅ Google Drive API service created successfully
✅ Can access 6 files/folders
   - Merck Test Documents
   - Blue Yonder Files
   - Organon Documents
✅ Google Drive setup is working correctly!
```

### Step 9.5: Test Full Pipeline (Optional)

Run a single client to verify end-to-end:

```bash
# Test with one client using Google Drive folder
python3 main.py --mode fast --clients merck_test

# Watch logs
tail -f logs/merck_test.log
```

Look for these log messages:
```
✅ Using cached Drive files
# or
⬇️  Downloading from Drive...
✅ Downloaded 34 files from Drive
```

**✅ Checkpoint:** All tests pass, ready to run Project APE with Drive integration

---

## 🔐 Security Best Practices

### Credential Management

**DO:**
- ✅ Store credentials in `.env` file (never in code)
- ✅ Use `chmod 600` on sensitive files
- ✅ Add `.env` and `*.json` to `.gitignore`
- ✅ Rotate service account keys periodically (every 90 days)
- ✅ Use minimum required permissions (Viewer for Drive)
- ✅ Monitor API usage in Google Cloud Console

**DON'T:**
- ❌ Commit `.env` or JSON keys to git
- ❌ Share credentials via email/Slack/chat
- ❌ Grant "Editor" or "Owner" Drive permissions
- ❌ Use personal API keys for shared projects
- ❌ Store credentials in screenshots or documentation

### Service Account Permissions

**Principle of Least Privilege:**

1. **Gemini API:**
   - Role: `Generative Language User` (read-only)
   - No additional project roles needed

2. **Google Drive:**
   - Permission: `Viewer` only (per-folder)
   - No domain-wide delegation
   - No org-level permissions

### Key Rotation

**Recommended schedule:**

1. **Every 90 days:**
   - Create new service account key
   - Update `.env` with new key path
   - Test with one client
   - Delete old key from Google Cloud Console

2. **Immediately if compromised:**
   - Delete compromised key in Console
   - Generate new key
   - Update all environments
   - Review audit logs

### Monitoring

**Monitor API usage:**

1. Navigate to: [Google Cloud Console - APIs & Services - Dashboard](https://console.cloud.google.com/apis/dashboard)

2. Check quotas:
   - **Generative Language API:** Monitor requests/day
   - **Google Drive API:** Monitor read requests

3. Set up alerts:
   - Quota exceeded warnings
   - Unusual usage patterns

---

## 🐛 Troubleshooting

### Issue: GEMINI_API_KEY not working

**Symptoms:**
```
❌ Error: API key not valid
❌ 403 Forbidden
```

**Solutions:**

1. **Verify API key format:**
   ```bash
   # Should start with "AIza"
   grep GEMINI_API_KEY .env
   ```

2. **Check Generative Language API is enabled:**
   - Go to: [APIs & Services - Library](https://console.cloud.google.com/apis/library)
   - Search: "Generative Language API"
   - Should show "Manage" (not "Enable")

3. **Verify API key restrictions:**
   - Go to: [APIs & Services - Credentials](https://console.cloud.google.com/apis/credentials)
   - Click your API key
   - Ensure "Generative Language API" is in allowed list

4. **Test API key directly:**
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
   # Should return list of models, not error
   ```

### Issue: Cannot access Drive folders

**Symptoms:**
```
❌ No permission to access folder: 1abc123XYZ456
❌ Folder not found: 1abc123XYZ456
```

**Solutions:**

1. **Verify folder is shared:**
   - Open folder in Google Drive
   - Click "Share"
   - Confirm service account email is in "People with access"

2. **Check service account email:**
   ```bash
   grep client_email project-ape-service-key.json
   ```
   
   Must match email used for folder sharing.

3. **Verify Drive API is enabled:**
   - Go to: [APIs & Services - Library](https://console.cloud.google.com/apis/library)
   - Search: "Google Drive API"
   - Should show "Manage" (not "Enable")

4. **Test Drive access:**
   ```bash
   python3 test_drive_access.py
   ```

### Issue: Service account key file not found

**Symptoms:**
```
❌ Service account key not found: /path/to/key.json
```

**Solutions:**

1. **Verify file exists:**
   ```bash
   ls -la project-ape-service-key.json
   ```

2. **Check path in .env is absolute:**
   ```bash
   # BAD (relative path):
   GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=./key.json
   
   # GOOD (absolute path):
   GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/jasona/dev/Project-APE/project-ape-service-key.json
   ```

3. **Verify file permissions:**
   ```bash
   chmod 600 project-ape-service-key.json
   ```

### Issue: "Invalid JSON" error

**Symptoms:**
```
❌ Error: Invalid JSON in service account key
```

**Solutions:**

1. **Validate JSON syntax:**
   ```bash
   python3 -m json.tool project-ape-service-key.json
   ```

2. **Re-download key:**
   - Go to: [IAM & Admin - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click ⋮ (three dots) on service account
   - "Manage keys" → "Add Key" → "Create new key" → JSON
   - Replace old file

3. **Check for file corruption:**
   ```bash
   file project-ape-service-key.json
   # Should say: "JSON data"
   ```

### Issue: Rate limit exceeded

**Symptoms:**
```
❌ 429 Too Many Requests
⚠️  Quota exceeded for quota metric
```

**Solutions:**

1. **Check quota limits:**
   - Gemini API: 15 requests/minute, 1500 requests/day
   - Drive API: 12,000 requests/minute (typically not an issue)

2. **For Gemini:**
   - Use manual industry/subsegments in `vars.py` (bypass Gemini)
   - Reduce number of concurrent clients
   - Add delays between requests

3. **View quota usage:**
   - Go to: [APIs & Services - Dashboard](https://console.cloud.google.com/apis/dashboard)
   - Click "Generative Language API"
   - View "Quotas" tab

---

## 📋 Quick Reference

### Service Account Email Format

```
[service-account-name]@[project-id].iam.gserviceaccount.com
```

Example:
```
project-ape-service@project-ape-123456.iam.gserviceaccount.com
```

### File Locations

```bash
# Project APE directory
/Users/yourusername/dev/Project-APE/

# Service account key
/Users/yourusername/dev/Project-APE/project-ape-service-key.json

# Environment variables
/Users/yourusername/dev/Project-APE/.env

# Drive cache
~/.project-ape/drive_cache/
```

### Required APIs

- ✅ **Generative Language API** (Gemini)
- ✅ **Google Drive API**

### Required Credentials

1. **GEMINI_API_KEY** - API key (format: `AIzaSy...`)
2. **GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY** - Path to JSON key file

### Minimum Permissions

1. **Gemini:** `Generative Language User` role (project-level)
2. **Drive:** `Viewer` permission (per-folder)

---

## ✅ Setup Checklist

Use this checklist to verify complete setup:

### Google Cloud Setup

- [ ] Created Google Cloud project
- [ ] Created service account
- [ ] Noted service account email address
- [ ] Enabled Generative Language API
- [ ] Enabled Google Drive API

### Credentials

- [ ] Created Gemini API key
- [ ] Restricted API key to Generative Language API
- [ ] Generated service account JSON key
- [ ] Downloaded JSON key file
- [ ] Moved key file to Project APE directory
- [ ] Renamed key file (optional)
- [ ] Set file permissions (chmod 600)

### Environment Configuration

- [ ] Created/updated `.env` file
- [ ] Added GEMINI_API_KEY to `.env`
- [ ] Added GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY to `.env`
- [ ] Used absolute path for key file
- [ ] Secured `.env` file (chmod 600)
- [ ] Added `.env` and `*.json` to `.gitignore`

### Drive Folder Sharing

- [ ] Identified all client folders in Google Drive
- [ ] Shared each folder with service account email
- [ ] Set permissions to "Viewer" (not Editor/Owner)
- [ ] Disabled "Notify people" when sharing
- [ ] Documented which folders are shared

### Verification

- [ ] Verified .env file contents
- [ ] Validated service account key JSON
- [ ] Tested Gemini API access
- [ ] Tested Google Drive API access
- [ ] Ran test_drive_access.py successfully
- [ ] (Optional) Tested full pipeline with one client

### Security

- [ ] Credentials not committed to git
- [ ] File permissions set to 600
- [ ] Using minimum required permissions
- [ ] Documented key rotation schedule

---

## 🎓 Best Practices Summary

1. **One service account for both APIs** - Simpler credential management
2. **Restrict API key** - Only allow Generative Language API
3. **Viewer permissions only** - Never grant Editor/Owner for Drive folders
4. **Absolute paths** - Always use full paths in `.env`
5. **Secure storage** - chmod 600 on all credential files
6. **Never commit** - Add to `.gitignore` immediately
7. **Regular rotation** - Rotate keys every 90 days
8. **Monitor usage** - Check quotas in Cloud Console
9. **Document folders** - Keep track of which folders are shared
10. **Test before production** - Verify setup with single client first

---

## 📞 Support

**Having issues?**

1. Review [Troubleshooting](#troubleshooting) section above
2. Check [DRIVE-INTEGRATION.md](DRIVE-INTEGRATION.md) for Drive-specific help
3. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for general issues
4. Contact Jason Anderson (Project APE maintainer)

**Common Questions:**

- **Q: Can I use same service account for multiple projects?**
  - A: Yes, but recommended to create separate accounts for security isolation

- **Q: Do I need to reshare folders if I create new service account?**
  - A: Yes, share folders with the new service account email

- **Q: Can I use personal Gmail for service account?**
  - A: No, service accounts are separate from personal accounts

---

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE" width="100"/>
</p>

<h3 align="center">Project APE - Service Account Setup Complete</h3>

<p align="center">
  <strong>Ready to use Gemini AI and Google Drive!</strong><br>
  Maintained by Jason Anderson | 2026-06-15
</p>

---

**Next Steps:** Configure `vars.py` with your client details and Drive folder URLs, then run Project APE!
