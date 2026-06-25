# Screenshot Capture Instructions

This document provides detailed instructions for capturing screenshots referenced in Project APE documentation.

---

## Required Screenshots

### 1. configure-page.png
**Location:** Configuration form with sample client  
**When to capture:** Initial load of configuration page with one client filled in  

**Steps:**
1. Launch Project APE: `http://localhost:8765/configure`
2. Fill in one sample client:
   - Name: "Acme Corporation"
   - Drive Folder: (use a real example)
   - Industry: "technology"
   - Subsegments: "cloud computing, cybersecurity"
3. Ensure page shows:
   - Green checkmarks for setup status
   - All form fields visible
   - "Add Client" and "Start Workflow" buttons visible
4. Take full-page screenshot
5. Crop to show configuration section clearly
6. Save as: `configure-page.png`

**Recommended size:** 1200x800px  
**Format:** PNG  
**What to show:**
- Header with Project APE title
- Setup status indicators (green checkmarks)
- Client form with sample data
- Action buttons at bottom

---

### 2. dashboard-monitoring.png
**Location:** Active workflow with progress  
**When to capture:** During workflow execution, showing real-time progress  

**Steps:**
1. Start a workflow with 2-3 clients
2. Wait until at least one client is 30-50% complete
3. Ensure dashboard shows:
   - Execution timer running
   - Progress bars for multiple clients
   - Different completion states (some running, some complete)
   - Overall progress bar in header
4. Expand logs section (show some log entries)
5. Take full-page screenshot
6. Save as: `dashboard-monitoring.png`

**Recommended size:** 1400x900px  
**Format:** PNG  
**What to show:**
- Header with timer and progress stats
- At least 2-3 client cards with varying progress
- Progress bars showing different percentages
- Status indicators (RUNNING, COMPLETE)
- Visible log entries at bottom

---

### 3. oauth-wizard.png
**Location:** OAuth wizard Step 1  
**When to capture:** OAuth setup wizard showing step navigation  

**Steps:**
1. Navigate to: `http://localhost:8765/configure`
2. Click "Google Drive Setup" button
3. OAuth wizard modal opens
4. Ensure showing:
   - Step indicator (Step 1 of 5)
   - Clear instructions for creating GCP project
   - "Next" button
   - Clean, professional appearance
5. Take screenshot of modal
6. Save as: `oauth-wizard.png`

**Recommended size:** 800x600px  
**Format:** PNG  
**What to show:**
- Modal dialog overlay
- Step 1 content clearly visible
- Step indicator at top
- Navigation buttons (Next/Back)
- Instructions text legible

---

### 4. setup-environment.png
**Location:** Setup button with output  
**When to capture:** During or after environment setup completion  

**Steps:**
1. Navigate to: `http://localhost:8765/configure`
2. If setup already complete: Reset environment (for clean capture)
3. Click "Setup Environment" button
4. Capture either:
   - **Option A:** During setup (showing progress spinner)
   - **Option B:** After completion (showing green checkmark)
5. Ensure showing:
   - "Setup Environment" section
   - Progress indicator or success status
   - Brief description text
6. Take screenshot
7. Save as: `setup-environment.png`

**Recommended size:** 600x300px  
**Format:** PNG  
**What to show:**
- Setup Environment button/section
- Status indicator (in progress or complete)
- Success message if complete

---

### 5. auth-status.png
**Location:** NotebookLM auth with green checkmark  
**When to capture:** After successful NotebookLM authentication  

**Steps:**
1. Navigate to: `http://localhost:8765/configure`
2. Ensure NotebookLM authentication is complete
3. Locate authentication status section
4. Ensure showing:
   - ✅ Green checkmark
   - "NotebookLM: Authenticated" or similar
   - Login button (disabled or showing "Re-authenticate")
5. Take screenshot of auth status area
6. Save as: `auth-status.png`

**Recommended size:** 600x200px  
**Format:** PNG  
**What to show:**
- Authentication status indicator
- Green checkmark clearly visible
- Status text ("Authenticated")
- NotebookLM logo/icon if present

---

### 6. completed-workflow.png
**Location:** Finished workflow with quality score  
**When to capture:** After all clients have completed successfully  

**Steps:**
1. Wait for complete workflow execution
2. Ensure all clients show:
   - 100% progress
   - "COMPLETE" status badge (green)
   - Quality score displayed (e.g., "8.5/10")
   - Clickable NotebookLM link
3. Ensure dashboard shows:
   - Total execution time
   - All clients in "Complete" state
   - No failures
4. Take full-page screenshot
5. Save as: `completed-workflow.png`

**Recommended size:** 1400x900px  
**Format:** PNG  
**What to show:**
- All client cards showing COMPLETE status
- Quality scores visible
- NotebookLM links present
- Final execution time in header
- Overall 100% progress

---

## Screenshot Guidelines

### Technical Specifications

**Resolution:**
- Minimum: 1200px width
- Recommended: 1400-1600px width
- Use retina/2x resolution when possible

**Format:**
- PNG (preferred for UI screenshots)
- JPG only if file size is a concern
- No GIF or WebP

**File Size:**
- Target: Under 500KB per image
- Maximum: 1MB per image
- Compress using tools like TinyPNG if needed

**Color:**
- Full color (no grayscale)
- Maintain original UI colors
- Ensure good contrast

### Capture Best Practices

**Browser Setup:**
1. Use Chrome or Firefox (consistent rendering)
2. Set browser zoom to 100%
3. Use consistent window size for related screenshots
4. Clear browser cache before capturing
5. Disable browser extensions that modify page appearance

**Content Preparation:**
1. Use realistic sample data (not "test test test")
2. Avoid sensitive or real client information
3. Ensure all text is legible when scaled down
4. Remove any personal information from view
5. Clear notification badges or alerts

**Image Quality:**
1. Use native screenshot tools (Cmd+Shift+4 on Mac)
2. Avoid scaling/resizing after capture
3. Crop to focus on relevant content
4. Maintain aspect ratios
5. Check for blurriness before saving

**Consistency:**
1. Use same browser for all screenshots
2. Use same theme/appearance settings
3. Capture at same time of day (consistent lighting)
4. Use consistent sample data across related images
5. Maintain similar zoom levels

### Editing Guidelines

**Allowed edits:**
- Crop to focus on relevant area
- Add red arrows/boxes to highlight features (optional)
- Add text annotations for clarity (optional)
- Blur sensitive information if needed
- Optimize file size

**Avoid:**
- Don't alter colors or contrast significantly
- Don't add fake/misleading UI elements
- Don't composite multiple screenshots
- Don't use filters or effects
- Don't change fonts or styling

---

## Screenshot Checklist

Before saving each screenshot, verify:

- [ ] Content is clearly visible and legible
- [ ] No sensitive information visible
- [ ] File name matches documentation reference
- [ ] Image is properly cropped
- [ ] Resolution meets minimum requirements
- [ ] File size is reasonable (< 1MB)
- [ ] Format is PNG
- [ ] Image demonstrates intended feature/state
- [ ] Sample data looks realistic
- [ ] Browser UI is clean (no excessive toolbars)

---

## Alternative: Placeholder Images

If you cannot capture real screenshots yet, create placeholder images:

**Using ImageMagick:**
```bash
# Create placeholder
convert -size 1200x800 xc:lightgray \
  -pointsize 48 -fill gray \
  -gravity center -annotate +0+0 "Configure Page\nScreenshot Placeholder" \
  configure-page.png
```

**Using Python (PIL):**
```python
from PIL import Image, ImageDraw, ImageFont

# Create placeholder
img = Image.new('RGB', (1200, 800), color='lightgray')
d = ImageDraw.Draw(img)
d.text((600, 400), "Configure Page\nScreenshot Placeholder", 
       fill='gray', anchor="mm")
img.save('configure-page.png')
```

**Online tools:**
- https://placeholder.com/
- https://via.placeholder.com/
- https://dummyimage.com/

**Placeholder specs:**
- Size: Match required dimensions above
- Color: Light gray background (#E0E0E0)
- Text: Feature name + "Screenshot Placeholder"
- Font: Arial or similar, readable size

---

## Updating Screenshots

When to update screenshots:

1. **UI changes:** Any visual updates to dashboard or configuration page
2. **Feature additions:** New buttons, sections, or indicators
3. **Branding changes:** Logo updates or color scheme changes
4. **Bug fixes:** If existing screenshots show incorrect behavior
5. **Quality improvement:** If current images are low quality or unclear

**Process:**
1. Capture new screenshot following guidelines above
2. Compare with existing screenshot
3. Verify new image is higher quality or more accurate
4. Replace old file with same filename
5. Update documentation if features have changed
6. Commit changes with descriptive message:
   ```bash
   git commit -m "Update dashboard screenshot with new quality indicator"
   ```

---

## Questions?

If you need clarification on any screenshot requirements:

1. Check existing documentation for context
2. Review similar projects for examples
3. Open GitHub issue with question
4. Tag @jasona for screenshot guidance

---

## Credits

Screenshots should be captured from actual Project APE instances running locally.

Do not use:
- Stock photos
- Screenshots from other projects
- AI-generated images
- Photoshopped composites

All screenshots should represent real, working features.

---

**Last Updated:** June 25, 2026  
**Maintained By:** Project APE Documentation Team
