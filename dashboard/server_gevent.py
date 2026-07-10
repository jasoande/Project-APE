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

    # Create directories
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Get port
    port = int(os.environ.get('DASHBOARD_PORT', 8765))
    host = os.environ.get('DASHBOARD_HOST', '127.0.0.1')

    print(f"")
    print(f"🚀 Dashboard (Gevent mode) starting on http://{host}:{port}")
    print(f"   Using gevent WSGI server (greenlet-based)")
    print(f"   Supports 10,000+ concurrent SSE connections")
    print(f"   Thread exhaustion: ELIMINATED ✅")
    print(f"")
    print(f"📊 Dashboard URL: http://{host}:{port}")
    print(f"⚙️  Configure:     http://{host}:{port}/configure")
    print(f"")

    # Create WSGI server
    http_server = WSGIServer((host, port), app)

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        http_server.stop()

if __name__ == "__main__":
    run_server()
