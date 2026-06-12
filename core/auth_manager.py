#!/usr/bin/env python3
"""
Authentication Manager
======================
Manages NotebookLM authentication with session persistence
"""

import subprocess
import logging
import time

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

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with NotebookLM.

        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Try to list notebooks - this will fail if not authenticated
            # Using 'list' instead of 'status' as status command doesn't exist in all versions
            result = subprocess.run(
                ["notebooklm", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # If list command succeeds (even with 0 notebooks), we're authenticated
            if result.returncode == 0:
                return True

            # Check if error message indicates auth issue
            error_output = result.stderr.lower()
            if "not authenticated" in error_output or "login" in error_output:
                return False

            return False

        except Exception as e:
            logger.error(f"Auth check failed: {e}")
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
        prefix = f"[{client_id}] " if client_id else ""

        # Check if we need to verify auth
        now = time.time()
        if not force_check and now - self.last_check < self.check_interval:
            # Recently checked, assume still valid
            return True

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
