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
    echo "  ./launch_ape.sh fast --refresh            # Force refresh Drive cache"
    echo "  ./launch_ape.sh fast client1 client2      # Specific clients only"
    echo ""
    echo "Modes:"
    echo "  fast     Quick research (15-20 minutes per client)"
    echo "  deep     Thorough research (35-40 minutes per client)"
    echo ""
    echo "Options:"
    echo "  --refresh    Force refresh Google Drive cache (ignore 24hr TTL)"
    echo ""
    echo "Examples:"
    echo "  ./launch_ape.sh fast                      # Run all clients in vars.py"
    echo "  ./launch_ape.sh fast merck_test           # Run one client"
    echo "  ./launch_ape.sh deep merck_test blue_yonder_test  # Multiple clients, deep mode"
    echo "  ./launch_ape.sh fast --refresh            # Force fresh download from Drive"
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

log_error() {
    echo -e "${YELLOW}[ERROR]${NC} $1" >&2
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
    local refresh_flag=$4
    shift 4
    local clients="$@"

    # Clear consolidation timestamps for fresh PDF generation each run
    # This ensures each workflow run creates new PDFs even if files haven't changed
    if [ -d "$HOME/.project-ape/consolidation_timestamps" ]; then
        rm -f "$HOME/.project-ape/consolidation_timestamps"/*.json 2>/dev/null
        log_info "Cleared consolidation cache for fresh run"
    fi

    # Clear previous run status files for fresh timer and status tracking
    # This prevents old run data from showing in the dashboard
    local status_dir="$(pwd)/.multi_process_status"
    if [ -d "$status_dir" ]; then
        rm -f "$status_dir"/*.json 2>/dev/null
        log_info "Cleared previous run status files"
    fi

    local version=$(get_image_version "$arch")
    local image="${REGISTRY}/${IMAGE_NAME}:${version}"

    # Build command
    local cmd="/opt/venv/bin/python3 main.py --mode ${mode}"
    if [ -n "$clients" ]; then
        cmd="${cmd} --clients ${clients}"
    fi
    if [ -n "$refresh_flag" ]; then
        cmd="${cmd} ${refresh_flag}"
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

    # Mount the .project-ape directory for OAuth credentials and cache
    # This contains: drive_credentials.json, drive_token.json, and drive_cache/
    local project_ape_mount=""
    if [ -d "$HOME/.project-ape" ]; then
        project_ape_mount="-v $HOME/.project-ape:/home/apeuser/.project-ape:z"
        log_info "Mounting OAuth credentials from ~/.project-ape"
    else
        log_info "No ~/.project-ape directory found (OAuth not configured yet)"
    fi

    # Detect if we need --userns=keep-id for Podman
    # This allows container to access host files with proper permissions
    userns_flag=""
    if [[ "$runtime" == "podman" ]]; then
        userns_flag="--userns=keep-id"
    fi

    # Run container with SELinux-compatible volume flags
    # IMPORTANT: Set HOME=/home/apeuser so NotebookLM CLI finds credentials
    # Mount code for development (core/, dashboard/, main.py)
    # Note: No -it flags so container exits cleanly when pipeline completes
    # --stop-timeout: Force kill if container doesn't stop within 10 seconds
    # --stop-signal: Use SIGTERM for graceful shutdown
    $runtime run --rm \
        --name project-ape \
        --stop-timeout 10 \
        --stop-signal SIGTERM \
        ${userns_flag} \
        -p ${DASHBOARD_PORT}:8765 \
        -e HOME=/home/apeuser \
        $([ -f "$(pwd)/.env" ] && echo "-v $(pwd)/.env:/app/.env:ro,z") \
        -v $(pwd)/vars.py:/app/vars.py:ro,z \
        -v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \
        -v $(pwd)/main.py:/app/main.py:ro,z \
        -v $(pwd)/core:/app/core:ro,z \
        -v $(pwd)/dashboard:/app/dashboard:ro,z \
        -v $(pwd)/logs:/app/logs:z \
        -v $(pwd)/.multi_process_status:/app/.multi_process_status:z \
        ${project_ape_mount} \
        ${creds_mount} \
        "${image}" \
        ${cmd}

    # Container has exited
    log_info "Container stopped successfully"
}

################################################################################
# NotebookLM Authentication Check
################################################################################

check_notebooklm_auth() {
    log_step "Checking NotebookLM authentication..."

    # Check if notebooklm CLI is available
    if ! command -v notebooklm &> /dev/null; then
        log_error "NotebookLM CLI not found"
        echo "Please install: pip install notebooklm-cli"
        return 1
    fi

    # Check authentication status
    if ! notebooklm auth check &> /dev/null; then
        log_error "NotebookLM authentication expired or invalid"
        echo ""
        echo "Your NotebookLM credentials need to be refreshed."
        echo "This happens when:"
        echo "  • Cookies expire (typically after 30-90 days)"
        echo "  • Google session is invalidated"
        echo "  • Browser profile is cleared"
        echo ""
        echo "To fix this, run:"
        echo "  ${GREEN}notebooklm auth refresh${NC}"
        echo ""
        echo "This will:"
        echo "  1. Open your browser"
        echo "  2. Sign in to NotebookLM"
        echo "  3. Save fresh credentials"
        echo ""
        read -p "Run auth refresh now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            notebooklm auth refresh
            if [ $? -eq 0 ]; then
                log_info "✅ Authentication refreshed successfully"
            else
                log_error "Authentication refresh failed"
                return 1
            fi
        else
            echo "Please refresh authentication before launching workflows."
            return 1
        fi
    else
        log_info "✅ NotebookLM authentication valid"
    fi

    return 0
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
    local refresh_flag=""

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
            --refresh)
                refresh_flag="--refresh"
                shift
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

    # Check NotebookLM authentication before proceeding
    if ! check_notebooklm_auth; then
        echo ""
        echo "Cannot proceed without valid NotebookLM authentication."
        exit 1
    fi
    echo ""

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
    run_container "$runtime" "$arch" "$mode" "$refresh_flag" $clients
}

main "$@"
