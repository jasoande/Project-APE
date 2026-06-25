"""
Configuration Parser
====================
Parses existing vars.py files into structured data for editing
"""

import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional


def parse_vars_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse vars.py file into structured dict of clients and settings.

    Args:
        file_path: Path to vars.py file

    Returns:
        Dict with keys: clients (list), settings (dict)

    Raises:
        FileNotFoundError: If vars.py doesn't exist
        ImportError: If vars.py can't be imported
        AttributeError: If required attributes missing
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # Load vars.py as a module (same pattern as main.py)
    spec = importlib.util.spec_from_file_location("config", file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load configuration from {file_path}")

    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    # Extract client configurations
    clients = extract_client_configs(config)

    # Extract global settings
    settings = extract_global_settings(config)

    return {
        'clients': clients,
        'settings': settings
    }


def extract_client_configs(config_module) -> List[Dict[str, str]]:
    """
    Extract client configurations from loaded vars.py module.

    Args:
        config_module: Loaded Python module

    Returns:
        List of client dicts with keys: id, name, folder, industry, subsegments
    """
    clients = []

    # Get client list
    client_ids = getattr(config_module, 'clients', [])

    if not client_ids:
        return []

    # Extract each client's configuration
    for client_id in client_ids:
        client = {
            'id': client_id,
            'name': getattr(config_module, f'{client_id}_name', client_id),
            'folder': getattr(config_module, f'{client_id}_folder', ''),
            'industry': getattr(config_module, f'{client_id}_industry', ''),
            'subsegments': getattr(config_module, f'{client_id}_subsegments', '')
        }
        clients.append(client)

    return clients


def extract_global_settings(config_module) -> Dict[str, Any]:
    """
    Extract global settings from loaded vars.py module.

    Args:
        config_module: Loaded Python module

    Returns:
        Dict of global settings (persona, default_mode, TIMINGS, etc.)
    """
    settings = {}

    # Simple string/int settings
    settings['persona'] = getattr(config_module, 'persona', 'Red Hat solutions architect')
    settings['default_mode'] = getattr(config_module, 'default_mode', 'fast')
    settings['DASHBOARD_PORT'] = getattr(config_module, 'DASHBOARD_PORT', 8765)
    settings['DASHBOARD_REFRESH_INTERVAL'] = getattr(config_module, 'DASHBOARD_REFRESH_INTERVAL', 2)

    # Complex dict settings - convert to JSON-serializable format
    settings['TIMINGS'] = dict(getattr(config_module, 'TIMINGS', {}))
    settings['DEEP_TIMINGS'] = dict(getattr(config_module, 'DEEP_TIMINGS', {}))
    settings['RETRY_CONFIG'] = dict(getattr(config_module, 'RETRY_CONFIG', {}))
    settings['DRIVE_CONFIG'] = dict(getattr(config_module, 'DRIVE_CONFIG', {}))
    settings['PDF_CONSOLIDATION'] = dict(getattr(config_module, 'PDF_CONSOLIDATION', {}))
    settings['GEMINI_AGENT_CONFIG'] = dict(getattr(config_module, 'GEMINI_AGENT_CONFIG', {}))
    settings['QUALITY_THRESHOLDS'] = dict(getattr(config_module, 'QUALITY_THRESHOLDS', {}))
    settings['ARTIFACT_VERIFICATION'] = dict(getattr(config_module, 'ARTIFACT_VERIFICATION', {}))

    # Logging settings
    settings['AUTH_CHECK_INTERVAL'] = getattr(config_module, 'AUTH_CHECK_INTERVAL', 300)
    settings['AUTH_PROFILE'] = getattr(config_module, 'AUTH_PROFILE', 'default')
    settings['LOG_LEVEL'] = getattr(config_module, 'LOG_LEVEL', 'INFO')
    settings['LOG_FORMAT'] = getattr(config_module, 'LOG_FORMAT',
                                     '%(asctime)s | %(levelname)s | [%(processName)s] %(message)s')
    settings['LOG_DATE_FORMAT'] = getattr(config_module, 'LOG_DATE_FORMAT', '%H:%M:%S')

    return settings


def get_editable_settings_schema() -> Dict[str, Any]:
    """
    Get schema of editable settings with their types and constraints.

    Returns:
        Dict describing editable settings structure for frontend
    """
    return {
        'persona': {
            'type': 'string',
            'label': 'Persona',
            'description': 'Role perspective for AI responses (e.g., solutions architect, account executive)',
            'examples': [
                'Red Hat solutions architect',
                'account executive',
                'solutions engineer',
                'customer success manager',
                'technical account manager'
            ]
        },
        'default_mode': {
            'type': 'select',
            'label': 'Default Execution Mode',
            'description': 'Default mode when --mode not specified',
            'options': ['fast', 'deep'],
            'default': 'fast'
        },
        'DASHBOARD_PORT': {
            'type': 'number',
            'label': 'Dashboard Port',
            'description': 'Port for dashboard server',
            'min': 1024,
            'max': 65535,
            'default': 8765
        },
        'TIMINGS': {
            'type': 'dict',
            'label': 'Fast Mode Timings',
            'description': 'Delay settings for fast mode (10-15 min target)',
            'editable': True,
            'fields': {
                'notebook_creation_delay': {'type': 'number', 'unit': 'seconds'},
                'source_add_delay': {'type': 'tuple', 'unit': 'seconds', 'description': '(min, max) range'},
                'source_processing_delay': {'type': 'number', 'unit': 'seconds'},
                'ask_prompt_delay': {'type': 'tuple', 'unit': 'seconds'},
                'chat_prompt_delay': {'type': 'tuple', 'unit': 'seconds'},
                'deduplication_delay': {'type': 'number', 'unit': 'seconds'},
                'mindmap_delay': {'type': 'number', 'unit': 'seconds'},
                'source_import_wait': {'type': 'number', 'unit': 'seconds'}
            }
        },
        'DEEP_TIMINGS': {
            'type': 'dict',
            'label': 'Deep Mode Timings',
            'description': 'Delay settings for deep mode (35-40 min target)',
            'editable': True,
            'fields': {
                'notebook_creation_delay': {'type': 'number', 'unit': 'seconds'},
                'source_add_delay': {'type': 'tuple', 'unit': 'seconds'},
                'source_processing_delay': {'type': 'number', 'unit': 'seconds'},
                'ask_prompt_delay': {'type': 'tuple', 'unit': 'seconds'},
                'chat_prompt_delay': {'type': 'tuple', 'unit': 'seconds'},
                'deduplication_delay': {'type': 'number', 'unit': 'seconds'},
                'mindmap_delay': {'type': 'number', 'unit': 'seconds'},
                'source_import_wait': {'type': 'number', 'unit': 'seconds'}
            }
        },
        'DRIVE_CONFIG': {
            'type': 'dict',
            'label': 'Google Drive Configuration',
            'description': 'Settings for Google Drive integration',
            'editable': True,
            'fields': {
                'cache_enabled': {'type': 'boolean', 'label': 'Enable Cache'},
                'cache_ttl_hours': {'type': 'number', 'label': 'Cache TTL', 'unit': 'hours'},
                'export_google_docs': {'type': 'boolean', 'label': 'Export Google Docs to PDF'},
                'recursive': {'type': 'boolean', 'label': 'Recursive Folder Scan'},
                'max_file_size_mb': {'type': 'number', 'label': 'Max File Size', 'unit': 'MB'}
            }
        }
    }


def validate_settings(settings: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate global settings values.

    Args:
        settings: Settings dict to validate

    Returns:
        Tuple of (valid, error_messages)
    """
    errors = []

    # Validate persona
    if 'persona' in settings:
        if not isinstance(settings['persona'], str) or not settings['persona'].strip():
            errors.append("persona must be a non-empty string")

    # Validate default_mode
    if 'default_mode' in settings:
        if settings['default_mode'] not in ['fast', 'deep']:
            errors.append("default_mode must be 'fast' or 'deep'")

    # Validate DASHBOARD_PORT
    if 'DASHBOARD_PORT' in settings:
        port = settings['DASHBOARD_PORT']
        if not isinstance(port, int) or port < 1024 or port > 65535:
            errors.append("DASHBOARD_PORT must be integer between 1024-65535")

    # Validate TIMINGS structure
    for timing_key in ['TIMINGS', 'DEEP_TIMINGS']:
        if timing_key in settings:
            timings = settings[timing_key]
            if not isinstance(timings, dict):
                errors.append(f"{timing_key} must be a dict")
                continue

            required_keys = [
                'notebook_creation_delay', 'source_add_delay',
                'source_processing_delay', 'ask_prompt_delay',
                'chat_prompt_delay', 'deduplication_delay',
                'mindmap_delay', 'source_import_wait'
            ]

            for key in required_keys:
                if key not in timings:
                    errors.append(f"{timing_key} missing required key: {key}")

    return (len(errors) == 0, errors)
