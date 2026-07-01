#!/usr/bin/env python3
"""
Notebook Manager
================
Handles notebook deduplication and management
"""

import subprocess
import logging
import json
import re
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class NotebookManager:
    """Manages NotebookLM notebooks with deduplication."""

    def __init__(self, client_id: str):
        """
        Initialize notebook manager.

        Args:
            client_id: Client identifier
        """
        self.client_id = client_id

    def find_notebook_by_name(self, name: str) -> Optional[str]:
        """
        Find existing notebook by exact name match.

        Args:
            name: Exact notebook name to search for

        Returns:
            Notebook ID if found, None otherwise
        """
        try:
            logger.info(f"[{self.client_id}] Checking for existing notebook: {name}")

            result = subprocess.run(
                ["notebooklm", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.warning(f"[{self.client_id}] Failed to list notebooks")
                return None

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                # Handle both formats: {"notebooks": [...]} or [...]
                if isinstance(data, dict):
                    notebooks = data.get('notebooks', [])
                else:
                    notebooks = data
            except json.JSONDecodeError:
                # Fallback: parse text output
                return self._parse_text_list(result.stdout, name)

            # Find exact match
            for notebook in notebooks:
                # Skip if not a dict
                if not isinstance(notebook, dict):
                    continue

                notebook_name = notebook.get('name', notebook.get('title', ''))
                if notebook_name == name:
                    notebook_id = notebook.get('id', notebook.get('notebook_id', ''))
                    logger.info(f"[{self.client_id}] ✅ Found existing notebook: {notebook_id}")
                    return notebook_id

            logger.info(f"[{self.client_id}] No existing notebook found")
            return None

        except Exception as e:
            logger.error(f"[{self.client_id}] Error finding notebook: {e}")
            return None

    def _parse_text_list(self, output: str, name: str) -> Optional[str]:
        """Parse text-based list output as fallback."""
        # Look for lines with notebook ID and name
        # Format might be: "abc123-def456 - Notebook Name"
        uuid_pattern = r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

        for line in output.split('\n'):
            if name in line:
                match = re.search(uuid_pattern, line)
                if match:
                    return match.group(1)

        return None

    def create_notebook(self, name: str) -> Optional[str]:
        """
        Create a new notebook.

        Args:
            name: Notebook name

        Returns:
            Notebook ID if successful, None otherwise
        """
        try:
            logger.info(f"[{self.client_id}] Creating new notebook: {name}")

            result = subprocess.run(
                ["notebooklm", "create", name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"[{self.client_id}] Failed to create notebook: {result.stderr}")
                return None

            # Parse notebook ID from output
            notebook_id = self._parse_notebook_id(result.stdout)

            if notebook_id:
                logger.info(f"[{self.client_id}] ✅ Created notebook: {notebook_id}")
                return notebook_id
            else:
                logger.error(f"[{self.client_id}] Failed to parse notebook ID from: {result.stdout}")
                return None

        except Exception as e:
            logger.error(f"[{self.client_id}] Error creating notebook: {e}")
            return None

    def _parse_notebook_id(self, output: str) -> Optional[str]:
        """Parse notebook ID from CLI output."""
        # UUID pattern
        uuid_pattern = r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

        match = re.search(uuid_pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)

        # Try standalone ID
        output_clean = output.strip()
        if len(output_clean) < 100 and re.match(r'^[a-zA-Z0-9_-]+$', output_clean):
            return output_clean

        return None

    def get_or_create_notebook(self, name: str) -> Optional[str]:
        """
        Get existing notebook or create new one.

        This implements the deduplication requirement:
        - Check if notebook with exact name exists
        - If yes, use it
        - If no, create it

        Args:
            name: Notebook name

        Returns:
            Notebook ID
        """
        # First check for existing
        notebook_id = self.find_notebook_by_name(name)

        if notebook_id:
            logger.info(f"[{self.client_id}] Using existing notebook")
            return notebook_id

        # Create new
        notebook_id = self.create_notebook(name)
        return notebook_id

    def set_context(self, notebook_id: str) -> bool:
        """
        Set current notebook context.

        Args:
            notebook_id: Notebook ID to set as current

        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["notebooklm", "use", notebook_id],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"[{self.client_id}] Set notebook context: {notebook_id}")
                return True
            else:
                logger.error(f"[{self.client_id}] Failed to set context: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"[{self.client_id}] Error setting context: {e}")
            return False
