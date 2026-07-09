"""Shared test fixtures for Account Intelligence test suite."""

import sys
from pathlib import Path

import pytest

# Add project root to sys.path so tests can import core.* and dashboard.*
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def tmp_vars_py(tmp_path):
    """Create a temporary vars.py with valid configuration for test_client."""
    vars_content = '''\
"""Test configuration for Account Intelligence."""

from pathlib import Path

clients = ["test_client"]

test_client_name = "Test Client Corp"
test_client_folder = "https://drive.google.com/drive/folders/1ABC123_test_folder"
test_client_industry = "technology"
test_client_subsegments = "cloud, AI, enterprise software"

persona = "Red Hat solutions architect"
default_mode = "fast"

DASHBOARD_PORT = 8765
DASHBOARD_REFRESH_INTERVAL = 2

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

DEEP_TIMINGS = {
    'notebook_creation_delay': 3.0,
    'source_add_delay': (2.0, 4.0),
    'source_processing_delay': 45.0,
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    'deduplication_delay': 25.0,
    'mindmap_delay': 20.0,
    'source_import_wait': 30.0,
}

RETRY_CONFIG = {
    'max_attempts': 5,
    'base_delay': 10.0,
    'ask_max_attempts': 7,
    'ask_base_delay': 30.0,
}

DRIVE_CONFIG = {
    'enabled': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
    'export_google_docs': True,
    'recursive': False,
    'max_file_size_mb': 50,
}

PDF_CONSOLIDATION = {
    'enabled': True,
    'output_suffix': '-One.pdf',
    'max_file_size_mb': 500,
}

GEMINI_AGENT_CONFIG = {
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
}

QUALITY_THRESHOLDS = {
    'min_sources': 40,
    'required_notes': 6,
    'min_quality_score': 8.5,
    'source_diversity': True,
    'verify_mindmap': True,
}

ARTIFACT_VERIFICATION = {
    'enabled': True,
    'verify_notebook': True,
    'verify_sources': True,
    'verify_notes': True,
    'verify_mindmap': True,
    'export_notes_for_verification': True,
}

AUTH_CHECK_INTERVAL = 300
AUTH_PROFILE = "default"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(processName)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"
'''
    vars_file = tmp_path / "vars.py"
    vars_file.write_text(vars_content)
    return vars_file


@pytest.fixture
def mock_subprocess(mocker):
    """Patch subprocess.run to prevent real process execution."""
    return mocker.patch("subprocess.run")


@pytest.fixture
def flask_test_client():
    """Create a Flask test client from dashboard.server app."""
    from dashboard.server import app

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def tmp_logs_dir(tmp_path):
    """Create a temporary logs directory."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


@pytest.fixture
def tmp_status_dir(tmp_path):
    """Create a temporary status directory."""
    status_dir = tmp_path / ".multi_process_status"
    status_dir.mkdir()
    return status_dir
