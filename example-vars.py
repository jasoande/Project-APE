"""
Project APE - Configuration File
=================================

This file contains all configuration needed to run Project APE.

REQUIRED CONFIGURATION:
- clients: List of client IDs to process
- For each client, define: {client_id}_name, {client_id}_industry, {client_id}_folder

OPTIONAL CONFIGURATION:
- TIMINGS: Adjust delays for Fast mode
- DEEP_TIMINGS: Adjust delays for Deep mode
- DASHBOARD_PORT: Change dashboard port (default: 8765)
"""

from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATION
# ==============================================================================
#
# Step 1: Add your client IDs to the 'clients' list
# Step 2: For each client ID, define three variables:
#   - {client_id}_name: Display name (shown in dashboard)
#   - {client_id}_industry: Industry description (used in research prompts)
#   - {client_id}_folder: Path to folder containing client documents
#
# Example:
#   clients = ["acme_corp", "globex_inc"]
#
#   acme_corp_name = "ACME Corporation"
#   acme_corp_industry = "manufacturing and logistics"
#   acme_corp_folder = str(Path(__file__).parent / "client_data" / "ACME_Corp")
#
#   globex_inc_name = "Globex Inc"
#   globex_inc_industry = "technology and software"
#   globex_inc_folder = str(Path(__file__).parent / "client_data" / "Globex_Inc")
#
# ==============================================================================

# List of clients to process (add your client IDs here)
clients = [
    "example_client_1",
    "example_client_2",
]

# --- Example Client 1 Configuration ---
example_client_1_name = "Example Client 1"
example_client_1_industry = "technology and software"
example_client_1_folder = str(Path(__file__).parent / "client_data" / "Example_Client_1")

# --- Example Client 2 Configuration ---
example_client_2_name = "Example Client 2"
example_client_2_industry = "financial services"
example_client_2_folder = str(Path(__file__).parent / "client_data" / "Example_Client_2")

# ==============================================================================
# TIMING CONFIGURATION
# ==============================================================================
#
# Fast Mode: Optimized for speed (13-15 min per client, 15-16 min for 6 parallel)
# Deep Mode: Conservative timing for comprehensive research (30-90 min per client)
#
# Delays are in seconds. Tuple values (min, max) pick random delay in that range.
#
# WARNING: Reducing delays may cause rate limiting. Only adjust if you understand
# the implications or are experiencing issues.
# ==============================================================================

# FAST MODE - Optimized for speed
TIMINGS = {
    'notebook_creation_delay': 3.0,           # Wait after creating notebook
    'source_add_delay': (2.0, 4.0),          # Wait between adding sources
    'source_processing_delay': 30.0,          # Wait after uploading documents
    'ask_prompt_delay': (8.0, 12.0),         # Wait between research prompts
    'chat_prompt_delay': (5.0, 8.0),         # Wait between chat prompts
    'deduplication_delay': 20.0,              # Wait before deduplication
    'mindmap_delay': 15.0,                    # Wait before mind map generation
    'source_import_wait': 15.0,               # Wait for async source imports
}

# DEEP MODE - Conservative timing for comprehensive research
DEEP_TIMINGS = {
    'notebook_creation_delay': 5.0,
    'source_add_delay': (3.0, 5.0),
    'source_processing_delay': 60.0,          # Longer wait for bulk uploads
    'ask_prompt_delay': (45.0, 60.0),        # Deep research is network intensive
    'chat_prompt_delay': (60.0, 90.0),       # Conservative chat delays
    'deduplication_delay': 30.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 30.0,               # Longer wait for deep imports
}

# ==============================================================================
# DASHBOARD CONFIGURATION
# ==============================================================================

# Port for dashboard web server (default: 8765)
# Change if port 8765 is already in use on your system
DASHBOARD_PORT = 8765

# ==============================================================================
# DIRECTORY SETUP (Do not modify)
# ==============================================================================

# These directories are created automatically
PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
STATUS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
