# Project APE Voiceover System - Complete Guide

## Overview

This system generates professional AI voiceover narration for your Project APE explainer video using Google Text-to-Speech (gTTS) and merges it with Manim-rendered video using ffmpeg.

## Quick Start (Recommended)

```bash
# Make the script executable
chmod +x create-voiceover.sh

# Run the complete pipeline
./create-voiceover.sh
```

This single command will:
1. Install gTTS (if needed)
2. Generate voiceover for all 3 scenes
3. Merge audio files together
4. Overlay audio onto your video
5. Output: `project_ape_explainer_with_audio.mp4`

## Files Created

### Core Scripts
- `generate_voiceover.py` - Main voiceover generation script
- `create-voiceover.sh` - One-command execution wrapper
- `voiceover_utils.py` - Utility functions for timing checks and diagnostics

### Generated Audio Files
- `scene1_voiceover.mp3` - Scene 1 narration (~30 seconds)
- `scene2_voiceover.mp3` - Scene 2 narration (~50 seconds)
- `scene3_voiceover.mp3` - Scene 3 narration (~40 seconds)
- `combined_voiceover.mp3` - All scenes merged together
- `voiceover_concat.txt` - FFmpeg concat file (intermediate)

### Final Output
- `project_ape_explainer_with_audio.mp4` - Complete video with voiceover

## Manual Step-by-Step

### Step 1: Install Dependencies

```bash
# Install gTTS
~/.project-ape-venv/bin/pip install gTTS

# Verify ffmpeg is installed (required for audio/video merging)
ffmpeg -version

# If ffmpeg not installed on macOS:
brew install ffmpeg
```

### Step 2: Check Dependencies

```bash
~/.project-ape-venv/bin/python3 voiceover_utils.py check
```

This will verify:
- ffmpeg is installed
- ffprobe is installed
- Python 3 is available
- gTTS library is installed

### Step 3: Generate Voiceover

```bash
~/.project-ape-venv/bin/python3 generate_voiceover.py
```

This will:
- Create MP3 files for each scene
- Merge them into `combined_voiceover.mp3`
- Automatically find your rendered video
- Merge audio with video
- Create final output

### Step 4: Check Timing

```bash
~/.project-ape-venv/bin/python3 voiceover_utils.py timing
```

This displays:
- Duration of each scene's audio
- Total audio duration
- Video duration (if found)
- Timing differences

## Scene Scripts

### Scene 1: Introduction (Target: 30 seconds)
```
Welcome to Project APE, the AI-Powered Account Planning Engine.
Project APE automates company research using AI-generated insights.
It integrates seamlessly with Google Drive and provides a modern web-based interface.
Let's see how it works.
```

### Scene 2: How It Works (Target: 50 seconds)
```
Here's how Project APE transforms your data into actionable insights.
First, you upload company documents to a Google Drive folder.
Project APE then feeds these files to NotebookLM, Google's advanced AI research assistant.
NotebookLM analyzes your documents and generates comprehensive research.
Finally, Project APE consolidates everything into a professional account plan PDF.
The best part? It can process multiple clients simultaneously, saving you hours of manual work.
```

### Scene 3: Using Project APE (Target: 40 seconds)
```
Using Project APE is incredibly simple.
Open your web browser and navigate to localhost port 8765.
Configure your client information in the easy-to-use form.
Click the Start Workflow button and watch the magic happen.
The dashboard shows real-time progress for all your clients.
Within minutes, you'll have comprehensive account plans with quality scores.
Project APE: Turning data into intelligence, automatically.
```

## Customization

### Adjust Speech Rate

Edit `generate_voiceover.py`:

```python
# For normal speed (default)
tts = gTTS(text=text, lang='en', slow=False)

# For slower, more deliberate speech
tts = gTTS(text=text, lang='en', slow=True)
```

### Modify Script Text

Edit `generate_voiceover.py` and update the `scripts` dictionary:

```python
scripts = {
    'scene1': """Your custom text for scene 1...""",
    'scene2': """Your custom text for scene 2...""",
    'scene3': """Your custom text for scene 3..."""
}
```

### Add Pauses

Insert pauses in the script by adding periods and spaces:

```python
'scene1': """Welcome to Project APE. . . The AI-Powered Account Planning Engine."""
          # The extra periods create brief pauses
```

### Use Different Voice Language

gTTS supports multiple languages:

```python
tts = gTTS(text=text, lang='en')  # English (default)
tts = gTTS(text=text, lang='es')  # Spanish
tts = gTTS(text=text, lang='fr')  # French
tts = gTTS(text=text, lang='de')  # German
```

### Specify Custom Video Path

```bash
# Edit generate_voiceover.py, modify the merge_with_video() call:
success = merge_with_video(
    video_path='path/to/your/custom/video.mp4',
    output_path='custom_output_name.mp4'
)
```

## Video Auto-Detection

The script automatically searches for your rendered video in this order:

1. `media/videos/project_explainer/1080p60/ProjectExplainerFull.mp4`
2. `media/videos/project_explainer/720p30/ProjectExplainerFull.mp4`
3. `media/videos/project_explainer/480p15/ProjectExplainerFull.mp4`
4. `media/videos/project_explainer/1080p60/Scene1_TitleIntro.mp4`
5. `media/videos/project_explainer/720p30/Scene1_TitleIntro.mp4`
6. `media/videos/project_explainer/480p15/Scene1_TitleIntro.mp4`

It uses the first video file it finds.

## Troubleshooting

### Error: "ffmpeg not found"

**Solution:** Install ffmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version
```

### Error: "No module named 'gtts'"

**Solution:** Install gTTS in the virtual environment
```bash
~/.project-ape-venv/bin/pip install gTTS
```

### Error: "Video file not found"

**Cause:** The Manim video hasn't been rendered yet.

**Solution:** Render the video first using Manim:
```bash
# Render at 1080p60 (high quality)
manim -pqh project_explainer.py ProjectExplainerFull

# Or render at 480p15 (faster)
manim -pql project_explainer.py ProjectExplainerFull
```

### Audio/Video Out of Sync

**Symptoms:** Audio doesn't match video timing

**Solutions:**
1. Check actual timing:
   ```bash
   ~/.project-ape-venv/bin/python3 voiceover_utils.py timing
   ```

2. Adjust script length (add/remove text)

3. Modify Manim scene durations to match audio

4. Add explicit pauses in the script:
   ```python
   """Text here. . . . Pause. . . . More text."""
   ```

### Audio Too Fast/Too Slow

**Solution 1:** Change speech rate
```python
tts = gTTS(text=text, lang='en', slow=True)  # Slower
```

**Solution 2:** Adjust the audio speed with ffmpeg
```bash
# Speed up 1.25x
ffmpeg -i combined_voiceover.mp3 -filter:a "atempo=1.25" faster_audio.mp3

# Slow down to 0.75x
ffmpeg -i combined_voiceover.mp3 -filter:a "atempo=0.75" slower_audio.mp3
```

### Low Audio Volume

**Solution:** Normalize audio volume
```bash
ffmpeg -i combined_voiceover.mp3 -filter:a "volume=2.0" louder_audio.mp3
```

Then use `louder_audio.mp3` for merging with video.

## Advanced Usage

### Generate Only Audio (No Video Merge)

Edit `generate_voiceover.py` and comment out the video merge:

```python
def main():
    # Generate voiceovers
    scene_names = generate_voiceovers()

    # Merge audio files
    merge_voiceovers(scene_names)

    # Skip video merge
    # success = merge_with_video()

    print("Audio generation complete!")
```

### Work with Individual Scenes

```python
from voiceover_utils import merge_scene_audio_with_video

# Merge just scene 1
merge_scene_audio_with_video(
    scene_name='scene1',
    video_file='media/videos/project_explainer/480p15/Scene1_TitleIntro.mp4',
    audio_file='scene1_voiceover.mp3',
    output_file='scene1_with_audio.mp4'
)
```

### Concatenate Scene Videos

If you have separate scene videos with audio:

```python
from voiceover_utils import concatenate_videos

videos = [
    'scene1_with_audio.mp4',
    'scene2_with_audio.mp4',
    'scene3_with_audio.mp4'
]

concatenate_videos(videos, 'complete_video.mp4')
```

## Audio Quality Considerations

### gTTS (Current Solution)
**Pros:**
- Free and unlimited
- Simple to use
- No API keys required
- Good pronunciation
- Consistent quality

**Cons:**
- Robotic voice
- Limited emotion/inflection
- Cannot adjust tone or pitch
- Single voice option per language

### Alternatives for Production

For higher quality voiceovers, consider:

1. **Professional Voice Actors**
   - Highest quality
   - Natural emotion
   - Expensive and time-consuming

2. **AWS Polly**
   - Neural voices (very natural)
   - Multiple voice options
   - Requires AWS account
   - Pay per character

3. **Google Cloud Text-to-Speech**
   - WaveNet voices (high quality)
   - Multiple languages/voices
   - Requires Google Cloud account
   - Pay per character

4. **ElevenLabs**
   - Very natural AI voices
   - Voice cloning available
   - Subscription required
   - Excellent quality

5. **Record Yourself**
   - Free
   - Personal touch
   - Requires audio equipment
   - Time-intensive

## Best Practices

1. **Preview before finalizing**
   - Listen to generated MP3s before merging
   - Check timing with `voiceover_utils.py timing`

2. **Match video length**
   - Ensure total audio ≈ total video duration
   - Use `-shortest` flag (already in script)

3. **Script writing tips**
   - Write for listening, not reading
   - Use short, clear sentences
   - Avoid complex jargon
   - Add natural pauses with punctuation

4. **Testing workflow**
   - Test with one scene first
   - Verify audio quality
   - Then generate all scenes

5. **Version control**
   - Keep script text in version control
   - Track changes to narration
   - Save different versions for A/B testing

## Technical Details

### FFmpeg Command Explanation

```bash
ffmpeg -i video.mp4 -i audio.mp3 \
       -c:v copy \              # Copy video codec (no re-encoding)
       -c:a aac \               # Encode audio as AAC
       -map 0:v:0 \             # Use video from first input
       -map 1:a:0 \             # Use audio from second input
       -shortest \              # End when shortest stream ends
       output.mp4
```

### Why `-shortest`?

Ensures the output duration matches whichever is shorter (video or audio). This prevents:
- Black screen if audio is longer
- Silent video if audio is shorter

### Audio Codec Choice (AAC)

AAC is chosen because:
- Universal compatibility
- Good quality at low bitrates
- Supported by all modern players
- Standard for MP4 containers

## Environment

- **Working Directory:** `/Users/jasona/test/Project-APE-dev`
- **Virtual Environment:** `~/.project-ape-venv`
- **Python:** 3.x
- **Video Input:** `media/videos/project_explainer/*/ProjectExplainerFull.mp4`
- **Final Output:** `project_ape_explainer_with_audio.mp4`

## Support

If you encounter issues:

1. Run dependency check:
   ```bash
   ~/.project-ape-venv/bin/python3 voiceover_utils.py check
   ```

2. Check timing:
   ```bash
   ~/.project-ape-venv/bin/python3 voiceover_utils.py timing
   ```

3. Verify files exist:
   ```bash
   ls -lh *.mp3 *.mp4
   ```

4. Check video was rendered:
   ```bash
   find media/videos -name "*.mp4" | grep -v partial
   ```

## Next Steps

After creating your voiceover video:

1. **Review the output**
   ```bash
   open project_ape_explainer_with_audio.mp4
   ```

2. **Share it**
   - Upload to YouTube
   - Embed in documentation
   - Include in presentations

3. **Iterate**
   - Adjust script based on feedback
   - Re-render with changes
   - Test different narration styles

## License

This voiceover system is part of Project APE and follows the same license.
