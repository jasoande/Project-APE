# ==============================================================================
# PROJECT APE - MULTI-CLIENT CONFIGURATION EXAMPLE
# Shows how to configure multiple clients in one vars.py file
# ==============================================================================

from pathlib import Path
import os

# ==============================================================================
# PERSONA CONFIGURATION
# ==============================================================================

# Define the persona/role for AI responses in chat prompts
# Customize based on your department and use case:
persona = "Red Hat solutions architect"

# Other persona examples:
#   - "Red Hat account executive" (sales focus)
#   - "Red Hat marketing specialist" (campaigns/messaging)
#   - "Red Hat customer success manager" (post-sale)
#   - "senior industry analyst" (research focus)

# ==============================================================================
# CLIENT DEFINITIONS - 3 Example Clients
# ==============================================================================

clients = [
    "acme_corp",
    "globex_inc",
    "initech_llc",
]

# Detect if running in container or locally
if os.path.exists('/app/core'):
    # Running in container
    BASE_PATH = "/app/client_data"
else:
    # Running locally
    BASE_PATH = str(Path(__file__).parent / "client_data")

# -----------------------------------------------------------------------------
# Client 1: ACME Corporation (Technology)
# -----------------------------------------------------------------------------
acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_subsegments = "cloud infrastructure, SaaS platforms, DevOps automation, cybersecurity"
acme_corp_folder = f"{BASE_PATH}/ACME_Corp"

# -----------------------------------------------------------------------------
# Client 2: Globex Inc (Manufacturing)
# -----------------------------------------------------------------------------
globex_inc_name = "Globex Inc"
globex_inc_industry = "manufacturing"
globex_inc_subsegments = "robotics, supply chain automation, predictive maintenance, IoT sensors"
globex_inc_folder = f"{BASE_PATH}/Globex_Inc"

# -----------------------------------------------------------------------------
# Client 3: Initech LLC (Financial Services)
# -----------------------------------------------------------------------------
initech_llc_name = "Initech LLC"
initech_llc_industry = "financial services"
initech_llc_subsegments = "banking, payment processing, fintech innovation, regulatory compliance"
initech_llc_folder = f"{BASE_PATH}/Initech_LLC"

# ==============================================================================
# EXECUTION MODES & TIMING
# ==============================================================================

default_mode = "fast"

# FAST MODE - Optimized for speed (10-15 minutes per client)
TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,
    'ask_prompt_delay': (10.0, 15.0),  # Increased from 8-12s to reduce retry rate
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
    'ask_base_delay': 15.0,  # Reduced from 30s - faster recovery from transient errors
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
# PATHS (Container and Local Execution)
# ==============================================================================

# Auto-detect if running in container or locally
if os.path.exists('/app/core'):
    # Running in container
    PROJECT_ROOT = Path("/app")
else:
    # Running locally
    PROJECT_ROOT = Path(__file__).parent

STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs_generated"

# ==============================================================================
# USAGE NOTES
# ==============================================================================

# To use this configuration:
# 1. Copy this file: cp example-multi-client-vars.py vars.py
# 2. Update client names, industries, and subsegments
# 3. Create client data directories:
#    mkdir -p client_data/ACME_Corp
#    mkdir -p client_data/Globex_Inc
#    mkdir -p client_data/Initech_LLC
# 4. Add client documents to each directory
# 5. Run: python3 main.py --mode fast --clients acme_corp globex_inc initech_llc
#    Or: ./ape-run.sh --vars ./vars.py --mode fast
