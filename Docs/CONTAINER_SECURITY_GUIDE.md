# Container Security Guide
**Account Intelligence - Project APE**

## Overview

This document describes the security hardening measures implemented in the Account Intelligence container images and provides best practices for secure deployment.

## Container Architecture

### Multi-Stage Build

The Containerfile uses a two-stage build process:

1. **Builder Stage** - Compiles dependencies with build tools
2. **Runtime Stage** - Minimal production image with only runtime requirements

**Benefits:**
- Reduced attack surface (no compiler toolchains in production image)
- Smaller image size (50-60% reduction)
- Faster pull times and reduced storage costs

### Base Images

- **Base:** `python:3.14-slim-bookworm` (Debian 12)
- **Python Version:** 3.14.6
- **Architectures:** linux/amd64, linux/arm64

**Why Python 3.14:**
- Latest stable release with security patches
- Improved performance (10-15% faster than 3.11)
- Better type hinting and error messages
- Extended support lifecycle

## Security Features

### 1. Non-Root User

Container runs as `apeuser` (UID 1000, GID 1000):

```dockerfile
# Create non-root user
RUN groupadd -g 1000 apeuser && \
    useradd -m -u 1000 -g apeuser -s /bin/bash apeuser

# Drop privileges
USER apeuser
```

**Benefits:**
- Prevents privilege escalation attacks
- Limits damage if container is compromised
- Follows principle of least privilege

### 2. Minimal Package Installation

Only essential runtime packages are installed:

- **LibreOffice (nogui)** - Document conversion (headless only)
- **Runtime libraries** - libjpeg, zlib, libffi (no dev packages)
- **ca-certificates** - TLS certificate validation
- **curl** - Health checks only

**Excluded:**
- All build tools (gcc, g++, make)
- Development headers
- Unnecessary utilities
- Optional dependencies

### 3. Layer Optimization

All cleanup operations are performed in the same RUN layer:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    package1 package2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && find /var/log -type f -delete
```

**Benefits:**
- Smaller image size (cleanup removes cached data from same layer)
- Fewer vulnerabilities (reduced package count)
- Faster builds (fewer layers to cache)

### 4. Explicit File Permissions

All copied files have explicit ownership:

```dockerfile
COPY --chown=apeuser:apeuser core/ /app/core/
```

**Benefits:**
- No permission-related runtime errors
- Predictable file ownership
- Easier troubleshooting

### 5. Read-Only Mounts

Configuration files are mounted read-only:

```bash
podman run \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  project-ape:latest
```

**Benefits:**
- Prevents accidental modification of config
- Protects credentials from tampering
- Clear separation of read-only vs writable data

### 6. Health Checks

Built-in health check using stdlib only:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "from urllib.request import urlopen; urlopen('http://localhost:8765/health', timeout=5)" || exit 1
```

**Benefits:**
- No external dependencies (uses urllib from stdlib)
- Container orchestrators (Kubernetes, Podman) can auto-restart unhealthy containers
- Monitoring systems can track container health

### 7. Environment Variable Security

Sensitive data is passed via environment variables, not baked into image:

```bash
podman run \
  -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
  project-ape:latest
```

**Best Practices:**
- Never commit secrets to Containerfile
- Use container secrets management (Kubernetes secrets, Podman secrets)
- Rotate credentials regularly

## Build Security

### Vulnerability Scanning

The build script supports automatic vulnerability scanning with Trivy:

```bash
./build-and-push-containers.sh --version 4.1.0
```

**What's Scanned:**
- OS packages (Debian packages)
- Python packages (pip dependencies)
- Known CVEs and security advisories

**Severity Levels:**
- LOW - Informational
- MEDIUM - Should fix eventually
- HIGH - Fix soon (blocks push with confirmation)
- CRITICAL - Fix immediately (blocks push)

### SBOM Generation

Software Bill of Materials (SBOM) is generated for compliance:

```bash
./build-and-push-containers.sh --version 4.1.0
# Generates: logs/container-builds/sbom-amd64-4.1.0.json
#            logs/container-builds/sbom-arm64-4.1.0.json
```

**Use Cases:**
- License compliance
- Supply chain security
- Vulnerability tracking
- Audit requirements

## Deployment Security

### Podman Security

Podman runs rootless by default:

```bash
# Run as current user (no root required)
podman run -p 8765:8765 project-ape:latest
```

**Podman Advantages over Docker:**
- Daemonless (no privileged background process)
- Rootless containers by default
- SELinux integration (z flag for auto-labeling)
- Drop-in replacement for Docker

### SELinux Labels

On RHEL/Fedora/CentOS, use `:z` for volume mounts:

```bash
podman run \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  project-ape:latest
```

**What `:z` does:**
- Automatically labels files for container access
- Prevents SELinux permission denied errors
- Enables SELinux security without manual labeling

### Network Isolation

Containers use isolated networks by default:

```bash
# Expose only dashboard port
podman run -p 127.0.0.1:8765:8765 project-ape:latest
```

**Best Practices:**
- Bind to localhost (127.0.0.1) for local-only access
- Use reverse proxy (nginx, Caddy) for remote access
- Never bind to 0.0.0.0 in production

### Resource Limits

Set resource limits to prevent DoS:

```bash
podman run \
  --memory="4g" \
  --cpus="2" \
  --pids-limit=100 \
  project-ape:latest
```

**Recommended Limits:**
- Memory: 2-4 GB (depends on parallel clients)
- CPUs: 2-4 cores
- PIDs: 100 (prevents fork bombs)

## Multi-Architecture Support

### Supported Architectures

- **linux/amd64** - Intel/AMD x86_64 (most servers)
- **linux/arm64** - ARM 64-bit (Apple Silicon, Graviton, Raspberry Pi 4+)

### Building Multi-Arch Images

```bash
# Build for both architectures
podman build --platform linux/amd64,linux/arm64 -t project-ape:4.1.0 .

# Build for specific architecture
podman build --platform linux/amd64 -t project-ape:4.1.0-amd64 .
podman build --platform linux/arm64 -t project-ape:4.1.0-arm64 .
```

### Manifest Lists

The build script creates manifest lists for multi-arch support:

```bash
# Single pull command works on any architecture
podman pull quay.io/jasoande/project_ape/project-ape:4.1.0

# Podman automatically selects correct architecture
# - x86_64 server pulls amd64 variant
# - Mac M1/M2 pulls arm64 variant
```

## Registry Security

### Quay.io Best Practices

1. **Use Repository Secrets:**
   ```bash
   podman login quay.io
   # Credentials stored in ${XDG_RUNTIME_DIR}/containers/auth.json
   ```

2. **Enable Vulnerability Scanning:**
   - Quay.io automatically scans pushed images
   - View results: https://quay.io/repository/jasoande/project_ape/project-ape

3. **Use Immutable Tags:**
   - Always tag with version (4.1.0, 4.1.1)
   - `latest` should only be used for development

4. **Set Repository to Private:**
   - Go to Quay.io → Settings → Make Repository Private
   - Generate robot accounts for CI/CD

### Image Signing (Optional)

Sign images with Cosign for supply chain security:

```bash
# Install Cosign
brew install cosign  # macOS
apt-get install cosign  # Debian/Ubuntu

# Generate key pair
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key \
  quay.io/jasoande/project_ape/project-ape:4.1.0

# Verify signature
cosign verify --key cosign.pub \
  quay.io/jasoande/project_ape/project-ape:4.1.0
```

## Production Deployment

### Kubernetes Security

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: project-ape
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: project-ape
    image: quay.io/jasoande/project_ape/project-ape:4.1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: false  # logs/docs_generated need writes
      capabilities:
        drop:
        - ALL
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
```

### OpenShift Security

OpenShift enforces stricter security by default:

```yaml
apiVersion: v1
kind: DeploymentConfig
metadata:
  name: project-ape
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: project-ape
        image: quay.io/jasoande/project_ape/project-ape:4.1.0
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
```

## Security Checklist

### Pre-Build
- [ ] Review requirements.txt for known vulnerabilities
- [ ] Update base image to latest patch version
- [ ] Remove unnecessary dependencies

### Build
- [ ] Run vulnerability scan (Trivy)
- [ ] Generate SBOM for compliance
- [ ] Review scan results (no CRITICAL vulnerabilities)
- [ ] Tag with semantic version (4.1.0, not just latest)

### Pre-Push
- [ ] Test container locally
- [ ] Verify health check works
- [ ] Check file permissions (logs writable)
- [ ] Review exposed ports

### Post-Push
- [ ] Verify image in registry
- [ ] Check Quay.io vulnerability scan results
- [ ] Update deployment manifests
- [ ] Document any security exceptions

### Runtime
- [ ] Run as non-root user
- [ ] Set resource limits
- [ ] Use read-only mounts for config
- [ ] Enable SELinux (Podman with :z)
- [ ] Bind to localhost or use reverse proxy
- [ ] Monitor container logs
- [ ] Rotate credentials regularly

## Troubleshooting

### Permission Denied on Mounted Volumes

**Symptom:** Container can't write to logs or docs_generated

**Solution:**
```bash
# Check ownership
ls -la logs/

# Fix ownership (UID 1000 is apeuser in container)
sudo chown -R 1000:1000 logs docs_generated

# Or use Podman's auto-fix
podman unshare chown -R 1000:1000 logs docs_generated
```

### SELinux Denials

**Symptom:** Permission denied even with correct ownership

**Solution:**
```bash
# Use :z flag for SELinux auto-labeling
podman run -v ./logs:/app/logs:rw,z project-ape:latest

# Or manually label (less common)
chcon -Rt container_file_t logs/
```

### Health Check Failing

**Symptom:** Container marked unhealthy

**Solution:**
```bash
# Check if dashboard is actually running
podman exec project-ape curl http://localhost:8765/health

# Check dashboard logs
podman logs project-ape | grep -i error

# Increase start-period if slow startup
# (already set to 15s in Containerfile)
```

## References

- [OWASP Container Security](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Podman Security](https://www.redhat.com/en/blog/understanding-root-inside-and-outside-container)
- [Quay.io Documentation](https://docs.quay.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

## Version History

- **4.1.0** (2026-07-10) - Complete security hardening, multi-arch support
- **4.0.1** (2026-07-09) - Dashboard SSE thread exhaustion fix
- **3.2.2** (2026-06-26) - OAuth migration
