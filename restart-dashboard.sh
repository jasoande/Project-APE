#!/bin/bash
#
# Simple Dashboard Restart Script
# Clears cache, kills old processes, starts fresh
#

echo "Stopping dashboard..."
pkill -f "dashboard/server.py" 2>/dev/null || true
pkill -f "launch-project-ape.py" 2>/dev/null || true
sleep 1

echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Testing import..."
python3 -c "import sys; sys.path.insert(0, 'developer-docs'); import workflow_detector; print('✅ Import OK')"

if [ $? -eq 0 ]; then
    echo ""
    echo "Starting dashboard..."
    python3 launch-project-ape.py
else
    echo ""
    echo "❌ Import failed - check error above"
    exit 1
fi
