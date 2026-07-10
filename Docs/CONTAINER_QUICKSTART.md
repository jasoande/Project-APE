# Container Quickstart Guide
**Account Intelligence - Project APE**

## Quick Commands

### Build Containers

```bash
# Build both architectures (amd64 + arm64)
./build-and-push-containers.sh --build-only

# Build and push to Quay.io
./build-and-push-containers.sh

# Build specific version
./build-and-push-containers.sh --version 4.1.0

# Build with security scanning
./build-and-push-containers.sh --build-only
# (Trivy and Syft must be installed)
```

### Run Container Locally

```bash
# Basic run
podman run -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  quay.io/jasoande/project_ape/project-ape:latest

# With NotebookLM credentials
podman run -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  -v ~/.notebooklm:/home/apeuser/.notebooklm:ro,z \
  quay.io/jasoande/project_ape/project-ape:latest

# With Gemini API key
podman run -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  -e GEMINI_API_KEY="your-api-key" \
  quay.io/jasoande/project_ape/project-ape:latest

# Deep mode
podman run -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  quay.io/jasoande/project_ape/project-ape:latest \
  python3 main.py --mode deep
```

### Pull from Registry

```bash
# Latest version
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Specific version
podman pull quay.io/jasoande/project_ape/project-ape:4.1.0

# Specific architecture
podman pull quay.io/jasoande/project_ape/project-ape:4.1.0-amd64
podman pull quay.io/jasoande/project_ape/project-ape:4.1.0-arm64
```

### Push to Registry

```bash
# Login first
podman login quay.io
# Username: jasoande
# Password: <robot account token>

# Build and push
./build-and-push-containers.sh

# Push only (if already built)
./build-and-push-containers.sh --push-only --version 4.1.0
```

## File Structure

Required files for container build:

```
project-ape/
├── Containerfile               # Multi-stage production container
├── container-entrypoint.sh     # Startup validation script
├── build-and-push-containers.sh # Build automation
├── requirements.txt            # Python dependencies
├── main.py                     # Main application
├── launch-project-ape.py       # GUI launcher
├── setup-oauth-drive.py        # Drive OAuth setup
├── vars.py.example             # Example configuration
├── core/                       # Core modules
│   ├── auth_manager.py
│   ├── drive_manager.py
│   ├── client_pipeline.py
│   └── ...
└── dashboard/                  # Web dashboard
    ├── server.py
    ├── server_gevent.py
    └── ...
```

Runtime mounts:

```
Host                    Container                   Mode
./vars.py           →   /app/vars.py                ro (read-only)
./logs/             →   /app/logs/                  rw (read-write)
./docs_generated/   →   /app/docs_generated/        rw (read-write)
~/.notebooklm/      →   /home/apeuser/.notebooklm/  ro (optional)
./credentials/      →   /app/credentials/           ro (optional)
```

## Version Tags

Available tags on Quay.io:

- `latest` - Latest stable release (auto-updated)
- `4.1.0` - Specific version (immutable)
- `4.1.0-amd64` - x86_64 specific
- `4.1.0-arm64` - ARM 64-bit specific

## Common Issues

### 1. Permission Denied on Logs

**Problem:** Container can't write to /app/logs

**Solution:**
```bash
# Fix ownership (UID 1000 is apeuser)
sudo chown -R 1000:1000 logs docs_generated

# Or use Podman's user namespace
podman unshare chown -R 1000:1000 logs docs_generated
```

### 2. vars.py Not Found

**Problem:** ERROR: vars.py file not found

**Solution:**
```bash
# Create from example
cp vars.py.example vars.py
nano vars.py  # Edit configuration

# Then mount correctly
podman run -v $(pwd)/vars.py:/app/vars.py:ro,z ...
```

### 3. SELinux Denials

**Problem:** Permission denied even with correct ownership (RHEL/Fedora)

**Solution:**
```bash
# Use :z flag for automatic SELinux labeling
podman run -v ./logs:/app/logs:rw,z ...

# Verify labels
ls -Z logs/
# Should show: system_u:object_r:container_file_t:s0
```

### 4. Port Already in Use

**Problem:** Error: bind: address already in use

**Solution:**
```bash
# Check what's using port 8765
sudo lsof -i:8765

# Kill existing container
podman ps | grep project-ape
podman stop <container-id>

# Or use different port
podman run -p 8766:8765 ...
```

### 5. Health Check Failing

**Problem:** Container marked as unhealthy

**Solution:**
```bash
# Check dashboard logs
podman logs <container-id> | grep -i error

# Manually test health endpoint
podman exec <container-id> curl http://localhost:8765/health

# Check if dashboard started
podman exec <container-id> ps aux | grep python
```

## Development Workflow

### 1. Make Code Changes

Edit Python files in core/ or dashboard/

### 2. Test Locally (No Container)

```bash
python3 launch-project-ape.py
```

### 3. Build Container

```bash
./build-and-push-containers.sh --build-only --skip-scan
```

### 4. Test Container Locally

```bash
podman run --rm -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  localhost/project-ape:latest
```

### 5. Push to Registry

```bash
# Tag for registry
podman tag localhost/project-ape:latest \
  quay.io/jasoande/project_ape/project-ape:4.1.0

# Push
podman push quay.io/jasoande/project_ape/project-ape:4.1.0
```

Or use the automated script:

```bash
./build-and-push-containers.sh --version 4.1.0
```

## Multi-Architecture Notes

### Building on Mac (ARM)

Mac M1/M2/M3 builds arm64 natively and emulates amd64:

```bash
# Native arm64 build (fast)
podman build --platform linux/arm64 -t project-ape:latest .

# Emulated amd64 build (slow, uses QEMU)
podman build --platform linux/amd64 -t project-ape:latest .

# Both architectures (automated)
./build-and-push-containers.sh --build-only
```

### Building on Linux (x86_64)

Linux x86_64 builds amd64 natively and emulates arm64:

```bash
# Native amd64 build (fast)
podman build --platform linux/amd64 -t project-ape:latest .

# Emulated arm64 build (slow, uses QEMU)
podman build --platform linux/arm64 -t project-ape:latest .

# Both architectures (automated)
./build-and-push-containers.sh --build-only
```

### Using Manifest Lists

The build script creates a manifest list that includes both architectures:

```bash
# Pull works on any platform
podman pull quay.io/jasoande/project_ape/project-ape:4.1.0

# Podman automatically selects the right architecture:
# - x86_64 host → pulls amd64 image
# - ARM64 host → pulls arm64 image
```

## Resource Requirements

### Minimum (Fast Mode, 1 Client)

- CPU: 1 core
- RAM: 1 GB
- Disk: 5 GB

### Recommended (Deep Mode, 5 Clients)

- CPU: 4 cores
- RAM: 4 GB
- Disk: 20 GB

### Setting Limits

```bash
podman run \
  --memory="4g" \
  --cpus="2" \
  --pids-limit=100 \
  -p 8765:8765 \
  project-ape:latest
```

## Next Steps

- [CONTAINER_SECURITY_GUIDE.md](./CONTAINER_SECURITY_GUIDE.md) - Security hardening details
- [CLAUDE.md](./CLAUDE.md) - Complete developer documentation
- [README.md](./README.md) - Project overview
- [Docs/DEPLOYMENT_GUIDE.md](./Docs/DEPLOYMENT_GUIDE.md) - Production deployment

## Support

- GitHub Issues: https://github.com/jasoande/Project-APE-dev/issues
- Container Registry: https://quay.io/repository/jasoande/project_ape/project-ape
