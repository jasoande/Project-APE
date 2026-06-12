# ==============================================================================
# PROJECT APE - EXAMPLE CONFIGURATION
# Configuration Template - Copy to vars.py and customize
# ==============================================================================

from pathlib import Path

# ==============================================================================
# PERSONA CONFIGURATION
# ==============================================================================

# Define the persona/role for AI responses in chat prompts
# This determines the perspective and expertise level of the generated content
# Examples:
#   - "Red Hat account executive"
#   - "Red Hat solutions architect"
#   - "Red Hat marketing specialist"
#   - "Red Hat customer success manager"
#   - "Red Hat technical account manager"
#   - "senior industry analyst"
persona = "Red Hat solutions architect"

# ==============================================================================
# CLIENT DEFINITIONS
# ==============================================================================

clients = [
    "example_client",
]

# --- Example Client Configuration ---
example_client_name = "Example Corporation"
example_client_industry = "technology"
example_client_subsegments = "cloud computing, enterprise software, cybersecurity"
example_client_folder = "/app/client_data/Example_Corporation"

# ==============================================================================
# EXECUTION MODES & TIMING (Advanced - Usually no changes needed)
# ==============================================================================

default_mode = "fast"

# FAST MODE - Optimized for speed (12-16 minutes per client)
TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'deduplication_delay': 20.0,
    'mindmap_delay': 15.0,
    'source_import_wait': 10.0,
}

# DEEP MODE - Conservative delays for quota management (30-90 minutes per client)
DEEP_TIMINGS = {
    'notebook_creation_delay': 5.0,
    'source_add_delay': (3.0, 5.0),
    'source_processing_delay': 90.0,
    'ask_prompt_delay': (90.0, 120.0),
    'chat_prompt_delay': (120.0, 180.0),
    'deduplication_delay': 45.0,
    'mindmap_delay': 30.0,
    'source_import_wait': 45.0,
}

# Retry configuration for API errors
RETRY_CONFIG = {
    'max_attempts': 5,
    'base_delay': 10.0,
    'ask_max_attempts': 7,
    'ask_base_delay': 30.0,
}

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2

# ==============================================================================
# PDF CONSOLIDATION SETTINGS
# ==============================================================================

PDF_CONSOLIDATION = {
    'enabled': True,
    'output_suffix': '-One.pdf',
    'max_file_size_mb': 500,
}

# ==============================================================================
# AUTHENTICATION SETTINGS
# ==============================================================================

AUTH_CHECK_INTERVAL = 300
AUTH_PROFILE = "default"

# ==============================================================================
# LOGGING SETTINGS
# ==============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(processName)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# ==============================================================================
# PATHS (Auto-configured for containers - do not change)
# ==============================================================================

PROJECT_ROOT = Path("/app")
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
