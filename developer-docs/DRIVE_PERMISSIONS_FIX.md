# Google Drive Permission Error - Fix Guide

**Error**: "Sorry, you do not have permission to share."  
**Service Account**: `project-ape-service@jasoande.iam.gserviceaccount.com`

---

## Why This Happens

Google Drive requires the **folder owner** to manually grant access to service accounts. The automated script cannot share the folder with itself due to Google's security model.

---

## Solution: Manual Folder Sharing

### Step 1: Open Google Drive

Go to: https://drive.google.com

### Step 2: Locate Your Folder

Find the folder:
- **Panasonic Avionics**
- URL: `https://drive.google.com/drive/folders/1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB`

### Step 3: Share the Folder

1. **Right-click** on the folder
2. Click **"Share"** or **"Manage access"**
3. In the "Add people and groups" field, paste:
   ```
   project-ape-service@jasoande.iam.gserviceaccount.com
   ```
4. Set permission level to: **"Viewer"**
5. **Uncheck** "Notify people" (service accounts don't need emails)
6. Click **"Share"** or **"Done"**

### Step 4: Verify Access

Run this verification script:

```bash
python3 << 'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load service account
credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)

# Build Drive API client
service = build('drive', 'v3', credentials=credentials)

# Test access to folder
folder_id = '1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB'

try:
    folder = service.files().get(fileId=folder_id, fields='id,name,permissions').execute()
    print(f"✅ SUCCESS: Can access folder '{folder.get('name')}'")
    print(f"   Folder ID: {folder.get('id')}")
    
    # Try to list files
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        pageSize=5,
        fields="files(id, name)"
    ).execute()
    
    files = results.get('files', [])
    print(f"   Files found: {len(files)}")
    
    if files:
        print("\n   Sample files:")
        for file in files[:3]:
            print(f"     - {file['name']}")
    
    print("\n🎉 Drive access is working correctly!")
    
except Exception as e:
    print(f"❌ ERROR: Cannot access folder")
    print(f"   {str(e)}")
    print("\n   Please ensure the folder is shared with the service account.")

EOF
```

---

## Alternative: Use Browser Authentication Instead

If you prefer not to use a service account, you can configure Project APE to use browser-based OAuth authentication:

### Option 1: Modify vars.py

Change the Drive configuration:

```python
DRIVE_CONFIG = {
    'enabled': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'auth_method': 'browser',  # Changed from 'service_account'
    'service_account_key': None,
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}
```

### Option 2: Update .env File

Add this line to your `.env` file:

```bash
DRIVE_AUTH_METHOD=browser
```

**Note**: Browser authentication will prompt you to log in with your Google account the first time. Your credentials will be cached.

---

## Troubleshooting

### Error: "File not found"

**Cause**: Service account still doesn't have access

**Fix**:
1. Verify the service account email is correct
2. Check that you shared the folder (not just individual files)
3. Wait 1-2 minutes for Google's permissions to propagate

### Error: "Invalid credentials"

**Cause**: Service account key file is missing or invalid

**Fix**:
```bash
# Verify key file exists
ls -lh service-account-key.json

# Check if it's valid JSON
python3 -m json.tool service-account-key.json > /dev/null && echo "✅ Valid JSON"
```

### Folder Shows "Shared" But Still Fails

**Cause**: Permission level might be wrong

**Fix**:
1. Go back to Drive sharing settings
2. Ensure permission is **"Viewer"** (not "Commenter" only)
3. Click "Advanced" to verify the service account is listed

---

## Quick Copy-Paste Commands

### Get Service Account Email

```bash
python3 -c "import json; print(json.load(open('service-account-key.json'))['client_email'])"
```

Output:
```
project-ape-service@jasoande.iam.gserviceaccount.com
```

### Get Folder ID from URL

If your folder URL is:
```
https://drive.google.com/drive/folders/1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB
```

The folder ID is:
```
1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB
```

---

## After Fixing Permissions

Once you've manually shared the folder, continue with setup:

```bash
# If setup.sh failed, you can skip Drive sharing step
# and manually verify instead:

# 1. Verify access (use script above)
python3 verify-drive-access.py

# 2. If verification passes, continue with launcher
./launch-project-ape.command
```

---

## For Multiple Clients

If you have multiple client folders, repeat the sharing process for each:

1. **Client 1**: Panasonic Avionics
   - Folder ID: `1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB`
   - Share with: `project-ape-service@jasoande.iam.gserviceaccount.com`
   - Permission: Viewer

2. **Client 2**: [Your next client]
   - Folder ID: [from vars.py]
   - Share with: `project-ape-service@jasoande.iam.gserviceaccount.com`
   - Permission: Viewer

---

## Best Practices

### For Production Use

1. **Domain-Wide Delegation** (if using Google Workspace):
   - Allows service account to access all domain files
   - Requires admin privileges
   - More complex setup but no manual sharing needed

2. **Shared Drive** (Google Workspace feature):
   - Create a Shared Drive for all client folders
   - Add service account to Shared Drive once
   - All folders inherit permissions automatically

3. **Browser Authentication**:
   - Simpler for personal use
   - No service account setup needed
   - Works immediately with your own files

### Security Notes

- ✅ Service account has **Viewer** access only (read-only)
- ✅ Cannot modify or delete files
- ✅ Cannot share with others
- ✅ Credentials are local to your machine

---

## Summary

**Quick Fix**:
1. Go to https://drive.google.com
2. Find folder: Panasonic Avionics
3. Share → Add: `project-ape-service@jasoande.iam.gserviceaccount.com`
4. Permission: Viewer
5. Uncheck "Notify people"
6. Click "Share"

**Verify**:
```bash
# Run verification script above
# Should see: ✅ SUCCESS: Can access folder
```

**Continue**:
```bash
# Once verified, proceed with setup
./launch-project-ape.command
```

---

**Need Help?**

If you continue to have issues:
1. Check service account email is correct
2. Ensure you're the owner of the Drive folder
3. Wait 1-2 minutes after sharing (permissions propagate)
4. Try the verification script to confirm access

This is a one-time setup step. Once configured, the service account will have permanent access to the folder.
