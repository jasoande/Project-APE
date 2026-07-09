#!/bin/bash
################################################################################
# Account Intelligence - Direct Browser Launcher
# Double-click this file to open the configuration page in your browser
#
# This launcher opens the configuration UI directly without showing terminal
################################################################################

# Configuration
DASHBOARD_PORT=8765
CONFIG_URL="http://localhost:$DASHBOARD_PORT/configure"

# Get script directory (works even when double-clicked)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if server is already running
if curl -s -o /dev/null -w "%{http_code}" "$CONFIG_URL" | grep -q "200"; then
    # Server already running, just open browser
    open "$CONFIG_URL"
    exit 0
fi

# Server not running, start it in background
VENV_PYTHON="$HOME/.project-ape-venv/bin/python3"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run: ./setup-environment.sh"
    exit 1
fi

# Start dashboard server in background with virtual environment Python
nohup "$VENV_PYTHON" "$SCRIPT_DIR/dashboard/server.py" > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start (max 10 seconds)
for i in {1..20}; do
    if curl -s -o /dev/null -w "%{http_code}" "$CONFIG_URL" | grep -q "200"; then
        # Server is ready, open browser
        open "$CONFIG_URL"
        exit 0
    fi
    sleep 0.5
done

# Server didn't start, show error
echo "Failed to start dashboard server"
exit 1
