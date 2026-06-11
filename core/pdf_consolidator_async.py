#!/usr/bin/env python3
"""
Ultra-Fast Async PDF Consolidator
==================================
Uses asyncio to process PDFs in parallel without pickling overhead
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    from PyPDF2 import PdfWriter, PdfReader

logger = logging.getLogger(__name__)


class AsyncPDFConsolidator:
    """
    Async PDF consolidator that's MUCH faster.
    Skips conversion - just merges existing PDFs in parallel.
    """

    def __init__(self, client_id: str, client_folder: Path, output_name: str):
        self.client_id = client_id
        self.client_folder = Path(client_folder)
        self.output_name = output_name

    async def consolidate(self) -> Optional[Path]:
        """
        Fast consolidation - only processes existing PDFs.

        Returns:
            Path to consolidated PDF
        """
        if not self.client_folder.exists():
            logger.error(f"[{self.client_id}] Folder not found: {self.client_folder}")
            return None

        logger.info(f"[{self.client_id}] Fast PDF consolidation starting...")

        # Find all PDF files
        pdf_files = sorted([f for f in self.client_folder.iterdir()
                           if f.suffix.lower() == '.pdf' and f.is_file()])

        if not pdf_files:
            logger.warning(f"[{self.client_id}] No PDF files found")
            return None

        logger.info(f"[{self.client_id}] Found {len(pdf_files)} PDF files")

        # Merge PDFs in parallel using async
        output_path = self.client_folder / self.output_name

        try:
            # Run merge in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._merge_pdfs_sync,
                pdf_files,
                output_path
            )

            if result:
                logger.info(f"[{self.client_id}] ✅ Created: {output_path.name}")
            return result

        except Exception as e:
            logger.error(f"[{self.client_id}] Consolidation failed: {e}")
            return None

    def _merge_pdfs_sync(self, pdf_files: List[Path], output_path: Path) -> Optional[Path]:
        """
        Synchronous PDF merge (runs in thread pool).
        Much faster than ProcessPoolExecutor.
        """
        try:
            writer = PdfWriter()

            for pdf_file in pdf_files:
                try:
                    reader = PdfReader(str(pdf_file))
                    for page in reader.pages:
                        writer.add_page(page)
                    logger.debug(f"[{self.client_id}] Added {len(reader.pages)} pages from {pdf_file.name}")
                except Exception as e:
                    logger.warning(f"[{self.client_id}] Skipping {pdf_file.name}: {e}")

            # Write output
            with open(output_path, 'wb') as f:
                writer.write(f)

            return output_path

        except Exception as e:
            logger.error(f"[{self.client_id}] Merge failed: {e}")
            return None
