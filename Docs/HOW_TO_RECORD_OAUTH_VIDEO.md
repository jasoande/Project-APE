# How to Record the OAuth Setup Video Tutorial

This guide provides quick-start instructions for recording the OAuth setup video tutorial for Project APE.

---

## Quick Start

### 1. Review Documentation
Read these files in order:
1. **OAUTH_VIDEO_SCRIPT.md** - Your recording script (5-7 min tutorial)
2. **OAUTH_VIDEO_RECORDING_GUIDE.md** - Technical setup and recording instructions
3. **VIDEO_PRODUCTION_WORKFLOW.md** - Complete production workflow (optional, for reference)

### 2. Pre-Recording Setup (15-20 minutes)

#### Environment
```bash
# Start the dashboard
cd /Users/jasona/test/Project-APE-dev
python3 dashboard/server.py

# Open in browser (incognito mode recommended)
# http://localhost:8765/configure
```

#### Browser Setup
- Use Chrome or Safari in Incognito/Private mode
- Set zoom to 100%
- Hide bookmarks bar (Cmd+Shift+B)
- Close unnecessary tabs
- Keep only:
  - Project APE localhost tab
  - Google Cloud Console tab (logged in)

#### Screen Settings
- Resolution: 1920x1080 or 1280x720
- Close all other applications
- Enable Do Not Disturb mode
- Disable screen saver

#### Prepare Materials
- Sample `client_secret_*.json` file ready (from GCP)
- Script printed or on second monitor
- Microphone tested
- Recording software configured

### 3. Choose Recording Software

#### macOS (Easiest)
**QuickTime Player** (Built-in, Free)
1. Open QuickTime Player
2. File → New Screen Recording
3. Click options dropdown
4. Select microphone
5. Click record → Select full screen or window
6. Record your tutorial
7. File → Export As → 1080p or 720p

#### Windows
**Xbox Game Bar** (Built-in, Free)
1. Press Win+G
2. Click "Capture" widget
3. Click record button (or Win+Alt+R)
4. Record your tutorial
5. Videos saved to: `C:\Users\[username]\Videos\Captures`

#### Cross-Platform
**OBS Studio** (Free, Professional)
1. Download from obsproject.com
2. Create scene with "Display Capture"
3. Add audio input source
4. Settings → Output → Recording Quality: High
5. Start Recording button

### 4. Recording Process

#### A. Final Check (2 minutes)
- [ ] Dashboard running at http://localhost:8765/configure
- [ ] Browser in incognito mode, zoom 100%
- [ ] GCP Console logged in (separate tab)
- [ ] Sample client_secret file downloaded and ready
- [ ] Microphone working
- [ ] Recording software ready
- [ ] Script reviewed
- [ ] Do Not Disturb enabled

#### B. Record (10-15 minutes)
1. Start recording software
2. **Wait 3 seconds** (gives you room to trim)
3. Open browser to http://localhost:8765/configure
4. Follow script from OAUTH_VIDEO_SCRIPT.md:
   - Opening (0:00-0:30)
   - Step 1: Prerequisites (0:30-1:00)
   - Step 2: Create OAuth Credentials (1:00-3:30)
   - Step 3: Upload Credentials (3:30-4:30)
   - Step 4: Authenticate (4:30-5:45)
   - Step 5: Verify Access (5:45-6:45)
   - Closing (6:45-7:00)
5. **Wait 3 seconds** after finishing
6. Stop recording

#### C. Review (5 minutes)
- [ ] Watch entire recording
- [ ] Audio clear and audible
- [ ] All steps visible on screen
- [ ] No major mistakes or long pauses
- [ ] Video smooth, no stuttering

**If issues found**: Re-record problem sections or start over

### 5. Screenshots (During Recording)

Capture these 14 screenshots while recording:
1. oauth-wizard-step1-status.png
2. oauth-wizard-step2-instructions.png
3. gcp-console-credentials-page.png
4. gcp-console-create-oauth-client.png
5. gcp-console-download-json.png
6. oauth-wizard-step3-upload.png
7. oauth-wizard-step3-success.png
8. oauth-wizard-step4-start.png
9. oauth-wizard-step4-progress.png
10. google-oauth-consent-screen.png
11. oauth-wizard-step4-complete.png
12. oauth-wizard-step5-test.png
13. oauth-wizard-step5-results.png
14. oauth-wizard-complete.png

**macOS**: Cmd+Shift+4 (select area) or Cmd+Shift+3 (full screen)
**Windows**: Win+Shift+S (Snipping Tool)

Save to: `/Users/jasona/test/Project-APE-dev/Docs/screenshots/`

### 6. Basic Editing (Optional, 15-30 minutes)

If you want to polish the video:

#### Free Tools
- **macOS**: iMovie (built-in)
- **Windows**: DaVinci Resolve (free download)
- **Cross-platform**: Shotcut (free, open source)

#### Basic Edits
- Trim silence at beginning/end
- Remove mistakes or long pauses
- Add title card (5 sec): "Project APE - OAuth Setup Tutorial"
- Add end card (5 sec): GitHub link or "Thanks for watching"

### 7. Export Video

#### Export Settings
**Format**: MP4
**Resolution**: 1920x1080 or 1280x720 (match recording)
**Frame Rate**: 30 FPS
**Quality**: High (5000 kbps for 1080p, 3000 kbps for 720p)

#### File Naming
`oauth-setup-tutorial-v1.mp4`

#### Save Location
`/Users/jasona/test/Project-APE-dev/Docs/videos/oauth-setup-tutorial-v1.mp4`

### 8. Publish

#### Option A: YouTube (Recommended)
1. Upload to YouTube
2. Title: "Project APE - OAuth Setup Tutorial"
3. Description: Include GitHub link and tutorial steps
4. Visibility: Public or Unlisted
5. Add to playlist: "Project APE Tutorials"
6. Upload captions (auto-generate or manual .srt file)
7. Set thumbnail (create 1280x720 image from screenshot)

#### Option B: GitHub
If file is <100MB:
```bash
cd /Users/jasona/test/Project-APE-dev
git lfs install
git lfs track "*.mp4"
git add Docs/videos/oauth-setup-tutorial-v1.mp4
git commit -m "Add OAuth setup video tutorial"
git push
```

If file is 100MB-2GB:
1. Go to GitHub → Releases
2. Create new release
3. Upload video as asset

#### Option C: Vimeo
1. Upload to Vimeo
2. Set privacy (public or password-protected)
3. Enable downloads (optional)

### 9. Update Documentation

Edit `Docs/videos/README.md`:
```markdown
### OAuth Setup Tutorial

**Status**: ✅ Available
**Duration**: 6:32
**Watch**: [YouTube](https://youtu.be/YOUR_VIDEO_ID)
**Download**: [MP4](link-to-file)
```

Update main `README.md` (add to Getting Started):
```markdown
📹 **Video Tutorial**: [OAuth Setup Guide](https://youtu.be/YOUR_VIDEO_ID)
```

Commit changes:
```bash
git add Docs/videos/README.md README.md
git commit -m "Update documentation with OAuth video tutorial link"
git push
```

---

## Troubleshooting

### Common Issues

**Audio not recording**
- Check microphone selected in recording software
- Test with 5-second recording first
- Check system sound preferences

**Video stuttering**
- Close background applications
- Lower recording resolution (try 720p)
- Use SSD for recording destination

**File too large**
- Re-export with lower bitrate (3000 kbps)
- Use 720p instead of 1080p
- Trim unnecessary sections

**Mistakes while recording**
- Option 1: Pause for 5 seconds, restart sentence (edit out later)
- Option 2: Stop recording, restart from last clean section
- Option 3: Start over (if early in recording)

---

## Tips for Success

### Voice-Over
- Speak naturally, like explaining to a friend
- Don't rush - viewers can pause/rewind
- Smile while speaking (makes voice sound friendlier)
- Stay hydrated - keep water nearby

### Screen Recording
- Move mouse smoothly, not erratically
- Hover over buttons for 1-2 seconds before clicking
- Let animations complete before proceeding
- Wait for pages to fully load

### Pacing
- Total duration: aim for 6-8 minutes
- Don't try to be perfect - authenticity > perfection
- It's okay to have minor pauses or "um"s - editing can fix
- Practice run recommended before final recording

---

## Time Estimate

Total time to complete:
- **Setup**: 15-20 minutes
- **Recording**: 10-15 minutes
- **Review**: 5 minutes
- **Re-takes** (if needed): 10-20 minutes
- **Basic editing** (optional): 15-30 minutes
- **Export**: 5-10 minutes
- **Publish & documentation**: 10-15 minutes

**Total**: 1.5 - 2.5 hours (first time)
**Subsequent videos**: 1 - 1.5 hours (once familiar with process)

---

## Questions?

If you have questions while recording:
1. Check **OAUTH_VIDEO_RECORDING_GUIDE.md** for detailed technical info
2. Check **VIDEO_PRODUCTION_WORKFLOW.md** for production workflow
3. Open GitHub issue if documentation is unclear

---

## Next Steps After OAuth Video

Once the OAuth video is complete, consider creating:
1. **Complete Workflow Walkthrough** (10-15 min) - End-to-end demonstration
2. **Client Configuration Guide** (5-7 min) - Setting up client spreadsheets
3. **Troubleshooting Guide** (8-10 min) - Common issues and solutions

See `Docs/videos/README.md` for planned future tutorials.

---

**Good luck with your recording!**

Remember: The goal is to be helpful and clear, not perfect. Your first video will be great practice, and you can always create an updated version later if needed.
