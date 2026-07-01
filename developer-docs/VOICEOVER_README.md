# Project APE Voiceover Generation

This system generates AI voiceover narration for the Project APE explainer video and merges it with the rendered video.

## Quick Start

```bash
chmod +x create-voiceover.sh
./create-voiceover.sh
```

This will:
1. Install gTTS (Google Text-to-Speech)
2. Generate voiceover audio for all 3 scenes
3. Merge audio files together
4. Overlay combined audio onto the video
5. Output: `project_ape_explainer_with_audio.mp4`

## Manual Steps

If you prefer to run steps individually:

### 1. Install gTTS
```bash
~/.project-ape-venv/bin/pip install gTTS
```

### 2. Generate voiceover and merge
```bash
~/.project-ape-venv/bin/python3 generate_voiceover.py
```

## Scene Scripts

### Scene 1: Introduction (30 seconds)
- Introduces Project APE
- Highlights key features
- Sets the stage

### Scene 2: How It Works (50 seconds)
- Explains the workflow
- Shows integration with Google Drive and NotebookLM
- Emphasizes automation benefits

### Scene 3: Using Project APE (40 seconds)
- Demonstrates the web interface
- Shows dashboard features
- Concludes with value proposition

## Generated Files

- `scene1_voiceover.mp3` - Introduction narration
- `scene2_voiceover.mp3` - How it works narration
- `scene3_voiceover.mp3` - Usage demonstration narration
- `combined_voiceover.mp3` - All scenes merged
- `voiceover_concat.txt` - FFmpeg concat file (intermediate)
- `project_ape_explainer_with_audio.mp4` - **Final output**

## Customization

### Adjust Speech Rate
Edit `generate_voiceover.py` and change:
```python
tts = gTTS(text=text, lang='en', slow=False)  # Change to slow=True for slower speech
```

### Modify Scripts
Edit the `scripts` dictionary in `generate_voiceover.py`:
```python
scripts = {
    'scene1': """Your custom text here...""",
    'scene2': """Your custom text here...""",
    'scene3': """Your custom text here..."""
}
```

### Change Video Path
Modify the `merge_with_video()` call in `generate_voiceover.py`:
```python
merge_with_video(
    video_path='path/to/your/video.mp4',
    output_path='your_output_name.mp4'
)
```

## Timing Considerations

- **Scene 1**: ~30 seconds
- **Scene 2**: ~50 seconds  
- **Scene 3**: ~40 seconds
- **Total**: ~120 seconds (2 minutes)

The `-shortest` flag in ffmpeg ensures the output duration matches whichever is shorter (video or audio).

## Requirements

- Python 3.x
- gTTS library
- ffmpeg (must be installed on your system)
- Input video: `media/videos/project_explainer/1080p60/ProjectExplainerFull.mp4`

## Troubleshooting

### ffmpeg not found
Install ffmpeg:
```bash
brew install ffmpeg  # macOS
```

### Video file not found
Check that the Manim rendering completed successfully and the video exists at:
```
media/videos/project_explainer/1080p60/ProjectExplainerFull.mp4
```

### Audio too fast/slow
Adjust the `slow` parameter in `generate_voiceover.py` or add pauses in the script text.

### Audio/video sync issues
The current setup assumes the video duration matches the script duration (~120 seconds). If there's a mismatch:
- Adjust video length in Manim scenes
- Modify script text to be shorter/longer
- Add silence/pauses between scenes

## Audio Quality

gTTS provides good quality AI-generated speech for:
- Clear pronunciation
- Natural cadence
- Consistent tone

For production use, consider:
- Professional voice actors
- Higher-quality TTS services (AWS Polly, Google Cloud TTS)
- Audio post-processing (normalization, compression)
