#!/bin/bash
################################################################################
# Project APE Launcher
#
# Simple wrapper script for running Project APE from Gemini or command line
#
# Usage:
#   ./launch_ape.sh fast          # Run all clients in fast mode
#   ./launch_ape.sh deep          # Run all clients in deep mode
#   ./launch_ape.sh update        # Update existing notebooks with new data
#   ./launch_ape.sh fast merck_test blue_yonder_test  # Run specific clients
################################################################################

# Change to Project APE directory
cd /Users/jasona/test/Project-APE

# Default to fast mode if no argument provided
MODE="${1:-fast}"

# Shift to get remaining arguments (client list)
shift

# Build command
CMD="python main.py --mode $MODE"

# Add specific clients if provided
if [ $# -gt 0 ]; then
    CMD="$CMD --clients $@"
fi

# Display what we're running
echo "========================================="
echo "Project APE Launcher"
echo "========================================="
echo "Mode: $MODE"
if [ $# -gt 0 ]; then
    echo "Clients: $@"
else
    echo "Clients: ALL (from vars.py)"
fi
echo "Command: $CMD"
echo "========================================="
echo ""

# Execute
eval $CMD
