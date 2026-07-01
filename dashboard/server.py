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

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
try:
    config_path = SCRIPT_DIR.parent / "vars.py"
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    STATUS_DIR = getattr(config, 'STATUS_DIR', SCRIPT_DIR.parent / ".multi_process_status")
    LOGS_DIR = getattr(config, 'LOGS_DIR', SCRIPT_DIR.parent / "logs")
except Exception:
    # Fallback to default paths if config loading fails
    STATUS_DIR = SCRIPT_DIR.parent / ".multi_process_status"
    LOGS_DIR = SCRIPT_DIR.parent / "logs"

app = Flask(__name__,
            template_folder=str(SCRIPT_DIR / 'templates'),
            static_folder=str(SCRIPT_DIR / 'static'))


@app.route('/')
def dashboard():
    """Serve the dashboard HTML template."""
    return render_template('dashboard.html')


@app.route('/configure')
def configure():
    """Serve the configuration form HTML template."""
    return render_template('configure.html')


@app.route('/status')
def status():
    """Serve aggregated status as JSON."""
    clients = []
    running = 0
    complete = 0
    failed = 0
    mode = "fast"
    run_id = None

    if STATUS_DIR.exists():
        for status_file in STATUS_DIR.glob("*.json"):
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
                print(f"Error reading {status_file}: {e}")

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


@app.route('/logs/<client_token>')
def stream_logs(client_token):
    """Stream logs for a specific client."""
    def generate():
        log_file = LOGS_DIR / f"{client_token}.log"

        if not log_file.exists():
            yield f"data: Log file not found: {log_file}\n\n"
            return

        with open(log_file, 'r') as f:
            # Send existing content
            for line in f:
                yield f"data: {line}\n\n"

            # Stream new content
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/logs/overall')
def stream_overall_logs():
    """Stream combined logs from all components."""
    def generate():
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
            return

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

        # Stream new content from most recent log file
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

                    while True:
                        line = f.readline()
                        if line:
                            yield f"data: {line}\n\n"
                        else:
                            time.sleep(0.5)
            except Exception as e:
                yield f"data: Error streaming {most_recent.name}: {e}\n\n"

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
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/validate-drive-url', methods=['POST'])
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
            'error': str(e)
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
            'error': f'Failed to load configuration: {str(e)}'
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
            'error': f'Failed to save configuration: {str(e)}'
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
            'error': f'Failed to parse CSV: {str(e)}'
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
                'error': str(e)
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
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


@app.route('/api/start-workflow', methods=['POST'])
def start_workflow():
    """
    Trigger workflow execution in background.
    Called by the launch page to start the pipeline.

    Also marks that first-time configuration is complete.
    """
    import subprocess
    import threading
    from pathlib import Path

    try:
        workflow = request.json
        if not workflow or 'command' not in workflow:
            return jsonify({
                'success': False,
                'error': 'Invalid workflow data'
            }), 400

        # CRITICAL: Validate authentication BEFORE starting workflow
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Authentication Required',
                'auth_error': True,
                'instructions': [
                    'You need to authenticate with NotebookLM before launching workflows.',
                    'Please run the following commands in your terminal:',
                    '',
                    '1. Authenticate with NotebookLM:',
                    '   notebooklm login',
                    '',
                    '2. For container mode, update credentials:',
                    '   ./setup-credentials.sh',
                    '',
                    'Then return to this page and try launching again.'
                ]
            }), 401

        # Mark that first configuration is complete
        # This prevents the configuration UI from appearing on next launch
        from datetime import datetime
        first_config_marker = Path.home() / '.ape_first_config_done'
        if not first_config_marker.exists():
            first_config_marker.write_text(json.dumps({
                'first_config_completed': datetime.now().isoformat() + 'Z',
                'via': 'web_ui'
            }, indent=2))

        # Store workflow execution result
        workflow_result = {'success': False, 'error': None, 'pid': None}

        def run_workflow():
            """Background thread to execute workflow launcher"""
            try:
                # Parse command into parts
                cmd = workflow['command'].split()

                print(f"[WORKFLOW] Starting workflow: {' '.join(cmd)}", file=sys.stderr)
                print(f"[WORKFLOW] Working directory: {PROJECT_ROOT}", file=sys.stderr)

                # Validate command exists before executing
                if cmd[0].startswith('./'):
                    script_path = PROJECT_ROOT / cmd[0][2:]
                    if not script_path.exists():
                        error_msg = f"Workflow script not found: {script_path}"
                        print(f"[WORKFLOW] ERROR: {error_msg}", file=sys.stderr)
                        workflow_result['error'] = error_msg
                        return

                # Execute in project root directory as background process
                # Don't use subprocess.run() - it blocks and waits for completion
                # Use Popen() so main.py can spawn its own client processes
                process = subprocess.Popen(
                    cmd,
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                print(f"[WORKFLOW] Workflow process started (PID: {process.pid})", file=sys.stderr)
                print(f"[WORKFLOW] Command: {' '.join(cmd)}", file=sys.stderr)

                workflow_result['success'] = True
                workflow_result['pid'] = process.pid

            except FileNotFoundError as e:
                error_msg = f"Workflow script not found: {e}"
                print(f"[WORKFLOW] {error_msg}", file=sys.stderr)
                workflow_result['error'] = error_msg
                import traceback
                traceback.print_exc()
            except PermissionError as e:
                error_msg = f"Permission denied executing workflow: {e}"
                print(f"[WORKFLOW] {error_msg}", file=sys.stderr)
                workflow_result['error'] = error_msg
                import traceback
                traceback.print_exc()
            except Exception as e:
                error_msg = f"Error running workflow: {e}"
                print(f"[WORKFLOW] {error_msg}", file=sys.stderr)
                workflow_result['error'] = error_msg
                import traceback
                traceback.print_exc()

        # Start workflow in background thread
        thread = threading.Thread(target=run_workflow, daemon=True)
        thread.start()

        # Give thread a moment to start and validate command
        thread.join(timeout=1.0)

        # Check if workflow started successfully
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
            'error': f'Failed to start workflow: {str(e)}'
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
            'error': str(e),
            'authenticated': False
        }), 500


@app.route('/api/notebooklm-login', methods=['POST'])
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
                            # Use shell pipe to auto-confirm overwrite
                            sync_result = subprocess.run(
                                f"echo 'y' | /bin/bash {setup_script}",
                                shell=True,
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
            'message': 'Login flow initiated. A browser window should open for authentication.',
            'instructions': [
                'A browser window should open automatically for Google login.',
                'If no browser opens, run this command in your terminal:',
                '  notebooklm login',
                '',
                'After login completes:',
                '✅ Credentials will automatically sync to container',
                '✅ You can launch workflows immediately',
                '',
                'The authentication status will update automatically once login is complete.'
            ]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
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
        result = subprocess.run(
            ['notebooklm', 'auth', 'logout'],
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
            'error': str(e)
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
                        'error': str(e)
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
            'error': str(e)
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
            'error': str(e)
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
            'ready_for_upload': True  # Always ready to accept credentials
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
            'error': str(e)
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


@app.route('/api/start-oauth-flow', methods=['POST'])
def start_oauth_flow():
    """Trigger OAuth flow and stream progress via SSE."""
    def generate():
        try:
            # Check if Google OAuth packages are available
            if not GOOGLE_AUTH_AVAILABLE:
                yield 'data: {"status": "error", "message": "Google OAuth packages not installed. Activate virtual environment: source ~/.project-ape-venv/bin/activate"}\n\n'
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
                    success_message='✅ Authentication successful! You can close this window and return to Project APE.',
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
            'error': str(e)
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
            'error': str(e)
        }), 500


@app.route('/api/cache-files/<client_id>', methods=['GET'])
def get_cache_files(client_id):
    """List individual cached files for a client."""
    try:
        cache_dir = Path.home() / '.project-ape' / 'drive_cache' / client_id

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
            'error': str(e)
        }), 500


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
            'error': str(e)
        }), 500


def run_server(port=8765, debug=False):
    """Run the Flask server."""
    import signal
    import sys

    print(f"\n📊 Dashboard server starting...")
    print(f"   URL: http://localhost:{port}")
    print(f"   Refresh: Every 2 seconds")
    print(f"   Logs: Real-time streaming")
    print(f"\n   Press Ctrl+C to stop\n")

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n⏰ Dashboard server received shutdown signal")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Bind to 0.0.0.0 for container compatibility (allows external access)
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    # Create directories if needed
    STATUS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    run_server()
