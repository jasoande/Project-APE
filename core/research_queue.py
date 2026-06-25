#!/usr/bin/env python3
"""
Research Queue Manager
======================
Implements a file-based queue for deep mode research to prevent API rate limits.
Only one client can run research at a time - others wait in queue.
"""

import time
import logging
from pathlib import Path
from typing import Optional
import os
import fcntl

logger = logging.getLogger(__name__)


class ResearchQueue:
    """
    File-based queue for serializing deep research across multiple clients.
    Uses file locking to ensure only one client runs research at a time.
    """

    def __init__(self, client_id: str, queue_dir: Path):
        """
        Initialize research queue.

        Args:
            client_id: Client identifier
            queue_dir: Directory for queue lock files
        """
        self.client_id = client_id
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(exist_ok=True)

        # Lock file for the research queue
        self.lock_file_path = self.queue_dir / "research_queue.lock"
        self.lock_file = None

    def acquire(self, timeout: int = 3600) -> bool:
        """
        Acquire the research queue lock (join queue and wait turn).

        Args:
            timeout: Maximum seconds to wait for lock (default 1 hour)

        Returns:
            True if lock acquired, False if timeout
        """
        logger.info(f"[{self.client_id}] 🚦 Joining research queue...")

        start_time = time.time()
        position_logged = False

        while True:
            try:
                # Try to acquire exclusive lock
                self.lock_file = open(self.lock_file_path, 'w')
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                # Lock acquired!
                self.lock_file.write(f"{self.client_id}\n{time.time()}\n")
                self.lock_file.flush()

                logger.info(f"[{self.client_id}] ✅ Research queue lock acquired - starting research")
                return True

            except (IOError, OSError):
                # Lock is held by another client
                if not position_logged:
                    logger.info(f"[{self.client_id}] ⏳ Waiting in queue for previous client to finish research...")
                    position_logged = True

                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.error(f"[{self.client_id}] ❌ Queue timeout after {timeout}s")
                    if self.lock_file:
                        self.lock_file.close()
                        self.lock_file = None
                    return False

                # Wait and retry
                time.sleep(5)  # Check every 5 seconds

    def release(self):
        """Release the research queue lock."""
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_file = None
                logger.info(f"[{self.client_id}] 🔓 Research queue lock released")
            except Exception as e:
                logger.error(f"[{self.client_id}] Error releasing lock: {e}")

    def __enter__(self):
        """Context manager entry - acquire lock."""
        if not self.acquire():
            raise RuntimeError(f"[{self.client_id}] Failed to acquire research queue lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release lock."""
        self.release()
        return False  # Don't suppress exceptions
