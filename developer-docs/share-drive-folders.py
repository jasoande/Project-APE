#!/usr/bin/env python3
"""
Automatically share Google Drive folders with service account.
Reads folder URLs from vars.py and grants service account viewer access.
"""

import json
import re
import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ANSI colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def extract_folder_id(drive_url: str) -> str:
    """Extract folder ID from Google Drive URL."""
    # Pattern: https://drive.google.com/drive/folders/FOLDER_ID or /u/0/folders/FOLDER_ID
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    return None


def get_service_account_email(key_file: Path) -> str:
    """Get service account email from key file."""
    with open(key_file, 'r') as f:
        key_data = json.load(f)
    return key_data['client_email']


def share_folder_with_service_account(service, folder_id: str, service_account_email: str, folder_name: str) -> bool:
    """
    Share a folder with the service account.

    Args:
        service: Google Drive API service object
        folder_id: The ID of the folder to share
        service_account_email: Email of the service account
        folder_name: Human-readable folder name for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if already shared
        try:
            permissions = service.permissions().list(
                fileId=folder_id,
                fields='permissions(emailAddress,role)'
            ).execute()

            for perm in permissions.get('permissions', []):
                if perm.get('emailAddress') == service_account_email:
                    print(f"{YELLOW}⚠️  {NC}Already shared: {folder_name}")
                    print(f"   Current role: {perm.get('role')}")
                    return True
        except HttpError as e:
            # Ignore error - we'll try to share anyway
            pass

        # Create permission
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': service_account_email
        }

        service.permissions().create(
            fileId=folder_id,
            body=permission,
            sendNotificationEmail=False,  # Don't email service account
            fields='id'
        ).execute()

        print(f"{GREEN}✅{NC} Shared: {folder_name}")
        print(f"   Folder ID: {folder_id}")
        return True

    except HttpError as error:
        print(f"{RED}❌{NC} Failed to share: {folder_name}")
        print(f"   Error: {error}")
        return False


def main():
    print("=" * 72)
    print("SHARE GOOGLE DRIVE FOLDERS WITH SERVICE ACCOUNT")
    print("=" * 72)
    print()

    # Check for service account key
    key_file = Path('service-account-key.json')
    if not key_file.exists():
        print(f"{RED}❌ Error:{NC} service-account-key.json not found")
        print("   Run: ./create-service-account.sh")
        sys.exit(1)

    # Get service account email
    try:
        sa_email = get_service_account_email(key_file)
        print(f"{BLUE}Service Account:{NC} {sa_email}")
        print()
    except Exception as e:
        print(f"{RED}❌ Error:{NC} Could not read service account key: {e}")
        sys.exit(1)

    # Import vars.py
    try:
        import vars
    except ImportError:
        print(f"{RED}❌ Error:{NC} vars.py not found")
        print("   Configure your clients in vars.py first")
        sys.exit(1)

    # Get clients list
    if not hasattr(vars, 'clients') or not vars.clients:
        print(f"{RED}❌ Error:{NC} No clients configured in vars.py")
        print("   Add clients to vars.py first")
        sys.exit(1)

    print(f"Found {len(vars.clients)} client(s) to process...")
    print()

    # Authenticate with Drive API
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            str(key_file), scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        print(f"{GREEN}✅{NC} Authenticated with Google Drive API")
        print()
    except Exception as e:
        print(f"{RED}❌ Error:{NC} Could not authenticate with Drive API: {e}")
        sys.exit(1)

    # Process each client
    success_count = 0
    failed_count = 0

    for client_id in vars.clients:
        # Get folder URL
        folder_attr = f"{client_id}_folder"
        if not hasattr(vars, folder_attr):
            print(f"{YELLOW}⚠️  {NC}Skipped: {client_id} (no {folder_attr} in vars.py)")
            continue

        folder_url = getattr(vars, folder_attr)

        # Get client name
        name_attr = f"{client_id}_name"
        client_name = getattr(vars, name_attr, client_id)

        # Extract folder ID
        folder_id = extract_folder_id(folder_url)
        if not folder_id:
            print(f"{RED}❌{NC} Invalid URL for {client_name}")
            print(f"   URL: {folder_url}")
            failed_count += 1
            continue

        # Share folder
        print(f"Processing: {client_name}")
        if share_folder_with_service_account(service, folder_id, sa_email, client_name):
            success_count += 1
        else:
            failed_count += 1
        print()

    # Summary
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"{GREEN}✅ Successfully shared:{NC} {success_count}")
    if failed_count > 0:
        print(f"{RED}❌ Failed:{NC} {failed_count}")
    print()

    if failed_count == 0:
        print(f"{GREEN}All folders are now accessible by the service account!{NC}")
        print()
        print("You can now run:")
        print(f"  {GREEN}./launch_ape.sh fast{NC}")
    else:
        print(f"{YELLOW}Some folders could not be shared automatically.{NC}")
        print("You may need to manually share them:")
        print(f"  1. Go to https://drive.google.com")
        print(f"  2. Right-click folder → Share")
        print(f"  3. Add: {sa_email}")
        print(f"  4. Set permission: Viewer")
        print(f"  5. Uncheck 'Notify people'")
        sys.exit(1)


if __name__ == '__main__':
    main()
