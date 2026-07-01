#!/bin/bash
################################################################################
# Project APE - Container Build, Tag, and Push Automation
#
# Features:
#   - Multi-arch builds (x86_64 + arm64)
#   - Automatic version extraction and tagging
#   - Security vulnerability scanning (Trivy)
#   - SBOM generation (Syft)
#   - Image signing (Cosign - optional)
#   - Registry authentication verification
#   - Rollback on failure
#   - Comprehensive logging
#
# Usage:
#   ./build-and-push-containers.sh                    # Build and push with auto-version
#   ./build-and-push-containers.sh --version 4.0.2    # Override version
#   ./build-and-push-containers.sh --build-only       # Build but don't push
#   ./build-and-push-containers.sh --push-only        # Push existing images
#   ./build-and-push-containers.sh --skip-scan        # Skip vulnerability scan
#   ./build-and-push-containers.sh --sign             # Sign images with Cosign
#   ./build-and-push-containers.sh --help             # Show help
#
# Environment Variables:
#   REGISTRY          - Container registry (default: quay.io/jasoande/project_ape)
#   IMAGE_NAME        - Image name (default: project-ape)
#   SCAN_SEVERITY     - Min severity for scan failures (default: HIGH)
#   SKIP_SCAN         - Skip vulnerability scanning (default: false)
#   SKIP_SBOM         - Skip SBOM generation (default: false)
#   SIGN_IMAGES       - Sign images with Cosign (default: false)
#
################################################################################

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# Configuration
REGISTRY="${REGISTRY:-quay.io/jasoande/project_ape}"
IMAGE_NAME="${IMAGE_NAME:-project-ape}"
CONTAINERFILE="developer-docs/Containerfile.debian"
BUILD_CONTEXT="."
SCAN_SEVERITY="${SCAN_SEVERITY:-HIGH}"
LOG_DIR="build-logs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/build-${TIMESTAMP}.log"

# Flags
BUILD_ONLY=false
PUSH_ONLY=false
SKIP_SCAN="${SKIP_SCAN:-false}"
SKIP_SBOM="${SKIP_SBOM:-false}"
SIGN_IMAGES="${SIGN_IMAGES:-false}"
VERSION_OVERRIDE=""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Logging Functions
################################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}  $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

################################################################################
# Help
################################################################################

show_help() {
    cat << EOF
Project APE - Container Build and Push Automation

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --version VERSION       Override version (default: auto-detect from README.md)
    --build-only           Build images but don't push to registry
    --push-only            Push existing images without rebuilding
    --skip-scan            Skip vulnerability scanning
    --skip-sbom            Skip SBOM generation
    --sign                 Sign images with Cosign (requires cosign installed)
    --help, -h             Show this help message

EXAMPLES:
    # Standard build and push with auto-version detection
    $0

    # Build specific version
    $0 --version 4.0.2

    # Build only (no push)
    $0 --build-only

    # Push existing images
    $0 --push-only --version 4.0.2

    # Build and push with image signing
    $0 --sign

    # Quick build without security checks
    $0 --skip-scan --skip-sbom

ENVIRONMENT VARIABLES:
    REGISTRY          Container registry (default: quay.io/jasoande/project_ape)
    IMAGE_NAME        Image name (default: project-ape)
    SCAN_SEVERITY     Minimum severity for scan failures (default: HIGH)
    SKIP_SCAN         Skip vulnerability scanning (default: false)
    SKIP_SBOM         Skip SBOM generation (default: false)
    SIGN_IMAGES       Sign images with Cosign (default: false)

REQUIREMENTS:
    - Podman or Docker
    - Trivy (for vulnerability scanning, optional with --skip-scan)
    - Syft (for SBOM generation, optional with --skip-sbom)
    - Cosign (for image signing, optional unless --sign used)
    - Registry credentials (podman login or docker login)

OUTPUT:
    Build logs: ${LOG_DIR}/build-YYYYMMDD-HHMMSS.log
    SBOM files: ${LOG_DIR}/sbom-{arch}-{version}.json
    Scan reports: ${LOG_DIR}/scan-{arch}-{version}.txt

EOF
    exit 0
}

################################################################################
# Parse Arguments
################################################################################

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --version)
                VERSION_OVERRIDE="$2"
                shift 2
                ;;
            --build-only)
                BUILD_ONLY=true
                shift
                ;;
            --push-only)
                PUSH_ONLY=true
                shift
                ;;
            --skip-scan)
                SKIP_SCAN=true
                shift
                ;;
            --skip-sbom)
                SKIP_SBOM=true
                shift
                ;;
            --sign)
                SIGN_IMAGES=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

################################################################################
# Pre-flight Checks
################################################################################

check_runtime() {
    log_step "Checking container runtime..."

    if command -v podman &> /dev/null; then
        RUNTIME="podman"
        log_info "Using Podman"
    elif command -v docker &> /dev/null; then
        RUNTIME="docker"
        log_info "Using Docker"
    else
        log_error "Neither podman nor docker found"
        log_error "Please install podman or docker"
        exit 1
    fi

    # Check buildx support for multi-arch
    if [ "$RUNTIME" = "docker" ]; then
        if ! docker buildx version &> /dev/null; then
            log_warn "Docker buildx not available - falling back to single-arch builds"
        fi
    fi
}

check_containerfile() {
    log_step "Checking Containerfile..."

    if [ ! -f "$CONTAINERFILE" ]; then
        log_error "Containerfile not found: $CONTAINERFILE"
        exit 1
    fi

    log_info "Containerfile: $CONTAINERFILE"
}

check_security_tools() {
    if [ "$SKIP_SCAN" = "false" ]; then
        log_step "Checking security scanning tools..."

        if ! command -v trivy &> /dev/null; then
            log_warn "Trivy not found - vulnerability scanning will be skipped"
            log_warn "Install: https://github.com/aquasecurity/trivy#installation"
            SKIP_SCAN=true
        else
            log_info "Trivy found: $(trivy --version | head -1)"
        fi
    fi

    if [ "$SKIP_SBOM" = "false" ]; then
        log_step "Checking SBOM tools..."

        if ! command -v syft &> /dev/null; then
            log_warn "Syft not found - SBOM generation will be skipped"
            log_warn "Install: https://github.com/anchore/syft#installation"
            SKIP_SBOM=true
        else
            log_info "Syft found: $(syft version | head -1)"
        fi
    fi

    if [ "$SIGN_IMAGES" = "true" ]; then
        log_step "Checking image signing tools..."

        if ! command -v cosign &> /dev/null; then
            log_error "Cosign not found but --sign was specified"
            log_error "Install: https://github.com/sigstore/cosign#installation"
            exit 1
        else
            log_info "Cosign found: $(cosign version 2>&1 | grep GitVersion || echo 'installed')"
        fi
    fi
}

check_registry_auth() {
    if [ "$PUSH_ONLY" = "true" ] || [ "$BUILD_ONLY" = "false" ]; then
        log_step "Checking registry authentication..."

        # Try to login to verify credentials
        if $RUNTIME login "$REGISTRY" --get-login &> /dev/null; then
            log_info "Registry authentication valid: $REGISTRY"
        else
            log_warn "Not logged into registry: $REGISTRY"
            log_warn "Run: $RUNTIME login $REGISTRY"

            read -p "Attempt login now? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if ! $RUNTIME login "$REGISTRY"; then
                    log_error "Registry login failed"
                    exit 1
                fi
                log_success "Registry login successful"
            else
                log_error "Cannot proceed without registry authentication"
                exit 1
            fi
        fi
    fi
}

################################################################################
# Version Detection
################################################################################

detect_version() {
    log_step "Detecting version..."

    if [ -n "$VERSION_OVERRIDE" ]; then
        VERSION="$VERSION_OVERRIDE"
        log_info "Using override version: $VERSION"
        return
    fi

    # Try to extract version from README.md
    if [ -f "README.md" ]; then
        VERSION=$(grep -E "version-[0-9]+\.[0-9]+\.[0-9]+" README.md | head -1 | sed 's/.*version-\([0-9.]*\).*/\1/')
        if [ -n "$VERSION" ]; then
            log_info "Auto-detected version from README.md: $VERSION"
            return
        fi
    fi

    # Try CLAUDE.md
    if [ -f "CLAUDE.md" ]; then
        VERSION=$(grep -E "Current Version.*[0-9]+\.[0-9]+\.[0-9]+" CLAUDE.md | head -1 | sed 's/.*\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
        if [ -n "$VERSION" ]; then
            log_info "Auto-detected version from CLAUDE.md: $VERSION"
            return
        fi
    fi

    # Fallback to git tag
    if git describe --tags --abbrev=0 &> /dev/null; then
        VERSION=$(git describe --tags --abbrev=0 | sed 's/^v//')
        log_info "Using git tag version: $VERSION"
        return
    fi

    log_error "Could not detect version"
    log_error "Use --version to specify manually"
    exit 1
}

################################################################################
# Build Functions
################################################################################

build_multiarch() {
    log_section "Building Multi-Architecture Images"

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    if [ "$RUNTIME" = "podman" ]; then
        build_podman_multiarch "$full_image"
    else
        build_docker_multiarch "$full_image"
    fi
}

build_podman_multiarch() {
    local full_image="$1"

    # Podman approach: Build each arch separately, then create manifest
    log_step "Building x86_64 image..."
    $RUNTIME build \
        --platform linux/x86_64 \
        -t "${full_image}:${VERSION}-x86_64" \
        -f "$CONTAINERFILE" \
        "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"

    log_step "Building arm64 image..."
    $RUNTIME build \
        --platform linux/arm64 \
        -t "${full_image}:${VERSION}-arm64" \
        -f "$CONTAINERFILE" \
        "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"

    log_success "Multi-arch builds complete"

    # Create manifest for latest and version tags
    log_step "Creating multi-arch manifest..."

    # Version-specific manifest
    $RUNTIME manifest create "${full_image}:${VERSION}" \
        "${full_image}:${VERSION}-x86_64" \
        "${full_image}:${VERSION}-arm64" 2>&1 | tee -a "$LOG_FILE" || true

    # Latest manifest
    $RUNTIME manifest create "${full_image}:latest" \
        "${full_image}:${VERSION}-x86_64" \
        "${full_image}:${VERSION}-arm64" 2>&1 | tee -a "$LOG_FILE" || true

    log_success "Manifests created"
}

build_docker_multiarch() {
    local full_image="$1"

    # Docker buildx approach: Single command for multi-arch
    if docker buildx version &> /dev/null; then
        log_step "Building multi-arch with Docker buildx..."

        # Create builder if not exists
        docker buildx create --name ape-builder --use 2>&1 | tee -a "$LOG_FILE" || true

        # Build and load (can't push multi-arch to local registry)
        docker buildx build \
            --platform linux/x86_64,linux/arm64 \
            -t "${full_image}:${VERSION}" \
            -t "${full_image}:latest" \
            --load \
            -f "$CONTAINERFILE" \
            "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"

        log_success "Multi-arch build complete"
    else
        # Fallback to single-arch
        log_warn "Docker buildx not available - building for current arch only"
        docker build \
            -t "${full_image}:${VERSION}" \
            -t "${full_image}:latest" \
            -f "$CONTAINERFILE" \
            "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"
    fi
}

################################################################################
# Security Scanning
################################################################################

scan_images() {
    if [ "$SKIP_SCAN" = "true" ]; then
        log_warn "Skipping vulnerability scanning (--skip-scan)"
        return
    fi

    log_section "Security Vulnerability Scanning"

    local full_image="${REGISTRY}/${IMAGE_NAME}"
    local scan_failed=false

    for arch in x86_64 arm64; do
        local image="${full_image}:${VERSION}-${arch}"
        local report_file="${LOG_DIR}/scan-${arch}-${VERSION}.txt"

        log_step "Scanning ${arch} image..."

        if trivy image \
            --severity "${SCAN_SEVERITY},CRITICAL" \
            --exit-code 0 \
            --format table \
            --output "$report_file" \
            "$image" 2>&1 | tee -a "$LOG_FILE"; then

            log_info "Scan report saved: $report_file"

            # Check for critical vulnerabilities
            if grep -q "CRITICAL:" "$report_file"; then
                log_warn "CRITICAL vulnerabilities found in ${arch} image"
                scan_failed=true
            fi
        else
            log_error "Scan failed for ${arch} image"
            scan_failed=true
        fi
    done

    if [ "$scan_failed" = "true" ]; then
        log_warn "Vulnerability scans found issues - review reports in ${LOG_DIR}/"
        read -p "Continue with push anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Build aborted due to security vulnerabilities"
            exit 1
        fi
    else
        log_success "All images passed vulnerability scanning"
    fi
}

################################################################################
# SBOM Generation
################################################################################

generate_sbom() {
    if [ "$SKIP_SBOM" = "true" ]; then
        log_warn "Skipping SBOM generation (--skip-sbom)"
        return
    fi

    log_section "Generating Software Bill of Materials (SBOM)"

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    for arch in x86_64 arm64; do
        local image="${full_image}:${VERSION}-${arch}"
        local sbom_file="${LOG_DIR}/sbom-${arch}-${VERSION}.json"

        log_step "Generating SBOM for ${arch}..."

        if syft "$image" -o json > "$sbom_file" 2>&1; then
            log_info "SBOM saved: $sbom_file"

            # Show package summary
            local pkg_count=$(jq '.artifacts | length' "$sbom_file" 2>/dev/null || echo "unknown")
            log_info "Packages: $pkg_count"
        else
            log_warn "SBOM generation failed for ${arch}"
        fi
    done

    log_success "SBOM generation complete"
}

################################################################################
# Push Functions
################################################################################

push_images() {
    if [ "$BUILD_ONLY" = "true" ]; then
        log_warn "Skipping push (--build-only)"
        return
    fi

    log_section "Pushing Images to Registry"

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    if [ "$RUNTIME" = "podman" ]; then
        push_podman_images "$full_image"
    else
        push_docker_images "$full_image"
    fi
}

push_podman_images() {
    local full_image="$1"

    # Push individual arch images
    for arch in x86_64 arm64; do
        log_step "Pushing ${arch} image..."
        $RUNTIME push "${full_image}:${VERSION}-${arch}" 2>&1 | tee -a "$LOG_FILE"
        log_success "${arch} image pushed"
    done

    # Push manifests
    log_step "Pushing version manifest..."
    $RUNTIME manifest push "${full_image}:${VERSION}" 2>&1 | tee -a "$LOG_FILE"

    log_step "Pushing latest manifest..."
    $RUNTIME manifest push "${full_image}:latest" 2>&1 | tee -a "$LOG_FILE"

    log_success "All manifests pushed"
}

push_docker_images() {
    local full_image="$1"

    if docker buildx version &> /dev/null; then
        log_step "Pushing multi-arch images with buildx..."

        # Rebuild and push (buildx requirement)
        docker buildx build \
            --platform linux/x86_64,linux/arm64 \
            -t "${full_image}:${VERSION}" \
            -t "${full_image}:latest" \
            --push \
            -f "$CONTAINERFILE" \
            "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"
    else
        log_step "Pushing current-arch image..."
        docker push "${full_image}:${VERSION}" 2>&1 | tee -a "$LOG_FILE"
        docker push "${full_image}:latest" 2>&1 | tee -a "$LOG_FILE"
    fi

    log_success "Images pushed"
}

################################################################################
# Image Signing
################################################################################

sign_images() {
    if [ "$SIGN_IMAGES" != "true" ]; then
        return
    fi

    log_section "Signing Images with Cosign"

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    for arch in x86_64 arm64; do
        local image="${full_image}:${VERSION}-${arch}"

        log_step "Signing ${arch} image..."

        if cosign sign --key cosign.key "$image" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "${arch} image signed"
        else
            log_warn "Failed to sign ${arch} image"
        fi
    done

    # Sign manifests
    log_step "Signing version manifest..."
    cosign sign --key cosign.key "${full_image}:${VERSION}" 2>&1 | tee -a "$LOG_FILE" || log_warn "Manifest signing failed"

    log_step "Signing latest manifest..."
    cosign sign --key cosign.key "${full_image}:latest" 2>&1 | tee -a "$LOG_FILE" || log_warn "Manifest signing failed"

    log_success "Image signing complete"
}

################################################################################
# Rollback
################################################################################

rollback() {
    log_error "Build/Push failed - initiating rollback"

    # Note: We don't delete remote images on rollback as they may be in use
    # We only clean up local artifacts

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    if [ "$BUILD_ONLY" = "false" ] && [ "$PUSH_ONLY" = "false" ]; then
        log_step "Cleaning up local images..."

        $RUNTIME rmi "${full_image}:${VERSION}" 2>/dev/null || true
        $RUNTIME rmi "${full_image}:${VERSION}-x86_64" 2>/dev/null || true
        $RUNTIME rmi "${full_image}:${VERSION}-arm64" 2>/dev/null || true

        if [ "$RUNTIME" = "podman" ]; then
            $RUNTIME manifest rm "${full_image}:${VERSION}" 2>/dev/null || true
        fi
    fi

    log_warn "Local cleanup complete - remote images (if any) were NOT removed"
    exit 1
}

################################################################################
# Summary
################################################################################

print_summary() {
    log_section "Build Summary"

    local full_image="${REGISTRY}/${IMAGE_NAME}"

    echo -e "${GREEN}Version:${NC} $VERSION" | tee -a "$LOG_FILE"
    echo -e "${GREEN}Registry:${NC} $REGISTRY" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    echo -e "${CYAN}Tagged Images:${NC}" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:${VERSION}" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:${VERSION}-x86_64" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:${VERSION}-arm64" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:latest" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    if [ "$BUILD_ONLY" = "false" ]; then
        echo -e "${CYAN}Pull Commands:${NC}" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:${VERSION}" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:${VERSION}-x86_64" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:${VERSION}-arm64" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:latest" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi

    if [ "$SKIP_SCAN" = "false" ]; then
        echo -e "${CYAN}Security Reports:${NC}" | tee -a "$LOG_FILE"
        echo "  - ${LOG_DIR}/scan-x86_64-${VERSION}.txt" | tee -a "$LOG_FILE"
        echo "  - ${LOG_DIR}/scan-arm64-${VERSION}.txt" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi

    if [ "$SKIP_SBOM" = "false" ]; then
        echo -e "${CYAN}SBOM Files:${NC}" | tee -a "$LOG_FILE"
        echo "  - ${LOG_DIR}/sbom-x86_64-${VERSION}.json" | tee -a "$LOG_FILE"
        echo "  - ${LOG_DIR}/sbom-arm64-${VERSION}.json" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi

    echo -e "${CYAN}Build Log:${NC}" | tee -a "$LOG_FILE"
    echo "  - ${LOG_FILE}" | tee -a "$LOG_FILE"
    echo ""

    log_success "Container build and push complete!"
}

################################################################################
# Main
################################################################################

main() {
    # Setup
    mkdir -p "$LOG_DIR"

    # Banner
    log_section "Project APE - Container Build & Push Automation"

    # Parse arguments
    parse_args "$@"

    # Set up error handling
    trap rollback ERR

    # Pre-flight checks
    if [ "$PUSH_ONLY" = "false" ]; then
        check_runtime
        check_containerfile
        check_security_tools
    fi

    check_registry_auth

    # Detect version
    detect_version

    # Build
    if [ "$PUSH_ONLY" = "false" ]; then
        build_multiarch
        scan_images
        generate_sbom
    fi

    # Push
    push_images

    # Sign
    sign_images

    # Summary
    print_summary
}

# Run main
main "$@"
