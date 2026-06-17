#!/bin/bash
################################################################################
# Project APE Container Entrypoint
# Sets up environment and launches the application
################################################################################

set -e

# Verify required files are mounted
if [ ! -f "/app/.env" ]; then
    echo "ERROR: .env file not found"
    echo "Mount it with: -v \$(pwd)/.env:/app/.env:ro"
    exit 1
fi

if [ ! -f "/app/vars.py" ]; then
    echo "ERROR: vars.py file not found"
    echo "Mount it with: -v \$(pwd)/vars.py:/app/vars.py:ro"
    exit 1
fi

if [ ! -f "/app/service-account.json" ]; then
    echo "WARNING: service-account.json not found"
    echo "Google Drive access will not work"
    echo "Mount it with: -v \$(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro"
fi

# Load environment variables
export $(grep -v '^#' /app/.env | xargs)

# Ensure log directory exists and is writable
mkdir -p /app/logs /app/.multi_process_status
chmod 755 /app/logs /app/.multi_process_status

# Execute the provided command
exec "$@"
