#!/bin/bash
################################################################################
# Test Script for Setup Environment Button
# Tests the /api/run-setup endpoint without actually running full setup
################################################################################

echo "🧪 Testing Setup Environment Button"
echo "===================================="
echo ""

# Check if dashboard is running
if ! curl -s http://localhost:8765/ > /dev/null; then
    echo "❌ Dashboard is not running"
    echo "   Please start it with: ./restart-dashboard.sh"
    exit 1
fi

echo "✅ Dashboard is running"
echo ""

# Check if configure page has the button
echo "🔍 Checking if Setup Environment button exists in UI..."
if curl -s http://localhost:8765/configure | grep -q "setupEnvBtn"; then
    echo "✅ Setup Environment button found in configure.html"
else
    echo "❌ Setup Environment button NOT found"
    exit 1
fi
echo ""

# Check if API endpoint exists
echo "🔍 Testing /api/run-setup endpoint..."
echo "   (Will cancel after 2 seconds to avoid full setup)"
timeout 2 curl -X POST -N http://localhost:8765/api/run-setup 2>/dev/null | head -10

echo ""
echo ""
echo "✅ Setup Environment Button Test Complete!"
echo ""
echo "To use the button:"
echo "  1. Open http://localhost:8765/configure in your browser"
echo "  2. Look for the 'System Tools' section at the top"
echo "  3. Click '🔧 Setup Environment'"
echo "  4. Confirm the dialog"
echo "  5. Watch real-time output in the collapsible panel"
echo ""
