# Container Build Examples

Real-world examples of using the build automation script.

## Example 1: First-Time Setup

Complete walkthrough for first-time users.

### 1.1 Install Prerequisites

```bash
# macOS
brew install podman trivy syft

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y podman

# Install Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install -y trivy

# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

### 1.2 Registry Authentication

```bash
# Login to Quay.io
podman login quay.io

# Enter credentials
Username: jasoande
Password: [enter your token]

# Verify login
podman login quay.io --get-login
# Output: jasoande
```

### 1.3 Update Version

```bash
# Edit README.md to update version badge
vim README.md

# Change:
# [![Version](https://img.shields.io/badge/version-3.0.4-blue.svg)]
# To:
# [![Version](https://img.shields.io/badge/version-4.0.2-blue.svg)]
```

### 1.4 Run Build

```bash
# Make script executable
chmod +x build-and-push-containers.sh

# Run build
./build-and-push-containers.sh

# Expected output:
═══════════════════════════════════════════════════════════════
  Project APE - Container Build & Push Automation
═══════════════════════════════════════════════════════════════

[STEP] Checking container runtime...
[INFO] Using Podman
[STEP] Checking Containerfile...
[INFO] Containerfile: developer-docs/Containerfile.debian
[STEP] Checking security scanning tools...
[INFO] Trivy found: Version: 0.48.0
[STEP] Checking SBOM tools...
[INFO] Syft found: 0.99.0
[STEP] Checking registry authentication...
[INFO] Registry authentication valid: quay.io/jasoande/project_ape
[STEP] Detecting version...
[INFO] Auto-detected version from README.md: 4.0.2

═══════════════════════════════════════════════════════════════
  Building Multi-Architecture Images
═══════════════════════════════════════════════════════════════

[STEP] Building amd64 image...
... [build output] ...
[STEP] Building arm64 image...
... [build output] ...
[STEP] Creating multi-arch manifest...
[SUCCESS] Manifests created

═══════════════════════════════════════════════════════════════
  Security Vulnerability Scanning
═══════════════════════════════════════════════════════════════

[STEP] Scanning amd64 image...
[INFO] Scan report saved: build-logs/scan-amd64-4.0.2.txt
[STEP] Scanning arm64 image...
[INFO] Scan report saved: build-logs/scan-arm64-4.0.2.txt
[SUCCESS] All images passed vulnerability scanning

═══════════════════════════════════════════════════════════════
  Generating Software Bill of Materials (SBOM)
═══════════════════════════════════════════════════════════════

[STEP] Generating SBOM for amd64...
[INFO] SBOM saved: build-logs/sbom-amd64-4.0.2.json
[INFO] Packages: 247
[STEP] Generating SBOM for arm64...
[INFO] SBOM saved: build-logs/sbom-arm64-4.0.2.json
[INFO] Packages: 247
[SUCCESS] SBOM generation complete

═══════════════════════════════════════════════════════════════
  Pushing Images to Registry
═══════════════════════════════════════════════════════════════

[STEP] Pushing amd64 image...
[SUCCESS] amd64 image pushed
[STEP] Pushing arm64 image...
[SUCCESS] arm64 image pushed
[STEP] Pushing version manifest...
[STEP] Pushing latest manifest...
[SUCCESS] All manifests pushed

═══════════════════════════════════════════════════════════════
  Build Summary
═══════════════════════════════════════════════════════════════

Version: 4.0.2
Registry: quay.io/jasoande/project_ape

Tagged Images:
  - quay.io/jasoande/project_ape/project-ape:4.0.2
  - quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
  - quay.io/jasoande/project_ape/project-ape:4.0.2-arm64
  - quay.io/jasoande/project_ape/project-ape:latest

Pull Commands:
  podman pull quay.io/jasoande/project_ape/project-ape:4.0.2
  podman pull quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
  podman pull quay.io/jasoande/project_ape/project-ape:4.0.2-arm64
  podman pull quay.io/jasoande/project_ape/project-ape:latest

Security Reports:
  - build-logs/scan-amd64-4.0.2.txt
  - build-logs/scan-arm64-4.0.2.txt

SBOM Files:
  - build-logs/sbom-amd64-4.0.2.json
  - build-logs/sbom-arm64-4.0.2.json

Build Log:
  - build-logs/build-20260630-143022.log

[SUCCESS] Container build and push complete!
```

---

## Example 2: Quick Development Build

Fast build for testing without security scans.

```bash
# Build but don't push
./build-and-push-containers.sh \
  --build-only \
  --skip-scan \
  --skip-sbom \
  --version 4.0.2-dev

# Test locally
podman run --rm \
  -v $(pwd)/vars.py:/app/vars.py:ro \
  quay.io/jasoande/project_ape/project-ape:4.0.2-dev \
  --help

# If tests pass, push
./build-and-push-containers.sh \
  --push-only \
  --version 4.0.2-dev
```

**Use case:** Rapid iteration during development

**Time saved:** ~5-10 minutes (skips security scans)

---

## Example 3: Production Release with Signing

Full security workflow with image signing.

```bash
# Generate signing keys (first time only)
cosign generate-key-pair
mkdir -p ~/.cosign
mv cosign.key ~/.cosign/
mv cosign.pub ~/.cosign/
chmod 600 ~/.cosign/cosign.key

# Build, scan, and sign
./build-and-push-containers.sh \
  --sign \
  --version 4.0.2

# Verify signature
cosign verify \
  --key ~/.cosign/cosign.pub \
  quay.io/jasoande/project_ape/project-ape:4.0.2

# Expected output:
Verification for quay.io/jasoande/project_ape/project-ape:4.0.2 --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
```

**Use case:** Production releases requiring provenance verification

---

## Example 4: Security-First Build

Maximum security scanning with strict thresholds.

```bash
# Set strict severity threshold (fail on MEDIUM or higher)
SCAN_SEVERITY=MEDIUM ./build-and-push-containers.sh --version 4.0.2

# Review scan results
cat build-logs/scan-amd64-4.0.2.txt | grep -E "CRITICAL|HIGH|MEDIUM"

# If vulnerabilities found, fix and rebuild
# 1. Update base image in Containerfile
# 2. Update Python dependencies in requirements.txt
# 3. Rebuild

# Rescan manually
trivy image quay.io/jasoande/project_ape/project-ape:4.0.2-amd64 \
  --severity MEDIUM,HIGH,CRITICAL \
  --exit-code 1  # Fail if vulnerabilities found
```

**Use case:** Security compliance for enterprise deployments

---

## Example 5: Multi-Version Build

Build multiple versions for A/B testing.

```bash
# Build stable version
./build-and-push-containers.sh --version 4.0.2

# Build experimental version with new features
./build-and-push-containers.sh --version 4.1.0-beta

# Build LTS version
./build-and-push-containers.sh --version 4.0.2-lts

# List all versions
podman images | grep project-ape

# Output:
quay.io/jasoande/project_ape/project-ape   4.0.2         abc123...
quay.io/jasoande/project_ape/project-ape   4.0.2-amd64   def456...
quay.io/jasoande/project_ape/project-ape   4.0.2-arm64   ghi789...
quay.io/jasoande/project_ape/project-ape   4.1.0-beta    jkl012...
quay.io/jasoande/project_ape/project-ape   4.0.2-lts     mno345...
quay.io/jasoande/project_ape/project-ape   latest        abc123...
```

**Use case:** Parallel development and testing

---

## Example 6: CI/CD Pipeline Integration

GitHub Actions workflow for automated builds on tag push.

### .github/workflows/build-containers.yml

```yaml
name: Build and Push Containers

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman

      - name: Install security tools
        run: |
          # Trivy
          wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
          echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
          sudo apt-get update
          sudo apt-get install -y trivy
          
          # Syft
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

      - name: Login to Quay.io
        run: |
          echo "${{ secrets.QUAY_PASSWORD }}" | podman login quay.io -u "${{ secrets.QUAY_USERNAME }}" --password-stdin

      - name: Extract version from tag
        id: get_version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "VERSION=$VERSION" >> $GITHUB_OUTPUT
          echo "Building version: $VERSION"

      - name: Build and push containers
        run: |
          chmod +x build-and-push-containers.sh
          ./build-and-push-containers.sh --version ${{ steps.get_version.outputs.VERSION }}
        env:
          SCAN_SEVERITY: HIGH

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-logs-${{ steps.get_version.outputs.VERSION }}
          path: build-logs/
          retention-days: 30

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ steps.get_version.outputs.VERSION }}
          body: |
            ## Container Images
            
            - `quay.io/jasoande/project_ape/project-ape:${{ steps.get_version.outputs.VERSION }}`
            - `quay.io/jasoande/project_ape/project-ape:latest`
            
            Pull with:
            ```bash
            podman pull quay.io/jasoande/project_ape/project-ape:${{ steps.get_version.outputs.VERSION }}
            ```
            
            See [CHANGELOG.md](CHANGELOG.md) for details.
          draft: false
          prerelease: false

      - name: Notify on failure
        if: failure()
        run: |
          echo "Build failed! Check logs in artifacts."
          exit 1
```

### Trigger the workflow

```bash
# Update version in README.md
sed -i 's/version-[0-9.]*/version-4.0.2/' README.md

# Commit changes
git add README.md
git commit -m "Release version 4.0.2"

# Tag and push
git tag v4.0.2
git push origin production --tags

# GitHub Actions will automatically:
# 1. Detect the tag
# 2. Run build script
# 3. Push to Quay.io
# 4. Create GitHub release
# 5. Upload build logs as artifacts
```

**Use case:** Automated releases on version tags

---

## Example 7: Debugging Build Failures

What to do when builds fail.

### Scenario: Build fails with "No space left on device"

```bash
# Check disk space
df -h

# Clean up old images
podman image prune -a

# Clean up build cache
podman system prune -a --volumes

# Retry build
./build-and-push-containers.sh --version 4.0.2
```

### Scenario: Multi-arch build fails on macOS

```bash
# macOS may struggle with arm64 builds on Intel
# Option 1: Use Docker instead of Podman
brew install docker
docker run --privileged --rm tonistiigi/binfmt --install all

# Option 2: Build single-arch for testing
# Edit script temporarily to remove one architecture
# Then restore for production builds

# Option 3: Use GitHub Actions for multi-arch builds
git tag v4.0.2
git push --tags
# Let CI handle the build
```

### Scenario: Trivy scan hangs

```bash
# Trivy may timeout on large images
# Increase timeout
export TRIVY_TIMEOUT=30m

# Or skip problematic databases
trivy image \
  --skip-db-update \
  --skip-java-db-update \
  quay.io/jasoande/project_ape/project-ape:4.0.2-amd64

# Or skip scanning temporarily
./build-and-push-containers.sh --skip-scan --version 4.0.2
```

### Scenario: Registry push fails with "unauthorized"

```bash
# Re-authenticate
podman logout quay.io
podman login quay.io

# Verify credentials
podman login quay.io --get-login

# Check repository permissions at https://quay.io
# Ensure your account has write access

# Retry push
./build-and-push-containers.sh --push-only --version 4.0.2
```

---

## Example 8: Custom Registry Configuration

Build for private registry or Docker Hub.

### Private Harbor Registry

```bash
# Login to private registry
podman login harbor.mycompany.com

# Build and push
REGISTRY=harbor.mycompany.com/project-ape \
IMAGE_NAME=ape \
./build-and-push-containers.sh --version 4.0.2

# Result:
# harbor.mycompany.com/project-ape/ape:4.0.2
# harbor.mycompany.com/project-ape/ape:4.0.2-amd64
# harbor.mycompany.com/project-ape/ape:4.0.2-arm64
# harbor.mycompany.com/project-ape/ape:latest
```

### Docker Hub

```bash
# Login to Docker Hub
docker login

# Build and push
REGISTRY=docker.io/myusername \
IMAGE_NAME=project-ape \
./build-and-push-containers.sh --version 4.0.2

# Result:
# docker.io/myusername/project-ape:4.0.2
# docker.io/myusername/project-ape:latest
```

**Use case:** Multi-registry distribution

---

## Example 9: SBOM Analysis

Extract and analyze Software Bill of Materials.

```bash
# Build with SBOM
./build-and-push-containers.sh --version 4.0.2

# View SBOM summary
cat build-logs/sbom-amd64-4.0.2.json | jq '.artifacts | length'
# Output: 247 packages

# List Python packages only
cat build-logs/sbom-amd64-4.0.2.json | \
  jq '.artifacts[] | select(.type=="python") | {name: .name, version: .version}'

# Output:
{"name": "Flask", "version": "3.0.0"}
{"name": "requests", "version": "2.31.0"}
{"name": "notebooklm", "version": "1.0.0"}
...

# Check for specific package
cat build-logs/sbom-amd64-4.0.2.json | \
  jq '.artifacts[] | select(.name=="requests")'

# Export to CSV for compliance reporting
cat build-logs/sbom-amd64-4.0.2.json | \
  jq -r '.artifacts[] | [.name, .version, .type, .licenses[0].value] | @csv' \
  > sbom-report.csv
```

**Use case:** License compliance and vulnerability tracking

---

## Example 10: Rollback Failed Release

Rollback to previous version after failed deployment.

```bash
# Scenario: v4.0.2 has critical bug, rollback to v4.0.1

# 1. Stop using broken version
podman stop $(podman ps -q --filter ancestor=quay.io/jasoande/project_ape/project-ape:4.0.2)

# 2. Re-tag latest to point to previous stable version
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1
podman tag quay.io/jasoande/project_ape/project-ape:4.0.1 \
           quay.io/jasoande/project_ape/project-ape:latest
podman push quay.io/jasoande/project_ape/project-ape:latest

# 3. Update launch scripts to use 4.0.1
sed -i 's/4\.0\.2/4.0.1/g' launch_ape.sh

# 4. Verify rollback
./launch_ape.sh fast --clients test_client

# 5. Fix bugs and re-release 4.0.3
# ... fix code ...
./build-and-push-containers.sh --version 4.0.3
```

**Use case:** Emergency production rollback

---

## Performance Benchmarks

Typical build times on different hardware:

| Hardware | Build Time | Push Time | Scan Time | Total |
|----------|------------|-----------|-----------|-------|
| MacBook Pro M2 (arm64) | 8 min | 3 min | 2 min | ~13 min |
| MacBook Pro Intel (amd64) | 12 min | 3 min | 2 min | ~17 min |
| AWS EC2 t3.xlarge | 10 min | 2 min | 3 min | ~15 min |
| GitHub Actions (free tier) | 15 min | 4 min | 3 min | ~22 min |

Add `--skip-scan --skip-sbom` to save ~5 minutes during development.

---

## Common Pitfalls

### ❌ Forgetting to update README version

```bash
# Bad: Build without updating README
./build-and-push-containers.sh
# Uses old version from README.md

# Good: Update README first
sed -i 's/version-3.0.4/version-4.0.2/' README.md
./build-and-push-containers.sh
```

### ❌ Not testing before push

```bash
# Bad: Build and push immediately
./build-and-push-containers.sh --version 4.0.2

# Good: Build, test, then push
./build-and-push-containers.sh --build-only --version 4.0.2
./launch_ape.sh fast --clients test_client
./build-and-push-containers.sh --push-only --version 4.0.2
```

### ❌ Ignoring security scan warnings

```bash
# Bad: Pushing with known CRITICAL vulnerabilities
./build-and-push-containers.sh
# [WARN] CRITICAL vulnerabilities found
# Continue anyway? y  ← DON'T DO THIS

# Good: Fix vulnerabilities first
cat build-logs/scan-amd64-4.0.2.txt
# Update base image or dependencies
vim requirements.txt
./build-and-push-containers.sh --version 4.0.2
```

### ❌ Building without git tag

```bash
# Bad: Orphan versions
./build-and-push-containers.sh --version 4.0.2
# No git tag to track what code this version contains

# Good: Always tag commits
git tag v4.0.2
git push --tags
./build-and-push-containers.sh --version 4.0.2
```

---

## Next Steps

- Review [CONTAINER-BUILD-GUIDE.md](CONTAINER-BUILD-GUIDE.md) for comprehensive documentation
- Check [BUILD-QUICK-REFERENCE.md](BUILD-QUICK-REFERENCE.md) for quick command lookup
- Set up CI/CD automation for releases
- Configure Quay.io repository security scanning
- Create robot account for CI/CD access
