#!/bin/bash
################################################################################
# Project APE - Cache Volume Setup (Optional)
# Creates a persistent volume for drive cache and industry detection cache
# This improves performance by caching:
#   - Google Drive file downloads
#   - Industry detection results
################################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VOLUME_NAME="project-ape-cache"

echo "========================================================================"
echo "PROJECT APE - CACHE VOLUME SETUP (Optional)"
echo "========================================================================"
echo
echo "This creates a persistent cache volume for:"
echo "  • Google Drive file downloads (faster subsequent runs)"
echo "  • Industry detection results (avoid re-detection)"
echo
echo "Benefits:"
echo "  • Faster pipeline execution on repeat runs"
echo "  • Reduced API calls to Google Drive"
echo "  • Persistent cache across container restarts"
echo
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi
echo

# Detect runtime
if command -v podman &> /dev/null; then
    RUNTIME="podman"
elif command -v docker &> /dev/null; then
    RUNTIME="docker"
else
    echo "ERROR: Neither podman nor docker found"
    exit 1
fi

# Create volume if needed
if $RUNTIME volume exists ${VOLUME_NAME} 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Volume '${VOLUME_NAME}' already exists"
    read -p "Recreate (will clear cache)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $RUNTIME volume rm ${VOLUME_NAME}
    else
        echo "Using existing cache volume"
        exit 0
    fi
fi

echo -e "${GREEN}✓${NC} Creating cache volume: ${VOLUME_NAME}"
$RUNTIME volume create ${VOLUME_NAME}

echo
echo "========================================================================"
echo -e "${GREEN}✅ Cache volume configured successfully!${NC}"
echo "========================================================================"
echo
echo "Volume '${VOLUME_NAME}' is ready."
echo
echo "The cache will be automatically used by launch_ape.sh"
echo
echo "To clear cache in the future:"
echo "  $RUNTIME volume rm ${VOLUME_NAME}"
echo "  ./setup-cache.sh"
echo
