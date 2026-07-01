# Google OAuth Setup - Complete Guide

**Detailed instructions for setting up OAuth 2.0 credentials for Google Drive access**

## Why OAuth?

OAuth provides browser-based authentication using your personal Google account. Benefits:

✅ **No folder sharing required** - Access your own Drive files  
✅ **More secure** - Browser-based authentication flow  
✅ **Easier setup** - No service account management  
✅ **Perfect for development** - Quick iteration  

⚠️ **Note:** Tokens expire after 7 days of inactivity but auto-refresh on next use.

---

## Step-by-Step Guide

### Prerequisites

- Google account with access to:
  - Google Drive (drive.google.com)
  - Google Cloud Console (console.cloud.google.com)
  - Google NotebookLM (notebooklm.google.com)

---

### Part 1: Create Google Cloud Project (5 minutes)

#### 1.1 Open Google Cloud Console

Navigate to: **https://console.cloud.google.com**

#### 1.2 Create New Project

```
Click: "Select a project" dropdown (top left)
      → "New Project"

Project Name: "Project APE" (or any name you prefer)
Organization: (leave default)
Location: (leave default)

Click: "Create"
```

**Wait 30 seconds** for project creation to complete.

#### 1.3 Select Your Project

```
Click: "Select a project" dropdown
      → Choose "Project APE"
```

You should see "Project APE" in the top navigation bar.

---

### Part 2: Enable Google Drive API (2 minutes)

#### 2.1 Open API Library

```
Navigation menu (☰) → "APIs & Services" → "Library"

Or direct link:
https://console.cloud.google.com/apis/library
```

#### 2.2 Enable Drive API

```
Search bar: Type "Google Drive API"
Click: "Google Drive API" card
Click: "Enable" button
```

**Wait 10 seconds** for API to enable.

You should see "API enabled" status.

---

### Part 3: Configure OAuth Consent Screen (5 minutes)

#### 3.1 Open OAuth Consent Screen

```
Navigation menu (☰) → "APIs & Services" → "OAuth consent screen"

Or direct link:
https://console.cloud.google.com/apis/credentials/consent
```

#### 3.2 Configure Consent Screen

**User Type:**
```
Select: "External" (for personal use)
Click: "Create"
```

**App Information:**
```
App name: "Project APE Desktop"
User support email: your-email@gmail.com
Developer contact: your-email@gmail.com

Click: "Save and Continue"
```

**Scopes (Step 2):**
```
Click: "Add or Remove Scopes"
Filter: Type "drive"
Check: "https://www.googleapis.com/auth/drive.readonly"
       (Shows as ".../auth/drive.readonly")
Click: "Update"
Click: "Save and Continue"
```

**Test Users (Step 3):**
```
Click: "Add Users"
Enter: your-email@gmail.com
Click: "Add"
Click: "Save and Continue"
```

**Summary (Step 4):**
```
Review settings
Click: "Back to Dashboard"
```

---

### Part 4: Create OAuth Client ID (3 minutes)

#### 4.1 Open Credentials Page

```
Navigation menu (☰) → "APIs & Services" → "Credentials"

Or direct link:
https://console.cloud.google.com/apis/credentials
```

#### 4.2 Create Credentials

```
Click: "Create Credentials" (top)
      → "OAuth client ID"
```

#### 4.3 Configure Client

**Application type:**
```
Select: "Desktop app"
```

**Name:**
```
Enter: "Project APE Desktop Client"
```

```
Click: "Create"
```

#### 4.4 Download Credentials

A dialog appears: "OAuth client created"

```
Click: "Download JSON" button
```

**Important:** Save this file! It contains your client ID and secret.

The file will be named something like:
```
client_secret_123456789-abcdefg.apps.googleusercontent.com.json
```

```
Click: "OK" to close dialog
```

---

### Part 5: Install Credentials (2 minutes)

#### 5.1 Create Credentials Directory

Open terminal and run:

```bash
mkdir -p ~/.project-ape
```

This creates the credentials folder in your home directory.

#### 5.2 Move Downloaded File

**macOS:**
```bash
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

**Linux:**
```bash
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

**Windows (WSL):**
```bash
mv /mnt/c/Users/YourName/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
```

#### 5.3 Verify File Exists

```bash
ls -la ~/.project-ape/drive_credentials.json
```

You should see:
```
-rw-r--r-- 1 yourname staff 451 Jun 25 09:00 /Users/yourname/.project-ape/drive_credentials.json
```

---

### Part 6: Authenticate (3 minutes)

#### 6.1 Run OAuth Setup Script

```bash
cd /path/to/project-ape
python3 setup-oauth-drive.py
```

#### 6.2 Follow Browser Flow

The script will:

1. **Open browser automatically**
   - If browser doesn't open, copy the URL from terminal

2. **Google Sign-In**
   ```
   Sign in with: your-email@gmail.com
   (The account you added as test user)
   ```

3. **Warning Screen** (first time only)
   ```
   "Google hasn't verified this app"
   Click: "Advanced" (bottom left)
   Click: "Go to Project APE Desktop (unsafe)"
   
   This is safe - it's YOUR app!
   ```

4. **Permissions Screen**
   ```
   "Project APE Desktop wants to access your Google Account"
   
   Permissions requested:
   ✓ See and download all your Google Drive files
   
   Click: "Allow"
   ```

5. **Success Message**
   ```
   "The authentication flow has completed."
   You can close this tab.
   ```

#### 6.3 Verify Success

Terminal should show:
```
✅ Authentication successful!
✅ Token saved to: /Users/yourname/.project-ape/drive_token.json

You can now use Project APE to access your Google Drive files.
```

---

### Part 7: Test Access (2 minutes)

#### 7.1 Run Verification Script

```bash
python3 verify-drive-access.py
```

Expected output:
```
Checking Google Drive access...
✅ Successfully authenticated with Google Drive
✅ Drive API is accessible

Testing folder access...
Enter a Google Drive folder URL to test (or press Enter to skip): 

[Paste your folder URL or press Enter]

✅ All checks passed!
```

#### 7.2 Test with Real Folder

Get a Drive folder URL:
```
1. Open Google Drive: drive.google.com
2. Navigate to any folder
3. Copy URL from address bar
4. Paste into verification script
```

Should see:
```
✅ Folder accessible
✅ Found X files
```

---

## Troubleshooting

### Issue: "OAuth client secrets not found"

**Cause:** Credentials file not in correct location

**Fix:**
```bash
# Check if file exists
ls -la ~/.project-ape/drive_credentials.json

# If missing, repeat Part 5
# Make sure file is named exactly: drive_credentials.json
```

---

### Issue: "Google hasn't verified this app"

**This is normal!** You're seeing this because:
- Your app is in "Testing" mode
- You're the only authorized user
- It's perfectly safe to proceed

**Fix:**
```
Click: "Advanced"
Click: "Go to Project APE Desktop (unsafe)"
```

**To remove this warning (optional):**
```
1. Go to OAuth consent screen
2. Click "Publish App"
3. Go through verification process (takes 1-2 weeks)

Note: Not necessary for personal use
```

---

### Issue: "Access blocked: Project APE's request is invalid"

**Cause:** Scopes not configured correctly

**Fix:**
```
1. Go to OAuth consent screen
2. Edit app
3. Scopes section: Verify ".../auth/drive.readonly" is added
4. Save changes
5. Re-run: python3 setup-oauth-drive.py
```

---

### Issue: "Token has expired"

**Cause:** Token inactive for 7+ days

**Fix:**
```bash
# Simply re-run setup - it will auto-refresh
python3 setup-oauth-drive.py
```

Or manually refresh:
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pathlib import Path

token_file = Path.home() / '.project-ape' / 'drive_token.json'
creds = Credentials.from_authorized_user_file(str(token_file))

if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    token_file.write_text(creds.to_json())
    print("✅ Token refreshed")
```

---

### Issue: "Invalid grant" error

**Cause:** Refresh token revoked

**Fix:**
```bash
# Delete old token
rm ~/.project-ape/drive_token.json

# Re-authenticate
python3 setup-oauth-drive.py
```

---

## Security Best Practices

### Protect Your Credentials

```bash
# Set proper file permissions
chmod 600 ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_token.json

# Verify permissions
ls -la ~/.project-ape/
# Should show: -rw------- (readable only by you)
```

### Never Commit Credentials

Add to `.gitignore`:
```
# Already included in project .gitignore
.project-ape/
drive_credentials.json
drive_token.json
service-account-key.json
```

### Rotate Credentials Regularly

For production use:
```
1. Create new OAuth client ID (every 90 days)
2. Download new credentials
3. Update drive_credentials.json
4. Re-authenticate
```

---

## OAuth vs Service Account Comparison

| Feature | OAuth | Service Account |
|---------|-------|-----------------|
| **Setup Time** | 5-10 minutes | 10-15 minutes |
| **Folder Sharing** | Not required | Required per folder |
| **Authentication** | Browser-based | Programmatic |
| **Token Lifetime** | 7 days (auto-refresh) | Long-lived |
| **Best For** | Personal, Development | Production, Automation |
| **Container Support** | Limited | Full support |
| **Headless Servers** | No | Yes |

---

## Advanced Configuration

### Use Custom Scopes

For additional permissions, modify `setup-oauth-drive.py`:

```python
# Read/Write access
SCOPES = [
    'https://www.googleapis.com/auth/drive',  # Full access
]

# Or specific scopes:
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',  # Read only
    'https://www.googleapis.com/auth/drive.metadata.readonly',  # Metadata
]
```

### Use Different Credentials Directory

```bash
export PROJECT_APE_CREDS_DIR="/custom/path"
python3 setup-oauth-drive.py
```

### Multiple Google Accounts

```bash
# Account 1
python3 setup-oauth-drive.py --profile personal
# Creates: ~/.project-ape/drive_token_personal.json

# Account 2
python3 setup-oauth-drive.py --profile work
# Creates: ~/.project-ape/drive_token_work.json

# Switch accounts in vars.py:
DRIVE_CONFIG = {
    'token_file': '~/.project-ape/drive_token_work.json',
}
```

---

## Verification Checklist

- [ ] Google Cloud project created
- [ ] Drive API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth client ID created
- [ ] Credentials downloaded
- [ ] File moved to `~/.project-ape/drive_credentials.json`
- [ ] Authentication completed (browser flow)
- [ ] Token file exists: `~/.project-ape/drive_token.json`
- [ ] Verification script passed
- [ ] Test folder accessible

---

## Next Steps

1. **Configure Project APE:**
   ```bash
   python3 dashboard/server.py
   # Open: http://localhost:8765/configure
   ```

2. **Add client folders:**
   - Use Drive folder URLs from your Google Drive
   - No sharing required - you already have access!

3. **Launch workflow:**
   ```bash
   ./launch_ape.sh fast
   ```

---

## Resources

- **Google Cloud Console**: https://console.cloud.google.com
- **OAuth 2.0 Documentation**: https://developers.google.com/identity/protocols/oauth2
- **Drive API Reference**: https://developers.google.com/drive/api/v3/reference
- **Project APE Docs**: See `README.md` and `Docs/`

---

**Need Help?**
- Check `Docs/TROUBLESHOOTING.md`
- Open GitHub issue with error details
- Include: screenshot of error, terminal output

---

**Version**: 3.2.0  
**Last Updated**: June 25, 2026  
**Estimated Time**: 20-25 minutes (first time)
