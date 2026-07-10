#!/usr/bin/env python3
"""
Test comprehensive health check endpoint.

This test validates:
1. /health/detailed endpoint returns proper structure
2. All subsystem checks are present
3. Status codes are correct (200 for healthy/degraded, 503 for unhealthy)
4. Individual check statuses are valid
"""

import sys
from pathlib import Path
import subprocess
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_health_detailed_endpoint():
    """Test that /health/detailed endpoint works and returns expected structure."""

    print("\n🧪 Testing /health/detailed endpoint...")

    # Start the dashboard server
    server_process = subprocess.Popen(
        [sys.executable, 'dashboard/server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    try:
        # Wait for server to start
        time.sleep(3)

        # Test the endpoint
        import urllib.request
        import json

        try:
            response = urllib.request.urlopen('http://localhost:8765/health/detailed', timeout=10)
            data = json.loads(response.read())

            # Verify structure
            assert 'status' in data, "❌ Missing 'status' field"
            assert 'timestamp' in data, "❌ Missing 'timestamp' field"
            assert 'checks' in data, "❌ Missing 'checks' field"

            print(f"✅ Response structure valid")
            print(f"   Overall status: {data['status']}")
            print(f"   Timestamp: {data['timestamp']}")

            # Verify all expected checks are present
            expected_checks = [
                'notebooklm_auth',
                'drive_auth',
                'disk_space',
                'process_health',
                'notebooklm_cli'
            ]

            for check_name in expected_checks:
                assert check_name in data['checks'], f"❌ Missing check: {check_name}"
                check = data['checks'][check_name]

                # Verify each check has status and message
                assert 'status' in check, f"❌ Check {check_name} missing 'status'"
                assert 'message' in check, f"❌ Check {check_name} missing 'message'"

                # Verify status is valid
                assert check['status'] in ['ok', 'warn', 'error'], f"❌ Invalid status for {check_name}: {check['status']}"

                print(f"   ✅ {check_name}: {check['status']} - {check['message']}")

            # Verify overall status is consistent
            has_error = any(c['status'] == 'error' for c in data['checks'].values())
            has_warn = any(c['status'] == 'warn' for c in data['checks'].values())

            if has_error:
                assert data['status'] in ['unhealthy'], f"❌ Expected 'unhealthy' status with errors, got '{data['status']}'"
            elif has_warn:
                assert data['status'] in ['degraded', 'healthy'], f"❌ Expected 'degraded' or 'healthy' with warnings, got '{data['status']}'"
            else:
                assert data['status'] == 'healthy', f"❌ Expected 'healthy' status, got '{data['status']}'"

            print(f"\n✅ All checks present and valid")

        except urllib.error.HTTPError as e:
            if e.code == 503:
                # Service unavailable - still valid if system is unhealthy
                data = json.loads(e.read())
                print(f"⚠️  Service returned 503 (unhealthy): {data.get('status')}")
                assert data['status'] == 'unhealthy', "❌ 503 response should have 'unhealthy' status"
                print("✅ Correct status code for unhealthy state")
            else:
                raise

    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait(timeout=5)
        print("🛑 Stopped server")


def test_health_detailed_checks():
    """Test individual health check logic."""

    print("\n🧪 Testing individual health check implementations...")

    # Test disk space check
    import shutil
    total, used, free = shutil.disk_usage('.')
    free_gb = free / (1024**3)
    print(f"   Disk space: {free_gb:.1f} GB free")

    if free_gb < 1.0:
        print("   ⚠️  Critical disk space!")
    elif free_gb < 5.0:
        print("   ⚠️  Low disk space")
    else:
        print("   ✅ Adequate disk space")

    # Test Drive token check
    from datetime import datetime
    drive_token_path = Path.home() / '.project-ape' / 'drive_token.json'

    if drive_token_path.exists():
        import json
        token_data = json.loads(drive_token_path.read_text())

        if 'expiry' in token_data:
            expiry_str = token_data['expiry']
            print(f"   Drive token expiry: {expiry_str}")

            try:
                # Try to parse expiry
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        expiry = datetime.strptime(expiry_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))

                days_left = (expiry - datetime.now(expiry.tzinfo or None)).days
                print(f"   Drive token: {days_left} days until expiry")

                if days_left < 0:
                    print("   ❌ Token expired!")
                elif days_left < 7:
                    print("   ⚠️  Token expires soon")
                else:
                    print("   ✅ Token valid")

            except Exception as e:
                print(f"   ⚠️  Could not parse expiry: {e}")
        else:
            print("   ✅ Drive token exists (no expiry info)")
    else:
        print("   ⚠️  Drive token not found")

    # Test NotebookLM CLI availability
    try:
        result = subprocess.run(
            ['notebooklm', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"   ✅ NotebookLM CLI available: {result.stdout.strip()}")
        else:
            print(f"   ❌ NotebookLM CLI error: {result.stderr.strip()}")

    except FileNotFoundError:
        print("   ❌ NotebookLM CLI not installed")
    except Exception as e:
        print(f"   ❌ NotebookLM CLI check failed: {e}")

    print("\n✅ Individual check tests complete")


if __name__ == '__main__':
    try:
        test_health_detailed_checks()
        test_health_detailed_endpoint()

        print("\n" + "="*60)
        print("✅ ALL HEALTH CHECK TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
