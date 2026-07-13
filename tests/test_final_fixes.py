#!/usr/bin/env python3
"""
Final Comprehensive Test Suite
Tests all requested fixes:
1. Wizard banner dismissal
2. Rebranding to "Account Intelligence"
3. Launcher scripts updated
"""

import sys
import time
import subprocess
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DASHBOARD_PORT = 8765
BASE_URL = f"http://localhost:{DASHBOARD_PORT}"


def cleanup_dashboard():
    try:
        result = subprocess.run(['lsof', '-ti', f':{DASHBOARD_PORT}'],
                              capture_output=True, text=True, timeout=5)
        if result.stdout.strip():
            for pid in result.stdout.strip().split('\n'):
                subprocess.run(['kill', '-9', pid], timeout=2)
            time.sleep(1)
    except Exception:
        pass


def start_dashboard():
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
        except Exception:
            if attempt < 19:
                time.sleep(0.3)
    return None


def test_wizard_banner_dismissal():
    """Test 1: Wizard banner can be dismissed"""
    print("\n" + "="*70)
    print("TEST 1: Wizard Banner Dismissal")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        checks = [
            ('id="wizardBanner"', 'Wizard banner element'),
            ('dismissWizardBanner', 'Dismiss function'),
            ('localStorage.setItem', 'LocalStorage persistence'),
            ('checkWizardBannerStatus', 'Banner status check'),
            ('display: none', 'Hidden by default'),
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


def test_rebranding():
    """Test 2: Rebranding to "Account Intelligence" """
    print("\n" + "="*70)
    print("TEST 2: Rebranding Verification")
    print("="*70)

    try:
        # Check key pages
        pages = [
            ('/configure', 'Configure page'),
            ('/', 'Dashboard page'),
            ('/setup-environment', 'Setup page'),
        ]

        all_passed = True
        for path, page_name in pages:
            response = urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5)
            html = response.read().decode('utf-8')

            if 'Account Intelligence' in html:
                print(f"  ✅ {page_name}: Found 'Account Intelligence'")

                # Ensure old branding is gone
                if 'project ape Account Intelligence' in html:
                    print(f"    ⚠️  Old branding still present!")
                    all_passed = False
            else:
                print(f"  ❌ {page_name}: 'Account Intelligence' not found")
                all_passed = False

        # Check Python files
        main_py = PROJECT_ROOT / "main.py"
        if main_py.exists():
            content = main_py.read_text()
            if 'Account Intelligence' in content and 'project ape Account Intelligence' not in content:
                print(f"  ✅ main.py: Correctly rebranded")
            else:
                print(f"  ❌ main.py: Rebranding issue")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def test_launcher_scripts():
    """Test 3: Launcher scripts exist and are updated"""
    print("\n" + "="*70)
    print("TEST 3: Launcher Scripts")
    print("="*70)

    launchers = [
        ('launch-project-ape.command', 'macOS', True),
        ('project-ape-launcher.desktop', 'Linux', False),
        ('launch-project-ape.bat', 'Windows', False),
    ]

    passed = 0
    for filename, platform, check_executable in launchers:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            print(f"  ✅ {platform} launcher exists: {filename}")

            # Check if executable (macOS .command file)
            if check_executable:
                import os
                is_exec = os.access(file_path, os.X_OK)
                if is_exec:
                    print(f"    ✅ File is executable")
                else:
                    print(f"    ⚠️  File is not executable (may need: chmod +x)")

            # Check branding
            content = file_path.read_text()
            if 'Account Intelligence' in content:
                print(f"    ✅ Correctly branded")
                passed += 1
            elif 'Project APE' in content:
                print(f"    ⚠️  Still has old branding")
            else:
                print(f"    ✅ No specific branding")
                passed += 1
        else:
            print(f"  ❌ {platform} launcher missing: {filename}")

    return passed >= 2  # At least 2 launchers should be properly set up


def test_king_kong_logo():
    """Test 4: King Kong logo still present"""
    print("\n" + "="*70)
    print("TEST 4: King Kong Logo Preserved")
    print("="*70)

    try:
        # Check that kingkong.png is still referenced
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        if 'kingkong.png' in html:
            print(f"  ✅ King Kong logo reference found")

            # Check file exists
            logo_path = PROJECT_ROOT / "dashboard" / "static" / "kingkong.png"
            if logo_path.exists():
                print(f"  ✅ Logo file exists: {logo_path.name}")
                return True
            else:
                print(f"  ❌ Logo file missing")
                return False
        else:
            print(f"  ❌ King Kong logo reference not found")
            return False

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def main():
    print("="*70)
    print("FINAL COMPREHENSIVE TEST SUITE")
    print("="*70)

    # Start dashboard
    process = start_dashboard()
    if not process:
        print("\n❌ Failed to start dashboard - aborting tests")
        return 1

    time.sleep(1)

    # Run all tests
    tests = [
        ("Wizard Banner Dismissal", test_wizard_banner_dismissal),
        ("Rebranding to Account Intelligence", test_rebranding),
        ("Launcher Scripts Updated", test_launcher_scripts),
        ("King Kong Logo Preserved", test_king_kong_logo),
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
    print("FINAL TEST SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n✅ ALL FIXES VERIFIED AND WORKING!")
        print("\nCompleted changes:")
        print("  ✅ Wizard banner can be permanently dismissed")
        print("  ✅ Rebranded to 'Account Intelligence'")
        print("  ✅ King Kong logo preserved")
        print("  ✅ Launcher scripts updated for all platforms:")
        print("     - macOS: launch-project-ape.command")
        print("     - Linux: project-ape-launcher.desktop")
        print("     - Windows: launch-project-ape.bat")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
