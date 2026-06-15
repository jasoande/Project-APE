#!/bin/bash
# Project APE - Container Entrypoint
# Handles credential setup and starts the application

set -e

# Validate notebooklm CLI is available
if ! command -v notebooklm &> /dev/null; then
    echo "❌ ERROR: notebooklm CLI not found in PATH"
    echo "   Container may not have been built correctly"
    exit 1
fi

echo "✅ NotebookLM CLI found: $(which notebooklm)"

# Check if credentials are mounted via persistent volume or need copying
if [ -d "/home/apeuser/.notebooklm/profiles" ]; then
    # Persistent volume mounted - credentials already in place
    echo "✅ Using persistent credential volume"
elif [ -d "/creds-ro/.notebooklm" ]; then
    # Legacy: Copy from read-only host mount (deprecated)
    echo "📋 Copying credentials from host mount (legacy mode)..."
    if cp -rL /creds-ro/.notebooklm ~/.notebooklm 2>/dev/null || \
       cp -r /creds-ro/.notebooklm/* ~/.notebooklm/ 2>/dev/null || \
       { mkdir -p ~/.notebooklm && cp -r /creds-ro/.notebooklm/* ~/.notebooklm/ 2>/dev/null; }; then
        find ~/.notebooklm -type d -exec chmod 700 {} \; 2>/dev/null || true
        find ~/.notebooklm -type f -exec chmod 600 {} \; 2>/dev/null || true
        echo "✅ Credentials copied"
    else
        echo "⚠️  Credential copy failed - use persistent volume instead"
        echo "   Run: ./setup-credentials.sh"
    fi
else
    echo "⚠️  No credentials found"
    echo "   Run setup: ./setup-credentials.sh"
fi

# Create runtime directories if they don't exist
mkdir -p /app/logs /app/.multi_process_status

# Validate vars.py exists and is readable
if [ ! -f "/app/vars.py" ] || [ ! -r "/app/vars.py" ]; then
    echo "❌ ERROR: vars.py not found or not readable"
    echo "   Ensure vars.py is mounted at /app/vars.py"
    exit 1
fi

echo "✅ Configuration validated"

# Execute the main command
echo "🚀 Starting Project APE..."
exec "$@"
