# OAuth Setup Video Tutorial Script

## Duration: 5-7 minutes

## Opening (0:00-0:30)
**Visual**: Show Project APE dashboard homepage
**Action**: Navigate to Configure page
**Voice-over**: "In this tutorial, we'll set up Google Drive access for Project APE using the OAuth wizard. This step-by-step process will guide you through creating credentials, authenticating with Google, and verifying your connection."

---

## Step 1: Check Prerequisites (0:30-1:00)
**Visual**: Configure page with tabs visible
**Action**: Click "🔑 Google Drive Setup" tab
**Voice-over**: "The wizard first checks if you already have OAuth configured. You can see the status of your credentials and authentication token here."
**Highlight**: 
- Status badges (credentials/token)
- Clear indicators showing what's missing
- "Next" button to proceed

---

## Step 2: Create OAuth Credentials (1:00-3:30)
**Visual**: Step 2 screen with instructions
**Action**: Click "Next" to Step 2
**Voice-over**: "To connect to Google Drive, you'll need to create OAuth credentials in the Google Cloud Console. Click the link provided to open the console in a new tab."

### GCP Console Navigation:
**Visual**: Switch to GCP Console tab
**Voice-over**: "In the Google Cloud Console, follow these steps:"

1. **Navigate to APIs & Services**
   - Click hamburger menu
   - Select "APIs & Services"
   - Click "Credentials"

2. **Create OAuth Client ID**
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   - Choose application type: "Desktop app"
   - Name: "Project APE Desktop" (or your preference)
   - Click "Create"

3. **Download Credentials**
   - Success dialog appears
   - Click "DOWNLOAD JSON"
   - Save to your Downloads folder
   - Note: File name starts with "client_secret_"

**Voice-over**: "Save this file - you'll upload it in the next step. Never share this file as it contains sensitive credentials."

---

## Step 3: Upload Credentials (3:30-4:30)
**Visual**: Return to Project APE tab
**Action**: Click "Next" to Step 3
**Voice-over**: "Now we'll upload the credentials file you just downloaded. You can either drag and drop the file, or click to browse."

### Demonstrate Drag-and-Drop:
**Actions**:
1. Drag client_secret file from Downloads to drop zone
2. **Highlight**: Drop zone changes color when file hovers
3. **Show**: File name appears in preview
4. **Show**: Validation success message (green checkmark)
5. Click "Upload Credentials" button
6. **Show**: Upload progress bar (brief)
7. **Show**: Success message with file details

**Voice-over**: "The wizard validates that your file is a genuine Google OAuth credentials file. Once validated, click 'Upload Credentials' to save it to your Project APE configuration."

**Alternative**: Show click-to-browse method briefly

---

## Step 4: Authenticate (4:30-5:45)
**Visual**: Step 4 screen with "Start OAuth Flow" button
**Action**: Click "Start OAuth Flow"
**Voice-over**: "Now we'll authenticate with Google using the credentials you just uploaded. Click 'Start OAuth Flow' to begin."

### Real-Time Progress Display:
**Visual**: Show progress indicators in dashboard
**Voice-over**: "The wizard will open your default browser automatically."

**Progress messages shown**:
1. "Opening browser..."
2. "Waiting for authentication..."

**Browser Window**:
- Google sign-in screen appears
- Enter Google account credentials
- Grant permissions screen:
  - "Project APE Desktop wants to access your Google Drive"
  - Scopes listed (read/write access)
- Click "Allow"
- Success callback page: "Authentication successful! You can close this window."

**Return to Project APE**:
- **Show**: Progress updates in real-time
- **Show**: "Authentication complete!" success message
- **Highlight**: Token status badge turns green

**Voice-over**: "Once you grant permissions, the browser will confirm success and you can return to Project APE. The wizard automatically detects the successful authentication."

---

## Step 5: Verify Access (5:45-6:45)
**Visual**: Step 5 screen with "Test Drive Access" button
**Action**: Click "Next" to Step 5
**Voice-over**: "Let's verify that everything is working correctly by testing your Google Drive connection."

**Action**: Click "Test Drive Access"

**Visual**: Show real-time test results:
- Loading spinner appears
- Success message: "Successfully connected to Google Drive!"
- Sample files list displays:
  - File names
  - File types (icons)
  - Last modified dates
  - File sizes

**Highlight**:
- Green checkmarks next to each test
- "Connection verified" badge
- File count displayed

**Voice-over**: "The test successfully retrieves a list of files from your Google Drive, confirming that Project APE can now access your files. You're all set!"

---

## Closing (6:45-7:00)
**Visual**: Step 5 success screen
**Action**: Click "Finish" button
**Visual**: Return to Configure page overview
**Highlight**: OAuth status badge now shows green checkmark

**Voice-over**: "Congratulations! Your Google Drive is now connected to Project APE. You can now move on to configuring your clients and launching workflows. If you need to re-authenticate or update credentials in the future, just return to this wizard."

**Visual**: Briefly show "Configure Clients" tab
**Action**: Hover over "Launch Workflow" button

**Voice-over**: "Check out the client configuration guide to set up your first client and start automating your workflows."

**End Screen**: Project APE logo or dashboard view
**Text overlay**: "For more tutorials, visit github.com/yourusername/Project-APE-dev"

---

## Recording Notes

### Pacing
- Speak clearly and not too fast
- Pause 2-3 seconds between major actions
- Allow time for viewers to read on-screen text

### Mouse Movement
- Move cursor smoothly, not erratically
- Hover over important elements for 1-2 seconds
- Use circular mouse movements to draw attention

### Error Handling
- If an error occurs, pause recording
- Fix the issue
- Resume from the last clean step
- Edit out errors in post-production

### Common Issues to Avoid
- Don't rush through GCP Console navigation
- Ensure file downloads are visible
- Wait for all animations to complete before clicking
- Check that all success messages are fully visible

### Optional Enhancements
- Add smooth zoom-ins on important UI elements
- Add text annotations for key points
- Use mouse click highlights (many screen recorders support this)
- Add subtle background music (keep volume low, -20dB to -25dB)
