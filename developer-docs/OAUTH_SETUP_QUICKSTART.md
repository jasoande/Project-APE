# OAuth Setup - Quick Start Guide
## Zero to working OAuth in 10 minutes

This guide gets you up and running with Google Drive access for Project APE with **zero prior Google Cloud experience required**.

---

## Prerequisites

- ✅ Google account (Gmail or Workspace)
- ✅ Project APE installed
- ✅ Internet connection

**That's it!** No billing account, no GCP experience needed.

---

## Quick Setup (10 minutes)

### 1. Run the automated setup script

```bash
cd /path/to/Project-APE-dev
python3 setup-oauth-drive-improved.py
```

### 2. Follow the wizard

The script will:

1. **Check your Google Cloud authentication** 
   - Opens browser if needed
   - Sign in with your Google account

2. **Set up a GCP project**
   - Asks if you want to create new or use existing
   - **Recommended**: Create new project called "Project APE Drive Access"
   - If creation fails (billing required), script offers to use existing project

3. **Enable Google Drive API**
   - Done automatically
   - Takes ~10 seconds

4. **Guide you to create OAuth credentials**
   - Opens browser to Google Cloud Console
   - Shows step-by-step instructions
   - You'll download a JSON file to Downloads folder
   - Script auto-detects and moves it to correct location

5. **Authenticate with Google**
   - Opens browser for OAuth flow
   - Sign in with Google
   - Click "Advanced" → "Go to Project APE (unsafe)" (this is normal!)
   - Click "Allow"
   - Done!

### 3. Verify it worked

You should see:

```
======================================================================
  ✅ SUCCESS - OAuth Setup Complete!
======================================================================

✅ Token saved to: /Users/you/.project-ape/drive_token.json
✅ Credentials at: /Users/you/.project-ape/drive_credentials.json
✅ Both files secured with chmod 600

You can now access your Google Drive files without manual folder sharing!
```

### 4. Update vars.py

Open `vars.py` and ensure:

```python
DRIVE_CONFIG = {
    'enabled': True,
    'auth_method': 'oauth',  # ← Make sure this says 'oauth'
    ...
}
```

### 5. Launch Project APE

```bash
./launch_ape.sh fast
```

**You're done!** 🎉

---

## Common Issues

### "You need to enable billing"

**Symptom**: Project creation fails with billing error

**Solution**: Use an existing project instead

The script will automatically offer this option. Just select one of your existing projects when prompted.

---

### "Google hasn't verified this app"

**Symptom**: Browser shows scary warning

**This is completely normal and safe!**

**Solution**: 
1. Click "Advanced" (bottom left)
2. Click "Go to Project APE (unsafe)"

**Why this happens**: Your app is in "Testing" mode. Google requires verification for public apps, but since you're the only user, this warning is expected and harmless.

---

### "Access blocked"

**Symptom**: OAuth flow fails with "Access blocked" error

**Solution**: Add yourself as a test user

The automated script should handle this, but if it doesn't:

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to "Test users"
3. Click "+ ADD USERS"
4. Add your email address
5. Run the script again

---

### "OAuth client created but can't find JSON file"

**Symptom**: You downloaded credentials but script can't find them

**Solution**: Manually move the file

```bash
mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
chmod 600 ~/.project-ape/drive_credentials.json
```

Then run the script again - it will detect the existing credentials and skip to authentication.

---

## What Gets Created

After successful setup:

```
~/.project-ape/
├── drive_credentials.json  (OAuth client secrets - keep safe!)
└── drive_token.json        (Your access token - auto-refreshes)
```

**Security**: Both files have `chmod 600` permissions (only you can read them).

---

## How It Works

**Old way (manual)**:
1. Read 1150-line documentation
2. Manually create GCP project
3. Manually enable APIs
4. Manually configure consent screen
5. Manually create OAuth client
6. Manually download and move files
7. Run authentication script

**New way (automated)**:
1. Run one script
2. Answer a few prompts
3. Click through OAuth flow
4. Done!

**Time saved**: 20+ minutes → 5-10 minutes

---

## Troubleshooting

### Script hangs at "Opening browser..."

**Press Ctrl+C and check**:
- Is Chrome/Firefox/Safari running?
- Try closing all browser windows and running again

### "gcloud not found"

**Solution**: Install Google Cloud SDK first

```bash
./setup-environment.sh
```

This installs gcloud, Python, and other dependencies.

### Token expires

**Symptom**: "Token has expired" error after 7+ days

**Solution**: Tokens auto-refresh when you use them, but if unused for 7+ days:

```bash
rm ~/.project-ape/drive_token.json
python3 setup-oauth-drive-improved.py
```

This re-runs just the authentication step (fast - 1 minute).

---

## Advanced: Switching Between Auth Methods

### From Service Account to OAuth

```bash
# Run OAuth setup
python3 setup-oauth-drive-improved.py

# Update vars.py
# Change: 'auth_method': 'service_account'
# To:     'auth_method': 'oauth'
```

### From OAuth to Service Account

See: `developer-docs/SERVICE-ACCOUNT-SETUP.md`

---

## Getting Help

**If you're stuck after following this guide:**

1. Check the error message carefully
2. Search the "Common Issues" section above
3. Check logs: `tail -f logs/overall.log`
4. Open GitHub issue with:
   - Error message
   - Output from script
   - OS and Python version (`python3 --version`)

---

## Next Steps

After OAuth setup:

1. **Configure clients**: `python3 dashboard/server.py` → http://localhost:8765/configure
2. **Add Drive folders**: Use folders from YOUR Google Drive (no sharing needed!)
3. **Launch workflow**: `./launch_ape.sh fast`
4. **Monitor**: http://localhost:8765

---

## Security Notes

**Your credentials are safe:**

- ✅ Stored in hidden directory (`~/.project-ape/`)
- ✅ Protected with `chmod 600` (only you can read)
- ✅ Never committed to git (in `.gitignore`)
- ✅ OAuth tokens auto-refresh (you don't see them)

**Never do this:**

- ❌ Share credentials in screenshots
- ❌ Commit credentials to git
- ❌ Email credentials
- ❌ Post credentials in support tickets

---

## Summary

| Step | Time | What Happens |
|------|------|--------------|
| 1. Run script | 1 min | Checks dependencies |
| 2. Authenticate gcloud | 1 min | One-time browser login |
| 3. Create/select project | 1 min | GCP project setup |
| 4. Enable API | 30 sec | Auto-enabled |
| 5. Create OAuth credentials | 3 min | Browser-guided setup |
| 6. Authenticate OAuth | 1 min | Final browser login |
| **Total** | **5-10 min** | **Ready to run!** |

---

**Version**: 4.0.2  
**Last Updated**: June 30, 2026  
**Tested On**: macOS, RHEL 9, Ubuntu 22.04
