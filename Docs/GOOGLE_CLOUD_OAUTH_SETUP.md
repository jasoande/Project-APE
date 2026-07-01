# Google Cloud OAuth Setup Guide

<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE" width="150"/>
  
  **Complete Step-by-Step Guide for Google Drive OAuth Configuration**
</div>

---

## Overview

This guide walks you through setting up OAuth 2.0 credentials in Google Cloud Console to enable Project APE to access your Google Drive files.

**Time Required:** 10-15 minutes  
**Prerequisites:** Google account

---

## Part 1: Create Google Cloud Project

### Step 1: Navigate to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account

### Step 2: Create New Project

Click **"New Project"** in the top navigation or project selector.

#### Project Configuration

**Project name:** Enter a descriptive name
```
ape-demo-3
```
*Or use your own name (e.g., "project-ape-prod", "my-company-ape")*

**Project ID:** Auto-generated, cannot be changed later
```
ape-demo-3
```
*Note: Project IDs must be globally unique across all Google Cloud*

**Parent resource:** Select organization/folder
```
📁 Default Projects
```

**Important:** 
- ✅ **Default Projects** is the standard parent for personal/small team projects
- ✅ You can select a different folder if your organization requires it
- ✅ If you don't see "Default Projects", just leave it as "No organization"

**Location:** This determines:
- Billing account association
- IAM permissions inheritance
- Resource organization

**Common Options:**
- `No organization` - Personal Google account (most common)
- `Default Projects` - Google Workspace account
- `Your Company Name` - Enterprise organization

Click **"Create"** and wait 10-30 seconds for project creation.

---

## Part 2: Configure OAuth Consent Screen

### Step 1: Navigate to OAuth Consent Screen

1. In Google Cloud Console, select your new project
2. Navigate to: **APIs & Services → OAuth consent screen**
3. URL: `console.cloud.google.com/apis/credentials/consent`

### Step 2: Choose User Type

**Select:** `External`

**Why External?**
- ✅ Works with any Google account
- ✅ No Google Workspace requirement  
- ✅ Best for personal/small team use

Click **"Create"**

### Step 3: App Information

The OAuth consent screen is what users see when granting permissions.

#### **Required Fields:**

**App name:**
```
ape-demo-3
```
*Use your project name for consistency*

**User support email:**
```
jasoande@redhat.com
```
*Your email address - users contact you with questions*

**App logo:** (Optional)
- Upload Project APE logo if desired
- Recommended size: 120x120 pixels
- Not required for testing

#### **App Domain** (Optional - can skip)

These fields are optional for internal/testing use:

- **Application home page:** Leave blank
- **Application privacy policy:** Leave blank  
- **Application terms of service:** Leave blank

#### **Authorized domains** (Optional)

Leave blank for local development.

*Only needed if deploying to a web server*

#### **Developer Contact Information**

**Email addresses:** (Required)
```
jasoande@redhat.com
```
*These emails are for Google to notify you about changes to your project*

**Purpose:** Google uses these to contact you about:
- OAuth verification status changes
- Policy violations
- Security alerts

**Important:** All email addresses entered here receive notifications from Google about this OAuth application.

Click **"Save and Continue"**

### Step 4: Scopes

**For Project APE:** Click **"Add or Remove Scopes"**

**Required Scope:**
```
https://www.googleapis.com/auth/drive.readonly
```

**What this grants:**
- ✅ Read-only access to Google Drive files
- ✅ Download PDFs and documents
- ❌ Cannot modify, delete, or upload files
- ❌ Cannot access other Google services

**To add:**
1. Click "Add or Remove Scopes"
2. Filter by: `/auth/drive.readonly`
3. Check the box
4. Click "Update"
5. Click "Save and Continue"

### Step 5: Test Users (Optional)

**For External apps in testing mode:**
- Add email addresses of users who can test
- Limit: 100 test users
- **For personal use:** Add your own email

```
jasoande@redhat.com
```

Click **"Save and Continue"**

### Step 6: Review and Confirm

Review your settings:
- ✅ App name correct
- ✅ Support email correct
- ✅ Drive readonly scope added
- ✅ Test users added (if needed)

Click **"Back to Dashboard"**

---

## Part 3: Create OAuth Client ID

### Step 1: Navigate to Credentials

1. In Google Cloud Console: **APIs & Services → Credentials**
2. URL: `console.cloud.google.com/apis/credentials`

### Step 2: Create OAuth Client ID

Click **"+ Create Credentials" → "OAuth client ID"**

### Step 3: Configure Client ID

#### **Application type:**

**Select:** `Desktop app`

**Why Desktop app?**
- ✅ Designed for applications running on user's machine
- ✅ Supports local OAuth flow (localhost redirect)
- ✅ Works with Project APE's authentication method

**Other types (DO NOT use):**
- ❌ Web application - Requires public domain/URL
- ❌ Android/iOS - Mobile apps only
- ❌ Chrome extension - Browser extensions only
- ❌ TV and Limited Input - IoT devices only

#### **Name:**

```
ape-demo-3
```
*Use your project name or "Project APE Client"*

**Purpose:** This name appears in:
- OAuth consent screen
- Your Google Cloud Console credentials list
- Google Account security settings (user's view)

**Best practices:**
- Use descriptive names: "Project APE - Production"
- Include environment if you have multiple: "Project APE - Dev"
- Keep it recognizable for users

Click **"Create"**

### Step 4: Download Credentials

**Important:** A dialog appears immediately with your credentials.

**DO NOT CLOSE THIS DIALOG YET**

#### **What you see:**

- **Client ID:** `123456789-abcdefg.apps.googleusercontent.com`
- **Client Secret:** `GOCSPX-xxxxxxxxxxxx`

#### **Action Required:**

1. Click **"Download JSON"**  
2. File downloads as: `client_secret_123456789-abcdefg.apps.googleusercontent.com.json`
3. **Save this file** - you'll need it in Step 5
4. Click **"OK"** to close dialog

**Security Note:**
- 🔒 Keep this file secure (contains client secret)
- 🔒 Never commit to git repositories
- 🔒 Never share publicly

---

## Part 4: Enable Google Drive API

### Step 1: Navigate to API Library

1. In Google Cloud Console: **APIs & Services → Library**
2. URL: `console.cloud.google.com/apis/library`

### Step 2: Search for Drive API

1. Search: `Google Drive API`
2. Click on **"Google Drive API"**
3. Click **"Enable"**

**Wait time:** 10-30 seconds for API to activate

**Status:** You'll see "API enabled" confirmation

---

## Part 5: Upload Credentials to Project APE

### Step 1: Launch Project APE

```bash
python3 launch-project-ape.py
```

Browser opens to: `http://localhost:8765/configure`

### Step 2: Navigate to Google Drive Setup

Click the **"🔑 Google Drive Setup"** tab

### Step 3: Follow Setup Wizard

**Step 1: Project Creation** ✅ (Already done above)

**Step 2: Enable Drive API** ✅ (Already done above)

**Step 3: Upload Credentials**

1. Click **"Choose File"** or **"Upload OAuth Credentials"**
2. Select the downloaded JSON file:
   ```
   client_secret_123456789-abcdefg.apps.googleusercontent.com.json
   ```
3. Click **"Upload"**

**Success message:**
```
✅ Credentials uploaded successfully
Client ID: 123456789-abcde...
```

**Step 4: Authenticate with Google**

1. Click **"🔐 Authenticate with Google Drive"** button
2. Browser window opens automatically
3. Select your Google account
4. Click **"Continue"** on OAuth consent screen
5. Review permissions: `See and download all your Google Drive files`
6. Click **"Continue"**

**Success page:**
```
✅ Authentication successful! You can close this window and return to Project APE.
```

**Step 5: Verification**

Dashboard shows:
- ✅ OAuth Credentials: Uploaded
- ✅ Authentication Token: Valid
- ✅ Drive Access: Connected

---

## Troubleshooting

### Issue: "OAuth flow connection failed"

**Cause:** Fresh installation, `.project-ape` directory doesn't exist yet

**Solution:**
```bash
mkdir -p ~/.project-ape
chmod 700 ~/.project-ape
```

Then retry setup in dashboard.

---

### Issue: "Invalid OAuth credentials format"

**Symptoms:**
- Upload fails
- Error: "Expected 'installed' key"

**Cause:** Wrong credential type downloaded

**Solution:**
1. Return to Google Cloud Console → Credentials
2. Delete existing OAuth client
3. Create new OAuth client
4. **Select "Desktop app"** (not Web application)
5. Download new JSON file
6. Retry upload

**Verify JSON structure:**
```json
{
  "installed": {
    "client_id": "...",
    "project_id": "...",
    "auth_uri": "...",
    "token_uri": "...",
    ...
  }
}
```

---

### Issue: "This app isn't verified"

**Cause:** OAuth consent screen in "Testing" mode

**Solutions:**

**Option 1: Continue anyway (Recommended for personal use)**
1. Click **"Advanced"**
2. Click **"Go to [App Name] (unsafe)"**
3. Grant permissions

**Option 2: Publish app**
1. Go to OAuth consent screen
2. Click **"Publish App"**
3. Note: Takes 1-2 weeks for Google verification

**For personal/internal use:** Option 1 is perfectly safe.

---

### Issue: "Access blocked: This app's request is invalid"

**Cause:** Authorized redirect URIs mismatch

**Solution:**
- Ensure you selected **"Desktop app"** (not Web application)
- Desktop apps don't require redirect URI configuration
- If you accidentally created Web app, delete and recreate as Desktop app

---

### Issue: Browser doesn't open automatically

**Symptoms:**
- Click "Authenticate" button
- No browser window appears

**Solutions:**

**Check 1: Allow popups**
```
Browser Settings → Site Settings → Popups
Allow popups from localhost:8765
```

**Check 2: Firewall**
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/local/bin/python3
```

**Manual fallback:**
1. Watch terminal/console output
2. Copy the authorization URL shown
3. Paste into browser manually

---

### Issue: "Port already in use"

**Error:** `Address already in use` or `Port 8080 in use`

**Cause:** OAuth flow tries to bind localhost port, but it's occupied

**Solution:**
```bash
# Check what's using port 8080-8090
lsof -i :8080
lsof -i :8081
lsof -i :8082

# Kill processes if safe to do so
kill -9 <PID>
```

---

## Security Best Practices

### Credential Storage

**Location:**
```
~/.project-ape/drive_credentials.json  # OAuth client config
~/.project-ape/drive_token.json        # Access token (auto-generated)
```

**Permissions:**
```bash
chmod 600 ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_token.json
```

### What Gets Stored?

**drive_credentials.json:**
- Client ID (public)
- Client secret (private - keep secure)
- OAuth endpoints

**drive_token.json:**
- Access token (expires in 1 hour)
- Refresh token (long-lived)
- Scopes granted

**Security:**
- ✅ Stored locally only
- ✅ Not transmitted except to Google OAuth
- ✅ Refresh tokens auto-rotate
- ❌ Never commit to git (in .gitignore)

### Revoking Access

**To revoke Project APE access:**

1. Go to [Google Account Security](https://myaccount.google.com/permissions)
2. Find your app (e.g., "ape-demo-3")
3. Click **"Remove Access"**

**Result:**
- Existing tokens immediately invalidated
- Project APE can no longer access Drive
- Must re-authenticate to restore access

---

## Field Reference Quick Guide

### OAuth Consent Screen

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| **App name** | ✅ Yes | Displayed to users during auth | `ape-demo-3` |
| **User support email** | ✅ Yes | Users contact you here | `your@email.com` |
| **App logo** | ❌ No | Visual branding | 120x120 PNG |
| **Authorized domains** | ❌ No | Website domain (skip for local) | (blank) |
| **Developer email** | ✅ Yes | Google contacts you here | `your@email.com` |

### OAuth Client ID

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| **Application type** | ✅ Yes | Must be "Desktop app" | `Desktop app` |
| **Name** | ✅ Yes | Internal identifier | `ape-demo-3` |

### Parent Resource

| Option | Use Case |
|--------|----------|
| **No organization** | Personal Google account |
| **Default Projects** | Google Workspace (standard folder) |
| **Custom folder** | Enterprise with folder structure |

---

## Summary Checklist

Before starting Project APE, verify:

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured (External, with email)
- [ ] Drive API enabled
- [ ] OAuth client ID created (Desktop app type)
- [ ] Credentials JSON downloaded
- [ ] Credentials uploaded to Project APE dashboard
- [ ] OAuth flow completed successfully  
- [ ] Dashboard shows "Drive Access: Connected"

**Time investment:** 10-15 minutes (one-time setup)  
**Result:** Lifetime Drive access for Project APE

---

<div align="center">

**Questions? Issues?**

[View Troubleshooting Guide](TROUBLESHOOTING.md) | [Back to Main Documentation](../README.md)

</div>
