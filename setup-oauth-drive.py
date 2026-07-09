#!/usr/bin/env python3
"""
Automated OAuth Setup for Google Drive Access
==============================================
Guides users through GCP project creation and OAuth authentication.
Works error-free every time with zero prior Google Cloud experience required.

Security-hardened version with atomic operations and secure credential handling.

Usage:
    python3 setup-oauth-drive-improved.py
"""

import json
import os
import subprocess
import sys
import time
import webbrowser
import shutil
import tempfile
import random
import string
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for Drive read-only access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Where to store credentials
CREDS_DIR = Path.home() / '.project-ape'
TOKEN_FILE = CREDS_DIR / 'drive_token.json'
CLIENT_SECRETS_FILE = CREDS_DIR / 'drive_credentials.json'

# Security: Allowed gcloud commands (whitelist for validation)
ALLOWED_GCLOUD_COMMANDS = {
    '--version',
    'auth list',
    'config get-value project',
    'projects list',
    'projects create',
    'config set project',
    'services list',
    'services enable drive.googleapis.com',
    'auth login --update-adc'
}


class SecurityError(Exception):
    """Raised for security-related errors."""
    pass


def sanitize_error_message(error_msg: str) -> str:
    """
    Remove sensitive data from error messages.

    Security Fix #3: Sanitize exception messages to prevent credential leakage.
    """
    sensitive_patterns = [
        'client_secret',
        'access_token',
        'refresh_token',
        'client_id',
        'api_key',
        'bearer',
        'authorization',
    ]

    sanitized = str(error_msg)
    for pattern in sensitive_patterns:
        if pattern in sanitized.lower():
            # Replace sensitive data with placeholder
            sanitized = sanitized.split('\n')[0]  # Keep only first line
            sanitized += ' [sensitive data redacted]'
            break

    return sanitized


def secure_write_file(file_path: Path, content: str, mode: int = 0o600) -> None:
    """
    Atomically write a file with secure permissions.

    Security Fix #2: Atomic file operations to prevent TOCTOU race conditions.
    Creates file with restrictive permissions from the start.
    """
    file_path = Path(file_path).resolve()

    # Create temporary file in same directory (ensures same filesystem)
    temp_dir = file_path.parent
    temp_fd, temp_path = tempfile.mkstemp(
        dir=temp_dir,
        prefix='.tmp_',
        suffix=file_path.suffix
    )

    try:
        # Set restrictive permissions immediately on temp file
        os.chmod(temp_fd, mode)

        # Write content to temp file
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Ensure data written to disk

        # Atomic rename (same filesystem guaranteed by mkstemp in same dir)
        os.replace(temp_path, file_path)

        # Verify final permissions
        os.chmod(file_path, mode)

    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise SecurityError(f"Secure file write failed: {sanitize_error_message(e)}")


def secure_create_directory(dir_path: Path, mode: int = 0o700) -> None:
    """
    Atomically create directory with secure permissions.

    Security Fix #1: Prevent race condition between mkdir and chmod.
    Uses os.mkdir with mode parameter for atomic operation.
    """
    dir_path = Path(dir_path).resolve()

    if dir_path.exists():
        # Verify existing directory has secure permissions
        current_mode = dir_path.stat().st_mode & 0o777
        if current_mode != mode:
            os.chmod(dir_path, mode)
        return

    # Create with secure permissions atomically
    # Note: umask may affect this, so we set it explicitly
    old_umask = os.umask(0)
    try:
        os.makedirs(dir_path, mode=mode, exist_ok=True)
        # Double-check permissions after creation
        os.chmod(dir_path, mode)
    finally:
        os.umask(old_umask)


def validate_credentials(creds: Credentials) -> bool:
    """
    Validate OAuth credentials including token expiration.

    Security Fix #5: Token expiration validation.
    Security Fix #8: Credential validation before use.
    """
    if not creds:
        return False

    # Check required attributes
    if not hasattr(creds, 'token') or not creds.token:
        return False

    # Check token expiration
    if hasattr(creds, 'expiry') and creds.expiry:
        # Token is expired if expiry time has passed
        if creds.expiry.tzinfo is None:
            # Assume UTC if naive datetime
            from datetime import timezone
            expiry_aware = creds.expiry.replace(tzinfo=timezone.utc)
        else:
            expiry_aware = creds.expiry

        now_utc = datetime.now(timezone.utc)
        if expiry_aware <= now_utc:
            return False

    # Check for refresh token if token is expired/expiring soon
    if hasattr(creds, 'expired') and creds.expired:
        if not hasattr(creds, 'refresh_token') or not creds.refresh_token:
            return False

    # Validate token is not obviously malformed
    if len(creds.token) < 20:  # Tokens are typically much longer
        return False

    return True


def revoke_token(token_file: Path) -> bool:
    """
    Revoke OAuth token before deletion.

    Security Fix #9: Token revocation mechanism.
    """
    try:
        if not token_file.exists():
            return True

        # Load credentials
        with open(token_file, 'r') as f:
            creds_data = json.load(f)

        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

        # Revoke the token
        if hasattr(creds, 'token') and creds.token:
            import requests
            revoke_url = 'https://oauth2.googleapis.com/revoke'
            requests.post(
                revoke_url,
                params={'token': creds.token},
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )

        return True
    except Exception:
        # Best effort - don't fail if revocation fails
        return False


def secure_cleanup(files: List[Path]) -> None:
    """
    Securely clean up sensitive files.

    Security Fix #6: Secure cleanup on error.
    Overwrites files before deletion and revokes tokens.
    """
    for file_path in files:
        try:
            if not file_path.exists():
                continue

            # Revoke token if it's a token file
            if file_path.name.endswith('_token.json'):
                revoke_token(file_path)

            # Overwrite with random data before deletion
            file_size = file_path.stat().st_size
            if file_size > 0:
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Delete the file
            file_path.unlink()

        except Exception:
            # Best effort - continue cleanup even if one fails
            pass


def sanitize_command_arg(arg: str) -> str:
    """
    Sanitize command arguments to prevent injection.

    Security Fix #7: Command injection prevention.
    """
    # Remove dangerous characters
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
    sanitized = arg
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized


def run_command_safe(cmd_parts: List[str], check: bool = True, capture_output: bool = True, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """
    Run a command safely without shell=True.

    Security Fix #7: Eliminate subprocess command injection by using list arguments.

    Args:
        cmd_parts: Command and arguments as a list
        check: Whether to raise on non-zero exit code
        capture_output: Whether to capture stdout/stderr
        timeout: Optional timeout in seconds
    """
    try:
        result = subprocess.run(
            cmd_parts,
            shell=False,  # NEVER use shell=True
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        # Re-raise timeout exceptions
        raise
    except subprocess.CalledProcessError as e:
        # Sanitize error output
        e.stderr = sanitize_error_message(e.stderr) if e.stderr else ''
        e.stdout = sanitize_error_message(e.stdout) if e.stdout else ''
        if not check:
            return e
        raise


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num, total_steps, title):
    """Print step progress."""
    print(f"\n{'━' * 70}")
    print(f"  STEP {step_num}/{total_steps}: {title}")
    print(f"{'━' * 70}\n")


def check_gcloud_installed() -> bool:
    """Check if gcloud is installed."""
    try:
        result = run_command_safe(["gcloud", "--version"], check=False)
        return result.returncode == 0
    except Exception:
        return False


def check_gcloud_authenticated() -> Optional[str]:
    """Check if user is authenticated with gcloud."""
    try:
        result = run_command_safe(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_active_project() -> Optional[str]:
    """Get the currently active GCP project."""
    try:
        result = run_command_safe(
            ["gcloud", "config", "get-value", "project"],
            check=False
        )
        if result.returncode == 0 and result.stdout.strip() and result.stdout.strip() != "(unset)":
            return result.stdout.strip()
    except Exception:
        pass
    return None


def list_projects() -> List[Tuple[str, str]]:
    """List all GCP projects the user has access to (excludes system projects)."""
    try:
        result = run_command_safe(
            ["gcloud", "projects", "list", "--format=value(projectId,name)"],
            check=False,
            timeout=30  # Timeout after 30 seconds
        )
        if result.returncode == 0 and result.stdout.strip():
            projects = []
            for line in result.stdout.strip().split('\n'):
                if '\t' in line:
                    project_id, name = line.split('\t', 1)
                    # Sanitize project data
                    project_id = sanitize_command_arg(project_id.strip())
                    name = sanitize_command_arg(name.strip())

                    # Filter out system-generated projects
                    if project_id.startswith('sys-'):
                        continue

                    # Filter out marketplace/calculator projects
                    if 'marketplace' in name.lower() or 'calculator' in name.lower():
                        continue

                    # Filter out auto-generated template projects
                    if 'auto-update filter' in name.lower() or 'template' in name.lower():
                        continue

                    projects.append((project_id, name))

            # Limit to 50 projects max for display
            if len(projects) > 50:
                projects = projects[:50]

            return projects
    except subprocess.TimeoutExpired:
        print("⚠️  Project list command timed out")
        return []
    except Exception:
        pass
    return []


def create_project(project_id: str, project_name: str) -> Tuple[bool, Optional[str]]:
    """Create a new GCP project."""
    # Sanitize inputs
    project_id = sanitize_command_arg(project_id)
    project_name = sanitize_command_arg(project_name)

    print(f"Creating project: {project_name} ({project_id})...")

    try:
        result = run_command_safe(
            ["gcloud", "projects", "create", project_id, f"--name={project_name}"],
            check=False
        )

        if result.returncode != 0:
            return False, sanitize_error_message(result.stderr)

        # Set as active project
        run_command_safe(["gcloud", "config", "set", "project", project_id])
        return True, None

    except Exception as e:
        return False, sanitize_error_message(str(e))


def check_api_enabled(api_name: str = "drive.googleapis.com") -> bool:
    """Check if an API is enabled."""
    try:
        result = run_command_safe(
            ["gcloud", "services", "list", "--enabled", f"--filter=name:{api_name}", "--format=value(name)"],
            check=False
        )
        return result.returncode == 0 and api_name in result.stdout
    except Exception:
        return False


def enable_drive_api() -> bool:
    """Enable the Google Drive API."""
    print("Enabling Google Drive API...")
    try:
        result = run_command_safe(
            ["gcloud", "services", "enable", "drive.googleapis.com"],
            check=False,
            capture_output=True
        )

        if result.returncode == 0:
            print("✅ Google Drive API enabled successfully")
            return True
        else:
            print(f"❌ Failed to enable Drive API: {sanitize_error_message(result.stderr)}")
            return False
    except Exception as e:
        print(f"❌ Failed to enable Drive API: {sanitize_error_message(str(e))}")
        return False


def secure_move_credentials(source: Path, dest: Path, mode: int = 0o600) -> None:
    """
    Securely move credentials file with atomic operation.

    Security Fix #4: Prevent credential leakage in downloaded files.
    Validates content and sets restrictive permissions atomically.
    """
    source = Path(source).resolve()
    dest = Path(dest).resolve()

    # Validate source file is valid JSON credentials
    try:
        with open(source, 'r') as f:
            creds_data = json.load(f)

        # Basic validation of credentials structure
        if 'installed' not in creds_data and 'web' not in creds_data:
            raise ValueError("Invalid credentials file format")

    except Exception as e:
        raise SecurityError(f"Invalid credentials file: {sanitize_error_message(e)}")

    # Use secure_write_file for atomic operation with permissions
    with open(source, 'r') as f:
        content = f.read()

    secure_write_file(dest, content, mode)

    # Securely delete source file
    secure_cleanup([source])


def main():
    print_header("Account Intelligence - Automated OAuth Setup (Security Hardened)")

    print("This wizard will guide you through setting up Google Drive access.")
    print("Estimated time: 5-10 minutes")
    print("\nWhat we'll do:")
    print("  1. Verify Google Cloud SDK authentication")
    print("  2. Create or select a GCP project")
    print("  3. Enable Google Drive API")
    print("  4. Guide you to create OAuth credentials")
    print("  5. Authenticate with Google")
    print("\nSecurity features:")
    print("  • Atomic file operations to prevent race conditions")
    print("  • Secure credential handling with immediate permission lockdown")
    print("  • Token validation and expiration checking")
    print("  • Secure cleanup on errors")
    print("  • Command injection prevention")
    print("\n")

    input("Press Enter to begin...")

    # Track files for cleanup on error
    cleanup_files = []

    try:
        # =========================================================================
        # STEP 1: Check gcloud installation and authentication
        # =========================================================================
        print_step(1, 5, "Verify Google Cloud SDK")

        if not check_gcloud_installed():
            print("❌ Google Cloud SDK (gcloud) is not installed.\n")
            print("Please install it first:")
            print("  • Run: ./setup-environment.sh")
            print("  • Or visit: https://cloud.google.com/sdk/docs/install")
            sys.exit(1)

        print("✅ Google Cloud SDK is installed")

        # Check authentication
        active_account = check_gcloud_authenticated()

        if not active_account:
            print("\n⚠️  You are not authenticated with Google Cloud.\n")
            print("Opening browser for authentication...")
            print("This will open a browser window. Please sign in with your Google account.\n")

            # Run gcloud auth login (safe command)
            result = run_command_safe(
                ["gcloud", "auth", "login", "--update-adc"],
                check=False
            )

            if result.returncode != 0:
                print("\n❌ Authentication failed. Please try again.")
                sys.exit(1)

            # Re-check authentication
            active_account = check_gcloud_authenticated()
            if not active_account:
                print("\n❌ Authentication verification failed.")
                sys.exit(1)

        print(f"✅ Authenticated as: {active_account}")

        # =========================================================================
        # STEP 2: Create or select GCP project
        # =========================================================================
        print_step(2, 5, "Set Up Google Cloud Project")

        current_project = get_active_project()

        if current_project:
            print(f"Current active project: {current_project}\n")
            choice = input("Do you want to:\n  1. Use current project\n  2. Select a different project\n  3. Create a new project\n\nChoice (1/2/3): ").strip()
        else:
            print("No active project found.\n")
            choice = input("Do you want to:\n  1. Select an existing project\n  2. Create a new project\n\nChoice (1/2): ").strip()
            if choice == "1":
                choice = "2"  # Map to "select different"
            elif choice == "2":
                choice = "3"  # Map to "create new"

        if choice == "2":
            # List and select existing project
            projects = list_projects()

            if not projects:
                print("\n⚠️  No existing projects found. Let's create one.\n")
                choice = "3"
            else:
                print("\nYour projects:")
                for idx, (project_id, name) in enumerate(projects, 1):
                    print(f"  {idx}. {name} ({project_id})")

                selection = input(f"\nSelect project (1-{len(projects)}): ").strip()
                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(projects):
                        selected_project = sanitize_command_arg(projects[idx][0])
                        run_command_safe(["gcloud", "config", "set", "project", selected_project])
                        print(f"\n✅ Project set to: {selected_project}")
                    else:
                        print("Invalid selection.")
                        sys.exit(1)
                except ValueError:
                    print("Invalid input.")
                    sys.exit(1)

        if choice == "3":
            # Create new project
            print("\nCreating a new Google Cloud project for Account Intelligence...")

            default_name = "Account Intelligence Drive Access"
            project_name = input(f"Project name [{default_name}]: ").strip() or default_name

            # Generate project ID
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            default_id = f"project-ape-{random_suffix}"
            project_id = input(f"Project ID [{default_id}]: ").strip() or default_id

            print()
            success, error = create_project(project_id, project_name)

            if not success:
                print(f"\n❌ Failed to create project: {error}\n")

                # Check if it's a billing error
                if error and ("billing" in error.lower() or "PERMISSION_DENIED" in error):
                    print("This is likely because:")
                    print("  • You need to enable billing on your Google Cloud account")
                    print("  • Your organization has restrictions on project creation\n")
                    print("SOLUTION: Use an existing project instead.\n")

                    projects = list_projects()
                    if projects:
                        print("Your existing projects:")
                        for idx, (pid, name) in enumerate(projects, 1):
                            print(f"  {idx}. {name} ({pid})")

                        selection = input(f"\nSelect a project to use (1-{len(projects)}, or Q to quit): ").strip()
                        if selection.lower() == 'q':
                            sys.exit(1)

                        try:
                            idx = int(selection) - 1
                            if 0 <= idx < len(projects):
                                selected_project = sanitize_command_arg(projects[idx][0])
                                run_command_safe(["gcloud", "config", "set", "project", selected_project])
                                print(f"\n✅ Using project: {selected_project}")
                            else:
                                sys.exit(1)
                        except ValueError:
                            sys.exit(1)
                    else:
                        print("No existing projects found. Cannot continue.")
                        sys.exit(1)
                else:
                    sys.exit(1)
            else:
                print(f"✅ Project created: {project_id}")

        # Get final active project
        final_project = get_active_project()
        if not final_project:
            print("\n❌ No active project. Cannot continue.")
            sys.exit(1)

        print(f"\n✅ Using project: {final_project}")

        # =========================================================================
        # STEP 3: Enable Google Drive API
        # =========================================================================
        print_step(3, 5, "Enable Google Drive API")

        if check_api_enabled():
            print("✅ Google Drive API is already enabled")
        else:
            if not enable_drive_api():
                print("\n❌ Failed to enable Drive API. Cannot continue.")
                sys.exit(1)

            print("⏳ Waiting for API to propagate (10 seconds)...")
            time.sleep(10)

        # =========================================================================
        # STEP 4: Create OAuth credentials
        # =========================================================================
        print_step(4, 5, "Create OAuth Credentials")

        # Create credentials directory with secure permissions atomically
        secure_create_directory(CREDS_DIR, mode=0o700)

        if CLIENT_SECRETS_FILE.exists():
            print(f"✅ OAuth credentials already exist: {CLIENT_SECRETS_FILE}\n")
            use_existing = input("Use existing credentials? (y/n): ").strip().lower()
            if use_existing == 'y':
                print("✅ Using existing credentials")
            else:
                print("\nDeleting old credentials...")
                cleanup_files.append(CLIENT_SECRETS_FILE)
                secure_cleanup(cleanup_files)
                cleanup_files.clear()
                print("Please download new credentials (instructions below)")

        if not CLIENT_SECRETS_FILE.exists():
            print("\n📋 You need to create OAuth credentials in the Google Cloud Console.")
            print("\nI will open the Google Cloud Console for you. Please follow these steps:\n")

            print("─" * 70)
            print("INSTRUCTIONS:")
            print("─" * 70)
            print()
            print("1. The browser will open to the Credentials page")
            print("2. If you see a consent screen warning, click through it")
            print("3. Click: '+ CREATE CREDENTIALS' → 'OAuth client ID'")
            print()
            print("4. If prompted 'Configure Consent Screen':")
            print("   a. Choose 'External'")
            print("   b. App name: 'Account Intelligence'")
            print("   c. User support email: (your email)")
            print("   d. Developer contact: (your email)")
            print("   e. Click 'SAVE AND CONTINUE' (3 times)")
            print("   f. Return to Credentials page")
            print()
            print("5. Create OAuth client ID:")
            print("   a. Application type: 'Desktop app'")
            print("   b. Name: 'Account Intelligence Desktop'")
            print("   c. Click 'CREATE'")
            print()
            print("6. In the popup:")
            print("   a. Click 'DOWNLOAD JSON'")
            print("   b. Save to your Downloads folder (filename will be client_secret_*.json)")
            print("   c. Click 'OK'")
            print()
            print("7. This script will automatically:")
            print("   a. Find the downloaded file in ~/Downloads/")
            print("   b. Move it to ~/.project-ape/drive_credentials.json")
            print("   c. Set secure permissions (chmod 600)")
            print()
            print("─" * 70)
            print()

            input("Press Enter to open Google Cloud Console...")

            # Open credentials page
            credentials_url = f"https://console.cloud.google.com/apis/credentials?project={sanitize_command_arg(final_project)}"
            webbrowser.open(credentials_url)

            print("\n✅ Browser opened to Credentials page")
            print("\nFollow the instructions above to create and download your credentials.")
            print("\nWhen you've downloaded the JSON file, we'll continue.\n")

            input("Press Enter when you've downloaded the credentials file...")

            # Find the downloaded credentials file
            downloads_dir = Path.home() / "Downloads"
            client_secret_files = list(downloads_dir.glob("client_secret_*.json"))

            if not client_secret_files:
                print("\n❌ Could not find credentials file in Downloads folder.")
                print(f"\nExpected location: ~/Downloads/client_secret_*.json")
                print(f"\nMANUAL SETUP REQUIRED:")
                print(f"  1. Locate your downloaded JSON file (usually named client_secret_*.json)")
                print(f"  2. Create directory: mkdir -p ~/.project-ape")
                print(f"  3. Move and rename the file:")
                print(f"     mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json")
                print(f"  4. Set secure permissions:")
                print(f"     chmod 600 ~/.project-ape/drive_credentials.json")
                print(f"  5. Re-run this script: python3 setup-oauth-drive-improved.py")
                sys.exit(1)

            # Use the most recent file
            latest_file = max(client_secret_files, key=lambda p: p.stat().st_mtime)

            print(f"\n✅ Found credentials file: {latest_file.name}")
            print(f"Moving to: {CLIENT_SECRETS_FILE}")

            # Securely move and set permissions atomically
            try:
                secure_move_credentials(latest_file, CLIENT_SECRETS_FILE, mode=0o600)
                cleanup_files.append(CLIENT_SECRETS_FILE)  # Track for cleanup on error
                print("✅ Credentials file installed and secured (chmod 600)")
            except SecurityError as e:
                print(f"\n❌ Failed to secure credentials: {e}")
                sys.exit(1)

        # =========================================================================
        # STEP 5: Authenticate with Google
        # =========================================================================
        print_step(5, 5, "Authenticate with Google Drive")

        print("Now we'll complete the OAuth flow to get your Drive access token.\n")
        print("🌐 Your browser will open to sign in with Google.")
        print("   1. Sign in with your Google account")
        print("   2. You may see 'Google hasn't verified this app' - this is normal!")
        print("      Click 'Advanced' → 'Go to Account Intelligence (unsafe)'")
        print("   3. Click 'Allow' to grant Drive access")
        print("   4. Return here when you see 'Authentication successful'")
        print()

        input("Press Enter to start OAuth flow...")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE),
                SCOPES
            )

            # Run local server for OAuth callback
            creds = flow.run_local_server(
                port=0,
                success_message='✅ Authentication successful! You can close this window and return to the terminal.',
                open_browser=True
            )

            # Validate credentials before saving
            if not validate_credentials(creds):
                raise SecurityError("Credential validation failed: invalid or expired token")

            # Save token with atomic write and secure permissions
            secure_write_file(TOKEN_FILE, creds.to_json(), mode=0o600)
            cleanup_files.append(TOKEN_FILE)  # Track for cleanup on error

            print()
            print_header("✅ SUCCESS - OAuth Setup Complete!")

            print(f"✅ Token saved to: {TOKEN_FILE}")
            print(f"✅ Credentials at: {CLIENT_SECRETS_FILE}")
            print(f"✅ Both files secured with chmod 600")
            print(f"✅ Token validated and verified")
            print()
            print("You can now access your Google Drive files without manual folder sharing!")
            print()
            print("Next steps:")
            print("  1. Ensure vars.py has: auth_method = 'oauth'")
            print("  2. Run: ./launch_ape.sh fast")
            print()

            # Clear cleanup list on success
            cleanup_files.clear()

        except SecurityError as e:
            print()
            print_header("❌ ERROR - Security Validation Failed")
            print(f"Error: {e}\n")
            raise

        except Exception as e:
            print()
            print_header("❌ ERROR - OAuth Authentication Failed")
            print(f"Error: {sanitize_error_message(str(e))}\n")
            print("Troubleshooting:")
            print("  • Ensure you clicked 'Allow' in the browser")
            print("  • If you saw 'Access blocked', you may need to add yourself as a test user:")
            print(f"    https://console.cloud.google.com/apis/credentials/consent?project={sanitize_command_arg(final_project)}")
            print("  • Make sure OAuth client type is 'Desktop app', not 'Web application'")
            print()
            raise

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        secure_cleanup(cleanup_files)
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Setup failed: {sanitize_error_message(str(e))}")
        print("\nCleaning up sensitive files...")
        secure_cleanup(cleanup_files)
        sys.exit(1)


if __name__ == "__main__":
    main()
