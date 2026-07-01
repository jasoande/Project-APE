# OAuth Wizard Testing Guide

**Created:** 2026-06-25  
**Status:** Ready for Testing  
**Feature:** Browser-based Google Drive OAuth Setup Wizard

---

## Overview

The OAuth Wizard eliminates the last terminal dependency in Project APE by providing a complete 5-step web-based interface for Google Drive authentication setup.

**Key Achievement:** Users can now complete OAuth configuration entirely through the browser without opening a terminal.

---

## What Was Implemented

### Backend (dashboard/server.py)

Four new API endpoints added:

1. **GET `/api/oauth-status`**
   - Checks if OAuth credentials and token exist
   - Returns authentication status
   - Response includes: credentials_exist, token_exist, authenticated

2. **POST `/api/upload-oauth-credentials`**
   - Accepts client_secret JSON file upload
   - Validates JSON structure
   - Saves to `~/.project-ape/drive_credentials.json`
   - Sets secure permissions (0600)

3. **POST `/api/start-oauth-flow`**
   - Triggers OAuth authentication flow
   - Opens browser automatically for user consent
   - Streams progress via Server-Sent Events (SSE)
   - Saves token to `~/.project-ape/drive_token.json`

4. **GET `/api/test-drive-access`**
   - Verifies Drive API access with saved credentials
   - Lists sample accessible files
   - Refreshes expired tokens automatically

### Frontend (dashboard/templates/configure.html)

New "Google Drive Setup" tab with complete 5-step wizard:

**Step 1: Check Prerequisites**
- Displays current OAuth status
- Shows credentials, token, and access status
- Auto-checks on load

**Step 2: Create Credentials**
- Instructions with direct GCP Console links
- Interactive checklist to track progress
- Links to:
  - Project creation
  - API enablement
  - OAuth consent screen
  - Client ID creation

**Step 3: Upload Credentials**
- Drag-and-drop file upload zone
- Accepts `client_secret_*.json` files
- Validates JSON structure
- Shows upload success confirmation

**Step 4: Authenticate**
- Single-click OAuth flow trigger
- Real-time progress updates via SSE
- Browser auto-opens for consent
- Status messages guide user through process

**Step 5: Verify Access**
- Tests Drive API access
- Shows sample accessible files
- Confirms setup completion
- Returns to configuration page

### JavaScript (dashboard/static/oauth-wizard.js)

Complete wizard logic:
- State management and navigation
- File upload with drag-drop support
- EventSource for SSE streaming
- API integration for all endpoints
- Error handling and recovery
- Status checking and updates

### CSS Styling

Professional wizard UI matching Project APE design:
- Progress indicator with step tracking
- Responsive layout
- Smooth animations
- Clear visual feedback
- Error and success states

---

## Testing Instructions

### Prerequisites

1. Stop any running dashboard instances:
   ```bash
   pkill -f "dashboard/server.py"
   ```

2. Start the dashboard:
   ```bash
   cd /Users/jasona/test/Project-APE-dev
   python3 dashboard/server.py
   ```

3. Open browser: `http://localhost:8765/configure`

### Test Scenario 1: Fresh OAuth Setup (Primary Test)

**Goal:** Complete OAuth setup from scratch without terminal

**Steps:**

1. **Navigate to OAuth Tab**
   - Click "🔑 Google Drive Setup" tab
   - Verify wizard displays with 5 steps
   - Verify Step 1 is active
   - Verify progress indicator shows step 1

2. **Check Status (Step 1)**
   - Observe status badges:
     - OAuth Credentials: ❌ Not Configured
     - Authentication Token: ❌ Not Configured
     - Drive Access: ❌ Not Configured
   - Click "Next →"

3. **Create Credentials (Step 2)**
   - Review instructions
   - Click external links (verify they open in new tab):
     - "Open GCP Console →"
     - "Enable API →"
     - "Configure →"
     - "Create →"
   - Follow GCP Console steps to create OAuth credentials
   - Download `client_secret_*.json` file
   - Click "Next →"

4. **Upload Credentials (Step 3)**
   - **Test Drag-and-Drop:**
     - Drag `client_secret_*.json` onto upload zone
     - Verify zone highlights on drag-over
     - Verify upload success message appears
     - Verify file name displays
     - Verify "Next →" button enables
   - **Alternative: Click Upload:**
     - Click upload zone
     - Select file from file picker
     - Verify same success behavior
   - Click "Next →"

5. **Authenticate (Step 4)**
   - Click "🔐 Authenticate with Google Drive"
   - Verify status messages update in real-time:
     - "🔄 Starting OAuth flow..."
     - "🌐 Opening browser for authentication..."
     - "💾 Saving authentication token..."
   - **In opened browser window:**
     - Sign in with Google account
     - Review permissions request
     - Click "Allow"
     - Verify success message in browser
     - Close browser tab
   - **Back in Project APE:**
     - Verify "✅ Authentication complete!" message
     - Verify "Next →" button enables
   - Click "Next →"

6. **Verify Access (Step 5)**
   - Wait for automatic Drive access test
   - Verify results display:
     - "Authenticated: Yes"
     - "Accessible files: [number]"
     - List of sample files (if any exist in Drive)
   - Click "✅ Complete Setup"
   - Verify redirect to Clients tab
   - Verify success message appears

**Expected Results:**
- ✅ All steps complete without terminal access
- ✅ OAuth credentials saved to `~/.project-ape/drive_credentials.json`
- ✅ OAuth token saved to `~/.project-ape/drive_token.json`
- ✅ Drive API access verified
- ✅ Files listed from Google Drive

### Test Scenario 2: Already Configured

**Goal:** Verify wizard handles existing OAuth setup

**Steps:**

1. Navigate to OAuth Setup tab
2. Observe Step 1 status:
   - OAuth Credentials: ✅ Configured
   - Authentication Token: ✅ Configured
   - Drive Access: ✅ Configured
3. Verify success message: "OAuth already configured!"
4. User can skip wizard or reconfigure

**Expected Results:**
- ✅ Status badges show green checkmarks
- ✅ Clear messaging about existing setup
- ✅ Option to continue anyway for reconfiguration

### Test Scenario 3: Error Handling

**Goal:** Verify graceful error handling

**Test 3a: Invalid JSON Upload**

1. Go to Step 3
2. Upload a non-JSON file (e.g., .txt, .pdf)
3. Verify error message: "Please upload a JSON file"
4. Upload JSON without "installed" key
5. Verify error: "Invalid OAuth credentials format"

**Test 3b: OAuth Cancellation**

1. Complete Steps 1-3
2. Click "Authenticate" in Step 4
3. In browser, click "Cancel" or "Deny"
4. Verify error message displays
5. Verify "Authenticate" button re-enables
6. User can retry

**Test 3c: Network Issues**

1. Disconnect network
2. Try to check status in Step 1
3. Verify error message displays
4. Reconnect network
5. Retry and verify success

**Expected Results:**
- ✅ Clear error messages for each failure type
- ✅ Buttons re-enable for retry
- ✅ No crashes or unhandled exceptions
- ✅ User guidance for resolution

### Test Scenario 4: Navigation

**Goal:** Verify step navigation works correctly

**Steps:**

1. Navigate forward through all 5 steps
2. Click "← Back" at Step 5
3. Verify Step 4 displays
4. Click "← Back" again
5. Verify Step 3 displays
6. Navigate forward to Step 5
7. Verify progress indicator updates correctly

**Expected Results:**
- ✅ Forward/backward navigation works
- ✅ Progress indicator tracks current step
- ✅ Step content persists (uploaded file still shown)
- ✅ Smooth transitions between steps

### Test Scenario 5: Integration with Clients

**Goal:** Verify OAuth-configured Drive access works in client setup

**Steps:**

1. Complete OAuth wizard successfully
2. Go to "👥 Clients" tab
3. Click "➕ Add Client"
4. In Drive Folder URL field, paste a Google Drive folder URL
5. Complete client configuration
6. Save configuration
7. Start a workflow
8. Verify workflow accesses Drive files successfully

**Expected Results:**
- ✅ OAuth credentials used automatically
- ✅ No authentication errors in workflow
- ✅ Files downloaded from Drive
- ✅ Workflow completes successfully

---

## Verification Checklist

After testing, verify these files exist:

```bash
# OAuth credentials
ls -la ~/.project-ape/drive_credentials.json

# OAuth token
ls -la ~/.project-ape/drive_token.json

# Check permissions (should be 600)
ls -l ~/.project-ape/drive_*.json
```

Expected output:
```
-rw------- 1 user staff XXXX drive_credentials.json
-rw------- 1 user staff XXXX drive_token.json
```

---

## API Testing (Optional)

Test endpoints directly with `curl`:

### 1. Check OAuth Status
```bash
curl http://localhost:8765/api/oauth-status
```

Expected response:
```json
{
  "credentials_exist": true,
  "token_exist": true,
  "authenticated": true,
  "email": "Authenticated",
  "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
}
```

### 2. Upload Credentials
```bash
curl -X POST http://localhost:8765/api/upload-oauth-credentials \
  -F "file=@/path/to/client_secret_XXX.json"
```

Expected response:
```json
{
  "success": true,
  "message": "Credentials uploaded successfully",
  "client_id": "XXXXXXXXXXXX..."
}
```

### 3. Test Drive Access
```bash
curl http://localhost:8765/api/test-drive-access
```

Expected response:
```json
{
  "success": true,
  "authenticated": true,
  "total_accessible": 10,
  "sample_files": [
    {"name": "File1.pdf", "type": "application/pdf"},
    {"name": "File2.docx", "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
  ]
}
```

---

## Browser Console Testing

Open browser console (F12) and verify:

1. No JavaScript errors
2. API calls succeed (Network tab)
3. EventSource connection establishes (during Step 4)
4. SSE events received correctly

---

## Known Limitations

1. **Browser Requirement:** OAuth flow requires a browser that can open `localhost` callbacks
2. **Port Availability:** OAuth flow uses a random available port for callback
3. **Google Account:** User must have a Google account with Drive access
4. **GCP Project:** User must create GCP project and OAuth credentials first

---

## Troubleshooting

### Problem: "OAuth flow failed"

**Solutions:**
1. Verify `drive_credentials.json` contains valid OAuth client ID
2. Check that OAuth client type is "Desktop app" (not "Web app")
3. Ensure Google Drive API is enabled in GCP Console
4. Check browser console for detailed error messages

### Problem: "Invalid JSON file"

**Solutions:**
1. Verify file is the OAuth client JSON (not service account key)
2. Check file contains "installed" key (Desktop app credentials)
3. Re-download from GCP Console if corrupted

### Problem: Browser doesn't open

**Solutions:**
1. Check default browser settings
2. Manually open the authorization URL (displayed in console)
3. Verify no firewall blocking localhost connections

### Problem: Drive access test fails

**Solutions:**
1. Verify token file exists and is not corrupted
2. Check token hasn't expired (will auto-refresh if possible)
3. Re-run authentication flow to generate new token
4. Verify Google Drive API is enabled

---

## Success Criteria

All checkboxes must be ✅ for release:

- [ ] Fresh user completes OAuth without terminal
- [ ] File upload accepts and validates client_secret JSON
- [ ] OAuth flow opens browser automatically
- [ ] Drive access verification shows sample files
- [ ] Error messages are clear and actionable
- [ ] Navigation between steps works smoothly
- [ ] Integration with client configuration works
- [ ] Workflows use OAuth credentials successfully
- [ ] No JavaScript errors in console
- [ ] All API endpoints respond correctly
- [ ] SSE streaming works in Step 4
- [ ] File permissions are secure (600)

---

## Performance Metrics

Expected timing:
- Step 1 (Status Check): < 500ms
- Step 3 (File Upload): < 1s
- Step 4 (OAuth Flow): 10-30s (user dependent)
- Step 5 (Drive Test): 2-5s

---

## Next Steps

After successful testing:

1. Update README to include OAuth Wizard
2. Update QUICK_START guide with new wizard
3. Create video walkthrough (optional)
4. Add screenshots to documentation
5. Update user onboarding flow

---

## Support

For issues or questions:
- Check browser console for errors
- Review server logs: `tail -f dashboard/server.log`
- Check OAuth status: `ls -la ~/.project-ape/`
- Test API endpoints directly with curl

---

**Testing Completed:** ___________  
**Tested By:** ___________  
**Status:** ☐ Pass ☐ Fail  
**Notes:** ___________
