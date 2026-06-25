#!/bin/bash
################################################################################
# Project APE - Update Sources Script
# Updates existing NotebookLM notebooks with new/changed files from Google Drive
#
# Usage:
#   ./update-sources.sh fast                          # Update all clients
#   ./update-sources.sh fast merck_test               # Update specific client
#   ./update-sources.sh fast merck_test --research    # Update + re-run research
################################################################################

set -e

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ] || [ $# -eq 0 ]; then
    echo "Project APE - Update Sources"
    echo ""
    echo "Updates existing NotebookLM notebooks with new files from Google Drive"
    echo ""
    echo "Usage:"
    echo "  ./update-sources.sh fast [client1 client2 ...]  # Update specific clients"
    echo "  ./update-sources.sh fast --all                  # Update all clients"
    echo "  ./update-sources.sh fast client --research      # Update + re-run research"
    echo ""
    echo "Options:"
    echo "  --research    Re-run research prompts after adding new sources"
    echo "  --all         Update all clients defined in vars.py"
    echo ""
    echo "Examples:"
    echo "  ./update-sources.sh fast merck_test"
    echo "  ./update-sources.sh fast merck_test blue_yonder_test"
    echo "  ./update-sources.sh fast merck_test --research"
    echo "  ./update-sources.sh fast --all"
    echo ""
    echo "What it does:"
    echo "  1. Forces refresh of Google Drive cache"
    echo "  2. Downloads files from Drive"
    echo "  3. Compares with existing notebook sources"
    echo "  4. Adds only NEW files (no duplicates)"
    echo "  5. Deduplicates any duplicate sources"
    echo "  6. Optionally re-runs research prompts"
    echo ""
    echo "Note: The notebook must already exist. Run ./launch_ape.sh first to create it."
    echo ""
    exit 0
fi

# Configuration
IMAGE_NAME="project-ape"
REGISTRY="quay.io/jasoande/project_ape"
DASHBOARD_PORT=8765

# Get architecture-specific image version
get_image_version() {
    local arch=$1
    if [ "$arch" = "amd64" ]; then
        echo "3.0.5-amd64"
    else
        echo "latest"  # arm64 uses latest
    fi
}

# Detect architecture
detect_architecture() {
    local arch=$(uname -m)
    case "$arch" in
        x86_64|amd64) echo "amd64" ;;
        aarch64|arm64) echo "arm64" ;;
        *)
            echo "ERROR: Unsupported architecture: $arch" >&2
            exit 1
            ;;
    esac
}

# Detect container runtime
detect_runtime() {
    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        echo "ERROR: Neither podman nor docker found" >&2
        exit 1
    fi
}

# Parse arguments
if [ $# -eq 0 ]; then
    echo "ERROR: Mode is required (fast or deep)" >&2
    echo "Usage: $0 {fast|deep} [client1 client2 ...]" >&2
    exit 1
fi

MODE=$1
shift

CLIENTS=""
RESEARCH_FLAG=""

# Parse remaining arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --research)
            RESEARCH_FLAG="--research"
            shift
            ;;
        --all)
            CLIENTS="--all"
            shift
            ;;
        *)
            if [ "$CLIENTS" = "--all" ]; then
                echo "ERROR: Cannot specify both --all and individual clients" >&2
                exit 1
            fi
            CLIENTS="$CLIENTS $1"
            shift
            ;;
    esac
done

# Trim leading whitespace
CLIENTS=$(echo "$CLIENTS" | xargs)

if [ -z "$CLIENTS" ]; then
    echo "ERROR: No clients specified. Use client names or --all" >&2
    exit 1
fi

# Detect system
ARCH=$(detect_architecture)
RUNTIME=$(detect_runtime)
VERSION=$(get_image_version "$ARCH")
IMAGE="${REGISTRY}/${IMAGE_NAME}:${VERSION}"

echo "════════════════════════════════════════════════════════════════"
echo "  Project APE - Update Sources"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Architecture: ${ARCH}"
echo "Runtime: ${RUNTIME}"
echo "Mode: ${MODE}"
echo "Clients: ${CLIENTS}"
if [ -n "$RESEARCH_FLAG" ]; then
    echo "Re-run Research: YES"
fi
echo ""

# Create directories with proper permissions
mkdir -p logs .multi_process_status
chmod 777 logs .multi_process_status

# Build Python command
CMD="/opt/venv/bin/python3 main.py --mode update"

if [ "$CLIENTS" != "--all" ]; then
    CMD="${CMD} --clients ${CLIENTS}"
fi

if [ -n "$RESEARCH_FLAG" ]; then
    CMD="${CMD} ${RESEARCH_FLAG}"
fi

# Add --refresh to force Drive cache refresh
CMD="${CMD} --refresh"

# Check credentials volume
CREDS_VOLUME="project-ape-credentials"
CREDS_MOUNT=""
if $RUNTIME volume exists ${CREDS_VOLUME} 2>/dev/null; then
    CREDS_MOUNT="-v ${CREDS_VOLUME}:/home/apeuser/.notebooklm"
else
    echo "⚠️  WARNING: NotebookLM credentials volume not found"
    echo "   Run: ./setup-credentials.sh"
    echo ""
    exit 1
fi

# Check cache volume
CACHE_VOLUME="project-ape-cache"
CACHE_MOUNT=""
if $RUNTIME volume exists ${CACHE_VOLUME} 2>/dev/null; then
    CACHE_MOUNT="-v ${CACHE_VOLUME}:/home/apeuser/.project-ape"
fi

# Detect if we need --userns=keep-id for Podman
USERNS_FLAG=""
if [[ "$RUNTIME" == "podman" ]]; then
    USERNS_FLAG="--userns=keep-id"
fi

echo "Starting update..."
echo ""

# Run container
$RUNTIME run -it --rm \
    --name project-ape-update \
    ${USERNS_FLAG} \
    -p ${DASHBOARD_PORT}:8765 \
    -e HOME=/home/apeuser \
    -v $(pwd)/.env:/app/.env:ro,z \
    -v $(pwd)/vars.py:/app/vars.py:ro,z \
    -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
    -v $(pwd)/main.py:/app/main.py:ro,z \
    -v $(pwd)/core:/app/core:ro,z \
    -v $(pwd)/dashboard:/app/dashboard:ro,z \
    -v $(pwd)/logs:/app/logs:z \
    -v $(pwd)/.multi_process_status:/app/.multi_process_status:z \
    ${CREDS_MOUNT} \
    ${CACHE_MOUNT} \
    "${IMAGE}" \
    ${CMD}
