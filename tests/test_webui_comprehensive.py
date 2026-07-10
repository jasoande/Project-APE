#!/usr/bin/env python3
"""
Comprehensive Web UI Testing
Tests all buttons, features, and endpoints to ensure correct venv usage
"""

import sys
import time
import subprocess
import urllib.request
import urllib.parse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DASHBOARD_PORT = 8765
BASE_URL = f"http://localhost:{DASHBOARD_PORT}"


def cleanup_dashboard():
    """Kill any running dashboard processes"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{DASHBOARD_PORT}'],
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], timeout=2)
            time.sleep(1)
    except:
        pass


def start_dashboard():
    """Start dashboard using venv Python"""
    cleanup_dashboard()
    venv_python = Path.home() / ".project-ape-venv" / "bin" / "python3"
    server_script = PROJECT_ROOT / "dashboard" / "server.py"

    if not venv_python.exists():
        print(f"❌ Virtual environment not found at {venv_python}")
        return None

    print(f"Starting dashboard with venv: {venv_python}")
    process = subprocess.Popen(
        [str(venv_python), str(server_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(PROJECT_ROOT)
    )

    # Wait for server to be ready
    time.sleep(0.5)
    for attempt in range(20):
        try:
            urllib.request.urlopen(f"{BASE_URL}/ping", timeout=0.5)
            print(f"✅ Dashboard started successfully")
            return process
        except:
            if attempt < 19:
                time.sleep(0.3)

    print(f"❌ Dashboard failed to start")
    process.kill()
    return None


def get_csrf_token():
    """Get CSRF token from configure page"""
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')
        # Extract CSRF token from meta tag
        import re
        match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)
        if match:
            return match.group(1)
    except:
        pass
    return None


def test_api_endpoint(path, method="GET", data=None, expected_status=200, description="", csrf_token=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = urllib.request.urlopen(url, timeout=5)
        elif method == "POST":
            req = urllib.request.Request(url, method='POST')
            req.add_header('Content-Type', 'application/json')
            if csrf_token:
                req.add_header('X-CSRF-Token', csrf_token)
            if data:
                req.data = json.dumps(data).encode('utf-8')
            response = urllib.request.urlopen(req, timeout=5)

        status = response.status
        content = response.read()

        if status == expected_status:
            print(f"  ✅ {description or path}: {status}")
            return True, content
        else:
            print(f"  ❌ {description or path}: Expected {expected_status}, got {status}")
            return False, content
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            print(f"  ✅ {description or path}: {e.code} (expected)")
            return True, e.read()
        else:
            print(f"  ❌ {description or path}: HTTP {e.code}")
            return False, e.read()
    except Exception as e:
        print(f"  ❌ {description or path}: {e}")
        return False, None


def test_page_rendering():
    """Test 1: All HTML pages render correctly"""
    print("\n" + "="*70)
    print("TEST 1: Page Rendering")
    print("="*70)

    pages = [
        ("/", "Dashboard home"),
        ("/configure", "Configuration page"),
        ("/setup-environment", "Environment setup page"),
        ("/status", "Status JSON endpoint"),
    ]

    passed = 0
    for path, desc in pages:
        success, content = test_api_endpoint(path, description=desc)
        if success and content:
            # Check for correct branding
            if path != "/status":
                html = content.decode('utf-8')
                if "Account Intelligence" in html:
                    print(f"    → Correct branding found")
                    passed += 1
                else:
                    print(f"    ⚠️  Branding not found in page")
            else:
                passed += 1

    print(f"\nResult: {passed}/{len(pages)} pages working")
    return passed == len(pages)


def test_api_endpoints():
    """Test 2: All API endpoints respond correctly"""
    print("\n" + "="*70)
    print("TEST 2: API Endpoints")
    print("="*70)

    endpoints = [
        ("/ping", "GET", None, 200, "Health ping"),
        ("/health", "GET", None, 200, "Health check"),
        ("/api/config-status", "GET", None, 200, "Config status"),
        ("/api/oauth-status", "GET", None, 200, "OAuth status"),
        ("/api/available-logs", "GET", None, 200, "Available logs"),
        ("/api/system-status", "GET", None, 200, "System status"),
        ("/api/cache-stats", "GET", None, 200, "Cache stats"),
    ]

    passed = 0
    for path, method, data, expected, desc in endpoints:
        success, content = test_api_endpoint(path, method, data, expected, desc)
        if success:
            # Verify JSON response where applicable
            if path != "/ping" and content:
                try:
                    json_data = json.loads(content.decode('utf-8'))
                    print(f"    → Valid JSON response")
                    passed += 1
                except:
                    print(f"    ⚠️  Invalid JSON response")
            else:
                passed += 1

    print(f"\nResult: {passed}/{len(endpoints)} endpoints working")
    return passed == len(endpoints)


def test_authentication_endpoints():
    """Test 3: Authentication endpoints (without triggering actual OAuth)"""
    print("\n" + "="*70)
    print("TEST 3: Authentication Endpoints (Dry Run)")
    print("="*70)

    endpoints = [
        ("/api/check-auth-status", "GET", None, 200, "NotebookLM auth status"),
        ("/api/oauth-status", "GET", None, 200, "Drive OAuth status"),
    ]

    passed = 0
    for path, method, data, expected, desc in endpoints:
        success, content = test_api_endpoint(path, method, data, expected, desc)
        if success and content:
            try:
                json_data = json.loads(content.decode('utf-8'))
                if 'success' in json_data or 'authenticated' in json_data:
                    print(f"    → Response structure valid")
                    passed += 1
                else:
                    print(f"    ⚠️  Unexpected response structure")
            except:
                print(f"    ⚠️  Invalid JSON")

    print(f"\nResult: {passed}/{len(endpoints)} auth endpoints working")
    return passed == len(endpoints)


def test_configuration_api():
    """Test 4: Configuration API (CSRF Protection Verified)"""
    print("\n" + "="*70)
    print("TEST 4: Configuration API (CSRF Protection)")
    print("="*70)

    # Test 1: Verify CSRF protection is active (should reject without token)
    test_data = {"url": "https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J"}
    success, content = test_api_endpoint(
        "/api/validate-drive-url",
        "POST",
        test_data,
        400,  # Expect 400 without CSRF token
        "CSRF protection active (no token)"
    )

    tests_passed = 0
    if success:
        print(f"  ✅ CSRF protection working correctly")
        tests_passed += 1
    else:
        print(f"  ⚠️  CSRF protection may not be active")

    # Test 2: Verify config page loads (where CSRF tokens are used)
    success, content = test_api_endpoint(
        "/configure",
        "GET",
        None,
        200,
        "Config page with CSRF token"
    )

    if success and content:
        html = content.decode('utf-8')
        import re
        csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)
        if csrf_match:
            print(f"  ✅ CSRF token present in page")
            tests_passed += 1
        else:
            print(f"  ❌ CSRF token missing from page")

    print(f"\nResult: {tests_passed}/2 security tests passed")
    print(f"Note: Configuration POST endpoints require CSRF tokens (browser provides these)")
    return tests_passed == 2


def test_system_info_endpoints():
    """Test 5: System information endpoints"""
    print("\n" + "="*70)
    print("TEST 5: System Information")
    print("="*70)

    success, content = test_api_endpoint(
        "/api/system-status",
        "GET",
        None,
        200,
        "System status"
    )

    if success and content:
        try:
            data = json.loads(content.decode('utf-8'))
            print(f"    → Python version: {data.get('python_version')}")
            print(f"    → Virtual env active: {data.get('venv_active')}")
            print(f"    → Disk free: {data.get('disk_free_gb')} GB")

            if data.get('venv_active'):
                print(f"  ✅ Running in virtual environment")
                return True
            else:
                print(f"  ❌ NOT running in virtual environment!")
                return False
        except Exception as e:
            print(f"  ❌ Failed to parse system status: {e}")
            return False

    return False


def main():
    print("="*70)
    print("COMPREHENSIVE WEB UI TEST SUITE")
    print("="*70)

    # Start dashboard
    process = start_dashboard()
    if not process:
        print("\n❌ Failed to start dashboard - aborting tests")
        return 1

    time.sleep(1)  # Give server time to settle

    # Run all tests
    tests = [
        ("Page Rendering", test_page_rendering),
        ("API Endpoints", test_api_endpoints),
        ("Authentication Endpoints", test_authentication_endpoints),
        ("Configuration API", test_configuration_api),
        ("System Information & Venv Check", test_system_info_endpoints),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Cleanup
    process.kill()
    cleanup_dashboard()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} test suites passed")

    if total_passed == len(results):
        print("\n✅ ALL WEB UI TESTS PASSED")
        print("   - All pages render correctly")
        print("   - All API endpoints working")
        print("   - Correct virtual environment in use")
        print("   - Correct branding applied")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
