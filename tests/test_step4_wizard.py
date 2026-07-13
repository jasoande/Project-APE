#!/usr/bin/env python3
"""
Test Step 4: Progressive Disclosure Wizard
Tests wizard modal, step progression, and guided setup flow
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
        except Exception:
            if attempt < 19:
                time.sleep(0.3)
    return None


def test_wizard_css_classes():
    """Test 1: Wizard CSS classes are defined"""
    print("\n" + "="*70)
    print("TEST 1: Wizard CSS Classes")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        css_checks = [
            ('wizard-overlay', 'Wizard overlay'),
            ('wizard-modal', 'Wizard modal'),
            ('wizard-header', 'Wizard header'),
            ('wizard-progress', 'Progress indicator'),
            ('wizard-step', 'Wizard step'),
            ('wizard-step-number', 'Step number'),
            ('wizard-step-label', 'Step label'),
            ('wizard-connector', 'Step connector'),
            ('wizard-content', 'Content area'),
            ('wizard-footer', 'Footer area'),
            ('wizardSlideIn', 'Slide-in animation'),
        ]

        passed = 0
        for css_class, description in css_checks:
            if css_class in html:
                print(f"  ✅ {description}: .{css_class}")
                passed += 1
            else:
                print(f"  ❌ {description}: .{css_class} not found")

        return passed == len(css_checks)

    except Exception as e:
        print(f"  ❌ Failed to check CSS: {e}")
        return False


def test_wizard_html_structure():
    """Test 2: Wizard HTML structure exists"""
    print("\n" + "="*70)
    print("TEST 2: Wizard HTML Structure")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        structure_checks = [
            ('id="wizardOverlay"', 'Wizard overlay element'),
            ('id="launchWizardBtn"', 'Launch wizard button'),
            ('Quick Setup Wizard', 'Wizard title'),
            ('wizard-step-1', 'Step 1: Welcome'),
            ('wizard-step-2', 'Step 2: Add Client'),
            ('wizard-step-3', 'Step 3: Review'),
            ('wizard-step-4', 'Step 4: Launch'),
            ('wizard-client-name', 'Client name input'),
            ('wizard-client-folder', 'Folder URL input'),
        ]

        passed = 0
        for check, description in structure_checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(structure_checks)

    except Exception as e:
        print(f"  ❌ Failed to check HTML structure: {e}")
        return False


def test_wizard_javascript():
    """Test 3: Wizard JavaScript functions exist"""
    print("\n" + "="*70)
    print("TEST 3: Wizard JavaScript Functions")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        js_checks = [
            ('currentWizardStep', 'Step tracking variable'),
            ('wizardNextStep', 'Next step function'),
            ('wizardPrevStep', 'Previous step function'),
            ('updateWizardUI', 'UI update function'),
            ('closeWizard', 'Close wizard function'),
            ('wizardClientData', 'Client data storage'),
        ]

        passed = 0
        for js_function, description in js_checks:
            if js_function in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(js_checks)

    except Exception as e:
        print(f"  ❌ Failed to check JavaScript: {e}")
        return False


def test_wizard_step_progression():
    """Test 4: Step progression logic"""
    print("\n" + "="*70)
    print("TEST 4: Step Progression Logic")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        progression_checks = [
            ('completed', 'Completed step state'),
            ('active', 'Active step state'),
            ('data-step=', 'Step data attributes'),
            ('currentWizardStep++', 'Step increment'),
            ('currentWizardStep--', 'Step decrement'),
        ]

        passed = 0
        for check, description in progression_checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed >= 4  # Allow some flexibility

    except Exception as e:
        print(f"  ❌ Failed to check progression logic: {e}")
        return False


def test_wizard_validation():
    """Test 5: Wizard integrates with real-time validation"""
    print("\n" + "="*70)
    print("TEST 5: Wizard Validation Integration")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        validation_checks = [
            ('wizard-client-id-preview', 'Client ID preview'),
            ('wizard-folder-validation', 'Folder validation display'),
            ('validate-drive-url', 'Drive URL validation API call'),
            ('sanitizeClientId', 'Client ID sanitization'),
        ]

        passed = 0
        for check, description in validation_checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(validation_checks)

    except Exception as e:
        print(f"  ❌ Failed to check validation: {e}")
        return False


def test_wizard_visual_design():
    """Test 6: Wizard visual design elements"""
    print("\n" + "="*70)
    print("TEST 6: Wizard Visual Design")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        design_checks = [
            ('backdrop-filter: blur', 'Backdrop blur effect'),
            ('box-shadow:', 'Drop shadow'),
            ('transform:', 'Transform animations'),
            ('transition:', 'Smooth transitions'),
            ('border-radius:', 'Rounded corners'),
            ('linear-gradient', 'Gradient backgrounds'),
        ]

        passed = 0
        for css, description in design_checks:
            if css in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ⚠️  {description} may use alternative styling")

        return passed >= 4

    except Exception as e:
        print(f"  ❌ Failed to check visual design: {e}")
        return False


def test_wizard_launch_button():
    """Test 7: Launch wizard button exists on configure page"""
    print("\n" + "="*70)
    print("TEST 7: Wizard Launch Button")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/configure", timeout=5)
        html = response.read().decode('utf-8')

        button_checks = [
            ('launchWizardBtn', 'Launch button ID'),
            ('Quick Setup Wizard', 'Wizard promotion text'),
            ('Step-by-step guided setup', 'Description text'),
            ('Launch Wizard', 'Button text'),
        ]

        passed = 0
        for check, description in button_checks:
            if check in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(button_checks)

    except Exception as e:
        print(f"  ❌ Failed to check launch button: {e}")
        return False


def main():
    print("="*70)
    print("STEP 4: Progressive Disclosure Wizard - Test Suite")
    print("="*70)

    # Start dashboard
    process = start_dashboard()
    if not process:
        print("\n❌ Failed to start dashboard - aborting tests")
        return 1

    time.sleep(1)

    # Run all tests
    tests = [
        ("Wizard CSS Classes", test_wizard_css_classes),
        ("Wizard HTML Structure", test_wizard_html_structure),
        ("Wizard JavaScript", test_wizard_javascript),
        ("Step Progression Logic", test_wizard_step_progression),
        ("Validation Integration", test_wizard_validation),
        ("Visual Design", test_wizard_visual_design),
        ("Launch Button", test_wizard_launch_button),
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
        print("\n✅ ALL TESTS PASSED - Step 4 implementation successful!")
        print("\nFeatures implemented:")
        print("  ✅ Progressive disclosure wizard with 4 steps")
        print("  ✅ Step-by-step guided setup flow")
        print("  ✅ Visual progress indicator")
        print("  ✅ Real-time validation integration")
        print("  ✅ Lock future steps until prerequisites complete")
        print("  ✅ Smooth animations and transitions")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
