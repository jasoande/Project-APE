#!/bin/bash
################################################################################
# Project APE - Fix Directory Permissions
# Fixes permission issues for container access to logs and status directories
################################################################################

echo "Fixing directory permissions for container access..."
echo

# Remove old files/directories if they exist and have wrong permissions
if [ -e ".multi_process_status" ]; then
    echo "Removing old .multi_process_status..."
    rm -rf .multi_process_status
fi

if [ -e "logs" ]; then
    echo "Removing old logs directory..."
    rm -rf logs
fi

# Recreate with proper permissions
echo "Creating directories with proper permissions..."
mkdir -p logs .multi_process_status
chmod 777 logs .multi_process_status

# Make all existing files writable (important for Mac)
echo "Fixing file permissions inside directories..."
chmod -R a+rw logs .multi_process_status 2>/dev/null || true

echo
echo "✅ Permissions fixed!"
echo
echo "Directories created with permissions:"
ls -la | grep -E "(logs|multi_process_status)"
echo
echo "You can now run: ./launch_ape.sh fast"
