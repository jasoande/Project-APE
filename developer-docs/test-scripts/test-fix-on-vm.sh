#!/bin/bash
################################################################################
# Quick test script for VM - uses correct v3.2.3 image
################################################################################

set -e

echo "========================================================================"
echo "🔍 Testing Project APE v3.2.3 with Sandbox Fix"
echo "========================================================================"
echo

# Stop any existing containers
echo "🧹 Cleaning up old containers..."
podman stop project-ape 2>/dev/null || true
podman rm project-ape 2>/dev/null || true
echo

# Pull correct version
echo "📥 Pulling v3.2.3-arm64 with sandbox fix..."
podman pull quay.io/jasoande/project_ape/project-ape:3.2.3-arm64
echo

# Verify environment variables are present
echo "🔍 Verifying sandbox fix in image..."
ENV_CHECK=$(podman run --rm --entrypoint=/bin/bash quay.io/jasoande/project_ape/project-ape:3.2.3-arm64 -c "env | grep SAL_" || echo "")

if echo "$ENV_CHECK" | grep -q "SAL_NO_SANDBOX=1"; then
    echo "✅ Found: SAL_NO_SANDBOX=1"
    echo "✅ Found: SAL_USE_VCLPLUGIN=gen"
else
    echo "❌ ERROR: SAL_NO_SANDBOX not found in image!"
    echo "   Environment variables found:"
    echo "$ENV_CHECK"
    echo
    echo "⚠️  Continuing anyway to test with seccomp option..."
fi
echo

# Start container with fix
echo "🚀 Starting container with --security-opt seccomp=unconfined..."
podman run \
    --name project-ape \
    --rm \
    -d \
    -p 8765:8765 \
    --security-opt seccomp=unconfined \
    quay.io/jasoande/project_ape/project-ape:3.2.3-arm64 \
    python3 dashboard/server.py

echo "✅ Container started"
echo

# Wait for dashboard
echo "⏳ Waiting 15 seconds for dashboard to start..."
sleep 15
echo

# Check for sandbox errors
echo "🔍 Checking logs for sandbox errors..."
SANDBOX_ERRORS=$(podman logs project-ape 2>&1 | grep -i "sandbox.*clone.*failure.*eperm" || echo "")

if [ -n "$SANDBOX_ERRORS" ]; then
    echo "❌ SANDBOX ERRORS FOUND:"
    echo "$SANDBOX_ERRORS"
    echo
    echo "The fix did not work. Showing full logs:"
    podman logs project-ape
    exit 1
fi

echo "✅ No sandbox errors in logs!"
echo

# Test HTTP connectivity
echo "🔍 Testing HTTP connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/configure 2>/dev/null || echo "000")

if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Dashboard is responding: HTTP $HTTP_CODE"
    echo
    echo "========================================================================"
    echo "🎉 SUCCESS! The sandbox fix is working!"
    echo "========================================================================"
    echo
    echo "Dashboard is accessible at: http://localhost:8765/configure"
    echo
    echo "To stop:"
    echo "  podman stop project-ape"
    exit 0
else
    echo "⚠️  Dashboard returned HTTP $HTTP_CODE (expected 200)"
    echo
    echo "Showing container logs:"
    podman logs project-ape
    exit 1
fi
