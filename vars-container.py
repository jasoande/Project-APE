# ==============================================================================
# PROJECT APE - CONTAINER CONFIGURATION
# ==============================================================================
# Minimal configuration template for containerized deployment
#
# Quick Start:
#   1. Copy this file: cp vars-container.py vars.py
#   2. Edit the CLIENT CONFIGURATION section below
#   3. Run: ./ape-run.sh --mode fast
#
# ==============================================================================

from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATION - CUSTOMIZE THIS SECTION
# ==============================================================================

# List your clients here (use simple lowercase names with underscores)
clients = [
    "example_client",
]

# --- Example Client Configuration ---
# Copy this block for each client you add
#
# Required fields:
#   _name:     Client's full company name
#   _industry: Primary industry (e.g., "pharmaceuticals and healthcare")
#   _folder:   Path to client data in container (always /app/client_data/{ClientName})
#
# Optional fields:
#   _subsegments: Comma-separated industry subsegments for targeted analysis
#                 Examples:
#                 - Pharma: "oncology, vaccines, rare diseases"
#                 - Retail: "e-commerce, brick-and-mortar, omnichannel"
#                 - Finance: "retail banking, wealth management, payments"
#                 - Manufacturing: "discrete, process, automotive"
#                 If omitted, NotebookLM will discover subsegments during research.

example_client_name = "Example Corporation"
example_client_industry = "technology and software"
example_client_subsegments = "cloud services, enterprise software, SaaS platforms"
example_client_folder = "/app/client_data/Example"


# ==============================================================================
# ADVANCED SETTINGS - LEAVE AS-IS UNLESS YOU NEED TO TUNE
# ==============================================================================
# Note: Company branding (Red Hat, products, etc.) is hardcoded in prompt
#       template files (*.txt). To change company, edit those files directly.

# Execution mode (fast or deep)
default_mode = "fast"

# Dashboard
DASHBOARD_PORT = 8765

# Container paths (do not modify)
# Note: Directories are created by the application at runtime
PROJECT_ROOT = Path("/app")
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"


# ==============================================================================
# TIMING CONFIGURATION - ONLY MODIFY IF EXPERIENCING RATE LIMITING
# ==============================================================================

# Fast Mode - Optimized for speed (~15 minutes)
TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'deduplication_delay': 20.0,
    'mindmap_delay': 15.0,
    'source_import_wait': 15.0,
}

# Deep Mode - Conservative timing (~45 minutes)
DEEP_TIMINGS = {
    'notebook_creation_delay': 5.0,
    'source_add_delay': (3.0, 5.0),
    'source_processing_delay': 60.0,
    'ask_prompt_delay': (45.0, 60.0),
    'chat_prompt_delay': (60.0, 90.0),
    'deduplication_delay': 30.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 30.0,
}

# Retry behavior
RETRY_CONFIG = {
    'max_attempts': 3,
    'base_delay': 5.0,
    'ask_max_attempts': 5,
    'ask_base_delay': 15.0,
}

# PDF settings
PDF_CONSOLIDATION = {
    'enabled': True,
    'output_suffix': '-One.pdf',
    'max_file_size_mb': 500,
}

# Authentication
AUTH_CHECK_INTERVAL = 300
AUTH_PROFILE = "default"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(processName)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# Optional: Additional products (uncomment if needed)
# product_security = "Red Hat Advanced Cluster Security"
# product_ai = "Red Hat OpenShift AI"
# company_tagline = "the world's leading provider of enterprise open source solutions"
# services_types = "consulting, implementation, training, and managed services"
