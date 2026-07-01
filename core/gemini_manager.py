"""
Gemini Manager - AI-powered industry detection and subsegment generation

This module provides intelligent industry classification and subsegment
identification using Google's Gemini AI model. It enables automatic
configuration of client industry data without manual input.
"""

import logging
import os
import time
from typing import Dict, Optional, Tuple

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiManager:
    """
    Manages interactions with Google Gemini API for industry intelligence.

    Features:
    - Automatic industry detection from company name
    - AI-generated industry subsegments for technical account planning
    - Session-level caching to minimize API calls
    - Exponential backoff retry logic for resilience
    - Comprehensive error handling and validation
    """

    # Class-level cache shared across all instances in a session
    _session_cache: Dict[str, Tuple[str, str]] = {}

    def __init__(self, api_key: str, config: dict):
        """
        Initialize Gemini Manager.

        Args:
            api_key: Google Gemini API key
            config: Configuration dictionary with:
                - model: Gemini model name (default: gemini-1.5-pro-002)
                - temperature: Response randomness 0-1 (default: 0.3)
                - max_retries: Max retry attempts (default: 5)
                - retry_base_delay: Base retry delay in seconds (default: 10.0)
                - timeout: API call timeout in seconds (default: 60)
                - cache_per_session: Enable session caching (default: True)

        Raises:
            ValueError: If API key is missing or invalid
        """
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please add it to your vars.py configuration."
            )

        self.api_key = api_key
        self.model_name = config.get('model', 'gemini-2.5-flash')
        self.temperature = config.get('temperature', 0.3)
        self.max_retries = config.get('max_retries', 5)
        self.retry_base_delay = config.get('retry_base_delay', 10.0)
        self.timeout = config.get('timeout', 60)
        self.cache_enabled = config.get('cache_per_session', True)

        # Initialize Gemini client with new SDK
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"[GEMINI] Initialized with model: {self.model_name}")

    def detect_industry(self, client_name: str) -> str:
        """
        Detect the primary industry for a given company name.

        Args:
            client_name: Name of the company

        Returns:
            Industry sector as lowercase string (e.g., "pharmaceuticals and healthcare")

        Raises:
            Exception: If all retry attempts fail
        """
        # Check cache first
        if self.cache_enabled and client_name in self._session_cache:
            logger.info(f"[GEMINI] Cache hit for {client_name}")
            industry, _ = self._session_cache[client_name]
            return industry

        logger.info(f"[GEMINI] Detecting industry for client: {client_name}")

        prompt = f"""You are an expert business analyst. Given the company name "{client_name}", identify the primary industry sector this company operates in.

Respond with ONLY the industry name in lowercase, using 2-7 words maximum.
Examples: "pharmaceuticals and healthcare", "financial services", "electronics, technology, and manufacturing"

Company name: {client_name}
Industry:"""

        industry = self._call_gemini_with_retry(
            prompt=prompt,
            operation="industry detection",
            client_name=client_name
        )

        # Validate response
        industry = industry.strip().lower()
        if not industry or industry in ['unknown', 'n/a', 'not available']:
            raise ValueError(
                f"Gemini returned invalid industry for {client_name}: {industry}"
            )

        logger.info(f"[GEMINI] Industry detected: {industry}")
        return industry

    def generate_subsegments(self, client_name: str, industry: str) -> str:
        """
        Generate relevant industry subsegments for technical account planning.

        Args:
            client_name: Name of the company
            industry: Industry sector (from detect_industry)

        Returns:
            Comma-separated subsegments (e.g., "cloud infrastructure, enterprise software")

        Raises:
            Exception: If all retry attempts fail
        """
        # Check cache first
        if self.cache_enabled and client_name in self._session_cache:
            logger.info(f"[GEMINI] Cache hit for {client_name}")
            _, subsegments = self._session_cache[client_name]
            return subsegments

        logger.info(
            f"[GEMINI] Generating subsegments for {client_name} "
            f"in {industry}"
        )

        prompt = f"""You are a technical account planning specialist. For company "{client_name}" in the "{industry}" industry, identify the top 3 most relevant business subsegments for creating a Red Hat technical account plan.

Focus on:
- Core business divisions or product lines
- Strategic technology focus areas
- Market segments the company serves

Respond with ONLY a comma-separated list of 3-4 subsegments, lowercase, no additional text.

Example format: "cloud infrastructure, enterprise software, cybersecurity"

Company: {client_name}
Industry: {industry}
Subsegments:"""

        subsegments = self._call_gemini_with_retry(
            prompt=prompt,
            operation="subsegment generation",
            client_name=client_name
        )

        # Validate response
        subsegments = subsegments.strip().lower().rstrip(',')  # Remove trailing comma
        if not subsegments or subsegments in ['unknown', 'n/a', 'not available']:
            raise ValueError(
                f"Gemini returned invalid subsegments for {client_name}: {subsegments}"
            )

        # Ensure we have multiple subsegments
        subseg_list = [s.strip() for s in subsegments.split(',')]
        if len(subseg_list) < 2:
            logger.warning(
                f"[GEMINI] Only {len(subseg_list)} subsegment(s) returned "
                f"for {client_name}, expected 3-4"
            )

        logger.info(f"[GEMINI] Subsegments: {subsegments}")

        # Cache the results
        if self.cache_enabled:
            industry_from_cache = (
                self._session_cache[client_name][0]
                if client_name in self._session_cache
                else industry
            )
            self._session_cache[client_name] = (industry_from_cache, subsegments)
            logger.info(f"[GEMINI] Cached results for {client_name}")

        return subsegments

    def _call_gemini_with_retry(
        self,
        prompt: str,
        operation: str,
        client_name: str
    ) -> str:
        """
        Call Gemini API with exponential backoff retry logic.

        Args:
            prompt: Prompt text to send to Gemini
            operation: Human-readable operation name for logging
            client_name: Client name for logging context

        Returns:
            Response text from Gemini

        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"[GEMINI] {operation.capitalize()} API call "
                    f"(attempt {attempt}/{self.max_retries})"
                )

                # Make API call with new SDK
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=256,
                    )
                )

                # Extract text from response
                if not response.text:
                    raise ValueError("Empty response from Gemini API")

                logger.info(
                    f"[GEMINI] API call successful ({attempt}/{self.max_retries})"
                )
                return response.text

            except Exception as e:
                # Check if retryable error
                error_str = str(e).lower()
                is_retryable = any(keyword in error_str for keyword in [
                    'resource_exhausted', 'resourceexhausted',
                    'too many requests', 'rate limit',
                    'quota', 'unavailable', 'deadline'
                ])

                if is_retryable:
                    last_error = e
                    error_type = type(e).__name__

                    logger.warning(
                        f"[GEMINI] {operation.capitalize()} failed "
                        f"(attempt {attempt}/{self.max_retries}): {error_type}"
                    )

                    if attempt < self.max_retries:
                        # Exponential backoff: 10s, 20s, 40s, 80s, 160s
                        retry_delay = self.retry_base_delay * (2 ** (attempt - 1))
                        logger.info(f"[GEMINI] Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(
                            f"[GEMINI] All {self.max_retries} attempts failed "
                            f"for {client_name}"
                        )
                        raise Exception(
                            f"Gemini API {operation} failed after {self.max_retries} "
                            f"attempts: {error_type}"
                        ) from last_error
                else:
                    # Non-retryable errors
                    logger.error(
                        f"[GEMINI] {operation.capitalize()} failed with "
                        f"non-retryable error: {type(e).__name__}: {str(e)}"
                    )
                    raise

        # Should never reach here, but just in case
        raise Exception(
            f"Gemini API {operation} failed after {self.max_retries} attempts"
        )

    @classmethod
    def clear_cache(cls):
        """Clear the session-level cache. Useful for testing."""
        cls._session_cache.clear()
        logger.info("[GEMINI] Session cache cleared")

    @classmethod
    def get_cache_stats(cls) -> dict:
        """Get cache statistics for monitoring."""
        return {
            'cached_clients': len(cls._session_cache),
            'client_names': list(cls._session_cache.keys())
        }
