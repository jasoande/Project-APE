#!/usr/bin/env python3
"""
Project APE - Setup Validation Script
======================================
Validates that the environment is correctly configured for Project APE.

Usage:
    python3 validate_setup.py
"""

import sys
import subprocess
import shutil
from pathlib import Path
import importlib.util

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_check(name, passed, details=""):
    """Print check result."""
    if passed:
        print(f"{Colors.GREEN}✓{Colors.RESET} {name}")
        if details:
            print(f"  {Colors.RESET}{details}{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} {name}")
        if details:
            print(f"  {Colors.YELLOW}{details}{Colors.RESET}")
    return passed

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    required = (3, 8)
    passed = version >= required

    details = f"Found: {version.major}.{version.minor}.{version.micro}"
    if not passed:
        details += f" (Required: {required[0]}.{required[1]}+)"

    return print_check("Python 3.8+", passed, details)

def check_system_command(cmd, name):
    """Check if system command is available."""
    found = shutil.which(cmd) is not None
    details = f"Command: {cmd}"
    if not found:
        details += " (Not found in PATH)"
    return print_check(name, found, details)

def check_python_package(package, display_name=None):
    """Check if Python package is installed."""
    if display_name is None:
        display_name = package

    try:
        spec = importlib.util.find_spec(package)
        found = spec is not None
        if found:
            # Try to get version
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                details = f"Version: {version}"
            except:
                details = "Installed"
        else:
            details = "Not installed - run: pip install -r requirements.txt"
        return print_check(display_name, found, details)
    except Exception as e:
        return print_check(display_name, False, f"Error checking: {e}")

def check_notebooklm_auth():
    """Check NotebookLM authentication."""
    try:
        result = subprocess.run(
            ["notebooklm", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            output = result.stdout.lower()
            authenticated = "not authenticated" not in output and "login" not in output

            if authenticated:
                # Try to extract email
                lines = result.stdout.split('\n')
                email_line = [l for l in lines if '@' in l]
                details = email_line[0].strip() if email_line else "Authenticated"
            else:
                details = "Not authenticated - run: notebooklm login"

            return print_check("NotebookLM Authentication", authenticated, details)
        else:
            return print_check("NotebookLM Authentication", False, "Unable to check - is notebooklm CLI installed?")
    except FileNotFoundError:
        return print_check("NotebookLM Authentication", False, "notebooklm command not found")
    except Exception as e:
        return print_check("NotebookLM Authentication", False, f"Error: {e}")

def check_directory_structure():
    """Check required directory structure."""
    script_dir = Path(__file__).parent

    required_dirs = [
        ("core", "Core modules directory"),
        ("dashboard", "Dashboard directory"),
    ]

    required_files = [
        ("main.py", "Main entry point"),
        ("vars.py", "Configuration file"),
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Documentation"),
    ]

    all_passed = True

    for dirname, description in required_dirs:
        path = script_dir / dirname
        passed = path.exists() and path.is_dir()
        all_passed &= print_check(f"Directory: {dirname}", passed, description)

    for filename, description in required_files:
        path = script_dir / filename
        passed = path.exists() and path.is_file()
        all_passed &= print_check(f"File: {filename}", passed, description)

    return all_passed

def check_vars_configuration():
    """Check vars.py configuration."""
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))

    try:
        spec = importlib.util.spec_from_file_location("config", script_dir / "vars.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)

        # Check for clients list
        has_clients = hasattr(config, 'clients') and len(config.clients) > 0
        if has_clients:
            details = f"Found {len(config.clients)} client(s): {', '.join(config.clients[:3])}"
            if len(config.clients) > 3:
                details += f" (+{len(config.clients) - 3} more)"
        else:
            details = "No clients configured - edit vars.py to add clients"

        return print_check("vars.py Configuration", has_clients, details)
    except Exception as e:
        return print_check("vars.py Configuration", False, f"Error loading: {e}")

def check_disk_space():
    """Check available disk space."""
    script_dir = Path(__file__).parent

    try:
        stat = shutil.disk_usage(script_dir)
        free_gb = stat.free / (1024**3)

        required_gb = 2.0
        passed = free_gb >= required_gb

        details = f"Available: {free_gb:.1f}GB"
        if not passed:
            details += f" (Required: {required_gb}GB)"

        return print_check("Disk Space", passed, details)
    except Exception as e:
        return print_check("Disk Space", False, f"Error checking: {e}")

def main():
    """Run all validation checks."""
    print(f"\n{Colors.BOLD}Project APE - Setup Validation{Colors.RESET}")
    print(f"Checking system configuration...\n")

    results = {}

    # System Requirements
    print_header("System Requirements")
    results['python'] = check_python_version()
    results['libreoffice'] = check_system_command("libreoffice", "LibreOffice")
    results['soffice'] = check_system_command("soffice", "LibreOffice (soffice)")
    results['disk'] = check_disk_space()

    # Python Packages
    print_header("Python Dependencies")
    results['notebooklm_pkg'] = check_python_package("notebooklm", "notebooklm-py")
    results['flask'] = check_python_package("flask", "Flask")
    results['pypdf'] = check_python_package("pypdf", "PyPDF")
    results['reportlab'] = check_python_package("reportlab", "ReportLab")
    results['pillow'] = check_python_package("PIL", "Pillow")
    results['docx'] = check_python_package("docx", "python-docx")
    results['openpyxl'] = check_python_package("openpyxl", "openpyxl")
    results['google_auth'] = check_python_package("google.auth", "google-auth")

    # NotebookLM
    print_header("NotebookLM Configuration")
    results['notebooklm_auth'] = check_notebooklm_auth()

    # Project Structure
    print_header("Project Structure")
    results['structure'] = check_directory_structure()
    results['config'] = check_vars_configuration()

    # Summary
    print_header("Summary")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"Total Checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! You're ready to run Project APE.{Colors.RESET}")
        print(f"\nNext steps:")
        print(f"  1. Configure your clients in vars.py")
        print(f"  2. Run: python3 main.py --mode fast --clients your_client")
        print(f"  3. Monitor at: http://localhost:8765\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some checks failed. Please fix the issues above.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Common fixes:{Colors.RESET}")

        if not results.get('libreoffice') or not results.get('soffice'):
            print(f"  • LibreOffice: brew install --cask libreoffice (macOS)")
            print(f"                 sudo apt-get install libreoffice (Linux)")

        if not results.get('notebooklm_pkg'):
            print(f"  • Python packages: pip install -r requirements.txt")

        if not results.get('notebooklm_auth'):
            print(f"  • NotebookLM auth: notebooklm login")

        if not results.get('config'):
            print(f"  • Configuration: Edit vars.py to add clients")

        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
