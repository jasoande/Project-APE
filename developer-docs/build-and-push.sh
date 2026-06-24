#!/bin/bash
################################################################################
# Project APE - Multi-Architecture Container Build & Push Script
# Builds ARM64 and AMD64 containers, creates manifest, pushes to Quay.io
################################################################################

set -e  # Exit on error

# Configuration
REGISTRY="quay.io/jasoande/project_ape"
IMAGE_NAME="project-ape"
VERSION="3.2.1"  # v3.2.1: Critical fix - deep mode retries auth failures, pipeline halts on research failure
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINERFILE="${SCRIPT_DIR}/Containerfile"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Project APE Container Build & Push${NC}"
echo -e "${BLUE}Version: ${VERSION}${NC}"
echo -e "${BLUE}========================================${NC}"

# Verify Containerfile exists
if [ ! -f "$CONTAINERFILE" ]; then
    echo -e "${RED}ERROR: Containerfile not found at $CONTAINERFILE${NC}"
    exit 1
fi

# Verify we're logged into Quay.io
echo -e "\n${YELLOW}Checking registry authentication...${NC}"
if ! podman login quay.io --get-login &>/dev/null; then
    echo -e "${RED}ERROR: Not logged into quay.io${NC}"
    echo "Run: podman login quay.io"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated to quay.io${NC}"

# Build ARM64 image
echo -e "\n${YELLOW}Building ARM64 image...${NC}"
podman build \
    --platform linux/arm64 \
    -f "$CONTAINERFILE" \
    -t localhost/${IMAGE_NAME}:${VERSION}-arm64 \
    -t ${REGISTRY}/${IMAGE_NAME}:${VERSION}-arm64 \
    .

echo -e "${GREEN}✓ ARM64 build complete${NC}"

# Build AMD64 image
echo -e "\n${YELLOW}Building AMD64 image...${NC}"
podman build \
    --platform linux/amd64 \
    -f "$CONTAINERFILE" \
    -t localhost/${IMAGE_NAME}:${VERSION}-amd64 \
    -t ${REGISTRY}/${IMAGE_NAME}:${VERSION}-amd64 \
    .

echo -e "${GREEN}✓ AMD64 build complete${NC}"

# Push ARM64 image
echo -e "\n${YELLOW}Pushing ARM64 image...${NC}"
podman push ${REGISTRY}/${IMAGE_NAME}:${VERSION}-arm64
echo -e "${GREEN}✓ ARM64 image pushed${NC}"

# Push AMD64 image
echo -e "\n${YELLOW}Pushing AMD64 images...${NC}"
podman push ${REGISTRY}/${IMAGE_NAME}:${VERSION}-amd64
echo -e "${GREEN}✓ AMD64 image pushed${NC}"

# Create and push multi-arch manifest
echo -e "\n${YELLOW}Creating multi-architecture manifest...${NC}"

# Remove old manifest if it exists
podman manifest rm ${REGISTRY}/${IMAGE_NAME}:${VERSION} 2>/dev/null || true
podman manifest rm ${REGISTRY}/${IMAGE_NAME}:latest 2>/dev/null || true

# Create new manifests
podman manifest create ${REGISTRY}/${IMAGE_NAME}:${VERSION}
podman manifest create ${REGISTRY}/${IMAGE_NAME}:latest

# Add images to version-specific manifest
podman manifest add ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
    ${REGISTRY}/${IMAGE_NAME}:${VERSION}-arm64

podman manifest add ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
    ${REGISTRY}/${IMAGE_NAME}:${VERSION}-amd64

# Add images to latest manifest
podman manifest add ${REGISTRY}/${IMAGE_NAME}:latest \
    ${REGISTRY}/${IMAGE_NAME}:${VERSION}-arm64

podman manifest add ${REGISTRY}/${IMAGE_NAME}:latest \
    ${REGISTRY}/${IMAGE_NAME}:${VERSION}-amd64

echo -e "${GREEN}✓ Multi-arch manifests created${NC}"

# Push manifests
echo -e "\n${YELLOW}Pushing manifests...${NC}"
podman manifest push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
podman manifest push ${REGISTRY}/${IMAGE_NAME}:latest
echo -e "${GREEN}✓ Manifests pushed${NC}"

# Verify
echo -e "\n${YELLOW}Verifying multi-arch manifest...${NC}"
podman manifest inspect ${REGISTRY}/${IMAGE_NAME}:${VERSION} | \
    python3 -c "import sys, json; data = json.load(sys.stdin); print('Architectures:', [m['platform']['architecture'] for m in data['manifests']])"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Version: ${VERSION}"
echo -e "Registry: ${REGISTRY}/${IMAGE_NAME}"
echo -e ""
echo -e "Tagged images:"
echo -e "  - ${REGISTRY}/${IMAGE_NAME}:${VERSION}-arm64"
echo -e "  - ${REGISTRY}/${IMAGE_NAME}:${VERSION}-amd64"
echo -e "  - ${REGISTRY}/${IMAGE_NAME}:${VERSION} (multi-arch)"
echo -e "  - ${REGISTRY}/${IMAGE_NAME}:latest (multi-arch)"
echo -e ""
echo -e "${BLUE}To use:${NC}"
echo -e "  podman pull ${REGISTRY}/${IMAGE_NAME}:latest"
echo -e ""
echo -e "${BLUE}To run:${NC}"
echo -e "  podman run --rm \\"
echo -e "    -v \$(pwd)/.env:/app/.env:ro \\"
echo -e "    -v \$(pwd)/vars.py:/app/vars.py:ro \\"
echo -e "    -v \$(pwd)/service-account.json:/app/service-account.json:ro \\"
echo -e "    -p 8765:8765 \\"
echo -e "    ${REGISTRY}/${IMAGE_NAME}:latest python3 main.py --mode fast"
echo -e ""
