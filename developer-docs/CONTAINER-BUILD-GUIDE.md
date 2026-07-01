# Container Build & Push Guide

Comprehensive guide for building, scanning, and publishing Project APE container images.

## Quick Start

```bash
# Standard build and push (auto-detects version from README.md)
./build-and-push-containers.sh

# Build specific version
./build-and-push-containers.sh --version 4.0.2

# Build without pushing (for testing)
./build-and-push-containers.sh --build-only
```

## Prerequisites

### Required

- **Podman** or **Docker** installed
- **Registry credentials** (Quay.io authentication)

### Optional (but recommended)

- **Trivy** - Vulnerability scanning
  ```bash
  # macOS
  brew install trivy
  
  # Linux
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
  sudo apt-get update && sudo apt-get install trivy
  ```

- **Syft** - SBOM generation
  ```bash
  # macOS
  brew install syft
  
  # Linux
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
  ```

- **Cosign** - Image signing (optional)
  ```bash
  # macOS
  brew install cosign
  
  # Linux
  wget https://github.com/sigstore/cosign/releases/download/v2.2.0/cosign-linux-amd64
  sudo mv cosign-linux-amd64 /usr/local/bin/cosign
  sudo chmod +x /usr/local/bin/cosign
  ```

## Setup

### 1. Registry Authentication

```bash
# Login to Quay.io
podman login quay.io
# or
docker login quay.io

# Enter credentials when prompted
Username: jasoande
Password: [your robot account token or password]
```

**For CI/CD:** Use robot accounts or service account tokens:
1. Go to https://quay.io/organization/jasoande?tab=robots
2. Create robot account
3. Grant write permissions to `project_ape` repository
4. Use robot token for authentication

### 2. Generate Signing Keys (Optional)

If you want to sign images with Cosign:

```bash
# Generate key pair
cosign generate-key-pair

# This creates:
#   - cosign.key (private key - keep secret!)
#   - cosign.pub (public key - can be shared)

# Move keys to secure location
mkdir -p ~/.cosign
mv cosign.key ~/.cosign/
mv cosign.pub ~/.cosign/

# Set permissions
chmod 600 ~/.cosign/cosign.key
```

## Usage Examples

### Basic Builds

```bash
# Auto-detect version and build everything
./build-and-push-containers.sh

# Build specific version
./build-and-push-containers.sh --version 4.0.2

# Build for testing (no push)
./build-and-push-containers.sh --build-only

# Build and show help
./build-and-push-containers.sh --help
```

### Push Existing Images

```bash
# Push images that were built with --build-only
./build-and-push-containers.sh --push-only --version 4.0.2
```

### Security-Focused Builds

```bash
# Full security scan with SBOM
./build-and-push-containers.sh

# Quick build without security checks (development)
./build-and-push-containers.sh --skip-scan --skip-sbom

# Build with image signing
./build-and-push-containers.sh --sign

# Custom severity threshold
SCAN_SEVERITY=MEDIUM ./build-and-push-containers.sh
```

### Environment Variable Overrides

```bash
# Use different registry
REGISTRY=docker.io/myuser ./build-and-push-containers.sh

# Skip all security features
SKIP_SCAN=true SKIP_SBOM=true ./build-and-push-containers.sh

# Enable signing via environment
SIGN_IMAGES=true ./build-and-push-containers.sh --version 4.0.2
```

## What the Script Does

### 1. Pre-flight Checks
- ✅ Verifies Podman or Docker is installed
- ✅ Checks Containerfile exists
- ✅ Validates registry authentication
- ✅ Detects version from README.md or CLAUDE.md
- ✅ Checks security tool availability

### 2. Multi-Architecture Build
- 🏗️ Builds `linux/amd64` image
- 🏗️ Builds `linux/arm64` image
- 📦 Creates multi-arch manifest

### 3. Security Scanning (if Trivy installed)
- 🔍 Scans both architectures for vulnerabilities
- 📊 Generates detailed reports in `build-logs/`
- ⚠️ Prompts before pushing if CRITICAL issues found

### 4. SBOM Generation (if Syft installed)
- 📋 Generates Software Bill of Materials for each arch
- 💾 Saves JSON format in `build-logs/`
- 📈 Shows package count summary

### 5. Registry Push
- 🚀 Pushes arch-specific tags (`4.0.2-amd64`, `4.0.2-arm64`)
- 🚀 Pushes version tag (`4.0.2`)
- 🚀 Pushes latest tag (`latest`)

### 6. Image Signing (if --sign and Cosign installed)
- ✍️ Signs all arch-specific images
- ✍️ Signs manifest tags
- 🔐 Verifiable with `cosign verify`

## Output Files

All build artifacts are stored in `build-logs/`:

```
build-logs/
├── build-20260630-143022.log          # Full build log
├── scan-amd64-4.0.2.txt              # Vulnerability scan (amd64)
├── scan-arm64-4.0.2.txt              # Vulnerability scan (arm64)
├── sbom-amd64-4.0.2.json             # SBOM (amd64)
└── sbom-arm64-4.0.2.json             # SBOM (arm64)
```

## Image Tags

After successful build, the following images are available:

### Version-Specific
- `quay.io/jasoande/project_ape/project-ape:4.0.2` (multi-arch manifest)
- `quay.io/jasoande/project_ape/project-ape:4.0.2-amd64` (amd64 only)
- `quay.io/jasoande/project_ape/project-ape:4.0.2-arm64` (arm64 only)

### Latest
- `quay.io/jasoande/project_ape/project-ape:latest` (multi-arch manifest)

## Pull Commands

```bash
# Pull latest (multi-arch - automatically selects correct arch)
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Pull specific version (multi-arch)
podman pull quay.io/jasoande/project_ape/project-ape:4.0.2

# Pull architecture-specific
podman pull quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
podman pull quay.io/jasoande/project_ape/project-ape:4.0.2-arm64
```

## Verify Signed Images (if signed)

```bash
# Verify image signature
cosign verify --key ~/.cosign/cosign.pub quay.io/jasoande/project_ape/project-ape:4.0.2

# View SBOM
cosign download sbom quay.io/jasoande/project_ape/project-ape:4.0.2
```

## Troubleshooting

### "Authentication failed"

**Problem:** Not logged into container registry

**Solution:**
```bash
podman login quay.io
# or
docker login quay.io
```

### "Trivy not found"

**Problem:** Trivy not installed, but security scanning was requested

**Options:**
1. Install Trivy (recommended):
   ```bash
   brew install trivy  # macOS
   ```

2. Skip scanning (for quick builds):
   ```bash
   ./build-and-push-containers.sh --skip-scan
   ```

### "Buildx not available"

**Problem:** Docker buildx not enabled (Docker only)

**Solution:**
```bash
# Enable buildx
docker buildx create --use

# Or use Podman instead (supports multi-arch natively)
brew install podman
```

### "Version not detected"

**Problem:** Script can't auto-detect version from README.md or CLAUDE.md

**Solution:**
```bash
# Specify version manually
./build-and-push-containers.sh --version 4.0.2
```

### "Build failed - out of disk space"

**Problem:** Not enough disk space for multi-arch builds

**Solution:**
```bash
# Clean up old images
podman image prune -a

# Or build single arch only (edit script to remove one arch)
```

### "Manifest push failed"

**Problem:** Podman manifest issues (rare)

**Solution:**
```bash
# Remove and recreate manifest
podman manifest rm quay.io/jasoande/project_ape/project-ape:4.0.2
./build-and-push-containers.sh --version 4.0.2
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Containers

on:
  push:
    tags:
      - 'v*'

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman

      - name: Install security tools
        run: |
          # Trivy
          wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
          echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
          sudo apt-get update && sudo apt-get install -y trivy
          
          # Syft
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

      - name: Login to Quay.io
        run: |
          echo "${{ secrets.QUAY_PASSWORD }}" | podman login quay.io -u "${{ secrets.QUAY_USERNAME }}" --password-stdin

      - name: Extract version from tag
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Build and push
        run: |
          ./build-and-push-containers.sh --version ${{ steps.version.outputs.VERSION }}

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-logs
          path: build-logs/
```

### GitLab CI Example

```yaml
build-containers:
  stage: build
  image: quay.io/podman/stable:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache bash curl jq
    - curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
    - wget -qO /usr/local/bin/trivy https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.tar.gz
  script:
    - echo "$QUAY_PASSWORD" | podman login quay.io -u "$QUAY_USERNAME" --password-stdin
    - ./build-and-push-containers.sh
  artifacts:
    paths:
      - build-logs/
    expire_in: 30 days
  only:
    - tags
```

## Best Practices

### Version Management
- ✅ Use semantic versioning (MAJOR.MINOR.PATCH)
- ✅ Update version in README.md badge before building
- ✅ Tag git commits with version: `git tag v4.0.2`
- ✅ Keep CHANGELOG.md updated

### Security
- ✅ Always scan images before pushing to production
- ✅ Review vulnerability reports in `build-logs/`
- ✅ Fix CRITICAL and HIGH severity issues before deploying
- ✅ Generate SBOMs for compliance and audit trails
- ✅ Sign images for supply chain security

### Registry Hygiene
- ✅ Don't push untagged images to registry
- ✅ Clean up old versions periodically
- ✅ Use robot accounts for CI/CD (not personal credentials)
- ✅ Enable image scanning in Quay.io repository settings

### Build Optimization
- ✅ Use multi-stage builds (already in Containerfile.debian)
- ✅ Leverage layer caching
- ✅ Keep base images updated
- ✅ Review image size: `podman images | grep project-ape`

## Advanced Usage

### Custom Registry

```bash
# Build for different registry
REGISTRY=docker.io/myusername IMAGE_NAME=project-ape ./build-and-push-containers.sh
```

### Partial Builds

```bash
# Build only, no push (for testing)
./build-and-push-containers.sh --build-only --version 4.0.2-rc1

# Test locally
podman run --rm quay.io/jasoande/project_ape/project-ape:4.0.2-rc1 --help

# Push after testing
./build-and-push-containers.sh --push-only --version 4.0.2-rc1
```

### Debug Mode

```bash
# Enable bash debug output
bash -x ./build-and-push-containers.sh --version 4.0.2 2>&1 | tee debug.log
```

### Rebuild with Different Base Image

```bash
# Edit Containerfile to use different Python version
sed -i 's/python:3.13-slim/python:3.12-slim/' developer-docs/Containerfile.debian

# Build and tag as experimental
./build-and-push-containers.sh --version 4.0.2-python312
```

## Security Scan Interpretation

### Severity Levels

- **CRITICAL** - Immediate action required, patch ASAP
- **HIGH** - Important vulnerabilities, plan remediation
- **MEDIUM** - Moderate risk, address in next release
- **LOW** - Minor issues, fix when convenient

### Sample Scan Output

```
scan-amd64-4.0.2.txt:
┌────────────────┬─────────────────┬──────────┬───────────────────┐
│    Library     │  Vulnerability  │ Severity │    Installed      │
├────────────────┼─────────────────┼──────────┼───────────────────┤
│ openssl        │ CVE-2024-xxxxx  │ HIGH     │ 3.0.11-1          │
│ libc6          │ CVE-2024-xxxxx  │ MEDIUM   │ 2.36-9            │
└────────────────┴─────────────────┴──────────┴───────────────────┘
```

### Remediation Steps

1. **Update base image** to get patched system libraries
2. **Rebuild dependencies** with updated packages
3. **Rescan** to verify fixes
4. **Document** any accepted risks

## Maintenance

### Regular Tasks

**Weekly:**
- Pull latest base image updates
- Rebuild containers with updated dependencies
- Review security scan reports

**Monthly:**
- Review and prune old image versions from registry
- Update security scanning tools (Trivy, Syft)
- Audit SBOM for license compliance

**Per Release:**
- Update version in README.md
- Run full build with all security checks
- Tag git commit
- Update CHANGELOG.md
- Verify deployment on test environment

## Support

For issues or questions:
- Check build logs in `build-logs/`
- Review Containerfile: `developer-docs/Containerfile.debian`
- Consult main docs: `CLAUDE.md`
- File issue on GitHub repository

## References

- [Podman Documentation](https://docs.podman.io/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
- [Syft SBOM Tool](https://github.com/anchore/syft)
- [Cosign Signing](https://github.com/sigstore/cosign)
- [Quay.io Documentation](https://docs.quay.io/)
