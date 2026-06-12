#!/bin/bash
# Project APE - Simple Runner for Pre-Built Registry Image
# This is what other account teams will use - NO building required!

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default configuration - Pre-configured for Red Hat account teams
DEFAULT_REGISTRY="quay.io"
DEFAULT_NAMESPACE="jasoande/project_ape"
IMAGE_NAME="project-ape"
IMAGE_TAG="latest"

# Runtime defaults
MODE="fast"
CLIENTS=""
CLIENT_DATA_PATH="./client_data"
VARS_FILE="./vars.py"
LOGS_PATH="./logs"
CREDENTIALS_VOLUME="project-ape-credentials"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --clients)
            CLIENTS="$2"
            shift 2
            ;;
        --client-data)
            CLIENT_DATA_PATH="$2"
            shift 2
            ;;
        --vars)
            VARS_FILE="$2"
            shift 2
            ;;
        --logs)
            LOGS_PATH="$2"
            shift 2
            ;;
        --registry)
            DEFAULT_REGISTRY="$2"
            shift 2
            ;;
        --namespace)
            DEFAULT_NAMESPACE="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --help)
            echo "Project APE - Simple Runner"
            echo
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Runtime Options:"
            echo "  --mode MODE               Execution mode: fast or deep (default: fast)"
            echo "  --clients CLIENTS         Comma-separated client list (default: all from vars.py)"
            echo "  --client-data PATH        Path to client data directory (default: ./client_data)"
            echo "  --vars PATH               Path to vars.py file (default: ./vars.py)"
            echo "  --logs PATH               Path to logs directory (default: ./logs)"
            echo
            echo "Image Options:"
            echo "  --registry REGISTRY       Container registry (default: quay.io)"
            echo "  --namespace NAMESPACE     Registry namespace (default: your-org)"
            echo "  --tag TAG                 Image tag (default: latest)"
            echo
            echo "Examples:"
            echo "  $0 --mode fast"
            echo "  $0 --mode deep --clients merck_test"
            echo "  $0 --mode fast --client-data /path/to/clients"
            echo
            echo "First-time setup:"
            echo "  1. Create vars.py with your client configuration"
            echo "  2. Put client data in ./client_data/ directory"
            echo "  3. Login to NotebookLM: notebooklm login"
            echo "  4. Run: $0 --mode fast"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

FULL_IMAGE="${DEFAULT_REGISTRY}/${DEFAULT_NAMESPACE}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "========================================================================"
echo "PROJECT APE - RUNNING FROM REGISTRY IMAGE"
echo "========================================================================"
echo

# Pre-flight checks
echo "Pre-flight checks:"
echo

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}✗ Podman not installed${NC}"
    echo
    echo "Install Podman:"
    echo "  macOS: brew install podman && podman machine init && podman machine start"
    echo "  RHEL/Fedora: sudo dnf install podman"
    exit 1
fi
echo -e "${GREEN}✓${NC} Podman installed"

# Check if vars.py exists
if [ ! -f "$VARS_FILE" ]; then
    echo -e "${RED}✗ vars.py not found at: $VARS_FILE${NC}"
    echo
    echo "Create vars.py with your client configuration:"
    echo "  cp example-vars.py vars.py"
    echo "  # Edit vars.py with your clients"
    exit 1
fi
echo -e "${GREEN}✓${NC} vars.py found"

# Check if client data directory exists
if [ ! -d "$CLIENT_DATA_PATH" ]; then
    echo -e "${YELLOW}⚠${NC}  Client data directory not found: $CLIENT_DATA_PATH"
    echo "   Creating directory..."
    mkdir -p "$CLIENT_DATA_PATH"
fi
echo -e "${GREEN}✓${NC} Client data directory ready"

# Check NotebookLM credentials volume
if ! podman volume exists ${CREDENTIALS_VOLUME} 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  NotebookLM credentials volume not found"
    echo
    echo "Run the setup script first:"
    echo "  ./setup-credentials.sh"
    echo
    echo "This is a one-time setup that will authenticate with NotebookLM."
    echo
    read -p "Run setup now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./setup-credentials.sh
        if [ $? -ne 0 ]; then
            echo "Setup failed. Exiting."
            exit 1
        fi
    else
        exit 1
    fi
fi
echo -e "${GREEN}✓${NC} NotebookLM credentials ready"

# Create logs directory if needed
mkdir -p "$LOGS_PATH"

# Ensure logs directory is writable by container user (UID 1000)
# Container runs as UID 1000, host user may be different UID
# Setting 777 allows container to write regardless of host UID
chmod 777 "$LOGS_PATH" 2>/dev/null || true

echo
echo "Configuration:"
echo "  Image: ${FULL_IMAGE}"
echo "  Mode: ${MODE}"
if [ -n "$CLIENTS" ]; then
    echo "  Clients: ${CLIENTS}"
else
    echo "  Clients: all (from vars.py)"
fi
echo "  Client Data: ${CLIENT_DATA_PATH}"
echo "  Config: ${VARS_FILE}"
echo "  Logs: ${LOGS_PATH}"
echo

# Pull latest image (if needed)
echo "Pulling latest image (if needed)..."
podman pull ${FULL_IMAGE}
echo

# Build command (use explicit venv path)
CMD_ARGS="/opt/venv/bin/python3 main.py --mode ${MODE}"
if [ -n "$CLIENTS" ]; then
    CMD_ARGS="${CMD_ARGS} --clients ${CLIENTS}"
fi

# Run container
echo "Starting Project APE..."
echo "Dashboard will be available at: http://localhost:8765"
echo

CONTAINER_ID=$(podman run \
    --name project-ape-$(date +%s) \
    --rm \
    -d \
    -p 8765:8765 \
    -v "$(realpath ${CLIENT_DATA_PATH}):/app/client_data:ro,z" \
    -v "$(realpath ${VARS_FILE}):/app/vars.py:ro,z" \
    -v "$(realpath ${LOGS_PATH}):/app/logs:z" \
    -v "${CREDENTIALS_VOLUME}:/home/apeuser/.notebooklm" \
    -e PYTHONUNBUFFERED=1 \
    ${FULL_IMAGE} \
    ${CMD_ARGS})

# Follow logs
echo "Container started: $CONTAINER_ID"
echo "Following logs (Ctrl+C to detach, container keeps running)..."
echo
podman logs -f $CONTAINER_ID

echo
echo "========================================================================"
echo -e "${GREEN}✅ Execution complete${NC}"
echo "========================================================================"
echo
echo "Logs saved to: ${LOGS_PATH}"
echo
