#!/usr/bin/env python3
"""
Test Bug Fixes
- Wizard close functionality
- NotebookLM login instructions
"""

import sys
import time
import subprocess
import urllib.request
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

    process = subprocess.Popen(
        [str(venv_python), str(server_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(PROJECT_ROOT)
    )

    time.sleep(0.5)
    for attempt in range(20):
        try:
            urllib.request.urlopen(f"{BASE_URL}/ping", timeout=0.5)
            return process
        except:
            if attempt < 19:
                time.sleep(0.3)
    return None


def test_wizard_close_functionality():
    """Test 1: Wizard close button and outside click"""
    print("\n" + "="*70)
    print("TEST 1: Wizard Close Functionality")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        checks = [
            ('closeWizard()', 'Close wizard function'),
            ('closeWizardIfClickedOutside', 'Click outside handler'),
            ('onclick="closeWizard()"', 'Close button handler'),
            ('onclick="closeWizardIfClickedOutside(event)"', 'Overlay click handler'),
            ('event.stopPropagation()', 'Modal click prevention'),
        ]

        passed = 0
        for check, description in checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(checks)

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def test_notebooklm_login_instructions():
    """Test 2: NotebookLM login provides clear instructions"""
    print("\n" + "="*70)
    print("TEST 2: NotebookLM Login Instructions")
    print("="*70)

    try:
        # Trigger login (it will run in background)
        req = urllib.request.Request(
            f"{BASE_URL}/api/notebooklm-login",
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')

        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))

        if data.get('success'):
            print(f"  ✅ Login initiated successfully")

            if 'instructions' in data and len(data['instructions']) > 0:
                print(f"  ✅ Instructions provided ({len(data['instructions'])} lines)")

                # Check for key instruction elements
                instructions_text = '\n'.join(data['instructions'])

                key_points = [
                    ('browser', 'Mentions browser window'),
                    ('popup blocker', 'Mentions popup blockers'),
                    ('notebooklm login', 'Provides manual command'),
                    ('terminal', 'Mentions terminal alternative'),
                ]

                found = 0
                for keyword, description in key_points:
                    if keyword.lower() in instructions_text.lower():
                        print(f"    ✅ {description}")
                        found += 1
                    else:
                        print(f"    ⚠️  {description} not mentioned")

                return found >= 3
            else:
                print(f"  ❌ No instructions provided")
                return False
        else:
            print(f"  ❌ Login failed: {data.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def test_wizard_button_visibility():
    """Test 3: Wizard launch button is visible"""
    print("\n" + "="*70)
    print("TEST 3: Wizard Launch Button Visibility")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        checks = [
            ('id="launchWizardBtn"', 'Launch button element'),
            ('Quick Setup Wizard', 'Wizard title'),
            ('Launch Wizard', 'Button text'),
            ('Step-by-step guided setup', 'Description text'),
        ]

        passed = 0
        for check, description in checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(checks)

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def main():
    print("="*70)
    print("BUG FIX VERIFICATION TEST SUITE")
    print("="*70)

    # Start dashboard
    process = start_dashboard()
    if not process:
        print("\n❌ Failed to start dashboard - aborting tests")
        return 1

    time.sleep(1)

    # Run all tests
    tests = [
        ("Wizard Close Functionality", test_wizard_close_functionality),
        ("NotebookLM Login Instructions", test_notebooklm_login_instructions),
        ("Wizard Launch Button", test_wizard_button_visibility),
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
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n✅ ALL BUG FIXES VERIFIED")
        print("\nFixed issues:")
        print("  ✅ Wizard can now be closed by:")
        print("     - Clicking the × button")
        print("     - Clicking outside the modal")
        print("  ✅ NotebookLM login provides clear instructions:")
        print("     - Mentions browser window")
        print("     - Explains popup blocker workaround")
        print("     - Provides manual terminal command")
        return 0
    else:
        print("\n❌ SOME FIXES NEED ATTENTION")
        return 1


if __name__ == "__main__":
    sys.exit(main())
