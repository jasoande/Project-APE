#!/usr/bin/env python3
"""
Utility functions for working with Project APE voiceovers
"""
import os
import subprocess
import json

def get_audio_duration(audio_file):
    """Get duration of an audio file in seconds using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        audio_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting duration for {audio_file}: {e}")
        return None

def get_video_duration(video_file):
    """Get duration of a video file in seconds using ffprobe"""
    return get_audio_duration(video_file)  # Same command works for video

def show_timing_report():
    """Display timing information for all generated files"""
    print("\n" + "=" * 60)
    print("TIMING REPORT")
    print("=" * 60)

    scenes = ['scene1', 'scene2', 'scene3']
    total_duration = 0

    for scene in scenes:
        audio_file = f'{scene}_voiceover.mp3'
        if os.path.exists(audio_file):
            duration = get_audio_duration(audio_file)
            if duration:
                total_duration += duration
                print(f"{scene:10s}: {duration:6.2f} seconds")
        else:
            print(f"{scene:10s}: NOT FOUND")

    print("-" * 60)
    print(f"{'Total':10s}: {total_duration:6.2f} seconds ({total_duration/60:.2f} minutes)")

    # Check combined file
    if os.path.exists('combined_voiceover.mp3'):
        combined_duration = get_audio_duration('combined_voiceover.mp3')
        if combined_duration:
            print(f"{'Combined':10s}: {combined_duration:6.2f} seconds")

    # Check video file if it exists
    video_files = [
        'media/videos/project_explainer/1080p60/ProjectExplainerFull.mp4',
        'media/videos/project_explainer/720p30/ProjectExplainerFull.mp4',
        'media/videos/project_explainer/480p15/ProjectExplainerFull.mp4',
        'media/videos/project_explainer/1080p60/Scene1_TitleIntro.mp4',
        'media/videos/project_explainer/720p30/Scene1_TitleIntro.mp4',
        'media/videos/project_explainer/480p15/Scene1_TitleIntro.mp4',
    ]

    for video_file in video_files:
        if os.path.exists(video_file):
            video_duration = get_video_duration(video_file)
            if video_duration:
                print(f"\nVideo file: {video_file}")
                print(f"Duration: {video_duration:.2f} seconds")
                if total_duration > 0:
                    diff = video_duration - total_duration
                    print(f"Difference from audio: {diff:+.2f} seconds")
            break

    print("=" * 60)

def merge_scene_audio_with_video(scene_name, video_file, audio_file, output_file):
    """Merge a single scene's audio with its video"""
    if not os.path.exists(video_file):
        print(f"Error: Video file not found: {video_file}")
        return False

    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return False

    print(f"Merging {scene_name}...")
    print(f"  Video: {video_file}")
    print(f"  Audio: {audio_file}")
    print(f"  Output: {output_file}")

    cmd = [
        'ffmpeg', '-y',  # Overwrite output
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Created {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")
        return False

def concatenate_videos(video_files, output_file):
    """Concatenate multiple video files into one"""
    # Create concat file
    concat_file = 'video_concat.txt'
    with open(concat_file, 'w') as f:
        for video in video_files:
            if os.path.exists(video):
                f.write(f"file '{video}'\n")

    print(f"Concatenating {len(video_files)} videos...")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Created {output_file}")
        os.remove(concat_file)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")
        return False

def check_dependencies():
    """Check if required tools are installed"""
    print("Checking dependencies...")

    dependencies = {
        'ffmpeg': 'ffmpeg -version',
        'ffprobe': 'ffprobe -version',
        'python': 'python3 --version'
    }

    all_ok = True
    for name, cmd in dependencies.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"  ✓ {name} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ✗ {name} is NOT installed")
            all_ok = False

    # Check for gTTS
    try:
        import gtts
        print(f"  ✓ gTTS is installed")
    except ImportError:
        print(f"  ✗ gTTS is NOT installed")
        print("    Install with: ~/.project-ape-venv/bin/pip install gTTS")
        all_ok = False

    return all_ok

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'check':
            check_dependencies()
        elif command == 'timing':
            show_timing_report()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: check, timing")
    else:
        print("Project APE Voiceover Utilities")
        print("\nAvailable commands:")
        print("  python voiceover_utils.py check   - Check dependencies")
        print("  python voiceover_utils.py timing  - Show timing report")
