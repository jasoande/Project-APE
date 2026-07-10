#!/usr/bin/env python3
"""
Dashboard Server
================
Flask server with real-time status updates and log streaming
"""

import json
import time
import sys
import re
import csv
import io
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, Response, request
import logging
import importlib.util
# Google OAuth imports - check if available
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AUTH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Google OAuth packages not available: {e}", file=sys.stderr)
    print(f"   Google Drive authentication will not work until you install:", file=sys.stderr)
    print(f"   pip install google-auth-oauthlib google-auth google-api-python-client", file=sys.stderr)
    GOOGLE_AUTH_AVAILABLE = False
    # Define dummy values so dashboard can still start
    Credentials = None
    InstalledAppFlow = None
    build = None

# Enable Flask's logging with better visibility
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)  # Changed from ERROR to WARNING to see issues

# Add handler for stderr
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%H:%M:%S'))
log.addHandler(handler)

SCRIPT_DIR = Path(__file__).parent.resolve()

# Add project root to Python path for imports
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import core modules AFTER fixing path
from core.auth_manager import AuthManager

# Import workflow detector from project root (NOT developer-docs)
try:
    import workflow_detector
    WORKFLOW_DETECTOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: workflow_detector module not available: {e}", file=sys.stderr)
    print(f"   Workflow detection features will not work", file=sys.stderr)
    WORKFLOW_DETECTOR_AVAILABLE = False
    workflow_detector = None

# Load configuration to get proper paths (for container compatibility)
# Default paths relative to project root
DEFAULT_STATUS_DIR = SCRIPT_DIR.parent / ".multi_process_status"
DEFAULT_LOGS_DIR = SCRIPT_DIR.parent / "logs"

try:
    config_path = SCRIPT_DIR.parent / "vars.py"
    if config_path.exists():
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        STATUS_DIR = getattr(config, 'STATUS_DIR', DEFAULT_STATUS_DIR)
        LOGS_DIR = getattr(config, 'LOGS_DIR', DEFAULT_LOGS_DIR)

        # Validate that configured paths are under project root or user's home
        # This prevents issues when vars.py has test-specific paths
        project_root = SCRIPT_DIR.parent
        home = Path.home()

        # If STATUS_DIR is absolute and not under home or project, use default
        if STATUS_DIR.is_absolute():
            if not (str(STATUS_DIR).startswith(str(home)) or str(STATUS_DIR).startswith(str(project_root))):
                print(f"⚠️  Warning: STATUS_DIR '{STATUS_DIR}' is outside project/home, using default", file=sys.stderr)
                STATUS_DIR = DEFAULT_STATUS_DIR

        # Same validation for LOGS_DIR
        if LOGS_DIR.is_absolute():
            if not (str(LOGS_DIR).startswith(str(home)) or str(LOGS_DIR).startswith(str(project_root))):
                print(f"⚠️  Warning: LOGS_DIR '{LOGS_DIR}' is outside project/home, using default", file=sys.stderr)
                LOGS_DIR = DEFAULT_LOGS_DIR
    else:
        # No vars.py file, use defaults
        STATUS_DIR = DEFAULT_STATUS_DIR
        LOGS_DIR = DEFAULT_LOGS_DIR
except Exception as e:
    # Fallback to default paths if config loading fails
    print(f"⚠️  Warning: Failed to load vars.py: {e}, using defaults", file=sys.stderr)
    STATUS_DIR = DEFAULT_STATUS_DIR
    LOGS_DIR = DEFAULT_LOGS_DIR

app = Flask(__name__,
            template_folder=str(SCRIPT_DIR / 'templates'),
            static_folder=str(SCRIPT_DIR / 'static'))

# --- Security: Proxy Support ---
# If running behind a reverse proxy (nginx, Apache, etc.), trust proxy headers
# This allows request.is_secure to work correctly for HTTPS enforcement
if os.environ.get('BEHIND_PROXY', '').lower() == 'true':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    print("✅ Proxy headers enabled (X-Forwarded-Proto, X-Forwarded-Host)", file=sys.stderr)

# --- Security: CSRF Protection ---
def _get_or_create_secret_key() -> str:
    """
    Get persistent Flask secret key from disk, or create one if it doesn't exist.
    Prevents CSRF token invalidation on server restart.
    """
    secret_key_dir = Path.home() / '.project-ape'
    secret_key_file = secret_key_dir / 'flask_secret.key'

    try:
        secret_key_dir.mkdir(mode=0o700, exist_ok=True)

        if secret_key_file.exists():
            secret_key = secret_key_file.read_text().strip()
            if len(secret_key) == 64:  # Valid hex key (32 bytes = 64 hex chars)
                return secret_key
            else:
                print(f"⚠️  Invalid secret key format, regenerating", file=sys.stderr)

        # Generate new secret key
        import secrets
        secret_key = secrets.token_hex(32)
        secret_key_file.write_text(secret_key)
        secret_key_file.chmod(0o600)
        print(f"✅ Generated new Flask secret key: {secret_key_file}", file=sys.stderr)
        return secret_key

    except Exception as e:
        print(f"⚠️  Failed to persist secret key: {e}, using ephemeral key", file=sys.stderr)
        import secrets
        return secrets.token_hex(32)

try:
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    app.config['SECRET_KEY'] = _get_or_create_secret_key()
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    csrf = CSRFProtect(app)
    print("✅ CSRF protection enabled", file=sys.stderr)
except ImportError:
    print("⚠️  flask-wtf not installed, CSRF protection disabled", file=sys.stderr)
    csrf = None
    generate_csrf = None

@app.context_processor
def inject_csrf_token():
    if generate_csrf:
        return {'csrf_token': generate_csrf}
    return {'csrf_token': lambda: ''}

# --- Security: HTTPS and Security Headers ---
@app.before_request
def enforce_https():
    """
    Enforce HTTPS in production environments.
    Only active when FORCE_HTTPS environment variable is set to 'true'.
    """
    force_https = os.environ.get('FORCE_HTTPS', '').lower() == 'true'

    if force_https and not request.is_secure:
        # Redirect HTTP to HTTPS
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.after_request
def set_security_headers(response):
    """
    Add security headers to all responses.

    Headers added:
    - Strict-Transport-Security: Enforce HTTPS for 1 year
    - X-Content-Type-Options: Prevent MIME-type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable browser XSS filter
    - Content-Security-Policy: Restrict resource loading (self-only)
    """
    # Only add HSTS if HTTPS is enforced
    force_https = os.environ.get('FORCE_HTTPS', '').lower() == 'true'
    if force_https:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Always add these headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Content Security Policy - allow self only (prevents XSS)
    # Inline scripts/styles allowed for dashboard functionality
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )

    return response

# --- Security: Path Traversal Protection ---
_SAFE_TOKEN_RE = re.compile(r'^[a-zA-Z0-9_-]+$')

def _validate_client_token(token: str) -> bool:
    return bool(_SAFE_TOKEN_RE.match(token)) and len(token) <= 128

# --- Security: Error Sanitization ---
def _safe_error(e: Exception, context: str = "operation") -> str:
    print(f"[ERROR] {context}: {type(e).__name__}: {e}", file=sys.stderr)
    return f"An error occurred during {context}. Check server logs for details."

# --- Performance: Config Cache ---
_config_cache = {'module': None, 'mtime': 0, 'path': None}

# --- Connection Rate Limiting ---
# Track SSE connection attempts to prevent thread exhaustion from retry storms
_sse_connection_tracker = {}  # {remote_addr: [(timestamp, endpoint), ...]}
_max_connections_per_ip = 10  # Max concurrent SSE connections per IP
_connection_window = 60  # Track connections in last 60 seconds

def _check_sse_rate_limit(remote_addr: str, endpoint: str) -> tuple[bool, str]:
    """
    Check if client can open another SSE connection.
    Returns (allowed, reason)
    """
    import time
    now = time.time()

    # Clean up old entries
    if remote_addr in _sse_connection_tracker:
        _sse_connection_tracker[remote_addr] = [
            (ts, ep) for ts, ep in _sse_connection_tracker[remote_addr]
            if now - ts < _connection_window
        ]

    # Check current connection count
    current_connections = len(_sse_connection_tracker.get(remote_addr, []))
    if current_connections >= _max_connections_per_ip:
        return False, f"Too many concurrent SSE connections ({current_connections}/{_max_connections_per_ip})"

    # Record this connection attempt
    if remote_addr not in _sse_connection_tracker:
        _sse_connection_tracker[remote_addr] = []
    _sse_connection_tracker[remote_addr].append((now, endpoint))

    return True, ""

def _cleanup_sse_connection(remote_addr: str, endpoint: str):
    """Remove connection from tracking when it closes."""
    if remote_addr in _sse_connection_tracker:
        # Remove the most recent matching entry
        entries = _sse_connection_tracker[remote_addr]
        for i in range(len(entries) - 1, -1, -1):
            if entries[i][1] == endpoint:
                entries.pop(i)
                break
        # Clean up empty lists
        if not entries:
            del _sse_connection_tracker[remote_addr]

def get_config(vars_path: Path = None):
    if vars_path is None:
        vars_path = PROJECT_ROOT / "vars.py"
    if not vars_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {vars_path}")
    current_mtime = vars_path.stat().st_mtime
    if (_config_cache['module'] is not None
        and _config_cache['mtime'] == current_mtime
        and _config_cache['path'] == str(vars_path)):
        return _config_cache['module']
    spec = importlib.util.spec_from_file_location("config", vars_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    _config_cache['module'] = config
    _config_cache['mtime'] = current_mtime
    _config_cache['path'] = str(vars_path)
    return config


@app.route('/ping')
def ping():
    """Lightweight health check for fast startup validation (no heavy imports or JSON)."""
    return 'ok', 200, {'Content-Type': 'text/plain'}


@app.route('/health')
def health():
    """Basic health check endpoint for monitoring (lightweight)."""
    try:
        import threading
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return jsonify({
            'status': 'healthy',
            'pid': os.getpid(),
            'threads': threading.active_count(),
            'memory_mb': round(memory_info.rss / 1024 / 1024, 2),
            'status_dir': str(STATUS_DIR),
            'status_dir_exists': STATUS_DIR.exists(),
            'logs_dir': str(LOGS_DIR),
            'logs_dir_exists': LOGS_DIR.exists()
        })
    except ImportError:
        # psutil not available, return basic info
        import threading
        import os
        return jsonify({
            'status': 'healthy',
            'pid': os.getpid(),
            'threads': threading.active_count(),
            'status_dir': str(STATUS_DIR),
            'status_dir_exists': STATUS_DIR.exists()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/health/detailed')
def health_detailed():
    """
    Comprehensive health check endpoint with detailed subsystem status.

    Returns JSON with status for:
    - NotebookLM authentication
    - Google Drive OAuth
    - Disk space
    - Process health
    - Credential expiry warnings
    """
    from datetime import datetime, timedelta
    import shutil
    import subprocess
    import threading

    checks = {}
    overall_healthy = True

    # Check 1: NotebookLM Authentication
    try:
        sys.path.insert(0, str(PROJECT_ROOT / 'core'))
        from auth_manager import AuthManager

        auth_mgr = AuthManager()
        is_authenticated = auth_mgr.is_authenticated()

        checks['notebooklm_auth'] = {
            'status': 'ok' if is_authenticated else 'error',
            'authenticated': is_authenticated,
            'message': 'NotebookLM authenticated' if is_authenticated else 'NotebookLM not authenticated - run: notebooklm login'
        }

        if not is_authenticated:
            overall_healthy = False

    except Exception as e:
        checks['notebooklm_auth'] = {
            'status': 'error',
            'message': f'Failed to check NotebookLM auth: {str(e)}'
        }
        overall_healthy = False

    # Check 2: Drive OAuth Token Validity
    try:
        drive_token_path = Path.home() / '.project-ape' / 'drive_token.json'

        if not drive_token_path.exists():
            checks['drive_auth'] = {
                'status': 'warn',
                'message': 'Drive OAuth token not found - run: python3 setup-oauth-drive.py'
            }
        else:
            import json
            token_data = json.loads(drive_token_path.read_text())

            if 'expiry' in token_data:
                try:
                    # Parse expiry datetime (ISO format)
                    expiry_str = token_data['expiry']
                    # Handle both with and without microseconds
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            expiry = datetime.strptime(expiry_str, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # Couldn't parse, treat as ISO format
                        expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))

                    days_left = (expiry - datetime.now(expiry.tzinfo or None)).days

                    if days_left < 0:
                        checks['drive_auth'] = {
                            'status': 'error',
                            'message': f'Drive OAuth token expired {abs(days_left)} days ago',
                            'days_until_expiry': days_left
                        }
                        overall_healthy = False
                    elif days_left < 7:
                        checks['drive_auth'] = {
                            'status': 'warn',
                            'message': f'Drive OAuth token expires in {days_left} days - refresh recommended',
                            'days_until_expiry': days_left
                        }
                    else:
                        checks['drive_auth'] = {
                            'status': 'ok',
                            'message': f'Drive OAuth token valid ({days_left} days remaining)',
                            'days_until_expiry': days_left
                        }
                except Exception as parse_error:
                    checks['drive_auth'] = {
                        'status': 'warn',
                        'message': f'Drive token exists but expiry check failed: {str(parse_error)}'
                    }
            else:
                checks['drive_auth'] = {
                    'status': 'ok',
                    'message': 'Drive OAuth token exists (no expiry info)'
                }

    except Exception as e:
        checks['drive_auth'] = {
            'status': 'error',
            'message': f'Failed to check Drive auth: {str(e)}'
        }
        overall_healthy = False

    # Check 3: Disk Space
    try:
        total, used, free = shutil.disk_usage(PROJECT_ROOT)
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        percent_used = (used / total) * 100

        if free_gb < 1.0:
            checks['disk_space'] = {
                'status': 'error',
                'message': f'Critical: Only {free_gb:.1f} GB free',
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'percent_used': round(percent_used, 1)
            }
            overall_healthy = False
        elif free_gb < 5.0:
            checks['disk_space'] = {
                'status': 'warn',
                'message': f'Low disk space: {free_gb:.1f} GB free',
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'percent_used': round(percent_used, 1)
            }
        else:
            checks['disk_space'] = {
                'status': 'ok',
                'message': f'{free_gb:.1f} GB free',
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'percent_used': round(percent_used, 1)
            }

    except Exception as e:
        checks['disk_space'] = {
            'status': 'error',
            'message': f'Failed to check disk space: {str(e)}'
        }

    # Check 4: Process Health (zombie processes, thread count)
    try:
        import psutil
        import os

        current_process = psutil.Process(os.getpid())
        thread_count = threading.active_count()

        # Check for zombie child processes
        zombie_count = 0
        for child in current_process.children(recursive=True):
            if child.status() == psutil.STATUS_ZOMBIE:
                zombie_count += 1

        if zombie_count > 0:
            checks['process_health'] = {
                'status': 'warn',
                'message': f'{zombie_count} zombie process(es) detected',
                'thread_count': thread_count,
                'zombie_count': zombie_count
            }
        elif thread_count > 250:
            checks['process_health'] = {
                'status': 'warn',
                'message': f'High thread count: {thread_count}',
                'thread_count': thread_count,
                'zombie_count': 0
            }
        else:
            checks['process_health'] = {
                'status': 'ok',
                'message': f'{thread_count} threads active',
                'thread_count': thread_count,
                'zombie_count': 0
            }

    except ImportError:
        checks['process_health'] = {
            'status': 'ok',
            'message': 'psutil not available, basic check only',
            'thread_count': threading.active_count()
        }
    except Exception as e:
        checks['process_health'] = {
            'status': 'error',
            'message': f'Failed to check process health: {str(e)}'
        }

    # Check 5: NotebookLM CLI Availability
    try:
        result = subprocess.run(
            ['notebooklm', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            checks['notebooklm_cli'] = {
                'status': 'ok',
                'message': 'NotebookLM CLI available',
                'version': result.stdout.strip() if result.stdout else 'unknown'
            }
        else:
            checks['notebooklm_cli'] = {
                'status': 'error',
                'message': 'NotebookLM CLI not working',
                'error': result.stderr.strip() if result.stderr else 'unknown error'
            }
            overall_healthy = False

    except FileNotFoundError:
        checks['notebooklm_cli'] = {
            'status': 'error',
            'message': 'NotebookLM CLI not installed - run: pip install notebooklm-py'
        }
        overall_healthy = False
    except subprocess.TimeoutExpired:
        checks['notebooklm_cli'] = {
            'status': 'warn',
            'message': 'NotebookLM CLI check timed out'
        }
    except Exception as e:
        checks['notebooklm_cli'] = {
            'status': 'error',
            'message': f'Failed to check NotebookLM CLI: {str(e)}'
        }
        overall_healthy = False

    # Determine overall status
    status_priority = {'error': 3, 'warn': 2, 'ok': 1}
    highest_severity = max([status_priority.get(check.get('status', 'ok'), 1) for check in checks.values()])

    if highest_severity == 3:
        overall_status = 'unhealthy'
        status_code = 503
    elif highest_severity == 2:
        overall_status = 'degraded'
        status_code = 200  # Still operational, just warnings
    else:
        overall_status = 'healthy'
        status_code = 200

    return jsonify({
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'checks': checks
    }), status_code


@app.route('/')
def dashboard():
    """Serve the dashboard HTML template."""
    return render_template('dashboard.html')


@app.route('/configure')
def configure():
    """Serve the configuration form HTML template."""
    return render_template('configure.html')


@app.route('/setup-environment')
def setup_environment():
    """Serve the environment setup wizard HTML template."""
    return render_template('setup-environment.html')


@app.route('/api/config-status')
def config_status():
    """Check if vars.py configuration exists and is valid."""
    try:
        vars_path = PROJECT_ROOT / "vars.py"

        if not vars_path.exists():
            return jsonify({
                'configured': False,
                'error': 'Configuration file (vars.py) not found',
                'message': 'Please configure at least one client before starting a workflow.'
            })

        # Try to load and validate configuration
        if WORKFLOW_DETECTOR_AVAILABLE:
            try:
                vars_module = workflow_detector.load_vars_module(vars_path)
                clients = getattr(vars_module, 'clients', [])

                if not clients or len(clients) == 0:
                    return jsonify({
                        'configured': False,
                        'error': 'No clients configured',
                        'message': 'Your vars.py file exists but has no clients defined. Please add at least one client.'
                    })

                return jsonify({
                    'configured': True,
                    'client_count': len(clients),
                    'message': f'{len(clients)} client(s) configured'
                })
            except Exception as e:
                return jsonify({
                    'configured': False,
                    'error': 'Configuration validation failed',
                    'message': str(e)
                })
        else:
            # Workflow detector not available, just check file exists
            return jsonify({
                'configured': True,
                'message': 'Configuration file exists (validation unavailable)'
            })

    except Exception as e:
        return jsonify({
            'configured': False,
            'error': 'Failed to check configuration',
            'message': str(e)
        }), 500


@app.route('/status')
def status():
    """Serve aggregated status as JSON."""
    try:
        clients = []
        running = 0
        complete = 0
        failed = 0
        mode = "fast"
        run_id = None

        if not STATUS_DIR.exists():
            print(f"⚠️  STATUS_DIR does not exist: {STATUS_DIR}", file=sys.stderr)
            return jsonify({
                'total': 0,
                'running': 0,
                'complete': 0,
                'failed': 0,
                'mode': mode,
                'run_id': run_id,
                'clients': [],
                'error': f'Status directory not found: {STATUS_DIR}'
            })

        status_files = list(STATUS_DIR.glob("*.json"))
        if not status_files:
            print(f"⚠️  No status files found in {STATUS_DIR}", file=sys.stderr)

        for status_file in status_files:
            try:
                with open(status_file, 'r') as f:
                    client_data = json.load(f)
                    clients.append(client_data)

                    # Detect mode from first client
                    if 'mode' in client_data:
                        mode = client_data.get('mode', 'fast')

                    # Get run_id from first client
                    if run_id is None and 'run_id' in client_data:
                        run_id = client_data.get('run_id')

                    status = client_data.get('status', 'UNKNOWN').upper()
                    if status in ['RUNNING', 'PENDING']:
                        running += 1
                    elif status == 'COMPLETE':
                        complete += 1
                    elif status in ['FAILED', 'DEGRADED']:
                        failed += 1
            except Exception as e:
                print(f"❌ Error reading {status_file}: {e}", file=sys.stderr)

        # Sort by client name
        clients.sort(key=lambda x: x.get('name', ''))

        return jsonify({
            'total': len(clients),
            'running': running,
            'complete': complete,
            'failed': failed,
            'mode': mode,
            'run_id': run_id,  # Include run_id in response
            'clients': clients
        })

    except Exception as e:
        print(f"❌ FATAL: /status endpoint crashed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'error': _safe_error(e, "operation"),
            'total': 0,
            'running': 0,
            'complete': 0,
            'failed': 0,
            'mode': 'fast',
            'run_id': None,
            'clients': []
        }), 500


@app.route('/logs/<client_token>')
def stream_logs(client_token):
    """
    Stream logs for a specific client via Server-Sent Events (SSE).

    CRITICAL: This endpoint holds a thread open for the duration of the stream.
    In deep mode with multiple clients, this can exhaust Flask's thread pool.
    Waitress server is configured with threads=200 to handle this load.
    """
    if not _validate_client_token(client_token):
        return jsonify({'error': 'Invalid client token'}), 400

    # Rate limiting: prevent connection storms
    remote_addr = request.remote_addr or 'unknown'
    allowed, reason = _check_sse_rate_limit(remote_addr, f'/logs/{client_token}')
    if not allowed:
        print(f"🚫 SSE rate limit exceeded for {remote_addr}: {reason}", file=sys.stderr)
        return jsonify({'error': reason}), 429

    import threading
    connection_id = f"{client_token}_{time.time()}"

    print(f"📡 SSE connection opened: {connection_id} (active threads: {threading.active_count()})", file=sys.stderr)

    def generate():
        try:
            log_file = LOGS_DIR / f"{client_token}.log"
            if not log_file.resolve().is_relative_to(LOGS_DIR.resolve()):
                yield f"data: Invalid path\n\n"
                return

            if not log_file.exists():
                yield f"data: Log file not found: {log_file}\n\n"
                return

            # CRITICAL: Increase timeout for deep mode (15-25s delays between prompts)
            # Deep mode can have 25s idle periods, so 60s timeout is needed
            max_idle_time = 60  # 60 seconds max with no new content (handles deep mode delays)
            idle_iterations = 0
            max_iterations = max_idle_time * 2  # 0.5s sleep per iteration

            try:
                with open(log_file, 'r') as f:
                    # Send existing content
                    for line in f:
                        yield f"data: {line}\n\n"

                    # Stream new content with timeout
                    while idle_iterations < max_iterations:
                        line = f.readline()
                        if line:
                            yield f"data: {line}\n\n"
                            idle_iterations = 0  # Reset on new content
                        else:
                            # Send periodic heartbeat to keep connection alive
                            # This prevents proxy/firewall timeouts in long-running workflows
                            if idle_iterations % 20 == 0:  # Every 10 seconds
                                yield f": heartbeat\n\n"
                            time.sleep(0.5)
                            idle_iterations += 1

                    # Timeout reached
                    yield f"data: [Stream timeout - refresh to reconnect]\n\n"
            except (BrokenPipeError, ConnectionResetError, GeneratorExit):
                # Client disconnected - clean exit
                print(f"🔌 SSE connection closed (client disconnect): {connection_id}", file=sys.stderr)
            except Exception as e:
                # Log other errors but don't crash
                print(f"❌ Error streaming logs for {client_token}: {e}", file=sys.stderr)
        finally:
            _cleanup_sse_connection(remote_addr, f'/logs/{client_token}')
            print(f"🔚 SSE connection cleanup: {connection_id} (active threads: {threading.active_count()})", file=sys.stderr)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/logs/overall')
def stream_overall_logs():
    """Stream combined logs from all components."""
    # Rate limiting: prevent connection storms
    remote_addr = request.remote_addr or 'unknown'
    allowed, reason = _check_sse_rate_limit(remote_addr, '/logs/overall')
    if not allowed:
        print(f"🚫 SSE rate limit exceeded for {remote_addr}: {reason}", file=sys.stderr)
        return jsonify({'error': reason}), 429

    import threading
    connection_id = f"overall_{time.time()}"

    print(f"📡 SSE connection opened (overall): {connection_id} (active threads: {threading.active_count()})", file=sys.stderr)

    def generate():
        try:
            # Find all log files
            log_files = []

            if not LOGS_DIR.exists():
                yield f"data: Logs directory not found: {LOGS_DIR}\n\n"
                return

            # Collect all log files
            for log_file in sorted(LOGS_DIR.glob("*.log")):
                log_files.append(log_file)

            if not log_files:
                yield f"data: No log files found in {LOGS_DIR}\n\n"
                yield f"data: \n\n"
                yield f"data: Log files will appear here when workflows run.\n\n"
                # CRITICAL FIX: Send periodic heartbeats even when no logs exist
                # This prevents "connection failed" errors and thread leaks
                # Wait up to 60 seconds for logs to appear, then close connection
                max_wait = 60  # 60 seconds
                for i in range(max_wait * 2):  # Check every 0.5s
                    time.sleep(0.5)
                    # Check if logs appeared
                    if list(LOGS_DIR.glob("*.log")):
                        # Logs appeared, close this connection so client reconnects
                        yield f"data: ✅ Logs detected - please refresh\n\n"
                        return
                    # Send heartbeat every 10 seconds to keep connection alive
                    if i % 20 == 0:
                        yield f": heartbeat\n\n"
                yield f"data: [No logs after 60s - refresh to reconnect]\n\n"
                return

            # CRITICAL: Increase timeout for deep mode workflows
            # Deep mode can run 45-60 minutes, so we need a longer timeout
            # But not too long - we want to free up threads when clients disconnect
            max_idle_time = 600  # 10 minutes max with no new content (handles deep mode)
            idle_iterations = 0
            max_iterations = max_idle_time * 2
            # Send existing content from all files
            for log_file in log_files:
                try:
                    yield f"data: ═══════════════════════════════════════════════════════════════\n\n"
                    yield f"data: 📄 {log_file.name}\n\n"
                    yield f"data: ═══════════════════════════════════════════════════════════════\n\n"
                    with open(log_file, 'r') as f:
                        for line in f:
                            yield f"data: {line}\n\n"
                    yield f"data: \n\n"
                except Exception as e:
                    yield f"data: Error reading {log_file.name}: {e}\n\n"

            # Stream new content from most recent log file with timeout
            if log_files:
                most_recent = max(log_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(most_recent, 'r') as f:
                        f.seek(0, 2)  # Go to end
                        yield f"data: \n\n"
                        yield f"data: ──────────────────────────────────────────────────────────────\n\n"
                        yield f"data: 🔄 Streaming live updates from {most_recent.name}...\n\n"
                        yield f"data: ──────────────────────────────────────────────────────────────\n\n"
                        yield f"data: \n\n"

                        while idle_iterations < max_iterations:
                            line = f.readline()
                            if line:
                                yield f"data: {line}\n\n"
                                idle_iterations = 0
                            else:
                                time.sleep(0.5)
                                idle_iterations += 1

                        yield f"data: [Stream timeout - refresh to reconnect]\n\n"
                except Exception as e:
                    yield f"data: Error streaming {most_recent.name}: {e}\n\n"
        except (BrokenPipeError, ConnectionResetError, GeneratorExit):
            # Client disconnected - clean exit
            print(f"🔌 SSE connection closed (client disconnect): {connection_id}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error in overall log stream: {e}", file=sys.stderr)
        finally:
            _cleanup_sse_connection(remote_addr, '/logs/overall')
            print(f"🔚 SSE connection cleanup (overall): {connection_id} (active threads: {threading.active_count()})", file=sys.stderr)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/available-logs')
def available_logs():
    """Return list of available log files."""
    logs = []

    # Add overall option
    logs.append({
        'type': 'overall',
        'token': 'overall',
        'label': '📊 Overall Logs (All Components)',
        'path': str(LOGS_DIR)
    })

    # Add client logs from status files
    if STATUS_DIR.exists():
        for status_file in STATUS_DIR.glob("*.json"):
            try:
                with open(status_file, 'r') as f:
                    client_data = json.load(f)
                    client_name = client_data.get('name', 'Unknown')
                    client_token = client_data.get('token', status_file.stem)
                    log_file = LOGS_DIR / f"{client_token}.log"

                    if log_file.exists():
                        logs.append({
                            'type': 'client',
                            'token': client_token,
                            'label': f"👤 {client_name}",
                            'path': str(log_file),
                            'size': log_file.stat().st_size
                        })
            except Exception:
                pass

    # Add any standalone log files not in status
    if LOGS_DIR.exists():
        for log_file in LOGS_DIR.glob("*.log"):
            token = log_file.stem
            # Skip if already added
            if not any(l['token'] == token for l in logs):
                logs.append({
                    'type': 'standalone',
                    'token': token,
                    'label': f"📄 {log_file.stem}",
                    'path': str(log_file),
                    'size': log_file.stat().st_size
                })

    return jsonify({
        'success': True,
        'logs': logs,
        'total_count': len(logs)
    })


@app.route('/api/generate-config', methods=['POST'])
def generate_config():
    """Generate vars.py configuration from client data."""
    try:
        # Import config_generator from same directory
        import config_generator

        data = request.json
        if not data or 'clients' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request: missing clients data'
            }), 400

        clients = data['clients']
        settings = data.get('settings', {})

        # Generate configuration with or without custom settings
        try:
            if settings:
                # Use full generator with custom settings
                config_content = config_generator.generate_vars_py_full(clients, settings)
            else:
                # Use basic generator with defaults
                config_content = config_generator.generate_vars_py(clients)
            return jsonify({
                'success': True,
                'content': config_content,
                'filename': 'vars.py'
            })
        except ValueError as e:
            # Validation errors
            error_msg = str(e)
            # Extract individual errors from the message
            if 'Validation errors:' in error_msg:
                errors = [line.strip().lstrip('- ') for line in error_msg.split('\n')[1:] if line.strip()]
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "config generation")
        }), 500


@app.route('/api/validate-drive-url', methods=['POST'])
@csrf.exempt if csrf else lambda f: f  # Read-only validation, no state modification
def validate_drive_url():
    """Validate Drive URL format using regex (no API call)."""
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({
                'valid': False,
                'error': 'Missing URL parameter'
            }), 400

        url = data['url']

        # Reject empty/whitespace-only URLs
        if not url or not url.strip():
            return jsonify({
                'valid': False,
                'error': 'URL cannot be empty'
            })

        # Same regex as drive_manager.py
        folder_id_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)

        if folder_id_match:
            return jsonify({
                'valid': True,
                'folder_id': folder_id_match.group(1)
            })
        elif url.startswith('drive://'):
            # Extract folder ID from drive:// protocol
            folder_id = url[8:]
            return jsonify({
                'valid': True,
                'folder_id': folder_id
            })
        else:
            # Check if it's a local path (doesn't contain drive.google.com)
            if 'drive.google.com' not in url:
                # Assume local path is valid
                return jsonify({
                    'valid': True,
                    'folder_id': None
                })
            else:
                return jsonify({
                    'valid': False,
                    'error': 'Invalid Drive URL format. Expected: https://drive.google.com/drive/folders/FOLDER_ID'
                })

    except Exception as e:
        return jsonify({
            'valid': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/load-config', methods=['GET'])
def load_config():
    """Load current vars.py configuration."""
    try:
        import config_parser
        from datetime import datetime

        vars_path = SCRIPT_DIR.parent / 'vars.py'

        if not vars_path.exists():
            return jsonify({
                'success': False,
                'error': 'Configuration file not found. Please create vars.py first.'
            }), 404

        # Parse existing configuration
        config_data = config_parser.parse_vars_file(vars_path)

        # Add metadata
        config_data['metadata'] = {
            'file_path': str(vars_path),
            'last_modified': datetime.fromtimestamp(vars_path.stat().st_mtime).isoformat(),
            'size_bytes': vars_path.stat().st_size
        }

        return jsonify({
            'success': True,
            'config': config_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "loading configuration")
        }), 500


@app.route('/api/save-config', methods=['POST'])
def save_config():
    """
    Save configuration directly to vars.py file.

    Also marks that first-time configuration is complete (when called from configure page).
    """
    try:
        import config_generator
        import shutil
        from datetime import datetime
        from pathlib import Path

        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400

        clients = data.get('clients', [])
        settings = data.get('settings', {})

        # Save vars.py to project root where main.py expects it
        vars_path = SCRIPT_DIR.parent / 'vars.py'

        # Debug logging
        print(f"[SAVE-CONFIG] SCRIPT_DIR: {SCRIPT_DIR}", file=sys.stderr)
        print(f"[SAVE-CONFIG] SCRIPT_DIR.parent: {SCRIPT_DIR.parent}", file=sys.stderr)
        print(f"[SAVE-CONFIG] vars_path: {vars_path}", file=sys.stderr)
        print(f"[SAVE-CONFIG] vars_path.exists(): {vars_path.exists()}", file=sys.stderr)

        # Create backup before overwriting
        backup_path = None
        if vars_path.exists():
            backup_path = SCRIPT_DIR.parent / f'vars.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            print(f"[SAVE-CONFIG] backup_path: {backup_path}", file=sys.stderr)
            shutil.copy2(vars_path, backup_path)

        # Generate configuration with custom settings if provided
        if settings:
            # Use full generator with settings
            config_content = config_generator.generate_vars_py_full(clients, settings)
        else:
            # Use basic generator
            config_content = config_generator.generate_vars_py(clients)

        # Write to file
        with open(vars_path, 'w') as f:
            f.write(config_content)

        # Validate syntax
        try:
            compile(config_content, str(vars_path), 'exec')
        except SyntaxError as e:
            # Restore backup if syntax invalid
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, vars_path)
            return jsonify({
                'success': False,
                'error': f'Generated configuration has syntax error: {e}'
            }), 500

        # Mark that first configuration is complete
        # This prevents the configuration UI from appearing on next launch
        first_config_marker = Path.home() / '.ape_first_config_done'
        if not first_config_marker.exists():
            first_config_marker.write_text(json.dumps({
                'first_config_completed': datetime.now().isoformat() + 'Z',
                'via': 'web_ui'
            }, indent=2))

        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully',
            'backup_created': str(backup_path) if backup_path else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "saving configuration")
        }), 500


@app.route('/api/import-csv', methods=['POST'])
def import_csv():
    """Parse CSV file and return client data."""
    try:
        import config_generator

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Read CSV content
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))

        clients = []
        errors = []
        line_num = 2  # Start at 2 (1 is header)

        for row in csv_reader:
            # Expected columns: name, folder, industry, subsegments
            try:
                name = row.get('name', '').strip()
                folder = row.get('folder', '').strip()
                industry = row.get('industry', '').strip()
                subsegments = row.get('subsegments', '').strip()

                if not name:
                    errors.append(f"Line {line_num}: Missing name")
                    line_num += 1
                    continue

                if not folder:
                    errors.append(f"Line {line_num}: Missing folder")
                    line_num += 1
                    continue

                # Generate client ID
                client_id = config_generator.sanitize_client_id(name)

                client = {
                    'id': client_id,
                    'name': name,
                    'folder': folder,
                    'industry': industry,
                    'subsegments': subsegments
                }

                # Validate client data
                valid, error = config_generator.validate_client_data(client)
                if not valid:
                    errors.append(f"Line {line_num}: {error}")
                else:
                    clients.append(client)

                line_num += 1

            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
                line_num += 1

        return jsonify({
            'success': True,
            'clients': clients,
            'errors': errors,
            'total_rows': line_num - 2,
            'imported': len(clients),
            'failed': len(errors)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "CSV parsing")
        }), 500


@app.route('/api/preview-config', methods=['POST'])
def preview_config():
    """Generate vars.py preview without saving to disk."""
    try:
        import config_generator

        data = request.json
        if not data or 'clients' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request: missing clients data'
            }), 400

        clients = data['clients']
        settings = data.get('settings', {})

        # Generate configuration preview
        try:
            if settings:
                config_content = config_generator.generate_vars_py_full(clients, settings)
            else:
                config_content = config_generator.generate_vars_py(clients)

            return jsonify({
                'success': True,
                'content': config_content,
                'line_count': len(config_content.split('\n')),
                'char_count': len(config_content)
            })

        except ValueError as e:
            return jsonify({
                'success': False,
                'error': _safe_error(e, "operation")
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "config generation")
        }), 500


@app.route('/launch')
def launch_page():
    """
    Launch confirmation page - shows workflow details and triggers execution.
    This is the transition from configuration to workflow execution.
    """
    try:
        # Check if workflow detector is available
        if not WORKFLOW_DETECTOR_AVAILABLE:
            return render_template('error.html',
                                 error="Workflow detector not available",
                                 message="The workflow_detector module could not be loaded. Check server logs."), 500

        # Check if vars.py exists
        vars_path = PROJECT_ROOT / "vars.py"
        if not vars_path.exists():
            return render_template('error.html',
                                 error="Configuration file (vars.py) not found",
                                 message="Please complete the configuration first."), 404

        # Load and detect workflow
        vars_module = workflow_detector.load_vars_module(vars_path)
        workflow = workflow_detector.detect_workflow(vars_module)

        # Render launch page with workflow details
        return render_template('launch.html', workflow=workflow)

    except Exception as e:
        return render_template('error.html',
                             error="Failed to detect workflow",
                             message=str(e)), 500


_VALID_MODES = {'fast', 'deep', 'update'}
_VALID_CLIENT_ID_RE = re.compile(r'^[a-zA-Z0-9_]+$')
_VALID_FLAGS = {'--refresh', '--skip-preflight', '--resume', '--no-dashboard'}


def _build_workflow_command(workflow: dict) -> list:
    """Build a validated subprocess argument list from structured workflow params.

    Accepts only known fields; rejects arbitrary strings.
    Returns a list suitable for subprocess.Popen (no shell).

    Raises ValueError on invalid input.
    """
    mode = workflow.get('mode', 'fast')
    if mode not in _VALID_MODES:
        raise ValueError(f"Invalid mode: {mode!r}. Must be one of {_VALID_MODES}")

    clients = workflow.get('clients', [])
    if not isinstance(clients, list):
        raise ValueError("clients must be a list")
    for cid in clients:
        if not isinstance(cid, str) or not _VALID_CLIENT_ID_RE.match(cid):
            raise ValueError(f"Invalid client ID: {cid!r}")
        if len(cid) > 128:
            raise ValueError(f"Client ID too long: {cid!r}")

    flags = workflow.get('flags', [])
    if not isinstance(flags, list):
        raise ValueError("flags must be a list")
    for flag in flags:
        if flag not in _VALID_FLAGS:
            raise ValueError(f"Invalid flag: {flag!r}. Allowed: {_VALID_FLAGS}")

    cmd = [sys.executable, str(PROJECT_ROOT / 'main.py'), '--mode', mode]
    if clients:
        cmd.append('--clients')
        cmd.extend(clients)
    cmd.extend(flags)
    return cmd


@app.route('/api/start-workflow', methods=['POST'])
def start_workflow():
    """
    Trigger workflow execution in background.
    Called by the launch page to start the pipeline.

    Accepts structured JSON with validated fields — never raw command strings.
    """
    import subprocess
    import threading
    from pathlib import Path

    try:
        workflow = request.json
        if not workflow:
            return jsonify({'success': False, 'error': 'Invalid workflow data'}), 400

        if 'command' in workflow and 'mode' not in workflow:
            return jsonify({
                'success': False,
                'error': 'Raw command strings are not accepted. '
                         'Send mode, clients, and flags instead.'
            }), 400

        try:
            cmd = _build_workflow_command(workflow)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400

        # Mark that first configuration is complete
        from datetime import datetime
        first_config_marker = Path.home() / '.ape_first_config_done'
        if not first_config_marker.exists():
            first_config_marker.write_text(json.dumps({
                'first_config_completed': datetime.now().isoformat() + 'Z',
                'via': 'web_ui'
            }, indent=2))

        workflow_result = {'success': False, 'error': None, 'pid': None}

        def run_workflow():
            try:
                print(f"[WORKFLOW] Starting workflow: {' '.join(cmd)}", file=sys.stderr)
                print(f"[WORKFLOW] Working directory: {PROJECT_ROOT}", file=sys.stderr)

                main_py = PROJECT_ROOT / 'main.py'
                if not main_py.exists():
                    workflow_result['error'] = f"main.py not found at {main_py}"
                    return

                venv_bin = Path.home() / '.project-ape-venv' / 'bin'
                env = os.environ.copy()
                if venv_bin.exists():
                    env['PATH'] = f"{venv_bin}:{env.get('PATH', '')}"

                process = subprocess.Popen(
                    cmd,
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )

                print(f"[WORKFLOW] Workflow process started (PID: {process.pid})", file=sys.stderr)
                workflow_result['success'] = True
                workflow_result['pid'] = process.pid

            except FileNotFoundError as e:
                workflow_result['error'] = f"Workflow script not found: {e}"
                print(f"[WORKFLOW] {workflow_result['error']}", file=sys.stderr)
            except PermissionError as e:
                workflow_result['error'] = f"Permission denied: {e}"
                print(f"[WORKFLOW] {workflow_result['error']}", file=sys.stderr)
            except Exception as e:
                workflow_result['error'] = f"Error running workflow: {e}"
                print(f"[WORKFLOW] {workflow_result['error']}", file=sys.stderr)

        thread = threading.Thread(target=run_workflow, daemon=True)
        thread.start()
        thread.join(timeout=1.0)

        if workflow_result['error']:
            return jsonify({
                'success': False,
                'error': workflow_result['error']
            }), 500

        return jsonify({
            'success': True,
            'message': 'Workflow started in background',
            'pid': workflow_result.get('pid'),
            'dashboard_url': workflow.get('dashboard_url', 'http://localhost:8765')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "workflow start")
        }), 500


@app.route('/api/run-setup', methods=['GET', 'POST'])
def run_setup():
    """
    Execute setup-environment.sh script with real-time output streaming.
    Returns progress updates via Server-Sent Events (SSE).
    """
    import subprocess
    import select
    import fcntl
    import os

    def generate_setup_output():
        """Generator that streams setup script output in real-time."""
        setup_script = PROJECT_ROOT / 'setup-environment.sh'

        # Verify script exists
        if not setup_script.exists():
            yield f"data: {{\"type\": \"error\", \"message\": \"Setup script not found at {setup_script}\"}}\n\n"
            return

        # Make script executable
        try:
            os.chmod(setup_script, 0o755)
        except Exception as e:
            yield f"data: {{\"type\": \"error\", \"message\": \"Failed to make script executable: {str(e)}\"}}\n\n"
            return

        yield f"data: {{\"type\": \"info\", \"message\": \"Starting environment setup...\"}}\n\n"

        try:
            # Execute script with non-interactive input (auto-confirm with 'y')
            # Use 'yes' command to automatically answer prompts
            process = subprocess.Popen(
                ['/bin/bash', '-c', f'yes | {setup_script}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=PROJECT_ROOT,
                universal_newlines=True
            )

            # Stream output line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Clean up ANSI color codes for web display
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line.rstrip())

                    # Detect message type based on content
                    msg_type = 'output'
                    if '✅' in line or 'SUCCESS' in line.upper() or 'COMPLETE' in line.upper():
                        msg_type = 'success'
                    elif '❌' in line or 'ERROR' in line.upper() or 'FAILED' in line.upper():
                        msg_type = 'error'
                    elif '⚠️' in line or 'WARNING' in line.upper():
                        msg_type = 'warning'

                    # Send as SSE event
                    yield f"data: {{\"type\": \"{msg_type}\", \"message\": {json.dumps(clean_line)}}}\n\n"

            # Wait for completion
            return_code = process.wait(timeout=300)  # 5 minute timeout

            if return_code == 0:
                yield f"data: {{\"type\": \"success\", \"message\": \"✅ Environment setup completed successfully!\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"success\": true}}\n\n"
            else:
                yield f"data: {{\"type\": \"error\", \"message\": \"❌ Setup failed with exit code {return_code}\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"success\": false}}\n\n"

        except subprocess.TimeoutExpired:
            process.kill()
            yield f"data: {{\"type\": \"error\", \"message\": \"❌ Setup timed out after 5 minutes\"}}\n\n"
            yield f"data: {{\"type\": \"complete\", \"success\": false}}\n\n"
        except Exception as e:
            yield f"data: {{\"type\": \"error\", \"message\": \"❌ Setup failed: {str(e)}\"}}\n\n"
            yield f"data: {{\"type\": \"complete\", \"success\": false}}\n\n"

    return Response(generate_setup_output(), mimetype='text/event-stream')


@app.route('/api/check-auth-status', methods=['GET'])
def check_auth_status():
    """
    Check NotebookLM authentication status.
    Returns authentication state without exposing credentials.
    """
    try:
        auth_manager = AuthManager()
        is_authenticated = auth_manager.is_authenticated()

        return jsonify({
            'success': True,
            'authenticated': is_authenticated,
            'profile': 'default',
            'checked_at': time.time()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation"),
            'authenticated': False
        }), 500


@app.route('/api/notebooklm-login', methods=['POST'])
@csrf.exempt if csrf else lambda f: f  # Login trigger doesn't modify state server-side
def notebooklm_login():
    """
    Trigger NotebookLM login flow.
    Attempts to run 'notebooklm login' command which opens browser for OAuth.
    """
    import subprocess
    import threading

    try:
        def run_login():
            """Background thread to execute login command"""
            try:
                # Run notebooklm login in background
                # This will open a browser window for OAuth

                # Use full path to notebooklm in virtual environment
                # The venv may not be activated in the Flask server's environment
                venv_notebooklm = Path.home() / '.project-ape-venv' / 'bin' / 'notebooklm'

                if venv_notebooklm.exists():
                    notebooklm_cmd = str(venv_notebooklm)
                else:
                    # Fallback to PATH (if venv is activated)
                    notebooklm_cmd = 'notebooklm'

                result = subprocess.run(
                    [notebooklm_cmd, 'login'],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    print(f"[AUTH] NotebookLM login completed successfully", file=sys.stderr)

                    # STEP 1: Setup Google Cloud Application Default Credentials
                    print(f"[AUTH] Setting up Google Cloud ADC...", file=sys.stderr)

                    # Detect Linux headless environment for xvfb
                    import platform
                    is_linux = platform.system() == 'Linux'
                    has_display = os.environ.get('DISPLAY') is not None

                    # On Linux without DISPLAY, use xvfb-run for gcloud browser auth
                    if is_linux and not has_display:
                        adc_cmd = ['xvfb-run', '-a', 'gcloud', 'auth', 'application-default', 'login']
                    else:
                        adc_cmd = ['gcloud', 'auth', 'application-default', 'login']

                    adc_result = subprocess.run(
                        adc_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                    if adc_result.returncode == 0:
                        print(f"[AUTH] ✅ Application Default Credentials configured", file=sys.stderr)
                    else:
                        print(f"[AUTH] ⚠️  ADC setup failed: {adc_result.stderr}", file=sys.stderr)

                    # STEP 2: Set quota project
                    project_result = subprocess.run(
                        ['gcloud', 'config', 'get-value', 'project'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    project_name = project_result.stdout.strip()

                    if project_name and project_name != '(unset)':
                        print(f"[AUTH] Setting quota project: {project_name}...", file=sys.stderr)
                        subprocess.run(
                            ['gcloud', 'auth', 'application-default', 'set-quota-project', project_name],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        print(f"[AUTH] ✅ Quota project set: {project_name}", file=sys.stderr)
                    else:
                        print(f"[AUTH] ⚠️  No GCP project set. Run: gcloud config set project YOUR_PROJECT", file=sys.stderr)

                    # STEP 3: Sync credentials to container volume
                    # After successful login, run setup-credentials.sh to update the
                    # project-ape-credentials volume so container workflows can access them
                    setup_script = PROJECT_ROOT / 'setup-credentials.sh'
                    if setup_script.exists():
                        print(f"[AUTH] Syncing credentials to container volume...", file=sys.stderr)
                        try:
                            sync_result = subprocess.run(
                                ['/bin/bash', str(setup_script)],
                                input='y\n',
                                cwd=str(PROJECT_ROOT),
                                capture_output=True,
                                text=True,
                                timeout=60
                            )

                            if sync_result.returncode == 0:
                                print(f"[AUTH] ✅ Credentials synced to container successfully", file=sys.stderr)
                            else:
                                print(f"[AUTH] ⚠️ Credential sync failed: {sync_result.stderr}", file=sys.stderr)
                                print(f"[AUTH] You may need to run manually: ./setup-credentials.sh", file=sys.stderr)
                        except Exception as e:
                            print(f"[AUTH] ⚠️ Error syncing credentials: {e}", file=sys.stderr)
                            print(f"[AUTH] You may need to run manually: ./setup-credentials.sh", file=sys.stderr)
                    else:
                        print(f"[AUTH] ⚠️ setup-credentials.sh not found, skipping container sync", file=sys.stderr)
                else:
                    print(f"[AUTH] NotebookLM login failed: {result.stderr}", file=sys.stderr)

            except subprocess.TimeoutExpired:
                print(f"[AUTH] NotebookLM login timed out", file=sys.stderr)
            except Exception as e:
                print(f"[AUTH] Error running notebooklm login: {e}", file=sys.stderr)

        # Start login in background thread
        thread = threading.Thread(target=run_login, daemon=True)
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Login process started in background. Check your browser for the authentication window.',
            'instructions': [
                '🔍 Look for a browser window that just opened asking you to sign in with Google.',
                '',
                'If no browser window appeared:',
                '  1. Check if popup blockers are preventing the window',
                '  2. Or run this command in your terminal instead:',
                '     notebooklm login',
                '',
                'After you complete the Google login:',
                '✅ Credentials will automatically sync',
                '✅ This page will update to show "Authenticated"',
                '✅ You can then launch workflows',
                '',
                '⏱️  Checking authentication status every 5 seconds...'
            ]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation"),
            'fallback_instructions': [
                'Automatic login failed. Please run this command manually in your terminal:',
                '  notebooklm login',
                '',
                'For a fresh login, run:',
                '  notebooklm auth logout',
                '  notebooklm login'
            ]
        }), 500


@app.route('/api/notebooklm-logout', methods=['POST'])
def notebooklm_logout():
    """
    Trigger NotebookLM logout.
    Clears saved authentication credentials.
    """
    import subprocess

    try:
        # Use full path to notebooklm in virtual environment
        venv_notebooklm = Path.home() / '.project-ape-venv' / 'bin' / 'notebooklm'

        if venv_notebooklm.exists():
            notebooklm_cmd = str(venv_notebooklm)
        else:
            # Fallback to PATH (if venv is activated)
            notebooklm_cmd = 'notebooklm'

        result = subprocess.run(
            [notebooklm_cmd, 'auth', 'logout'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Successfully logged out of NotebookLM'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Logout failed: {result.stderr}'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/refresh-sources', methods=['POST'])
def refresh_sources():
    """
    Refresh cached Google Drive sources without running full workflow.

    Request JSON:
    {
        "clients": ["merck", "blue_yonder"] // Optional: specific clients, or omit for all
    }

    Returns Server-Sent Events stream with progress updates.
    """
    import importlib.util
    from pathlib import Path

    def generate_refresh_progress():
        """Generator that streams refresh progress via SSE."""
        try:
            # Load vars.py configuration
            vars_path = PROJECT_ROOT / "vars.py"
            if not vars_path.exists():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Configuration file (vars.py) not found'})}\n\n"
                return

            spec = importlib.util.spec_from_file_location("config", vars_path)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)

            # Get list of clients to refresh
            request_data = request.get_json() or {}
            selected_clients = request_data.get('clients', [])

            # If no clients specified, refresh all configured clients
            all_clients = getattr(config, 'clients', [])
            if not selected_clients:
                selected_clients = all_clients

            # Validate selected clients exist in config
            invalid_clients = [c for c in selected_clients if c not in all_clients]
            if invalid_clients:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Invalid clients: {', '.join(invalid_clients)}'})}\n\n"
                return

            total_clients = len(selected_clients)
            if total_clients == 0:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No clients configured to refresh'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'info', 'message': f'Starting refresh for {total_clients} client(s)...'})}\n\n"

            # Import DriveManager
            from core.drive_manager import DriveManager

            drive_config = getattr(config, 'DRIVE_CONFIG', {})

            # Track results
            total_files_updated = 0
            errors = []

            # Refresh each client
            for idx, client_id in enumerate(selected_clients, 1):
                try:
                    client_name = getattr(config, f"{client_id}_name", client_id)
                    folder_url = getattr(config, f"{client_id}_folder", None)

                    if not folder_url:
                        error_msg = f"No Drive folder configured for {client_name}"
                        errors.append(error_msg)
                        yield f"data: {json.dumps({'type': 'warning', 'message': f'⚠️  {error_msg}'})}\n\n"
                        continue

                    # Check if folder is a Drive URL (skip local folders)
                    if not ('drive.google.com' in folder_url or folder_url.startswith('drive://')):
                        yield f"data: {json.dumps({'type': 'info', 'message': f'⏭️  Skipping {client_name} (local folder)'})}\n\n"
                        continue

                    yield f"data: {json.dumps({'type': 'progress', 'current': idx, 'total': total_clients, 'client': client_name})}\n\n"
                    yield f"data: {json.dumps({'type': 'info', 'message': f'🔄 Refreshing {client_name} ({idx}/{total_clients})...'})}\n\n"

                    # Use DriveManager with force_refresh=True to bypass cache
                    with DriveManager(
                        client_id=client_id,
                        folder_spec=folder_url,
                        cache_enabled=True,
                        force_refresh=True,  # Force download even if cache exists
                        config=drive_config
                    ) as folder_path:
                        # Count files in refreshed cache
                        file_count = len([f for f in Path(folder_path).iterdir() if f.is_file() and f.name != 'metadata.json'])
                        total_files_updated += file_count

                        yield f"data: {json.dumps({'type': 'success', 'message': f'✅ {client_name}: {file_count} files refreshed'})}\n\n"

                except Exception as e:
                    error_msg = f"{client_name}: {str(e)}"
                    errors.append(error_msg)
                    yield f"data: {json.dumps({'type': 'error', 'message': f'❌ {error_msg}'})}\n\n"

            # Send completion summary
            success_count = total_clients - len(errors)
            summary = {
                'type': 'complete',
                'success': len(errors) == 0,
                'total_clients': total_clients,
                'successful': success_count,
                'failed': len(errors),
                'total_files': total_files_updated,
                'errors': errors
            }

            yield f"data: {json.dumps(summary)}\n\n"

            if len(errors) == 0:
                yield f"data: {json.dumps({'type': 'success', 'message': f'✅ Refresh complete! Updated {total_files_updated} files across {total_clients} client(s)'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'warning', 'message': f'⚠️  Refresh completed with {len(errors)} error(s)'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Refresh failed: {str(e)}'})}\n\n"

    return Response(generate_refresh_progress(), mimetype='text/event-stream')


@app.route('/api/cache-stats', methods=['GET'])
def cache_stats():
    """
    Get cache statistics for all clients.

    Returns JSON with cache info: size, file count, last refresh time.
    """
    try:
        import importlib.util
        from datetime import datetime

        # Load vars.py configuration
        vars_path = PROJECT_ROOT / "vars.py"
        if not vars_path.exists():
            return jsonify({
                'success': False,
                'error': 'Configuration file not found'
            }), 404

        spec = importlib.util.spec_from_file_location("config", vars_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        all_clients = getattr(config, 'clients', [])
        cache_root = Path.home() / '.project-ape' / 'drive_cache'

        stats = []
        total_size = 0
        total_files = 0

        for client_id in all_clients:
            client_name = getattr(config, f"{client_id}_name", client_id)
            folder_url = getattr(config, f"{client_id}_folder", None)

            if not folder_url:
                continue

            # Check if Drive folder (not local)
            if not ('drive.google.com' in folder_url or folder_url.startswith('drive://')):
                stats.append({
                    'client_id': client_id,
                    'client_name': client_name,
                    'type': 'local',
                    'cached': False
                })
                continue

            # Extract folder ID
            match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder_url)
            if match:
                folder_id = match.group(1)
            elif folder_url.startswith('drive://'):
                folder_id = folder_url[8:]
            else:
                continue

            cache_dir = cache_root / folder_id
            metadata_file = cache_dir / 'metadata.json'

            if cache_dir.exists() and metadata_file.exists():
                try:
                    # Read metadata
                    with open(metadata_file) as f:
                        metadata = json.load(f)

                    # Calculate cache size
                    cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                    file_count = metadata.get('file_count', 0)
                    cached_at = metadata.get('cached_at')

                    # Calculate age
                    age_str = 'Unknown'
                    if cached_at:
                        cached_time = datetime.fromisoformat(cached_at)
                        age_delta = datetime.now() - cached_time

                        if age_delta.days > 0:
                            age_str = f"{age_delta.days}d ago"
                        elif age_delta.seconds > 3600:
                            age_str = f"{age_delta.seconds // 3600}h ago"
                        else:
                            age_str = f"{age_delta.seconds // 60}m ago"

                    total_size += cache_size
                    total_files += file_count

                    stats.append({
                        'client_id': client_id,
                        'client_name': client_name,
                        'type': 'drive',
                        'cached': True,
                        'size_bytes': cache_size,
                        'size_mb': round(cache_size / (1024 * 1024), 2),
                        'file_count': file_count,
                        'last_refresh': cached_at,
                        'age': age_str
                    })
                except Exception as e:
                    stats.append({
                        'client_id': client_id,
                        'client_name': client_name,
                        'type': 'drive',
                        'cached': False,
                        'error': _safe_error(e, "operation")
                    })
            else:
                stats.append({
                    'client_id': client_id,
                    'client_name': client_name,
                    'type': 'drive',
                    'cached': False
                })

        return jsonify({
            'success': True,
            'stats': stats,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_files': total_files,
            'cache_path': str(cache_root)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """
    Clear cached Google Drive files.

    Request JSON:
    {
        "clients": ["merck", "blue_yonder"] // Optional: specific clients, or omit for all
    }
    """
    try:
        import importlib.util
        import shutil

        # Load vars.py configuration
        vars_path = PROJECT_ROOT / "vars.py"
        if not vars_path.exists():
            return jsonify({
                'success': False,
                'error': 'Configuration file not found'
            }), 404

        spec = importlib.util.spec_from_file_location("config", vars_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        request_data = request.get_json() or {}
        selected_clients = request_data.get('clients', [])

        all_clients = getattr(config, 'clients', [])
        if not selected_clients:
            selected_clients = all_clients

        cache_root = Path.home() / '.project-ape' / 'drive_cache'
        cleared_count = 0
        cleared_size = 0

        for client_id in selected_clients:
            folder_url = getattr(config, f"{client_id}_folder", None)
            if not folder_url:
                continue

            # Extract folder ID
            match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder_url)
            if match:
                folder_id = match.group(1)
            elif folder_url.startswith('drive://'):
                folder_id = folder_url[8:]
            else:
                continue

            cache_dir = cache_root / folder_id

            if cache_dir.exists():
                # Calculate size before deletion
                size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
                cleared_size += size

                # Delete cache directory
                shutil.rmtree(cache_dir)
                cleared_count += 1

        return jsonify({
            'success': True,
            'message': f'Cleared cache for {cleared_count} client(s)',
            'cleared_count': cleared_count,
            'cleared_size_mb': round(cleared_size / (1024 * 1024), 2)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/oauth-status', methods=['GET'])
def oauth_status():
    """Check if OAuth credentials and token exist."""
    try:
        # Ensure .project-ape directory exists
        creds_dir = Path.home() / '.project-ape'
        creds_dir.mkdir(parents=True, exist_ok=True)

        creds_file = creds_dir / 'drive_credentials.json'
        token_file = creds_dir / 'drive_token.json'

        response = {
            'success': True,
            'credentials_exist': creds_file.exists(),
            'token_exist': token_file.exists(),
            'authenticated': False,
            'email': None,
            'scopes': [],
            'ready_for_upload': True,  # Always ready to accept credentials
            'google_packages_available': GOOGLE_AUTH_AVAILABLE
        }

        # If token exists, check if it's valid
        if token_file.exists():
            try:
                if not GOOGLE_AUTH_AVAILABLE:
                    response['authenticated'] = False
                    response['error'] = 'Google OAuth packages not installed'
                else:
                    creds = Credentials.from_authorized_user_file(str(token_file))
                    response['authenticated'] = creds.valid or (creds.expired and creds.refresh_token)
                    if hasattr(creds, 'token') and creds.token:
                        response['email'] = 'Authenticated'
                    if hasattr(creds, 'scopes'):
                        response['scopes'] = creds.scopes
            except Exception as e:
                print(f"Error checking token validity: {e}", file=sys.stderr)
                response['token_error'] = str(e)

        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/upload-oauth-credentials', methods=['POST'])
def upload_oauth_credentials():
    """Accept uploaded client_secret JSON file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Parse and validate JSON
        file_content = file.read()
        credentials_data = json.loads(file_content)

        # Validate structure (must have installed.client_id, etc.)
        if 'installed' not in credentials_data:
            return jsonify({'success': False, 'error': 'Invalid OAuth credentials format. Expected "installed" key.'}), 400

        if 'client_id' not in credentials_data['installed']:
            return jsonify({'success': False, 'error': 'Invalid OAuth credentials format. Missing client_id.'}), 400

        # Save to ~/.project-ape/drive_credentials.json
        creds_dir = Path.home() / '.project-ape'
        creds_dir.mkdir(parents=True, exist_ok=True)
        creds_file = creds_dir / 'drive_credentials.json'

        with open(creds_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)

        os.chmod(creds_file, 0o600)  # Secure permissions

        client_id_preview = credentials_data['installed']['client_id'][:20] + '...'

        return jsonify({
            'success': True,
            'message': 'Credentials uploaded successfully',
            'client_id': client_id_preview
        })
    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Invalid JSON file'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/start-oauth-flow', methods=['GET', 'POST'])
def start_oauth_flow():
    """Trigger OAuth flow and stream progress via SSE."""
    def generate():
        try:
            # Check if Google OAuth packages are available
            if not GOOGLE_AUTH_AVAILABLE:
                yield 'data: {"status": "error", "message": "Google OAuth packages not available. Please restart the dashboard using: python3 launch-project-ape.py (This ensures the virtual environment is used)"}\n\n'
                return

            yield 'data: {"status": "starting", "message": "Initializing OAuth flow..."}\n\n'

            # Ensure directory exists
            creds_dir = Path.home() / '.project-ape'
            creds_dir.mkdir(parents=True, exist_ok=True)

            creds_file = creds_dir / 'drive_credentials.json'
            token_file = creds_dir / 'drive_token.json'

            if not creds_file.exists():
                yield 'data: {"status": "error", "message": "OAuth credentials not uploaded. Please go to Step 3 and upload your credentials.json file first."}\n\n'
                return

            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

            yield 'data: {"status": "loading", "message": "Loading OAuth configuration..."}\n\n'

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_file), SCOPES
                )
            except Exception as e:
                yield f'data: {{"status": "error", "message": "Invalid credentials file: {str(e)}. Please re-upload your OAuth credentials."}}\n\n'
                return

            yield 'data: {"status": "browser_opening", "message": "Opening browser for authentication... (Check for popup blockers)"}\n\n'

            # Run OAuth flow (opens browser automatically)
            try:
                creds = flow.run_local_server(
                    port=0,
                    success_message='✅ Authentication successful! You can close this window and return to Account Intelligence.',
                    open_browser=True
                )
            except Exception as e:
                error_detail = str(e)
                if "Connection refused" in error_detail or "Address already in use" in error_detail:
                    yield 'data: {"status": "error", "message": "Port conflict detected. Please close any applications using ports 8080-8090 and try again."}\n\n'
                else:
                    yield f'data: {{"status": "error", "message": "Browser authentication failed: {error_detail}"}}\n\n'
                return

            yield 'data: {"status": "token_saving", "message": "Saving authentication token..."}\n\n'

            # Save token
            try:
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
                os.chmod(token_file, 0o600)  # Secure permissions
            except Exception as e:
                yield f'data: {{"status": "error", "message": "Failed to save token: {str(e)}"}}\n\n'
                return

            yield 'data: {"status": "complete", "message": "✅ Authentication complete! Google Drive access granted.", "email": "Authenticated"}\n\n'

        except Exception as e:
            error_msg = str(e)
            print(f"[OAuth Flow Error] {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            yield f'data: {{"status": "error", "message": "OAuth flow failed: {error_msg}. Check console for details."}}\n\n'

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/test-drive-access', methods=['GET'])
def test_drive_access():
    """Verify Drive API access by listing sample files."""
    try:
        token_file = Path.home() / '.project-ape' / 'drive_token.json'

        if not token_file.exists():
            return jsonify({
                'success': False,
                'error': 'Authentication token not found. Please complete OAuth flow first.'
            }), 404

        creds = Credentials.from_authorized_user_file(str(token_file))

        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            # Save refreshed token
            with open(token_file, 'w') as f:
                f.write(creds.to_json())
            # Secure file permissions (owner read/write only)
            os.chmod(token_file, 0o600)

        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=10,
            fields="files(id, name, mimeType)"
        ).execute()

        files = results.get('files', [])

        return jsonify({
            'success': True,
            'authenticated': True,
            'total_accessible': len(files),
            'sample_files': [{'name': f['name'], 'type': f.get('mimeType', 'unknown')} for f in files[:5]]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Return system resource status."""
    try:
        import shutil

        disk = shutil.disk_usage('/')

        return jsonify({
            'success': True,
            'venv_active': sys.prefix != sys.base_prefix,
            'venv_path': sys.prefix if sys.prefix != sys.base_prefix else None,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_percent': round((disk.used / disk.total) * 100, 1),
            'python_version': sys.version.split()[0],
            'container_mode': os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/cache-files/<client_id>', methods=['GET'])
def get_cache_files(client_id):
    """List individual cached files for a client."""
    if not _validate_client_token(client_id):
        return jsonify({'success': False, 'error': 'Invalid client ID'}), 400
    try:
        cache_root = Path.home() / '.project-ape' / 'drive_cache'
        cache_dir = (cache_root / client_id).resolve()
        if not cache_dir.is_relative_to(cache_root.resolve()):
            return jsonify({'success': False, 'error': 'Invalid client ID'}), 400

        if not cache_dir.exists():
            return jsonify({'files': []})

        files = []
        for file_path in cache_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'metadata.json':
                files.append({
                    'name': file_path.name,
                    'size_bytes': file_path.stat().st_size,
                    'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                    'cached_at': file_path.stat().st_mtime,
                    'path': str(file_path.relative_to(cache_dir))
                })

        # Sort by name
        files.sort(key=lambda x: x['name'])

        return jsonify({
            'success': True,
            'files': files,
            'total_count': len(files)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


@app.route('/api/preflight-check', methods=['GET'])
def preflight_check():
    """Run pre-flight health checks before workflow launch."""
    try:
        from core.health_checks import run_preflight_checks
        results = run_preflight_checks(PROJECT_ROOT / "vars.py")
        return jsonify(results)
    except Exception as e:
        return jsonify({
            'all_passed': False,
            'checks': [],
            'summary': _safe_error(e, "preflight checks")
        }), 500


@app.route('/api/stop-workflow', methods=['POST'])
def stop_workflow():
    """Stop the running workflow and all child processes."""
    import signal as sig_module

    pid_file = STATUS_DIR / '.workflow_pid'
    if not pid_file.exists():
        return jsonify({'success': False, 'error': 'No workflow is running'}), 404

    try:
        with open(pid_file) as f:
            data = json.load(f)
        pid = data['pid']

        try:
            os.killpg(os.getpgid(pid), sig_module.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass

        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break
        else:
            try:
                os.killpg(os.getpgid(pid), sig_module.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

        if STATUS_DIR.exists():
            for sf in STATUS_DIR.glob("*.json"):
                if sf.name.startswith('.'):
                    continue
                try:
                    with open(sf, 'r') as f:
                        status = json.load(f)
                    if status.get('status', '').upper() in ('RUNNING', 'PENDING'):
                        status['status'] = 'CANCELLED'
                        status['step'] = 'Cancelled by user'
                        with open(sf, 'w') as f:
                            json.dump(status, f, indent=2)
                except Exception:
                    pass

        pid_file.unlink(missing_ok=True)

        return jsonify({'success': True, 'message': 'Workflow cancelled'})

    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "stop workflow")}), 500


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server and container."""
    try:
        print("\n⏰ Shutdown requested via API")

        # Schedule shutdown after short delay
        def delayed_shutdown():
            import time
            time.sleep(2)  # Give response time to send
            import os
            os._exit(0)  # Force exit the entire process

        import threading
        threading.Thread(target=delayed_shutdown, daemon=True).start()

        return jsonify({
            'success': True,
            'message': 'Server shutting down...'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': _safe_error(e, "operation")
        }), 500


# ============================================================================
# ENVIRONMENT SETUP API ENDPOINTS
# ============================================================================

@app.route('/api/setup/system-info', methods=['GET'])
def setup_system_info():
    """Get system information (OS, architecture, platform)."""
    try:
        import platform
        import os

        system = platform.system()

        # Map to user-friendly OS names
        os_map = {
            'Darwin': 'macOS',
            'Linux': 'Linux',
            'Windows': 'Windows'
        }

        os_name = os_map.get(system, system)

        # Detect specific Linux distros
        if os_name == 'Linux':
            if Path('/etc/redhat-release').exists():
                os_name = 'RHEL/Fedora'
            elif Path('/etc/debian_version').exists():
                os_name = 'Debian/Ubuntu'

        return jsonify({
            'os': os_name,
            'arch': platform.machine(),
            'platform': platform.platform(),
            'python_version': platform.python_version()
        })
    except Exception as e:
        return jsonify({'error': _safe_error(e, "system detection")}), 500


@app.route('/api/setup/check-homebrew', methods=['GET'])
def setup_check_homebrew():
    """Check if Homebrew is installed (macOS only)."""
    try:
        import subprocess

        result = subprocess.run(['which', 'brew'], capture_output=True, text=True)

        if result.returncode == 0:
            # Get version
            version_result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip().split('\n')[0] if version_result.returncode == 0 else 'Unknown'

            return jsonify({
                'installed': True,
                'version': version,
                'path': result.stdout.strip()
            })
        else:
            return jsonify({'installed': False})
    except Exception as e:
        return jsonify({'error': _safe_error(e, "Homebrew check")}), 500


@app.route('/api/setup/install-homebrew', methods=['POST'])
def setup_install_homebrew():
    """Install Homebrew (macOS only)."""
    try:
        import subprocess

        curl_result = subprocess.run(
            ['curl', '-fsSL', 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh'],
            capture_output=True, text=True, timeout=60
        )
        if curl_result.returncode != 0:
            return jsonify({'success': False, 'error': 'Failed to download Homebrew installer'}), 500

        result = subprocess.run(
            ['/bin/bash'],
            input=curl_result.stdout,
            capture_output=True, text=True, timeout=600
        )

        if result.returncode == 0 or 'already installed' in result.stdout.lower():
            # Verify installation
            check_result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
            version = check_result.stdout.strip().split('\n')[0] if check_result.returncode == 0 else 'Unknown'

            path_result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
            path = path_result.stdout.strip()

            return jsonify({
                'success': True,
                'version': version,
                'path': path
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Installation failed'
            }), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Installation timed out (>10 minutes)'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "Homebrew installation")}), 500


@app.route('/api/setup/check-podman', methods=['GET'])
def setup_check_podman():
    """Check if Podman is installed."""
    try:
        import subprocess

        result = subprocess.run(['which', 'podman'], capture_output=True, text=True)

        if result.returncode == 0:
            version_result = subprocess.run(['podman', '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip() if version_result.returncode == 0 else 'Unknown'

            # Check Podman machine status on macOS
            machine_running = False
            try:
                machine_result = subprocess.run(['podman', 'machine', 'list', '--format', '{{.Running}}'],
                                              capture_output=True, text=True, timeout=10)
                if machine_result.returncode == 0:
                    machine_running = 'true' in machine_result.stdout.lower()
            except:
                pass

            return jsonify({
                'installed': True,
                'version': version,
                'machine_running': machine_running
            })
        else:
            return jsonify({'installed': False})
    except Exception as e:
        return jsonify({'error': _safe_error(e, "Podman check")}), 500


@app.route('/api/setup/install-podman', methods=['POST'])
def setup_install_podman():
    """Install Podman."""
    try:
        import subprocess
        import platform

        system = platform.system()

        if system == 'Darwin':  # macOS
            result = subprocess.run(['brew', 'install', 'podman'], capture_output=True, text=True, timeout=300)
        elif system == 'Linux':
            # Detect distro
            if Path('/etc/redhat-release').exists():
                result = subprocess.run(['sudo', 'dnf', 'install', '-y', 'podman'],
                                      capture_output=True, text=True, timeout=300)
            elif Path('/etc/debian_version').exists():
                subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, timeout=120)
                result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'podman'],
                                      capture_output=True, text=True, timeout=300)
            else:
                return jsonify({'success': False, 'error': 'Unsupported Linux distribution'}), 400
        else:
            return jsonify({'success': False, 'error': 'Unsupported operating system'}), 400

        if result.returncode == 0 or 'already installed' in result.stdout.lower():
            # Verify installation
            version_result = subprocess.run(['podman', '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip()

            # Initialize Podman machine on macOS
            if system == 'Darwin':
                subprocess.run(['podman', 'machine', 'init'], capture_output=True, timeout=60)
                subprocess.run(['podman', 'machine', 'start'], capture_output=True, timeout=120)

            return jsonify({
                'success': True,
                'version': version
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Installation timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "Podman installation")}), 500


@app.route('/api/setup/check-gcloud', methods=['GET'])
def setup_check_gcloud():
    """Check if Google Cloud SDK is installed."""
    try:
        import subprocess

        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)

        if result.returncode == 0:
            version_result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip().split('\n')[0] if version_result.returncode == 0 else 'Unknown'

            # Check authentication
            auth_result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE',
                                        '--format=value(account)'],
                                       capture_output=True, text=True)
            authenticated = bool(auth_result.stdout.strip())
            account = auth_result.stdout.strip().split('\n')[0] if authenticated else None

            return jsonify({
                'installed': True,
                'version': version,
                'authenticated': authenticated,
                'account': account
            })
        else:
            return jsonify({'installed': False})
    except Exception as e:
        return jsonify({'error': _safe_error(e, "Google Cloud SDK check")}), 500


@app.route('/api/setup/install-gcloud', methods=['POST'])
def setup_install_gcloud():
    """Install Google Cloud SDK."""
    try:
        import subprocess
        import platform

        system = platform.system()

        if system == 'Darwin':  # macOS
            result = subprocess.run(['brew', 'install', '--cask', 'google-cloud-sdk'],
                                  capture_output=True, text=True, timeout=300)
        elif system == 'Linux':
            if Path('/etc/redhat-release').exists():
                # RHEL/Fedora
                arch = platform.machine()
                if arch == 'x86_64':
                    # Use official repo
                    repo_config = """[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
"""
                    with open('/tmp/google-cloud-sdk.repo', 'w') as f:
                        f.write(repo_config)
                    subprocess.run(['sudo', 'mv', '/tmp/google-cloud-sdk.repo', '/etc/yum.repos.d/'], timeout=10)
                    result = subprocess.run(['sudo', 'dnf', 'install', '-y', 'google-cloud-cli'],
                                          capture_output=True, text=True, timeout=300)
                else:
                    return jsonify({'success': False, 'error': f'Architecture {arch} not supported for auto-install'}), 400
            elif Path('/etc/debian_version').exists():
                # Debian/Ubuntu
                subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, timeout=60)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'apt-transport-https', 'ca-certificates', 'gnupg', 'curl'],
                              capture_output=True, timeout=60)
                gpg_key = subprocess.run(
                    ['curl', '-fsSL', 'https://packages.cloud.google.com/apt/doc/apt-key.gpg'],
                    capture_output=True, timeout=60
                )
                if gpg_key.returncode == 0:
                    subprocess.run(
                        ['sudo', 'gpg', '--dearmor', '-o', '/usr/share/keyrings/cloud.google.gpg'],
                        input=gpg_key.stdout, capture_output=True, timeout=30
                    )

                repo_line = 'deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main\n'
                subprocess.run(
                    ['sudo', 'tee', '-a', '/etc/apt/sources.list.d/google-cloud-sdk.list'],
                    input=repo_line.encode(), capture_output=True, timeout=10
                )
                subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, timeout=60)
                result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'google-cloud-cli'],
                                      capture_output=True, text=True, timeout=300)
            else:
                return jsonify({'success': False, 'error': 'Unsupported Linux distribution'}), 400
        else:
            return jsonify({'success': False, 'error': 'Unsupported operating system'}), 400

        if result.returncode == 0 or 'already installed' in result.stdout.lower():
            version_result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip().split('\n')[0]

            return jsonify({
                'success': True,
                'version': version
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Installation timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "Google Cloud SDK installation")}), 500


@app.route('/api/setup/check-python', methods=['GET'])
def setup_check_python():
    """Check if Python 3.10+ is installed."""
    try:
        import subprocess
        import platform

        # Try to find Python 3
        python_cmds = ['python3', '/opt/homebrew/bin/python3', '/usr/local/bin/python3']
        python_cmd = None

        for cmd in python_cmds:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    python_cmd = cmd
                    break
            except:
                continue

        if python_cmd:
            version_str = subprocess.run([python_cmd, '--version'], capture_output=True, text=True).stdout.strip()
            version = version_str.split()[1]  # "Python 3.14.0" -> "3.14.0"

            # Check if version is 3.10+
            parts = version.split('.')
            major = int(parts[0])
            minor = int(parts[1])
            compatible = (major == 3 and minor >= 10) or major > 3

            path_result = subprocess.run(['which', python_cmd], capture_output=True, text=True)

            return jsonify({
                'installed': True,
                'compatible': compatible,
                'version': version,
                'path': path_result.stdout.strip()
            })
        else:
            return jsonify({
                'installed': False,
                'compatible': False
            })
    except Exception as e:
        return jsonify({'error': _safe_error(e, "Python check")}), 500


@app.route('/api/setup/install-python', methods=['POST'])
def setup_install_python():
    """Install Python 3.14."""
    try:
        import subprocess
        import platform

        system = platform.system()

        if system == 'Darwin':  # macOS
            result = subprocess.run(['brew', 'install', 'python@3.14'],
                                  capture_output=True, text=True, timeout=300)
        elif system == 'Linux':
            if Path('/etc/redhat-release').exists():
                result = subprocess.run(['sudo', 'dnf', 'install', '-y', 'python3.14', 'python3.14-pip'],
                                      capture_output=True, text=True, timeout=300)
            elif Path('/etc/debian_version').exists():
                subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, timeout=60)
                result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3.14', 'python3.14-pip', 'python3.14-venv'],
                                      capture_output=True, text=True, timeout=300)
            else:
                return jsonify({'success': False, 'error': 'Unsupported Linux distribution'}), 400
        else:
            return jsonify({'success': False, 'error': 'Unsupported operating system'}), 400

        if result.returncode == 0 or 'already installed' in result.stdout.lower():
            # Find the installed Python
            python_cmd = 'python3'
            if system == 'Darwin':
                python_cmd = '/opt/homebrew/bin/python3'

            version_result = subprocess.run([python_cmd, '--version'], capture_output=True, text=True)
            version = version_result.stdout.strip().split()[1]

            path_result = subprocess.run(['which', python_cmd], capture_output=True, text=True)

            return jsonify({
                'success': True,
                'version': version,
                'path': path_result.stdout.strip()
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Installation timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "Python installation")}), 500


@app.route('/api/setup/check-venv', methods=['GET'])
def setup_check_venv():
    """Check if virtual environment exists."""
    try:
        import subprocess

        venv_path = Path.home() / '.project-ape-venv'

        if venv_path.exists() and (venv_path / 'bin' / 'python3').exists():
            # Get Python version in venv
            version_result = subprocess.run([str(venv_path / 'bin' / 'python3'), '--version'],
                                          capture_output=True, text=True)
            version = version_result.stdout.strip().split()[1] if version_result.returncode == 0 else 'Unknown'

            # Check if version is 3.10+
            parts = version.split('.')
            major = int(parts[0])
            minor = int(parts[1])
            compatible = (major == 3 and minor >= 10) or major > 3

            return jsonify({
                'exists': True,
                'compatible': compatible,
                'version': version,
                'path': str(venv_path)
            })
        else:
            return jsonify({'exists': False})
    except Exception as e:
        return jsonify({'error': _safe_error(e, "Virtual environment check")}), 500


@app.route('/api/setup/create-venv', methods=['POST'])
def setup_create_venv():
    """Create Python virtual environment."""
    try:
        import subprocess
        import platform

        venv_path = Path.home() / '.project-ape-venv'

        # Remove old venv if exists
        if venv_path.exists():
            import shutil
            shutil.rmtree(venv_path)

        # Find Python 3 command
        system = platform.system()
        python_cmd = 'python3'
        if system == 'Darwin':
            if Path('/opt/homebrew/bin/python3').exists():
                python_cmd = '/opt/homebrew/bin/python3'

        # Create venv
        result = subprocess.run([python_cmd, '-m', 'venv', str(venv_path)],
                              capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            # Verify creation
            version_result = subprocess.run([str(venv_path / 'bin' / 'python3'), '--version'],
                                          capture_output=True, text=True)
            version = version_result.stdout.strip().split()[1]

            # Upgrade pip in venv
            subprocess.run([str(venv_path / 'bin' / 'python3'), '-m', 'pip', 'install', '--upgrade', 'pip'],
                         capture_output=True, timeout=60)

            return jsonify({
                'success': True,
                'version': version,
                'path': str(venv_path)
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Creation timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "Virtual environment creation")}), 500


@app.route('/api/setup/check-notebooklm', methods=['GET'])
def setup_check_notebooklm():
    """Check if NotebookLM CLI and dependencies are installed."""
    try:
        import subprocess

        venv_path = Path.home() / '.project-ape-venv'
        notebooklm_bin = venv_path / 'bin' / 'notebooklm'

        if notebooklm_bin.exists():
            # Get NotebookLM version
            version_result = subprocess.run([str(notebooklm_bin), '--version'],
                                          capture_output=True, text=True)
            version = version_result.stdout.strip() if version_result.returncode == 0 else 'Unknown'

            # Check Flask
            flask_result = subprocess.run([str(venv_path / 'bin' / 'python3'), '-c',
                                         'import flask; print(flask.__version__)'],
                                        capture_output=True, text=True)
            flask_version = flask_result.stdout.strip() if flask_result.returncode == 0 else 'Not installed'

            return jsonify({
                'installed': True,
                'version': version,
                'flask_version': flask_version
            })
        else:
            return jsonify({'installed': False})
    except Exception as e:
        return jsonify({'error': _safe_error(e, "NotebookLM CLI check")}), 500


@app.route('/api/setup/install-notebooklm', methods=['POST'])
def setup_install_notebooklm():
    """Install NotebookLM CLI and all dependencies."""
    try:
        import subprocess

        venv_path = Path.home() / '.project-ape-venv'
        pip_cmd = str(venv_path / 'bin' / 'pip')

        # Install NotebookLM with browser support
        subprocess.run([pip_cmd, 'install', 'notebooklm-py[browser]'],
                     capture_output=True, text=True, timeout=300)

        # Install Google API libraries
        subprocess.run([pip_cmd, 'install', 'google-auth', 'google-auth-oauthlib',
                       'google-auth-httplib2', 'google-api-python-client'],
                     capture_output=True, text=True, timeout=180)

        # Install Flask and dependencies
        subprocess.run([pip_cmd, 'install', 'flask>=3.0.0', 'werkzeug>=3.0.0',
                       'waitress>=3.0.0', 'python-dotenv>=1.0.0', 'pypdf>=4.0.0',
                       'Pillow>=10.0.0', 'reportlab>=4.0.0', 'flask-wtf'],
                     capture_output=True, text=True, timeout=240)

        # Install Playwright browsers
        playwright_cmd = str(venv_path / 'bin' / 'playwright')
        result = subprocess.run([playwright_cmd, 'install', 'chromium'],
                              capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            # Verify installations
            notebooklm_version = subprocess.run([str(venv_path / 'bin' / 'notebooklm'), '--version'],
                                              capture_output=True, text=True).stdout.strip()

            flask_version = subprocess.run([str(venv_path / 'bin' / 'python3'), '-c',
                                          'import flask; print(flask.__version__)'],
                                         capture_output=True, text=True).stdout.strip()

            return jsonify({
                'success': True,
                'version': notebooklm_version,
                'flask_version': flask_version
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Installation timed out'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': _safe_error(e, "NotebookLM CLI installation")}), 500


# --- CSRF Exemptions ---
# SSE streaming endpoints accessed via EventSource (GET) are naturally exempt.
# No POST endpoints are exempted — all JS callers include X-CSRFToken via
# the fetch interceptor or explicit XHR header.


def run_server(port=8765, debug=False):
    """Run the Flask server."""
    import signal
    import sys
    import threading

    print(f"\n📊 Dashboard server starting...")
    print(f"   URL: http://localhost:{port}")
    print(f"   Refresh: Every 2 seconds")
    print(f"   Logs: Real-time streaming")
    print(f"   STATUS_DIR: {STATUS_DIR}")
    print(f"   LOGS_DIR: {LOGS_DIR}")
    print(f"   Initial threads: {threading.active_count()}")
    print(f"\n   Press Ctrl+C to stop\n")

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n⏰ Dashboard server received shutdown signal (active threads: {threading.active_count()})")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # CRITICAL: Use waitress instead of Flask's dev server for better thread handling
    # Flask dev server has limited threads and struggles with multiple SSE connections
    # waitress supports many concurrent connections and is production-ready
    try:
        from waitress import serve
        print(f"   Using Waitress WSGI server (production-grade)")
        print(f"   Max threads: 200 (increased for SSE log streams)")

        # Configure Waitress for high concurrency
        # threads=200: Handle up to 200 concurrent connections (SSE streams + polling)
        #   - In deep mode with 5 clients, each client can have multiple SSE streams
        #   - Plus browser polling, plus retries = need higher limit
        # channel_timeout=300: Keep SSE connections alive for 5 minutes
        # cleanup_interval=30: Clean up stale connections every 30 seconds
        bind_host = os.environ.get('DASHBOARD_HOST', '127.0.0.1')
        serve(app,
              host=bind_host,
              port=port,
              threads=200,
              channel_timeout=300,
              cleanup_interval=30,
              _quiet=False)
    except ImportError:
        # Fallback to Flask dev server if waitress not installed
        print(f"   ⚠️  Waitress not installed - using Flask dev server (limited concurrency)")
        print(f"   For production use: pip install waitress")
        try:
            from werkzeug.serving import WSGIRequestHandler
            WSGIRequestHandler.protocol_version = "HTTP/1.1"  # Enable keep-alive
        except:
            pass
        bind_host = os.environ.get('DASHBOARD_HOST', '127.0.0.1')
        app.run(host=bind_host, port=port, debug=debug, threaded=True, processes=1)


if __name__ == "__main__":
    # Create directories if needed (including parent directories)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    run_server()
