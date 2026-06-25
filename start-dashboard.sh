#!/bin/bash
################################################################################
# Project APE - Dashboard Startup Script
# Starts the dashboard server in the background with output logging
################################################################################

VENV_PYTHON="$HOME/.project-ape-venv/bin/python3"
LOG_FILE="$HOME/.project-ape/dashboard.log"

# Create log directory
mkdir -p "$HOME/.project-ape"

# Check if already running
if pgrep -f "dashboard/server.py" > /dev/null; then
    echo "Dashboard server is already running"
    echo "Visit: http://localhost:8765"
    exit 0
fi

# Start server
echo "Starting dashboard server..."
nohup "$VENV_PYTHON" dashboard/server.py >> "$LOG_FILE" 2>&1 &

# Wait for startup
sleep 2

# Check if started successfully
if pgrep -f "dashboard/server.py" > /dev/null; then
    echo "✅ Dashboard server started successfully"
    echo "   URL: http://localhost:8765"
    echo "   Logs: $LOG_FILE"
else
    echo "❌ Failed to start dashboard server"
    echo "   Check logs: $LOG_FILE"
    exit 1
fi
