# Container Build Quick Reference

One-page reference for common container build operations.

## Quick Commands

```bash
# Standard build and push
./build-and-push-containers.sh

# Build specific version
./build-and-push-containers.sh --version 4.0.2

# Test build (no push)
./build-and-push-containers.sh --build-only

# Fast build (skip security)
./build-and-push-containers.sh --skip-scan --skip-sbom

# Production build (with signing)
./build-and-push-containers.sh --sign
```

## Pre-Build Checklist

- [ ] Updated version in README.md
- [ ] Logged into registry: `podman login quay.io`
- [ ] Trivy installed (or use `--skip-scan`)
- [ ] Syft installed (or use `--skip-sbom`)
- [ ] Git committed and tagged
- [ ] Tested locally with current code

## Post-Build Verification

```bash
# Check images were created
podman images | grep project-ape

# Check registry tags
podman search quay.io/jasoande/project_ape --limit 10

# Pull and test
podman pull quay.io/jasoande/project_ape/project-ape:4.0.2
podman run --rm quay.io/jasoande/project_ape/project-ape:4.0.2 --help

# Check multi-arch manifest
podman manifest inspect quay.io/jasoande/project_ape/project-ape:4.0.2
```

## Common Flags

| Flag | Description |
|------|-------------|
| `--version X.Y.Z` | Override version (default: auto-detect) |
| `--build-only` | Build but don't push |
| `--push-only` | Push existing images |
| `--skip-scan` | Skip vulnerability scanning |
| `--skip-sbom` | Skip SBOM generation |
| `--sign` | Sign images with Cosign |
| `--help` | Show full help |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REGISTRY` | `quay.io/jasoande/project_ape` | Container registry |
| `IMAGE_NAME` | `project-ape` | Image name |
| `SCAN_SEVERITY` | `HIGH` | Min scan severity |
| `SKIP_SCAN` | `false` | Skip vulnerability scan |
| `SKIP_SBOM` | `false` | Skip SBOM generation |
| `SIGN_IMAGES` | `false` | Sign with Cosign |

## Output Files

| File | Description |
|------|-------------|
| `build-logs/build-YYYYMMDD-HHMMSS.log` | Full build log |
| `build-logs/scan-{arch}-{version}.txt` | Vulnerability reports |
| `build-logs/sbom-{arch}-{version}.json` | Software Bill of Materials |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not logged in" | `podman login quay.io` |
| "Trivy not found" | `brew install trivy` or `--skip-scan` |
| "Version not detected" | Add `--version 4.0.2` |
| "Manifest push failed" | `podman manifest rm ...` and retry |
| "Out of disk space" | `podman image prune -a` |

## Tags Created

Each build creates 4 tags:

1. `4.0.2` - Version (multi-arch manifest)
2. `4.0.2-amd64` - Version amd64-specific
3. `4.0.2-arm64` - Version arm64-specific
4. `latest` - Latest (multi-arch manifest)

## Full Image Names

```
quay.io/jasoande/project_ape/project-ape:4.0.2
quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
quay.io/jasoande/project_ape/project-ape:4.0.2-arm64
quay.io/jasoande/project_ape/project-ape:latest
```

## Release Workflow

1. **Update Version**
   ```bash
   # Update README.md badge
   sed -i 's/version-[0-9.]*/version-4.0.2/' README.md
   ```

2. **Commit and Tag**
   ```bash
   git add README.md
   git commit -m "Bump version to 4.0.2"
   git tag v4.0.2
   git push origin production --tags
   ```

3. **Build and Push**
   ```bash
   ./build-and-push-containers.sh
   ```

4. **Verify**
   ```bash
   podman pull quay.io/jasoande/project_ape/project-ape:4.0.2
   ./launch_ape.sh fast --clients test_client
   ```

5. **Update Changelog**
   ```bash
   echo "## v4.0.2 - $(date +%Y-%m-%d)" >> CHANGELOG.md
   echo "- Feature: XYZ" >> CHANGELOG.md
   git add CHANGELOG.md
   git commit -m "Update changelog for v4.0.2"
   git push
   ```

## Security Scan Workflow

1. **Build with scan**
   ```bash
   ./build-and-push-containers.sh --build-only
   ```

2. **Review reports**
   ```bash
   cat build-logs/scan-amd64-*.txt
   cat build-logs/scan-arm64-*.txt
   ```

3. **Fix issues** (update base image, dependencies, etc.)

4. **Rescan**
   ```bash
   trivy image quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
   ```

5. **Push if clean**
   ```bash
   ./build-and-push-containers.sh --push-only --version 4.0.2
   ```

## Manual Build (Alternative)

If the script fails, manual build process:

```bash
# Build each arch
podman build --platform linux/amd64 \
  -t quay.io/jasoande/project_ape/project-ape:4.0.2-amd64 \
  -f developer-docs/Containerfile.debian .

podman build --platform linux/arm64 \
  -t quay.io/jasoande/project_ape/project-ape:4.0.2-arm64 \
  -f developer-docs/Containerfile.debian .

# Create manifest
podman manifest create quay.io/jasoande/project_ape/project-ape:4.0.2 \
  quay.io/jasoande/project_ape/project-ape:4.0.2-amd64 \
  quay.io/jasoande/project_ape/project-ape:4.0.2-arm64

# Push
podman push quay.io/jasoande/project_ape/project-ape:4.0.2-amd64
podman push quay.io/jasoande/project_ape/project-ape:4.0.2-arm64
podman manifest push quay.io/jasoande/project_ape/project-ape:4.0.2
```

## CI/CD Integration

**GitHub Actions:**
```yaml
- name: Build and push
  run: ./build-and-push-containers.sh --version ${{ steps.version.outputs.VERSION }}
  env:
    SKIP_SCAN: false
    SKIP_SBOM: false
```

**GitLab CI:**
```yaml
script:
  - ./build-and-push-containers.sh
artifacts:
  paths:
    - build-logs/
```

## Help

```bash
./build-and-push-containers.sh --help
```

Full documentation: `developer-docs/CONTAINER-BUILD-GUIDE.md`
