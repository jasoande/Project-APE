# ==============================================================================
# PROJECT APE - MARRIAGE (Unified Version)
# Configuration File
# ==============================================================================

import os
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
merck_test_folder = str(Path(__file__).parent / "Venella_2026" / "Merck")

# --- Blue Yonder Configuration ---
blue_yonder_test_name = "Blue Yonder"
blue_yonder_test_industry = "AI-driven supply chain management"
blue_yonder_test_folder = str(Path(__file__).parent / "Venella_2026" / "Blue_Yonder")

# --- Organon Configuration ---
organon_test_name = "Organon"
organon_test_industry = "pharmaceuticals and healthcare"
organon_test_folder = str(Path(__file__).parent / "Venella_2026" / "Organon")

# --- Panasonic Avionics Configuration ---
panasonic_avionics_test_name = "Panasonic Avionics"
panasonic_avionics_test_industry = "electronics, technology, and manufacturing"
panasonic_avionics_test_folder = str(Path(__file__).parent / "Venella_2026" / "Panasonic_Avionics")

# --- Hershey Configuration ---
hershey_test_name = "Hershey"
hershey_test_industry = "confectionery and snack food manufacturing"
hershey_test_folder = str(Path(__file__).parent / "Venella_2026" / "Hershey")

# --- Lord Abbett Configuration ---
lord_abbett_test_name = "Lord Abbett"
lord_abbett_test_industry = "financial services"
lord_abbett_test_folder = str(Path(__file__).parent / "Venella_2026" / "Lord_Abbett")

# ==============================================================================
# EXECUTION MODES & TIMING
# ==============================================================================

# Default execution mode
default_mode = "fast"

# Timing configuration (in seconds)
# FAST MODE - Optimized for speed (sub-16 minute target)
TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,  # After bulk upload
    'ask_prompt_delay': (8.0, 12.0),  # Research questions - minimum safe delay
    'chat_prompt_delay': (5.0, 8.0),   # Chat prompts - minimum safe delay
    'deduplication_delay': 20.0,
    'mindmap_delay': 15.0,
    'source_import_wait': 15.0,  # Wait after research for async imports
}

# DEEP MODE - Conservative delays for extreme rate limiting
DEEP_TIMINGS = {
    'notebook_creation_delay': 5.0,
    'source_add_delay': (3.0, 5.0),
    'source_processing_delay': 60.0,  # Longer wait after bulk upload
    'ask_prompt_delay': (45.0, 60.0),  # Deep research is network intensive
    'chat_prompt_delay': (60.0, 90.0),  # Conservative delays for chat
    'deduplication_delay': 30.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 30.0,  # Longer wait for deep research imports
}

# Retry configuration
RETRY_CONFIG = {
    'max_attempts': 3,
    'base_delay': 5.0,
    'ask_max_attempts': 5,  # Research needs more retries
    'ask_base_delay': 15.0,
}

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds

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

AUTH_CHECK_INTERVAL = 300  # Check auth every 5 minutes
AUTH_PROFILE = "default"  # NotebookLM profile name

# ==============================================================================
# LOGGING SETTINGS
# ==============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(processName)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# ==============================================================================
# PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Create directories
STATUS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)
