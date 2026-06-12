# ==============================================================================
# PROJECT APE - MULTI-CLIENT CONFIGURATION EXAMPLE
# Shows how to configure multiple clients in one vars.py file
# ==============================================================================

from pathlib import Path

# ==============================================================================
# CLIENT DEFINITIONS
# ==============================================================================

clients = [
    "acme_corp",
    "globex_inc",
    "initech_llc",
]

# --- ACME Corporation ---
acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology and cloud services"
acme_corp_subsegments = "cloud infrastructure, SaaS platforms, DevOps automation"
acme_corp_folder = "/app/client_data/ACME_Corp"

# --- Globex Inc ---
globex_inc_name = "Globex Inc"
globex_inc_industry = "manufacturing and industrial automation"
globex_inc_subsegments = "robotics, supply chain automation, predictive maintenance, IoT"
globex_inc_folder = "/app/client_data/Globex_Inc"

# --- Initech LLC ---
initech_llc_name = "Initech LLC"
initech_llc_industry = "financial services"
initech_llc_subsegments = "banking, payment processing, fintech, regulatory compliance"
initech_llc_folder = "/app/client_data/Initech_LLC"

# ==============================================================================
# EXECUTION MODES & TIMING
# ==============================================================================

default_mode = "fast"

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
# PATHS
# ==============================================================================

PROJECT_ROOT = Path("/app")
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
