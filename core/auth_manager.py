#!/usr/bin/env python3
"""
Authentication Manager
======================
Manages NotebookLM authentication with session persistence
"""

import subprocess
import logging
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages NotebookLM CLI authentication."""

    def __init__(self, profile: str = "default"):
        """
        Initialize auth manager.

        Args:
            profile: NotebookLM profile name
        """
        self.profile = profile
        self.last_check = 0
        self.check_interval = 60  # 1 minute - check frequently during long runs

    def is_authenticated(self, max_retries: int = 3) -> bool:
        """
        Check if currently authenticated with NotebookLM.

        Uses file-based check instead of launching browser to avoid
        profile lock contention when multiple clients check simultaneously.

        Args:
            max_retries: Maximum number of retry attempts for file access failures

        Returns:
            True if authenticated, False otherwise
        """
        import random

        # Path to NotebookLM credentials
        storage_file = Path.home() / '.notebooklm' / 'profiles' / self.profile / 'storage_state.json'

        for attempt in range(max_retries):
            try:
                # Check if credentials file exists
                if not storage_file.exists():
                    logger.debug(f"Auth check: credentials file not found at {storage_file}")
                    return False

                # Try to read and validate credentials file
                with open(storage_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as e:
                        logger.error(f"Auth check: invalid JSON in credentials file: {e}")
                        return False

                # Check if credentials have required structure
                # NotebookLM stores cookies/tokens in the storage_state.json file
                # If the file is valid JSON and not empty, assume credentials are present
                if not data:
                    logger.debug("Auth check: credentials file is empty")
                    return False

                # Check for cookies (indicates valid browser session)
                if 'cookies' not in data or not isinstance(data['cookies'], list):
                    logger.debug("Auth check: no cookies found in credentials")
                    return False

                if len(data['cookies']) == 0:
                    logger.debug("Auth check: cookie list is empty")
                    return False

                # Credentials exist and appear valid
                logger.debug(f"Auth check: valid credentials found ({len(data['cookies'])} cookies)")
                return True

            except (OSError, IOError) as e:
                # File access error - might be transient (lock, permission issue)
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Auth check file access error, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Auth check failed after retries: {e}")
                    return False
            except Exception as e:
                # Unexpected error
                logger.error(f"Unexpected error during auth check: {type(e).__name__}: {e}")
                return False

        # All retries exhausted (shouldn't reach here)
        return False

    def ensure_authenticated(self, client_id: str = None, force_check: bool = False) -> bool:
        """
        Ensure we're authenticated, login if needed.

        Args:
            client_id: Client identifier for logging
            force_check: Force fresh auth check, ignore check_interval cache

        Returns:
            True if authenticated (or successfully logged in), False otherwise
        """
        import random

        prefix = f"[{client_id}] " if client_id else ""

        # Check if we need to verify auth
        now = time.time()
        if not force_check and now - self.last_check < self.check_interval:
            # Recently checked, assume still valid
            return True

        # Add small random delay to spread out auth checks from multiple clients
        # This prevents browser profile lock contention
        if client_id:
            delay = random.uniform(0, 3)
            logger.info(f"{prefix}Auth check anti-collision delay: {delay:.1f}s")
            time.sleep(delay)

        logger.info(f"{prefix}Checking authentication status...")

        if self.is_authenticated():
            logger.info(f"{prefix}✅ Already authenticated")
            self.last_check = now
            return True

        # Not authenticated - need to login
        logger.warning(f"{prefix}❌ Not authenticated. Login required!")
        logger.warning(f"{prefix}")
        logger.warning(f"{prefix}Run this command in your terminal:")
        logger.warning(f"{prefix}  notebooklm login")
        logger.warning(f"{prefix}")
        logger.warning(f"{prefix}Or run these commands for a fresh login:")
        logger.warning(f"{prefix}  notebooklm auth logout")
        logger.warning(f"{prefix}  notebooklm login")
        logger.warning(f"{prefix}")
        logger.warning(f"{prefix}Pipeline will wait 60 seconds for you to authenticate...")

        # Wait for user to login
        for i in range(6):  # Check every 10 seconds for 60 seconds
            time.sleep(10)
            if self.is_authenticated():
                logger.info(f"{prefix}✅ Authentication detected!")
                self.last_check = now
                return True
            logger.info(f"{prefix}Waiting for authentication... ({(i+1)*10}s)")

        logger.error(f"{prefix}❌ Authentication timeout - no valid session found")
        return False
