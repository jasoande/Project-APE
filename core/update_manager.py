#!/usr/bin/env python3
"""
Update Manager
==============
Manages incremental updates to existing NotebookLM notebooks
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime

from core.notebook_manager import NotebookManager
from core.source_manager import SourceManager
from core.drive_manager import DriveManager

logger = logging.getLogger(__name__)


class UpdateManager:
    """Manages incremental updates to existing NotebookLM notebooks."""

    def __init__(self, client_id: str, config):
        """
        Initialize update manager.

        Args:
            client_id: Client identifier
            config: Configuration module
        """
        self.client_id = client_id
        self.config = config
        self.client_name = getattr(config, f"{client_id}_name", client_id)

        # Initialize managers
        self.notebook_manager = NotebookManager(client_id)
        self.source_manager = None  # Initialized after notebook is found

    def update_client_sources(
        self,
        notebook_name: str,
        force_drive_refresh: bool = True,
        re_run_research: bool = False
    ) -> Dict:
        """
        Update an existing notebook with new/changed sources from Google Drive.

        Steps:
        1. Find existing notebook
        2. Force refresh Drive cache if requested
        3. Download files from Drive
        4. Compare with existing sources in notebook
        5. Add only new files
        6. Deduplicate
        7. Optionally re-run research prompts
        8. Calculate updated quality score

        Args:
            notebook_name: Name of existing notebook to update
            force_drive_refresh: Force refresh of Google Drive cache
            re_run_research: Re-run research prompts with new sources

        Returns:
            Dict with update results
        """
        results = {
            "success": False,
            "notebook_id": None,
            "files_downloaded": 0,
            "new_sources_added": 0,
            "duplicates_removed": 0,
            "research_updated": False,
            "quality_score": None,
            "error": None
        }

        try:
            logger.info(f"[{self.client_id}] ========================================")
            logger.info(f"[{self.client_id}] UPDATE MODE: {self.client_name}")
            logger.info(f"[{self.client_id}] ========================================")

            # Step 1: Find existing notebook
            logger.info(f"[{self.client_id}] Looking for notebook: {notebook_name}")
            notebook_id = self.notebook_manager.find_notebook_by_name(notebook_name)

            if not notebook_id:
                error_msg = f"Notebook '{notebook_name}' not found. Create it first using fast/deep mode."
                logger.error(f"[{self.client_id}] ❌ {error_msg}")
                results["error"] = error_msg
                return results

            results["notebook_id"] = notebook_id
            logger.info(f"[{self.client_id}] ✅ Found notebook: {notebook_id}")

            # Initialize source manager
            self.source_manager = SourceManager(self.client_id, notebook_id)

            # Step 2: Get existing sources before update
            logger.info(f"[{self.client_id}] Fetching current sources...")
            existing_sources = self._get_existing_source_titles()
            logger.info(f"[{self.client_id}] Current sources: {len(existing_sources)}")

            # Step 3: List files from Google Drive (no download)
            logger.info(f"[{self.client_id}] Listing files from Google Drive...")
            client_folder_spec = getattr(self.config, f"{self.client_id}_folder", "")

            if not client_folder_spec:
                error_msg = "No Google Drive folder configured"
                logger.error(f"[{self.client_id}] ❌ {error_msg}")
                results["error"] = error_msg
                return results

            drive_config = getattr(self.config, 'DRIVE_CONFIG', {})

            drive_manager = DriveManager(
                client_id=self.client_id,
                folder_spec=client_folder_spec,
                cache_enabled=False,  # No caching needed for listing
                force_refresh=False,
                config=drive_config
            )

            # List files without downloading
            files_metadata = drive_manager.list_files_metadata()
            results["files_downloaded"] = len(files_metadata)
            logger.info(f"[{self.client_id}] Found {len(files_metadata)} files")

            # Step 4: Identify new files
            new_files = self._identify_new_drive_files(files_metadata, existing_sources)
            logger.info(f"[{self.client_id}] New files detected: {len(new_files)}")

            if not new_files:
                logger.info(f"[{self.client_id}] ✅ No new files to add")
                results["success"] = True
                return results

            # Step 5: Add new files to notebook by Drive URL
            logger.info(f"[{self.client_id}] Adding {len(new_files)} new sources...")
            for file_info in new_files:
                if self.source_manager.add_drive_url_source(
                    file_id=file_info['id'],
                    file_name=file_info['name'],
                    mime_type=file_info['mimeType']
                ):
                    results["new_sources_added"] += 1

            logger.info(f"[{self.client_id}] ✅ Added {results['new_sources_added']} new sources")

            # Step 6: Deduplicate sources
            logger.info(f"[{self.client_id}] Deduplicating sources...")
            duplicates = self.source_manager.deduplicate_sources()
            results["duplicates_removed"] = duplicates

            # Step 7: Optionally re-run research
            if re_run_research and results["new_sources_added"] > 0:
                logger.info(f"[{self.client_id}] Re-running research with updated sources...")
                self._rerun_research_prompts()
                results["research_updated"] = True

            # Step 8: Calculate quality score
            # (This would need to be implemented based on your quality scoring logic)
            # For now, just mark as successful
            results["success"] = True

            logger.info(f"[{self.client_id}] ✅ Update completed successfully!")
            logger.info(f"[{self.client_id}]    New sources: {results['new_sources_added']}")
            logger.info(f"[{self.client_id}]    Duplicates removed: {results['duplicates_removed']}")

            return results

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{self.client_id}] ❌ Update failed: {error_msg}")
            results["error"] = error_msg
            return results

    def _get_existing_source_titles(self) -> Set[str]:
        """
        Get set of existing source titles in notebook.

        Returns:
            Set of normalized source titles
        """
        sources = self.source_manager.list_sources()

        # Normalize titles for comparison
        titles = set()
        for source in sources:
            title = source.get('title', '')
            if title:
                # Normalize: remove extensions, lowercase, strip
                normalized = Path(title).stem.lower().strip()
                titles.add(normalized)

        return titles

    def _identify_new_drive_files(self, files_metadata: List[Dict], existing_titles: Set[str]) -> List[Dict]:
        """
        Identify Drive files that are not already in the notebook.

        Args:
            files_metadata: List of file metadata dicts from Drive (id, name, mimeType, etc.)
            existing_titles: Set of existing source titles

        Returns:
            List of new file metadata dicts to add
        """
        new_files = []

        for file_info in files_metadata:
            file_name = file_info['name']
            # Normalize filename for comparison
            normalized = Path(file_name).stem.lower().strip()

            if normalized not in existing_titles:
                new_files.append(file_info)
                logger.debug(f"[{self.client_id}]    NEW: {file_name}")
            else:
                logger.debug(f"[{self.client_id}]    SKIP (exists): {file_name}")

        return new_files

    def _identify_new_files(self, files: List[Path], existing_titles: Set[str]) -> List[Path]:
        """
        Identify files that are not already in the notebook.

        Args:
            files: List of file paths (PDF, DOCX, XLSX, PPTX, etc.)
            existing_titles: Set of existing source titles

        Returns:
            List of new file paths to add
        """
        new_files = []

        for file_path in files:
            # Normalize filename for comparison
            normalized = file_path.stem.lower().strip()

            if normalized not in existing_titles:
                new_files.append(file_path)
                logger.debug(f"[{self.client_id}]    NEW: {file_path.name}")
            else:
                logger.debug(f"[{self.client_id}]    SKIP (exists): {file_path.name}")

        return new_files

    def _rerun_research_prompts(self):
        """Re-run research prompts with updated sources."""
        # Get industry and subsegments
        industry = getattr(self.config, f"{self.client_id}_industry", None)
        subsegments = getattr(self.config, f"{self.client_id}_subsegments", None)

        # Run ask prompts (research queries)
        project_root = Path(__file__).parent.parent
        ask_prompts = [
            project_root / "ask_prompt_01.txt",
            project_root / "ask_prompt_02.txt",
            project_root / "ask_prompt_03.txt",
        ]

        for prompt_file in ask_prompts:
            if prompt_file.exists():
                logger.info(f"[{self.client_id}]    Running: {prompt_file.name}")
                self.source_manager.add_research_with_import(
                    query_file=prompt_file,
                    mode="fast",
                    client_name=self.client_name,
                    client_industry=industry,
                    client_subsegments=subsegments
                )
