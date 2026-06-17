#!/bin/bash
################################################################################
# Project APE - Container Runtime Wrapper
# Automatically detects architecture and runs the appropriate container
################################################################################

set -e

# Configuration
IMAGE_NAME="project-ape-rhel9"
IMAGE_VERSION="3.0.5"
REGISTRY="${REGISTRY:-quay.io/yourorg}"  # Override with your registry
DASHBOARD_PORT=8765

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
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
            log_error "Unsupported architecture: $arch"
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
        log_error "Neither Podman nor Docker is installed"
        log_error "Please install one of them:"
        log_error "  RHEL/Fedora: sudo dnf install podman"
        log_error "  Ubuntu: sudo apt-get install podman"
        log_error "  Or install Docker from: https://docs.docker.com/engine/install/"
        exit 1
    fi
}

################################################################################
# Build or Pull Image
################################################################################

get_image() {
    local runtime=$1
    local arch=$2
    local mode=$3  # "build" or "pull"

    local full_image="${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}-${arch}"

    if [ "$mode" = "build" ]; then
        log_info "Building image for architecture: $arch"
        $runtime build \
            --platform linux/$arch \
            -t ${IMAGE_NAME}:latest \
            -t ${IMAGE_NAME}:${IMAGE_VERSION} \
            -t ${IMAGE_NAME}:${IMAGE_VERSION}-${arch} \
            -f Containerfile .

        log_info "✅ Build complete: ${IMAGE_NAME}:${IMAGE_VERSION}-${arch}"
        echo "${IMAGE_NAME}:${IMAGE_VERSION}-${arch}"
    else
        log_info "Pulling image for architecture: $arch"

        # Try to pull from registry
        if $runtime pull $full_image 2>/dev/null; then
            log_info "✅ Pulled: $full_image"
            echo "$full_image"
        else
            log_warn "Could not pull from registry: $full_image"
            log_info "Checking for local image..."

            # Check if local image exists
            if $runtime images ${IMAGE_NAME}:latest | grep -q ${IMAGE_NAME}; then
                log_info "✅ Using local image: ${IMAGE_NAME}:latest"
                echo "${IMAGE_NAME}:latest"
            else
                log_error "No image found. Please build locally or configure registry."
                log_error "To build locally, run: $0 --build"
                exit 1
            fi
        fi
    fi
}

################################################################################
# Run Container
################################################################################

run_container() {
    local runtime=$1
    local image=$2
    local mode=$3
    local clients=$4

    log_info "Starting Project APE container..."
    log_info "Runtime: $runtime"
    log_info "Image: $image"
    log_info "Mode: $mode"

    # Build volume mounts
    local volumes=""

    # Required: .env file
    if [ -f ".env" ]; then
        volumes="$volumes -v $(pwd)/.env:/opt/project-ape/.env:ro"
    else
        log_warn ".env file not found - container may fail without API keys"
    fi

    # Required: Service account (if exists)
    if [ -f "jasoande-3aec1043e544.json" ]; then
        volumes="$volumes -v $(pwd)/jasoande-3aec1043e544.json:/opt/project-ape/service-account.json:ro"
    else
        log_warn "Service account not found - Google Drive integration may fail"
    fi

    # Required: Client data
    if [ -d "test_client_data" ]; then
        volumes="$volumes -v $(pwd)/test_client_data:/opt/project-ape/test_client_data:ro"
    else
        log_warn "test_client_data directory not found"
    fi

    # Optional: Logs (for persistence)
    mkdir -p logs
    volumes="$volumes -v $(pwd)/logs:/opt/project-ape/logs:rw"

    # Optional: Status files (for dashboard)
    mkdir -p .multi_process_status
    volumes="$volumes -v $(pwd)/.multi_process_status:/opt/project-ape/.multi_process_status:rw"

    # Build command arguments
    local cmd_args="main.py --mode $mode"
    if [ -n "$clients" ]; then
        cmd_args="$cmd_args --clients $clients"
    fi

    # Run container
    log_info "Dashboard will be available at: http://localhost:${DASHBOARD_PORT}"

    $runtime run -it --rm \
        --name project-ape \
        -p ${DASHBOARD_PORT}:8765 \
        $volumes \
        $image \
        $cmd_args
}

################################################################################
# Main
################################################################################

main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "  Project APE - RHEL 9 Container Runtime"
    echo "  Architecture-aware container launcher"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Parse arguments
    local build_mode="pull"
    local run_mode="fast"
    local clients=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_mode="build"
                shift
                ;;
            --mode)
                run_mode="$2"
                shift 2
                ;;
            --clients)
                clients="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --help|-h)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
    --build              Build image locally instead of pulling
    --mode MODE          Execution mode: fast|deep|update (default: fast)
    --clients CLIENTS    Space-separated client list (default: all)
    --registry REGISTRY  Container registry URL (default: quay.io/yourorg)
    --help, -h           Show this help message

Examples:
    # Pull and run (fast mode, all clients)
    $0

    # Build locally and run
    $0 --build

    # Run in deep mode
    $0 --mode deep

    # Run specific clients
    $0 --mode fast --clients "merck_test blue_yonder_test"

    # Use custom registry
    $0 --registry registry.example.com/project-ape

Environment Variables:
    REGISTRY    Override default registry (same as --registry)

EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                log_error "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Detect architecture
    local arch=$(detect_architecture)
    log_info "Detected architecture: $arch"

    # Detect container runtime
    local runtime=$(detect_runtime)
    log_info "Detected runtime: $runtime"

    # Get image
    local image=$(get_image "$runtime" "$arch" "$build_mode")

    # Run container
    run_container "$runtime" "$image" "$run_mode" "$clients"
}

main "$@"
