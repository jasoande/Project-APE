#!/bin/bash
# Project APE - Credential Volume Setup
# Copies your host NotebookLM credentials to a persistent volume

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VOLUME_NAME="project-ape-credentials"
HOST_CREDS="${HOME}/.notebooklm"

echo "========================================================================"
echo "PROJECT APE - CREDENTIAL SETUP"
echo "========================================================================"
echo

# Check if host credentials exist
if [ ! -d "${HOST_CREDS}/profiles/default" ]; then
    echo -e "${RED}✗${NC} NotebookLM credentials not found on host"
    echo
    echo "Please authenticate first:"
    echo "  pip install notebooklm-py"
    echo "  notebooklm login"
    echo
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✓${NC} Found NotebookLM credentials on host"

# Create volume if needed
if podman volume exists ${VOLUME_NAME} 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Volume '${VOLUME_NAME}' already exists"
    read -p "Overwrite credentials? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
    podman volume rm ${VOLUME_NAME}
fi

echo -e "${GREEN}✓${NC} Creating volume: ${VOLUME_NAME}"
podman volume create ${VOLUME_NAME}

# Make credentials readable temporarily
echo "Preparing credentials for copy..."
chmod -R a+rX "${HOST_CREDS}" 2>/dev/null || true

# Copy credentials to volume using a temporary container
echo "Copying credentials to persistent volume..."
podman run --rm \
    -v "${HOST_CREDS}:/source:ro,z" \
    -v "${VOLUME_NAME}:/dest" \
    quay.io/jasoande/project_ape/project-ape:latest \
    bash -c "cp -a /source/. /dest/ && chmod -R 700 /dest && ls -la /dest/profiles/default/storage_state.json && echo 'Credentials copied successfully'"

# Restore original permissions
chmod 700 "${HOST_CREDS}" "${HOST_CREDS}/profiles" "${HOST_CREDS}/profiles/default" 2>/dev/null || true

if [ $? -eq 0 ]; then
    echo
    echo "========================================================================"
    echo -e "${GREEN}✅ Credentials configured successfully!${NC}"
    echo "========================================================================"
    echo
    echo "Volume '${VOLUME_NAME}' is ready to use."
    echo
    echo "Run workflows with:"
    echo "  ./ape-run.sh --vars ./vars.py --clients yourclient --mode fast"
    echo
else
    echo
    echo "========================================================================"
    echo -e "${RED}❌ Setup failed${NC}"
    echo "========================================================================"
    exit 1
fi
