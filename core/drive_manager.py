"""
Google Drive Manager
====================
Manages Google Drive folder downloads with OAuth authentication and caching.

Features:
- OAuth 2.0 user authentication with token caching
- Automatic Google Workspace file export (Docs → PDF, Sheets → XLSX)
- Intelligent caching with TTL
- Context manager pattern for automatic cleanup
- Retry logic with exponential backoff

Usage:
    with DriveManager(client_id, folder_url, cache_enabled=True) as folder_path:
        # Use folder_path as local directory
        process_files(folder_path)
"""

import io
import json
import logging
import os
import re
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


# ==============================================================================
# CUSTOM EXCEPTIONS
# ==============================================================================

class DriveError(Exception):
    """Base exception for Drive-related errors."""
    pass


class DriveAuthenticationError(DriveError):
    """Authentication failed."""
    pass


class DriveFolderNotFoundError(DriveError):
    """Folder not found or invalid ID."""
    pass


class DrivePermissionError(DriveError):
    """No permission to access folder."""
    pass


class DriveRateLimitError(DriveError):
    """Rate limit exceeded."""
    pass


# ==============================================================================
# DRIVE MANAGER
# ==============================================================================

class DriveManager:
    """Manages Google Drive folder downloads with authentication and caching."""

    # Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # Google Workspace export formats
    # Export all to PDF for NotebookLM compatibility
    EXPORT_FORMATS = {
        'application/vnd.google-apps.document': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.spreadsheet': ('application/pdf', '.pdf'),
        'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),
    }

    # Retry configuration
    MAX_RETRIES = 5
    RETRY_BASE_DELAY = 10.0

    def __init__(
        self,
        client_id: str,
        folder_spec: str,
        cache_enabled: bool = True,
        force_refresh: bool = False,
        config: Optional[Dict] = None
    ):
        """
        Initialize Drive manager.

        Args:
            client_id: Client identifier for logging
            folder_spec: Google Drive folder URL or ID
            cache_enabled: Enable file caching
            force_refresh: Force refresh, bypass cache even if valid
            config: Optional configuration dict (DRIVE_CONFIG from vars.py)
        """
        self.client_id = client_id
        self.folder_spec = folder_spec
        self.cache_enabled = cache_enabled
        self.force_refresh = force_refresh
        self.config = config or {}

        self.folder_id = None
        self.service = None
        self._creds = None
        self.temp_dir = None
        self.using_cache = False

        # Extract configuration
        # OAuth is the only supported authentication method
        self.export_google_docs = self.config.get('export_google_docs', True)
        self.recursive = self.config.get('recursive', False)
        self.max_file_size_mb = self.config.get('max_file_size_mb', 2048)  # 2GB limit for NotebookLM
        self.cache_ttl_hours = self.config.get('cache_ttl_hours', 24)

    def __enter__(self) -> Path:
        """
        Context manager entry - download files and return temp directory.

        Returns:
            Path to temporary directory containing downloaded files
        """
        logger.info(f"[{self.client_id}] 🔄 Initializing Google Drive download...")

        # Parse folder ID
        self.folder_id = self._parse_folder_spec(self.folder_spec)
        logger.info(f"[{self.client_id}]    Folder ID: {self.folder_id}")

        # Authenticate
        if not self.authenticate():
            raise DriveAuthenticationError("Failed to authenticate with Google Drive")

        # Check cache (skip if force_refresh)
        if self.cache_enabled and not self.force_refresh and self._should_use_cache(self.folder_id):
            cache_dir = self._get_cache_dir(self.folder_id)
            # Clean up zero-byte files left by failed downloads
            zero_byte = [f for f in cache_dir.iterdir() if f.is_file() and f.stat().st_size == 0 and f.name != 'metadata.json']
            for f in zero_byte:
                f.unlink()
                logger.info(f"[{self.client_id}]    🧹 Removed empty cached file: {f.name}")
            logger.info(f"[{self.client_id}] ✅ Using cached Drive files")
            logger.info(f"[{self.client_id}]    Cache: {cache_dir}")
            self.temp_dir = cache_dir
            self.using_cache = True
            return Path(cache_dir)

        # Log if cache was bypassed due to force_refresh
        if self.force_refresh and self.cache_enabled:
            logger.info(f"[{self.client_id}] 🔄 Force refresh enabled - bypassing cache")

        # Download files
        if self.cache_enabled:
            self.temp_dir = self._get_cache_dir(self.folder_id)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix=f"drive_{self.client_id}_"))

        logger.info(f"[{self.client_id}] ⬇️  Downloading from Drive...")
        logger.info(f"[{self.client_id}]    Target: {self.temp_dir}")

        file_count = self._download_folder(self.folder_id, self.temp_dir)

        logger.info(f"[{self.client_id}] ✅ Downloaded {file_count} files from Drive")

        # Save cache metadata
        if self.cache_enabled:
            self._save_cache_metadata(self.folder_id)

        return Path(self.temp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temp directory if not cached."""
        if self.temp_dir and not self.cache_enabled and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            logger.info(f"[{self.client_id}] 🧹 Cleaned up temp directory")

    # ==========================================================================
    # AUTHENTICATION
    # ==========================================================================

    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive using OAuth 2.0.

        Returns:
            True if authentication successful
        """
        try:
            creds = self._oauth_authenticate()
            self._creds = creds
            self.service = build('drive', 'v3', credentials=creds)
            logger.info(f"[{self.client_id}] 🔐 Authenticated with Google Drive")
            return True

        except Exception as e:
            logger.error(f"[{self.client_id}] ❌ Authentication failed: {e}")
            raise DriveAuthenticationError(str(e))

    def _oauth_authenticate(self) -> Credentials:
        """
        Authenticate using OAuth 2.0 user flow.

        Returns:
            Valid credentials

        Raises:
            DriveAuthenticationError: If authentication fails
        """
        creds = None
        token_file = Path.home() / '.project-ape' / 'drive_token.json'
        credentials_file = Path.home() / '.project-ape' / 'drive_credentials.json'

        # Load cached token
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)

        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info(f"[{self.client_id}] 🔄 Refreshing OAuth token...")
                creds.refresh(Request())
            else:
                if not credentials_file.exists():
                    raise DriveAuthenticationError(
                        f"OAuth credentials not found: {credentials_file}\n"
                        f"Run: python3 setup_drive_auth.py"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(token_file, 'w') as f:
                f.write(creds.to_json())
            # Secure file permissions (owner read/write only)
            os.chmod(token_file, 0o600)

        return creds

    # ==========================================================================
    # FOLDER ID PARSING
    # ==========================================================================

    def _parse_folder_spec(self, spec: str) -> str:
        """
        Extract folder ID from URL or return as-is.

        Supported formats:
        - https://drive.google.com/drive/folders/ABC123
        - https://drive.google.com/drive/u/0/folders/ABC123
        - drive://ABC123
        - ABC123 (folder ID)

        Args:
            spec: Folder URL or ID

        Returns:
            Folder ID
        """
        # URL format
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', spec)
        if match:
            return match.group(1)

        # drive:// protocol
        if spec.startswith('drive://'):
            return spec[8:]

        # Assume it's a folder ID
        return spec

    # ==========================================================================
    # FOLDER DOWNLOAD
    # ==========================================================================

    def _download_folder(self, folder_id: str, target_dir: Path) -> int:
        """
        Download all files from folder.

        Args:
            folder_id: Google Drive folder ID
            target_dir: Local directory to download files to

        Returns:
            Number of files downloaded
        """
        files = self._list_folder_files(folder_id)
        logger.info(f"[{self.client_id}]    Found {len(files)} files in Drive folder")

        downloadable = []
        for file_info in files:
            file_size_mb = int(file_info.get('size', 0)) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                logger.warning(
                    f"[{self.client_id}]    ⚠️  Skipping {file_info['name']} "
                    f"({file_size_mb:.1f}MB > {self.max_file_size_mb}MB limit)"
                )
                continue
            downloadable.append(file_info)

        def _download_one(file_info):
            file_id = file_info['id']
            file_name = file_info['name']
            mime_type = file_info['mimeType']
            thread_service = build('drive', 'v3', credentials=self._creds)
            try:
                if mime_type.startswith('application/vnd.google-apps.'):
                    if self.export_google_docs:
                        self._export_google_doc(file_id, file_name, mime_type, target_dir, service=thread_service)
                        return True
                    else:
                        logger.info(f"[{self.client_id}]    ⏭️  Skipping Google Doc: {file_name}")
                        return False
                else:
                    self._download_file(file_id, file_name, mime_type, target_dir, service=thread_service)
                    return True
            except Exception as e:
                logger.warning(f"[{self.client_id}]    ⚠️  Failed to download {file_name}: {e}")
                return False

        downloaded = 0
        max_workers = min(4, len(downloadable)) if downloadable else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_download_one, f): f for f in downloadable}
            for future in as_completed(futures):
                if future.result():
                    downloaded += 1

        return downloaded

    def list_files_metadata(self) -> List[Dict]:
        """
        List all files in the configured folder without downloading.

        Returns:
            List of dicts with keys: id, name, mimeType, size, modifiedTime
        """
        # Parse folder ID if not already done
        if not self.folder_id:
            self.folder_id = self._parse_folder_spec(self.folder_spec)

        if not self.service:
            self.authenticate()

        logger.info(f"[{self.client_id}] 📋 Listing files in Drive folder...")
        logger.info(f"[{self.client_id}]    Folder ID: {self.folder_id}")

        files = self._list_folder_files(self.folder_id)

        # Filter out files over size limit
        filtered_files = []
        for file_info in files:
            file_name = file_info['name']
            file_size_mb = int(file_info.get('size', 0)) / (1024 * 1024)

            if file_size_mb > self.max_file_size_mb:
                logger.warning(
                    f"[{self.client_id}]    ⚠️  Skipping {file_name} "
                    f"({file_size_mb:.1f}MB > {self.max_file_size_mb}MB limit)"
                )
                continue

            filtered_files.append(file_info)

        logger.info(f"[{self.client_id}] ✅ Found {len(filtered_files)} files")
        return filtered_files

    def _list_folder_files(self, folder_id: str) -> List[Dict]:
        """
        List all files in a folder.

        Args:
            folder_id: Google Drive folder ID

        Returns:
            List of file metadata dicts

        Raises:
            DriveFolderNotFoundError: If folder not found
            DrivePermissionError: If no permission to access folder
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if not self.recursive:
                query += " and mimeType!='application/vnd.google-apps.folder'"

            results = self.service.files().list(
                q=query,
                pageSize=1000,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()

            files = results.get('files', [])
            return files

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFolderNotFoundError(f"Folder not found: {folder_id}")
            elif e.resp.status == 403:
                raise DrivePermissionError(
                    f"No permission to access folder: {folder_id}\n"
                    f"Make sure the folder is shared with your Google account"
                )
            else:
                raise DriveError(f"Failed to list folder files: {e}")

    def _download_file(self, file_id: str, file_name: str, mime_type: str, target_dir: Path, service=None):
        """
        Download a single file.

        Args:
            file_id: Google Drive file ID
            file_name: File name
            mime_type: File MIME type
            target_dir: Local directory to download to
            service: Optional Drive API service (for thread safety)
        """
        logger.info(f"[{self.client_id}]       ⬇️  {file_name}")

        svc = service or self.service
        request = svc.files().get_media(fileId=file_id)
        file_path = target_dir / file_name

        try:
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
        except Exception:
            if file_path.exists() and file_path.stat().st_size == 0:
                file_path.unlink()
            raise

    def _export_google_doc(
        self,
        file_id: str,
        file_name: str,
        mime_type: str,
        target_dir: Path,
        service=None
    ):
        """
        Export Google Workspace file to compatible format.

        Args:
            file_id: Google Drive file ID
            file_name: File name
            mime_type: Google Workspace MIME type
            target_dir: Local directory to export to
            service: Optional Drive API service (for thread safety)
        """
        if mime_type not in self.EXPORT_FORMATS:
            logger.warning(
                f"[{self.client_id}]    ⚠️  No export format for: {file_name} ({mime_type})"
            )
            return

        export_mime, extension = self.EXPORT_FORMATS[mime_type]

        # Remove extension if present, add correct one
        file_stem = Path(file_name).stem
        export_name = f"{file_stem}{extension}"

        logger.info(f"[{self.client_id}]       📄 {export_name} (exported from Google Doc)")

        svc = service or self.service
        request = svc.files().export_media(fileId=file_id, mimeType=export_mime)
        file_path = target_dir / export_name

        try:
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
        except Exception:
            if file_path.exists() and file_path.stat().st_size == 0:
                file_path.unlink()
            raise

    # ==========================================================================
    # CACHING
    # ==========================================================================

    def _get_cache_dir(self, folder_id: str) -> Path:
        """Get cache directory for folder."""
        cache_root = Path.home() / '.project-ape' / 'drive_cache'
        return cache_root / folder_id

    def _should_use_cache(self, folder_id: str) -> bool:
        """
        Check if cache is valid and should be used.

        Args:
            folder_id: Google Drive folder ID

        Returns:
            True if cache exists and is still valid
        """
        cache_dir = self._get_cache_dir(folder_id)
        metadata_file = cache_dir / 'metadata.json'

        if not metadata_file.exists():
            return False

        try:
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Check TTL
            cached_time = datetime.fromisoformat(metadata['cached_at'])
            ttl = timedelta(hours=self.cache_ttl_hours)

            if datetime.now() - cached_time > ttl:
                logger.info(f"[{self.client_id}]    Cache expired (TTL: {self.cache_ttl_hours}h)")
                return False

            # Cache is valid
            file_count = metadata.get('file_count', 0)
            logger.info(f"[{self.client_id}]    Cache hit ({file_count} files, age: {(datetime.now() - cached_time).seconds // 60}m)")
            return True

        except Exception as e:
            logger.warning(f"[{self.client_id}]    Cache metadata invalid: {e}")
            return False

    def _save_cache_metadata(self, folder_id: str):
        """Save metadata about cached files."""
        cache_dir = self._get_cache_dir(folder_id)
        metadata_file = cache_dir / 'metadata.json'

        file_count = len(list(cache_dir.glob('*'))) - 1  # Exclude metadata.json

        metadata = {
            'folder_id': folder_id,
            'cached_at': datetime.now().isoformat(),
            'file_count': file_count,
            'client_id': self.client_id,
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        self._enforce_cache_limit()

    # 2 GB default limit
    CACHE_MAX_BYTES = 2 * 1024 * 1024 * 1024

    def _enforce_cache_limit(self):
        """Evict oldest cache entries when total cache exceeds CACHE_MAX_BYTES."""
        cache_root = Path.home() / '.project-ape' / 'drive_cache'
        if not cache_root.exists():
            return

        entries = []
        total_size = 0
        for entry_dir in cache_root.iterdir():
            if not entry_dir.is_dir():
                continue
            dir_size = sum(f.stat().st_size for f in entry_dir.rglob('*') if f.is_file())
            meta_file = entry_dir / 'metadata.json'
            try:
                with open(meta_file) as f:
                    meta = json.load(f)
                cached_at = datetime.fromisoformat(meta['cached_at'])
            except Exception:
                cached_at = datetime.min
            entries.append((entry_dir, dir_size, cached_at))
            total_size += dir_size

        if total_size <= self.CACHE_MAX_BYTES:
            return

        entries.sort(key=lambda e: e[2])
        for entry_dir, dir_size, _ in entries:
            if total_size <= self.CACHE_MAX_BYTES:
                break
            logger.info(f"[{self.client_id}] Evicting cache entry: {entry_dir.name} ({dir_size / (1024*1024):.1f}MB)")
            shutil.rmtree(entry_dir)
            total_size -= dir_size

    # ==========================================================================
    # STATIC METHODS
    # ==========================================================================

    @staticmethod
    def setup_oauth():
        """
        Interactive OAuth setup - run once to authenticate.

        This opens a browser for Google authentication and saves credentials.
        """
        credentials_file = Path.home() / '.project-ape' / 'drive_credentials.json'

        if not credentials_file.exists():
            print(f"\n❌ OAuth credentials not found: {credentials_file}")
            print("\nTo set up Google Drive OAuth:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Create OAuth 2.0 credentials (Desktop app)")
            print("3. Download credentials.json")
            print(f"4. Save to: {credentials_file}")
            print("\nSee: https://developers.google.com/drive/api/quickstart/python")
            return False

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            DriveManager.SCOPES
        )

        creds = flow.run_local_server(port=0)

        # Save token
        token_file = Path.home() / '.project-ape' / 'drive_token.json'
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        # Secure file permissions (owner read/write only)
        os.chmod(token_file, 0o600)

        print(f"\n✅ Credentials saved to: {token_file}")
        return True
