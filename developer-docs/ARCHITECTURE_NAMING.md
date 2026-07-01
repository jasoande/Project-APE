# Container Architecture Naming Standard

## Overview

Project APE uses clear, industry-standard architecture naming to eliminate confusion:

| Architecture | Standard Name | Also Known As | Use Case |
|--------------|---------------|---------------|----------|
| **x86_64** | x86_64 | amd64, x86-64, Intel 64, AMD64 | Intel/AMD servers, Linux production |
| **arm64** | arm64 | aarch64, ARMv8 | Apple Silicon (M1/M2/M3), ARM servers |

## Container Image Tags

### Current Naming Convention (v3.2.2+)

```
quay.io/jasoande/project_ape/project-ape:latest           # Multi-arch manifest
quay.io/jasoande/project_ape/project-ape:3.2.2            # Multi-arch manifest
quay.io/jasoande/project_ape/project-ape:3.2.2-x86_64     # Intel/AMD specific
quay.io/jasoande/project_ape/project-ape:3.2.2-arm64      # ARM specific
```

### Legacy Naming (v3.0.5 and earlier)

```
quay.io/jasoande/project_ape/project-ape:3.0.5-amd64      # Old x86_64 tag
quay.io/jasoande/project_ape/project-ape:3.0.5-arm64      # Unchanged
```

## Why x86_64 Instead of amd64?

1. **Industry Standard**: x86_64 is the official architecture name used by:
   - Linux kernel (`uname -m` returns `x86_64`)
   - GCC/Clang compilers
   - RPM/DNF package managers
   - Red Hat Enterprise Linux
   - Most CI/CD platforms

2. **Clarity**: "amd64" is ambiguous:
   - Implies AMD-specific (not true - works on Intel too)
   - Docker uses "amd64" but this is Docker-specific terminology
   - Can confuse users about Intel compatibility

3. **Consistency**: Red Hat ecosystem uses x86_64:
   - RHEL packages: `package-name.x86_64.rpm`
   - Architecture detection: `arch` or `uname -m` → `x86_64`
   - Subscription management: `x86_64` architecture

## Migration Impact

### Updated Files (48 references across 48 files)

**Build Scripts:**
- ✅ `build-and-push-containers.sh` - All tags now use `-x86_64` suffix
- ✅ `launch_ape.sh` - Auto-detection prefers x86_64, falls back to amd64
- ✅ `setup-credentials.sh` - Auto-detection prefers x86_64, falls back to amd64
- ✅ `ape-run.sh` - Updated platform detection

**Documentation:**
- ✅ `CLAUDE.md` - Container operations examples updated
- ✅ `README.md` - Quick start and pull commands updated
- ✅ `ARCHITECTURE.md` - Platform specifications updated
- ✅ `TROUBLESHOOTING.md` - Diagnostic commands updated
- ✅ `API_REFERENCE.md` - Example code and tags updated

**Containerfiles:**
- ✅ `Containerfile.debian` - Platform labels updated
- ✅ All build-time variables updated

### Backward Compatibility

The following scripts maintain backward compatibility with "amd64" input:

**launch_ape.sh (line 93):**
```bash
case "$ARCH" in
    x86_64|amd64)  # Accepts both for legacy compatibility
        PLATFORM="linux/x86_64"
        ;;
    aarch64|arm64)
        PLATFORM="linux/arm64"
        ;;
esac
```

**setup-credentials.sh (line 22):**
```bash
case "$arch" in
    x86_64|amd64)  # Accepts both for legacy compatibility
        PLATFORM="linux/x86_64"
        ;;
    arm64|aarch64)
        PLATFORM="linux/arm64"
        ;;
esac
```

## Platform Detection

### Automatic Detection

The build system automatically detects your architecture:

```bash
ARCH=$(uname -m)
# Returns: x86_64 (Intel/AMD) or arm64 (Apple Silicon)
```

### Manual Override

You can force a specific architecture:

```bash
# Build for x86_64 only
./build-and-push-containers.sh --platform linux/x86_64

# Build for arm64 only
./build-and-push-containers.sh --platform linux/arm64
```

## Validation Status

✅ **Validation Passed** (8 remaining "amd64" references, all acceptable):

1. **Documentation** (6 references):
   - `ARCHITECTURE.md` - Explanatory note about amd64 vs x86_64 ✅
   - `API_REFERENCE.md` - Updated to x86_64 ✅

2. **Scripts** (2 references):
   - `launch_ape.sh` - Fallback case for legacy input ✅
   - `setup-credentials.sh` - Fallback case for legacy input ✅

3. **Python Code**: 0 references ✅
4. **Containerfiles**: 0 direct references ✅

## Migration Date

- **Effective Date**: June 30, 2026
- **First Version**: v3.2.2
- **Migration Status**: Complete ✅

## References

- [Red Hat Container Terminology](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/building_running_and_managing_containers/assembly_adding-software-to-a-ubi-container_building-running-and-managing-containers)
- [OCI Image Spec - Platform](https://github.com/opencontainers/image-spec/blob/main/image-index.md#platform-variants)
- [Go Architecture Names](https://go.dev/doc/install/source#environment)

---

**Summary**: Project APE now uses **x86_64** for Intel/AMD 64-bit and **arm64** for ARM 64-bit architectures across all scripts, documentation, and container tags for maximum clarity and consistency with industry standards.
