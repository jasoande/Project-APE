# Project APE Screenshots

This directory contains screenshots referenced in documentation and video tutorials.

---

## OAuth Setup Wizard Screenshots

These screenshots correspond to the video tutorial and should be captured during recording.

### Required Screenshots

1. **oauth-wizard-step1-status.png**
   - Location: Configure page, OAuth tab, Step 1
   - Shows: Credential and token status badges
   - Purpose: Users can see what a "not configured" state looks like

2. **oauth-wizard-step2-instructions.png**
   - Location: Step 2 - Create OAuth Credentials
   - Shows: Instructions with GCP Console link
   - Purpose: Reference for what to do in GCP

3. **gcp-console-credentials-page.png**
   - Location: Google Cloud Console - APIs & Services - Credentials
   - Shows: Create Credentials dropdown
   - Purpose: Visual guide for GCP navigation

4. **gcp-console-create-oauth-client.png**
   - Location: GCP Console - Create OAuth client ID form
   - Shows: Desktop app selection, naming field
   - Purpose: Shows correct application type selection

5. **gcp-console-download-json.png**
   - Location: GCP Console - OAuth client created dialog
   - Shows: Download JSON button
   - Purpose: Users know what file to download

6. **oauth-wizard-step3-upload.png**
   - Location: Step 3 - Upload Credentials
   - Shows: Drag-and-drop zone, file preview
   - Purpose: Visual guide for upload interface

7. **oauth-wizard-step3-success.png**
   - Location: Step 3 - After successful upload
   - Shows: Success message, validated file info
   - Purpose: Confirmation of correct upload

8. **oauth-wizard-step4-start.png**
   - Location: Step 4 - Authenticate
   - Shows: "Start OAuth Flow" button
   - Purpose: Shows authentication initiation

9. **oauth-wizard-step4-progress.png**
   - Location: Step 4 - During authentication
   - Shows: Real-time progress indicators
   - Purpose: Users know what to expect during flow

10. **google-oauth-consent-screen.png**
    - Location: Google OAuth consent page (in browser)
    - Shows: Permission grant screen
    - Purpose: Users know what permissions are requested

11. **oauth-wizard-step4-complete.png**
    - Location: Step 4 - After successful authentication
    - Shows: Success message, token status updated
    - Purpose: Confirmation of successful auth

12. **oauth-wizard-step5-test.png**
    - Location: Step 5 - Verify Access
    - Shows: Test Drive Access button
    - Purpose: Shows verification interface

13. **oauth-wizard-step5-results.png**
    - Location: Step 5 - Test results
    - Shows: Sample files list, success indicators
    - Purpose: Confirmation of working connection

14. **oauth-wizard-complete.png**
    - Location: Configure page overview after completion
    - Shows: Green checkmark on OAuth status badge
    - Purpose: Final confirmation and next steps

---

## How to Capture Screenshots

### During Video Recording
1. Take screenshots at each key step while recording
2. Use native screenshot tools:
   - macOS: Cmd+Shift+4 (select area) or Cmd+Shift+3 (full screen)
   - Windows: Win+Shift+S (Snipping Tool)
   - Linux: Varies by desktop environment

### Resolution and Format
- **Format**: PNG (lossless, good for UI)
- **Minimum width**: 1280px (720p)
- **Ideal width**: 1920px (1080p)
- **Crop**: Remove unnecessary browser chrome/toolbar when possible
- **Annotations**: Use red arrows/boxes to highlight important elements

### Privacy
- Blur or remove any sensitive information:
  - Email addresses
  - API keys
  - Personal file names
  - Account identifiers

### Naming Convention
`{location}-{feature}-{state}.png`

Examples:
- `oauth-wizard-step1-status.png`
- `gcp-console-credentials-page.png`
- `oauth-complete-success.png`

---

## Screenshot Annotation Tools

### Free Options
- **macOS**: Preview (built-in)
  - Open image → Tools → Annotate
  - Add arrows, boxes, text
  
- **Windows**: Paint 3D or Snip & Sketch
  - Basic annotations included

- **Linux**: GIMP or Shutter
  - GIMP: Full-featured image editor
  - Shutter: Screenshot tool with annotations

### Recommended Annotations
- Red rectangles around clickable buttons
- Red arrows pointing to important fields
- Yellow highlights for text to read
- Numbered steps (1, 2, 3) for sequential actions

---

## Using Screenshots in Documentation

### Markdown Embedding
```markdown
![OAuth Step 1 Status](screenshots/oauth-wizard-step1-status.png)
*Figure 1: OAuth wizard showing unconfigured status*
```

### HTML with Captions
```html
<figure>
  <img src="screenshots/oauth-wizard-step1-status.png" alt="OAuth Step 1" width="800">
  <figcaption>Figure 1: OAuth wizard Step 1 - Status check</figcaption>
</figure>
```

---

## Current Status

| Screenshot | Status | Notes |
|------------|--------|-------|
| oauth-wizard-step1-status.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step2-instructions.png | ⏳ Pending | Capture during video recording |
| gcp-console-credentials-page.png | ⏳ Pending | Capture during video recording |
| gcp-console-create-oauth-client.png | ⏳ Pending | Capture during video recording |
| gcp-console-download-json.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step3-upload.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step3-success.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step4-start.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step4-progress.png | ⏳ Pending | Capture during video recording |
| google-oauth-consent-screen.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step4-complete.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step5-test.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-step5-results.png | ⏳ Pending | Capture during video recording |
| oauth-wizard-complete.png | ⏳ Pending | Capture during video recording |

---

**Last Updated**: 2026-06-25
