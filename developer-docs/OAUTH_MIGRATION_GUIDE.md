# OAuth Migration Guide
## Upgrading to OAuth 2.0-Only Authentication (v4.0.0+)

---

## What Changed and Why

**Starting with Project APE v4.0.0, Google Drive authentication has been simplified:**

- **Service Account authentication has been completely removed**
- **OAuth 2.0 is now the only authentication method**
- **Parallel execution race conditions have been fixed**

### Why This Change?

**Problems with Service Accounts:**
- ❌ Required manual folder sharing for every client
- ❌ Complex Google Cloud setup (IAM, key file management)
- ❌ Security concerns with key file distribution
- ❌ Difficult troubleshooting for non-technical users
- ❌ Required billing account for GCP project

**Benefits of OAuth-Only:**
- ✅ No manual folder sharing needed
- ✅ Automatic access to all your Drive files
- ✅ One-time browser authentication
- ✅ Simpler setup (5-10 minutes vs 30+ minutes)
- ✅ No service account key files to manage
- ✅ No billing account required for GCP project
- ✅ Better security (credentials auto-refresh, no static keys)

---

## Who Needs to Migrate?

### Check Your Current Setup

Run this command to see your authentication method:

```bash
cd /path/to/Project-APE-dev

# Check if you have service account files
ls -la service-account-key.json 2>/dev/null && echo "🔴 SERVICE ACCOUNT DETECTED" || echo "✅ No service account"

# Check vars.py configuration
grep -E "auth_method|service_account" vars.py 2>/dev/null || echo "No auth config found"
```

**You need to migrate if any of these are true:**
- 🔴 You have `service-account-key.json` file
- 🔴 Your `vars.py` contains `auth_method: 'service_account'`
- 🔴 You manually share Drive folders with a service account email
- 🔴 You're running Project APE v3.x or earlier

---

## Migration Paths

### Path A: Fresh OAuth Setup (Recommended for Most Users)

**Best for:**
- Users comfortable with a clean slate
- Users who want the simplest migration
- Users who had issues with service accounts

**Time Required:** 10-15 minutes

[Jump to Path A Instructions ↓](#path-a-fresh-oauth-setup)

---

### Path B: Re-run Setup Wizard

**Best for:**
- Users who partially completed OAuth setup
- Users with expired OAuth tokens
- Users who want guided setup

**Time Required:** 5-10 minutes

[Jump to Path B Instructions ↓](#path-b-re-run-setup-wizard)

---

### Path C: Manual OAuth Configuration

**Best for:**
- Advanced users
- Users who already have OAuth credentials from another project
- Users troubleshooting specific issues

**Time Required:** 15-20 minutes

[Jump to Path C Instructions ↓](#path-c-manual-oauth-configuration)

---

### Path D: Already Have OAuth (Update Only)

**Best for:**
- Users who already set up OAuth in v3.x
- Users who only need to update code

**Time Required:** 2-5 minutes

[Jump to Path D Instructions ↓](#path-d-already-have-oauth)

---

## Comparison: Old vs New Setup

| Feature | Service Account (OLD) | OAuth 2.0 (NEW) |
|---------|----------------------|-----------------|
| **Setup Time** | 30-40 minutes | 5-10 minutes |
| **Manual Folder Sharing** | Required (every client) | Not needed |
| **GCP Billing Account** | Required | Not required |
| **Browser Authentication** | No | Yes (one-time) |
| **Credential Management** | Manual key file | Auto-refresh token |
| **Security** | Static key file | Rotating OAuth tokens |
| **Multi-Client Support** | Complex (share each folder) | Simple (automatic) |
| **Troubleshooting** | Difficult | Easy |
| **Race Condition Fix** | Not applicable | ✅ Fixed in v4.0.1 |

---

## Migration Instructions

### Path A: Fresh OAuth Setup

**This is the recommended path for most users.**

#### Step 1: Backup Current Setup

```bash
cd /path/to/Project-APE-dev

# Backup service account credentials (just in case)
if [ -f service-account-key.json ]; then
    cp service-account-key.json service-account-key.json.backup
    echo "✅ Service account backed up"
fi

# Backup vars.py
cp vars.py vars.py.backup
echo "✅ Configuration backed up"
```

#### Step 2: Remove Old Service Account Setup

```bash
# Remove service account key file (no longer used)
rm -f service-account-key.json

# Remove old OAuth credentials if they exist (we'll create fresh ones)
rm -rf ~/.project-ape/

echo "✅ Old credentials removed"
```

#### Step 3: Pull Latest Code

```bash
# Get the latest version with OAuth-only support
git fetch origin
git checkout production
git pull origin production

# Verify version
grep "Current Version" CLAUDE.md
# Should show v4.0.0 or higher
```

#### Step 4: Run OAuth Setup Wizard

```bash
# Run the automated OAuth setup
python3 setup-oauth-drive.py
```

**The wizard will guide you through:**

1. **Google Cloud Authentication**
   - Opens browser
   - Sign in with your Google account
   - Click "Allow"

2. **OAuth Credential Creation**
   - Opens Google Cloud Console
   - Follow on-screen instructions:
     - Click "Create Credentials" → "OAuth client ID"
     - Application type: "Desktop app"
     - Name: "Project APE Desktop"
     - Click "Create" and download JSON
   - Wizard auto-detects downloaded file and moves it

3. **Drive Authentication**
   - Opens browser for OAuth flow
   - Sign in with Google
   - You may see "Google hasn't verified this app" warning
     - This is normal! Click "Advanced" → "Go to Project APE (unsafe)"
   - Click "Allow" to grant Drive access
   - Done!

#### Step 5: Update vars.py

Open `vars.py` and verify/update the Drive configuration:

```python
DRIVE_CONFIG = {
    'enabled': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'auth_method': 'oauth',  # ← Should be 'oauth' (not 'service_account')
    # Remove these lines if present:
    # 'service_account_key': 'service-account-key.json',
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}
```

**Important:** Remove any `service_account_key` entries from your config.

#### Step 6: Verify Setup

```bash
# Check credentials were created
ls -la ~/.project-ape/
# Should show:
# drwx------  drive_credentials.json
# drwx------  drive_token.json

# Test Drive access
python3 -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('$HOME/.project-ape/drive_token.json')
service = build('drive', 'v3', credentials=creds)
results = service.files().list(pageSize=5).execute()
print('✅ Successfully accessed Drive!')
print(f'Found {len(results.get(\"files\", []))} files')
"
```

#### Step 7: Launch Project APE

```bash
# Test with fast mode first
./launch_ape.sh fast

# Monitor at: http://localhost:8765
```

**✅ Migration complete!**

---

### Path B: Re-run Setup Wizard

**Best if you already attempted OAuth setup but encountered issues.**

#### Step 1: Clean Existing OAuth Credentials

```bash
cd /path/to/Project-APE-dev

# Remove old OAuth credentials
rm -rf ~/.project-ape/

echo "✅ Old OAuth credentials cleared"
```

#### Step 2: Pull Latest Code

```bash
git fetch origin
git checkout production
git pull origin production
```

#### Step 3: Run Setup Script

```bash
# This will run the complete setup process
./setup.sh
```

**The unified setup script will:**
- Install dependencies (Podman, Python, NotebookLM CLI)
- Authenticate with Google Cloud
- Guide you through OAuth credential creation
- Authenticate with NotebookLM
- Configure container credentials

**When prompted for authentication method:**
- Choose **Option 1: OAuth (Browser)** ✅

#### Step 4: Verify and Launch

```bash
# Check OAuth credentials exist
ls -la ~/.project-ape/drive_token.json

# Launch
./launch_ape.sh fast
```

---

### Path C: Manual OAuth Configuration

**For advanced users who want full control.**

#### Step 1: Create GCP Project (if needed)

```bash
# Authenticate with Google Cloud
gcloud auth login

# Create project
gcloud projects create project-ape-drive --name="Project APE Drive Access"

# Set as active project
gcloud config set project project-ape-drive

# Enable Drive API
gcloud services enable drive.googleapis.com
```

#### Step 2: Configure OAuth Consent Screen

```bash
# This requires manual steps in Cloud Console
open "https://console.cloud.google.com/apis/credentials/consent"
```

**In the browser:**
1. User Type: **External**
2. Click "Create"
3. App name: `Project APE`
4. User support email: `<your-email>`
5. Developer contact: `<your-email>`
6. Click "Save and Continue"
7. Scopes: Click "Add or Remove Scopes"
   - Search for: `https://www.googleapis.com/auth/drive.readonly`
   - Select it
   - Click "Update"
8. Test users: Click "+ ADD USERS"
   - Add your email address
   - Click "Save"
9. Click "Save and Continue" through remaining screens

#### Step 3: Create OAuth Client ID

```bash
open "https://console.cloud.google.com/apis/credentials"
```

**In the browser:**
1. Click "Create Credentials" → "OAuth client ID"
2. Application type: **Desktop app**
3. Name: `Project APE Desktop`
4. Click "Create"
5. Click "Download JSON"
6. Save to Downloads folder

#### Step 4: Move Credentials to Correct Location

```bash
# Create directory
mkdir -p ~/.project-ape

# Move downloaded credentials
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json

# Secure permissions
chmod 600 ~/.project-ape/drive_credentials.json

echo "✅ Credentials configured"
```

#### Step 5: Run Authentication Script

```bash
cd /path/to/Project-APE-dev

# Run OAuth authentication
python3 setup-oauth-drive.py
```

This will open a browser to complete the OAuth flow.

#### Step 6: Update vars.py

```python
DRIVE_CONFIG = {
    'enabled': True,
    'auth_method': 'oauth',
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}
```

Remove any `service_account_key` references.

---

### Path D: Already Have OAuth

**If you already set up OAuth in v3.x, just update your code.**

#### Step 1: Verify OAuth Credentials Exist

```bash
ls -la ~/.project-ape/
# Should show:
# drive_credentials.json
# drive_token.json
```

If missing, follow [Path A](#path-a-fresh-oauth-setup) instead.

#### Step 2: Pull Latest Code

```bash
cd /path/to/Project-APE-dev

git fetch origin
git checkout production
git pull origin production
```

#### Step 3: Update vars.py

Remove service account references:

```python
DRIVE_CONFIG = {
    'enabled': True,
    'auth_method': 'oauth',  # ← Verify this is 'oauth'
    # Remove this line if present:
    # 'service_account_key': 'service-account-key.json',
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}
```

#### Step 4: Test

```bash
# Quick verification
python3 -c "
from google.oauth2.credentials import Credentials
creds = Credentials.from_authorized_user_file('$HOME/.project-ape/drive_token.json')
print('✅ OAuth credentials valid')
"

# Launch
./launch_ape.sh fast
```

**✅ Migration complete!**

---

## Verification Checklist

After migration, verify everything is working:

### 1. Check Files Exist

```bash
ls -la ~/.project-ape/

# Should show:
# drwx------ 2 you you 64 Jun 30 14:00 .
# drwx------ 20 you you 640 Jun 30 14:00 ..
# -rw------- 1 you you 425 Jun 30 14:00 drive_credentials.json
# -rw------- 1 you you 342 Jun 30 14:00 drive_token.json
```

**✅ Pass:** Both files exist with `600` permissions  
**❌ Fail:** Run `python3 setup-oauth-drive.py` again

### 2. Test Drive API Access

```bash
python3 << 'EOF'
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    creds = Credentials.from_authorized_user_file('~/.project-ape/drive_token.json'.replace('~', str(Path.home())))
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=5).execute()
    files = results.get('files', [])
    print(f'✅ SUCCESS: Found {len(files)} Drive files')
    if files:
        print('Sample files:')
        for f in files[:3]:
            print(f"  - {f['name']}")
except Exception as e:
    print(f'❌ ERROR: {e}')
EOF
```

**✅ Pass:** Shows "SUCCESS" message  
**❌ Fail:** Check [Troubleshooting](#troubleshooting) section

### 3. Verify vars.py Configuration

```bash
grep -A 10 "DRIVE_CONFIG" vars.py | grep "auth_method"

# Should show:
#     'auth_method': 'oauth',
```

**✅ Pass:** Shows `'oauth'`  
**❌ Fail:** Edit `vars.py` and change to `'oauth'`

### 4. Check for Service Account Remnants

```bash
# These should NOT exist anymore
ls service-account-key.json 2>/dev/null && echo "❌ Found old service account file" || echo "✅ No service account files"

grep -r "service_account" vars.py && echo "❌ Found service account references" || echo "✅ No service account references"
```

**✅ Pass:** No service account files or references  
**❌ Fail:** Remove them manually

### 5. Test Single Client Run

```bash
# Run with one client to verify everything works
./launch_ape.sh fast

# Check logs
tail -f logs/*.log

# Check dashboard
open http://localhost:8765
```

**✅ Pass:** Pipeline completes without Drive auth errors  
**❌ Fail:** Check [Troubleshooting](#troubleshooting) section

### 6. Test Multi-Client Parallel Run (v4.0.1+)

```bash
# Edit vars.py to include 2-3 clients
# Run in parallel
./launch_ape.sh fast

# Monitor for OAuth race conditions
grep -i "oauth\|credential" logs/*.log
```

**✅ Pass:** All clients authenticate successfully  
**❌ Fail:** Update to v4.0.1+ (race condition fix)

---

## Rollback Instructions

**If something goes wrong and you need to revert:**

### Option 1: Rollback Code Only

```bash
cd /path/to/Project-APE-dev

# Restore previous version
git log --oneline -10  # Find commit before v4.0.0
git checkout <commit-hash>

# Restore vars.py backup
cp vars.py.backup vars.py

# Restore service account key
cp service-account-key.json.backup service-account-key.json

# Launch with old version
./launch_ape.sh fast
```

### Option 2: Complete Rollback with Old Service Account

```bash
# Checkout last stable v3.x version
git checkout v3.0.4

# Restore backups
cp vars.py.backup vars.py
cp service-account-key.json.backup service-account-key.json

# Verify service account is configured
grep "service_account" vars.py

# Manually share Drive folders (if needed)
# Follow: developer-docs/DRIVE_PERMISSIONS_FIX.md

# Launch
./launch_ape.sh fast
```

### Option 3: Fresh Install of v3.x

```bash
# Clone fresh v3.x version to different directory
cd /tmp
git clone https://github.com/yourusername/Project-APE-dev.git Project-APE-v3
cd Project-APE-v3
git checkout v3.0.4

# Copy your old configuration
cp /path/to/Project-APE-dev/vars.py.backup ./vars.py
cp /path/to/Project-APE-dev/service-account-key.json.backup ./service-account-key.json

# Run old setup
./setup.sh
```

**Note:** Rollback means you'll continue using service accounts. You'll need to:
- Manually share Drive folders for each client
- Manage service account key files
- Accept longer setup times

**We recommend fixing the OAuth issue instead of rolling back.**

---

## Troubleshooting

### Issue: "OAuth client secrets not found"

**Symptom:**
```
❌ OAuth client secrets not found
You need to create OAuth credentials first
```

**Solution:**

You skipped credential creation. Run:

```bash
python3 setup-oauth-drive.py
```

Follow the prompts to create and download OAuth credentials.

---

### Issue: "Google hasn't verified this app"

**Symptom:**
Browser shows scary warning during OAuth flow.

**This is completely normal and expected!**

**Solution:**

1. Click **"Advanced"** (bottom left of warning)
2. Click **"Go to Project APE (unsafe)"**
3. Click **"Allow"**

**Why:** Your OAuth app is in "Testing" mode. Google requires verification for public apps, but since you're the only user, this is safe.

---

### Issue: "Token has expired"

**Symptom:**
```
❌ ERROR: Token has been expired or revoked
```

**Solution:**

Tokens auto-refresh when used, but if unused for 7+ days:

```bash
# Re-authenticate (keeps credentials, just gets new token)
python3 setup-oauth-drive.py
```

This takes ~1 minute.

---

### Issue: "OAuth race condition - only some clients authenticate"

**Symptom:**
- 6 clients launched in parallel
- 1-2 succeed, others fail with OAuth errors
- Logs show: `Client secrets must be for web or installed app`

**This was fixed in v4.0.1**

**Solution:**

```bash
# Update to latest version
git fetch origin
git checkout production
git pull origin production

# Verify version
grep "Current Version" CLAUDE.md
# Should show v4.0.1 or higher
```

**What was fixed:**
- OAuth authentication now happens AFTER process stagger
- Each client authenticates sequentially with proper spacing
- No more OAuth callback port collisions

---

### Issue: "redirect_uri_mismatch"

**Symptom:**
```
❌ Error: redirect_uri_mismatch
```

**Cause:** You created a "Web application" OAuth client instead of "Desktop app"

**Solution:**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth client
3. Delete it
4. Create new one:
   - Type: **Desktop app** (not Web app)
   - Name: `Project APE Desktop`
5. Download JSON
6. Move to `~/.project-ape/drive_credentials.json`
7. Run `python3 setup-oauth-drive.py` again

---

### Issue: "Access blocked: Project APE has not completed Google verification"

**Symptom:**
OAuth flow shows "Access blocked" error

**Solution:**

Add yourself as a test user:

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to **"Test users"**
3. Click **"+ ADD USERS"**
4. Enter your email address
5. Click **"Save"**
6. Run `python3 setup-oauth-drive.py` again

---

### Issue: "Drive API has not been enabled"

**Symptom:**
```
❌ Drive API has not been used in project before or it is disabled
```

**Solution:**

```bash
# Enable Drive API
gcloud services enable drive.googleapis.com

# Verify
gcloud services list --enabled | grep drive
```

---

### Issue: "gcloud not found"

**Symptom:**
```
bash: gcloud: command not found
```

**Solution:**

Install Google Cloud SDK:

```bash
./setup-environment.sh
```

This installs gcloud, Python, Podman, and other dependencies.

---

### Issue: "Cannot find downloaded credentials file"

**Symptom:**
Setup wizard can't find your downloaded OAuth JSON file.

**Solution:**

Manually move it:

```bash
# Find the file in Downloads
ls ~/Downloads/client_secret_*.json

# Move to correct location
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json

# Set permissions
chmod 600 ~/.project-ape/drive_credentials.json

# Run setup again
python3 setup-oauth-drive.py
```

The wizard will detect existing credentials and skip to authentication.

---

### Issue: "vars.py still references service_account"

**Symptom:**
Pipeline tries to use service account authentication.

**Solution:**

Edit `vars.py` and remove/update these lines:

```python
# REMOVE these lines:
'auth_method': 'service_account',
'service_account_key': 'service-account-key.json',

# ENSURE this line exists:
'auth_method': 'oauth',
```

---

## FAQ

### Q: Can I use both OAuth and service accounts?

**A:** No. As of v4.0.0, service account support has been completely removed. OAuth is the only authentication method.

If you absolutely need service accounts (e.g., for automation), you must use v3.x or earlier.

---

### Q: Will my old service account key still work?

**A:** No. The code that supported service accounts has been removed. The key file won't be used even if present.

---

### Q: Do I need to manually share Drive folders anymore?

**A:** No! That's the beauty of OAuth. You automatically have access to all files in your Google Drive. No sharing needed.

---

### Q: What happens to my existing notebooks in NotebookLM?

**A:** Nothing changes. Your NotebookLM notebooks are unaffected. OAuth only changes how Project APE accesses Google Drive to download source PDFs.

---

### Q: Can I migrate without losing my configuration?

**A:** Yes! Migration only affects authentication. Your `vars.py` client configurations, prompts, and other settings remain unchanged.

Just backup `vars.py` before migration, then update the `DRIVE_CONFIG` section.

---

### Q: How long does OAuth token last?

**A:** OAuth tokens auto-refresh when used. If unused for 7+ days, you may need to re-authenticate (takes ~1 minute).

The token file is at `~/.project-ape/drive_token.json`.

---

### Q: Can I run Project APE on a headless server with OAuth?

**A:** Yes, but you need to complete OAuth authentication on a machine with a browser first, then copy the token file:

```bash
# On machine with browser:
python3 setup-oauth-drive.py

# Copy to server:
scp ~/.project-ape/drive_token.json user@server:~/.project-ape/
scp ~/.project-ape/drive_credentials.json user@server:~/.project-ape/
```

---

### Q: What if I have multiple Google accounts?

**A:** You'll authenticate with one account during OAuth setup. To switch accounts:

```bash
# Remove existing token
rm ~/.project-ape/drive_token.json

# Re-authenticate with different account
python3 setup-oauth-drive.py
# When browser opens, sign in with the other account
```

---

### Q: Can I revoke Project APE's access to my Drive?

**A:** Yes. Go to: https://myaccount.google.com/permissions

Find "Project APE" and click "Remove Access".

To restore access, run `python3 setup-oauth-drive.py` again.

---

### Q: Is OAuth more secure than service accounts?

**A:** Yes, for this use case:
- OAuth tokens auto-rotate and expire
- No static key files to protect
- Revocable from Google account settings
- Scoped to read-only Drive access

Service accounts were designed for server-to-server automation, not user applications.

---

### Q: What if migration fails halfway through?

**A:** Migration is safe to retry. You can run `python3 setup-oauth-drive.py` multiple times.

If you're stuck:
1. Delete `~/.project-ape/` directory
2. Run `python3 setup-oauth-drive.py` from scratch
3. Follow prompts carefully

If still failing, see [Troubleshooting](#troubleshooting) or [Rollback](#rollback-instructions).

---

### Q: Will my team members need to migrate individually?

**A:** Yes. Each user must authenticate with their own Google account. OAuth credentials are per-user.

**For team deployments**, each team member should:
1. Pull latest code
2. Run `python3 setup-oauth-drive.py`
3. Authenticate with their Google account

---

### Q: Can I automate OAuth authentication for CI/CD?

**A:** OAuth requires browser interaction, so it's not ideal for fully automated CI/CD.

For automation, consider:
- **Option 1:** Run authentication manually once, then copy token to CI environment (token expires after 7+ days unused)
- **Option 2:** Use v3.x with service accounts for CI/CD only
- **Option 3:** Pre-download all Drive files and commit to repo (if files are small)

Most users run Project APE interactively, not in CI/CD.

---

## Getting Help

If you're still having trouble after following this guide:

### 1. Check Logs

```bash
cd /path/to/Project-APE-dev

# Overall logs
tail -f logs/overall.log

# Client-specific logs
tail -f logs/<client-name>.log

# Search for errors
grep -i "error\|fail\|oauth" logs/*.log
```

### 2. Verify Setup

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check dependencies
python3 -c "from google_auth_oauthlib.flow import InstalledAppFlow; print('✅ OAuth libraries installed')"

# Check gcloud
gcloud --version

# Check project
gcloud config get-value project
```

### 3. Create GitHub Issue

Open an issue at: https://github.com/yourusername/Project-APE-dev/issues

**Include:**
- Migration path you attempted (A, B, C, or D)
- Error messages (full text)
- Output from setup script
- OS and Python version
- Whether you had service accounts or OAuth before

**Example issue title:**
```
Migration Issue: OAuth authentication fails on macOS with redirect_uri_mismatch
```

---

## Success Stories

**Help us improve this guide!**

If you successfully migrated, please share:
- Which migration path did you use?
- How long did it take?
- Any issues you encountered?
- Suggestions for improving this guide

Create a GitHub Discussion or comment on the migration issue.

---

## Summary

**Quick Migration Steps:**

1. **Backup:** `cp vars.py vars.py.backup`
2. **Update code:** `git pull origin production`
3. **Run OAuth setup:** `python3 setup-oauth-drive.py`
4. **Update vars.py:** Set `'auth_method': 'oauth'`
5. **Remove service account references** from vars.py
6. **Test:** `./launch_ape.sh fast`

**Total Time:** 10-15 minutes

**Benefits:**
- ✅ No more manual folder sharing
- ✅ Simpler authentication
- ✅ Better security
- ✅ Parallel execution race condition fixed (v4.0.1+)
- ✅ Faster setup for new users

---

**Version:** 4.0.1  
**Last Updated:** June 30, 2026  
**Applies to:** Project APE v4.0.0 and higher  
**Migration Status:** Production Ready
