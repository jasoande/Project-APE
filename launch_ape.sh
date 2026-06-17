#!/bin/bash
################################################################################
# Project APE Launcher
# Automatically detects architecture and runs the appropriate container image
#
# Usage:
#   ./launch_ape.sh fast                              # All clients, fast mode
#   ./launch_ape.sh deep                              # All clients, deep mode
#   ./launch_ape.sh fast merck_test blue_yonder_test  # Specific clients
################################################################################

set -e

# Configuration
IMAGE_NAME="project-ape"
IMAGE_VERSION="3.0.5"
REGISTRY="quay.io/jasoande/project_ape"
DASHBOARD_PORT=8765

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

################################################################################
# Detect Architecture
################################################################################

detect_architecture() {
    local arch=$(uname -m)

    case "$arch" in
        x86_64|amd64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        *)
            echo "ERROR: Unsupported architecture: $arch" >&2
            exit 1
            ;;
    esac
}

################################################################################
# Detect Container Runtime
################################################################################

detect_runtime() {
    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        echo "ERROR: Neither podman nor docker found" >&2
        echo "Please install podman or docker to run Project APE" >&2
        exit 1
    fi
}

################################################################################
# Pull Container Image
################################################################################

pull_image() {
    local runtime=$1
    local arch=$2
    local image="${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}-${arch}"

    log_step "Checking for container image..."

    # Check if image exists locally
    if $runtime images | grep -q "${IMAGE_NAME}.*${IMAGE_VERSION}-${arch}"; then
        log_info "Using local image: ${image}"
        return 0
    fi

    # Pull from registry
    log_step "Pulling image from Quay.io..."
    log_info "Image: ${image}"

    if $runtime pull "${image}"; then
        log_info "✅ Image pulled successfully"
        return 0
    else
        echo "ERROR: Failed to pull image ${image}" >&2
        echo "Trying latest tag..." >&2
        $runtime pull "${REGISTRY}/${IMAGE_NAME}:latest-${arch}" || {
            echo "ERROR: Could not pull container image" >&2
            exit 1
        }
    fi
}

################################################################################
# Run Container
################################################################################

run_container() {
    local runtime=$1
    local arch=$2
    local mode=$3
    shift 3
    local clients="$@"

    local image="${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}-${arch}"

    # Build command
    local cmd="/opt/venv/bin/python3 main.py --mode ${mode}"
    if [ -n "$clients" ]; then
        cmd="${cmd} --clients ${clients}"
    fi

    log_step "Starting Project APE..."
    log_info "Architecture: ${arch}"
    log_info "Mode: ${mode}"
    if [ -n "$clients" ]; then
        log_info "Clients: ${clients}"
    else
        log_info "Clients: ALL (from vars.py)"
    fi
    log_info "Dashboard: http://localhost:${DASHBOARD_PORT}"
    echo ""

    # Run container
    $runtime run -it --rm \
        --name project-ape \
        -p ${DASHBOARD_PORT}:8765 \
        -v $(pwd)/.env:/app/.env:ro \
        -v $(pwd)/vars.py:/app/vars.py:ro \
        -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro \
        -v $(pwd)/logs:/app/logs:rw \
        -v $(pwd)/.multi_process_status:/app/.multi_process_status:rw \
        "${image}" \
        ${cmd}
}

################################################################################
# Main
################################################################################

main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "  Project APE - Account Planning Engine"
    echo "  Automatic Architecture Detection & Container Launcher"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Parse arguments
    local mode="${1:-fast}"
    shift || true
    local clients="$@"

    # Detect system
    local arch=$(detect_architecture)
    local runtime=$(detect_runtime)

    log_info "Detected architecture: ${arch}"
    log_info "Detected runtime: ${runtime}"
    echo ""

    # Pull image
    pull_image "$runtime" "$arch"
    echo ""

    # Run container
    run_container "$runtime" "$arch" "$mode" $clients
}

main "$@"
