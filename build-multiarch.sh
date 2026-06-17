#!/bin/bash
################################################################################
# Project APE - Multi-Architecture Container Build Script
# Builds container images for both amd64 and arm64 architectures
################################################################################

set -e

# Configuration
IMAGE_NAME="project-ape-rhel9"
IMAGE_VERSION="3.0.5"
REGISTRY="${REGISTRY:-quay.io/yourorg}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

################################################################################
# Detect Build Tool
################################################################################

detect_builder() {
    if command -v buildah &> /dev/null; then
        echo "buildah"
    elif command -v podman &> /dev/null && podman --version | grep -q "buildx"; then
        echo "podman-buildx"
    elif command -v docker &> /dev/null && docker buildx version &> /dev/null; then
        echo "docker-buildx"
    elif command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        log_error "No suitable build tool found"
        log_error "Please install: buildah, podman, or docker"
        exit 1
    fi
}

################################################################################
# Build Multi-Arch Image
################################################################################

build_multiarch() {
    local builder=$1

    log_step "Building multi-architecture images..."
    log_info "Architectures: amd64, arm64"

    case "$builder" in
        buildah)
            log_info "Using buildah for multi-arch build"

            # Build for amd64
            log_step "Building for linux/amd64..."
            buildah build \
                --platform linux/amd64 \
                --tag ${IMAGE_NAME}:${IMAGE_VERSION}-amd64 \
                --tag ${IMAGE_NAME}:latest-amd64 \
                --file Containerfile \
                .

            # Build for arm64
            log_step "Building for linux/arm64..."
            buildah build \
                --platform linux/arm64 \
                --tag ${IMAGE_NAME}:${IMAGE_VERSION}-arm64 \
                --tag ${IMAGE_NAME}:latest-arm64 \
                --file Containerfile \
                .

            # Create manifest
            log_step "Creating multi-arch manifest..."
            buildah manifest create ${IMAGE_NAME}:${IMAGE_VERSION}
            buildah manifest add ${IMAGE_NAME}:${IMAGE_VERSION} ${IMAGE_NAME}:${IMAGE_VERSION}-amd64
            buildah manifest add ${IMAGE_NAME}:${IMAGE_VERSION} ${IMAGE_NAME}:${IMAGE_VERSION}-arm64

            buildah manifest create ${IMAGE_NAME}:latest
            buildah manifest add ${IMAGE_NAME}:latest ${IMAGE_NAME}:latest-amd64
            buildah manifest add ${IMAGE_NAME}:latest ${IMAGE_NAME}:latest-arm64
            ;;

        podman-buildx|docker-buildx)
            local runtime=${builder%-buildx}
            log_info "Using $runtime buildx for multi-arch build"

            # Create and use builder
            $runtime buildx create --name ape-builder --use 2>/dev/null || true

            # Build multi-arch
            $runtime buildx build \
                --platform linux/amd64,linux/arm64 \
                --tag ${IMAGE_NAME}:${IMAGE_VERSION} \
                --tag ${IMAGE_NAME}:latest \
                --file Containerfile \
                --load \
                .
            ;;

        podman|docker)
            log_warn "$builder doesn't support native multi-arch builds"
            log_info "Building for current architecture only..."

            local current_arch=$(uname -m)
            case "$current_arch" in
                x86_64|amd64)
                    platform="linux/amd64"
                    arch_tag="amd64"
                    ;;
                aarch64|arm64)
                    platform="linux/arm64"
                    arch_tag="arm64"
                    ;;
                *)
                    log_error "Unsupported architecture: $current_arch"
                    exit 1
                    ;;
            esac

            $builder build \
                --platform $platform \
                --tag ${IMAGE_NAME}:${IMAGE_VERSION}-${arch_tag} \
                --tag ${IMAGE_NAME}:latest \
                --file Containerfile \
                .
            ;;
    esac

    log_info "✅ Build complete!"
}

################################################################################
# Push to Registry
################################################################################

push_images() {
    local builder=$1
    local push_registry=$2

    if [ -z "$push_registry" ]; then
        log_warn "No registry specified, skipping push"
        log_info "To push images, run with --push <registry>"
        return
    fi

    log_step "Pushing images to registry: $push_registry"

    # Determine push tool
    local push_tool
    if command -v podman &> /dev/null; then
        push_tool="podman"
    elif command -v docker &> /dev/null; then
        push_tool="docker"
    else
        log_error "No push tool available"
        exit 1
    fi

    # Tag for registry
    log_info "Tagging images for registry..."
    $push_tool tag ${IMAGE_NAME}:${IMAGE_VERSION} ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}
    $push_tool tag ${IMAGE_NAME}:latest ${push_registry}/${IMAGE_NAME}:latest

    # Push
    log_info "Pushing ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}..."
    $push_tool push ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}

    log_info "Pushing ${push_registry}/${IMAGE_NAME}:latest..."
    $push_tool push ${push_registry}/${IMAGE_NAME}:latest

    # Push arch-specific tags if they exist
    if $push_tool images | grep -q "${IMAGE_NAME}:${IMAGE_VERSION}-amd64"; then
        $push_tool tag ${IMAGE_NAME}:${IMAGE_VERSION}-amd64 ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}-amd64
        $push_tool push ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}-amd64
    fi

    if $push_tool images | grep -q "${IMAGE_NAME}:${IMAGE_VERSION}-arm64"; then
        $push_tool tag ${IMAGE_NAME}:${IMAGE_VERSION}-arm64 ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}-arm64
        $push_tool push ${push_registry}/${IMAGE_NAME}:${IMAGE_VERSION}-arm64
    fi

    log_info "✅ Push complete!"
}

################################################################################
# List Built Images
################################################################################

list_images() {
    log_step "Built images:"

    if command -v podman &> /dev/null; then
        podman images | grep ${IMAGE_NAME} || log_warn "No images found"
    elif command -v docker &> /dev/null; then
        docker images | grep ${IMAGE_NAME} || log_warn "No images found"
    fi
}

################################################################################
# Main
################################################################################

main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "  Project APE - Multi-Architecture Container Build"
    echo "  RHEL 9 UBI Base | amd64 + arm64"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Parse arguments
    local push_registry=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --push)
                push_registry="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                push_registry="$2"
                shift 2
                ;;
            --help|-h)
                cat << EOF
Usage: $0 [OPTIONS]

Options:
    --push REGISTRY      Push images to registry after build
    --registry REGISTRY  Set registry URL (default: quay.io/yourorg)
    --help, -h           Show this help message

Examples:
    # Build locally only
    $0

    # Build and push to Quay.io
    $0 --push quay.io/yourorg

    # Build and push to Red Hat registry
    $0 --push registry.redhat.io/yourorg

Environment Variables:
    REGISTRY    Override default registry

EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Detect builder
    local builder=$(detect_builder)
    log_info "Detected builder: $builder"

    # Build
    build_multiarch "$builder"

    # List images
    list_images

    # Push if requested
    if [ -n "$push_registry" ]; then
        push_images "$builder" "$push_registry"
    fi

    echo ""
    log_info "════════════════════════════════════════════════════════════════"
    log_info "Build complete!"
    log_info ""
    log_info "To run locally:"
    log_info "  ./run-container.sh"
    log_info ""
    log_info "To push to registry:"
    log_info "  $0 --push $REGISTRY"
    log_info "════════════════════════════════════════════════════════════════"
}

main "$@"
