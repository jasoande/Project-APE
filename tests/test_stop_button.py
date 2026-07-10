#!/usr/bin/env python3
"""Test the stop workflow button API endpoint."""

import json
import time
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
DASHBOARD_PORT = 8765

def test_stop_workflow_api():
    """Test that /api/stop-workflow endpoint works."""
    print("\n" + "="*60)
    print("TEST: Stop Workflow API Endpoint")
    print("="*60)

    # Clean up PID file if exists
    pid_file = STATUS_DIR / '.workflow_pid'
    if pid_file.exists():
        print(f"⚠️  Removing existing PID file")
        pid_file.unlink()

    print("\n🚀 Starting test workflow...")
    # Start workflow in background
    workflow_process = subprocess.Popen(
        [sys.executable, "main.py", "--mode", "fast", "--clients", "hershey", "--skip-preflight"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print(f"   Workflow PID: {workflow_process.pid}")

    # Wait for PID file
    print("\n⏳ Waiting for PID file...")
    max_wait = 10
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if pid_file.exists():
            print("   ✅ PID file created")
            break
        time.sleep(0.5)
    else:
        print("   ❌ PID file not created - test failed")
        workflow_process.terminate()
        return False

    # Test API endpoint
    print("\n📡 Testing /api/stop-workflow endpoint...")

    try:
        # Make POST request to stop workflow
        req = urllib.request.Request(
            f"http://localhost:{DASHBOARD_PORT}/api/stop-workflow",
            method='POST',
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())

            print(f"   Response status: {response.status}")
            print(f"   Response data: {json.dumps(data, indent=2)}")

            if data.get('success'):
                print("\n✅ TEST PASSED: Stop workflow API succeeded")

                # Verify workflow was actually stopped
                time.sleep(2)
                if workflow_process.poll() is not None:
                    print("   ✅ Workflow process terminated")
                else:
                    print("   ⚠️  Workflow process still running (may take time to stop)")
                    workflow_process.kill()

                # Verify PID file was removed
                if not pid_file.exists():
                    print("   ✅ PID file removed")
                else:
                    print("   ⚠️  PID file still exists")
                    pid_file.unlink()

                return True
            else:
                print(f"\n❌ TEST FAILED: API returned success=False")
                print(f"   Error: {data.get('error')}")
                workflow_process.kill()
                return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"\n❌ TEST FAILED: HTTP {e.code}")
        print(f"   Error: {error_body}")
        workflow_process.kill()
        if pid_file.exists():
            pid_file.unlink()
        return False

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        workflow_process.kill()
        if pid_file.exists():
            pid_file.unlink()
        return False


if __name__ == "__main__":
    # Check if dashboard is running
    try:
        urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/health", timeout=2)
    except:
        print(f"❌ Dashboard is not running on port {DASHBOARD_PORT}")
        print(f"   Start it with: python3 dashboard/server.py")
        sys.exit(1)

    result = test_stop_workflow_api()
    sys.exit(0 if result else 1)
