#!/usr/bin/env python3
"""
Verify Google Drive Service Account Access
===========================================
Tests that the service account can access configured Drive folders

Usage:
    python3 verify-drive-access.py
"""

import sys
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def log_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def log_error(msg):
    print(f"{RED}❌ {msg}{NC}")

def log_info(msg):
    print(f"{BLUE}ℹ️  {msg}{NC}")

def log_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")

def main():
    print("=" * 70)
    print("  Google Drive Access Verification")
    print("=" * 70)
    print()

    # Check for service account key
    sa_key_path = Path("service-account-key.json")
    if not sa_key_path.exists():
        log_error("Service account key not found: service-account-key.json")
        print("\nPlease ensure the service account key file exists.")
        print("Run: ./create-service-account.sh")
        return 1

    log_success("Found service account key")

    # Load service account email
    try:
        with open(sa_key_path, 'r') as f:
            sa_data = json.load(f)
            sa_email = sa_data.get('client_email', 'unknown')
            print(f"   Service Account: {BLUE}{sa_email}{NC}")
    except Exception as e:
        log_error(f"Failed to read service account key: {e}")
        return 1

    # Load vars.py to get folder IDs
    vars_path = Path("vars.py")
    if not vars_path.exists():
        log_warning("vars.py not found - will test with sample folder")
        # Use the folder from the error message
        test_folders = [{
            'id': 'panasonic_avionics',
            'name': 'Panasonic Avionics',
            'folder': 'https://drive.google.com/drive/folders/1mV3nUeKg9NBs0Mru7ltc9ILybJgBQnGB'
        }]
    else:
        log_success("Found vars.py configuration")
        # Import vars.py
        sys.path.insert(0, str(Path.cwd()))
        try:
            import vars as config

            # Extract client folders
            test_folders = []
            for client_id in config.clients:
                name = getattr(config, f"{client_id}_name", client_id)
                folder = getattr(config, f"{client_id}_folder", "")

                if folder:
                    test_folders.append({
                        'id': client_id,
                        'name': name,
                        'folder': folder
                    })

            print(f"   Found {len(test_folders)} client(s) to test")
        except Exception as e:
            log_error(f"Failed to load vars.py: {e}")
            return 1

    if not test_folders:
        log_error("No client folders found to test")
        return 1

    print()

    # Create Drive API client
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(sa_key_path),
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=credentials)
        log_success("Authenticated with Google Drive API")
    except Exception as e:
        log_error(f"Failed to authenticate: {e}")
        return 1

    print()
    print("-" * 70)
    print("Testing folder access...")
    print("-" * 70)
    print()

    # Test each folder
    success_count = 0
    failed_folders = []

    for folder_info in test_folders:
        client_name = folder_info['name']
        folder_url = folder_info['folder']

        # Extract folder ID from URL
        if '/folders/' in folder_url:
            folder_id = folder_url.split('/folders/')[-1].split('?')[0]
        elif folder_url.startswith('drive://'):
            folder_id = folder_url.replace('drive://', '')
        else:
            folder_id = folder_url

        print(f"Testing: {BLUE}{client_name}{NC}")
        print(f"   Folder ID: {folder_id}")

        try:
            # Try to get folder metadata
            folder = service.files().get(
                fileId=folder_id,
                fields='id,name,mimeType,owners'
            ).execute()

            log_success(f"Can access folder: {folder.get('name')}")

            # Try to list files
            results = service.files().list(
                q=f"'{folder_id}' in parents",
                pageSize=5,
                fields="files(id, name, mimeType)"
            ).execute()

            files = results.get('files', [])
            print(f"   Files found: {len(files)}")

            if files:
                print(f"   Sample files:")
                for i, file in enumerate(files[:3], 1):
                    print(f"     {i}. {file['name']}")

            success_count += 1
            print()

        except HttpError as e:
            error_msg = str(e)

            if e.resp.status == 404:
                log_error("Cannot access folder - Not found or no permission")
                print(f"   Error: Folder ID not found or not shared")
            elif e.resp.status == 403:
                log_error("Cannot access folder - Permission denied")
                print(f"   Error: Folder not shared with service account")
            else:
                log_error(f"Cannot access folder")
                print(f"   Error: {error_msg}")

            failed_folders.append({
                'name': client_name,
                'folder_id': folder_id,
                'url': folder_url
            })
            print()

        except Exception as e:
            log_error(f"Unexpected error: {e}")
            failed_folders.append({
                'name': client_name,
                'folder_id': folder_id,
                'url': folder_url
            })
            print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"{GREEN}✅ Successfully accessed:{NC} {success_count}")
    print(f"{RED}❌ Failed:{NC} {len(failed_folders)}")
    print()

    if failed_folders:
        print(f"{YELLOW}Folders that need to be shared:{NC}")
        print()
        print(f"Service Account Email: {BLUE}{sa_email}{NC}")
        print()
        print("Manual steps:")
        print("  1. Go to https://drive.google.com")
        print("  2. For each folder below:")
        print()

        for i, folder in enumerate(failed_folders, 1):
            print(f"  {i}. {folder['name']}")
            print(f"     Folder URL: {folder['url']}")
            print(f"     Right-click → Share → Add: {sa_email}")
            print(f"     Permission: Viewer")
            print(f"     Uncheck 'Notify people' → Share")
            print()

        print(f"{BLUE}After sharing, run this script again to verify.{NC}")
        return 1
    else:
        print(f"{GREEN}🎉 All folders are accessible!{NC}")
        print()
        print("You can now proceed with Project APE:")
        print(f"  {BLUE}./launch-project-ape.command{NC}")
        return 0

if __name__ == '__main__':
    sys.exit(main())
