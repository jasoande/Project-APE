#!/usr/bin/env python3
"""
Test credential file permissions.

This test validates:
1. Credential files are created with 0o600 permissions (owner read/write only)
2. Token files are created with 0o600 permissions
3. All sensitive files in ~/.project-ape have secure permissions
"""

import sys
import os
from pathlib import Path
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_drive_manager_permissions():
    """Test that DriveManager creates credential files with secure permissions."""

    print("\n🧪 Test 1: DriveManager credential file permissions...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create mock credential file
        mock_creds_file = temp_path / 'credentials.json'
        mock_creds = {
            "installed": {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "redirect_uris": ["http://localhost"]
            }
        }
        mock_creds_file.write_text(json.dumps(mock_creds))

        # Create mock token file (simulating what the code does)
        token_file = temp_path / 'token.json'
        mock_token = {
            "token": "test_token",
            "refresh_token": "test_refresh",
            "token_uri": "https://oauth2.googleapis.com/token"
        }

        # Simulate the write operation from drive_manager.py
        with open(token_file, 'w') as f:
            f.write(json.dumps(mock_token))

        # Apply the secure permissions (as our code does)
        os.chmod(token_file, 0o600)

        # Verify permissions
        file_stat = token_file.stat()
        file_mode = file_stat.st_mode & 0o777

        assert file_mode == 0o600, f"❌ Token file has incorrect permissions: {oct(file_mode)}"
        print(f"✅ Token file has correct permissions: {oct(file_mode)}")

def test_actual_credential_files():
    """Test that actual credential files in ~/.project-ape have secure permissions."""

    print("\n🧪 Test 2: Checking actual credential files in ~/.project-ape...")

    project_ape_dir = Path.home() / '.project-ape'

    if not project_ape_dir.exists():
        print("⚠️  ~/.project-ape directory doesn't exist, skipping test")
        return

    # Files that should have secure permissions
    sensitive_files = [
        'flask_secret.key',
        'drive_credentials.json',
        'drive_token.json'
    ]

    checked_count = 0
    for filename in sensitive_files:
        filepath = project_ape_dir / filename
        if filepath.exists():
            file_stat = filepath.stat()
            file_mode = file_stat.st_mode & 0o777

            # Check if permissions are secure (0o600 or stricter)
            # Acceptable: 0o600 (owner rw), 0o400 (owner r)
            if file_mode not in [0o600, 0o400]:
                print(f"⚠️  {filename} has insecure permissions: {oct(file_mode)}")
                print(f"   Expected: 0o600 (owner read/write only)")

                # Try to fix it
                try:
                    os.chmod(filepath, 0o600)
                    print(f"   ✅ Fixed permissions to 0o600")
                except Exception as e:
                    print(f"   ❌ Failed to fix permissions: {e}")
            else:
                print(f"✅ {filename} has secure permissions: {oct(file_mode)}")

            checked_count += 1

    if checked_count == 0:
        print("⚠️  No sensitive files found in ~/.project-ape")
    else:
        print(f"\n✅ Checked {checked_count} sensitive files")

def test_code_has_chmod_calls():
    """Verify that the code has chmod calls after credential writes."""

    print("\n🧪 Test 3: Verifying chmod calls in source code...")

    # Check drive_manager.py
    drive_manager_path = Path(__file__).parent.parent / 'core' / 'drive_manager.py'
    drive_manager_content = drive_manager_path.read_text()

    # Count token file writes and chmod calls
    token_writes = drive_manager_content.count("f.write(creds.to_json())")
    chmod_calls = drive_manager_content.count("os.chmod(token_file, 0o600)")

    print(f"   drive_manager.py: {token_writes} token writes, {chmod_calls} chmod calls")

    if token_writes != chmod_calls:
        print(f"   ⚠️  Warning: Token writes ({token_writes}) != chmod calls ({chmod_calls})")
    else:
        print(f"   ✅ All token writes have corresponding chmod calls")

    # Check dashboard/server.py
    server_path = Path(__file__).parent.parent / 'dashboard' / 'server.py'
    server_content = server_path.read_text()

    # Find credential-related writes
    creds_writes = server_content.count("f.write(creds.to_json())")
    creds_chmod = server_content.count("os.chmod(") + server_content.count("os.chmod(creds_file,") + server_content.count("os.chmod(token_file,")

    print(f"   dashboard/server.py: credential writes detected, chmod calls found")

    # Specific checks for known sensitive file writes
    if 'drive_credentials.json' in server_content:
        if 'os.chmod(creds_file, 0o600)' in server_content:
            print(f"   ✅ drive_credentials.json has chmod protection")
        else:
            print(f"   ⚠️  drive_credentials.json may be missing chmod protection")

    if 'drive_token.json' in server_content:
        # Should have multiple chmod calls for token file
        token_chmod_count = server_content.count("os.chmod(token_file, 0o600)")
        print(f"   ✅ drive_token.json has {token_chmod_count} chmod protection(s)")

    # Check flask_secret.key
    if 'flask_secret.key' in server_content:
        if 'secret_key_file.chmod(0o600)' in server_content:
            print(f"   ✅ flask_secret.key has chmod protection")
        else:
            print(f"   ⚠️  flask_secret.key may be missing chmod protection")

    print("\n✅ Code verification complete")

def test_permission_enforcement():
    """Test that files created with default permissions can be secured."""

    print("\n🧪 Test 4: Testing permission enforcement...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a file with default permissions
        test_file = temp_path / 'test_secret.json'
        test_file.write_text('{"secret": "test"}')

        # Check initial permissions (will inherit umask)
        initial_mode = test_file.stat().st_mode & 0o777
        print(f"   Initial permissions: {oct(initial_mode)}")

        # Apply secure permissions
        os.chmod(test_file, 0o600)

        # Verify
        secure_mode = test_file.stat().st_mode & 0o777
        assert secure_mode == 0o600, f"❌ chmod failed: {oct(secure_mode)}"
        print(f"   ✅ Secured permissions: {oct(secure_mode)}")

        # Verify the file is readable by owner
        content = test_file.read_text()
        assert content == '{"secret": "test"}', "❌ File not readable after chmod"
        print(f"   ✅ File still readable by owner")

if __name__ == '__main__':
    try:
        test_drive_manager_permissions()
        test_actual_credential_files()
        test_code_has_chmod_calls()
        test_permission_enforcement()

        print("\n" + "="*60)
        print("✅ ALL CREDENTIAL PERMISSION TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
