# ==============================================================================
# Account Intelligence (Project APE) - Production Container Image
# ==============================================================================
# Version: 4.1.0
# Base: Debian 12 (Bookworm) with Python 3.14
# Architectures: linux/amd64, linux/arm64
# Registry: quay.io/jasoande/project_ape/project-ape
#
# Security Features:
#   - Multi-stage build (minimized attack surface)
#   - Non-root user (UID 1000)
#   - Read-only filesystem where possible
#   - No unnecessary packages or build tools in final image
#   - Explicit file permissions
#   - Health check included
#   - Minimal layer count for reduced vulnerabilities
#
# Build:
#   podman build --platform linux/amd64,linux/arm64 -t project-ape:4.1.0 -f Containerfile .
#
# Run:
#   podman run -p 8765:8765 \
#     -v ./vars.py:/app/vars.py:ro,z \
#     -v ./logs:/app/logs:rw,z \
#     -v ./docs_generated:/app/docs_generated:rw,z \
#     quay.io/jasoande/project_ape/project-ape:4.1.0
# ==============================================================================

# ==============================================================================
# Stage 1: Builder - Compile dependencies
# ==============================================================================
FROM python:3.14-slim-bookworm AS builder

# Install build dependencies (minimal set)
# Combined in single RUN to minimize layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
# Using --no-cache-dir to reduce image size
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip check && \
    rm /tmp/requirements.txt

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.14-slim-bookworm

# Metadata labels (OCI standard + legacy)
LABEL org.opencontainers.image.title="Account Intelligence"
LABEL org.opencontainers.image.description="AI-powered enterprise account planning automation using NotebookLM"
LABEL org.opencontainers.image.version="4.1.0"
LABEL org.opencontainers.image.authors="Jason Anderson"
LABEL org.opencontainers.image.source="https://github.com/jasoande/Project-APE-dev"
LABEL org.opencontainers.image.licenses="Proprietary"
LABEL org.opencontainers.image.vendor="Account Intelligence Project"
LABEL maintainer="Jason Anderson"
LABEL version="4.1.0"
LABEL description="Account Intelligence - Account Planning Engine"
LABEL registry-ready="true"
LABEL base-image="Debian"

# Install ONLY runtime dependencies (no build tools)
# Combined in single RUN layer to minimize image size and attack surface
RUN apt-get update && apt-get install -y --no-install-recommends \
    # LibreOffice for document conversion (headless only - no GUI)
    libreoffice-core-nogui \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libreoffice-impress-nogui \
    # Runtime libraries for compiled dependencies
    libjpeg62-turbo \
    zlib1g \
    libffi8 \
    # Essential utilities
    ca-certificates \
    curl \
    # Cleanup in same layer to reduce image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && find /var/log -type f -delete

# Copy Python virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user (UID 1000 for compatibility with most systems)
RUN groupadd -g 1000 apeuser && \
    useradd -m -u 1000 -g apeuser -s /bin/bash apeuser

# Create application directory structure with proper ownership
RUN mkdir -p \
    /app \
    /app/logs \
    /app/.multi_process_status \
    /app/client_data \
    /app/docs_generated \
    /app/core \
    /app/dashboard \
    && chown -R apeuser:apeuser /app

# Set working directory
WORKDIR /app

# Copy application code with explicit ownership
# NOTE: We do NOT copy client data or vars.py - these are runtime mounts
COPY --chown=apeuser:apeuser core/ /app/core/
COPY --chown=apeuser:apeuser dashboard/ /app/dashboard/
COPY --chown=apeuser:apeuser *.txt /app/
COPY --chown=apeuser:apeuser main.py /app/
COPY --chown=apeuser:apeuser launch-project-ape.py /app/
COPY --chown=apeuser:apeuser setup-oauth-drive.py /app/

# Copy example configuration for reference
COPY --chown=apeuser:apeuser vars.py.example /app/

# Create container entrypoint script
# This validates required mounts and sets up the environment
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
# Verify required mounts\n\
if [ ! -f "/app/vars.py" ]; then\n\
    echo "ERROR: vars.py not found."\n\
    echo "Mount with: -v ./vars.py:/app/vars.py:ro,z"\n\
    exit 1\n\
fi\n\
\n\
# Ensure writable directories exist\n\
mkdir -p /app/logs /app/.multi_process_status /app/docs_generated 2>/dev/null || true\n\
\n\
# Execute command\n\
exec "$@"\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    chown apeuser:apeuser /app/entrypoint.sh

# Create placeholder for runtime-mounted vars.py
RUN echo "# vars.py will be mounted at runtime from host" > /app/vars.py && \
    echo "# Mount with: -v ./vars.py:/app/vars.py:ro,z" >> /app/vars.py && \
    chown apeuser:apeuser /app/vars.py

# Security: Drop privileges to non-root user
USER apeuser

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=dashboard/server.py \
    DASHBOARD_PORT=8765 \
    CLIENT_DATA_PATH=/app/client_data \
    PYTHONPATH=/app

# Expose dashboard port
EXPOSE 8765

# Health check (using urllib from stdlib - no external dependencies)
# Increased start-period to 15s to account for dashboard startup time
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "from urllib.request import urlopen; urlopen('http://localhost:8765/health', timeout=5)" || exit 1

# Default command - can be overridden at runtime
CMD ["python3", "main.py", "--mode", "fast"]
