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

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Project APE - Account Planning Engine v3.2.0"
    echo ""
    echo "Usage:"
    echo "  ./launch_ape.sh fast                      # All clients, fast mode (15-20 min)"
    echo "  ./launch_ape.sh deep                      # All clients, deep mode (35-40 min)"
    echo "  ./launch_ape.sh fast client1 client2      # Specific clients only"
    echo ""
    echo "Modes:"
    echo "  fast     Quick research (15-20 minutes per client)"
    echo "  deep     Thorough research (35-40 minutes per client)"
    echo ""
    echo "Examples:"
    echo "  ./launch_ape.sh fast                      # Run all clients in vars.py"
    echo "  ./launch_ape.sh fast merck_test           # Run one client"
    echo "  ./launch_ape.sh deep merck_test blue_yonder_test  # Multiple clients, deep mode"
    echo ""
    echo "Dashboard:"
    echo "  Automatically opens at http://localhost:8765"
    echo "  Shows real-time progress, quality scores, and logs"
    echo ""
    exit 0
fi

# Configuration
IMAGE_NAME="project-ape"
REGISTRY="quay.io/jasoande/project_ape"
DASHBOARD_PORT=8765

# Version selection based on architecture
# amd64: Use versioned tag (more stable for production EC2)
# arm64: Use latest tag (Mac development)
get_image_version() {
    local arch=$1
    if [ "$arch" = "amd64" ]; then
        echo "3.0.5-amd64"
    else
        echo "latest"  # arm64 uses latest
    fi
}

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
    local version=$(get_image_version "$arch")
    local image="${REGISTRY}/${IMAGE_NAME}:${version}"

    log_step "Checking for container image..."

    # Check if image exists locally
    if $runtime images | grep -q "${IMAGE_NAME}.*${version}"; then
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
        echo "Trying latest tag as fallback..." >&2
        $runtime pull "${REGISTRY}/${IMAGE_NAME}:latest" || {
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

    local version=$(get_image_version "$arch")
    local image="${REGISTRY}/${IMAGE_NAME}:${version}"

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
    # Make directories world-writable
    chmod 777 logs .multi_process_status

    # Also fix permissions on any existing files (important for Mac)
    # This ensures old logs don't block new runs
    if [ -d "logs" ]; then
        chmod -R a+rw logs 2>/dev/null || true
    fi
    if [ -d ".multi_process_status" ]; then
        chmod -R a+rw .multi_process_status 2>/dev/null || true
    fi

    # Option 2: If you want tighter permissions, use --userns=keep-id
    # This maps the container user to your host user

    # Check if credentials volume exists (REQUIRED)
    local creds_volume="project-ape-credentials"
    local creds_mount=""
    if $runtime volume exists ${creds_volume} 2>/dev/null; then
        log_info "Using credentials volume: ${creds_volume}"
        creds_mount="-v ${creds_volume}:/home/apeuser/.notebooklm"
    else
        echo ""
        echo "⚠️  WARNING: NotebookLM credentials volume not found"
        echo "   The pipeline will fail without authentication"
        echo "   Run: ./setup-credentials.sh"
        echo ""
    fi

    # Check for cache volume (OPTIONAL - improves performance)
    local cache_volume="project-ape-cache"
    local cache_mount=""
    if $runtime volume exists ${cache_volume} 2>/dev/null; then
        log_info "Using cache volume: ${cache_volume}"
        cache_mount="-v ${cache_volume}:/home/apeuser/.project-ape"
    fi

    # Detect if we need --userns=keep-id for Podman
    # This allows container to access host files with proper permissions
    userns_flag=""
    if [[ "$runtime" == "podman" ]]; then
        userns_flag="--userns=keep-id"
    fi

    # Run container with SELinux-compatible volume flags
    # IMPORTANT: Set HOME=/home/apeuser so NotebookLM CLI finds credentials
    # NOTE: core/, dashboard/, main.py could be mounted for development but
    #       require container rebuild to pick up dependency changes
    $runtime run -it --rm \
        --name project-ape \
        ${userns_flag} \
        -p ${DASHBOARD_PORT}:8765 \
        -e HOME=/home/apeuser \
        -v $(pwd)/.env:/app/.env:ro,z \
        -v $(pwd)/vars.py:/app/vars.py:ro,z \
        -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
        -v $(pwd)/logs:/app/logs:z \
        -v $(pwd)/.multi_process_status:/app/.multi_process_status:z \
        ${creds_mount} \
        ${cache_mount} \
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
