# ==============================================================================
# PROJECT APE - SINGLE CLIENT CONTAINER EXAMPLE
# Configuration template for containerized single-client execution
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
# CLIENT DEFINITION
# ==============================================================================

# Single client configuration
clients = [
    "example_client",
]

# --- Example Client Configuration ---
example_client_name = "Example Corporation"
example_client_industry = "technology"
example_client_subsegments = "cloud computing, enterprise software, cybersecurity"
example_client_folder = "/app/client_data/Example_Corporation"

# ==============================================================================
# EXECUTION MODES & TIMING
# ==============================================================================

default_mode = "fast"

# FAST MODE - Optimized for speed (10-15 minutes per client)
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

# DEEP MODE - Balanced delays for quality with improved performance
# Optimized based on actual API timing analysis while maintaining safety margins
DEEP_TIMINGS = {
    'notebook_creation_delay': 3.0,           # Reduced from 5.0 - no quota impact
    'source_add_delay': (2.0, 4.0),           # Reduced from (3.0, 5.0) - safe range
    'source_processing_delay': 45.0,          # Reduced from 90.0 - still conservative
    'ask_prompt_delay': (15.0, 25.0),         # Reduced from (90.0, 120.0) - API handles spacing
    'chat_prompt_delay': (10.0, 15.0),        # Reduced from (120.0, 180.0) - consolidated prompts longer
    'deduplication_delay': 25.0,              # Reduced from 45.0 - operation is fast
    'mindmap_delay': 20.0,                    # Reduced from 30.0 - operation is fast
    'source_import_wait': 30.0,               # Increased from 20.0 - deep mode imports 90-180 sources
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
# CONTAINER PATHS (for containerized execution)
# ==============================================================================

PROJECT_ROOT = Path("/app")
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
