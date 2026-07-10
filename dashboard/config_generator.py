"""
Configuration Generator
=======================
Generates valid vars.py configuration files from client data
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def sanitize_client_id(name: str) -> str:
    """
    Convert client name to valid Python identifier.

    Args:
        name: Client display name (e.g., "Acme Corp")

    Returns:
        Valid Python identifier (e.g., "acme_corp")
    """
    # Convert to lowercase
    client_id = name.lower()

    # Replace spaces and hyphens with underscores
    client_id = re.sub(r'[\s-]+', '_', client_id)

    # Remove any characters that aren't alphanumeric or underscore
    client_id = re.sub(r'[^a-z0-9_]', '', client_id)

    # Ensure it doesn't start with a number
    if client_id and client_id[0].isdigit():
        client_id = '_' + client_id

    # Limit length to 64 characters
    client_id = client_id[:64]

    return client_id


def validate_client_data(client: Dict) -> Tuple[bool, str]:
    """
    Validate single client configuration.

    Args:
        client: Client configuration dict with keys: id, name, folder, industry, subsegments

    Returns:
        Tuple of (valid, error_message). error_message is empty string if valid.
    """
    # Check required fields
    required_fields = ['id', 'name', 'folder', 'industry', 'subsegments']
    for field in required_fields:
        if field not in client:
            return False, f"Missing required field: {field}"

        if not isinstance(client[field], str):
            return False, f"Field '{field}' must be a string"

        # Allow empty industry/subsegments (can be auto-detected)
        if field in ['id', 'name', 'folder'] and not client[field].strip():
            return False, f"Field '{field}' cannot be empty"

    # Validate client ID format (must be valid Python identifier)
    client_id = client['id']
    if not re.match(r'^[a-z_][a-z0-9_]*$', client_id):
        return False, f"Client ID '{client_id}' must be a valid Python identifier (lowercase, alphanumeric, underscores only)"

    # Validate Drive URL format if it looks like a URL
    folder = client['folder']
    if 'drive.google.com' in folder or 'drive://' in folder:
        # Use same regex as drive_manager.py
        folder_id_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder)
        if not folder_id_match and not folder.startswith('drive://'):
            return False, f"Invalid Drive URL format for '{client['name']}'. Expected: https://drive.google.com/drive/folders/FOLDER_ID"

    return True, ""


def escape_python_string(value: str) -> str:
    """
    Escape special characters in string for Python code generation.

    Args:
        value: String value to escape

    Returns:
        Escaped string safe for Python code
    """
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace("'", "\\'")
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\t', '\\t')
    value = value.replace('\0', '\\0')
    return value


def format_client_section(client: Dict) -> str:
    """
    Format 4-line client configuration section.

    Args:
        client: Client configuration dict

    Returns:
        Formatted Python code for client configuration
    """
    client_id = client['id']
    name = escape_python_string(client['name'])
    folder = escape_python_string(client['folder'])
    industry = escape_python_string(client.get('industry', ''))
    subsegments = escape_python_string(client.get('subsegments', ''))

    section = f'''# --- {client['name']} ---
{client_id}_name = "{name}"
{client_id}_folder = "{folder}"
{client_id}_industry = "{industry}"
{client_id}_subsegments = "{subsegments}"
'''

    return section


def generate_vars_py(clients_data: List[Dict]) -> str:
    """
    Generate complete vars.py content from client data.

    Args:
        clients_data: List of client configuration dicts

    Returns:
        Complete vars.py file content as string

    Raises:
        ValueError: If validation fails or generated code has syntax errors
    """
    # Validate all clients first
    errors = []
    for client in clients_data:
        valid, error = validate_client_data(client)
        if not valid:
            errors.append(error)

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Check for duplicate client IDs
    client_ids = [c['id'] for c in clients_data]
    duplicates = set([cid for cid in client_ids if client_ids.count(cid) > 1])
    if duplicates:
        raise ValueError(f"Duplicate client IDs found: {', '.join(duplicates)}")

    # Generate client list
    client_list_items = ',\n    '.join(f'"{c["id"]}"' for c in clients_data)
    client_list = f'''clients = [
    {client_list_items}
]'''

    # Generate client sections
    client_sections = '\n'.join(format_client_section(c) for c in clients_data)

    # Complete template with all static configuration
    vars_content = f'''"""
Account Intelligence Configuration
==========================
Generated by Web Configuration Tool on {Path(__file__).parent.parent / "dashboard"}
All configuration settings for the Account Planning Engine
"""

from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATIONS
# ==============================================================================
# Define all clients with their settings in one place

{client_list}

{client_sections}
# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

# Persona for AI responses in chat prompts
persona = "Red Hat solutions architect"

# Default execution mode
default_mode = "fast"

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2  # seconds

# ==============================================================================
# SSL/HTTPS CONFIGURATION (Optional)
# ==============================================================================
# Enable HTTPS for secure dashboard access

SSL_ENABLED = False  # Set to True to enable HTTPS
SSL_CERT_PATH = ""   # Path to SSL certificate file (e.g., "certs/cert.pem")
SSL_KEY_PATH = ""    # Path to SSL private key file (e.g., "certs/key.pem")

# ==============================================================================
# EXECUTION TIMING PROFILES
# ==============================================================================

# FAST MODE - Optimized for speed (10-15 minute target)
TIMINGS = {{
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 30.0,
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'deduplication_delay': 20.0,
    'mindmap_delay': 15.0,
    'source_import_wait': 10.0,
}}

# DEEP MODE - Enhanced quality (35-40 minute target)
DEEP_TIMINGS = {{
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 45.0,
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    'deduplication_delay': 25.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 30.0,
}}

# Retry configuration
RETRY_CONFIG = {{
    'max_attempts': 5,
    'base_delay': 10.0,
    'ask_max_attempts': 7,
    'ask_base_delay': 30.0,
}}

# ==============================================================================
# GOOGLE DRIVE INTEGRATION
# ==============================================================================

DRIVE_CONFIG = {{
    'enabled': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}}

# ==============================================================================
# PDF CONSOLIDATION
# ==============================================================================

PDF_CONSOLIDATION = {{
    'enabled': True,
    'output_suffix': '-One.pdf',
    'max_file_size_mb': 500,
}}

# ==============================================================================
# GEMINI AI AGENT ORCHESTRATION
# ==============================================================================

GEMINI_AGENT_CONFIG = {{
    'enabled': True,
    'model': 'gemini-2.5-flash',
    'temperature': 0.2,
    'max_retries': 5,
    'retry_base_delay': 10.0,
    'timeout': 60,
    'enable_error_analysis': True,
    'enable_quality_validation': True,
    'enable_self_healing': True,
    'quality_target': 8.5,
}}

# NOTE: Industry detection via Gemini has been removed
# Industry and subsegments are now configured manually above per client
# This provides more accurate, predictable results

# ==============================================================================
# QUALITY SCORING & VERIFICATION
# ==============================================================================

QUALITY_THRESHOLDS = {{
    'min_sources': 40,           # Minimum sources for full points (increased from 15)
    'required_notes': 6,          # All 6 chat prompts must succeed
    'min_quality_score': 8.5,     # Target quality score
    'source_diversity': True,     # Check for diverse source types
    'verify_mindmap': True,       # Ensure mindmap is non-trivial
}}

ARTIFACT_VERIFICATION = {{
    'enabled': True,
    'verify_notebook': True,
    'verify_sources': True,
    'verify_notes': True,
    'verify_mindmap': True,
    'export_notes_for_verification': True,
}}

# ==============================================================================
# AUTHENTICATION & LOGGING
# ==============================================================================

AUTH_CHECK_INTERVAL = 300
AUTH_PROFILE = "default"

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(processName)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# ==============================================================================
# PROJECT PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
'''

    # Validate generated Python syntax
    try:
        compile(vars_content, '<generated>', 'exec')
    except SyntaxError as e:
        raise ValueError(f"Generated configuration has syntax error: {e}")

    return vars_content


def _is_numeric_sequence(s: str) -> bool:
    """Check if string looks like a serialized tuple or list of numbers."""
    if not isinstance(s, str):
        return False
    s = s.strip()
    # Match patterns like "[8, 12]" or "(8, 12)" or "[8,12]" or "(8,12)"
    return bool(re.match(r'^[\(\[][\s\d,\.]+[\)\]]$', s))


def _parse_numeric_sequence(s: str) -> list:
    """Parse '(8, 12)' or '[8, 12]' into a list of numbers. Returns None on failure."""
    s = s.strip()
    inner = s[1:-1]
    try:
        parts = [float(x.strip()) for x in inner.split(',') if x.strip()]
        return [int(x) if x == int(x) else x for x in parts]
    except (ValueError, TypeError):
        return None


def generate_vars_py_full(clients_data: List[Dict], settings: Dict) -> str:
    """
    Generate complete vars.py content with custom global settings.

    Args:
        clients_data: List of client configuration dicts
        settings: Dict of global settings to customize

    Returns:
        Complete vars.py file content as string

    Raises:
        ValueError: If validation fails or generated code has syntax errors
    """
    # Validate all clients first
    errors = []
    for client in clients_data:
        valid, error = validate_client_data(client)
        if not valid:
            errors.append(error)

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Check for duplicate client IDs
    client_ids = [c['id'] for c in clients_data]
    duplicates = set([cid for cid in client_ids if client_ids.count(cid) > 1])
    if duplicates:
        raise ValueError(f"Duplicate client IDs found: {', '.join(duplicates)}")

    # Extract settings with defaults
    persona = settings.get('persona', 'Red Hat solutions architect')
    default_mode = settings.get('default_mode', 'fast')
    dashboard_port = settings.get('DASHBOARD_PORT', 8765)
    dashboard_refresh = settings.get('DASHBOARD_REFRESH_INTERVAL', 2)

    # Get timing configurations
    timings = settings.get('TIMINGS', {
        'notebook_creation_delay': 3.0,
        'source_add_delay': (2.0, 4.0),
        'source_processing_delay': 30.0,
        'ask_prompt_delay': (8.0, 12.0),
        'chat_prompt_delay': (5.0, 8.0),
        'deduplication_delay': 20.0,
        'mindmap_delay': 15.0,
        'source_import_wait': 10.0,
    })

    deep_timings = settings.get('DEEP_TIMINGS', {
        'notebook_creation_delay': 3.0,
        'source_add_delay': (2.0, 4.0),
        'source_processing_delay': 45.0,
        'ask_prompt_delay': (15.0, 25.0),
        'chat_prompt_delay': (10.0, 15.0),
        'deduplication_delay': 25.0,
        'mindmap_delay': 20.0,
        'source_import_wait': 30.0,
    })

    retry_config = settings.get('RETRY_CONFIG', {
        'max_attempts': 5,
        'base_delay': 10.0,
        'ask_max_attempts': 7,
        'ask_base_delay': 30.0,
    })

    drive_config = settings.get('DRIVE_CONFIG', {
        'enabled': True,
        'cache_enabled': True,
        'cache_ttl_hours': 24,
        'export_google_docs': True,
        'recursive': False,
        'max_file_size_mb': 50,
    })

    pdf_consolidation = settings.get('PDF_CONSOLIDATION', {
        'enabled': True,
        'output_suffix': '-One.pdf',
        'max_file_size_mb': 500,
    })

    gemini_config = settings.get('GEMINI_AGENT_CONFIG', {
        'enabled': True,
        'model': 'gemini-2.5-flash',
        'temperature': 0.2,
        'max_retries': 5,
        'retry_base_delay': 10.0,
        'timeout': 60,
        'enable_error_analysis': True,
        'enable_quality_validation': True,
        'enable_self_healing': True,
        'quality_target': 8.5,
    })

    quality_thresholds = settings.get('QUALITY_THRESHOLDS', {
        'min_sources': 40,
        'required_notes': 6,
        'min_quality_score': 8.5,
        'source_diversity': True,
        'verify_mindmap': True,
    })

    artifact_verification = settings.get('ARTIFACT_VERIFICATION', {
        'enabled': True,
        'verify_notebook': True,
        'verify_sources': True,
        'verify_notes': True,
        'verify_mindmap': True,
        'export_notes_for_verification': True,
    })

    # Generate client list
    client_list_items = ',\n    '.join(f'"{c["id"]}"' for c in clients_data)
    client_list = f'''clients = [
    {client_list_items}
]'''

    # Generate client sections
    client_sections = '\n'.join(format_client_section(c) for c in clients_data)

    # Format timing dicts
    def format_dict(d, indent=1):
        """Format dict for Python code."""
        ind = '    ' * indent
        lines = []
        for k, v in d.items():
            if isinstance(v, (tuple, list)):
                # Already a tuple/list - format directly
                lines.append(f"{ind}'{k}': ({', '.join(str(x) for x in v)}),")
            elif isinstance(v, str):
                # Check if string looks like a numeric sequence
                if _is_numeric_sequence(v):
                    nums = _parse_numeric_sequence(v)
                    if nums is not None:
                        # Convert string "[8, 12]" to tuple (8, 12)
                        lines.append(f"{ind}'{k}': ({', '.join(str(x) for x in nums)}),")
                    else:
                        # Parse failed, keep as string
                        lines.append(f"{ind}'{k}': \"{v}\",")
                else:
                    # Regular string value
                    lines.append(f"{ind}'{k}': \"{v}\",")
            elif isinstance(v, bool):
                lines.append(f"{ind}'{k}': {str(v)},")
            elif isinstance(v, (int, float)):
                lines.append(f"{ind}'{k}': {v},")
            elif v is None:
                lines.append(f"{ind}'{k}': None,")
            else:
                lines.append(f"{ind}'{k}': \"{v}\",")
        return '\n'.join(lines)

    # Complete template with custom settings
    vars_content = f'''"""
Account Intelligence Configuration
==========================
Generated by Web Configuration Tool
All configuration settings for the Account Planning Engine
"""

from pathlib import Path

# ==============================================================================
# CLIENT CONFIGURATIONS
# ==============================================================================
# Define all clients with their settings in one place

{client_list}

{client_sections}
# ==============================================================================
# GENERAL SETTINGS
# ==============================================================================

# Persona for AI responses in chat prompts
persona = "{escape_python_string(persona)}"

# Default execution mode
default_mode = "{default_mode}"

# ==============================================================================
# DASHBOARD SETTINGS
# ==============================================================================

DASHBOARD_PORT = {dashboard_port}
DASHBOARD_REFRESH_INTERVAL = {dashboard_refresh}  # seconds

# ==============================================================================
# EXECUTION TIMING PROFILES
# ==============================================================================

# FAST MODE - Optimized for speed (10-15 minute target)
TIMINGS = {{
{format_dict(timings)}
}}

# DEEP MODE - Enhanced quality (35-40 minute target)
DEEP_TIMINGS = {{
{format_dict(deep_timings)}
}}

# Retry configuration
RETRY_CONFIG = {{
{format_dict(retry_config)}
}}

# ==============================================================================
# GOOGLE DRIVE INTEGRATION
# ==============================================================================

DRIVE_CONFIG = {{
{format_dict(drive_config)}
}}

# ==============================================================================
# PDF CONSOLIDATION
# ==============================================================================

PDF_CONSOLIDATION = {{
{format_dict(pdf_consolidation)}
}}

# ==============================================================================
# GEMINI AI AGENT ORCHESTRATION
# ==============================================================================

GEMINI_AGENT_CONFIG = {{
{format_dict(gemini_config)}
}}

# NOTE: Industry detection via Gemini has been removed
# Industry and subsegments are now configured manually above per client
# This provides more accurate, predictable results

# ==============================================================================
# QUALITY SCORING & VERIFICATION
# ==============================================================================

QUALITY_THRESHOLDS = {{
{format_dict(quality_thresholds)}
}}

ARTIFACT_VERIFICATION = {{
{format_dict(artifact_verification)}
}}

# ==============================================================================
# AUTHENTICATION & LOGGING
# ==============================================================================

AUTH_CHECK_INTERVAL = {settings.get('AUTH_CHECK_INTERVAL', 300)}
AUTH_PROFILE = "{settings.get('AUTH_PROFILE', 'default')}"

LOG_LEVEL = "{settings.get('LOG_LEVEL', 'INFO')}"
LOG_FORMAT = "{settings.get('LOG_FORMAT', '%(asctime)s | %(levelname)s | [%(processName)s] %(message)s')}"
LOG_DATE_FORMAT = "{settings.get('LOG_DATE_FORMAT', '%H:%M:%S')}"

# ==============================================================================
# PROJECT PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
'''

    # Validate generated Python syntax
    try:
        compile(vars_content, '<generated>', 'exec')
    except SyntaxError as e:
        raise ValueError(f"Generated configuration has syntax error: {e}")

    return vars_content
