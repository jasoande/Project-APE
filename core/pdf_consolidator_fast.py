#!/usr/bin/env python3
"""
Fast PDF Consolidation Module
==============================
High-performance parallel PDF conversion and consolidation

Uses asyncio with thread pool for I/O-bound conversions to maximize throughput.
"""

import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    from PyPDF2 import PdfMerger as PdfWriter, PdfReader

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


# Worker functions (must be at module level for multiprocessing)

def _convert_text_worker(args):
    """Worker function for text-to-PDF conversion."""
    file_path, temp_dir, client_id = args

    if not REPORTLAB_AVAILABLE:
        return None

    try:
        temp_pdf = Path(temp_dir) / f"{file_path.stem}.pdf"

        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = file_path.read_text(encoding='latin-1')

        doc = SimpleDocTemplate(str(temp_pdf), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph(f"<b>{file_path.name}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Limit content to avoid huge PDFs
        for line in content.split('\n')[:1000]:
            if line.strip():
                p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), styles['Normal'])
                story.append(p)

        doc.build(story)
        return temp_pdf

    except Exception as e:
        logger.error(f"[{client_id}] Text conversion failed: {e}")
        return None


def _convert_image_worker(args):
    """Worker function for image-to-PDF conversion."""
    file_path, temp_dir, client_id = args

    if not PIL_AVAILABLE:
        return None

    try:
        temp_pdf = Path(temp_dir) / f"{file_path.stem}.pdf"

        img = Image.open(file_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        img.save(temp_pdf, 'PDF', resolution=100.0)
        return temp_pdf

    except Exception as e:
        logger.error(f"[{client_id}] Image conversion failed: {e}")
        return None


def _convert_office_worker(args):
    """
    Worker function for Office-to-PDF conversion.

    IMPORTANT: Never modifies original files on Drive.
    Creates a temporary copy, converts it, then cleans up.
    """
    file_path, temp_dir, client_id = args

    try:
        import shutil

        # Step 1: Copy original file to temp dir (never modify Drive cache)
        temp_copy = Path(temp_dir) / file_path.name
        shutil.copy2(file_path, temp_copy)

        # Step 2: Convert the COPY to PDF
        temp_pdf = Path(temp_dir) / f"{file_path.stem}-pdf.pdf"

        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', temp_dir,
            str(temp_copy)
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=60)

        # LibreOffice creates {filename}.pdf, rename to our format
        libreoffice_output = Path(temp_dir) / f"{file_path.stem}.pdf"
        if result.returncode == 0 and libreoffice_output.exists():
            libreoffice_output.rename(temp_pdf)
            # Step 3: Clean up the temporary copy
            temp_copy.unlink()
            return temp_pdf

        # Clean up on failure
        if temp_copy.exists():
            temp_copy.unlink()
        return None

    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"[{client_id}] Office conversion skipped: {type(e).__name__}")
        return None


class FastPDFConsolidator:
    """High-performance parallel PDF consolidator."""

    TEXT_EXTENSIONS = {'.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.py', '.js', '.html', '.css'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
    OFFICE_EXTENSIONS = {'.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.ods', '.odp', '.rtf', '.csv'}
    PDF_EXTENSION = {'.pdf'}

    def __init__(self, client_id: str, client_folder: Path, output_name: str = None, output_dir: Path = None):
        self.client_id = client_id
        self.client_folder = Path(client_folder)
        self.output_name = output_name or f"{client_id}-One.pdf"
        self.output_dir = Path(output_dir) if output_dir else self.client_folder
        self.temp_dir = None
        self.max_workers = max(1, multiprocessing.cpu_count() - 1)

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix=f"pdf_conv_{self.client_id}_")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def consolidate(self) -> Optional[Path]:
        """
        Parallel consolidation - uses all CPU cores.

        Returns:
            Path to consolidated PDF
        """
        if not self.client_folder.exists():
            logger.error(f"[{self.client_id}] Folder not found: {self.client_folder}")
            return None

        logger.info(f"[{self.client_id}] Fast parallel PDF consolidation starting...")

        # Collect files by type
        all_files = [f for f in self.client_folder.iterdir() if f.is_file()]
        if not all_files:
            logger.warning(f"[{self.client_id}] No files found")
            return None

        text_files = []
        image_files = []
        office_files = []
        pdf_files = []

        for f in sorted(all_files):
            ext = f.suffix.lower()
            if ext in self.TEXT_EXTENSIONS:
                text_files.append(f)
            elif ext in self.IMAGE_EXTENSIONS:
                image_files.append(f)
            elif ext in self.OFFICE_EXTENSIONS:
                office_files.append(f)
            elif ext in self.PDF_EXTENSION:
                pdf_files.append(f)

        logger.info(f"[{self.client_id}] Found: {len(text_files)} text, {len(image_files)} images, "
                   f"{len(office_files)} office, {len(pdf_files)} PDFs")

        # Convert ALL file types in parallel using single executor pool
        converted_pdfs = []
        all_conversion_tasks = []

        # Collect all conversion tasks
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit text file conversions
            for text_file in text_files:
                future = executor.submit(_convert_text_worker, (text_file, self.temp_dir, self.client_id))
                all_conversion_tasks.append(future)

            # Submit image conversions
            for image_file in image_files:
                future = executor.submit(_convert_image_worker, (image_file, self.temp_dir, self.client_id))
                all_conversion_tasks.append(future)

            # Submit office doc conversions (NOW IN PARALLEL!)
            # LibreOffice can handle parallel instances with different temp dirs
            for office_file in office_files:
                future = executor.submit(_convert_office_worker, (office_file, self.temp_dir, self.client_id))
                all_conversion_tasks.append(future)

            # Process results as they complete
            logger.info(f"[{self.client_id}] Converting {len(all_conversion_tasks)} files in parallel...")
            for future in as_completed(all_conversion_tasks):
                try:
                    result = future.result()
                    if result:
                        converted_pdfs.append(result)
                except Exception as e:
                    logger.warning(f"[{self.client_id}] Conversion failed: {e}")

        # Add existing PDFs
        converted_pdfs.extend(pdf_files)

        if not converted_pdfs:
            logger.warning(f"[{self.client_id}] No files converted")
            return None

        logger.info(f"[{self.client_id}] Converted {len(converted_pdfs)} files, merging...")

        # Merge all PDFs to output directory (writable)
        output_path = self.output_dir / self.output_name
        return self._merge_pdfs(converted_pdfs, output_path)

    def _merge_pdfs(self, pdf_files: List[Path], output_path: Path) -> Optional[Path]:
        """Merge multiple PDFs into one."""
        try:
            writer = PdfWriter()

            for pdf_path in sorted(pdf_files):
                try:
                    reader = PdfReader(str(pdf_path))
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    logger.error(f"[{self.client_id}] Error merging {pdf_path.name}: {e}")

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"[{self.client_id}] ✅ Created: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"[{self.client_id}] PDF merge failed: {e}")
            return None
