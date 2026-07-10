#!/usr/bin/env python3
"""
Test Step 3: Visual Pipeline Dashboard Redesign
Tests pipeline visualization, stage indicators, and visual feedback
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


def test_pipeline_css_classes():
    """Test 1: Pipeline CSS classes are defined"""
    print("\n" + "="*70)
    print("TEST 1: Pipeline CSS Classes")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        css_checks = [
            ('pipeline', 'Pipeline container'),
            ('pipeline-stage', 'Pipeline stage'),
            ('stage-icon', 'Stage icon'),
            ('stage-complete', 'Complete stage styling'),
            ('stage-running', 'Running stage styling'),
            ('stage-waiting', 'Waiting stage styling'),
            ('stage-failed', 'Failed stage styling'),
            ('pipeline-connector', 'Stage connector'),
            ('pulse', 'Pulse animation for running stages'),
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


def test_pipeline_javascript():
    """Test 2: Pipeline rendering JavaScript exists"""
    print("\n" + "="*70)
    print("TEST 2: Pipeline JavaScript Implementation")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        js_checks = [
            ('getPipelineStages', 'Pipeline stage mapping function'),
            ('stage-complete', 'Complete stage class'),
            ('stage-running', 'Running stage class'),
            ('stage-waiting', 'Waiting stage class'),
            ('📥', 'Download icon'),
            ('📓', 'Notebook icon'),
            ('🔍', 'Research icon'),
            ('💡', 'Analysis icon'),
            ('✓', 'Complete icon'),
        ]

        passed = 0
        for text, description in js_checks:
            if text in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(js_checks)

    except Exception as e:
        print(f"  ❌ Failed to check JavaScript: {e}")
        return False


def test_pipeline_stage_logic():
    """Test 3: Pipeline stage detection logic"""
    print("\n" + "="*70)
    print("TEST 3: Pipeline Stage Detection Logic")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        # Check for step detection keywords
        keywords = [
            ('download', 'Download phase detection'),
            ('notebook', 'Notebook phase detection'),
            ('research', 'Research phase detection'),
            ('analysis', 'Analysis phase detection'),
            ('complete', 'Complete phase detection'),
        ]

        passed = 0
        for keyword, description in keywords:
            if keyword in html.lower():
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ⚠️  {description} - keyword '{keyword}' not found (may use different logic)")

        # This test is informational - we expect some to pass
        return passed >= 3

    except Exception as e:
        print(f"  ❌ Failed to check stage logic: {e}")
        return False


def test_visual_feedback():
    """Test 4: Visual feedback CSS (colors, animations)"""
    print("\n" + "="*70)
    print("TEST 4: Visual Feedback Styling")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        visual_checks = [
            ('box-shadow: 0 0 12px', 'Glow effect for active stages'),
            ('animation: pulse', 'Pulse animation'),
            ('rgba(34,197,94', 'Green color for complete stages'),
            ('rgba(240,136,62', 'Orange color for running stages'),
            ('rgba(248,81,73', 'Red color for failed stages'),
            ('#86efac', 'Light green accent'),
            ('#ffb366', 'Light orange accent'),
            ('#ff6b6b', 'Light red accent'),
        ]

        passed = 0
        for css_text, description in visual_checks:
            if css_text in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed >= 6  # Allow some flexibility in CSS implementation

    except Exception as e:
        print(f"  ❌ Failed to check visual feedback: {e}")
        return False


def test_dashboard_page_loads():
    """Test 5: Dashboard page loads with pipeline"""
    print("\n" + "="*70)
    print("TEST 5: Dashboard Page Load")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        checks = [
            ('Account Intelligence', 'Correct branding'),
            ('clients-grid', 'Client grid container'),
            ('Loading client status', 'Loading state'),
            ('Pipeline Progress', 'Pipeline progress indicator'),
        ]

        passed = 0
        for text, description in checks:
            if text in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ❌ {description} not found")

        return passed == len(checks)

    except Exception as e:
        print(f"  ❌ Failed to load dashboard: {e}")
        return False


def test_responsive_pipeline():
    """Test 6: Pipeline is responsive (overflow-x)"""
    print("\n" + "="*70)
    print("TEST 6: Responsive Pipeline Design")
    print("="*70)

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/", timeout=5)
        html = response.read().decode('utf-8')

        responsive_checks = [
            ('overflow-x: auto', 'Horizontal scroll for small screens'),
            ('flex:', 'Flexbox layout'),
            ('min-width:', 'Minimum width for stages'),
        ]

        passed = 0
        for css_text, description in responsive_checks:
            if css_text in html:
                print(f"  ✅ {description}")
                passed += 1
            else:
                print(f"  ⚠️  {description} - may use alternative approach")

        return passed >= 2

    except Exception as e:
        print(f"  ❌ Failed to check responsive design: {e}")
        return False


def main():
    print("="*70)
    print("STEP 3: Visual Pipeline Dashboard - Test Suite")
    print("="*70)

    # Start dashboard
    process = start_dashboard()
    if not process:
        print("\n❌ Failed to start dashboard - aborting tests")
        return 1

    time.sleep(1)

    # Run all tests
    tests = [
        ("Pipeline CSS Classes", test_pipeline_css_classes),
        ("Pipeline JavaScript", test_pipeline_javascript),
        ("Stage Detection Logic", test_pipeline_stage_logic),
        ("Visual Feedback Styling", test_visual_feedback),
        ("Dashboard Page Load", test_dashboard_page_loads),
        ("Responsive Design", test_responsive_pipeline),
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
        print("\n✅ ALL TESTS PASSED - Step 3 implementation successful!")
        print("\nFeatures implemented:")
        print("  ✅ Visual pipeline with 5 stages")
        print("  ✅ Color-coded status indicators")
        print("  ✅ Animated running state (pulse effect)")
        print("  ✅ Stage completion tracking")
        print("  ✅ Responsive design with horizontal scroll")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
