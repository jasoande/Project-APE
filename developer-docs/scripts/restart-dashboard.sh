#!/bin/bash
################################################################################
# Project APE - Dashboard Restart Script
# Safely restart the dashboard server with latest code
################################################################################

DASHBOARD_PORT=8765

echo "🔄 Restarting Project APE Dashboard..."
echo ""

# Kill existing dashboard server
if lsof -ti:$DASHBOARD_PORT > /dev/null 2>&1; then
    echo "  Stopping existing dashboard server..."
    lsof -ti:$DASHBOARD_PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start new dashboard server with virtual environment Python
VENV_PYTHON="$HOME/.project-ape-venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "  ❌ Virtual environment not found at: $VENV_PYTHON"
    echo "  Please run: ./setup-environment.sh"
    exit 1
fi

echo "  Starting dashboard server..."
nohup "$VENV_PYTHON" dashboard/server.py > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo -n "  Waiting for server to be ready"
for i in {1..20}; do
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$DASHBOARD_PORT/" | grep -q "200"; then
        echo ""
        echo ""
        echo "✅ Dashboard server restarted successfully!"
        echo "   URL: http://localhost:$DASHBOARD_PORT"
        echo "   PID: $SERVER_PID"
        echo ""
        exit 0
    fi
    echo -n "."
    sleep 0.5
done

echo ""
echo "❌ Dashboard server failed to start"
exit 1
