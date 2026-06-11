#!/usr/bin/env python3
"""
Dashboard Server
================
Flask server with real-time status updates and log streaming
"""

import json
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, Response
import logging

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

SCRIPT_DIR = Path(__file__).parent.resolve()
STATUS_DIR = SCRIPT_DIR.parent / ".multi_process_status"
LOGS_DIR = SCRIPT_DIR.parent / "logs"

app = Flask(__name__,
            template_folder=str(SCRIPT_DIR / 'templates'),
            static_folder=str(SCRIPT_DIR / 'static'))


@app.route('/')
def dashboard():
    """Serve the dashboard HTML template."""
    return render_template('dashboard.html')


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


def run_server(port=8765, debug=False):
    """Run the Flask server."""
    print(f"\n📊 Dashboard server starting...")
    print(f"   URL: http://localhost:{port}")
    print(f"   Refresh: Every 2 seconds")
    print(f"   Logs: Real-time streaming")
    print(f"\n   Press Ctrl+C to stop\n")

    app.run(host='localhost', port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    # Create directories if needed
    STATUS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    run_server()
