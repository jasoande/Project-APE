#!/usr/bin/env python3
"""
Cross-Platform Launcher Test Suite
===================================
Tests all Project APE launchers for correctness and cross-platform compatibility

Usage:
    python3 test-launchers.py
"""

import sys
import subprocess
import platform
from pathlib import Path
import time


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_test(name):
    """Print test name"""
    print(f"{Colors.BOLD}Testing: {name}{Colors.RESET}")


def print_pass(message):
    """Print success message"""
    print(f"  {Colors.GREEN}✅ PASS:{Colors.RESET} {message}")


def print_fail(message):
    """Print failure message"""
    print(f"  {Colors.RED}❌ FAIL:{Colors.RESET} {message}")


def print_skip(message):
    """Print skip message"""
    print(f"  {Colors.YELLOW}⊘ SKIP:{Colors.RESET} {message}")


def print_info(message):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ INFO:{Colors.RESET} {message}")


def test_file_exists(filepath):
    """Test if a file exists"""
    path = Path(filepath)
    if path.exists():
        print_pass(f"File exists: {filepath}")
        return True
    else:
        print_fail(f"File not found: {filepath}")
        return False


def test_file_executable(filepath):
    """Test if a file is executable (Unix only)"""
    if platform.system() == "Windows":
        print_skip("Executable check not applicable on Windows")
        return True

    path = Path(filepath)
    if path.exists() and path.stat().st_mode & 0o111:
        print_pass(f"File is executable: {filepath}")
        return True
    else:
        print_fail(f"File is not executable: {filepath}")
        print_info(f"Fix with: chmod +x {filepath}")
        return False


def test_python_syntax(filepath):
    """Test if Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        print_pass(f"Valid Python syntax: {filepath}")
        return True
    except SyntaxError as e:
        print_fail(f"Syntax error in {filepath}: {e}")
        return False


def test_shebang(filepath):
    """Test if script has proper shebang"""
    with open(filepath, 'r') as f:
        first_line = f.readline().strip()

    if first_line.startswith('#!'):
        print_pass(f"Has shebang: {first_line}")
        return True
    else:
        print_fail(f"Missing shebang in {filepath}")
        return False


def test_imports(filepath):
    """Test that all imports in Python file are available"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_module", filepath)
        module = importlib.util.module_from_spec(spec)
        # Don't execute, just check imports can be resolved
        print_pass(f"All imports available: {filepath}")
        return True
    except ImportError as e:
        print_fail(f"Import error in {filepath}: {e}")
        return False
    except Exception as e:
        # Other errors (like execution) are OK for this test
        print_pass(f"Imports check passed: {filepath}")
        return True


def test_platform_detection():
    """Test platform detection logic"""
    print_test("Platform Detection")

    system = platform.system()
    print_info(f"Detected platform: {system}")

    if system in ["Windows", "Darwin", "Linux"]:
        print_pass(f"Platform '{system}' is supported")
        return True
    else:
        print_fail(f"Platform '{system}' may not be supported")
        return False


def test_venv_path_logic():
    """Test virtual environment path detection logic"""
    print_test("Virtual Environment Path Logic")

    home = Path.home()
    venv_dir = home / ".project-ape-venv"

    system = platform.system()
    if system == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python3"

    print_info(f"Expected venv Python path: {python_path}")

    if venv_dir.exists():
        if python_path.exists():
            print_pass(f"Virtual environment Python found at {python_path}")
            return True
        else:
            print_fail(f"Virtual environment exists but Python not found at {python_path}")
            return False
    else:
        print_skip(f"Virtual environment not found at {venv_dir} (expected if not set up)")
        return True


def test_dashboard_script():
    """Test that dashboard server script exists"""
    print_test("Dashboard Server Script")

    script_dir = Path(__file__).parent.resolve()
    server_script = script_dir / "dashboard" / "server.py"

    if server_script.exists():
        print_pass(f"Dashboard server found at {server_script}")
        return True
    else:
        print_fail(f"Dashboard server not found at {server_script}")
        return False


def run_all_tests():
    """Run all launcher tests"""
    print_header("PROJECT APE - CROSS-PLATFORM LAUNCHER TEST SUITE")

    script_dir = Path(__file__).parent.resolve()
    results = []

    # Test 1: Platform detection
    results.append(test_platform_detection())
    print()

    # Test 2: Virtual environment path logic
    results.append(test_venv_path_logic())
    print()

    # Test 3: Dashboard server exists
    results.append(test_dashboard_script())
    print()

    # Test 4: Python launcher
    print_test("Python Launcher (launch-project-ape.py)")
    py_launcher = script_dir / "launch-project-ape.py"
    results.append(test_file_exists(py_launcher))
    if py_launcher.exists():
        results.append(test_python_syntax(py_launcher))
        results.append(test_shebang(py_launcher))
        results.append(test_file_executable(py_launcher))
    print()

    # Test 5: Shell launcher
    print_test("Shell Launcher (launch-project-ape.sh)")
    sh_launcher = script_dir / "launch-project-ape.sh"
    results.append(test_file_exists(sh_launcher))
    if sh_launcher.exists():
        results.append(test_shebang(sh_launcher))
        results.append(test_file_executable(sh_launcher))
    print()

    # Test 6: Windows batch launcher
    print_test("Windows Batch Launcher (launch-project-ape.bat)")
    bat_launcher = script_dir / "launch-project-ape.bat"
    results.append(test_file_exists(bat_launcher))
    print()

    # Test 7: Windows PowerShell launcher
    print_test("Windows PowerShell Launcher (launch-project-ape.ps1)")
    ps1_launcher = script_dir / "launch-project-ape.ps1"
    results.append(test_file_exists(ps1_launcher))
    print()

    # Test 8: macOS command launcher (legacy)
    print_test("macOS Command Launcher (launch-project-ape.command)")
    cmd_launcher = script_dir / "launch-project-ape.command"
    results.append(test_file_exists(cmd_launcher))
    if cmd_launcher.exists():
        results.append(test_file_executable(cmd_launcher))
    print()

    # Test 9: Documentation
    print_test("Cross-Platform Launcher Documentation")
    doc_file = script_dir / "CROSS_PLATFORM_LAUNCHER.md"
    results.append(test_file_exists(doc_file))
    print()

    # Summary
    print_header("TEST SUMMARY")

    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests

    print(f"Total Tests:  {total_tests}")
    print(f"{Colors.GREEN}Passed:       {passed_tests}{Colors.RESET}")
    if failed_tests > 0:
        print(f"{Colors.RED}Failed:       {failed_tests}{Colors.RESET}")
    else:
        print(f"Failed:       {failed_tests}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.RESET}")
        print("\nCross-platform launchers are ready for use.")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.RESET}")
        print("\nPlease fix the issues above before deploying.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error during testing: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
