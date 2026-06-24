#!/bin/bash
################################################################################
# Quick Fix: Recreate NotebookLM Credentials Volume with Correct UID
# Run this if you get "Authentication required - please run: notebooklm login"
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================================================"
echo "FIX: NotebookLM Credentials Volume UID Compatibility"
echo "========================================================================"
echo
echo "This script fixes the 'Authentication required' error by recreating"
echo "the NotebookLM credentials volume with the correct UID mapping."
echo

CREDS_VOLUME="project-ape-credentials"

# Check if volume exists
if ! podman volume exists ${CREDS_VOLUME} 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Volume '${CREDS_VOLUME}' does not exist${NC}"
    echo "Running setup-credentials.sh to create it..."
    ./setup-credentials.sh
    exit 0
fi

echo -e "${BLUE}Found existing volume: ${CREDS_VOLUME}${NC}"
echo
echo "Removing old volume and recreating with correct UID mapping..."
echo

# Remove old volume
podman volume rm ${CREDS_VOLUME}
echo -e "${GREEN}✅ Old volume removed${NC}"

# Recreate with setup-credentials.sh
echo
echo "Recreating credentials volume..."
./setup-credentials.sh

echo
echo "========================================================================"
echo -e "${GREEN}✅ FIX COMPLETE${NC}"
echo "========================================================================"
echo
echo "NotebookLM credentials volume recreated with correct UID."
echo
echo "You can now run:"
echo "  ${GREEN}./launch_ape.sh fast${NC}"
echo
