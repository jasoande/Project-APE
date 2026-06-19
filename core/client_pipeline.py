#!/usr/bin/env python3
"""
Client Pipeline
===============
Complete pipeline execution for a single client
"""

import subprocess
import logging
import time
import json
import random
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth_manager import AuthManager
from core.notebook_manager import NotebookManager
from core.source_manager import SourceManager
from core.pdf_consolidator_fast import FastPDFConsolidator
from core.drive_manager import DriveManager
# from core.research_queue import ResearchQueue  # Removed - no longer using queue lock

# Gemini Agent (optional - enabled via config)
try:
    from core.gemini_agent import GeminiOrchestrationAgent
    GEMINI_AGENT_AVAILABLE = True
except ImportError:
    GEMINI_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClientPipeline:
    """Executes complete pipeline for a single client."""

    def __init__(self, client_id: str, config, status_file: Path, mode: str = "fast"):
        """
        Initialize client pipeline.

        Args:
            client_id: Client identifier (e.g., 'merck_test')
            config: Configuration module
            status_file: Path to status JSON file
            mode: Execution mode (fast or deep)
        """
        self.client_id = client_id
        self.config = config
        self.status_file = status_file
        self.mode = mode

        # Get client details from config
        self.client_name = getattr(config, f"{client_id}_name", client_id)
        client_folder_spec = getattr(config, f"{client_id}_folder", "")

        # Handle Google Drive folders - download before pipeline starts
        self.client_folder = self._setup_client_folder(client_folder_spec)

        # Industry and subsegments will be determined in execute()
        # Either from manual config or Gemini AI detection
        self.industry = None
        self.subsegments = None

        # Get global persona setting (role perspective for chat prompts)
        self.persona = getattr(config, "persona", "Red Hat solutions architect")

        # Initialize managers
        self.auth_manager = AuthManager()
        self.notebook_manager = NotebookManager(client_id)
        self.source_manager = None  # Initialized after notebook creation

        self.notebook_id = None
        self.project_root = Path(__file__).parent.parent

        # Select timing configuration based on mode
        self.timings = config.DEEP_TIMINGS if mode == "deep" else config.TIMINGS

    def _setup_client_folder(self, folder_spec: str) -> Path:
        """
        Setup client folder - download from Drive if needed, or use local path.

        Args:
            folder_spec: Local path or Google Drive URL/ID

        Returns:
            Path to local folder (downloaded or original)
        """
        # Check if Drive folder
        if isinstance(folder_spec, str) and ('drive.google.com' in folder_spec or folder_spec.startswith('drive://')):
            # Download from Drive
            drive_config = getattr(self.config, 'DRIVE_CONFIG', {})

            with DriveManager(
                client_id=self.client_id,
                folder_spec=folder_spec,
                cache_enabled=drive_config.get('cache_enabled', True),
                config=drive_config
            ) as temp_dir:
                # DriveManager returns temp/cache directory - use it directly
                return Path(temp_dir)
        else:
            # Local folder
            return Path(folder_spec) if folder_spec else Path.cwd()

    def update_status(self, step: str, progress: int, status: str = "RUNNING", **kwargs):
        """Update status file for dashboard."""
        try:
            # Read existing status to preserve start_time
            existing_start_time = None
            if self.status_file.exists():
                try:
                    with open(self.status_file, 'r') as f:
                        existing_data = json.load(f)
                        existing_start_time = existing_data.get('start_time')
                except:
                    pass  # If file doesn't exist or is corrupted, proceed without start_time

            # Remove start_time from kwargs if it's None (don't let it override)
            if 'start_time' in kwargs and kwargs['start_time'] is None:
                kwargs = {k: v for k, v in kwargs.items() if k != 'start_time'}

            status_data = {
                "name": self.client_name,
                "token": self.client_id,
                "step": step,
                "progress": progress,
                "status": status.upper(),
                "notebook_id": self.notebook_id,
                "mode": self.mode,
                "last_update": time.time(),
                **kwargs
            }

            # Preserve start_time from initial status file creation
            if 'start_time' not in status_data:
                if existing_start_time is not None:
                    status_data["start_time"] = existing_start_time
                else:
                    # First time creating status in pipeline - set start_time now
                    status_data["start_time"] = time.time()

            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)

        except Exception as e:
            logger.error(f"[{self.client_id}] Failed to update status: {e}")

    def execute(self) -> bool:
        """
        Execute complete pipeline with optional Gemini agent orchestration.

        Returns:
            True if successful, False otherwise
        """
        # Check if Gemini Agent is enabled
        agent_config = getattr(self.config, 'GEMINI_AGENT_CONFIG', {})
        use_agent = agent_config.get('enabled', False) and GEMINI_AGENT_AVAILABLE

        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if use_agent and not gemini_api_key:
            logger.warning(f"[{self.client_id}] Gemini agent enabled but API key missing - falling back to standard execution")
            use_agent = False

        # Check for update mode
        if self.mode == "update":
            return self._execute_update_mode()
        elif use_agent:
            return self._execute_with_agent(gemini_api_key)
        else:
            return self._execute_standard()

    def _execute_standard(self) -> bool:
        """
        Execute pipeline without Gemini agent (standard mode).

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[{self.client_id}] ========================================")
            logger.info(f"[{self.client_id}] Starting pipeline for {self.client_name}")
            logger.info(f"[{self.client_id}] Mode: {self.mode.upper()}")
            logger.info(f"[{self.client_id}] ========================================")

            # No initial delay - removed to maximize speed

            # Step 0.5: Determine Industry and Subsegments (Gemini AI or manual config)
            self.update_status("Determining industry and subsegments...", 3)
            self.industry, self.subsegments = self._determine_industry_and_subsegments()
            logger.info(f"[{self.client_id}] Industry: {self.industry}")
            logger.info(f"[{self.client_id}] Subsegments: {self.subsegments}")

            # Step 1: Check Authentication (force fresh check)
            self.update_status("Checking authentication...", 5)
            if not self.auth_manager.ensure_authenticated(self.client_id, force_check=True):
                raise Exception("Authentication required - please run: notebooklm login")

            # Step 2: Get or Create Notebook (with deduplication)
            self.update_status("Checking for existing notebook...", 10)

            # Generate notebook name in format: DEV_{client_id}-TEST
            # Always use client_id to ensure readable, consistent names
            notebook_name = f"DEV_{self.client_id}-TEST"

            logger.info(f"[{self.client_id}] Generated notebook name: {notebook_name}")

            # Check if notebook exists
            existing_notebook = self.notebook_manager.find_notebook_by_name(notebook_name)
            is_existing = existing_notebook is not None

            self.notebook_id = self.notebook_manager.get_or_create_notebook(notebook_name)

            if not self.notebook_id:
                raise Exception("Failed to get/create notebook")

            # Set notebook context
            if not self.notebook_manager.set_context(self.notebook_id):
                raise Exception("Failed to set notebook context")

            self.update_status("Notebook ready", 15, notebook_id=self.notebook_id)

            # Check if consolidated PDF already exists (from previous run)
            # If it exists, skip PDF consolidation but ALWAYS run research for fresh web data
            consolidated_pdf_path = self.client_folder / f"{self.client_name}-One.pdf"
            pdf_exists = consolidated_pdf_path.exists()

            if pdf_exists:
                logger.info(f"[{self.client_id}] ✅ Found existing PDF: {consolidated_pdf_path.name}")
                logger.info(f"[{self.client_id}] Skipping PDF consolidation, but will run fresh research")

            # Initialize source manager now that we have notebook_id
            self.source_manager = SourceManager(self.client_id, self.notebook_id)

            # Step 3: PDF Consolidation (skip if exists)
            if pdf_exists:
                consolidated_pdf = consolidated_pdf_path
                logger.info(f"[{self.client_id}] Using existing PDF: {consolidated_pdf.name}")
            else:
                consolidated_pdf = self._consolidate_pdfs()
                self.update_status("PDF consolidation complete", 25)

            # Step 4: Upload Consolidated PDF (only if new notebook or PDF was regenerated)
            if consolidated_pdf and not is_existing:
                self._upload_pdf(consolidated_pdf)
                self.update_status("Sources uploaded", 30)
            elif is_existing:
                logger.info(f"[{self.client_id}] Notebook exists, skipping PDF upload")
                self.update_status("PDF upload skipped", 30)

            # Step 5: ALWAYS Run Ask Prompts (Research) for fresh web data
            # Deep mode deduplicates after EACH prompt (inside _run_ask_prompts)
            # Fast mode deduplicates once at the end (below)
            self._run_ask_prompts()
            self.update_status("Research complete", 60)

            # Step 6: Deduplicate Sources (Fast mode only - deep mode already did it)
            if self.mode == "fast":
                # Fast mode: Deduplicate once (no wait - NotebookLM processes async)
                logger.info(f"[{self.client_id}] Deduplicating sources...")

                self._deduplicate_sources()
                self.update_status("Sources deduplicated", 65)
            else:
                # Deep mode: Already deduplicated after each prompt
                logger.info(f"[{self.client_id}] Sources already deduplicated (deep mode)")
                self.update_status("Sources deduplicated", 65)

            # Step 7: Run Chat Prompts - Sequential with Notes
            self._run_chat_prompts()
            self.update_status("Chat prompts complete", 95)

            # Step 8: Generate Mind Map
            self._generate_mindmap()

            # Step 9: Calculate Quality Score
            quality_score = self._calculate_quality_score()

            self.update_status("Mind map generated", 100, status="COMPLETE", quality_score=quality_score)

            logger.info(f"[{self.client_id}] ✅ Pipeline completed successfully!")
            logger.info(f"[{self.client_id}] 📊 Quality Score: {quality_score}/10")
            return True

        except Exception as e:
            logger.error(f"[{self.client_id}] ❌ Pipeline failed: {e}")
            self.update_status(f"Failed: {str(e)}", 0, status="FAILED", error=str(e))
            return False

    def _execute_with_agent(self, gemini_api_key: str) -> bool:
        """
        Execute pipeline with Gemini agent orchestration.

        Args:
            gemini_api_key: Gemini API key

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[{self.client_id}] ========================================")
            logger.info(f"[{self.client_id}] Starting AGENT-ORCHESTRATED pipeline for {self.client_name}")
            logger.info(f"[{self.client_id}] Mode: {self.mode.upper()}")
            logger.info(f"[{self.client_id}] ========================================")

            # Initialize Gemini agent
            agent = GeminiOrchestrationAgent(
                client_id=self.client_id,
                config=self.config,
                gemini_api_key=gemini_api_key,
                status_updater=lambda step, progress: self.update_status(step, progress)
            )

            # Define pipeline steps
            pipeline_steps = [
                ('determine_industry', lambda: self._determine_industry_step()),
                ('check_auth', lambda: self.auth_manager.ensure_authenticated(self.client_id, force_check=True)),
                ('create_notebook', lambda: self._create_notebook_step()),
                ('prepare_pdf', lambda: self._prepare_pdf_step()),
                ('upload_pdf', lambda: self._upload_pdf_step()),
                ('run_research', lambda: self._run_ask_prompts_step()),
                ('deduplicate', lambda: self._deduplicate_step()),
                ('run_chat', lambda: self._run_chat_prompts_step()),
                ('generate_mindmap', lambda: self._generate_mindmap_step()),
            ]

            # Execute with agent monitoring
            quality_target = self.config.GEMINI_AGENT_CONFIG.get('quality_target', 8.5)
            result = agent.execute_pipeline(
                pipeline_steps=pipeline_steps,
                quality_target=quality_target,
                ensure_all_artifacts=True
            )

            # Update final status
            if result.success:
                self.update_status(
                    "Pipeline complete",
                    100,
                    status="COMPLETE",
                    quality_score=result.quality_score
                )
                logger.info(f"[{self.client_id}] ✅ Agent-orchestrated pipeline completed successfully!")
                logger.info(f"[{self.client_id}] 📊 Quality Score: {result.quality_score:.1f}/10")
            else:
                self.update_status(
                    f"Failed: {result.error_summary}",
                    0,
                    status="FAILED",
                    error=result.error_summary
                )
                logger.error(f"[{self.client_id}] ❌ Agent-orchestrated pipeline failed")

            return result.success

        except Exception as e:
            logger.error(f"[{self.client_id}] ❌ Agent-orchestrated pipeline failed: {e}")
            self.update_status(f"Failed: {str(e)}", 0, status="FAILED", error=str(e))
            return False

    # Pipeline step wrappers for agent execution

    def _determine_industry_step(self) -> bool:
        """Determine industry and subsegments."""
        self.industry, self.subsegments = self._determine_industry_and_subsegments()
        logger.info(f"[{self.client_id}] Industry: {self.industry}")
        logger.info(f"[{self.client_id}] Subsegments: {self.subsegments}")
        return True

    def _create_notebook_step(self) -> Tuple[bool, str]:
        """Create or get notebook - returns (success, notebook_id)."""
        notebook_name = f"DEV_{self.client_id}-TEST"
        existing_notebook = self.notebook_manager.find_notebook_by_name(notebook_name)

        # Track if this is a new notebook
        self._notebook_just_created = (existing_notebook is None)

        self.notebook_id = self.notebook_manager.get_or_create_notebook(notebook_name)

        if not self.notebook_id:
            raise Exception("Failed to get/create notebook")

        if not self.notebook_manager.set_context(self.notebook_id):
            raise Exception("Failed to set notebook context")

        # Initialize source manager
        self.source_manager = SourceManager(self.client_id, self.notebook_id)

        return (True, self.notebook_id)

    def _prepare_pdf_step(self) -> bool:
        """Prepare PDF - consolidate if needed."""
        consolidated_pdf_path = self.client_folder / f"{self.client_name}-One.pdf"
        pdf_exists = consolidated_pdf_path.exists()

        if pdf_exists:
            logger.info(f"[{self.client_id}] ✅ Found existing PDF: {consolidated_pdf_path.name}")
            self.consolidated_pdf = consolidated_pdf_path
        else:
            self.consolidated_pdf = self._consolidate_pdfs()

        return True

    def _upload_pdf_step(self) -> bool:
        """Upload PDF to NotebookLM - always upload to catch new files from Drive."""
        if hasattr(self, 'consolidated_pdf') and self.consolidated_pdf:
            # Always upload PDF to ensure latest Drive files are included
            self._upload_pdf(self.consolidated_pdf)
            logger.info(f"[{self.client_id}] ✅ PDF uploaded to NotebookLM")
        return True

    def _run_ask_prompts_step(self) -> bool:
        """Run research prompts."""
        self._run_ask_prompts()
        return True

    def _deduplicate_step(self) -> bool:
        """Deduplicate sources."""
        if self.mode == "fast":
            self._deduplicate_sources()
        return True

    def _run_chat_prompts_step(self) -> bool:
        """Run chat prompts."""
        self._run_chat_prompts()
        return True

    def _generate_mindmap_step(self) -> bool:
        """Generate mind map."""
        self._generate_mindmap()
        return True

    def _determine_industry_and_subsegments(self) -> Tuple[str, str]:
        """
        Determine industry and subsegments using Claude AI auto-detection or manual config.

        Priority:
        1. Manual config in vars.py (if provided - for override)
        2. Claude AI auto-detection (default - uses Anthropic or Gemini)
        3. Error: require at least one AI API key

        Returns:
            Tuple of (industry, subsegments)

        Raises:
            ValueError: If no manual config and no AI API keys available
        """
        config = self.config
        client_id = self.client_id

        # Check for manual overrides in config
        manual_industry = getattr(config, f"{client_id}_industry", None)
        manual_subsegments = getattr(config, f"{client_id}_subsegments", None)

        if manual_industry and manual_subsegments:
            logger.info(f"[{client_id}] Using manual industry configuration")
            logger.info(f"[{client_id}] Industry: {manual_industry}")
            logger.info(f"[{client_id}] Subsegments: {manual_subsegments}")
            return manual_industry, manual_subsegments

        # Use Claude AI auto-detection
        logger.info(f"[{client_id}] Using Claude AI for automatic industry detection")

        # Import Claude industry detector
        from core.claude_industry_detector import ClaudeIndustryDetector

        # Check for API keys
        if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('GEMINI_API_KEY'):
            raise ValueError(
                f"Client {client_id}: No industry/subsegments in vars.py "
                "and no AI API keys (ANTHROPIC_API_KEY or GEMINI_API_KEY) found. "
                "Please add an API key to your .env file or provide manual config in vars.py."
            )

        # Initialize Claude detector (falls back to Gemini if Anthropic unavailable)
        detector = ClaudeIndustryDetector(config)

        # Get Drive files list for better detection
        drive_files = None
        if self.client_folder and self.client_folder.exists():
            drive_files = [f.name for f in self.client_folder.iterdir() if f.is_file()]

        # Detect industry and subsegments
        self.update_status("Auto-detecting industry with Claude AI", 1, status="RUNNING")
        industry, subsegments = detector.detect_industry(
            client_name=self.client_name,
            drive_files=drive_files
        )

        logger.info(f"[{client_id}] Industry: {industry}")
        logger.info(f"[{client_id}] Subsegments: {subsegments}")

        return industry, subsegments

    def _consolidate_pdfs(self) -> Optional[Path]:
        """Consolidate all files into {Client}-One.pdf - converts everything to PDF first"""
        if not self.client_folder.exists():
            logger.warning(f"[{self.client_id}] Client folder not found: {self.client_folder}")
            return None

        try:
            logger.info(f"[{self.client_id}] Consolidating all files to PDF...")
            self.update_status("Converting files to PDF...", 20)

            # Use FastPDFConsolidator which converts ALL file types to PDF
            # Handles: PDFs, text files, images, office docs (xlsx, docx, pptx)
            # Write consolidated PDF to logs directory (writable in containers)
            logs_dir = Path(vars.LOGS_DIR if hasattr(vars, 'LOGS_DIR') else './logs')
            with FastPDFConsolidator(
                self.client_id,
                self.client_folder,
                f"{self.client_name}-One.pdf",
                output_dir=logs_dir
            ) as consolidator:
                consolidated = consolidator.consolidate()

                if consolidated:
                    logger.info(f"[{self.client_id}] ✅ Consolidated PDF: {consolidated.name}")
                    return consolidated
                else:
                    logger.warning(f"[{self.client_id}] No files to consolidate")
                    return None

        except Exception as e:
            logger.error(f"[{self.client_id}] PDF consolidation failed: {e}")
            return None

    def _upload_pdf(self, pdf_path: Path):
        """Upload consolidated PDF to notebook."""
        try:
            logger.info(f"[{self.client_id}] Uploading consolidated PDF...")
            self.source_manager.add_file_source(pdf_path)
        except Exception as e:
            logger.error(f"[{self.client_id}] PDF upload failed: {e}")

    def _run_ask_prompts(self):
        """Run research (ask) prompts sequentially."""
        ask_prompts = sorted(self.project_root.glob("ask_*.txt"))

        if not ask_prompts:
            logger.warning(f"[{self.client_id}] No ask prompts found")
            return

        # Both modes now run in parallel with staggered start delays
        # Deep mode: Small delay to avoid simultaneous API calls
        # Fast mode: Random delay for additional spread
        if self.mode == "deep":
            import random
            delay = random.uniform(0, 15)
            logger.info(f"[{self.client_id}] ⏱️  Anti-collision delay: {delay:.1f}s")
            time.sleep(delay)

            logger.info(f"[{self.client_id}] Running {len(ask_prompts)} research prompts...")

            for idx, prompt_file in enumerate(ask_prompts, 1):
                try:
                    progress = 30 + (idx / len(ask_prompts)) * 30  # 30-60%
                    self.update_status(f"Research {idx}/{len(ask_prompts)}: {prompt_file.stem}", int(progress))

                    logger.info(f"[{self.client_id}] Research prompt: {prompt_file.name}")

                    # Run research with source import (with variable substitution)
                    result = self.source_manager.add_research_with_import(
                        prompt_file,
                        mode="deep",
                        client_name=self.client_name,
                        client_industry=self.industry,
                        client_subsegments=self.subsegments
                    )

                    if result["success"]:
                        logger.info(f"[{self.client_id}] ✅ Imported {result['imported']} sources")
                    else:
                        logger.warning(f"[{self.client_id}] Research failed: {result.get('error')}")

                    # Deduplicate after EACH research prompt (deep mode only)
                    logger.info(f"[{self.client_id}] Deduplicating sources (after prompt {idx})...")
                    removed = self.source_manager.deduplicate_sources()
                    logger.info(f"[{self.client_id}] ✅ Removed {removed} duplicates")

                except Exception as e:
                    logger.error(f"[{self.client_id}] Ask prompt failed {prompt_file.name}: {e}")

        else:
            # Fast mode: small random delay, then run in parallel
            import random
            delay = random.uniform(0, 15)
            logger.info(f"[{self.client_id}] ⏱️  Anti-rate-limit delay: {delay:.1f}s")
            time.sleep(delay)

            logger.info(f"[{self.client_id}] Running {len(ask_prompts)} research prompts...")

            for idx, prompt_file in enumerate(ask_prompts, 1):
                try:
                    progress = 30 + (idx / len(ask_prompts)) * 30  # 30-60%
                    self.update_status(f"Research {idx}/{len(ask_prompts)}: {prompt_file.stem}", int(progress))

                    logger.info(f"[{self.client_id}] Research prompt: {prompt_file.name}")

                    # Run research with source import (with variable substitution)
                    result = self.source_manager.add_research_with_import(
                        prompt_file,
                        mode="fast",
                        client_name=self.client_name,
                        client_industry=self.industry,
                        client_subsegments=self.subsegments
                    )

                    if result["success"]:
                        logger.info(f"[{self.client_id}] ✅ Imported {result['imported']} sources")
                    else:
                        logger.warning(f"[{self.client_id}] Research failed: {result.get('error')}")

                except Exception as e:
                    logger.error(f"[{self.client_id}] Ask prompt failed {prompt_file.name}: {e}")

    def _deduplicate_sources(self):
        """Deduplicate sources after research."""
        try:
            logger.info(f"[{self.client_id}] Deduplicating sources...")
            removed = self.source_manager.deduplicate_sources()
            logger.info(f"[{self.client_id}] ✅ Removed {removed} duplicates")
        except Exception as e:
            logger.error(f"[{self.client_id}] Deduplication failed: {e}")

    def _run_chat_prompts(self):
        """Run chat prompts sequentially with note creation."""
        chat_prompts = sorted(self.project_root.glob("chat_prompt_consolidated_*.txt"))

        if not chat_prompts:
            logger.warning(f"[{self.client_id}] No chat prompts found")
            return

        # Descriptive titles for consolidated chat prompts (6 instead of 12)
        note_titles = {
            'chat_prompt_consolidated_01.txt': 'Industry Analysis & Customer Business Profile',
            'chat_prompt_consolidated_02.txt': 'Innovation Assessment & Executive Summary',
            'chat_prompt_consolidated_03.txt': 'Technology Partners & Red Hat Value Propositions',
            'chat_prompt_consolidated_04.txt': 'Strategic Ideas & How Might We Statements',
            'chat_prompt_consolidated_05.txt': 'Account Team & Partner Onboarding',
            'chat_prompt_consolidated_06.txt': 'Comprehensive Red Hat Account Plan',
        }

        logger.info(f"[{self.client_id}] Running {len(chat_prompts)} chat prompts...")

        for idx, prompt_file in enumerate(chat_prompts, 1):
            try:
                # No jitter delay - removed to maximize speed
                progress = 65 + (idx / len(chat_prompts)) * 30  # 65-95%
                self.update_status(f"Chat {idx}/{len(chat_prompts)}: {prompt_file.stem}", int(progress))

                logger.info(f"[{self.client_id}] Chat prompt: {prompt_file.name}")

                # Read prompt and substitute variables
                prompt_text = prompt_file.read_text()
                prompt_text = prompt_text.replace('$name', self.client_name)
                prompt_text = prompt_text.replace('$industry', self.industry)
                prompt_text = prompt_text.replace('$subsegments', self.subsegments or 'various segments')
                prompt_text = prompt_text.replace('$persona', self.persona)

                # Create temporary file with substituted prompt
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(prompt_text)
                    tmp_path = tmp.name

                try:
                    # Execute ask command with --save-as-note flag (with retry for rate limits)
                    max_retries = 3
                    retry_delay = 60  # Wait 60 seconds on rate limit

                    for attempt in range(max_retries):
                        # Get descriptive title or fallback to filename
                        note_title = note_titles.get(prompt_file.name, prompt_file.stem.replace('_', ' ').title())

                        result = subprocess.run(
                            [
                                "notebooklm", "ask",
                                "--prompt-file", tmp_path,  # Use substituted prompt
                                "-n", self.notebook_id,
                                "--save-as-note",
                                "-t", note_title
                            ],
                            capture_output=True,
                            text=True,
                            timeout=180
                        )

                        if result.returncode == 0:
                            logger.info(f"[{self.client_id}] ✅ Created note: {prompt_file.stem}")
                            break
                        elif "rate limit" in result.stderr.lower() or "quota" in result.stderr.lower() or "rpc_code=3" in result.stderr.lower() or "rpc_code=9" in result.stderr.lower() or "rpc_code=8" in result.stderr.lower():
                            if attempt < max_retries - 1:
                                logger.warning(f"[{self.client_id}] Quota/rate limit hit, waiting {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                            else:
                                logger.error(f"[{self.client_id}] Chat failed after {max_retries} retries (quota exhausted): {result.stderr}")
                        else:
                            logger.warning(f"[{self.client_id}] Chat failed: {result.stderr}")
                            break
                finally:
                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)

                # No delay between prompts - removed to maximize speed
                pass

            except Exception as e:
                logger.error(f"[{self.client_id}] Chat prompt failed {prompt_file.name}: {e}")

    def _generate_mindmap(self):
        """Generate mind map artifact."""
        try:
            logger.info(f"[{self.client_id}] Generating mind map...")

            result = subprocess.run(
                [
                    "notebooklm", "generate", "mind-map",
                    "-n", self.notebook_id
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                logger.info(f"[{self.client_id}] ✅ Mind map generated")
            else:
                logger.warning(f"[{self.client_id}] Mind map generation failed: {result.stderr}")

        except Exception as e:
            logger.error(f"[{self.client_id}] Mind map error: {e}")

    def _calculate_quality_score(self) -> float:
        """
        Calculate quality score (0-10) based on notebook completeness.

        Scoring:
        - Sources count: 0-3 points (need 15+ sources for full points)
        - Notes created: 0-4 points (need 6 notes for full points - v3.0.4 consolidated prompts)
        - Has mindmap: 0-1 points
        - Has PDF source: 0-1 points
        - Research sources: 0-1 points (10+ web sources)

        Returns:
            float: Quality score from 0.0 to 10.0
        """
        try:
            score = 0.0

            # Get notebook sources
            result = subprocess.run(
                ["notebooklm", "source", "list", "-n", self.notebook_id, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                sources = data.get('sources', [])
                source_count = len(sources)

                # Count different types of sources
                pdf_count = sum(1 for s in sources if s.get('type', '').lower() == 'pdf')
                web_count = sum(1 for s in sources if s.get('type', '').lower() in ['web', 'url', 'webpage'])

                # 1. Sources count (0-3 points)
                # 15+ sources = 3 points, scales linearly
                score += min(3.0, (source_count / 15.0) * 3.0)

                # 2. Has PDF source (0-1 point)
                if pdf_count > 0:
                    score += 1.0

                # 3. Research sources (0-1 point)
                # 10+ web sources = 1 point
                if web_count >= 10:
                    score += 1.0
                elif web_count > 0:
                    score += (web_count / 10.0)

            # Get notebook notes
            result = subprocess.run(
                ["notebooklm", "note", "list", "-n", self.notebook_id, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                notes = data.get('notes', [])
                note_count = len(notes)

                # 4. Notes created (0-4 points)
                # 6 notes = 4 points (consolidated prompts in v3.0.4)
                score += min(4.0, (note_count / 6.0) * 4.0)

            # 5. Has mindmap (0-1 point)
            # Check if mindmap exists
            result = subprocess.run(
                ["notebooklm", "artifact", "list", "-n", self.notebook_id],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and "mind-map" in result.stdout.lower():
                score += 1.0

            # Round to 1 decimal place
            score = round(score, 1)

            logger.info(f"[{self.client_id}] Quality score breakdown: {score}/10")
            return score

        except Exception as e:
            logger.error(f"[{self.client_id}] Quality score calculation failed: {e}")
            return 0.0

    def _execute_update_mode(self) -> bool:
        """
        Execute pipeline in UPDATE mode - refresh existing notebook with new data.

        Workflow:
        1. Find existing notebook (error if not found)
        2. Run fresh research (latest web data)
        3. Add new sources if available
        4. Update all 6 notes with latest information
        5. Regenerate mind map
        6. Calculate new quality score

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[{self.client_id}] ========================================")
            logger.info(f"[{self.client_id}] UPDATE MODE - Refreshing {self.client_name}")
            logger.info(f"[{self.client_id}] ========================================")

            # Step 1: Determine Industry (for research context)
            self.update_status("Loading industry configuration...", 5)
            self.industry, self.subsegments = self._determine_industry_and_subsegments()

            # Step 2: Check Authentication
            self.update_status("Checking authentication...", 10)
            if not self.auth_manager.ensure_authenticated(self.client_id, force_check=True):
                raise Exception("Authentication required - please run: notebooklm login")

            # Step 3: Find Existing Notebook
            self.update_status("Finding existing notebook...", 15)
            notebook_name = f"DEV_{self.client_id}-TEST"

            existing_notebook = self.notebook_manager.find_notebook_by_name(notebook_name)
            if not existing_notebook:
                raise Exception(
                    f"No existing notebook found with name: {notebook_name}. "
                    f"Run in 'fast' or 'deep' mode first to create it."
                )

            self.notebook_id = existing_notebook
            logger.info(f"[{self.client_id}] ✅ Found notebook: {self.notebook_id}")

            # Set notebook context
            self.notebook_manager.set_notebook_context(self.notebook_id)
            self.source_manager = SourceManager(self.client_id, self.notebook_id)

            # Step 4: Run Fresh Research (always get latest web data)
            self.update_status("Running fresh research...", 20)
            logger.info(f"[{self.client_id}] Running research with latest data...")
            self._run_ask_prompts()
            self.update_status("Research updated", 50)

            # Step 5: Deduplicate Sources
            self.update_status("Deduplicating sources...", 55)
            self._deduplicate_sources()

            # Step 6: Update All Notes
            self.update_status("Updating notes...", 60)
            logger.info(f"[{self.client_id}] Refreshing all 6 notes...")
            self._run_chat_prompts()
            self.update_status("Notes updated", 90)

            # Step 7: Regenerate Mind Map
            self.update_status("Regenerating mind map...", 95)
            self._generate_mindmap()

            # Step 8: Calculate Quality Score
            quality_score = self._calculate_quality_score()

            self.update_status("Update complete", 100, status="COMPLETE", quality_score=quality_score)

            logger.info(f"[{self.client_id}] ✅ UPDATE completed successfully!")
            logger.info(f"[{self.client_id}] 📊 Quality Score: {quality_score}/10")
            return True

        except Exception as e:
            logger.error(f"[{self.client_id}] ❌ Update failed: {e}")
            self.update_status(f"Update failed: {str(e)}", 0, status="FAILED", error=str(e))
            return False


def main():
    """Entry point for single client execution."""
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description="Project APE - Client Pipeline")
    parser.add_argument("client_id", help="Client identifier")
    parser.add_argument("--mode", choices=["fast", "deep", "update"], default="fast")
    parser.add_argument("--status-file", type=Path, required=True)
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Load config
    config_path = Path(__file__).parent.parent / "vars.py"
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    # Run pipeline
    pipeline = ClientPipeline(args.client_id, config, args.status_file, args.mode)
    success = pipeline.execute()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
