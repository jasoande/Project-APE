# Complete OAuth Setup Guide for Project APE
**From zero to working OAuth in 30 minutes - No prior Google Cloud experience required**

---

## Table of Contents

- [Quick Start for Experienced Users](#quick-start-for-experienced-users)
- [Complete Beginner's Guide](#complete-beginners-guide)
  - [Prerequisites](#prerequisites)
  - [Part 1: Create Google Cloud Project](#part-1-create-google-cloud-project-5-minutes)
  - [Part 2: Enable Required APIs](#part-2-enable-required-apis-3-minutes)
  - [Part 3: Configure API Quotas](#part-3-configure-api-quotas-2-minutes)
  - [Part 4: Set Up OAuth Consent Screen](#part-4-set-up-oauth-consent-screen-5-minutes)
  - [Part 5: Create OAuth Credentials](#part-5-create-oauth-credentials-3-minutes)
  - [Part 6: Install Credentials Locally](#part-6-install-credentials-locally-2-minutes)
  - [Part 7: Authenticate with Google](#part-7-authenticate-with-google-3-minutes)
  - [Part 8: Verify Setup](#part-8-verify-setup-2-minutes)
- [Troubleshooting](#troubleshooting)
- [Understanding OAuth vs Service Account](#understanding-oauth-vs-service-account)

---

## Quick Start for Experienced Users

If you're already familiar with Google Cloud Platform, here's the fast track:

```bash
# 1. Create GCP project and enable Drive API
gcloud projects create project-ape-$(date +%s) --name="Project APE"
gcloud config set project PROJECT_ID
gcloud services enable drive.googleapis.com

# 2. Create OAuth credentials
# → Go to console.cloud.google.com/apis/credentials
# → Create OAuth client ID → Desktop app
# → Download JSON

# 3. Install credentials
mkdir -p ~/.project-ape
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json

# 4. Authenticate
python3 setup-oauth-drive.py

# 5. Done! Launch Project APE
./launch-project-ape.command
```

**For detailed step-by-step instructions, continue reading below.**

---

## Complete Beginner's Guide

### Prerequisites

Before starting, ensure you have:

- **Google Account**: Any Gmail or Google Workspace account
  - Sign up at: https://accounts.google.com/signup if needed
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge
  - JavaScript must be enabled
  - Cookies must be enabled
- **Project APE Installed**: You should have already cloned the repository
  - If not, run: `git clone https://github.com/yourusername/project-ape.git`

**Estimated Total Time**: 25-30 minutes (first time)

---

## Part 1: Create Google Cloud Project (5 minutes)

A Google Cloud Project is a container that holds your API credentials and usage data. Think of it like creating a new app registration.

### Step 1.1: Open Google Cloud Console

1. Open your web browser
2. Navigate to: **https://console.cloud.google.com**
3. Sign in with your Google account
4. Accept the Terms of Service if prompted

**What you'll see**: A dashboard with menu icon (☰) in top-left corner

### Step 1.2: Create a New Project

1. Click the **project dropdown** at the top of the page
   - It says "Select a project" or shows your current project name
   - Located next to the Google Cloud logo

2. In the popup window, click **"NEW PROJECT"** (top-right)

3. Fill in the project details:
   ```
   Project name: Project APE NotebookLM
   Organization: (leave as "No organization" - this is fine for personal use)
   Location: (leave as "No organization")
   ```

4. Click **"CREATE"** button

5. **Wait 30-60 seconds** - A notification will appear when ready
   - You'll see a spinner while the project is being created
   - Don't close the browser window

**Troubleshooting**:
- If you see "You don't have permission to create projects": Your organization has restrictions. Contact your Google Workspace admin or use a personal Gmail account instead.

### Step 1.3: Select Your New Project

1. Click the **project dropdown** again (top of page)
2. Find and click **"Project APE NotebookLM"** from the list
3. Verify the project name appears in the top bar

✅ **Success Indicator**: The project name "Project APE NotebookLM" appears in the blue header bar

---

## Part 2: Enable Required APIs (3 minutes)

Google Cloud requires you to explicitly enable APIs before using them. This is like turning on features.

### Step 2.1: Navigate to API Library

**Method 1 (Using Menu)**:
1. Click the **hamburger menu** (☰) in top-left
2. Hover over **"APIs & Services"**
3. Click **"Library"**

**Method 2 (Direct Link)**:
1. Click this link: https://console.cloud.google.com/apis/library
2. Ensure "Project APE NotebookLM" is selected in the project dropdown

### Step 2.2: Enable Google Drive API

1. In the search box at the top, type: **`Google Drive API`**

2. Click on the **"Google Drive API"** card
   - It has a triangular Drive icon
   - Published by Google

3. Click the blue **"ENABLE"** button

4. **Wait 10-15 seconds** for the API to enable
   - You'll see a loading spinner
   - Page will refresh when complete

5. You'll see **"API enabled"** status at the top

**What this does**: Allows your OAuth credentials to access Google Drive files

### Step 2.3: Verify API is Enabled

1. Click **"APIs & Services"** → **"Enabled APIs & Services"** from menu
2. You should see:
   ```
   ✓ Google Drive API
   ✓ Cloud Resource Manager API (auto-enabled)
   ```

✅ **Success Indicator**: "Google Drive API" appears in the enabled APIs list

---

## Part 3: Configure API Quotas (2 minutes)

Google provides default quotas for API usage. For Project APE, the default quotas are typically sufficient, but it's good to understand them.

### Step 3.1: View Current Quotas

1. Navigate to: **APIs & Services** → **"Enabled APIs & services"**
2. Click **"Google Drive API"**
3. Click the **"Quotas & System Limits"** tab

### Step 3.2: Understanding Default Quotas

You'll see default limits like:

| Quota | Default Limit | Project APE Usage |
|-------|---------------|-------------------|
| **Queries per day** | 1,000,000,000 | ~100-1,000 per run |
| **Queries per 100 seconds per user** | 1,000 | ~50-100 per run |
| **Queries per 100 seconds** | 20,000 | ~50-100 per run |

**For typical Project APE usage** (processing 1-10 clients):
- ✅ Default quotas are MORE than sufficient
- ✅ No changes needed
- ✅ You can process hundreds of clients per day

### Step 3.3: Request Quota Increase (Optional - Only if Needed)

**You typically DON'T need this**, but if you plan to:
- Process 50+ clients simultaneously
- Run the pipeline hundreds of times per day
- Download thousands of files per client

Then you can request increases:

1. On the Quotas page, find the quota to increase
2. Check the box next to it
3. Click **"EDIT QUOTAS"** at the top
4. Fill out the request form:
   - Why you need the increase
   - How much you need (2x-10x current limit)
5. Click **"SUBMIT REQUEST"**
6. **Wait 1-2 business days** for Google to review

**Pro Tip**: Start with default quotas. Only request increases if you actually hit limits.

✅ **Success Indicator**: You can see the quotas page and understand the limits

---

## Part 4: Set Up OAuth Consent Screen (5 minutes)

The OAuth Consent Screen is what users see when they authorize your app. Even though you're the only user, Google requires this configuration.

### Step 4.1: Navigate to OAuth Consent Screen

1. Click **hamburger menu (☰)** → **"APIs & Services"** → **"OAuth consent screen"**

**Or use direct link**: https://console.cloud.google.com/apis/credentials/consent

### Step 4.2: Choose User Type

You'll see two options:

**Internal** (Only for Google Workspace organizations)
- Only available if you're using a Workspace account
- Restricts access to your organization

**External** (For everyone else)
- ✅ **Choose this one** for personal Gmail accounts
- Allows you to add specific test users

1. Select **"External"**
2. Click **"CREATE"**

### Step 4.3: Configure App Information (Screen 1 of 4)

Fill in the required fields:

**App name**:
```
Project APE
```

**User support email**:
```
your-email@gmail.com  (select from dropdown)
```

**App logo** (optional):
```
Skip this - not required
```

**Application home page** (optional):
```
Skip this - not required
```

**Application privacy policy link** (optional):
```
Skip this - not required
```

**Application terms of service link** (optional):
```
Skip this - not required
```

**Authorized domains** (optional):
```
Skip this - not required
```

**Developer contact information**:
```
your-email@gmail.com
```

**Action**: Click **"SAVE AND CONTINUE"**

### Step 4.4: Configure Scopes (Screen 2 of 4)

Scopes define what permissions your app requests.

1. Click **"ADD OR REMOVE SCOPES"**

2. In the "Filter" box, type: **`drive`**

3. **Find and check the box** for:
   ```
   https://www.googleapis.com/auth/drive.readonly
   
   Description: "See and download all your Google Drive files"
   Restricted: No
   ```

4. Click **"UPDATE"** (bottom of the panel)

5. Verify the scope appears in the table:
   ```
   Your sensitive scopes
   Scope: .../auth/drive.readonly
   ```

6. Click **"SAVE AND CONTINUE"**

**⚠️ Important**: Make sure you select `drive.readonly` (read-only), not just `drive.metadata` or `drive.file`. Project APE needs to download files.

### Step 4.5: Add Test Users (Screen 3 of 4)

Since your app is in "External" testing mode, you must explicitly add yourself as a test user.

1. Click **"+ ADD USERS"**

2. Enter your email address:
   ```
   your-email@gmail.com
   ```

3. Click **"ADD"**

4. Verify your email appears in the "Test users" list

5. Click **"SAVE AND CONTINUE"**

**Why this matters**: Without adding yourself as a test user, you'll get an "Access blocked" error when trying to authenticate.

### Step 4.6: Review Summary (Screen 4 of 4)

1. Review all your settings:
   - App name: Project APE
   - User support email: your-email@gmail.com
   - Scopes: .../auth/drive.readonly
   - Test users: your-email@gmail.com

2. Click **"BACK TO DASHBOARD"**

✅ **Success Indicator**: You're back on the OAuth consent screen dashboard, and it shows "External" publishing status

---

## Part 5: Create OAuth Credentials (3 minutes)

Now you'll create the actual OAuth client ID that Project APE will use.

### Step 5.1: Navigate to Credentials

1. Click **hamburger menu (☰)** → **"APIs & Services"** → **"Credentials"**

**Or use direct link**: https://console.cloud.google.com/apis/credentials

### Step 5.2: Create OAuth Client ID

1. Click the blue **"+ CREATE CREDENTIALS"** button (top of page)

2. Select **"OAuth client ID"** from the dropdown

**If prompted to configure consent screen**: You already did this in Part 4, so you shouldn't see this. If you do, click "Configure Consent Screen" and complete Part 4.

### Step 5.3: Configure Application Type

You'll see "Create OAuth client ID" form:

**Application type**:
```
Desktop app  ← Select this option
```

**⚠️ Critical**: Must be "Desktop app", NOT "Web application"
- Web application won't work with the setup script
- Desktop app enables the local redirect flow

**Name**:
```
Project APE Desktop Client
```

Click **"CREATE"**

### Step 5.4: Download Credentials

A popup appears: **"OAuth client created"**

You'll see:
```
Your Client ID
your-client-id-xyz.apps.googleusercontent.com

Your Client Secret
GOCSPX-abc123xyz...
```

**Action**:
1. Click the **"DOWNLOAD JSON"** button
2. The file downloads to your Downloads folder
3. Click **"OK"** to close the popup

**File name will be something like**:
```
client_secret_123456789-abc.apps.googleusercontent.com.json
```

**⚠️ Important**: Don't lose this file! Keep it safe. You'll move it in the next step.

✅ **Success Indicator**: JSON file is in your Downloads folder

---

## Part 6: Install Credentials Locally (2 minutes)

Now move the downloaded credentials to where Project APE expects them.

### Step 6.1: Create Credentials Directory

Open your terminal (Mac: Terminal app, Linux: Terminal, Windows: WSL or Git Bash)

```bash
mkdir -p ~/.project-ape
```

This creates a hidden folder in your home directory.

### Step 6.2: Move Credentials File

**macOS / Linux**:
```bash
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

**Windows (WSL)**:
```bash
mv /mnt/c/Users/YourWindowsUsername/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

**Windows (Git Bash)**:
```bash
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

### Step 6.3: Verify File Location

```bash
ls -lh ~/.project-ape/drive_credentials.json
```

**Expected output**:
```
-rw-r--r-- 1 yourname staff 451 Jun 25 10:30 /Users/yourname/.project-ape/drive_credentials.json
```

### Step 6.4: Secure File Permissions (Recommended)

```bash
chmod 600 ~/.project-ape/drive_credentials.json
```

This ensures only you can read the credentials file.

**Verify**:
```bash
ls -lh ~/.project-ape/drive_credentials.json
```

Should now show:
```
-rw------- 1 yourname staff 451 Jun 25 10:30 /Users/yourname/.project-ape/drive_credentials.json
```

✅ **Success Indicator**: File exists at `~/.project-ape/drive_credentials.json` with 600 permissions

---

## Part 7: Authenticate with Google (3 minutes)

Now run Project APE's setup script to complete the OAuth flow.

### Step 7.1: Navigate to Project APE Directory

```bash
cd /path/to/project-ape
```

Example:
```bash
cd ~/Documents/project-ape
# or wherever you cloned the repository
```

### Step 7.2: Run OAuth Setup Script

```bash
python3 setup-oauth-drive.py
```

### Step 7.3: Follow Browser Authentication

**Expected output**:
```
======================================================================
  Google Drive OAuth Setup
======================================================================

This will authenticate Project APE to access your Google Drive files
using your personal Google account (no service account needed).

✅ Found OAuth client secrets: /Users/yourname/.project-ape/drive_credentials.json

Starting OAuth flow...

🌐 Your browser will open shortly.
   1. Sign in with your Google account
   2. Click 'Allow' to grant access
   3. Return to this terminal when done
```

**Your browser will automatically open** and show the Google sign-in page.

### Step 7.4: Complete Google Authentication

**Screen 1: Sign In**
```
Choose your Google account
→ Click on: your-email@gmail.com
```

**Screen 2: Warning (First Time Only)**
```
"Google hasn't verified this app"

This is NORMAL and SAFE - it's your own app!

→ Click: "Advanced" (bottom left)
→ Click: "Go to Project APE (unsafe)"
```

**Why you see this**: Your app is in "Testing" mode and hasn't been verified by Google. Since you're the developer and the only user, this is perfectly safe.

**Screen 3: Grant Permissions**
```
"Project APE wants to access your Google Account"

This app will be able to:
☑ See and download all your Google Drive files

→ Review the permission
→ Click: "Allow"
```

**Screen 4: Success**
```
"The authentication flow has completed."

✅ You can close this tab.
```

### Step 7.5: Return to Terminal

Back in your terminal, you should see:

```
======================================================================
✅ SUCCESS - OAuth Setup Complete!
======================================================================

Token saved to: /Users/yourname/.project-ape/drive_token.json

You can now access your Google Drive files without sharing!

Next steps:
  1. Ensure vars.py has: auth_method: 'oauth'
  2. Run: ./launch-project-ape.command
```

✅ **Success Indicator**: File `~/.project-ape/drive_token.json` now exists

---

## Part 8: Verify Setup (2 minutes)

Let's confirm everything is working correctly.

### Step 8.1: Check Token File Exists

```bash
ls -lh ~/.project-ape/
```

**Expected output**:
```
-rw------- 1 yourname staff 451 Jun 25 10:30 drive_credentials.json
-rw------- 1 yourname staff 890 Jun 25 10:35 drive_token.json
```

Both files should be present.

### Step 8.2: Test Drive Access (Optional)

If Project APE includes a verification script:

```bash
python3 verify-drive-access.py
```

**Expected output**:
```
Checking Google Drive access...
✅ Successfully authenticated with Google Drive
✅ Drive API is accessible

Testing folder access...
✅ All checks passed!
```

### Step 8.3: Verify vars.py Configuration

Ensure Project APE is configured to use OAuth:

```bash
grep -A 5 "DRIVE_CONFIG" vars.py
```

Should show:
```python
DRIVE_CONFIG = {
    'enabled': True,
    'auth_method': 'oauth',  # ← Should be 'oauth'
    ...
}
```

**If it says `'service_account'`**, edit vars.py:

```bash
# Open vars.py in your editor
nano vars.py
# or: code vars.py
# or: vim vars.py
```

Change:
```python
'auth_method': 'service_account',  # OLD
```

To:
```python
'auth_method': 'oauth',  # NEW
```

### Step 8.4: Launch Project APE

You're ready to go!

```bash
./launch-project-ape.command
```

Or if using Docker:
```bash
./launch_ape.sh fast
```

The dashboard should open at: **http://localhost:8765**

✅ **Success Indicator**: Dashboard loads and shows your configured clients

---

## Troubleshooting

### Error: "OAuth client secrets not found"

**Symptom**:
```
❌ OAuth client secrets not found
```

**Cause**: Credentials file not in the right place

**Solution**:
```bash
# Check if file exists
ls -lh ~/.project-ape/drive_credentials.json

# If missing, re-download from:
# https://console.cloud.google.com/apis/credentials
# Click the download icon (⬇️) next to your OAuth client ID

# Move to correct location
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

---

### Error: "Google hasn't verified this app"

**Symptom**: Browser shows warning about unverified app

**This is NORMAL and SAFE**

**Solution**:
```
1. Click "Advanced" (bottom left)
2. Click "Go to Project APE (unsafe)"
```

**Why this happens**: Your app is in "Testing" mode. Google requires a verification process to remove this warning, which takes 1-2 weeks and is unnecessary for personal use.

**To remove warning permanently** (optional):
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click "PUBLISH APP"
3. Follow Google's verification process (requires domain ownership, privacy policy, etc.)
4. **Not recommended for personal use** - the warning is harmless

---

### Error: "Access blocked: Project APE's request is invalid"

**Symptom**: Can't complete OAuth flow, get "Access blocked" error

**Cause 1**: Wrong OAuth scope configured

**Solution**:
```
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Click "EDIT APP"
3. Navigate to "Scopes" section
4. Verify this scope is added:
   https://www.googleapis.com/auth/drive.readonly
5. Click "SAVE AND CONTINUE"
6. Re-run: python3 setup-oauth-drive.py
```

**Cause 2**: Email not added as test user

**Solution**:
```
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to "Test users" section
3. Click "+ ADD USERS"
4. Add your Gmail address
5. Click "ADD"
6. Re-run: python3 setup-oauth-drive.py
```

---

### Error: "redirect_uri_mismatch"

**Symptom**:
```
Error 400: redirect_uri_mismatch
The redirect URI in the request, http://localhost:XXXXX/, does not match...
```

**Cause**: OAuth client type is "Web application" instead of "Desktop app"

**Solution**:
```
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID
3. Click the trash icon to delete it
4. Create new OAuth client ID:
   → Application type: "Desktop app"
   → Name: "Project APE Desktop Client"
5. Download new JSON file
6. Move to: ~/.project-ape/drive_credentials.json
7. Re-run: python3 setup-oauth-drive.py
```

---

### Error: "Token has expired or been revoked"

**Symptom**: OAuth worked before, now getting auth errors

**Cause**: Refresh token expired (after 7 days of inactivity) or you revoked access

**Solution**:
```bash
# Delete old token
rm ~/.project-ape/drive_token.json

# Re-authenticate
python3 setup-oauth-drive.py
```

**Prevention**: Use Project APE at least once per week, or the token will expire. It automatically refreshes when you use it.

---

### Error: "Google Drive API has not been used in project"

**Symptom**:
```
Google Drive API has not been used in project 123456789 before or it is disabled.
```

**Cause**: Drive API not enabled

**Solution**:
```
1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
2. Ensure correct project is selected (top dropdown)
3. Click "ENABLE"
4. Wait 15 seconds
5. Re-run: python3 setup-oauth-drive.py
```

**Alternative via command line**:
```bash
gcloud services enable drive.googleapis.com --project=PROJECT_ID
```

---

### Browser Doesn't Open Automatically

**Symptom**: Script says "browser will open" but nothing happens

**Solution**: Copy the URL manually

The script will print a URL like:
```
Please visit this URL to authorize this application:
https://accounts.google.com/o/oauth2/auth?client_id=...
```

Copy the entire URL and paste it into your browser.

---

### Error: "Permission denied" when accessing Drive folders

**Symptom**: OAuth succeeds, but can't access specific Drive folders

**Cause**: This is actually NOT possible with OAuth - if you authenticated, you have access to all your own Drive files.

**Likely actual cause**: 
- Folder URL is incorrect
- Folder was deleted
- Folder belongs to a different Google account

**Solution**:
```bash
# Verify you're using the correct Google account
# The account you authenticated with during OAuth setup

# Check folder URL format:
# Correct:
https://drive.google.com/drive/folders/ABC123XYZ456

# Incorrect:
https://drive.google.com/file/d/ABC123  (this is a file, not folder)
https://docs.google.com/...  (this is a specific doc, not folder)
```

---

### Error: "Invalid client" or "Client ID not found"

**Symptom**: 
```
Error: invalid_client
The OAuth client was not found.
```

**Cause**: Using credentials from wrong project, or client was deleted

**Solution**:
```bash
# Verify you're in the correct Google Cloud project
1. Go to: https://console.cloud.google.com
2. Check project name in top bar
3. Ensure it matches the project where you created OAuth client

# Re-create OAuth client ID
1. Go to: https://console.cloud.google.com/apis/credentials
2. Verify OAuth client exists
3. If missing, create new one (Part 5)
4. Download fresh credentials
5. Move to: ~/.project-ape/drive_credentials.json
```

---

## Understanding OAuth vs Service Account

Project APE supports two authentication methods. Here's when to use each:

### OAuth (Browser-based Authentication)

**How it works**:
1. You authenticate in browser with your Google account
2. Google issues a token to Project APE
3. Token grants access to all YOUR Drive files
4. No manual folder sharing needed

**Pros**:
- ✅ **Easiest setup** for personal use
- ✅ **No folder sharing required** - automatic access to your files
- ✅ **More secure** - uses your personal Google account
- ✅ **Better for development** - quick iteration

**Cons**:
- ❌ **Requires browser** - can't run completely headless
- ❌ **Token expires** - needs refresh every 7 days (automatic on first use)
- ❌ **Single user** - only works for the Google account that authenticated
- ❌ **Container challenges** - harder to pass credentials into containers

**Best for**:
- Personal use
- Development
- Small teams (each person authenticates separately)
- Interactive environments

**Setup time**: 25-30 minutes (first time)

---

### Service Account (Programmatic Authentication)

**How it works**:
1. You create a service account (like a robot user)
2. Service account gets a long-lived key file
3. You manually share Drive folders with the service account email
4. Service account can only access explicitly shared folders

**Pros**:
- ✅ **Fully automated** - no browser required
- ✅ **Long-lived credentials** - no expiration
- ✅ **Container-friendly** - just mount the key file
- ✅ **Headless servers** - works in CI/CD, cron jobs, etc.
- ✅ **Multi-user** - one service account, many team members

**Cons**:
- ❌ **Manual folder sharing** - must share each folder individually
- ❌ **"Permission denied" errors** - if you forget to share a folder
- ❌ **More setup steps** - service account creation + sharing
- ❌ **Harder to debug** - less clear error messages

**Best for**:
- Production deployments
- Automation pipelines
- Scheduled jobs (cron)
- Headless servers
- Large teams with many shared folders

**Setup time**: 15-20 minutes (plus folder sharing time)

---

### Comparison Table

| Feature | OAuth | Service Account |
|---------|-------|-----------------|
| **Setup Complexity** | Medium | Medium-High |
| **First-Time Setup** | 25-30 min | 15-20 min + sharing |
| **Folder Sharing Required** | ❌ No | ✅ Yes (every folder) |
| **Access to Your Files** | ✅ Automatic | ❌ Only if shared |
| **Access to Others' Files** | ❌ No (unless they share) | ✅ Yes (if shared) |
| **Browser Required** | ✅ Yes (once) | ❌ No |
| **Token Expiration** | 7 days (auto-refresh) | Never |
| **Container Support** | ⚠️ Limited | ✅ Full |
| **Headless Servers** | ❌ No | ✅ Yes |
| **Best For** | Personal use | Production |
| **Error Proneness** | Low | Medium (sharing errors) |
| **Security** | Very High | High |

---

### When to Switch

**Start with OAuth if**:
- You're new to Project APE
- You're using your own Drive folders
- You want to test quickly
- You're working on a laptop/desktop

**Switch to Service Account when**:
- You're deploying to production
- You need scheduled/automated runs
- You're running in containers
- Multiple team members need access
- You have a dedicated GCP organization

---

### How to Switch Between Methods

**From OAuth to Service Account**:

1. Create service account (see `developer-docs/SERVICE-ACCOUNT-SETUP.md`)
2. Share all Drive folders with service account email
3. Edit `vars.py`:
   ```python
   DRIVE_CONFIG = {
       'auth_method': 'service_account',  # Change from 'oauth'
       'service_account_key': 'service-account-key.json',
   }
   ```
4. Test with: `python3 verify-drive-access.py --service-account`

**From Service Account to OAuth**:

1. Complete Parts 1-7 of this guide
2. Edit `vars.py`:
   ```python
   DRIVE_CONFIG = {
       'auth_method': 'oauth',  # Change from 'service_account'
   }
   ```
3. Remove folder sharing (optional - doesn't hurt to leave it)

---

## Summary Checklist

After completing this guide, you should have:

- ✅ Google Cloud Project created ("Project APE NotebookLM")
- ✅ Google Drive API enabled
- ✅ Understanding of API quotas (defaults are fine)
- ✅ OAuth consent screen configured
- ✅ OAuth client ID created (Desktop app type)
- ✅ Credentials downloaded and moved to `~/.project-ape/drive_credentials.json`
- ✅ OAuth authentication completed (token at `~/.project-ape/drive_token.json`)
- ✅ vars.py configured with `auth_method: 'oauth'`
- ✅ Access verified (optional test script passed)
- ✅ Project APE successfully launched

---

## Next Steps

1. **Configure Your Clients**:
   ```bash
   # Open web configuration UI
   python3 dashboard/server.py
   # Navigate to: http://localhost:8765/configure
   ```

2. **Add Drive Folders**:
   - Use folders from YOUR Google Drive
   - No sharing needed - you already have access!

3. **Launch Your First Workflow**:
   ```bash
   ./launch-project-ape.command
   # or
   ./launch_ape.sh fast
   ```

4. **Monitor Progress**:
   - Dashboard: http://localhost:8765
   - Watch clients process in real-time
   - Click NotebookLM links when complete

---

## Additional Resources

- **Project APE Documentation**: `README.md`
- **Quick Start Guide**: `QUICK_START.md`
- **Troubleshooting**: `Docs/TROUBLESHOOTING.md`
- **Service Account Setup**: `developer-docs/SERVICE-ACCOUNT-SETUP.md`
- **Google OAuth Documentation**: https://developers.google.com/identity/protocols/oauth2
- **Google Drive API Reference**: https://developers.google.com/drive/api/v3/reference

---

## Getting Help

**If you're stuck**:

1. **Check logs**:
   ```bash
   tail -f logs/overall.log
   ```

2. **Search troubleshooting section above** (Ctrl+F / Cmd+F)

3. **Verify file locations**:
   ```bash
   ls -lh ~/.project-ape/
   # Should show both:
   # - drive_credentials.json
   # - drive_token.json
   ```

4. **Re-run verification**:
   ```bash
   python3 verify-drive-access.py
   ```

5. **Open GitHub Issue**:
   - Include error message
   - Include relevant log snippets
   - Include OS and Python version (`python3 --version`)

---

## Security Notes

**Protecting Your Credentials**:

```bash
# Set restrictive permissions
chmod 600 ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_token.json

# Never commit to git
# (Already in .gitignore, but double-check)
grep -E "credentials|token" .gitignore
```

**What to NEVER do**:
- ❌ Never commit credentials to git
- ❌ Never share credentials in screenshots
- ❌ Never post credentials in support tickets
- ❌ Never email credentials

**What's safe**:
- ✅ Storing credentials in `~/.project-ape/` (hidden directory)
- ✅ Using restrictive file permissions (600)
- ✅ Sharing the OAuth client ID (not the secret)
- ✅ Describing errors without including secrets

**If credentials are compromised**:
```bash
# Revoke access
# Go to: https://myaccount.google.com/permissions
# Find "Project APE"
# Click "Remove Access"

# Delete local credentials
rm ~/.project-ape/drive_credentials.json
rm ~/.project-ape/drive_token.json

# Create new OAuth client ID (repeat Part 5)
```

---

**Congratulations! You've successfully set up OAuth for Project APE. 🎉**

**Version**: 3.2.0  
**Last Updated**: June 25, 2026  
**Estimated Completion Time**: 25-30 minutes
