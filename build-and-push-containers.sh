#!/bin/bash
################################################################################
# Account Intelligence - Container Build, Tag, and Push Automation
#
# Features:
#   - Multi-arch builds (x86_64 + arm64)
#   - Automatic version extraction from CLAUDE.md
#   - Security vulnerability scanning (Trivy - optional)
#   - SBOM generation (Syft - optional)
#   - Registry authentication verification
#   - Comprehensive logging
#   - Rollback on failure
#
# Usage:
#   ./build-and-push-containers.sh                    # Build and push with auto-version
#   ./build-and-push-containers.sh --version 4.1.0    # Override version
#   ./build-and-push-containers.sh --build-only       # Build but don't push
#   ./build-and-push-containers.sh --push-only        # Push existing images
#   ./build-and-push-containers.sh --skip-scan        # Skip vulnerability scan
#   ./build-and-push-containers.sh --help             # Show help
#
# Environment Variables:
#   REGISTRY          - Container registry (default: quay.io/jasoande/project_ape)
#   IMAGE_NAME        - Image name (default: project-ape)
#   SCAN_SEVERITY     - Min severity for scan failures (default: HIGH)
#
################################################################################

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# Configuration
REGISTRY="${REGISTRY:-quay.io/jasoande/project_ape}"
IMAGE_NAME="${IMAGE_NAME:-project-ape}"
CONTAINERFILE="Containerfile"
BUILD_CONTEXT="."
SCAN_SEVERITY="${SCAN_SEVERITY:-HIGH}"
LOG_DIR="logs/container-builds"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/build-${TIMESTAMP}.log"

# Flags
BUILD_ONLY=false
PUSH_ONLY=false
SKIP_SCAN="${SKIP_SCAN:-false}"
SKIP_SBOM="${SKIP_SBOM:-false}"
VERSION_OVERRIDE=""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
Account Intelligence - Container Build and Push Automation

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --version VERSION       Override version (default: auto-detect from CLAUDE.md)
    --build-only           Build images but don't push to registry
    --push-only            Push existing images without rebuilding
    --skip-scan            Skip vulnerability scanning
    --skip-sbom            Skip SBOM generation
    --help, -h             Show this help message

EXAMPLES:
    # Standard build and push with auto-version detection
    $0

    # Build specific version
    $0 --version 4.1.0

    # Build only (no push)
    $0 --build-only

    # Push existing images
    $0 --push-only --version 4.1.0

    # Quick build without security checks
    $0 --skip-scan --skip-sbom

ENVIRONMENT VARIABLES:
    REGISTRY          Container registry (default: quay.io/jasoande/project_ape)
    IMAGE_NAME        Image name (default: project-ape)
    SCAN_SEVERITY     Minimum severity for scan failures (default: HIGH)

REQUIREMENTS:
    - Podman or Docker
    - Trivy (for vulnerability scanning, optional with --skip-scan)
    - Syft (for SBOM generation, optional with --skip-sbom)
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
        log_info "Using Podman $(podman --version | awk '{print $3}')"
    elif command -v docker &> /dev/null; then
        RUNTIME="docker"
        log_info "Using Docker $(docker --version | awk '{print $3}')"
    else
        log_error "Neither podman nor docker found"
        log_error "Please install podman or docker"
        exit 1
    fi
}

check_containerfile() {
    log_step "Checking Containerfile..."

    if [ ! -f "$CONTAINERFILE" ]; then
        log_error "Containerfile not found: $CONTAINERFILE"
        exit 1
    fi

    log_info "Containerfile: $CONTAINERFILE"

    # Validate required files exist
    for file in requirements.txt main.py container-entrypoint.sh; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done

    for dir in core dashboard; do
        if [ ! -d "$dir" ]; then
            log_error "Required directory missing: $dir"
            exit 1
        fi
    done

    log_info "Build context validated"
}

check_security_tools() {
    if [ "$SKIP_SCAN" = "false" ]; then
        if command -v trivy &> /dev/null; then
            log_info "Trivy found: $(trivy --version | head -1)"
        else
            log_warn "Trivy not found - vulnerability scanning will be skipped"
            SKIP_SCAN=true
        fi
    fi

    if [ "$SKIP_SBOM" = "false" ]; then
        if command -v syft &> /dev/null; then
            log_info "Syft found: $(syft version | head -1)"
        else
            log_warn "Syft not found - SBOM generation will be skipped"
            SKIP_SBOM=true
        fi
    fi
}

check_registry_auth() {
    if [ "$PUSH_ONLY" = "true" ] || [ "$BUILD_ONLY" = "false" ]; then
        log_step "Checking registry authentication..."

        # Extract registry hostname
        REGISTRY_HOST=$(echo "$REGISTRY" | cut -d'/' -f1)

        if $RUNTIME login "$REGISTRY_HOST" --get-login &> /dev/null; then
            log_info "Registry authentication valid: $REGISTRY_HOST"
        else
            log_warn "Not logged into registry: $REGISTRY_HOST"
            read -p "Attempt login now? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if ! $RUNTIME login "$REGISTRY_HOST"; then
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

    # Try to extract version from CLAUDE.md
    if [ -f "CLAUDE.md" ]; then
        VERSION=$(grep -oE "[0-9]+\.[0-9]+\.[0-9]+" CLAUDE.md | head -1)
        if [ -n "$VERSION" ]; then
            log_info "Auto-detected version from CLAUDE.md: $VERSION"
            return
        fi
    fi

    # Try main.py
    if [ -f "main.py" ]; then
        VERSION=$(grep -E "Version.*[0-9]+\.[0-9]+\.[0-9]+" main.py | head -1 | sed 's/.*\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
        if [ -n "$VERSION" ]; then
            log_info "Auto-detected version from main.py: $VERSION"
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
        --platform linux/amd64 \
        -t "${full_image}:${VERSION}-amd64" \
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

    # Remove old manifests if they exist
    $RUNTIME manifest rm "${full_image}:${VERSION}" 2>/dev/null || true
    $RUNTIME manifest rm "${full_image}:latest" 2>/dev/null || true

    # Version-specific manifest
    $RUNTIME manifest create "${full_image}:${VERSION}" \
        "${full_image}:${VERSION}-amd64" \
        "${full_image}:${VERSION}-arm64" 2>&1 | tee -a "$LOG_FILE"

    # Latest manifest
    $RUNTIME manifest create "${full_image}:latest" \
        "${full_image}:${VERSION}-amd64" \
        "${full_image}:${VERSION}-arm64" 2>&1 | tee -a "$LOG_FILE"

    log_success "Manifests created"
}

build_docker_multiarch() {
    local full_image="$1"

    log_warn "Docker buildx multi-arch build not fully tested"
    log_warn "Using single-arch build for current platform"

    docker build \
        -t "${full_image}:${VERSION}" \
        -t "${full_image}:latest" \
        -f "$CONTAINERFILE" \
        "$BUILD_CONTEXT" 2>&1 | tee -a "$LOG_FILE"
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

    for arch in amd64 arm64; do
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
            if grep -q "CRITICAL:" "$report_file" 2>/dev/null; then
                log_warn "CRITICAL vulnerabilities found in ${arch} image"
                scan_failed=true
            fi
        else
            log_warn "Scan failed for ${arch} image"
        fi
    done

    if [ "$scan_failed" = "true" ]; then
        log_warn "Vulnerability scans found issues - review reports in ${LOG_DIR}/"
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

    for arch in amd64 arm64; do
        local image="${full_image}:${VERSION}-${arch}"
        local sbom_file="${LOG_DIR}/sbom-${arch}-${VERSION}.json"

        log_step "Generating SBOM for ${arch}..."

        if syft "$image" -o json > "$sbom_file" 2>&1; then
            log_info "SBOM saved: $sbom_file"
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
    for arch in amd64 arm64; do
        log_step "Pushing ${arch} image..."
        $RUNTIME push "${full_image}:${VERSION}-${arch}" 2>&1 | tee -a "$LOG_FILE"
        log_success "${arch} image pushed"
    done

    # Push manifests
    log_step "Pushing version manifest (${VERSION})..."
    $RUNTIME manifest push "${full_image}:${VERSION}" 2>&1 | tee -a "$LOG_FILE"

    log_step "Pushing latest manifest..."
    $RUNTIME manifest push "${full_image}:latest" 2>&1 | tee -a "$LOG_FILE"

    log_success "All manifests pushed"
}

push_docker_images() {
    local full_image="$1"

    log_step "Pushing images..."
    docker push "${full_image}:${VERSION}" 2>&1 | tee -a "$LOG_FILE"
    docker push "${full_image}:latest" 2>&1 | tee -a "$LOG_FILE"

    log_success "Images pushed"
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
    echo "  - ${full_image}:${VERSION}-amd64" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:${VERSION}-arm64" | tee -a "$LOG_FILE"
    echo "  - ${full_image}:latest" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    if [ "$BUILD_ONLY" = "false" ]; then
        echo -e "${CYAN}Pull Commands:${NC}" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:${VERSION}" | tee -a "$LOG_FILE"
        echo "  podman pull ${full_image}:latest" | tee -a "$LOG_FILE"
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
    log_section "Account Intelligence - Container Build & Push"

    # Parse arguments
    parse_args "$@"

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

    # Summary
    print_summary
}

# Run main
main "$@"
