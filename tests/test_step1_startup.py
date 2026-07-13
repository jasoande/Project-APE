#!/usr/bin/env python3
"""
Test Step 1: Dashboard Startup Optimization
Tests that the new startup logic is faster and still reliable
"""

import sys
import time
import subprocess
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DASHBOARD_PORT = 8765

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
    except Exception:
        pass


def test_ping_endpoint():
    """Test 1: /ping endpoint exists and responds quickly"""
    print("\n" + "="*70)
    print("TEST 1: Lightweight /ping endpoint")
    print("="*70)

    cleanup_dashboard()

    # Start dashboard
    venv_python = Path.home() / ".project-ape-venv" / "bin" / "python3"
    server_script = PROJECT_ROOT / "dashboard" / "server.py"

    print(f"Starting dashboard server...")
    start_time = time.time()

    process = subprocess.Popen(
        [str(venv_python), str(server_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(PROJECT_ROOT)
    )

    # Wait for /ping to respond
    ping_responded = False
    for attempt in range(30):
        try:
            response = urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/ping", timeout=0.5)
            if response.read().decode() == 'ok':
                elapsed = time.time() - start_time
                print(f"✅ /ping responded in {elapsed:.2f}s (attempt {attempt + 1})")
                ping_responded = True
                break
        except Exception:
            time.sleep(0.3)

    if not ping_responded:
        print(f"❌ /ping did not respond within timeout")
        process.kill()
        return False

    # Verify /health also works
    try:
        response = urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/health", timeout=2)
        data = response.read()
        print(f"✅ /health endpoint also working")
    except Exception as e:
        print(f"❌ /health endpoint failed: {e}")
        process.kill()
        return False

    # Verify /configure page loads
    try:
        response = urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/configure", timeout=2)
        html = response.read().decode()
        if "Account Intelligence" in html:
            print(f"✅ /configure page loads with correct branding")
        else:
            print(f"⚠️  /configure page loads but branding not found")
    except Exception as e:
        print(f"❌ /configure page failed: {e}")
        process.kill()
        return False

    process.kill()
    time.sleep(1)

    return True


def test_smart_polling_speed():
    """Test 2: Smart polling is faster than old hardcoded 3-second sleep"""
    print("\n" + "="*70)
    print("TEST 2: Smart Polling Performance")
    print("="*70)

    cleanup_dashboard()

    venv_python = Path.home() / ".project-ape-venv" / "bin" / "python3"
    server_script = PROJECT_ROOT / "dashboard" / "server.py"

    # Simulate the new smart polling logic
    print(f"Testing smart polling logic...")
    start_time = time.time()

    process = subprocess.Popen(
        [str(venv_python), str(server_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(PROJECT_ROOT)
    )

    time.sleep(0.5)  # Initial settle
    responded = False

    for attempt in range(20):
        try:
            urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/ping", timeout=0.5)
            total_time = time.time() - start_time
            print(f"✅ Server ready in {total_time:.2f}s (vs 3.0s hardcoded)")

            if total_time < 3.0:
                print(f"✅ Improvement: {3.0 - total_time:.2f}s faster ({(1 - total_time/3.0)*100:.1f}% reduction)")
                responded = True
            else:
                print(f"⚠️  No improvement over old method")
            break
        except Exception:
            if attempt < 19:
                time.sleep(0.3)

    process.kill()
    time.sleep(1)

    return responded


def test_reliability():
    """Test 3: Multiple consecutive starts work reliably"""
    print("\n" + "="*70)
    print("TEST 3: Reliability Check (5 consecutive starts)")
    print("="*70)

    venv_python = Path.home() / ".project-ape-venv" / "bin" / "python3"
    server_script = PROJECT_ROOT / "dashboard" / "server.py"

    success_count = 0
    times = []

    for i in range(5):
        cleanup_dashboard()
        print(f"\nRun {i+1}/5:", end=" ")

        start_time = time.time()
        process = subprocess.Popen(
            [str(venv_python), str(server_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT)
        )

        time.sleep(0.5)
        responded = False

        for attempt in range(20):
            try:
                urllib.request.urlopen(f"http://localhost:{DASHBOARD_PORT}/ping", timeout=0.5)
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"✅ Ready in {elapsed:.2f}s")
                success_count += 1
                responded = True
                break
            except Exception:
                if attempt < 19:
                    time.sleep(0.3)

        if not responded:
            print(f"❌ Failed to start")

        process.kill()
        time.sleep(1)

    print(f"\n{'='*70}")
    print(f"Results: {success_count}/5 successful starts")
    if times:
        avg_time = sum(times) / len(times)
        print(f"Average startup time: {avg_time:.2f}s")
        print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")

    return success_count == 5


def main():
    print("="*70)
    print("STEP 1: Dashboard Startup Optimization - Test Suite")
    print("="*70)

    # Run all tests
    tests = [
        ("Ping Endpoint", test_ping_endpoint),
        ("Smart Polling Speed", test_smart_polling_speed),
        ("Reliability", test_reliability),
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

    # Final cleanup
    cleanup_dashboard()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n✅ ALL TESTS PASSED - Step 1 implementation successful!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
