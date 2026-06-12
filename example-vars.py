# ==============================================================================
# PROJECT APE - CONTAINER CONFIGURATION (Jason's Version)
# Streamlined vars file for container execution
# ==============================================================================

from pathlib import Path

# ==============================================================================
# GLOBAL SETTINGS
# ==============================================================================

# Persona for all prompts
persona = "senior account solutions architect"

# Company branding
company_name = "Red Hat"
company_tagline = "the world's leading provider of enterprise open source solutions"

# Product portfolio
product_platform = "Red Hat Enterprise Linux (RHEL)"
product_containers = "OpenShift Container Platform"
product_automation = "Ansible Automation Platform"
product_security = "Red Hat Advanced Cluster Security"
product_ai = "Red Hat OpenShift AI"

# Services
services_types = "consulting, implementation, training, and managed services"

# ==============================================================================
# CLIENT DEFINITIONS
# ==============================================================================

clients = [
    "merck_test",
    "blue_yonder_test",
    "organon_test",
    "panasonic_avionics_test",
    "hershey_test",
    "lord_abbett_test"
]

# --- Merck Configuration ---
merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_subsegments = "oncology, vaccines, rare diseases, women's health"
merck_test_folder = "/app/client_data/Merck"

# --- Blue Yonder Configuration ---
blue_yonder_test_name = "Blue Yonder"
blue_yonder_test_industry = "AI-driven supply chain management"
blue_yonder_test_folder = "/app/client_data/Blue_Yonder"

# --- Organon Configuration ---
organon_test_name = "Organon"
organon_test_industry = "pharmaceuticals and healthcare"
organon_test_folder = "/app/client_data/Organon"

# --- Panasonic Avionics Configuration ---
panasonic_avionics_test_name = "Panasonic Avionics"
panasonic_avionics_test_industry = "electronics, technology, and manufacturing"
panasonic_avionics_test_folder = "/app/client_data/Panasonic_Avionics"

# --- Hershey Configuration ---
hershey_test_name = "Hershey"
hershey_test_industry = "confectionery and snack food manufacturing"
hershey_test_folder = "/app/client_data/Hershey"

# --- Lord Abbett Configuration ---
lord_abbett_test_name = "Lord Abbett"
lord_abbett_test_industry = "financial services"
lord_abbett_test_folder = "/app/client_data/Lord_Abbett"

# ==============================================================================
# EXECUTION MODES & TIMING
# ==============================================================================

default_mode = "fast"

# FAST MODE - Optimized for speed (sub-16 minute target)
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

# DEEP MODE - Conservative delays for quota management
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

# Retry configuration
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
# CONTAINER PATHS (hardcoded for container environment)
# ==============================================================================

PROJECT_ROOT = Path("/app")
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Directories are created by container entrypoint - no mkdir needed
