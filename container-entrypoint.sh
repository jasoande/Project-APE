#!/bin/bash
################################################################################
# Account Intelligence - Container Entrypoint
# Sets up environment and launches the application
################################################################################

set -e

echo "=========================================="
echo "Account Intelligence Container Starting"
echo "=========================================="
echo

# Verify required files are mounted
echo "Checking required mounts..."

if [ ! -f "/app/vars.py" ]; then
    echo "❌ ERROR: vars.py file not found"
    echo "   Mount it with: -v \$(pwd)/vars.py:/app/vars.py:ro,z"
    exit 1
fi
echo "✅ vars.py found"

# Check for optional .env file
if [ -f "/app/.env" ]; then
    echo "✅ .env file found - loading environment variables"
    export $(grep -v '^#' /app/.env | xargs)
else
    echo "⚠️  No .env file found (optional)"
fi

# Check for NotebookLM credentials (optional - can be set up later)
if [ -f "$HOME/.notebooklm/credentials.json" ]; then
    echo "✅ NotebookLM credentials found"
else
    echo "⚠️  NotebookLM credentials not found"
    echo "   Authenticate with: notebooklm login"
    echo "   Or mount with: -v ~/.notebooklm:/opt/app-root/src/.notebooklm:ro,z"
fi

# Check for Drive OAuth token (optional - can be set up later)
if [ -f "/app/credentials/token_drive.json" ]; then
    echo "✅ Drive OAuth token found"
else
    echo "⚠️  Drive OAuth token not found (optional)"
    echo "   Set up with: python3 setup-oauth-drive.py"
fi

# Ensure log and output directories exist and are writable
echo
echo "Setting up directories..."
mkdir -p /app/logs /app/.multi_process_status /app/docs_generated 2>/dev/null || true

# Verify writable
if [ -w /app/logs ]; then
    echo "✅ Logs directory writable"
else
    echo "❌ ERROR: Logs directory not writable"
    echo "   Mount with: -v ./logs:/app/logs:rw,z"
    exit 1
fi

if [ -w /app/docs_generated ]; then
    echo "✅ Output directory writable"
else
    echo "❌ ERROR: Output directory not writable"
    echo "   Mount with: -v ./docs_generated:/app/docs_generated:rw,z"
    exit 1
fi

echo
echo "=========================================="
echo "Environment Ready - Starting Application"
echo "=========================================="
echo

# Execute the provided command
exec "$@"
