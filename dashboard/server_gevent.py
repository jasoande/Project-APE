#!/usr/bin/env python3
"""
Gevent-based server runner for dashboard.

This eliminates thread exhaustion by using greenlet-based concurrency
instead of thread-per-connection.

Usage:
    python dashboard/server_gevent.py

Supports 10,000+ concurrent SSE connections on ~4 threads.
"""

# CRITICAL: Monkey-patch FIRST before any other imports
from gevent import monkey
monkey.patch_all()

import sys
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now import the Flask app
from dashboard.server import app, STATUS_DIR, LOGS_DIR

def run_server():
    """Run server with gevent WSGI server."""
    import os
    from gevent.pywsgi import WSGIServer

    # Load SSL and host configuration from vars.py if available
    try:
        import importlib.util
        vars_path = PROJECT_ROOT / "vars.py"
        if vars_path.exists():
            spec = importlib.util.spec_from_file_location("vars", vars_path)
            vars_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vars_module)

            ssl_enabled = getattr(vars_module, 'SSL_ENABLED', False)
            ssl_cert_path = getattr(vars_module, 'SSL_CERT_PATH', '')
            ssl_key_path = getattr(vars_module, 'SSL_KEY_PATH', '')
            dashboard_host = getattr(vars_module, 'DASHBOARD_HOST', '127.0.0.1')
        else:
            ssl_enabled = False
            ssl_cert_path = ''
            ssl_key_path = ''
            dashboard_host = '127.0.0.1'
    except Exception:
        ssl_enabled = False
        ssl_cert_path = ''
        ssl_key_path = ''
        dashboard_host = '127.0.0.1'

    # Create directories
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Get port and host (environment variables override vars.py)
    port = int(os.environ.get('DASHBOARD_PORT', 8765))
    host = os.environ.get('DASHBOARD_HOST', dashboard_host)

    # Check SSL configuration
    ssl_kwargs = {}
    protocol = "http"
    if ssl_enabled and ssl_cert_path and ssl_key_path:
        cert_file = PROJECT_ROOT / ssl_cert_path
        key_file = PROJECT_ROOT / ssl_key_path

        if cert_file.exists() and key_file.exists():
            ssl_kwargs = {
                'keyfile': str(key_file),
                'certfile': str(cert_file)
            }
            protocol = "https"
            print(f"🔒 SSL/HTTPS enabled")
        else:
            print(f"⚠️  SSL enabled but certificate files not found:")
            if not cert_file.exists():
                print(f"   Certificate: {cert_file} (not found)")
            if not key_file.exists():
                print(f"   Key: {key_file} (not found)")
            print(f"   Falling back to HTTP")

    print(f"")
    print(f"🚀 Dashboard (Gevent mode) starting on {protocol}://{host}:{port}")
    print(f"   Using gevent WSGI server (greenlet-based)")
    print(f"   Supports 10,000+ concurrent SSE connections")
    print(f"   Thread exhaustion: ELIMINATED ✅")
    print(f"")
    print(f"📊 Dashboard URL: {protocol}://{host}:{port}")
    print(f"⚙️  Configure:     {protocol}://{host}:{port}/configure")
    print(f"")

    # Create WSGI server with optional SSL
    http_server = WSGIServer((host, port), app, **ssl_kwargs)

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        http_server.stop()

if __name__ == "__main__":
    run_server()
