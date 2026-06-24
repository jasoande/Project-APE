# Project APE - Generic Container Image for Registry Distribution
# RHEL-based using Universal Base Image (UBI) 9 with Python 3.14
# This image contains NO client-specific data - all data is mounted at runtime

# Stage 1: Build environment
FROM registry.redhat.io/ubi9/python-314:9.8-1781023605 as builder

USER root

# Install build dependencies
RUN dnf install -y \
    gcc \
    gcc-c++ \
    libjpeg-turbo-devel \
    zlib-devel \
    python3-devel \
    && dnf clean all

# Create virtual environment
RUN python3.14 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Runtime environment
FROM registry.redhat.io/ubi9/python-314:9.8-1781023605

USER root

# Metadata
LABEL maintainer="Jason Anderson"
LABEL description="Project APE - Account Planning Engine (RHEL UBI 9 with Python 3.14)"
LABEL version="3.0.4"
LABEL registry-ready="true"
LABEL base-image="RHEL UBI 9"
LABEL python-version="3.14"

# Enable EPEL for LibreOffice
# Note: CRB (CodeReady Builder) not available in UBI Python image, using EPEL only
RUN dnf install -y \
    https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm \
    && dnf clean all

# Install runtime dependencies
# Note: curl-minimal is pre-installed and conflicts with curl package
RUN dnf install -y \
    # Image processing libraries (already installed, but ensuring present)
    libjpeg-turbo \
    zlib \
    # Utilities (ca-certificates and findutils already installed)
    ca-certificates \
    findutils \
    && dnf clean all

# Conditional LibreOffice installation (x86_64 only)
# LibreOffice is NOT available in EPEL for aarch64 (ARM64/Apple Silicon)
# Production x86_64 builds will have LibreOffice
# For ARM64 development, use Debian variant: ./build-container.sh --debian
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        dnf install -y \
            libreoffice-core \
            libreoffice-writer \
            libreoffice-calc \
            libreoffice-impress \
            libreoffice-headless \
            && dnf clean all; \
    else \
        echo "⚠️  Skipping LibreOffice on $(uname -m) - not available in EPEL for ARM64"; \
        echo "    For LibreOffice support on ARM64, use: ./build-container.sh --debian"; \
    fi

# Install Node.js 18.x from NodeSource with conflict resolution
RUN curl -fsSL https://rpm.nodesource.com/setup_18.x | bash - && \
    dnf install -y --allowerasing nodejs && \
    dnf clean all

# Install NotebookLM CLI globally
RUN npm install -g notebooklm && \
    npm cache clean --force

# Copy Python virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash apeuser && \
    mkdir -p /app /app/logs /app/.multi_process_status /app/client_data && \
    chown -R apeuser:apeuser /app

# Set working directory
WORKDIR /app

# Copy ONLY the application code (NO client data, NO vars.py)
COPY --chown=apeuser:apeuser core/ /app/core/
COPY --chown=apeuser:apeuser dashboard/ /app/dashboard/
COPY --chown=apeuser:apeuser chat_prompt_consolidated_*.txt /app/
COPY --chown=apeuser:apeuser ask_prompt_*.txt /app/
COPY --chown=apeuser:apeuser main.py /app/
COPY --chown=apeuser:apeuser example-vars.py /app/
COPY --chown=apeuser:apeuser example-container.py /app/

# Create placeholder for vars.py (will be mounted at runtime)
RUN echo "# vars.py will be mounted at runtime" > /app/vars.py && \
    chown apeuser:apeuser /app/vars.py

# Switch to non-root user
USER apeuser

# Environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=dashboard/server.py
ENV DASHBOARD_PORT=8765
ENV CLIENT_DATA_PATH=/app/client_data

# Expose dashboard port
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8765', timeout=5)" || exit 1

# Default command - will be overridden with runtime parameters
# Use explicit path to venv python to ensure dependencies are found
CMD ["/opt/venv/bin/python3", "main.py", "--mode", "fast"]
