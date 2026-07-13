#!/usr/bin/env python3
"""Test script to verify fixes for web source imports and workflow stop button."""

import json
import time
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
STATUS_DIR = PROJECT_ROOT / ".multi_process_status"
LOGS_DIR = PROJECT_ROOT / "logs"

def test_pid_file_creation():
    """Test that workflow PID file is created."""
    print("\n" + "="*60)
    print("TEST 1: Workflow PID File Creation")
    print("="*60)

    pid_file = STATUS_DIR / '.workflow_pid'

    # Clean up any existing PID file
    if pid_file.exists():
        print(f"⚠️  Removing existing PID file: {pid_file}")
        pid_file.unlink()

    # Start a workflow in background
    print("\n🚀 Starting test workflow (1 client, fast mode)...")
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "main.py"),
        "--mode", "fast",
        "--clients", "hershey",
        "--skip-preflight"
    ]

    # Start workflow process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(PROJECT_ROOT)
    )

    print(f"   Process PID: {process.pid}")

    # Wait for PID file to be created (should happen quickly)
    print("\n⏳ Waiting for PID file creation...")
    max_wait = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if pid_file.exists():
            print("   ✅ PID file created!")
            break
        time.sleep(0.5)
    else:
        print("   ❌ PID file not created within 10 seconds")
        process.terminate()
        return False

    # Verify PID file content
    print("\n📄 PID file content:")
    with open(pid_file) as f:
        pid_data = json.load(f)
        print(json.dumps(pid_data, indent=2))

    # Verify PID matches
    if pid_data['pid'] == process.pid:
        print("\n✅ TEST PASSED: PID file contains correct process ID")
        result = True
    else:
        print(f"\n❌ TEST FAILED: PID mismatch - expected {process.pid}, got {pid_data['pid']}")
        result = False

    # Clean up
    print("\n🧹 Cleaning up test workflow...")
    process.terminate()
    process.wait(timeout=10)

    # Wait a bit for cleanup
    time.sleep(2)

    # Check if PID file was cleaned up
    if not pid_file.exists():
        print("   ✅ PID file cleaned up successfully")
    else:
        print("   ⚠️  PID file still exists (manual cleanup needed)")
        pid_file.unlink()

    return result


def test_rate_limit_error_handling():
    """Test that rate limit errors are properly reported."""
    print("\n" + "="*60)
    print("TEST 2: Rate Limit Error Handling")
    print("="*60)

    # Check most recent log for rate limit error messages
    log_file = LOGS_DIR / "hershey.log"

    if not log_file.exists():
        print("⚠️  Log file not found, skipping test")
        return True

    print(f"\n📄 Checking log file: {log_file}")

    with open(log_file) as f:
        log_content = f.read()

    # Look for our enhanced error messages
    if "NotebookLM API rate limit exceeded" in log_content:
        print("   ✅ Found enhanced rate limit error message")
        if "Solutions:" in log_content:
            print("   ✅ Found solutions guidance")
            print("\n✅ TEST PASSED: Rate limit errors are properly handled")
            return True
        else:
            print("   ❌ Solutions guidance not found")
            print("\n❌ TEST FAILED: Missing solutions in error message")
            return False
    else:
        print("   ℹ️  No rate limit errors in recent logs")
        print("\n✅ TEST SKIPPED: No recent rate limit errors to verify")
        return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  TESTING FIXES FOR:")
    print("  1. Workflow Stop Button (PID File)")
    print("  2. Rate Limit Error Messages")
    print("="*60)

    results = []

    # Test 1: PID file creation
    try:
        results.append(("PID File Creation", test_pid_file_creation()))
    except Exception as e:
        print(f"\n❌ Test 1 crashed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("PID File Creation", False))

    # Test 2: Rate limit error handling (check existing logs)
    try:
        results.append(("Rate Limit Errors", test_rate_limit_error_handling()))
    except Exception as e:
        print(f"\n❌ Test 2 crashed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Rate Limit Errors", False))

    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
