"""
Example vars.py for Project APE Container
==========================================
Copy this file to vars.py and customize for your clients
"""

from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATIONS
# ==============================================================================

clients = [
    "example_client",
]

# --- Example Client ---
example_client_name = "Example Corporation"

# Google Drive folder (container will download at runtime)
example_client_folder = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID_HERE"

# OR Local folder path (mount as volume)
# example_client_folder = "/app/client_data/example_client"

example_client_industry = "technology"
example_client_subsegments = "cloud computing, enterprise software, AI/ML"

# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

# Persona for AI responses
persona = "solutions architect"

# Default execution mode
default_mode = "fast"

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds

# ==============================================================================
# EXECUTION TIMING PROFILES
# ==============================================================================

# FAST MODE - Optimized for speed (15-20 minute target)
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

# DEEP MODE - Enhanced quality (35-40 minute target)
DEEP_TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 45.0,
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    'deduplication_delay': 25.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 15.0,
}

# ==============================================================================
# QUALITY THRESHOLDS
# ==============================================================================

QUALITY_THRESHOLDS = {
    'min_sources': 15,
    'required_notes': 6,
    'min_quality_score': 8.5,
}

# ==============================================================================
# GOOGLE DRIVE CONFIGURATION
# ==============================================================================

DRIVE_CONFIG = {
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'download_timeout': 300,
}

# ==============================================================================
# GEMINI AGENT CONFIGURATION
# ==============================================================================

GEMINI_AGENT_CONFIG = {
    'enabled': True,  # Enable intelligent orchestration
    'model': 'gemini-2.0-flash-exp',
    'max_retries': 3,
    'recovery_enabled': True,
}

# ==============================================================================
# PATHS (Container-specific)
# ==============================================================================

STATUS_DIR = Path('/app/.multi_process_status')
LOGS_DIR = Path('/app/logs')
