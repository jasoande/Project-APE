#!/usr/bin/env python3
"""
Local SSL Certificate Setup Script
Generates self-signed SSL certificates for local HTTPS development

Cross-platform: Works on Windows, macOS, and Linux

Usage:
    python3 setup-ssl-local.py

    or on Windows:
    python setup-ssl-local.py

What it does:
    1. Creates certs/ directory
    2. Generates 4096-bit RSA self-signed certificate (valid 1 year)
    3. Verifies certificate files
    4. Shows certificate details
    5. Provides next steps
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta


def print_header(title):
    """Print formatted header"""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def print_step(emoji, message):
    """Print formatted step"""
    print(f"{emoji} {message}")


def check_openssl():
    """Check if openssl is available"""
    try:
        result = subprocess.run(
            ["openssl", "version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def create_certs_directory():
    """Create certs/ directory if it doesn't exist"""
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    return certs_dir


def generate_certificate(certs_dir):
    """Generate self-signed SSL certificate"""
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"

    # OpenSSL command
    cmd = [
        "openssl", "req",
        "-x509",
        "-newkey", "rsa:4096",
        "-nodes",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-days", "365",
        "-subj", "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"
    ]

    try:
        # Run openssl command, suppress verbose output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, cert_file, key_file
    except subprocess.CalledProcessError as e:
        return False, str(e), None


def set_file_permissions(cert_file, key_file):
    """Set appropriate file permissions (Unix only)"""
    if platform.system() != "Windows":
        try:
            # Key: owner read/write only (600)
            os.chmod(key_file, 0o600)
            # Cert: world-readable (644)
            os.chmod(cert_file, 0o644)
            return True
        except Exception as e:
            print(f"   ⚠️  Warning: Could not set permissions: {e}")
            return False
    return True


def get_file_size(filepath):
    """Get human-readable file size"""
    size_bytes = filepath.stat().st_size
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_certificate_info(cert_file):
    """Get certificate subject and dates"""
    try:
        # Get subject
        result = subprocess.run(
            ["openssl", "x509", "-in", str(cert_file), "-noout", "-subject"],
            capture_output=True,
            text=True,
            check=True
        )
        subject = result.stdout.strip().replace("subject=", "")

        # Get dates
        result = subprocess.run(
            ["openssl", "x509", "-in", str(cert_file), "-noout", "-dates"],
            capture_output=True,
            text=True,
            check=True
        )
        dates = result.stdout.strip().split('\n')
        valid_from = dates[0].replace("notBefore=", "")
        valid_until = dates[1].replace("notAfter=", "")

        return subject, valid_from, valid_until
    except Exception as e:
        return None, None, None


def check_vars_py():
    """Check if vars.py exists and SSL is configured"""
    vars_path = Path("vars.py")

    if not vars_path.exists():
        return False, "vars.py not found"

    try:
        with open(vars_path, 'r') as f:
            content = f.read()
            if 'SSL_ENABLED' in content and 'True' in content:
                # Check more precisely
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('SSL_ENABLED') and '=' in line:
                        value = line.split('=')[1].strip()
                        if value in ('True', 'true', '1'):
                            return True, "SSL already enabled"
        return False, "SSL not enabled"
    except Exception as e:
        return False, f"Error reading vars.py: {e}"


def main():
    """Main script logic"""
    print_header("Local SSL Certificate Setup")

    # Step 1: Check for OpenSSL
    print_step("🔍", "Checking for OpenSSL...")
    openssl_available, openssl_version = check_openssl()

    if not openssl_available:
        print("   ❌ OpenSSL not found")
        print()
        print("   OpenSSL is required to generate SSL certificates.")
        print()
        if platform.system() == "Windows":
            print("   Installation options:")
            print("   1. Install Git for Windows (includes OpenSSL)")
            print("      https://git-scm.com/download/win")
            print("   2. Install OpenSSL via Chocolatey:")
            print("      choco install openssl")
            print("   3. Download from: https://slproweb.com/products/Win32OpenSSL.html")
        elif platform.system() == "Darwin":
            print("   Install via Homebrew:")
            print("      brew install openssl")
        else:  # Linux
            print("   Install via package manager:")
            print("      sudo apt-get install openssl    # Debian/Ubuntu")
            print("      sudo dnf install openssl         # RHEL/Fedora")
        print()
        sys.exit(1)

    print(f"   ✅ OpenSSL found: {openssl_version}")
    print()

    # Step 2: Create directory
    print_step("📁", "Creating certs directory...")
    certs_dir = create_certs_directory()
    print(f"   ✅ Directory created: {certs_dir}/")
    print()

    # Step 3: Generate certificate
    print_step("🔐", "Generating self-signed SSL certificate...")
    print("   Key size: 4096-bit RSA")
    print("   Validity: 365 days (1 year)")
    print("   Common Name: localhost")
    print()

    success, cert_or_error, key_file = generate_certificate(certs_dir)

    if not success:
        print(f"   ❌ Certificate generation failed: {cert_or_error}")
        sys.exit(1)

    cert_file = cert_or_error
    print("   ✅ Certificate generated successfully")
    print()

    # Step 4: Set permissions
    print_step("🔒", "Setting file permissions...")
    set_file_permissions(cert_file, key_file)

    if platform.system() == "Windows":
        print("   ℹ️  On Windows, use file properties to restrict access")
    else:
        print("   ✅ Permissions set (key: 600, cert: 644)")
    print()

    # Step 5: Verify files
    print_step("📋", "Certificate files:")
    print(f"   {cert_file.name} ({get_file_size(cert_file)})")
    print(f"   {key_file.name} ({get_file_size(key_file)})")
    print()

    # Step 6: Show certificate details
    print_step("📜", "Certificate details:")
    subject, valid_from, valid_until = get_certificate_info(cert_file)

    if subject:
        print(f"   Subject: {subject}")
        print(f"   Valid from: {valid_from}")
        print(f"   Valid until: {valid_until}")
    else:
        print("   ⚠️  Could not read certificate details")
    print()

    # Step 7: Check vars.py
    print_step("⚙️", "Checking vars.py configuration...")
    ssl_configured, message = check_vars_py()

    if ssl_configured:
        print(f"   ✅ {message}")
    else:
        print(f"   ⚠️  {message}")
        print()
        print("   Add these lines to vars.py:")
        print()
        print("   # SSL/HTTPS Configuration")
        print("   SSL_ENABLED = True")
        print('   SSL_CERT_PATH = "certs/cert.pem"')
        print('   SSL_KEY_PATH = "certs/key.pem"')
    print()

    # Success summary
    print_header("✅ SSL Setup Complete!")

    print("Next steps:")
    print()
    print("1. Enable SSL in vars.py (if not already done):")
    print("   SSL_ENABLED = True")
    print('   SSL_CERT_PATH = "certs/cert.pem"')
    print('   SSL_KEY_PATH = "certs/key.pem"')
    print()
    print("2. Start the dashboard:")
    if platform.system() == "Windows":
        print("   python launch-project-ape.py")
    else:
        print("   python3 launch-project-ape.py")
        print("   (or double-click launch-project-ape.command on macOS)")
    print()
    print("3. Access dashboard:")
    print("   https://localhost:8765/configure")
    print()
    print("4. Accept browser security warning:")
    print("   Click 'Advanced' → 'Proceed to localhost'")
    print("   (Normal for self-signed certificates)")
    print()
    print("📚 For detailed documentation, see:")
    print("   Docs/SSL_SETUP_LOCAL.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
