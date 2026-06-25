# Project APE Video Tutorials

This directory contains video tutorials for Project APE. Videos provide step-by-step visual guides to help users get started and make the most of the platform.

---

## Available Tutorials

### OAuth Setup Tutorial

**Status**: 🎬 Ready to Record

**Planned Duration**: 5-7 minutes

**Description**: Complete walkthrough of the OAuth setup wizard, from creating Google Cloud credentials to verifying Google Drive access.

**Topics Covered**:
- Accessing the OAuth wizard in the dashboard
- Creating OAuth credentials in Google Cloud Console
- Uploading credentials via drag-and-drop interface
- Completing the OAuth authentication flow
- Testing and verifying Google Drive connection

**Documentation**:
- **Recording Script**: [`/docs/OAUTH_VIDEO_SCRIPT.md`](../OAUTH_VIDEO_SCRIPT.md)
- **Recording Guide**: [`/docs/OAUTH_VIDEO_RECORDING_GUIDE.md`](../OAUTH_VIDEO_RECORDING_GUIDE.md)

**Prerequisites for Recording**:
- Project APE dashboard running locally
- Google Cloud Console account with project created
- Screen recording software installed
- Microphone for voice-over

**How to Record**:
1. Review the recording script: `docs/OAUTH_VIDEO_SCRIPT.md`
2. Follow setup instructions in: `docs/OAUTH_VIDEO_RECORDING_GUIDE.md`
3. Complete pre-recording checklist
4. Record following the script timing guide
5. Review and edit (optional)
6. Export as MP4 and place in this directory
7. Update this README with the video link

---

## Placeholder: Text Alternatives

Until videos are recorded, users can follow these text-based guides:

### OAuth Setup
- **Quick Start**: [`/docs/QUICK_START.md`](../QUICK_START.md) - Section on OAuth setup
- **Detailed Guide**: [`/docs/OAUTH_SETUP_GUIDE.md`](../OAUTH_SETUP_GUIDE.md) - Complete written instructions
- **Screenshots**: [`/docs/screenshots/`](../screenshots/) - Visual reference images

### Workflow Configuration
- **README**: [`/README.md`](../../README.md) - Overview and basic usage
- **Understanding Workflows**: [`/docs/UNDERSTANDING_THE_WORKFLOW.md`](../UNDERSTANDING_THE_WORKFLOW.md)

---

## Future Video Tutorials (Planned)

### 1. Complete Workflow Walkthrough
**Estimated Duration**: 10-15 minutes
**Topics**:
- Overview of Project APE capabilities
- OAuth setup (brief)
- Client configuration from spreadsheet
- Launching a workflow
- Monitoring progress in real-time
- Reviewing results and logs

**Priority**: High
**Status**: Script pending

---

### 2. Client Configuration Deep Dive
**Estimated Duration**: 5-7 minutes
**Topics**:
- Understanding the client data structure
- Creating a client spreadsheet template
- Importing client data
- Validating client configurations
- Testing with sample clients

**Priority**: Medium
**Status**: Script pending

---

### 3. Troubleshooting Common Issues
**Estimated Duration**: 8-10 minutes
**Topics**:
- OAuth authentication failures
- File permission errors
- Workflow stuck or hanging
- Dashboard connection issues
- Log file analysis

**Priority**: Medium
**Status**: Script pending

---

### 4. Advanced Features Tour
**Estimated Duration**: 12-15 minutes
**Topics**:
- Custom workflow detector patterns
- Advanced variable configuration
- Batch processing strategies
- Error handling and recovery
- Performance optimization tips

**Priority**: Low
**Status**: Script pending

---

## Video Specifications

All videos should follow these standards for consistency:

### Technical Requirements
- **Resolution**: 1920x1080 (1080p) or 1280x720 (720p)
- **Frame Rate**: 30 FPS
- **Format**: MP4 (H.264 codec)
- **Audio**: AAC, 48 kHz, stereo or mono
- **Bitrate**: 5-8 Mbps (1080p), 3-5 Mbps (720p)

### Content Guidelines
- **Duration**: Keep under 15 minutes (5-7 minutes ideal)
- **Pacing**: Speak clearly, pause between steps
- **Visuals**: Clean browser, 100% zoom, no distractions
- **Audio**: Clear voice-over, minimal background noise
- **Structure**: Intro → Steps → Conclusion

### Naming Convention
`{topic}-{type}-v{version}.mp4`

Examples:
- `oauth-setup-tutorial-v1.mp4`
- `workflow-walkthrough-tutorial-v1.mp4`
- `troubleshooting-guide-v1.mp4`

---

## Hosting Options

### Option 1: GitHub (Files < 100MB)
Store directly in this repository:
```bash
git lfs install
git lfs track "*.mp4"
git add docs/videos/*.mp4
git commit -m "Add tutorial video"
git push
```

### Option 2: GitHub Releases (Files 100MB - 2GB)
1. Create a new release
2. Upload video as release asset
3. Link in README and documentation

### Option 3: YouTube (Recommended)
**Pros**:
- No file size limits
- Streaming (no download needed)
- Automatic captions
- Analytics

**Setup**:
1. Create "Project APE Tutorials" playlist
2. Upload as public or unlisted
3. Enable captions (auto or manual)
4. Embed in documentation

### Option 4: Vimeo
**Pros**:
- Professional appearance
- Password protection option
- Downloadable files

---

## Contributing Videos

We welcome community-contributed tutorials! If you'd like to create a video:

1. **Check planned tutorials** above - pick an unassigned topic or propose a new one
2. **Open an issue** to claim the topic and get feedback on your outline
3. **Follow the recording guides** in this directory for quality standards
4. **Submit a pull request** with:
   - The video file (or link if hosted externally)
   - Recording script used
   - Any relevant screenshots or supplementary materials
5. **Update this README** with your video details

### Quality Standards
- Clear audio (no background noise)
- Smooth screen recording (no stuttering)
- Professional pacing (not too fast)
- Accurate content (tested and verified)
- Proper lighting (for webcam portions, if any)

---

## Accessibility

All videos should include:
- **Captions/Subtitles**: Either auto-generated or manually created
- **Transcript**: Plain text version of voice-over in docs
- **Screen reader friendly**: Descriptive titles and metadata

---

## License

All video content in this directory is subject to the same license as the Project APE project (see main LICENSE file).

By contributing videos, you agree to license your contribution under the same terms.

---

## Questions or Feedback

- **Issues**: Report video issues or request topics via GitHub Issues
- **Discussions**: Share feedback or ask questions in GitHub Discussions
- **Email**: Contact maintainers for sensitive matters

---

## Version History

| Date | Video | Version | Changes |
|------|-------|---------|---------|
| TBD  | OAuth Setup | v1.0 | Initial release |

---

**Last Updated**: 2026-06-25
**Maintainer**: Jason Anderson
