#!/usr/bin/env python3
"""
PDF Consolidation Module - Universal File Converter
====================================================
Converts ANY file type to PDF and consolidates into {Client}-One.pdf

Supports:
- Text files (.txt, .md, .log, .json, .xml, .yaml, .yml)
- Spreadsheets (.csv, .xlsx, .xls, .ods)
- Documents (.docx, .doc, .odt, .rtf)
- Images (.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp)
- Presentations (.pptx, .ppt)
- PDFs (.pdf)
- And more via LibreOffice conversion
"""

import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import time

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


class UniversalPDFConsolidator:
    """Converts all files to PDF and consolidates them."""

    # File extensions we can handle
    TEXT_EXTENSIONS = {'.txt', '.md', '.log', '.json', '.xml', '.yaml', '.yml', '.py', '.js', '.html', '.css'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
    OFFICE_EXTENSIONS = {'.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.ods', '.odp', '.rtf', '.csv'}
    PDF_EXTENSION = {'.pdf'}

    def __init__(self, client_id: str, client_folder: Path, output_name: str = None):
        """
        Initialize consolidator.

        Args:
            client_id: Client identifier
            client_folder: Source folder with files
            output_name: Output PDF name (default: {client_id}-One.pdf)
        """
        self.client_id = client_id
        self.client_folder = Path(client_folder)
        self.output_name = output_name or f"{client_id}-One.pdf"
        self.temp_dir = None

    def __enter__(self):
        """Context manager: create temp directory."""
        self.temp_dir = tempfile.mkdtemp(prefix=f"pdf_conv_{self.client_id}_")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: cleanup temp directory."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def consolidate(self) -> Optional[Path]:
        """
        Main consolidation method.

        Returns:
            Path to consolidated PDF, or None if no files processed
        """
        if not self.client_folder.exists():
            logger.error(f"Client folder does not exist: {self.client_folder}")
            return None

        logger.info(f"[{self.client_id}] Starting PDF consolidation from: {self.client_folder}")

        # Collect all files
        all_files = [f for f in self.client_folder.iterdir() if f.is_file()]
        if not all_files:
            logger.warning(f"[{self.client_id}] No files found")
            return None

        logger.info(f"[{self.client_id}] Found {len(all_files)} files")

        # Convert each file to PDF
        pdf_files = []
        for file_path in sorted(all_files):
            pdf = self._convert_to_pdf(file_path)
            if pdf:
                pdf_files.append(pdf)

        if not pdf_files:
            logger.warning(f"[{self.client_id}] No files could be converted to PDF")
            return None

        logger.info(f"[{self.client_id}] Successfully converted {len(pdf_files)} files")

        # Merge all PDFs
        output_path = self.client_folder / self.output_name
        return self._merge_pdfs(pdf_files, output_path)

    def _convert_to_pdf(self, file_path: Path) -> Optional[Path]:
        """
        Convert a single file to PDF.

        Args:
            file_path: File to convert

        Returns:
            Path to converted PDF in temp directory
        """
        ext = file_path.suffix.lower()

        try:
            # Already a PDF
            if ext in self.PDF_EXTENSION:
                return file_path

            # Text files
            if ext in self.TEXT_EXTENSIONS:
                return self._text_to_pdf(file_path)

            # Images
            if ext in self.IMAGE_EXTENSIONS:
                return self._image_to_pdf(file_path)

            # Office documents (try LibreOffice)
            if ext in self.OFFICE_EXTENSIONS:
                return self._office_to_pdf(file_path)

            logger.warning(f"[{self.client_id}] Unsupported format: {ext} - {file_path.name}")
            return None

        except Exception as e:
            logger.error(f"[{self.client_id}] Error converting {file_path.name}: {e}")
            return None

    def _text_to_pdf(self, file_path: Path) -> Optional[Path]:
        """Convert text file to PDF using ReportLab."""
        if not REPORTLAB_AVAILABLE:
            logger.warning(f"ReportLab not available, skipping {file_path.name}")
            return None

        temp_pdf = Path(self.temp_dir) / f"{file_path.stem}.pdf"

        try:
            # Read content
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = file_path.read_text(encoding='latin-1')

            # Create PDF
            doc = SimpleDocTemplate(str(temp_pdf), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title = Paragraph(f"<b>{file_path.name}</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))

            # Content (split by lines)
            for line in content.split('\n')[:1000]:  # Limit to 1000 lines
                if line.strip():
                    p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), styles['Normal'])
                    story.append(p)

            doc.build(story)
            logger.debug(f"[{self.client_id}] Converted text: {file_path.name}")
            return temp_pdf

        except Exception as e:
            logger.error(f"[{self.client_id}] Text conversion failed for {file_path.name}: {e}")
            return None

    def _image_to_pdf(self, file_path: Path) -> Optional[Path]:
        """Convert image to PDF using PIL."""
        if not PIL_AVAILABLE:
            logger.warning(f"PIL not available, skipping {file_path.name}")
            return None

        temp_pdf = Path(self.temp_dir) / f"{file_path.stem}.pdf"

        try:
            img = Image.open(file_path)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

            img.save(temp_pdf, 'PDF', resolution=100.0)
            logger.debug(f"[{self.client_id}] Converted image: {file_path.name}")
            return temp_pdf

        except Exception as e:
            logger.error(f"[{self.client_id}] Image conversion failed for {file_path.name}: {e}")
            return None

    def _office_to_pdf(self, file_path: Path) -> Optional[Path]:
        """Convert Office document to PDF using LibreOffice."""
        temp_pdf = Path(self.temp_dir) / f"{file_path.stem}.pdf"

        try:
            # Try LibreOffice conversion
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', self.temp_dir,
                str(file_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and temp_pdf.exists():
                logger.debug(f"[{self.client_id}] Converted office doc: {file_path.name}")
                return temp_pdf
            else:
                logger.warning(f"[{self.client_id}] LibreOffice conversion failed: {file_path.name}")
                return None

        except FileNotFoundError:
            logger.warning(f"[{self.client_id}] LibreOffice not installed, skipping {file_path.name}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"[{self.client_id}] Conversion timeout: {file_path.name}")
            return None
        except Exception as e:
            logger.error(f"[{self.client_id}] Office conversion failed for {file_path.name}: {e}")
            return None

    def _merge_pdfs(self, pdf_files: List[Path], output_path: Path) -> Optional[Path]:
        """Merge multiple PDFs into one."""
        try:
            writer = PdfWriter()

            for pdf_path in pdf_files:
                try:
                    reader = PdfReader(str(pdf_path))
                    for page in reader.pages:
                        writer.add_page(page)
                    logger.debug(f"[{self.client_id}] Merged: {pdf_path.name}")
                except Exception as e:
                    logger.error(f"[{self.client_id}] Error merging {pdf_path.name}: {e}")

            # Write consolidated PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"[{self.client_id}] ✅ Created consolidated PDF: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"[{self.client_id}] PDF merge failed: {e}")
            return None
