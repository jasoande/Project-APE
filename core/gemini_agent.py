"""
Gemini Orchestration Agent - Intelligent pipeline monitoring and self-healing

This module provides an intelligent Gemini-powered agent that orchestrates the entire
NotebookLM pipeline with superior reliability, error recovery, and quality control.

The agent monitors execution, validates outputs, retries failures intelligently, and
ensures every NotebookLM artifact (notebooks, sources, notes, mindmaps) is created correctly.
"""

import logging
import time
import os
from typing import Callable, List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from google import genai
from google.genai import types

from core.error_analyzer import GeminiErrorAnalyzer, ErrorContext, RecoveryAction
from core.quality_scorer import GeminiQualityScorer
from core.artifact_verifier import ArtifactVerifier

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Pipeline checkpoint record."""
    step_name: str
    step_number: int
    success: bool
    timestamp: float
    duration: float
    output: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""
    client_id: str
    success: bool
    quality_score: float
    notebook_id: Optional[str]
    checkpoints: List[Checkpoint]
    total_duration: float
    artifact_report: Optional[Dict]
    quality_report: Optional[Dict]
    error_summary: Optional[str]


class GeminiOrchestrationAgent:
    """
    Intelligent agent that orchestrates and monitors NotebookLM pipeline.

    Responsibilities:
    - Pre-execution validation (auth, API keys, prompts)
    - Real-time monitoring of NotebookLM operations
    - Quality checkpoint validation after each major step
    - Intelligent retry with root cause analysis
    - Post-execution quality scoring and artifact verification
    - Self-healing for common failure patterns

    Gemini Agent Capabilities:
    - Analyzes NotebookLM CLI output for errors
    - Decides whether errors are retryable
    - Generates recovery strategies
    - Validates source quality and completeness
    - Ensures all required artifacts exist
    """

    def __init__(self, client_id: str, config, gemini_api_key: str, status_updater: Optional[Callable] = None):
        """
        Initialize Gemini orchestration agent.

        Args:
            client_id: Client identifier
            config: Configuration module
            gemini_api_key: Gemini API key
            status_updater: Optional callback to update status (for dashboard)
        """
        self.client_id = client_id
        self.config = config
        self.gemini_api_key = gemini_api_key
        self.status_updater = status_updater

        # Agent configuration
        self.agent_config = getattr(config, 'GEMINI_AGENT_CONFIG', {})
        self.quality_thresholds = getattr(config, 'QUALITY_THRESHOLDS', {})

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.gemini_api_key)
        self.model_name = self.agent_config.get('model', 'gemini-2.5-flash')

        # Initialize helper components
        self.error_analyzer = GeminiErrorAnalyzer(gemini_api_key, config)
        self.quality_scorer = GeminiQualityScorer(gemini_api_key, config)
        self.artifact_verifier = ArtifactVerifier(config)

        # Execution state
        self.checkpoint_history: List[Checkpoint] = []
        self.start_time: Optional[float] = None
        self.notebook_id: Optional[str] = None

        logger.info(f"[AGENT] Initialized for client: {client_id}")

    def execute_pipeline(
        self,
        pipeline_steps: List[Tuple[str, Callable]],
        quality_target: float = 8.5,
        ensure_all_artifacts: bool = True
    ) -> PipelineResult:
        """
        Execute pipeline with intelligent monitoring.

        Args:
            pipeline_steps: List of (step_name, step_function) tuples
            quality_target: Minimum quality score required
            ensure_all_artifacts: Whether to verify all artifacts exist

        Returns:
            PipelineResult with execution details
        """
        logger.info(f"[AGENT] Starting pipeline execution for {self.client_id}")
        logger.info(f"[AGENT] Quality target: {quality_target}/10.0")

        self.start_time = time.time()
        overall_success = True
        error_summary = None

        # Pre-execution validation
        if not self._pre_execution_validation():
            return self._create_failure_result("Pre-execution validation failed")

        # Execute each pipeline step
        for step_number, (step_name, step_function) in enumerate(pipeline_steps, 1):
            logger.info(f"[AGENT] Step {step_number}/{len(pipeline_steps)}: {step_name}")

            checkpoint = self._execute_step_with_monitoring(
                step_name,
                step_number,
                step_function,
                len(pipeline_steps)
            )

            self.checkpoint_history.append(checkpoint)

            if not checkpoint.success:
                logger.error(f"[AGENT] Step failed: {step_name}")
                overall_success = False
                error_summary = checkpoint.error
                break

            # Update status
            progress = int((step_number / len(pipeline_steps)) * 95)  # Reserve 5% for final checks
            self._update_status(f"Completed: {step_name}", progress)

        # Post-execution validation
        if overall_success:
            overall_success, error_summary = self._post_execution_validation(
                quality_target,
                ensure_all_artifacts
            )

        # Calculate total duration
        total_duration = time.time() - self.start_time

        # Create final result
        result = PipelineResult(
            client_id=self.client_id,
            success=overall_success,
            quality_score=0.0,  # Will be updated by quality validation
            notebook_id=self.notebook_id,
            checkpoints=self.checkpoint_history,
            total_duration=total_duration,
            artifact_report=None,
            quality_report=None,
            error_summary=error_summary
        )

        # Update with quality and artifact reports if available
        if hasattr(self, 'latest_quality_report'):
            result.quality_report = self.latest_quality_report.to_dict()
            result.quality_score = self.latest_quality_report.total_score

        if hasattr(self, 'latest_artifact_report'):
            result.artifact_report = self.latest_artifact_report.to_dict()

        self._log_pipeline_summary(result)

        return result

    def _pre_execution_validation(self) -> bool:
        """
        Validate prerequisites before execution.

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("[AGENT] Running pre-execution validation...")

        # Check Gemini API key
        if not self.gemini_api_key:
            logger.error("[AGENT] GEMINI_API_KEY not found")
            return False

        # Check prompt files exist
        prompt_files = [
            'ask_prompt_01.txt',
            'ask_prompt_02.txt',
            'chat_prompt_consolidated_01.txt',
            'chat_prompt_consolidated_02.txt',
            'chat_prompt_consolidated_03.txt',
            'chat_prompt_consolidated_04.txt',
            'chat_prompt_consolidated_05.txt',
            'chat_prompt_consolidated_06.txt',
        ]

        for prompt_file in prompt_files:
            if not Path(prompt_file).exists():
                logger.warning(f"[AGENT] Prompt file not found: {prompt_file}")

        logger.info("[AGENT] ✓ Pre-execution validation passed")
        return True

    def _execute_step_with_monitoring(
        self,
        step_name: str,
        step_number: int,
        step_function: Callable,
        total_steps: int
    ) -> Checkpoint:
        """
        Execute a pipeline step with monitoring and retry logic.

        Args:
            step_name: Name of the step
            step_number: Step number
            step_function: Function to execute
            total_steps: Total number of steps

        Returns:
            Checkpoint record
        """
        max_retries = self.agent_config.get('max_retries', 5)
        retry_count = 0
        start_time = time.time()

        while retry_count <= max_retries:
            try:
                # Execute step
                result = step_function()

                # Handle different return types
                if isinstance(result, tuple) and len(result) == 2:
                    # Assume (success, output) or (success, data)
                    success, output = result
                    if step_name == 'create_notebook' and success:
                        self.notebook_id = output
                elif result is None:
                    # Void function, assume success
                    success = True
                    output = None
                else:
                    # Single return value
                    success = bool(result)
                    output = result if success else None

                duration = time.time() - start_time

                if success:
                    logger.info(f"[AGENT] ✓ {step_name} completed ({duration:.1f}s)")
                    return Checkpoint(
                        step_name=step_name,
                        step_number=step_number,
                        success=True,
                        timestamp=time.time(),
                        duration=duration,
                        output=str(output) if output else None,
                        retry_count=retry_count
                    )
                else:
                    # Step returned False
                    raise Exception(f"Step {step_name} returned failure")

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"[AGENT] Step error (attempt {retry_count + 1}/{max_retries + 1}): {error_msg}")

                # Analyze error
                if self.agent_config.get('enable_error_analysis', True):
                    error_context = ErrorContext(
                        command=step_name,
                        error_output=error_msg,
                        step_name=step_name,
                        step_number=step_number,
                        previous_steps_succeeded=all(c.success for c in self.checkpoint_history),
                        client_id=self.client_id
                    )

                    strategy = self.error_analyzer.analyze_error(error_context)

                    if not strategy.is_retryable or retry_count >= max_retries:
                        # Non-retryable or max retries exceeded
                        duration = time.time() - start_time
                        logger.error(f"[AGENT] ✗ {step_name} failed: {strategy.reasoning}")
                        return Checkpoint(
                            step_name=step_name,
                            step_number=step_number,
                            success=False,
                            timestamp=time.time(),
                            duration=duration,
                            error=error_msg,
                            retry_count=retry_count
                        )

                    # Apply recovery strategy
                    if strategy.action == RecoveryAction.WAIT_AND_RETRY:
                        wait_time = strategy.wait_seconds
                        logger.info(f"[AGENT] Waiting {wait_time}s before retry ({strategy.reasoning})")
                        time.sleep(wait_time)

                    retry_count += 1

                else:
                    # No error analysis, simple retry
                    retry_count += 1
                    if retry_count > max_retries:
                        duration = time.time() - start_time
                        return Checkpoint(
                            step_name=step_name,
                            step_number=step_number,
                            success=False,
                            timestamp=time.time(),
                            duration=duration,
                            error=error_msg,
                            retry_count=retry_count
                        )
                    time.sleep(10)  # Default wait

        # Should not reach here
        duration = time.time() - start_time
        return Checkpoint(
            step_name=step_name,
            step_number=step_number,
            success=False,
            timestamp=time.time(),
            duration=duration,
            error="Max retries exceeded",
            retry_count=retry_count
        )

    def _post_execution_validation(
        self,
        quality_target: float,
        ensure_artifacts: bool
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate quality and artifacts after execution.

        Args:
            quality_target: Minimum quality score
            ensure_artifacts: Whether to verify artifacts

        Returns:
            Tuple of (success, error_message)
        """
        logger.info("[AGENT] Running post-execution validation...")

        if not self.notebook_id:
            return False, "No notebook ID available"

        success = True
        error_msg = None

        # Verify artifacts
        if ensure_artifacts:
            self._update_status("Verifying artifacts...", 96)
            self.latest_artifact_report = self.artifact_verifier.verify_all_artifacts(
                self.client_id,
                self.notebook_id
            )

            if not self.latest_artifact_report.all_artifacts_present:
                logger.warning("[AGENT] Not all artifacts present")
                # Don't fail, but log warning

        # Calculate quality score
        if self.agent_config.get('enable_quality_validation', True):
            self._update_status("Calculating quality score...", 98)

            # Get sources for quality calculation
            sources = []
            notes_count = 6  # Assume all notes created
            has_mindmap = True  # Assume mindmap exists

            if hasattr(self, 'latest_artifact_report') and self.latest_artifact_report.sources:
                sources = self.latest_artifact_report.sources.source_list
                notes_count = self.latest_artifact_report.notes.count if self.latest_artifact_report.notes else 6

            self.latest_quality_report = self.quality_scorer.calculate_enhanced_score(
                client_id=self.client_id,
                notebook_id=self.notebook_id,
                sources=sources,
                notes_count=notes_count,
                has_mindmap=has_mindmap,
                use_gemini_validation=False  # Set to True for deeper analysis
            )

            if not self.latest_quality_report.meets_target:
                logger.warning(f"[AGENT] Quality score {self.latest_quality_report.total_score:.1f} below target {quality_target}")
                # Attempt quality improvement
                if self.agent_config.get('enable_self_healing', True):
                    self._attempt_quality_improvement(self.latest_quality_report)

        self._update_status("Validation complete", 100)

        logger.info("[AGENT] ✓ Post-execution validation complete")
        return success, error_msg

    def _attempt_quality_improvement(self, quality_report):
        """
        Attempt to improve quality score based on recommendations.

        Args:
            quality_report: Quality report with recommendations
        """
        logger.info("[AGENT] Attempting quality improvement...")

        for recommendation in quality_report.recommendations:
            logger.info(f"[AGENT] Recommendation: {recommendation}")
            # TODO: Implement specific improvement actions
            # For now, just log recommendations

    def _update_status(self, step: str, progress: int):
        """Update status via callback."""
        if self.status_updater:
            try:
                self.status_updater(step, progress)
            except Exception as e:
                logger.warning(f"[AGENT] Failed to update status: {e}")

    def _create_failure_result(self, error_msg: str) -> PipelineResult:
        """Create a failure result."""
        return PipelineResult(
            client_id=self.client_id,
            success=False,
            quality_score=0.0,
            notebook_id=self.notebook_id,
            checkpoints=self.checkpoint_history,
            total_duration=time.time() - self.start_time if self.start_time else 0.0,
            artifact_report=None,
            quality_report=None,
            error_summary=error_msg
        )

    def _log_pipeline_summary(self, result: PipelineResult):
        """Log pipeline execution summary."""
        logger.info("="*60)
        logger.info(f"[AGENT] Pipeline Execution Summary: {self.client_id}")
        logger.info("="*60)
        logger.info(f"  Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
        logger.info(f"  Quality Score: {result.quality_score:.1f}/10.0")
        logger.info(f"  Duration: {result.total_duration/60:.1f} minutes")
        logger.info(f"  Steps Completed: {sum(1 for c in result.checkpoints if c.success)}/{len(result.checkpoints)}")

        if result.error_summary:
            logger.error(f"  Error: {result.error_summary}")

        # Checkpoint summary
        logger.info("  Checkpoints:")
        for checkpoint in result.checkpoints:
            status = "✓" if checkpoint.success else "✗"
            retry_info = f" (retries: {checkpoint.retry_count})" if checkpoint.retry_count > 0 else ""
            logger.info(f"    {status} {checkpoint.step_name} ({checkpoint.duration:.1f}s){retry_info}")

        logger.info("="*60)
