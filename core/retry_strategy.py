"""Shared retry logic for pipeline operations with exponential backoff."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)

RETRYABLE_PATTERNS: List[str] = [
    "rate limit",
    "quota",
    "rpc_code=3",
    "rpc_code=9",
    "rpc_code=8",
    "rpc_code=16",
    "unauthenticated",
    "authentication expired",
    "token refresh failed",
    "transportservererror",
    "failed precondition",
    "no parseable chunks",
]


class RetryableError(Exception):
    """Raised when an operation fails with a retryable condition."""
    pass


class NonRetryableError(Exception):
    """Raised when an operation fails with a non-retryable condition."""
    pass


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 30.0
    max_delay: float = 300.0
    backoff_factor: float = 2.0
    retryable_patterns: List[str] = field(default_factory=lambda: list(RETRYABLE_PATTERNS))


def is_retryable_error(stderr: str, patterns: Optional[List[str]] = None) -> bool:
    """Check if an error message matches any retryable pattern (case-insensitive)."""
    if patterns is None:
        patterns = RETRYABLE_PATTERNS
    stderr_lower = stderr.lower()
    return any(pattern in stderr_lower for pattern in patterns)


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate exponential backoff delay capped at max_delay."""
    delay = config.base_delay * (config.backoff_factor ** attempt)
    return min(delay, config.max_delay)


def execute_with_retry(
    func: Callable[[int], Any],
    config: RetryConfig,
    client_id: str = "",
    operation_name: str = "operation",
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Any:
    """Execute a function with retry logic.

    Args:
        func: Callable that takes (attempt: int) and returns a result.
              Should raise RetryableError for transient failures
              and NonRetryableError for permanent failures.
        config: Retry configuration.
        client_id: Client identifier for log messages.
        operation_name: Human-readable operation name for logging.
        on_retry: Optional callback invoked before each retry with
                  (attempt, exception, delay).

    Returns:
        The return value of func on success.

    Raises:
        NonRetryableError: If func raises a non-retryable error.
        Exception: The last exception if all attempts are exhausted.
    """
    prefix = f"[{client_id}] " if client_id else ""
    last_exception: Optional[Exception] = None

    for attempt in range(config.max_attempts):
        try:
            return func(attempt)
        except NonRetryableError:
            raise
        except RetryableError as e:
            last_exception = e
            if attempt < config.max_attempts - 1:
                delay = calculate_delay(attempt, config)
                logger.warning(
                    f"{prefix}{operation_name} transient error, retrying in {delay:.1f}s "
                    f"(attempt {attempt + 1}/{config.max_attempts}): {e}"
                )
                if on_retry:
                    on_retry(attempt, e, delay)
                time.sleep(delay)
            else:
                logger.error(
                    f"{prefix}{operation_name} failed after {config.max_attempts} attempts: {e}"
                )

    raise last_exception
