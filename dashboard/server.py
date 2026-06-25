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
from pathlib import Path
from flask import Flask, render_template, jsonify, Response, request
import logging
import importlib.util
from core.auth_manager import AuthManager

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

SCRIPT_DIR = Path(__file__).parent.resolve()

# Add project root to Python path for imports
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
        # Import workflow detector
        sys.path.insert(0, str(PROJECT_ROOT))
        import workflow_detector

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

        def run_workflow():
            """Background thread to execute workflow launcher"""
            try:
                # Parse command into parts
                cmd = workflow['command'].split()

                print(f"[WORKFLOW] Starting workflow: {' '.join(cmd)}", file=sys.stderr)
                print(f"[WORKFLOW] Working directory: {PROJECT_ROOT}", file=sys.stderr)

                # Check if this is run-workflow.sh (local mode) - needs bash execution
                if cmd[0] == './run-workflow.sh':
                    # Make sure script is executable
                    script_path = PROJECT_ROOT / 'run-workflow.sh'
                    if script_path.exists():
                        import os
                        os.chmod(script_path, 0o755)

                    # Execute with bash to handle shebang and virtual env activation
                    cmd = ['/bin/bash'] + cmd

                # Execute in project root directory
                result = subprocess.run(
                    cmd,
                    cwd=PROJECT_ROOT,
                    check=True,
                    capture_output=True,
                    text=True
                )

                print(f"[WORKFLOW] Workflow completed successfully", file=sys.stderr)
                if result.stdout:
                    print(f"[WORKFLOW] stdout: {result.stdout}", file=sys.stderr)

            except subprocess.CalledProcessError as e:
                print(f"[WORKFLOW] Workflow execution failed with code {e.returncode}", file=sys.stderr)
                print(f"[WORKFLOW] stdout: {e.stdout}", file=sys.stderr)
                print(f"[WORKFLOW] stderr: {e.stderr}", file=sys.stderr)
            except Exception as e:
                print(f"[WORKFLOW] Error running workflow: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()

        # Start workflow in background thread
        thread = threading.Thread(target=run_workflow, daemon=True)
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Workflow started in background',
            'dashboard_url': workflow.get('dashboard_url', 'http://localhost:8765')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start workflow: {str(e)}'
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
