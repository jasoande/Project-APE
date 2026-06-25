# OAuth Video Recording Guide

## Overview
This guide provides technical instructions for recording the OAuth setup tutorial video for Project APE. Follow this checklist to ensure a professional, high-quality recording.

---

## Pre-Recording Checklist

### Environment Setup
- [ ] **Clean browser** (Chrome or Safari in incognito/private mode)
- [ ] **Clear browser cache** and cookies
- [ ] **Close unnecessary tabs** (only keep GCP Console and localhost)
- [ ] **Set browser zoom** to 100%
- [ ] **Hide bookmarks bar** (Cmd+Shift+B on Mac, Ctrl+Shift+B on Windows)
- [ ] **Close notification popups** (Do Not Disturb mode recommended)

### System Preparation
- [ ] **Dashboard running**: `python3 dashboard/server.py`
- [ ] **Verify URL**: http://localhost:8765/configure
- [ ] **OAuth wizard tab** exists and loads correctly
- [ ] **GCP Console account** logged in and ready
- [ ] **Sample client_secret JSON** prepared (from previous GCP setup or create new)
- [ ] **Desktop cleaned** (hide sensitive files/folders)

### Screen Settings
- [ ] **Resolution**: Set to 1920x1080 (1080p) or 1280x720 (720p)
- [ ] **Display scaling**: 100% (no scaling)
- [ ] **Hide desktop icons** (optional but cleaner)
- [ ] **Disable screen saver**
- [ ] **Disable auto-sleep**

### Recording Software Setup
- [ ] **Software installed and tested** (see recommendations below)
- [ ] **Recording settings configured** (see settings below)
- [ ] **Microphone tested** (record 10 seconds and play back)
- [ ] **Audio levels checked** (not too quiet or clipping)
- [ ] **Hotkeys memorized** (start/stop recording)

### Documentation
- [ ] **Script reviewed** (`OAUTH_VIDEO_SCRIPT.md`)
- [ ] **Timing practiced** (dry run without recording)
- [ ] **Browser tabs prepared** (localhost and GCP Console)

---

## Recommended Recording Software

### macOS
**QuickTime Player** (Built-in, Free)
- File → New Screen Recording
- Click options dropdown:
  - Microphone: Select your preferred mic
  - Quality: Maximum
- Click record, then select area or full screen
- **Pros**: Simple, reliable, native
- **Cons**: Basic features only

**ScreenFlow** (Paid, $169)
- Professional editing features
- Built-in annotations
- Mouse click highlights
- **Best for**: Final production-quality video

### Windows
**Xbox Game Bar** (Built-in, Free)
- Press Win+G to open
- Click "Capture" widget
- Click record button or Win+Alt+R
- **Pros**: Built-in, easy to use
- **Cons**: Limited settings

**OBS Studio** (Free, Open Source)
- Download from obsproject.com
- Create scene with "Display Capture"
- Add audio input source
- **Pros**: Professional features, free
- **Cons**: Steeper learning curve

### Linux
**SimpleScreenRecorder** (Free)
```bash
sudo apt install simplescreenrecorder  # Ubuntu/Debian
```
- Easy setup wizard
- Good performance
- **Pros**: Lightweight, reliable

**OBS Studio** (Free)
```bash
sudo apt install obs-studio
```

---

## Recording Settings

### Video Settings
| Setting | Recommended Value | Notes |
|---------|------------------|-------|
| Resolution | 1920x1080 or 1280x720 | 720p for smaller file size |
| Frame Rate | 30 FPS | Sufficient for tutorial |
| Codec | H.264 | Best compatibility |
| Bitrate | 5-8 Mbps (1080p), 3-5 Mbps (720p) | Higher = better quality |
| Format | MP4 | Universal playback |

### Audio Settings
| Setting | Recommended Value | Notes |
|---------|------------------|-------|
| Sample Rate | 48000 Hz | Professional standard |
| Bitrate | 192 kbps | Clear voice quality |
| Channels | Mono | Sufficient for voice-over |
| Format | AAC | Best compatibility |

### OBS Studio Specific Settings
```
Settings → Output:
  - Output Mode: Simple
  - Recording Quality: High Quality, Medium File Size
  - Recording Format: MP4
  
Settings → Video:
  - Base Resolution: 1920x1080
  - Output Resolution: 1920x1080 (or 1280x720)
  - Common FPS Values: 30

Settings → Audio:
  - Sample Rate: 48 kHz
  - Channels: Mono
```

---

## Recording Process

### Step 1: Final Check
1. Start Project APE dashboard
2. Open browser in incognito mode
3. Navigate to http://localhost:8765/configure
4. Open GCP Console in another tab (but stay on localhost tab)
5. Position windows for easy tab switching
6. Test microphone one last time

### Step 2: Start Recording
1. Open recording software
2. Select recording area (full screen or browser window only)
3. **Take a deep breath** - relax and speak naturally
4. Start recording
5. **Wait 3 seconds** before beginning (easier to trim)

### Step 3: Follow the Script
1. Refer to `OAUTH_VIDEO_SCRIPT.md`
2. Speak clearly and at a moderate pace
3. Follow the timing guide
4. Pause 2-3 seconds between major steps
5. Let animations complete before proceeding

### Step 4: Handle Mistakes
If you make a mistake:
- **Option A** (Preferred): Pause for 5 seconds, then restart the sentence
  - Easier to edit out the pause later
- **Option B**: Stop recording, fix issue, restart from last clean section
- **Don't**: Try to continue speaking while recovering - it's obvious

### Step 5: End Recording
1. After final voice-over, pause 3 seconds
2. Stop recording
3. Save file immediately to prevent data loss

---

## Recording Tips

### Voice-Over Best Practices
- **Speak naturally**: Pretend you're explaining to a colleague
- **Vary your pace**: Slow down for complex steps, normal pace for simple ones
- **Avoid filler words**: "um", "uh", "like", "you know"
- **Smile while speaking**: It makes your voice sound friendlier
- **Stay hydrated**: Keep water nearby

### Mouse Movement
- **Move smoothly**: No jerky or erratic movements
- **Hover to emphasize**: Pause cursor over important elements for 1-2 seconds
- **Circle to highlight**: Small circular movement draws attention
- **Click deliberately**: Don't rush clicks

### Pacing
- **Don't rush**: Viewers can pause/rewind
- **Allow processing time**: Wait for pages to load completely
- **Show, don't tell**: Let viewers see the result before moving on
- **Respect animation timing**: Wait for UI transitions to finish

### Common Mistakes to Avoid
- ❌ Speaking too fast
- ❌ Clicking before page loads
- ❌ Forgetting to switch tabs (show GCP Console when mentioned)
- ❌ Skipping steps from the script
- ❌ Background noise (notifications, phone, people)
- ❌ Mouse cursor off-screen when clicking
- ❌ Not showing success messages fully

---

## Post-Recording Checklist

### Immediate Review
- [ ] Watch entire recording
- [ ] Check audio levels (consistent throughout)
- [ ] Verify all steps are visible
- [ ] Note any sections that need re-recording
- [ ] Check for background noise or interruptions

### File Management
- [ ] Rename file: `oauth-setup-tutorial-raw-v1.mp4`
- [ ] Back up to external drive or cloud storage
- [ ] Keep original unedited version

### Basic Editing (Optional)
If you have editing software:
- [ ] Trim silence at beginning/end
- [ ] Remove long pauses or mistakes
- [ ] Speed up slow sections (1.5x max)
- [ ] Add title card (5 seconds): "Project APE - OAuth Setup Tutorial"
- [ ] Add end card (5 seconds): "For more info: [GitHub URL]"
- [ ] Add text annotations for key points
- [ ] Add mouse click highlights (if software supports)

### Quality Check
- [ ] Audio clear and intelligible
- [ ] Video smooth (no stuttering)
- [ ] All text readable (test on phone if possible)
- [ ] Total duration: 5-8 minutes (ideal)
- [ ] File size reasonable (<500MB for 7 min @ 1080p)

---

## Editing Software (Optional)

### Free Options
**DaVinci Resolve** (Cross-platform)
- Professional features
- Free version very capable
- Download: blackmagicdesign.com/products/davinciresolve

**Shotcut** (Cross-platform)
- Simple interface
- Good for basic editing
- Download: shotcut.org

**iMovie** (macOS only)
- Very beginner-friendly
- Built-in templates
- Pre-installed on Macs

### Paid Options
**Final Cut Pro** (macOS, $299)
- Professional editing
- Excellent for screen recordings

**Adobe Premiere Pro** (Cross-platform, $20.99/month)
- Industry standard
- Advanced features

**Camtasia** (Cross-platform, $299)
- Specialized for tutorials
- Built-in annotations and callouts
- Recommended for screen recording tutorials

---

## Editing Enhancements (Advanced)

### Text Annotations
Add text overlays for:
- Step numbers ("Step 2: Create OAuth Credentials")
- Key points ("Important: Save this file securely")
- URLs or commands
- Keyboard shortcuts shown

### Visual Enhancements
- **Zoom-ins**: Close-up on important buttons (2x zoom, 2 seconds)
- **Mouse highlights**: Circle or glow effect on clicks
- **Arrow annotations**: Point to specific UI elements
- **Screen transitions**: Smooth fade between major sections

### Audio Enhancements
- **Normalize audio**: Consistent volume throughout
- **Remove background noise**: Most editors have noise reduction
- **Add background music** (optional):
  - Keep volume very low (-20dB to -25dB)
  - Use royalty-free music (YouTube Audio Library, incompetech.com)
  - Fade out during speech

---

## Export Settings

### Final Export
```
Format: MP4
Codec: H.264
Resolution: 1920x1080 or 1280x720
Frame Rate: 30 FPS
Bitrate: 5000 kbps (1080p) or 3000 kbps (720p)
Audio: AAC, 192 kbps, 48 kHz
```

### File Naming
`oauth-setup-tutorial-v1.mp4`

Version numbering:
- v1: First release
- v1.1: Minor updates (typo fixes)
- v2: Major updates (UI changes, new features)

---

## Publishing

### File Storage
**GitHub** (for files <100MB)
```bash
git lfs install
git lfs track "*.mp4"
git add docs/videos/oauth-setup-tutorial-v1.mp4
git commit -m "Add OAuth setup video tutorial"
git push
```

**GitHub Releases** (for files 100MB-2GB)
1. Go to repository → Releases
2. Create new release
3. Upload video as asset
4. Reference in docs/videos/README.md

**YouTube** (Recommended for large files)
- Upload as unlisted or public
- Add to playlist: "Project APE Tutorials"
- Embed in README.md or documentation
- Enable captions (auto-generate or upload SRT file)

**Vimeo**
- Professional appearance
- Password protection option
- Download option for offline viewing

### Documentation Update
Update `docs/videos/README.md`:
```markdown
## OAuth Setup Tutorial

**Status**: ✅ Available
**Duration**: 6:32
**Watch**: [YouTube](https://youtu.be/...) | [Download](link-to-file)
```

### Announcement
- Update main README.md with video link
- Post in discussions/announcements
- Share on social media (if applicable)

---

## Troubleshooting

### Common Issues

**Audio out of sync**
- Solution: Use same sample rate (48 kHz) for recording and editing
- Re-export with "match source" settings

**Video stuttering**
- Solution: Close background applications during recording
- Lower recording bitrate or resolution
- Use SSD for recording destination

**File too large**
- Solution: Re-export with lower bitrate (3000 kbps is usually fine)
- Use 720p instead of 1080p
- Trim unnecessary sections

**Background noise**
- Solution: Record in quiet room
- Use noise reduction in editing
- Consider using headset microphone

**Mouse movements jerky**
- Solution: Practice smooth movements before recording
- Adjust mouse sensitivity (slower is smoother)
- Edit out erratic sections

---

## Final Checklist Before Publishing

- [ ] Video plays correctly on multiple devices
- [ ] Audio clear on laptop speakers (not just headphones)
- [ ] All sensitive information removed (API keys, emails, etc.)
- [ ] Credits/attributions added if using third-party assets
- [ ] Description/metadata prepared for hosting platform
- [ ] README.md updated with video link
- [ ] Thumbnail created (1280x720 image)
- [ ] File backed up in multiple locations

---

## Contact

If you need help with the recording process:
- Check the Project APE discussions board
- Review example tutorial videos for reference
- Consider doing a practice run and sharing for feedback

Good luck with your recording!
