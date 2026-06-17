#!/bin/bash
################################################################################
# Project APE - Mac ARM64 Image Builder
# Builds arm64 container image for Mac development
################################################################################

set -e

VERSION="${1:-latest}"
REGISTRY="quay.io/jasoande/project_ape"
IMAGE_NAME="project-ape"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================================================"
echo "  PROJECT APE - MAC ARM64 IMAGE BUILD"
echo "========================================================================"
echo
echo "Building: ${IMAGE_NAME}:${VERSION}"
echo "Architecture: arm64 (Apple Silicon)"
echo "Registry: ${REGISTRY}"
echo

# Verify we're on Mac
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not running on macOS${NC}"
    echo "This script is intended for Mac (arm64) builds"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify Containerfile exists
if [ ! -f "Containerfile" ]; then
    echo -e "${YELLOW}❌ Containerfile not found${NC}"
    echo "Run this script from the Project-APE directory"
    exit 1
fi

# Verify critical files exist
echo "Verifying build context..."
for file in main.py requirements.txt container-entrypoint.sh; do
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}❌ Missing required file: $file${NC}"
        exit 1
    fi
done

for dir in core dashboard; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}❌ Missing required directory: $dir${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Build context verified${NC}"
echo

# Build image
echo "========================================================================"
echo "BUILDING IMAGE"
echo "========================================================================"
echo

podman build --no-cache \
    --platform linux/arm64 \
    -t localhost/${IMAGE_NAME}:${VERSION} \
    -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
    -f Containerfile .

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}❌ Build failed${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✅ Build completed successfully${NC}"
echo

# Test image
echo "========================================================================"
echo "TESTING IMAGE"
echo "========================================================================"
echo

echo "Testing Python version..."
podman run --rm localhost/${IMAGE_NAME}:${VERSION} python3 --version

echo
echo "Testing NotebookLM CLI..."
podman run --rm -e HOME=/home/apeuser localhost/${IMAGE_NAME}:${VERSION} \
    /opt/venv/bin/notebooklm --version 2>&1 | head -5 || echo "CLI check skipped"

echo
echo "Verifying directory structure..."
podman run --rm localhost/${IMAGE_NAME}:${VERSION} ls -la /app/ | head -10

echo
echo -e "${GREEN}✅ Image tests passed${NC}"
echo

# Show image info
echo "========================================================================"
echo "IMAGE INFORMATION"
echo "========================================================================"
podman images | grep "${IMAGE_NAME}.*${VERSION}"
echo

# Push to registry
echo "========================================================================"
echo "REGISTRY PUSH"
echo "========================================================================"
echo
echo "Push image to registry?"
echo "  ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo
read -p "Push to quay.io? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if logged in
    if ! podman login quay.io --get-login &>/dev/null; then
        echo "Not logged in to quay.io"
        echo "Logging in..."
        podman login quay.io
    fi

    echo "Pushing image..."
    podman push ${REGISTRY}/${IMAGE_NAME}:${VERSION}

    if [ $? -eq 0 ]; then
        echo
        echo -e "${GREEN}✅ Image pushed successfully${NC}"
        echo
        echo "Image available at:"
        echo "  ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    else
        echo -e "${YELLOW}❌ Push failed${NC}"
        exit 1
    fi
else
    echo "Skipping registry push"
    echo
    echo "To push later, run:"
    echo "  podman push ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
fi

echo
echo "========================================================================"
echo "BUILD COMPLETE"
echo "========================================================================"
echo
echo "Local image: localhost/${IMAGE_NAME}:${VERSION}"
echo "Registry image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo
echo "To test locally:"
echo "  ./launch_ape.sh fast"
echo
