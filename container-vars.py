# ==============================================================================
# PROJECT APE - CONTAINER CONFIGURATION (Jason's Version)
# Streamlined vars file for container execution
# ==============================================================================

from pathlib import Path

# ==============================================================================
# GLOBAL SETTINGS
# ==============================================================================

# Persona for AI responses in chat prompts
# This determines the perspective and expertise level of the generated content
# Examples:
#   - "Red Hat account executive"
#   - "Red Hat solutions architect"
#   - "Red Hat marketing specialist"
#   - "Red Hat customer success manager"
#   - "Red Hat technical account manager"
#   - "senior industry analyst"
persona = "Red Hat solutions architect"

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
blue_yonder_test_subsegments = "warehouse management systems, transportation management, demand forecasting, inventory optimization"
blue_yonder_test_folder = "/app/client_data/Blue_Yonder"

# --- Organon Configuration ---
organon_test_name = "Organon"
organon_test_industry = "pharmaceuticals and healthcare"
organon_test_subsegments = "women's health, biosimilars, established brands, specialty pharmaceuticals"
organon_test_folder = "/app/client_data/Organon"

# --- Panasonic Avionics Configuration ---
panasonic_avionics_test_name = "Panasonic Avionics"
panasonic_avionics_test_industry = "electronics, technology, and manufacturing"
panasonic_avionics_test_subsegments = "in-flight entertainment systems, connectivity solutions, passenger experience, cabin management systems"
panasonic_avionics_test_folder = "/app/client_data/Panasonic_Avionics"

# --- Hershey Configuration ---
hershey_test_name = "Hershey"
hershey_test_industry = "confectionery and snack food manufacturing"
hershey_test_subsegments = "chocolate products, sweets and refreshments, snack bars, premium and artisan confections"
hershey_test_folder = "/app/client_data/Hershey"

# --- Lord Abbett Configuration ---
lord_abbett_test_name = "Lord Abbett"
lord_abbett_test_industry = "financial services"
lord_abbett_test_subsegments = "investment management, mutual funds, fixed income, equity strategies, wealth management"
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
    'source_import_wait': 20.0,               # Reduced from 45.0 - imports complete faster
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
