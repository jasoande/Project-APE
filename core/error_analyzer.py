"""
Error Analyzer - Gemini-powered error analysis and recovery strategy generation

This module uses Gemini AI to analyze NotebookLM CLI errors and determine optimal recovery strategies.
It learns from error patterns to minimize API calls and improve recovery success rates.
"""

import logging
import hashlib
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error classification categories."""
    AUTH = "authentication"
    RATE_LIMIT = "rate_limit"
    QUOTA = "quota"
    NETWORK = "network"
    CONTENT = "content"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Recommended recovery actions."""
    RETRY = "retry"
    WAIT_AND_RETRY = "wait_and_retry"
    SKIP = "skip"
    RE_AUTH = "re_authenticate"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Context for error analysis."""
    command: str
    error_output: str
    step_name: str
    step_number: int
    previous_steps_succeeded: bool
    client_id: str


@dataclass
class RecoveryStrategy:
    """Recommended recovery strategy."""
    is_retryable: bool
    category: ErrorCategory
    action: RecoveryAction
    wait_seconds: int
    success_probability: float  # 0.0-1.0
    reasoning: str
    alternative_actions: list[str]


class GeminiErrorAnalyzer:
    """
    Gemini-powered error analyzer for intelligent recovery strategies.

    Features:
    - Analyzes NotebookLM CLI errors
    - Determines if errors are retryable
    - Recommends recovery actions
    - Caches common error patterns
    - Learns from successful recoveries
    """

    def __init__(self, api_key: str, config):
        """
        Initialize error analyzer.

        Args:
            api_key: Gemini API key
            config: Configuration module
        """
        self.api_key = api_key
        self.config = config
        self.agent_config = getattr(config, 'GEMINI_AGENT_CONFIG', {})

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = self.agent_config.get('model', 'gemini-2.5-flash')

        # Error pattern cache
        self.error_cache: Dict[str, RecoveryStrategy] = {}

        # Known error patterns (fast path, no Gemini needed)
        self.known_patterns = self._init_known_patterns()

    def _init_known_patterns(self) -> Dict[str, RecoveryStrategy]:
        """Initialize known error patterns for fast resolution."""
        return {
            'rate_limit': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.RATE_LIMIT,
                action=RecoveryAction.WAIT_AND_RETRY,
                wait_seconds=60,
                success_probability=0.9,
                reasoning="Rate limit error - wait and retry",
                alternative_actions=["Increase wait time if retry fails"]
            ),
            'quota': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.QUOTA,
                action=RecoveryAction.WAIT_AND_RETRY,
                wait_seconds=120,
                success_probability=0.8,
                reasoning="Quota exceeded - wait longer and retry",
                alternative_actions=["Check quota limits", "Contact support if persistent"]
            ),
            'rpc_code=3': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.NETWORK,
                action=RecoveryAction.RETRY,
                wait_seconds=10,
                success_probability=0.7,
                reasoning="Invalid argument - may be transient, retry",
                alternative_actions=["Check input parameters if retry fails"]
            ),
            'rpc_code=8': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.RATE_LIMIT,
                action=RecoveryAction.WAIT_AND_RETRY,
                wait_seconds=30,
                success_probability=0.85,
                reasoning="Resource exhausted - wait and retry",
                alternative_actions=["Increase wait time incrementally"]
            ),
            'rpc_code=9': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.NETWORK,
                action=RecoveryAction.RETRY,
                wait_seconds=15,
                success_probability=0.75,
                reasoning="Failed precondition - retry may succeed",
                alternative_actions=["Check system state if retry fails"]
            ),
            'timeout': RecoveryStrategy(
                is_retryable=True,
                category=ErrorCategory.TIMEOUT,
                action=RecoveryAction.RETRY,
                wait_seconds=5,
                success_probability=0.8,
                reasoning="Operation timeout - retry with same or increased timeout",
                alternative_actions=["Increase timeout value", "Check network connection"]
            ),
            'authentication': RecoveryStrategy(
                is_retryable=False,
                category=ErrorCategory.AUTH,
                action=RecoveryAction.RE_AUTH,
                wait_seconds=0,
                success_probability=0.0,
                reasoning="Authentication failed - re-authentication required",
                alternative_actions=["Run 'notebooklm login'", "Check credentials"]
            ),
        }

    def analyze_error(self, error_context: ErrorContext) -> RecoveryStrategy:
        """
        Analyze error and recommend recovery strategy.

        Args:
            error_context: Error context information

        Returns:
            RecoveryStrategy with recommended actions
        """
        logger.info(f"[ERROR-ANALYZER] Analyzing error for {error_context.step_name}")

        # Try known patterns first (fast path)
        strategy = self._check_known_patterns(error_context)
        if strategy:
            logger.info(f"[ERROR-ANALYZER] Matched known pattern: {strategy.category.value}")
            return strategy

        # Check cache
        error_hash = self._hash_error(error_context)
        if error_hash in self.error_cache:
            logger.info(f"[ERROR-ANALYZER] Found in cache")
            return self.error_cache[error_hash]

        # Use Gemini for analysis
        if self.agent_config.get('enable_error_analysis', True):
            strategy = self._gemini_analyze(error_context)
            # Cache for future
            self.error_cache[error_hash] = strategy
            return strategy

        # Fallback strategy
        logger.warning(f"[ERROR-ANALYZER] Using fallback strategy")
        return self._fallback_strategy(error_context)

    def _check_known_patterns(self, error_context: ErrorContext) -> Optional[RecoveryStrategy]:
        """Check if error matches known patterns."""
        error_lower = error_context.error_output.lower()

        for pattern, strategy in self.known_patterns.items():
            if pattern in error_lower:
                return strategy

        return None

    def _gemini_analyze(self, error_context: ErrorContext) -> RecoveryStrategy:
        """
        Use Gemini to analyze error.

        Args:
            error_context: Error context

        Returns:
            RecoveryStrategy from Gemini analysis
        """
        try:
            prompt = self._build_analysis_prompt(error_context)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.agent_config.get('temperature', 0.2),
                    max_output_tokens=500,
                )
            )

            # Parse Gemini response
            strategy = self._parse_gemini_response(response.text, error_context)
            logger.info(f"[ERROR-ANALYZER] Gemini analysis: {strategy.category.value}, {strategy.action.value}")

            return strategy

        except Exception as e:
            logger.error(f"[ERROR-ANALYZER] Gemini analysis failed: {e}")
            return self._fallback_strategy(error_context)

    def _build_analysis_prompt(self, error_context: ErrorContext) -> str:
        """Build Gemini analysis prompt."""
        return f"""Analyze this NotebookLM CLI error and provide a recovery strategy.

**Command Executed:**
{error_context.command}

**Error Output:**
{error_context.error_output}

**Context:**
- Step: {error_context.step_name} (step {error_context.step_number})
- Previous steps succeeded: {error_context.previous_steps_succeeded}
- Client: {error_context.client_id}

**Determine:**
1. Root cause category: authentication, rate_limit, quota, network, content, timeout, or unknown
2. Is error retryable? (yes/no)
3. Recommended recovery action: retry, wait_and_retry, skip, re_authenticate, or manual_intervention
4. Estimated wait time before retry (in seconds, 0 if not applicable)
5. Probability of success on retry (0.0-1.0)
6. Brief reasoning (1-2 sentences)

**Respond in this exact format:**
Category: [category]
Retryable: [yes/no]
Action: [action]
Wait: [seconds]
Probability: [0.0-1.0]
Reasoning: [brief explanation]
"""

    def _parse_gemini_response(self, response_text: str, error_context: ErrorContext) -> RecoveryStrategy:
        """Parse Gemini response into RecoveryStrategy."""
        try:
            lines = response_text.strip().split('\n')
            parsed = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed[key.strip().lower()] = value.strip()

            # Extract values
            category_str = parsed.get('category', 'unknown')
            try:
                category = ErrorCategory(category_str)
            except ValueError:
                category = ErrorCategory.UNKNOWN

            is_retryable = parsed.get('retryable', 'no').lower() in ['yes', 'true']

            action_str = parsed.get('action', 'manual_intervention')
            try:
                action = RecoveryAction(action_str)
            except ValueError:
                action = RecoveryAction.MANUAL_INTERVENTION

            wait_seconds = int(parsed.get('wait', '60'))
            probability = float(parsed.get('probability', '0.5'))
            reasoning = parsed.get('reasoning', 'Gemini analysis completed')

            return RecoveryStrategy(
                is_retryable=is_retryable,
                category=category,
                action=action,
                wait_seconds=wait_seconds,
                success_probability=probability,
                reasoning=reasoning,
                alternative_actions=[]
            )

        except Exception as e:
            logger.error(f"[ERROR-ANALYZER] Failed to parse Gemini response: {e}")
            return self._fallback_strategy(error_context)

    def _fallback_strategy(self, error_context: ErrorContext) -> RecoveryStrategy:
        """Fallback recovery strategy when analysis fails."""
        # Conservative fallback: retry with moderate wait
        return RecoveryStrategy(
            is_retryable=True,
            category=ErrorCategory.UNKNOWN,
            action=RecoveryAction.WAIT_AND_RETRY,
            wait_seconds=30,
            success_probability=0.5,
            reasoning="Error analysis unavailable - using conservative retry strategy",
            alternative_actions=["Manual intervention if multiple retries fail"]
        )

    def _hash_error(self, error_context: ErrorContext) -> str:
        """Generate hash for error caching."""
        # Hash based on error output and command type
        error_signature = f"{error_context.command}:{error_context.error_output[:200]}"
        return hashlib.md5(error_signature.encode()).hexdigest()

    def clear_cache(self):
        """Clear error cache."""
        self.error_cache.clear()
        logger.info("[ERROR-ANALYZER] Cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'cache_size': len(self.error_cache),
            'known_patterns': len(self.known_patterns)
        }
