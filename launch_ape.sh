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

    # Create directories if they don't exist with proper permissions
    mkdir -p logs .multi_process_status

    # Set permissions so container user can write (container runs as UID 1000)
    # Option 1: World-writable (simple but less secure)
    chmod 777 logs .multi_process_status

    # Option 2: If you want tighter permissions, use --userns=keep-id
    # This maps the container user to your host user

    # Run container with SELinux-compatible volume flags
    $runtime run -it --rm \
        --name project-ape \
        -p ${DASHBOARD_PORT}:8765 \
        -v $(pwd)/.env:/app/.env:ro,z \
        -v $(pwd)/vars.py:/app/vars.py:ro,z \
        -v $(pwd)/jasoande-3aec1043e544.json:/app/service-account.json:ro,z \
        -v $(pwd)/logs:/app/logs:z \
        -v $(pwd)/.multi_process_status:/app/.multi_process_status:z \
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
    if [ $# -eq 0 ]; then
        echo "ERROR: Mode is required (fast or deep)" >&2
        echo "Usage: $0 {fast|deep} [client1 client2 ...]" >&2
        echo "   or: $0 --mode {fast|deep} [--clients client1 client2 ...]" >&2
        exit 1
    fi

    local mode=""
    local clients=""

    # Parse arguments - support both positional and flag-based syntax
    while [ $# -gt 0 ]; do
        case "$1" in
            --mode)
                mode="$2"
                shift 2
                ;;
            --clients)
                shift
                # Collect all remaining args as clients
                clients="$@"
                break
                ;;
            fast|deep)
                if [ -z "$mode" ]; then
                    mode="$1"
                    shift
                else
                    # If mode already set, treat as client
                    clients="$clients $1"
                    shift
                fi
                ;;
            *)
                # Any other arg is a client name
                clients="$clients $1"
                shift
                ;;
        esac
    done

    # Trim leading whitespace from clients
    clients=$(echo "$clients" | xargs)

    # Validate mode is set
    if [ -z "$mode" ]; then
        echo "ERROR: Mode is required (fast or deep)" >&2
        echo "Usage: $0 {fast|deep} [client1 client2 ...]" >&2
        echo "   or: $0 --mode {fast|deep} [--clients client1 client2 ...]" >&2
        exit 1
    fi

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
