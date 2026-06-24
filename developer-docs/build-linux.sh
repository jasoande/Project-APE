#!/bin/bash
################################################################################
# Project APE - Linux AMD64 Image Builder
# Builds amd64 container image for Linux production (EC2, RHEL9)
################################################################################

set -e

VERSION="${1:-3.0.5-amd64}"
REGISTRY="quay.io/jasoande/project_ape"
IMAGE_NAME="project-ape"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================================================"
echo "  PROJECT APE - LINUX AMD64 IMAGE BUILD"
echo "========================================================================"
echo
echo "Building: ${IMAGE_NAME}:${VERSION}"
echo "Architecture: amd64 (x86_64)"
echo "Registry: ${REGISTRY}"
echo

# Verify we're on Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: Running on macOS${NC}"
    echo "This script is intended for Linux (amd64) builds"
    echo "Building on Mac will create an arm64 image, not amd64"
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
    --platform linux/amd64 \
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

# Verify architecture
echo "Verifying image architecture..."
ARCH=$(podman inspect localhost/${IMAGE_NAME}:${VERSION} | grep -i architecture | head -1)
echo "  ${ARCH}"

if echo "${ARCH}" | grep -q "amd64"; then
    echo -e "${GREEN}✅ Correct architecture (amd64)${NC}"
elif echo "${ARCH}" | grep -q "arm64"; then
    echo -e "${YELLOW}⚠️  Warning: Image is arm64, not amd64${NC}"
    echo "This image was built on Mac, not Linux"
    echo "It will NOT work on x86_64 EC2 instances"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

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
        echo
        echo "EC2 instances will now pull this version"
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
echo "To update version in launch_ape.sh:"
echo "  Edit line 25: echo \"${VERSION}\""
echo
