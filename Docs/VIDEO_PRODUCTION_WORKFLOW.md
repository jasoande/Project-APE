# Video Production Workflow

This document outlines the complete workflow for producing Project APE tutorial videos, from planning to publication.

---

## Phase 1: Pre-Production

### 1.1 Topic Selection
- [ ] Identify tutorial topic and target audience
- [ ] Check if topic is already covered in existing videos
- [ ] Define learning objectives (what should viewers know after watching?)
- [ ] Estimate duration (keep under 15 minutes)

### 1.2 Script Writing
- [ ] Create script document in `/docs/` (see `OAUTH_VIDEO_SCRIPT.md` as template)
- [ ] Include timestamps for pacing
- [ ] Write voice-over narration
- [ ] Identify visual elements for each section
- [ ] Add notes for editor (zoom-ins, annotations, etc.)
- [ ] Review script for clarity and accuracy
- [ ] Test script with dry run (time it)

### 1.3 Environment Preparation
- [ ] Ensure software is running and bug-free
- [ ] Prepare sample data (test files, credentials, etc.)
- [ ] Set up browser bookmarks/tabs needed
- [ ] Clean desktop and close unnecessary applications
- [ ] Test all workflow steps work correctly

---

## Phase 2: Production

### 2.1 Recording Setup
- [ ] Follow checklist in `OAUTH_VIDEO_RECORDING_GUIDE.md`
- [ ] Set screen resolution (1920x1080 or 1280x720)
- [ ] Configure recording software settings
- [ ] Test microphone and audio levels
- [ ] Enable Do Not Disturb mode
- [ ] Close all notifications

### 2.2 Recording Session
- [ ] Start recording software
- [ ] Wait 3 seconds before beginning
- [ ] Follow script timing guide
- [ ] Speak clearly and at moderate pace
- [ ] Allow animations to complete
- [ ] Capture key screenshots for documentation
- [ ] End with 3 seconds of silence

### 2.3 Quality Check
- [ ] Immediately watch the full recording
- [ ] Check audio sync
- [ ] Verify all steps are visible
- [ ] Note any sections needing re-recording
- [ ] Save and backup raw file

### 2.4 Re-Takes (if needed)
- [ ] Identify problematic sections
- [ ] Re-record only necessary segments
- [ ] Maintain consistent audio levels
- [ ] Keep same visual settings

---

## Phase 3: Post-Production

### 3.1 Basic Editing
**Required Edits**:
- [ ] Trim silence at beginning and end
- [ ] Remove mistakes or long pauses
- [ ] Ensure smooth transitions between sections
- [ ] Normalize audio levels
- [ ] Remove background noise (if any)

**Optional Edits**:
- [ ] Add title card (5 seconds): "Project APE - [Tutorial Title]"
- [ ] Add section dividers
- [ ] Add end card (5 seconds): GitHub link, next steps
- [ ] Speed up very slow sections (max 1.5x)

### 3.2 Visual Enhancements (Optional)
- [ ] Add zoom-ins on important UI elements (2x zoom, 2 seconds)
- [ ] Add mouse click highlights
- [ ] Add text annotations for key points
- [ ] Add arrow annotations to guide viewer's eye
- [ ] Add keyboard shortcut overlays

### 3.3 Audio Enhancements (Optional)
- [ ] Add subtle background music (-20dB to -25dB)
- [ ] Fade music out during speech
- [ ] Add sound effects for success/error moments (use sparingly)
- [ ] Apply noise reduction filter

### 3.4 Accessibility
- [ ] Generate captions/subtitles (auto or manual)
- [ ] Review and correct auto-generated captions
- [ ] Export SRT subtitle file
- [ ] Create text transcript for documentation

---

## Phase 4: Export

### 4.1 Export Settings
Use these settings for final export:

**Video**:
- Format: MP4
- Codec: H.264
- Resolution: 1920x1080 or 1280x720 (match source)
- Frame rate: 30 FPS
- Bitrate: 5000 kbps (1080p) or 3000 kbps (720p)
- Profile: High

**Audio**:
- Codec: AAC
- Sample rate: 48 kHz
- Bitrate: 192 kbps
- Channels: Mono or Stereo

### 4.2 File Naming
Format: `{topic}-{type}-v{version}.mp4`

Examples:
- `oauth-setup-tutorial-v1.mp4`
- `workflow-walkthrough-tutorial-v1.mp4`

### 4.3 Quality Assurance
- [ ] Watch exported video fully
- [ ] Test on different devices (desktop, tablet, phone)
- [ ] Verify audio on laptop speakers (not just headphones)
- [ ] Check file size is reasonable (<500MB for 7 min @ 1080p)
- [ ] Verify captions display correctly (if embedded)

---

## Phase 5: Supplementary Materials

### 5.1 Screenshots
- [ ] Extract key screenshots from video
- [ ] Save in `/docs/screenshots/` directory
- [ ] Follow naming convention: `{location}-{feature}-{state}.png`
- [ ] Add annotations (arrows, highlights) as needed
- [ ] Update `/docs/screenshots/README.md`

### 5.2 Documentation
- [ ] Update `/docs/videos/README.md` with video details
- [ ] Create or update written guide companion
- [ ] Add video link to relevant documentation pages
- [ ] Update main README.md if appropriate

### 5.3 Thumbnail
Create attractive thumbnail (1280x720):
- [ ] Use screenshot from video
- [ ] Add title text overlay (large, readable font)
- [ ] Add Project APE branding/logo
- [ ] Save as `{video-name}-thumbnail.png`

---

## Phase 6: Publication

### 6.1 Choose Hosting Platform

**Option A: GitHub (files <100MB)**
```bash
cd /Users/jasona/test/Project-APE-dev
git lfs install
git lfs track "*.mp4"
git add docs/videos/oauth-setup-tutorial-v1.mp4
git commit -m "Add OAuth setup video tutorial"
git push
```

**Option B: GitHub Releases (files 100MB-2GB)**
1. Go to repository → Releases
2. Click "Draft a new release"
3. Tag version: `video-v1.0`
4. Upload video as release asset
5. Publish release

**Option C: YouTube (Recommended)**
1. Upload to YouTube channel
2. Settings:
   - Visibility: Public or Unlisted
   - Title: "Project APE - OAuth Setup Tutorial"
   - Description: Include GitHub link, timestamps, prerequisites
   - Tags: project-ape, oauth, google-drive, tutorial
   - Playlist: "Project APE Tutorials"
3. Upload thumbnail
4. Upload subtitle file (SRT)
5. Enable embedding
6. Copy embed code and URL

**Option D: Vimeo**
1. Upload video
2. Privacy: Public or password-protected
3. Enable downloads (optional)
4. Add description and tags

### 6.2 Update Documentation
Update the following files with video links:

**`/docs/videos/README.md`**:
```markdown
### OAuth Setup Tutorial
**Status**: ✅ Available
**Duration**: 6:32
**Watch**: [YouTube](https://youtu.be/...) | [Download](link)
```

**`/README.md`** (main repo README):
Add to "Getting Started" or "Resources" section:
```markdown
📹 **Video Tutorial**: [OAuth Setup Guide](https://youtu.be/...)
```

**`/docs/QUICK_START.md`** or **`/docs/OAUTH_SETUP_GUIDE.md`**:
Add video embed at the top:
```markdown
## Video Tutorial

<a href="https://youtu.be/VIDEO_ID">
  <img src="docs/videos/oauth-setup-tutorial-thumbnail.png" alt="OAuth Setup Tutorial" width="600">
</a>

*Watch the complete setup process (6:32)*
```

### 6.3 Commit to Repository
```bash
git add docs/videos/ docs/screenshots/ docs/*.md README.md
git commit -m "Add OAuth setup video tutorial and documentation"
git push origin dev
```

---

## Phase 7: Announcement

### 7.1 GitHub
- [ ] Create discussion post announcing new video
- [ ] Pin announcement to top of discussions
- [ ] Link video in welcome/pinned issue (if exists)

### 7.2 Social Media (if applicable)
- [ ] Twitter/X: Share with #ProjectAPE hashtag
- [ ] LinkedIn: Share in relevant groups
- [ ] Reddit: Post in r/selfhosted, r/automation (check rules first)
- [ ] Discord/Slack: Share in community channels

### 7.3 Changelog
Add to `CHANGELOG.md` or release notes:
```markdown
## [Version] - 2026-06-25

### Documentation
- Added OAuth setup video tutorial (6:32)
- Added video recording guides and scripts
- Added screenshot library for OAuth wizard
```

---

## Phase 8: Maintenance

### 8.1 Collect Feedback
- [ ] Monitor video comments/questions
- [ ] Track common confusion points
- [ ] Note requested clarifications
- [ ] Measure engagement metrics (views, watch time, retention)

### 8.2 Updates
When to create a new version:
- **v1.1** (minor update): Fix typos in captions, small corrections
- **v2.0** (major update): UI changes, new features, significant content changes

Process:
- [ ] Create new version with updated content
- [ ] Update version number in filename
- [ ] Keep old version in archive (don't delete)
- [ ] Update documentation links to new version
- [ ] Add changelog note explaining differences

### 8.3 Analytics Review (if using YouTube)
Monthly review:
- [ ] Check view count and watch time
- [ ] Review audience retention graph (where do people drop off?)
- [ ] Check traffic sources (where are viewers coming from?)
- [ ] Review comments for feedback
- [ ] Adjust future videos based on insights

---

## Phase 9: Follow-Up Content

### 9.1 Create Related Content
- [ ] Extract key screenshots for documentation
- [ ] Write companion blog post (if applicable)
- [ ] Create quick reference cheat sheet
- [ ] Identify topics for next video tutorial

### 9.2 Build Tutorial Series
Maintain consistency across videos:
- [ ] Use same intro/outro format
- [ ] Maintain same visual style
- [ ] Use consistent terminology
- [ ] Cross-reference related videos
- [ ] Create playlist on hosting platform

---

## Checklist Summary

Quick reference checklist for each video:

### Pre-Production
- [ ] Script written and reviewed
- [ ] Environment tested
- [ ] Sample data prepared

### Production
- [ ] Recording checklist completed
- [ ] Video recorded successfully
- [ ] Screenshots captured

### Post-Production
- [ ] Video edited and enhanced
- [ ] Captions/subtitles created
- [ ] Final export completed

### Publication
- [ ] Video uploaded to hosting platform
- [ ] Documentation updated
- [ ] Thumbnail created
- [ ] Changes committed to repo

### Announcement
- [ ] GitHub announcement posted
- [ ] Social media shared (if applicable)
- [ ] Changelog updated

---

## Resources

### Templates
- Video script: `/docs/OAUTH_VIDEO_SCRIPT.md`
- Recording guide: `/docs/OAUTH_VIDEO_RECORDING_GUIDE.md`
- Screenshots guide: `/docs/screenshots/README.md`

### Tools
- Recording: QuickTime, OBS Studio, ScreenFlow
- Editing: DaVinci Resolve, iMovie, Shotcut, Camtasia
- Annotations: Preview, GIMP, Snagit

### References
- YouTube Creator Academy: https://creatoracademy.youtube.com
- Vimeo Video School: https://vimeo.com/videoschool
- Royalty-free music: YouTube Audio Library, incompetech.com

---

**Last Updated**: 2026-06-25
**Template Version**: 1.0
