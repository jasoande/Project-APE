#!/usr/bin/env python3
"""
Setup OAuth for Google Drive Access
====================================
Creates OAuth credentials for browser-based Drive authentication.

This is an alternative to using a service account - no manual folder sharing needed!

Usage:
    python3 setup-oauth-drive.py
"""

import json
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for Drive read-only access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Where to store credentials
CREDS_DIR = Path.home() / '.project-ape'
TOKEN_FILE = CREDS_DIR / 'drive_token.json'
CLIENT_SECRETS_FILE = CREDS_DIR / 'drive_credentials.json'

print("=" * 70)
print("  Google Drive OAuth Setup")
print("=" * 70)
print()
print("This will authenticate Project APE to access your Google Drive files")
print("using your personal Google account (no service account needed).")
print()

# Create credentials directory
CREDS_DIR.mkdir(parents=True, exist_ok=True)

# Check if we already have credentials
if CLIENT_SECRETS_FILE.exists():
    print(f"✅ Found OAuth client secrets: {CLIENT_SECRETS_FILE}")
else:
    print("❌ OAuth client secrets not found")
    print()
    print("You need to create OAuth credentials first:")
    print()
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click 'Create Credentials' → 'OAuth client ID'")
    print("3. Application type: 'Desktop app'")
    print("4. Name: 'Project APE Desktop'")
    print("5. Click 'Create'")
    print("6. Click 'Download JSON'")
    print("7. Save the file as:")
    print(f"   {CLIENT_SECRETS_FILE}")
    print()
    print("Then run this script again.")
    print()

    # Offer to create a simple placeholder
    response = input("Would you like me to create a template file? (y/n): ").lower()
    if response == 'y':
        template = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["http://localhost"]
            }
        }

        with open(CLIENT_SECRETS_FILE, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"\n✅ Template created: {CLIENT_SECRETS_FILE}")
        print("\nNow edit this file and replace:")
        print("  - YOUR_CLIENT_ID")
        print("  - your-project-id")
        print("  - YOUR_CLIENT_SECRET")
        print("\nWith values from the Google Cloud Console.")

    sys.exit(1)

# Authenticate
print()
print("Starting OAuth flow...")
print()
print("🌐 Your browser will open shortly.")
print("   1. Sign in with your Google account")
print("   2. Click 'Allow' to grant access")
print("   3. Return to this terminal when done")
print()

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        SCOPES
    )

    # Run local server for OAuth callback
    creds = flow.run_local_server(
        port=0,
        success_message='✅ Authentication successful! You can close this window.',
        open_browser=True
    )

    # Save token
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())

    print()
    print("=" * 70)
    print("✅ SUCCESS - OAuth Setup Complete!")
    print("=" * 70)
    print()
    print(f"Token saved to: {TOKEN_FILE}")
    print()
    print("You can now access your Google Drive files without sharing!")
    print()
    print("Next steps:")
    print("  1. Ensure vars.py has: auth_method: 'oauth'")
    print("  2. Run: ./launch-project-ape.command")
    print()

except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERROR - OAuth Setup Failed")
    print("=" * 70)
    print()
    print(f"Error: {e}")
    print()
    print("Troubleshooting:")
    print("  • Ensure OAuth client secrets are correct")
    print("  • Check that you enabled Google Drive API in Cloud Console")
    print("  • Verify the client ID is for a 'Desktop app', not 'Web app'")
    print()
    sys.exit(1)
