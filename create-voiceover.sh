#!/bin/bash
# Create voiceover and merge with Project APE explainer video

set -e  # Exit on error

echo "=========================================="
echo "Project APE Voiceover Creation"
echo "=========================================="
echo ""

# Step 1: Install gTTS if not already installed
echo "Step 1: Installing gTTS..."
~/.project-ape-venv/bin/pip install gTTS -q

# Step 2: Run the voiceover generation script
echo ""
echo "Step 2: Generating voiceover and merging with video..."
~/.project-ape-venv/bin/python3 generate_voiceover.py

echo ""
echo "=========================================="
echo "Done! Check project_ape_explainer_with_audio.mp4"
echo "=========================================="
