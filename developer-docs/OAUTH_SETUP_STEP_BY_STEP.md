# Google Drive OAuth Setup - Step-by-Step Guide

**Time Required:** 5-10 minutes  
**Prerequisites:** Google account, Google Cloud SDK installed

---

## Overview

Project APE needs access to your Google Drive to download client documents. This guide walks you through the complete OAuth setup process.

**What the script does automatically:**
1. ✅ Creates/selects Google Cloud project
2. ✅ Enables Google Drive API
3. ✅ Opens Google Cloud Console for credential creation
4. ✅ **Finds your downloaded JSON file in ~/Downloads/**
5. ✅ **Moves it to ~/.project-ape/drive_credentials.json**
6. ✅ **Renames it from client_secret_*.json to drive_credentials.json**
7. ✅ Sets secure permissions (chmod 600)
8. ✅ Completes OAuth authentication
9. ✅ Saves token to ~/.project-ape/drive_token.json

---

## Step 1: Run the Setup Script

```bash
python3 setup-oauth-drive-improved.py
```

**Expected output:**
```
======================================================================
  Project APE - Automated OAuth Setup (Security Hardened)
======================================================================

This wizard will guide you through setting up Google Drive access.
Estimated time: 5-10 minutes
```

Press **Enter** to continue.

---

## Step 2: Authenticate with Google Cloud

**Script output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 1/5: Verify Google Cloud SDK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Cloud SDK is installed
✅ Authenticated as: your.email@example.com
```

If not authenticated:
```bash
gcloud auth login
```

---

## Step 3: Select or Create Project

**Script output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 2/5: Set Up Google Cloud Project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Do you want to:
  1. Select an existing project
  2. Create a new project

Choice (1/2):
```

**Choose option 2** (recommended - creates dedicated project for Project APE)

---

## Step 4: Enable Google Drive API

**Script output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 3/5: Enable Google Drive API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enabling Google Drive API...
✅ Google Drive API enabled successfully
```

This happens automatically.

---

## Step 5: Create OAuth Credentials (IMPORTANT!)

**Script output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 4/5: Create OAuth Credentials
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 You need to create OAuth credentials in the Google Cloud Console.

INSTRUCTIONS:
──────────────────────────────────────────────────────────────────────

1. The browser will open to the Credentials page
2. If you see a consent screen warning, click through it
3. Click: '+ CREATE CREDENTIALS' → 'OAuth client ID'

4. If prompted 'Configure Consent Screen':
   a. Choose 'External'
   b. App name: 'Project APE'
   c. User support email: (your email)
   d. Developer contact: (your email)
   e. Click 'SAVE AND CONTINUE' (3 times)
   f. Return to Credentials page

5. Create OAuth client ID:
   a. Application type: 'Desktop app'
   b. Name: 'Project APE Desktop'
   c. Click 'CREATE'

6. In the popup:
   a. Click 'DOWNLOAD JSON'
   b. Save to your Downloads folder (filename will be client_secret_*.json)
   c. Click 'OK'

7. This script will automatically:
   a. Find the downloaded file in ~/Downloads/
   b. Move it to ~/.project-ape/drive_credentials.json
   c. Set secure permissions (chmod 600)

──────────────────────────────────────────────────────────────────────

Press Enter to open Google Cloud Console...
```

### ⚠️ CRITICAL STEPS:

1. **Application Type:** MUST be **"Desktop app"** (not "Web application")
2. **Download Location:** Save to **~/Downloads/** folder
3. **Don't rename the file** - script will auto-rename it
4. **Don't move the file** - script will auto-move it

### What the file looks like:
```
client_secret_123456789-abcdefghijklmnop.apps.googleusercontent.com.json
```

---

## Step 6: Script Auto-Moves the File

After you download the JSON file and press Enter:

**Script output:**
```
✅ Found credentials file: client_secret_864693640316-av652qe9qko9gk2kckdiue3959bv0p4t.apps.googleusercontent.com.json
Moving to: /Users/yourname/.project-ape/drive_credentials.json
✅ Credentials file installed and secured (chmod 600)
```

**What happened behind the scenes:**
```bash
# Script automatically ran these commands:
mkdir -p ~/.project-ape
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_credentials.json
```

**You don't need to do anything!** The script handles everything.

---

## Step 7: Complete OAuth Authentication

**Script output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 5/5: Authenticate with Google
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Opening browser for Google authentication...
```

**Browser opens:**
1. Sign in with your Google account
2. Review permissions: "See and download all your Google Drive files"
3. Click **"Allow"**
4. You'll see "The authentication flow has completed"

**Script output:**
```
✅ OAuth token saved to: /Users/yourname/.project-ape/drive_token.json
✅ Token file secured (chmod 600)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Setup Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Google Drive access is now configured.

Created files:
  - /Users/yourname/.project-ape/drive_credentials.json
  - /Users/yourname/.project-ape/drive_token.json

Next steps:
  1. Run Project APE: ./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
  2. Files will be downloaded from Google Drive automatically
```

---

## Verification

**Check that files were created:**
```bash
ls -la ~/.project-ape/
```

**Expected output:**
```
drwx------   5 yourname  staff   160 Jun 30 17:30 .
drwxr-x---+ 89 yourname  staff  2848 Jun 30 17:30 ..
drwx------   3 yourname  staff    96 Jun 30 17:15 drive_cache/
-rw-------   1 yourname  staff   460 Jun 30 17:25 drive_credentials.json
-rw-------   1 yourname  staff   742 Jun 30 17:30 drive_token.json
```

**Key points:**
- ✅ Both files have permissions `600` (read/write for owner only)
- ✅ `drive_credentials.json` is ~460 bytes
- ✅ `drive_token.json` is ~740 bytes
- ✅ `drive_cache/` directory created

---

## Troubleshooting

### Error: "Could not find credentials file in Downloads folder"

**Cause:** File wasn't downloaded or was saved to a different location.

**Solution:**
```bash
# 1. Find the file
ls -la ~/Downloads/client_secret_*.json

# 2. If found, move it manually:
mkdir -p ~/.project-ape
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_credentials.json

# 3. Re-run the script
python3 setup-oauth-drive-improved.py
```

### Error: "OAuth credentials not found" in container

**Cause:** Ran OAuth setup inside container instead of on host machine.

**Solution:**
```bash
# 1. Exit container
exit

# 2. Run OAuth setup on HOST machine
python3 setup-oauth-drive-improved.py

# 3. Restart container
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

### Error: "Token has expired"

**Cause:** Token is older than 90 days.

**Solution:**
```bash
# 1. Delete old token
rm ~/.project-ape/drive_token.json

# 2. Re-authenticate
python3 setup-oauth-drive-improved.py
```

---

## File Locations Summary

| File | Location | Purpose | Auto-Generated? |
|------|----------|---------|-----------------|
| **Downloaded JSON** | `~/Downloads/client_secret_*.json` | OAuth credentials from Google | ❌ Manual download |
| **Credentials** | `~/.project-ape/drive_credentials.json` | OAuth client config | ✅ Auto-moved by script |
| **Token** | `~/.project-ape/drive_token.json` | OAuth access/refresh tokens | ✅ Auto-generated by script |
| **Cache** | `~/.project-ape/drive_cache/` | Downloaded Drive files | ✅ Auto-created on first download |

---

## Security Notes

**✅ Safe:**
- Credentials and tokens stored in `~/.project-ape/` with chmod 600
- Files are gitignored (never committed to version control)
- Token auto-refreshes every hour
- Containers mount credentials read-only

**⚠️ Keep Secret:**
- Never commit `drive_credentials.json` or `drive_token.json`
- Never share these files (contain your Google account access)
- Revoke access at any time: https://myaccount.google.com/permissions

---

## Next Steps

Now that OAuth is configured, you can run Project APE:

```bash
# Fast mode (10-12 minutes)
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast

# Deep mode (30-35 minutes, 8-9x more sources)
./ape-run.sh --vars ./vars.py --clients yourclient --mode deep
```

Files will be automatically downloaded from Google Drive on each run.

---

**Questions?** See `Docs/TROUBLESHOOTING.md` → "Google Drive OAuth Setup Issues"
