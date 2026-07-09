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
from core.update_manager import UpdateManager
# from core.research_queue import ResearchQueue  # Removed - no longer using queue lock

# Gemini Agent (optional - enabled via config)
try:
    from core.gemini_agent import GeminiOrchestrationAgent
    GEMINI_AGENT_AVAILABLE = True
except ImportError:
    GEMINI_AGENT_AVAILABLE = False

try:
    from core.quality_scorer import GeminiQualityScorer
    GEMINI_SCORER_AVAILABLE = True
except ImportError:
    GEMINI_SCORER_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClientPipeline:
    """Executes complete pipeline for a single client."""

    def __init__(self, client_id: str, config, status_file: Path, mode: str = "fast",
                 force_refresh: bool = False, resume: bool = False):
        """
        Initialize client pipeline.

        Args:
            client_id: Client identifier (e.g., 'merck_test')
            config: Configuration module
            status_file: Path to status JSON file
            mode: Execution mode (fast or deep)
            force_refresh: Force refresh of Google Drive cache
            resume: Resume from last checkpoint
        """
        self.client_id = client_id
        self.config = config
        self.status_file = status_file
        self.mode = mode
        self.force_refresh = force_refresh
        self.resume = resume

        # Initialize checkpoint manager
        try:
            from core.checkpoint_manager import CheckpointManager, PipelineCheckpoint
            logs_dir = Path(getattr(config, 'LOGS_DIR', './logs'))
            self.checkpoint_mgr = CheckpointManager(logs_dir, client_id, str(int(time.time())))
            self._PipelineCheckpoint = PipelineCheckpoint
        except ImportError:
            self.checkpoint_mgr = None
            self._PipelineCheckpoint = None

        # Get client details from config
        self.client_name = getattr(config, f"{client_id}_name", client_id)
        self.client_folder_spec = getattr(config, f"{client_id}_folder", "")

        # Defer Drive download until execute() to avoid OAuth race condition
        # Will be set in execute() after staggered launch
        self.client_folder = None

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
                force_refresh=self.force_refresh,
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

    def _should_skip(self, phase_name: str) -> bool:
        """Check if a phase should be skipped due to checkpoint resume."""
        if not self.resume or not self.checkpoint_mgr:
            return False
        checkpoint = self.checkpoint_mgr.load()
        if checkpoint and self.checkpoint_mgr.should_skip_phase(phase_name, checkpoint):
            logger.info(f"[{self.client_id}] Resuming: skipping {phase_name} (already done)")
            return True
        return False

    def _save_checkpoint(self, phase_name: str, **kwargs):
        """Save checkpoint after completing a phase."""
        if not self.checkpoint_mgr or not self._PipelineCheckpoint:
            return
        checkpoint = self.checkpoint_mgr.load()
        if not checkpoint:
            checkpoint = self._PipelineCheckpoint(
                client_id=self.client_id,
                run_id=self.checkpoint_mgr.run_id,
                mode=self.mode,
                phase=phase_name,
                phase_number=0,
                completed_phases=[]
            )
        if phase_name not in checkpoint.completed_phases:
            checkpoint.completed_phases.append(phase_name)
        checkpoint.phase = phase_name
        checkpoint.notebook_id = kwargs.get('notebook_id', checkpoint.notebook_id)
        checkpoint.consolidated_pdf_path = kwargs.get('pdf_path', checkpoint.consolidated_pdf_path)
        checkpoint.industry = kwargs.get('industry', checkpoint.industry)
        checkpoint.subsegments = kwargs.get('subsegments', checkpoint.subsegments)
        self.checkpoint_mgr.save(checkpoint)

    def _execute_standard(self) -> bool:
        """
        Execute pipeline without Gemini agent (standard mode).

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load checkpoint for resume
            if self.resume and self.checkpoint_mgr:
                checkpoint = self.checkpoint_mgr.load()
                if checkpoint:
                    logger.info(f"[{self.client_id}] Resuming from checkpoint: {checkpoint.phase}")
                    if checkpoint.notebook_id:
                        self.notebook_id = checkpoint.notebook_id
                    if checkpoint.industry:
                        self.industry = checkpoint.industry
                    if checkpoint.subsegments:
                        self.subsegments = checkpoint.subsegments

            logger.info(f"[{self.client_id}] ========================================")
            logger.info(f"[{self.client_id}] Starting pipeline for {self.client_name}")
            logger.info(f"[{self.client_id}] Mode: {self.mode.upper()}")
            logger.info(f"[{self.client_id}] ========================================")

            # Step 0: Setup client folder (Download from Drive if needed)
            if not self._should_skip("setup_folder"):
                self.update_status("Setting up client folder...", 1)
                self.client_folder = self._setup_client_folder(self.client_folder_spec)
                logger.info(f"[{self.client_id}] Client folder: {self.client_folder}")
                self._save_checkpoint("setup_folder")
            else:
                self.client_folder = self._setup_client_folder(self.client_folder_spec)

            # Step 0.5: Determine Industry and Subsegments (Gemini AI or manual config)
            if not self._should_skip("determine_industry"):
                self.update_status("Determining industry and subsegments...", 3)
                self.industry, self.subsegments = self._determine_industry_and_subsegments()
                logger.info(f"[{self.client_id}] Industry: {self.industry}")
                logger.info(f"[{self.client_id}] Subsegments: {self.subsegments}")
                self._save_checkpoint("determine_industry", industry=self.industry, subsegments=self.subsegments)
            elif not self.industry:
                self.industry, self.subsegments = self._determine_industry_and_subsegments()

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
            self._save_checkpoint("create_notebook", notebook_id=self.notebook_id)

            # Initialize source manager now that we have notebook_id
            self.source_manager = SourceManager(self.client_id, self.notebook_id)

            # Step 3: Consolidate to PDF and Upload (with change detection)
            logger.info(f"[{self.client_id}] Checking if consolidation needed...")
            self.update_status("Checking for file changes...", 23)

            # Pass is_new_notebook flag to force consolidation for new notebooks
            is_new_notebook = not is_existing
            needs_update, newest_file_time = self._check_consolidation_needed(is_new_notebook=is_new_notebook)

            # If using existing notebook on new VM, timestamp file won't exist
            # In that case, force upload to ensure PDF is in notebook
            logs_dir = Path(self.config.LOGS_DIR if hasattr(self.config, 'LOGS_DIR') else './logs')
            timestamp_file = logs_dir / '.consolidation_timestamps' / f"{self.client_id}.json"
            force_upload_on_new_vm = is_existing and not timestamp_file.exists()

            # CRITICAL FIX: Even if no file changes, verify consolidated PDF exists in notebook
            # The PDF might have been deleted, notebook re-created, or newly created
            force_upload_missing_pdf = False
            if not needs_update and not force_upload_on_new_vm:
                logger.info(f"[{self.client_id}] Verifying consolidated PDF exists in notebook...")
                if not self.source_manager.has_consolidated_pdf_source(self.client_name):
                    logger.info(f"[{self.client_id}] 📄 Consolidated PDF missing from notebook - will upload")
                    force_upload_missing_pdf = True

            if needs_update or force_upload_on_new_vm or force_upload_missing_pdf:
                if force_upload_on_new_vm:
                    logger.info(f"[{self.client_id}] 📄 No local timestamp (new VM?) - uploading PDF to ensure notebook has it...")
                elif force_upload_missing_pdf:
                    logger.info(f"[{self.client_id}] 📄 Consolidated PDF missing from notebook - re-uploading...")
                else:
                    logger.info(f"[{self.client_id}] 🔄 Files changed - consolidating to PDF...")

                self.update_status("Consolidating files to PDF...", 25)

                # Delete old consolidated PDFs first
                self.source_manager.delete_old_consolidated_pdfs(self.client_name)

                # Consolidate all files to single PDF
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                consolidated_filename = f"{self.client_name}-Consolidated-{timestamp}.pdf"

                consolidated_pdf = self._consolidate_pdfs(consolidated_filename)

                if consolidated_pdf and consolidated_pdf.exists():
                    # Upload consolidated PDF
                    logger.info(f"[{self.client_id}] Uploading consolidated PDF...")
                    self.update_status("Uploading consolidated PDF...", 28)

                    if self.source_manager.add_file_source(consolidated_pdf):
                        logger.info(f"[{self.client_id}] ✅ Uploaded: {consolidated_filename}")
                        # Save timestamp for future comparison
                        self._save_consolidation_timestamp(newest_file_time)
                    else:
                        logger.warning(f"[{self.client_id}] ⚠️  Failed to upload consolidated PDF")
                else:
                    logger.warning(f"[{self.client_id}] ⚠️  PDF consolidation failed")
            else:
                logger.info(f"[{self.client_id}] ✅ No file changes detected - skipping consolidation")

            self.update_status("Sources added", 30)

            # Step 4: ALWAYS Run Ask Prompts (Research) for fresh web data
            # Deep mode deduplicates after EACH prompt (inside _run_ask_prompts)
            # Fast mode deduplicates once at the end (below)
            self._run_ask_prompts()

            # CRITICAL: Verify sources were actually imported
            min_sources = 30 if self.mode == "deep" else 10
            if not self.source_manager.verify_sources_imported(min_sources):
                raise RuntimeError(
                    f"Research completed but sources not imported. "
                    f"Expected at least {min_sources} sources. "
                    f"Check NotebookLM API logs and verify --import-all succeeded."
                )

            self.update_status("Research complete", 60)
            self._save_checkpoint("run_research")

            # Step 5: Deduplicate Sources (Fast mode only - deep mode already did it)
            if self.mode == "fast":
                # Fast mode: Deduplicate once (no wait - NotebookLM processes async)
                logger.info(f"[{self.client_id}] Deduplicating sources...")

                self._deduplicate_sources()
                self.update_status("Sources deduplicated", 65)
            else:
                # Deep mode: Already deduplicated after each prompt
                logger.info(f"[{self.client_id}] Sources already deduplicated (deep mode)")
                self.update_status("Sources deduplicated", 65)

            # Step 6: Run Chat Prompts - Sequential with Notes
            self._run_chat_prompts()
            self.update_status("Chat prompts complete", 95)
            self._save_checkpoint("run_chat")

            # Step 7: Generate Mind Map
            self._generate_mindmap()

            # Step 8: Calculate Quality Score
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

            # Step 0: Setup client folder (Download from Drive if needed)
            self.update_status("Setting up client folder...", 1)
            self.client_folder = self._setup_client_folder(self.client_folder_spec)
            logger.info(f"[{self.client_id}] Client folder: {self.client_folder}")

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

    def _consolidate_pdfs(self, output_filename: str = None) -> Optional[Path]:
        """
        Consolidate all files into single PDF - converts everything to PDF first.

        Args:
            output_filename: Optional custom filename (default: {Client}-One.pdf)

        Returns:
            Path to consolidated PDF
        """
        if not self.client_folder.exists():
            logger.warning(f"[{self.client_id}] Client folder not found: {self.client_folder}")
            return None

        try:
            logger.info(f"[{self.client_id}] Consolidating all files to PDF...")
            self.update_status("Converting files to PDF...", 20)

            # Use custom filename or default
            pdf_filename = output_filename or f"{self.client_name}-One.pdf"

            # Use FastPDFConsolidator which converts ALL file types to PDF
            # Handles: PDFs, text files, images, office docs (xlsx, docx, pptx)
            # Write consolidated PDF to logs directory (writable in containers)
            logs_dir = Path(self.config.LOGS_DIR if hasattr(self.config, 'LOGS_DIR') else './logs')
            with FastPDFConsolidator(
                self.client_id,
                self.client_folder,
                pdf_filename,
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

    def _check_consolidation_needed(self, is_new_notebook: bool = False) -> tuple[bool, str]:
        """
        Check if files have changed since last consolidation using Drive API timestamps.

        Args:
            is_new_notebook: If True, forces consolidation regardless of file timestamps

        Returns:
            Tuple of (needs_update: bool, newest_drive_time: str)
        """
        from datetime import datetime
        import json

        try:
            # Get timestamp file path from logs directory (mounted in containers)
            logs_dir = Path(self.config.LOGS_DIR if hasattr(self.config, 'LOGS_DIR') else './logs')
            timestamp_file = logs_dir / '.consolidation_timestamps' / f"{self.client_id}.json"

            # Get Drive folder spec
            client_folder_spec = getattr(self.config, f"{self.client_id}_folder", "")
            if not client_folder_spec:
                logger.warning(f"[{self.client_id}] No Drive folder configured")
                return True, datetime.now().isoformat()

            # List files from Drive API to get actual modifiedTime
            drive_config = getattr(self.config, 'DRIVE_CONFIG', {})
            drive_manager = DriveManager(
                client_id=self.client_id,
                folder_spec=client_folder_spec,
                cache_enabled=False,
                force_refresh=False,
                config=drive_config
            )

            files_metadata = drive_manager.list_files_metadata()

            if not files_metadata:
                logger.warning(f"[{self.client_id}] No files found in Drive")
                return False, datetime.now().isoformat()

            # Find newest file modification time from Drive API
            newest_drive_time = None
            for file_info in files_metadata:
                modified_time_str = file_info.get('modifiedTime')
                if modified_time_str:
                    # Parse Drive API timestamp (RFC 3339 format)
                    file_time = datetime.fromisoformat(modified_time_str.replace('Z', '+00:00'))
                    if newest_drive_time is None or file_time > newest_drive_time:
                        newest_drive_time = file_time

            if newest_drive_time is None:
                logger.warning(f"[{self.client_id}] Could not determine file timestamps")
                return True, datetime.now().isoformat()

            # CRITICAL: If this is a new notebook, always consolidate regardless of file timestamps
            if is_new_notebook:
                logger.info(f"[{self.client_id}] New notebook detected - will upload consolidated PDF")
                return True, newest_drive_time.isoformat()

            # Check if we have a previous timestamp
            if not timestamp_file.exists():
                logger.info(f"[{self.client_id}] No previous consolidation timestamp - will consolidate")
                return True, newest_drive_time.isoformat()

            # Read previous timestamp
            with open(timestamp_file, 'r') as f:
                data = json.load(f)
                last_consolidation = datetime.fromisoformat(data['last_consolidation'])

            # Compare (make both timezone-aware for comparison)
            if last_consolidation.tzinfo is None:
                # Assume local timezone if no timezone info
                from datetime import timezone
                last_consolidation = last_consolidation.replace(tzinfo=timezone.utc)

            if newest_drive_time > last_consolidation:
                logger.info(f"[{self.client_id}] Files changed since last consolidation")
                logger.info(f"[{self.client_id}]    Last: {last_consolidation.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"[{self.client_id}]    Newest: {newest_drive_time.strftime('%Y-%m-%d %H:%M:%S')}")
                return True, newest_drive_time.isoformat()
            else:
                logger.info(f"[{self.client_id}] ✅ No changes since last consolidation - skipping")
                return False, newest_drive_time.isoformat()

        except Exception as e:
            logger.warning(f"[{self.client_id}] Error checking timestamps: {e} - will consolidate")
            return True, datetime.now().isoformat()

    def _save_consolidation_timestamp(self, timestamp: str):
        """
        Save consolidation timestamp for future comparison.

        Args:
            timestamp: ISO format timestamp string
        """
        import json
        from datetime import datetime

        try:
            # Save to logs directory (mounted in containers)
            logs_dir = Path(self.config.LOGS_DIR if hasattr(self.config, 'LOGS_DIR') else './logs')
            timestamp_dir = logs_dir / '.consolidation_timestamps'
            timestamp_dir.mkdir(parents=True, exist_ok=True)

            timestamp_file = timestamp_dir / f"{self.client_id}.json"

            data = {
                'client_id': self.client_id,
                'client_name': self.client_name,
                'last_consolidation': timestamp,
                'updated_at': datetime.now().isoformat()
            }

            with open(timestamp_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"[{self.client_id}] 💾 Saved consolidation timestamp: {timestamp_file}")

        except Exception as e:
            logger.warning(f"[{self.client_id}] Failed to save timestamp: {e}")

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

        total_imported = 0

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

                    result = self.source_manager.add_research_with_import(
                        prompt_file,
                        mode="deep",
                        client_name=self.client_name,
                        client_industry=self.industry,
                        client_subsegments=self.subsegments
                    )

                    if result["success"]:
                        imported = result.get('imported', 0)
                        total_imported += imported
                        logger.info(f"[{self.client_id}] ✅ Imported {imported} sources")
                    else:
                        error_msg = f"Research failed for {prompt_file.name}: {result.get('error')}"
                        logger.warning(f"[{self.client_id}] ⚠️  {error_msg}")

                        error_str = str(result.get('error', ''))
                        if 'rate limit' in error_str.lower() or 'ratelimiterror' in error_str.lower():
                            logger.warning(f"[{self.client_id}] 🚫 NotebookLM API rate limit hit — continuing with remaining prompts")

                    # Deduplicate after EACH research prompt (deep mode only)
                    logger.info(f"[{self.client_id}] Deduplicating sources (after prompt {idx})...")
                    removed = self.source_manager.deduplicate_sources()
                    logger.info(f"[{self.client_id}] ✅ Removed {removed} duplicates")

                except Exception as e:
                    logger.error(f"[{self.client_id}] Ask prompt failed {prompt_file.name}: {e}")

        else:
            import random
            delay = random.uniform(0, 12)
            logger.info(f"[{self.client_id}] ⏱️  Anti-rate-limit delay: {delay:.1f}s")
            time.sleep(delay)

            logger.info(f"[{self.client_id}] Running {len(ask_prompts)} research prompts...")

            for idx, prompt_file in enumerate(ask_prompts, 1):
                try:
                    progress = 30 + (idx / len(ask_prompts)) * 30  # 30-60%
                    self.update_status(f"Research {idx}/{len(ask_prompts)}: {prompt_file.stem}", int(progress))

                    logger.info(f"[{self.client_id}] Research prompt: {prompt_file.name}")

                    result = self.source_manager.add_research_with_import(
                        prompt_file,
                        mode="fast",
                        client_name=self.client_name,
                        client_industry=self.industry,
                        client_subsegments=self.subsegments
                    )

                    if result["success"]:
                        imported = result.get('imported', 0)
                        total_imported += imported
                        logger.info(f"[{self.client_id}] ✅ Imported {imported} sources")
                    else:
                        error_msg = f"Research failed for {prompt_file.name}: {result.get('error')}"
                        logger.warning(f"[{self.client_id}] ⚠️  {error_msg}")

                        error_str = str(result.get('error', ''))
                        if 'rate limit' in error_str.lower() or 'ratelimiterror' in error_str.lower():
                            logger.warning(f"[{self.client_id}] 🚫 NotebookLM API rate limit hit — continuing with remaining prompts")

                except Exception as e:
                    logger.error(f"[{self.client_id}] Ask prompt failed {prompt_file.name}: {e}")

        logger.info(f"[{self.client_id}] Research phase complete: {total_imported} total sources imported")
        if total_imported == 0:
            raise RuntimeError(f"All {len(ask_prompts)} research prompts failed — zero sources imported")

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

                        # Step 1: Get AI response with --json (preserves formatting)
                        result = subprocess.run(
                            [
                                "notebooklm", "ask",
                                "--prompt-file", tmp_path,
                                "-n", self.notebook_id,
                                "--json"
                            ],
                            capture_output=True,
                            text=True,
                            timeout=180
                        )

                        if result.returncode == 0:
                            # Step 2: Create note from the response
                            try:
                                import json
                                response_data = json.loads(result.stdout)
                                note_content = response_data.get('answer', '')

                                # Create note with the markdown content
                                create_result = subprocess.run(
                                    [
                                        "notebooklm", "note", "create",
                                        "--content", note_content,
                                        "-t", note_title,
                                        "-n", self.notebook_id
                                    ],
                                    capture_output=True,
                                    text=True,
                                    timeout=60
                                )

                                if create_result.returncode == 0:
                                    logger.info(f"[{self.client_id}] ✅ Created note: {prompt_file.stem}")
                                    break
                                else:
                                    # Check if note creation error is retryable
                                    stderr_lower = create_result.stderr.lower()
                                    if "rate limit" in stderr_lower or "quota" in stderr_lower or "rpc_code" in stderr_lower:
                                        if attempt < max_retries - 1:
                                            logger.warning(f"[{self.client_id}] Note creation quota/rate limit, waiting {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                                            time.sleep(retry_delay)
                                            retry_delay *= 2
                                            continue  # Retry
                                        else:
                                            logger.error(f"[{self.client_id}] Note creation failed after {max_retries} retries: {create_result.stderr}")
                                            break
                                    elif "no parseable chunks" in stderr_lower or "streaming" in stderr_lower:
                                        if attempt < max_retries - 1:
                                            logger.warning(f"[{self.client_id}] Note creation streaming error, retrying in 10s (attempt {attempt + 1}/{max_retries})")
                                            time.sleep(10)
                                            continue  # Retry
                                        else:
                                            logger.error(f"[{self.client_id}] Note creation failed after {max_retries} retries: {create_result.stderr}")
                                            break
                                    else:
                                        logger.warning(f"[{self.client_id}] Note creation failed (non-retryable): {create_result.stderr}")
                                        break
                            except json.JSONDecodeError as e:
                                # JSON parse error might be transient (truncated response, network issue)
                                if attempt < max_retries - 1:
                                    logger.warning(f"[{self.client_id}] JSON parse error, retrying (attempt {attempt + 1}/{max_retries}): {e}")
                                    time.sleep(10)
                                    continue  # Retry
                                else:
                                    logger.error(f"[{self.client_id}] JSON parse failed after {max_retries} retries: {e}")
                                    break
                        elif "rate limit" in result.stderr.lower() or "quota" in result.stderr.lower() or "rpc_code=3" in result.stderr.lower() or "rpc_code=9" in result.stderr.lower() or "rpc_code=8" in result.stderr.lower():
                            if attempt < max_retries - 1:
                                logger.warning(f"[{self.client_id}] Quota/rate limit hit, waiting {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                            else:
                                logger.error(f"[{self.client_id}] Chat failed after {max_retries} retries (quota exhausted): {result.stderr}")
                        elif "no parseable chunks" in result.stderr.lower():
                            # Intermittent streaming error - retry with delay
                            if attempt < max_retries - 1:
                                logger.warning(f"[{self.client_id}] Streaming error, retrying in 10s (attempt {attempt + 1}/{max_retries})")
                                time.sleep(10)
                            else:
                                logger.error(f"[{self.client_id}] Chat failed after {max_retries} retries (streaming error): {result.stderr}")
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
        Uses GeminiQualityScorer when GEMINI_API_KEY is available.

        Returns:
            float: Quality score from 0.0 to 10.0
        """
        try:
            # Gather notebook data for both paths
            sources = []
            notes_count = 0
            has_mindmap = False

            result = subprocess.run(
                ["notebooklm", "source", "list", "-n", self.notebook_id, "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                sources = data.get('sources', [])

            result = subprocess.run(
                ["notebooklm", "note", "list", "-n", self.notebook_id, "--json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                notes_count = len(data.get('notes', []))

            result = subprocess.run(
                ["notebooklm", "artifact", "list", "-n", self.notebook_id],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and "mind-map" in result.stdout.lower():
                has_mindmap = True

            # Use Gemini scorer when available
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if gemini_api_key and GEMINI_SCORER_AVAILABLE:
                logger.info(f"[{self.client_id}] Using Gemini quality scorer")
                scorer = GeminiQualityScorer(api_key=gemini_api_key, config=self.config)
                report = scorer.calculate_enhanced_score(
                    client_id=self.client_id,
                    notebook_id=self.notebook_id,
                    sources=sources,
                    notes_count=notes_count,
                    has_mindmap=has_mindmap
                )
                return round(report.total_score, 1)

            # Fallback: basic scoring
            score = 0.0
            source_count = len(sources)
            pdf_count = sum(1 for s in sources if s.get('type', '').lower() == 'pdf')
            web_count = sum(1 for s in sources if s.get('type', '').lower() in ['web', 'url', 'webpage'])

            score += min(3.0, (source_count / 15.0) * 3.0)
            if pdf_count > 0:
                score += 1.0
            if web_count >= 10:
                score += 1.0
            elif web_count > 0:
                score += (web_count / 10.0)
            score += min(4.0, (notes_count / 6.0) * 4.0)
            if has_mindmap:
                score += 1.0

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

            # Step 0: Setup client folder (Download from Drive if needed)
            self.update_status("Setting up client folder...", 1)
            self.client_folder = self._setup_client_folder(self.client_folder_spec)
            logger.info(f"[{self.client_id}] Client folder: {self.client_folder}")

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
            self.notebook_manager.set_context(self.notebook_id)
            self.source_manager = SourceManager(self.client_id, self.notebook_id)

            # Step 3.5: Check for new files from Google Drive
            self.update_status("Checking for new files...", 17)
            update_mgr = UpdateManager(self.client_id, self.config)
            update_results = update_mgr.update_client_sources(
                notebook_name=notebook_name,
                force_drive_refresh=True,
                re_run_research=False  # We'll run research separately
            )

            if update_results.get("new_sources_added", 0) > 0:
                logger.info(f"[{self.client_id}] ✅ Added {update_results['new_sources_added']} new files")
            else:
                logger.info(f"[{self.client_id}] ℹ️  No new files detected")

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
    parser.add_argument("--refresh", action="store_true", help="Force refresh Google Drive cache")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
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
    pipeline = ClientPipeline(args.client_id, config, args.status_file, args.mode, args.refresh, args.resume)
    success = pipeline.execute()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
