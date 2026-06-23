#!/bin/bash
################################################################################
# Quick Fix: Install Google API Libraries
# Run this if share-drive-folders.py fails with "No module named 'google'"
################################################################################

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo "Installing Google Drive API libraries..."

# Check if venv is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source ./activate-ape-env.sh
fi

# Install Google API libraries
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

echo
echo -e "${GREEN}✅ Google API libraries installed${NC}"
echo
echo "You can now run:"
echo "  ./share-drive-folders.py"
echo "  or"
echo "  ./setup.sh"
echo
