#!/usr/bin/env python3
"""
Source Manager
==============
Handles source import from research citations and deduplication
"""

import subprocess
import logging
import json
import re
from typing import List, Set, Dict, Optional
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class SourceManager:
    """Manages NotebookLM sources with import and deduplication."""

    def __init__(self, client_id: str, notebook_id: str):
        """
        Initialize source manager.

        Args:
            client_id: Client identifier
            notebook_id: Notebook ID to manage sources for
        """
        self.client_id = client_id
        self.notebook_id = notebook_id
        self._cached_sources = None
        self._cache_time = 0.0
        self._CACHE_TTL = 10.0

    def add_file_source(self, file_path: Path) -> bool:
        """
        Add a file as a source.

        Args:
            file_path: Path to file to add

        Returns:
            True if successful
        """
        try:
            logger.info(f"[{self.client_id}] Adding source: {file_path.name}")

            result = subprocess.run(
                ["notebooklm", "source", "add", str(file_path), "-n", self.notebook_id],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"[{self.client_id}] ✅ Added source: {file_path.name}")
                self._invalidate_source_cache()
                return True
            else:
                logger.error(f"[{self.client_id}] Failed to add source: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"[{self.client_id}] Error adding source: {e}")
            return False

    def delete_source(self, source_id: str) -> bool:
        """
        Delete a source from the notebook.

        Args:
            source_id: Source ID to delete

        Returns:
            True if successful
        """
        try:
            logger.info(f"[{self.client_id}] Deleting source: {source_id}")

            result = subprocess.run(
                ["notebooklm", "source", "delete", source_id, "-n", self.notebook_id, "--yes"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"[{self.client_id}] ✅ Deleted source: {source_id}")
                self._invalidate_source_cache()
                return True
            else:
                logger.error(f"[{self.client_id}] Failed to delete source: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"[{self.client_id}] Error deleting source: {e}")
            return False

    def delete_old_consolidated_pdfs(self, client_name: str) -> int:
        """
        Delete all old consolidated PDFs from the notebook.

        Args:
            client_name: Client name to match in consolidated PDF filenames

        Returns:
            Number of sources deleted
        """
        deleted_count = 0
        try:
            sources = self.list_sources()

            for source in sources:
                title = source.get('title', '')
                source_id = source.get('id', '')

                # Match pattern: {ClientName}-Consolidated-{timestamp}.pdf
                if f"{client_name}-Consolidated-" in title and title.endswith('.pdf'):
                    if self.delete_source(source_id):
                        deleted_count += 1

            if deleted_count > 0:
                logger.info(f"[{self.client_id}] 🗑️  Deleted {deleted_count} old consolidated PDF(s)")

            return deleted_count

        except Exception as e:
            logger.error(f"[{self.client_id}] Error deleting old consolidated PDFs: {e}")
            return deleted_count

    def has_consolidated_pdf(self, client_name: str) -> bool:
        """
        Check if notebook has a consolidated PDF source.

        Args:
            client_name: Client name to match in consolidated PDF filenames

        Returns:
            True if consolidated PDF exists in notebook
        """
        try:
            sources = self.list_sources()

            for source in sources:
                title = source.get('title', '')

                # Match pattern: {ClientName}-Consolidated-{timestamp}.pdf
                if f"{client_name}-Consolidated-" in title and title.endswith('.pdf'):
                    logger.info(f"[{self.client_id}] ✅ Found consolidated PDF in notebook: {title}")
                    return True

            logger.info(f"[{self.client_id}] 📄 No consolidated PDF found in notebook")
            return False

        except Exception as e:
            logger.warning(f"[{self.client_id}] Error checking for consolidated PDF: {e}")
            # On error, assume PDF is missing (safer to re-upload)
            return False

    def add_drive_url_source(self, file_id: str, file_name: str, mime_type: str) -> bool:
        """
        Add a Google Drive file as a source by URL.

        Args:
            file_id: Google Drive file ID
            file_name: Display name for the source
            mime_type: MIME type of the file

        Returns:
            True if successful
        """
        try:
            # Construct Google Drive URL
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"

            logger.info(f"[{self.client_id}] Adding Drive source: {file_name}")

            result = subprocess.run(
                ["notebooklm", "source", "add", drive_url, "--type", "url",
                 "--title", file_name, "-n", self.notebook_id],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"[{self.client_id}] ✅ Added Drive source: {file_name}")
                return True
            else:
                logger.error(f"[{self.client_id}] Failed to add Drive source: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"[{self.client_id}] Error adding Drive source: {e}")
            return False

    def add_research_with_import(self, query_file: Path, mode: str = "deep",
                                  client_name: str = None, client_industry: str = None,
                                  client_subsegments: str = None) -> Dict:
        """
        Add research query and import all cited sources.

        Args:
            query_file: Path to research query file
            mode: Research mode (fast or deep)
            client_name: Client name to substitute for $name variable
            client_industry: Client industry to substitute for $industry variable
            client_subsegments: Industry subsegments to substitute for $subsegments variable

        Returns:
            Dict with status and imported source count
        """
        # Retry configuration - Deep mode uses 3 attempts for critical failures, fast mode uses 5
        max_attempts = 3 if mode == "deep" else 5
        base_delay = 30.0  # Start with 30s delay

        self._invalidate_source_cache()

        try:
            logger.info(f"[{self.client_id}] Running research: {query_file.name} ({mode} mode, {max_attempts} attempt{'s' if max_attempts > 1 else ''})")

            # Read prompt and substitute variables
            prompt_text = query_file.read_text()

            # Substitute variables
            if client_name:
                prompt_text = prompt_text.replace('$name', client_name)
                logger.debug(f"[{self.client_id}] Substituted $name with: {client_name}")

            if client_industry:
                prompt_text = prompt_text.replace('$industry', client_industry)
                logger.debug(f"[{self.client_id}] Substituted $industry with: {client_industry}")

            if client_subsegments:
                prompt_text = prompt_text.replace('$subsegments', client_subsegments)
                logger.debug(f"[{self.client_id}] Substituted $subsegments with: {client_subsegments}")

            # Create temporary file with substituted prompt
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(prompt_text)
                tmp_path = tmp.name

            try:
                # Retry loop for transient errors
                for attempt in range(max_attempts):
                    try:
                        # Deep mode uses --mode deep with retry logic
                        if mode == "deep":
                            # Build command - always import sources (NotebookLM deduplicates)
                            cmd = [
                                "notebooklm", "source", "add-research",
                                "--mode", "deep",  # Use actual deep mode
                                "--prompt-file", tmp_path,
                                "-n", self.notebook_id,
                                "--import-all",  # CRITICAL: Always import, even on retry
                                "--cited-only",  # Only import sources actually cited
                                "--timeout", "3600"  # 60 minutes (30 min research + 30 min import)
                            ]

                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=4200  # 70 minutes (60 min + 10 min buffer)
                            )
                        else:
                            # Fast mode: standard fast research
                            cmd = [
                                "notebooklm", "source", "add-research",
                                "--mode", "fast",
                                "--prompt-file", tmp_path,
                                "-n", self.notebook_id,
                                "--import-all",  # CRITICAL: Always import, even on retry
                                "--cited-only",  # Only import sources actually cited
                                "--timeout", "900"  # 15 minutes (increased from 10 for safety)
                            ]

                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=1200  # 20 minutes (15 min + 5 min buffer)
                            )

                        if result.returncode == 0:
                            # Parse output to count imported sources
                            imported = self._count_imported_sources(result.stdout)

                            # CRITICAL: Validate sources were actually imported
                            min_sources = 10 if mode == "deep" else 5

                            if imported < min_sources:
                                logger.error(
                                    f"[{self.client_id}] ❌ Research succeeded but only imported {imported} sources "
                                    f"(expected {min_sources}+). Sources may not have been imported due to timeout."
                                )

                                # Retry if attempts remaining
                                if attempt < max_attempts - 1:
                                    retry_delay = base_delay * (2 ** attempt)
                                    logger.warning(
                                        f"[{self.client_id}] Retrying research with source import "
                                        f"(attempt {attempt + 1}/{max_attempts})..."
                                    )
                                    time.sleep(retry_delay)
                                    continue
                                else:
                                    # Max attempts reached with insufficient sources
                                    return {
                                        "success": False,
                                        "imported": imported,
                                        "error": f"Insufficient sources imported: {imported}/{min_sources} after {max_attempts} attempts"
                                    }

                            logger.info(f"[{self.client_id}] ✅ Research complete, imported {imported} sources")
                            return {
                                "success": True,
                                "imported": imported,
                                "output": result.stdout
                            }

                        # Check for retryable errors
                        stderr_lower = result.stderr.lower()
                        is_retryable = (
                            "rate limit" in stderr_lower or
                            "quota" in stderr_lower or
                            "rpc_code=3" in stderr_lower or
                            "rpc_code=9" in stderr_lower or
                            "rpc_code=8" in stderr_lower or  # RESOURCE_EXHAUSTED
                            "rpc_code=16" in stderr_lower or  # UNAUTHENTICATED
                            "unauthenticated" in stderr_lower or
                            "authentication expired" in stderr_lower or
                            "token refresh failed" in stderr_lower or
                            "transportservererror" in stderr_lower or
                            "failed precondition" in stderr_lower
                        )

                        if is_retryable and attempt < max_attempts - 1:
                            retry_delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"[{self.client_id}] Research transient error, retrying in {retry_delay}s "
                                f"(attempt {attempt + 1}/{max_attempts})"
                            )
                            time.sleep(retry_delay)
                            continue
                        else:
                            # Non-retryable error or max attempts reached
                            logger.error(f"[{self.client_id}] Research failed: {result.stderr}")
                            return {
                                "success": False,
                                "imported": 0,
                                "error": result.stderr
                            }

                    except subprocess.TimeoutExpired:
                        if attempt < max_attempts - 1:
                            retry_delay = base_delay * (2 ** attempt)
                            logger.warning(
                                f"[{self.client_id}] Research timeout, retrying in {retry_delay}s "
                                f"(attempt {attempt + 1}/{max_attempts})"
                            )
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.error(f"[{self.client_id}] Research timeout after {max_attempts} attempts")
                            return {"success": False, "imported": 0, "error": "Timeout"}

                # Should not reach here, but just in case
                return {"success": False, "imported": 0, "error": "Max retries exceeded"}

            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"[{self.client_id}] Research error: {e}")
            return {"success": False, "imported": 0, "error": str(e)}

    def _count_imported_sources(self, output: str) -> int:
        """Count how many sources were imported from output."""
        # Look for patterns like "Imported 5 sources" or "Added source:"
        count = 0

        # Try to find explicit count
        match = re.search(r'Imported\s+(\d+)\s+source', output, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Count individual "Added source" messages
        count = len(re.findall(r'Added source:', output, re.IGNORECASE))

        return count

    def extract_company_metadata(self, research_output: str) -> dict:
        """
        Extract company industry and subsegments from research output.

        Looks for COMPANY_METADATA block in the research results.

        Args:
            research_output: Raw output from research prompt

        Returns:
            dict with 'industry' and 'subsegments' keys, or empty dict if not found
        """
        metadata = {}

        try:
            # Look for COMPANY_METADATA block
            # Pattern: COMPANY_METADATA:\nIndustry: ...\nSubsegments: ...
            pattern = r'COMPANY_METADATA:\s*\n\s*Industry:\s*(.+?)\s*\n\s*Subsegments:\s*(.+?)(?:\n|```|\Z)'
            match = re.search(pattern, research_output, re.MULTILINE | re.DOTALL)

            if match:
                industry = match.group(1).strip()
                subsegments = match.group(2).strip()

                # Clean up any markdown artifacts
                industry = industry.replace('```', '').strip()
                subsegments = subsegments.replace('```', '').strip()

                metadata['industry'] = industry
                metadata['subsegments'] = subsegments

                logger.info(f"[{self.client_id}] Extracted metadata - Industry: {industry}, Subsegments: {subsegments}")
            else:
                logger.debug(f"[{self.client_id}] No COMPANY_METADATA block found in research output")

        except Exception as e:
            logger.warning(f"[{self.client_id}] Failed to extract company metadata: {e}")

        return metadata

    def _invalidate_source_cache(self):
        """Invalidate the cached source list after mutations."""
        self._cached_sources = None
        self._cache_time = 0.0

    def list_sources(self) -> List[Dict]:
        """
        List all sources in the notebook.

        Returns cached results if within TTL to avoid redundant subprocess calls.

        Returns:
            List of source dicts with id, title, url
        """
        now = time.time()
        if self._cached_sources is not None and (now - self._cache_time) < self._CACHE_TTL:
            return self._cached_sources

        sources = []
        try:
            result = subprocess.run(
                ["notebooklm", "source", "list", "-n", self.notebook_id, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"[{self.client_id}] Failed to list sources")
                return sources

            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    sources = data.get('sources', [])
                elif isinstance(data, list):
                    sources = data
            except json.JSONDecodeError:
                sources = self._parse_text_sources(result.stdout)

        except Exception as e:
            logger.error(f"[{self.client_id}] Error listing sources: {e}")
            return sources

        self._cached_sources = sources
        self._cache_time = time.time()
        return sources

    def _parse_text_sources(self, output: str) -> List[Dict]:
        """Parse text-based source list as fallback."""
        sources = []
        # Format might be: "src_123 - Title - URL"
        for line in output.split('\n'):
            if line.strip():
                parts = line.split(' - ')
                if len(parts) >= 2:
                    sources.append({
                        "id": parts[0].strip(),
                        "title": parts[1].strip() if len(parts) > 1 else "",
                        "url": parts[2].strip() if len(parts) > 2 else ""
                    })
        return sources

    def has_consolidated_pdf_source(self, client_name: str) -> bool:
        """
        Check if a consolidated PDF source exists in the notebook.

        Args:
            client_name: Client name to match in PDF title

        Returns:
            True if consolidated PDF found, False otherwise
        """
        try:
            sources = self.list_sources()

            # Look for sources with titles containing "{ClientName}-Consolidated"
            # Example: "Panasonic Avionics-Consolidated-2026-07-01_16-04.pdf"
            consolidated_pattern = f"{client_name}-Consolidated"

            for source in sources:
                title = source.get('title', '')
                if consolidated_pattern in title and title.endswith('.pdf'):
                    logger.info(f"[{self.client_id}] ✅ Found consolidated PDF in notebook: {title}")
                    return True

            logger.info(f"[{self.client_id}] ⚠️  No consolidated PDF found in notebook (pattern: {consolidated_pattern}*.pdf)")
            return False

        except Exception as e:
            logger.warning(f"[{self.client_id}] Error checking for consolidated PDF: {e}")
            # On error, assume PDF doesn't exist to be safe
            return False

    def verify_sources_imported(self, min_sources: int = 10) -> bool:
        """
        Verify that sources were actually imported after research.

        Args:
            min_sources: Minimum number of sources expected

        Returns:
            True if sufficient sources present, False otherwise
        """
        try:
            sources = self.list_sources()

            # Filter out PDF sources (only count web/research sources)
            # Web sources have URLs, PDFs typically don't (or have file:// URLs)
            # Note: Some sources may have url=None, so check for truthiness first
            research_sources = [
                s for s in sources
                if s.get('url') and str(s.get('url')).startswith('http')  # Web sources have http/https URLs
            ]

            source_count = len(research_sources)

            if source_count < min_sources:
                logger.error(
                    f"[{self.client_id}] ❌ Verification failed: "
                    f"Only {source_count} research sources found (expected {min_sources}+)"
                )
                logger.error(
                    f"[{self.client_id}]    Total sources in notebook: {len(sources)}"
                )
                logger.error(
                    f"[{self.client_id}]    Sources with http URLs: {source_count}"
                )
                # Log first few sources for debugging
                for idx, src in enumerate(sources[:5], 1):
                    url = src.get('url', 'NO_URL')
                    title = src.get('title', 'NO_TITLE')
                    logger.error(f"[{self.client_id}]      {idx}. {title[:50]}... URL: {url[:60]}...")
                return False

            logger.info(
                f"[{self.client_id}] ✅ Verified: {source_count} research sources imported"
            )
            return True

        except Exception as e:
            logger.error(f"[{self.client_id}] Source verification failed: {e}")
            return False

    def deduplicate_sources(self) -> int:
        """
        Remove duplicate sources from notebook.

        Sources are considered duplicates if they have:
        - Same URL (for web sources)
        - Same title (for file sources)

        Returns:
            Number of duplicates removed
        """
        try:
            logger.info(f"[{self.client_id}] Deduplicating sources...")

            sources = self.list_sources()

            if not sources:
                logger.info(f"[{self.client_id}] No sources to deduplicate")
                return 0

            # Track seen URLs and titles
            seen_urls: Set[str] = set()
            seen_titles: Set[str] = set()
            to_delete: List[str] = []

            for source in sources:
                source_id = source.get('id', '')
                # Handle None values - some sources may have None for url/title
                url = (source.get('url') or '').strip()
                title = (source.get('title') or '').strip()

                # Check URL duplicates
                if url:
                    if url in seen_urls:
                        logger.debug(f"[{self.client_id}] Duplicate URL: {url}")
                        to_delete.append(source_id)
                        continue
                    seen_urls.add(url)

                # Check title duplicates (for files without URLs)
                if not url and title:
                    if title in seen_titles:
                        logger.debug(f"[{self.client_id}] Duplicate title: {title}")
                        to_delete.append(source_id)
                        continue
                    seen_titles.add(title)

            # Delete duplicates
            deleted = 0
            for source_id in to_delete:
                if self._delete_source(source_id):
                    deleted += 1
                    time.sleep(1)  # Rate limiting

            logger.info(f"[{self.client_id}] ✅ Removed {deleted} duplicate sources")
            return deleted

        except Exception as e:
            logger.error(f"[{self.client_id}] Deduplication error: {e}")
            return 0

    def _delete_source(self, source_id: str) -> bool:
        """Delete a single source."""
        try:
            result = subprocess.run(
                ["notebooklm", "source", "delete", source_id, "-n", self.notebook_id, "-y"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self._invalidate_source_cache()
                return True
            return False

        except Exception as e:
            logger.error(f"[{self.client_id}] Error deleting source {source_id}: {e}")
            return False
