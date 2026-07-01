#!/usr/bin/env python3
"""
Generate voiceover for Project APE explainer video using gTTS
"""
from gtts import gTTS
import os
import subprocess

# Voiceover scripts for each scene
scripts = {
    'scene1': """Welcome to Project APE, the AI-Powered Account Planning Engine.
Project APE automates company research using AI-generated insights.
It integrates seamlessly with Google Drive and provides a modern web-based interface.
Let's see how it works.""",

    'scene2': """Here's how Project APE transforms your data into actionable insights.
First, you upload company documents to a Google Drive folder.
Project APE then feeds these files to NotebookLM, Google's advanced AI research assistant.
NotebookLM analyzes your documents and generates comprehensive research.
Finally, Project APE consolidates everything into a professional account plan PDF.
The best part? It can process multiple clients simultaneously, saving you hours of manual work.""",

    'scene3': """Using Project APE is incredibly simple.
Open your web browser and navigate to localhost port 8765.
Configure your client information in the easy-to-use form.
Click the Start Workflow button and watch the magic happen.
The dashboard shows real-time progress for all your clients.
Within minutes, you'll have comprehensive account plans with quality scores.
Project APE: Turning data into intelligence, automatically."""
}

def generate_voiceovers():
    """Generate individual voiceover MP3 files for each scene"""
    print("Generating voiceover files...")

    for scene_name, text in scripts.items():
        output_file = f'{scene_name}_voiceover.mp3'
        print(f"  Creating {output_file}...")

        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_file)

        print(f"  ✓ Generated {output_file}")

    print("\nVoiceover generation complete!")
    return list(scripts.keys())

def create_concat_file(scene_names):
    """Create ffmpeg concat file for merging all voiceovers"""
    concat_content = "\n".join([f"file '{scene}_voiceover.mp3'" for scene in scene_names])

    with open('voiceover_concat.txt', 'w') as f:
        f.write(concat_content)

    print("Created voiceover_concat.txt for ffmpeg")

def merge_voiceovers(scene_names):
    """Merge all voiceover files into a single MP3"""
    print("\nMerging voiceover files...")

    create_concat_file(scene_names)

    cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', 'voiceover_concat.txt',
        '-c', 'copy',
        'combined_voiceover.mp3'
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("✓ Created combined_voiceover.mp3")
    except subprocess.CalledProcessError as e:
        print(f"Error merging voiceovers: {e.stderr.decode()}")
        raise

def merge_with_video(video_path=None,
                     audio_path='combined_voiceover.mp3',
                     output_path='project_ape_explainer_with_audio.mp4'):
    """Merge the combined voiceover with the video"""
    print("\nMerging audio with video...")

    # Auto-detect video path if not provided
    if video_path is None:
        possible_paths = [
            'media/videos/project_explainer/1080p60/ProjectExplainerFull.mp4',
            'media/videos/project_explainer/720p30/ProjectExplainerFull.mp4',
            'media/videos/project_explainer/480p15/ProjectExplainerFull.mp4',
            'media/videos/project_explainer/1080p60/Scene1_TitleIntro.mp4',
            'media/videos/project_explainer/720p30/Scene1_TitleIntro.mp4',
            'media/videos/project_explainer/480p15/Scene1_TitleIntro.mp4',
        ]

        for path in possible_paths:
            if os.path.exists(path):
                video_path = path
                print(f"  Found video: {video_path}")
                break

        if video_path is None:
            print("Error: No video file found. Checked:")
            for path in possible_paths:
                print(f"  - {path}")
            return False

    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return False

    cmd = [
        'ffmpeg', '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Created {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error merging video: {e.stderr.decode()}")
        raise

def main():
    """Main execution flow"""
    print("=" * 60)
    print("Project APE Voiceover Generator")
    print("=" * 60)

    # Step 1: Generate individual voiceovers
    scene_names = generate_voiceovers()

    # Step 2: Merge all voiceovers into one file
    merge_voiceovers(scene_names)

    # Step 3: Merge combined voiceover with video
    success = merge_with_video()

    if success:
        print("\n" + "=" * 60)
        print("SUCCESS! Video with voiceover is ready:")
        print("  → project_ape_explainer_with_audio.mp4")
        print("=" * 60)

    # Display scene timing information
    print("\nScene Timing Information:")
    print("  Scene 1: ~30 seconds (Introduction)")
    print("  Scene 2: ~50 seconds (How it works)")
    print("  Scene 3: ~40 seconds (Using Project APE)")
    print("  Total: ~120 seconds (2 minutes)")

if __name__ == '__main__':
    main()
