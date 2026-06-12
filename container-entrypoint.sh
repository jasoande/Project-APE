#!/bin/bash
# Project APE - Container Entrypoint
# Handles credential setup and starts the application

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

# Execute the main command
echo "🚀 Starting Project APE..."
exec "$@"
