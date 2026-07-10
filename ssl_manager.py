#!/usr/bin/env python3
"""
SSL Certificate Manager
Automated SSL certificate generation and lifecycle management for Account Intelligence

This module provides:
- Automatic certificate generation with OpenSSL
- Certificate validity checking and expiration monitoring
- Smart auto-renewal (regenerate if <30 days remaining)
- Cross-platform support (Windows, macOS, Linux)
- Legacy configuration detection for backward compatibility

Usage:
    from ssl_manager import ensure_certificates

    certs_dir = Path("certs")
    if ensure_certificates(certs_dir):
        print("SSL certificates ready!")
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
from typing import Tuple
from datetime import datetime, timedelta


def check_openssl_available() -> Tuple[bool, str]:
    """
    Check if OpenSSL is installed and available in PATH.

    Returns:
        Tuple[bool, str]: (is_available, version_string or error_message)

    Example:
        >>> available, version = check_openssl_available()
        >>> if available:
        >>>     print(f"OpenSSL found: {version}")
    """
    try:
        result = subprocess.run(
            ["openssl", "version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        version = result.stdout.strip()
        return True, version
    except subprocess.CalledProcessError as e:
        return False, f"OpenSSL command failed: {e}"
    except FileNotFoundError:
        return False, "OpenSSL not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "OpenSSL command timed out"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_certificate_validity(cert_file: Path) -> Tuple[bool, int]:
    """
    Check if certificate is valid and calculate days until expiration.

    Args:
        cert_file: Path to certificate file (cert.pem)

    Returns:
        Tuple[bool, int]: (is_valid, days_remaining)
        - is_valid: False if missing, expired, or corrupted
        - days_remaining: -1 if invalid, else days until expiry

    Example:
        >>> valid, days = check_certificate_validity(Path("certs/cert.pem"))
        >>> if valid and days < 30:
        >>>     print(f"Certificate expires in {days} days - renewing...")
    """
    # Check if certificate file exists
    if not cert_file.exists():
        return False, -1

    # Check if file is readable and not empty
    try:
        file_size = cert_file.stat().st_size
        if file_size < 100:  # Valid cert should be at least a few hundred bytes
            return False, -1
    except Exception:
        return False, -1

    try:
        # Get certificate expiration date using openssl
        result = subprocess.run(
            ["openssl", "x509", "-in", str(cert_file), "-noout", "-enddate"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )

        # Parse output: "notAfter=Jul 10 15:11:26 2027 GMT"
        end_date_str = result.stdout.strip()
        if not end_date_str.startswith("notAfter="):
            return False, -1

        date_part = end_date_str.replace("notAfter=", "").strip()

        # Parse date (format: "Jul 10 15:11:26 2027 GMT")
        try:
            expiry_date = datetime.strptime(date_part, "%b %d %H:%M:%S %Y %Z")
        except ValueError:
            # Try alternate format without timezone
            expiry_date = datetime.strptime(date_part.replace(" GMT", ""), "%b %d %H:%M:%S %Y")

        # Calculate days remaining
        now = datetime.now()
        days_remaining = (expiry_date - now).days

        # Certificate is valid if not expired
        is_valid = days_remaining >= 0

        return is_valid, days_remaining

    except subprocess.CalledProcessError:
        # openssl command failed - certificate is corrupted
        return False, -1
    except Exception as e:
        # Any other error - treat as invalid
        print(f"   Warning: Could not check certificate validity: {e}")
        return False, -1


def generate_certificate(certs_dir: Path,
                        validity_days: int = 365,
                        force: bool = False) -> Tuple[bool, str]:
    """
    Generate self-signed SSL certificate using OpenSSL.

    Args:
        certs_dir: Directory to store certificate files
        validity_days: Certificate validity period in days (default 365)
        force: Regenerate even if valid certificate exists

    Returns:
        Tuple[bool, str]: (success, message)

    Example:
        >>> success, msg = generate_certificate(Path("certs"))
        >>> if success:
        >>>     print(f"Certificate generated: {msg}")
    """
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"

    # Check if certificates already exist and are valid (unless force=True)
    if not force and cert_file.exists() and key_file.exists():
        is_valid, days_remaining = check_certificate_validity(cert_file)
        if is_valid and days_remaining > 0:
            return True, f"Valid certificate already exists ({days_remaining} days remaining)"

    # Create certs directory if it doesn't exist
    try:
        certs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Failed to create certs directory: {e}"

    # Generate certificate using OpenSSL
    cmd = [
        "openssl", "req",
        "-x509",
        "-newkey", "rsa:4096",
        "-nodes",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", str(validity_days),
        "-subj", "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Certificate generation can take time
        )

        # Verify files were created
        if not cert_file.exists() or not key_file.exists():
            return False, "Certificate files not created (unknown error)"

        # Set proper file permissions
        set_certificate_permissions(cert_file, key_file)

        return True, f"Certificate generated successfully (valid for {validity_days} days)"

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return False, f"OpenSSL command failed: {error_msg}"
    except subprocess.TimeoutExpired:
        return False, "Certificate generation timed out (>30s)"
    except Exception as e:
        return False, f"Unexpected error during generation: {e}"


def set_certificate_permissions(cert_file: Path, key_file: Path):
    """
    Set secure permissions on certificate files.

    - cert.pem: 644 (world-readable, owner-writable)
    - key.pem: 600 (owner-only read/write)

    Note: Permissions only set on Unix-like systems (not Windows)

    Args:
        cert_file: Path to certificate file
        key_file: Path to private key file
    """
    # Skip permission setting on Windows
    if platform.system() == "Windows":
        return

    try:
        # Certificate: readable by all (644)
        os.chmod(cert_file, 0o644)

        # Private key: owner-only (600)
        os.chmod(key_file, 0o600)

    except Exception as e:
        # Don't fail if permissions can't be set, just warn
        print(f"   Warning: Could not set certificate permissions: {e}")


def ensure_certificates(certs_dir: Path,
                       renewal_threshold_days: int = 30) -> bool:
    """
    Ensure valid SSL certificates exist, auto-generating or renewing as needed.

    This is the main entry point for certificate management. It will:
    1. Create certs directory if missing
    2. Check if certificate files exist
    3. If missing: generate new certificates
    4. If exist: check validity and expiration
    5. If expired or <renewal_threshold days: regenerate
    6. Set proper file permissions

    Args:
        certs_dir: Directory containing certificate files
        renewal_threshold_days: Regenerate if expiring within this many days (default 30)

    Returns:
        bool: True if certificates are ready, False on error

    Example:
        >>> if ensure_certificates(Path("certs")):
        >>>     print("Certificates ready for use")
        >>> else:
        >>>     print("Failed to set up certificates")
    """
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"

    # Check if both certificate files exist
    if not cert_file.exists() or not key_file.exists():
        print(f"   SSL certificates not found, generating new...")
        success, message = generate_certificate(certs_dir)
        if success:
            print(f"   ✅ {message}")
            return True
        else:
            print(f"   ❌ {message}")
            return False

    # Check certificate validity and expiration
    is_valid, days_remaining = check_certificate_validity(cert_file)

    if not is_valid:
        print(f"   SSL certificate invalid or expired, regenerating...")
        success, message = generate_certificate(certs_dir, force=True)
        if success:
            print(f"   ✅ {message}")
            return True
        else:
            print(f"   ❌ {message}")
            return False

    # Check if certificate is expiring soon
    if days_remaining < renewal_threshold_days:
        print(f"   SSL certificate expiring in {days_remaining} days, regenerating...")
        success, message = generate_certificate(certs_dir, force=True)
        if success:
            print(f"   ✅ {message}")
            return True
        else:
            print(f"   ❌ {message}")
            return False

    # Certificate is valid and not expiring soon
    print(f"   SSL certificates valid ({days_remaining} days remaining)")
    return True


def check_legacy_ssl_config(vars_path: Path) -> Tuple[bool, str]:
    """
    Check for deprecated SSL_ENABLED configuration in vars.py.

    SSL_ENABLED is no longer used (SSL is always enabled). If detected with
    value=False, return a warning message for the user.

    Args:
        vars_path: Path to vars.py configuration file

    Returns:
        Tuple[bool, str]: (is_legacy, warning_message)
        - is_legacy: True if SSL_ENABLED=False detected
        - warning_message: User-facing deprecation warning or empty string

    Example:
        >>> is_legacy, warning = check_legacy_ssl_config(Path("vars.py"))
        >>> if is_legacy:
        >>>     print(warning)
    """
    if not vars_path.exists():
        return False, ""

    try:
        with open(vars_path, 'r') as f:
            content = f.read()

            # Check if SSL_ENABLED exists in file
            if 'SSL_ENABLED' not in content:
                return False, ""

            # Parse SSL_ENABLED value
            for line in content.split('\n'):
                line = line.strip()

                # Skip comments
                if line.startswith('#'):
                    continue

                # Check for SSL_ENABLED assignment
                if line.startswith('SSL_ENABLED') and '=' in line:
                    # Extract value after =
                    value_part = line.split('=', 1)[1].strip()

                    # Remove comments from value
                    if '#' in value_part:
                        value_part = value_part.split('#')[0].strip()

                    # Check if False
                    if value_part in ('False', 'false', '0', 'None'):
                        warning = (
                            "⚠️  WARNING: SSL_ENABLED=False detected in vars.py\n"
                            "   SSL is now always enabled for security (SSL_ENABLED is deprecated).\n"
                            "   Your configuration will be ignored - all communication uses HTTPS.\n"
                            "   \n"
                            "   You can safely remove SSL_ENABLED from vars.py.\n"
                        )
                        return True, warning
                    break

        return False, ""

    except Exception as e:
        # If we can't read the file, don't warn
        print(f"   Note: Could not check for legacy SSL configuration: {e}")
        return False, ""


def get_openssl_install_instructions() -> str:
    """
    Get platform-specific OpenSSL installation instructions.

    Returns:
        str: Installation instructions for current platform
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        return """
   Installation for macOS:

   Option 1: Homebrew (recommended)
     brew install openssl

   Option 2: MacPorts
     sudo port install openssl
"""

    elif system == "Linux":
        return """
   Installation for Linux:

   Debian/Ubuntu:
     sudo apt-get update
     sudo apt-get install openssl

   RHEL/Fedora/CentOS:
     sudo dnf install openssl

   Arch Linux:
     sudo pacman -S openssl
"""

    elif system == "Windows":
        return """
   Installation for Windows:

   Option 1: Git for Windows (recommended - includes OpenSSL)
     Download from: https://git-scm.com/download/win

   Option 2: Chocolatey
     choco install openssl

   Option 3: Direct download
     https://slproweb.com/products/Win32OpenSSL.html
"""

    else:
        return """
   Please install OpenSSL for your platform.
   Visit: https://www.openssl.org/
"""


if __name__ == "__main__":
    # Simple CLI for testing
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing SSL Manager...")
        print()

        # Test OpenSSL availability
        available, version = check_openssl_available()
        if available:
            print(f"✅ OpenSSL available: {version}")
        else:
            print(f"❌ OpenSSL not available: {version}")
            print(get_openssl_install_instructions())
            sys.exit(1)

        # Test certificate management
        test_dir = Path("certs")
        print(f"\nEnsuring certificates in {test_dir}...")
        if ensure_certificates(test_dir):
            print("✅ Certificates ready")
        else:
            print("❌ Certificate setup failed")
            sys.exit(1)

        # Check for legacy config
        vars_path = Path("vars.py")
        if vars_path.exists():
            is_legacy, warning = check_legacy_ssl_config(vars_path)
            if is_legacy:
                print(warning)

        print("\n✅ All tests passed")
    else:
        print("Usage: python3 ssl_manager.py test")
