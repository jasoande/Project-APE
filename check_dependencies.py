#!/usr/bin/env python3
"""
Dependency Verification Script
Checks that all Python dependencies are available via pip
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python 3.10+ is being used."""
    print("=" * 70)
    print("PYTHON VERSION CHECK")
    print("=" * 70)

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version >= (3, 10):
        print("✅ Python 3.10+ requirement met\n")
        return True
    else:
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}\n")
        return False


def check_imports():
    """Test that all required packages can be imported."""
    print("=" * 70)
    print("IMPORT CHECK")
    print("=" * 70)

    # Standard library modules (should always work)
    stdlib_modules = [
        'json', 'logging', 'pathlib', 'subprocess', 'time', 're', 'typing',
        'tempfile', 'random', 'multiprocessing', 'concurrent.futures', 'sys',
        'shutil', 'os'
    ]

    # Third-party packages from requirements.txt
    # Format: (import_name, package_name)
    third_party = [
        ('flask', 'flask'),
        ('pypdf', 'pypdf'),
        ('reportlab', 'reportlab'),
        ('PIL', 'Pillow'),
        ('docx', 'python-docx'),
        ('openpyxl', 'openpyxl'),
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('google.auth', 'google-auth'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('googleapiclient', 'google-api-python-client'),
    ]

    all_ok = True

    # Check standard library
    print("\nStandard Library:")
    for module in stdlib_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module} - {e}")
            all_ok = False

    # Check third-party packages
    print("\nThird-Party Packages:")
    missing = []
    for import_name, package_name in third_party:
        try:
            __import__(import_name)
            print(f"  ✅ {import_name} ({package_name})")
        except ImportError:
            print(f"  ❌ {import_name} (pip install {package_name})")
            missing.append(package_name)
            all_ok = False

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")

    print()
    return all_ok


def check_requirements_file():
    """Verify requirements.txt exists and is valid."""
    print("=" * 70)
    print("REQUIREMENTS.TXT CHECK")
    print("=" * 70)

    req_file = Path(__file__).parent / "requirements.txt"

    if not req_file.exists():
        print("❌ requirements.txt not found\n")
        return False

    print(f"✅ Found: {req_file}")

    # Count packages
    with open(req_file) as f:
        lines = [l.strip() for l in f.readlines()]
        packages = [l for l in lines if l and not l.startswith('#')]

    print(f"✅ Contains {len(packages)} package specifications")
    print()
    return True


def test_pip_install():
    """Test that requirements.txt can be used with pip."""
    print("=" * 70)
    print("PIP COMPATIBILITY CHECK")
    print("=" * 70)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ No dependency conflicts detected")
        else:
            print(f"⚠️  Dependency issues found:\n{result.stdout}")

        print()
        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running pip check: {e}\n")
        return False


def main():
    """Run all dependency checks."""
    print("\n" + "=" * 70)
    print("PROJECT APE - DEPENDENCY VERIFICATION")
    print("=" * 70 + "\n")

    checks = {
        "Python Version": check_python_version(),
        "Requirements File": check_requirements_file(),
        "Package Imports": check_imports(),
        "Pip Compatibility": test_pip_install(),
    }

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")

    all_passed = all(checks.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL DEPENDENCY CHECKS PASSED")
        print("=" * 70)
        print("\nYour environment is ready for Project APE!")
        print("\nTo install/update dependencies:")
        print("  pip install -r requirements.txt")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above before running Project APE.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")

    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
