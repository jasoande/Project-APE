"""Tests for core/retry_strategy.py - shared retry logic with exponential backoff."""

import pytest

from core.retry_strategy import (
    RETRYABLE_PATTERNS,
    NonRetryableError,
    RetryableError,
    RetryConfig,
    calculate_delay,
    execute_with_retry,
    is_retryable_error,
)


# ---------------------------------------------------------------------------
# TestIsRetryableError
# ---------------------------------------------------------------------------
class TestIsRetryableError:
    """Verify pattern matching against known retryable error strings."""

    @pytest.mark.parametrize(
        "error_text",
        [
            "Rate limit exceeded for this project",
            "Quota exhausted, try again later",
            "Error rpc_code=3: resource exhausted",
            "Error rpc_code=9: precondition failed",
            "Error rpc_code=8: resource exhausted",
            "Error rpc_code=16: unauthenticated",
            "Unauthenticated - please re-login",
            "Authentication expired for session",
            "Token refresh failed: invalid grant",
            "TransportServerError: 503",
            "Failed precondition: stale read",
            "No parseable chunks in response",
        ],
    )
    def test_retryable_patterns_recognized(self, error_text):
        assert is_retryable_error(error_text) is True

    def test_non_retryable_strings(self):
        assert is_retryable_error("File not found: /tmp/data.csv") is False
        assert is_retryable_error("Permission denied") is False
        assert is_retryable_error("Invalid argument supplied") is False
        assert is_retryable_error("") is False

    def test_case_insensitivity(self):
        assert is_retryable_error("RATE LIMIT exceeded") is True
        assert is_retryable_error("QUOTA EXHAUSTED") is True
        assert is_retryable_error("RPC_CODE=3") is True
        assert is_retryable_error("TransportServerError") is True

    def test_custom_patterns(self):
        custom = ["custom_error", "special_failure"]
        assert is_retryable_error("hit a custom_error today", patterns=custom) is True
        assert is_retryable_error("got a timeout", patterns=custom) is False


# ---------------------------------------------------------------------------
# TestCalculateDelay
# ---------------------------------------------------------------------------
class TestCalculateDelay:
    """Verify exponential backoff delay calculation."""

    def test_first_attempt_returns_base_delay(self):
        cfg = RetryConfig(base_delay=10.0, backoff_factor=2.0, max_delay=300.0)
        # attempt 0 => base_delay * (2.0 ** 0) = 10.0
        assert calculate_delay(0, cfg) == 10.0

    def test_exponential_growth(self):
        cfg = RetryConfig(base_delay=10.0, backoff_factor=2.0, max_delay=1000.0)
        assert calculate_delay(0, cfg) == 10.0
        assert calculate_delay(1, cfg) == 20.0
        assert calculate_delay(2, cfg) == 40.0
        assert calculate_delay(3, cfg) == 80.0

    def test_max_delay_caps_properly(self):
        cfg = RetryConfig(base_delay=10.0, backoff_factor=2.0, max_delay=50.0)
        # attempt 3 => 10 * 8 = 80, but capped at 50
        assert calculate_delay(3, cfg) == 50.0
        # attempt 10 => 10 * 1024, still capped at 50
        assert calculate_delay(10, cfg) == 50.0


# ---------------------------------------------------------------------------
# TestExecuteWithRetry
# ---------------------------------------------------------------------------
class TestExecuteWithRetry:
    """Verify the retry orchestration function."""

    def test_success_on_first_attempt(self):
        call_count = 0

        def succeed(attempt):
            nonlocal call_count
            call_count += 1
            return "ok"

        cfg = RetryConfig(max_attempts=3, base_delay=0.01)
        result = execute_with_retry(succeed, cfg)
        assert result == "ok"
        assert call_count == 1

    def test_success_after_retries(self):
        call_count = 0

        def fail_then_succeed(attempt):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("transient error")
            return "recovered"

        cfg = RetryConfig(max_attempts=5, base_delay=0.01)
        result = execute_with_retry(fail_then_succeed, cfg)
        assert result == "recovered"
        assert call_count == 3

    def test_non_retryable_error_stops_immediately(self):
        call_count = 0

        def always_fail(attempt):
            nonlocal call_count
            call_count += 1
            raise NonRetryableError("permanent failure")

        cfg = RetryConfig(max_attempts=5, base_delay=0.01)
        with pytest.raises(NonRetryableError, match="permanent failure"):
            execute_with_retry(always_fail, cfg)
        assert call_count == 1

    def test_exhausted_retries_raises_last_exception(self):
        def always_transient(attempt):
            raise RetryableError(f"transient #{attempt}")

        cfg = RetryConfig(max_attempts=3, base_delay=0.01)
        with pytest.raises(RetryableError, match="transient #2"):
            execute_with_retry(always_transient, cfg)

    def test_on_retry_callback_called(self):
        retry_log = []

        def fail_twice(attempt):
            if attempt < 2:
                raise RetryableError("oops")
            return "done"

        def on_retry_cb(attempt, exc, delay):
            retry_log.append((attempt, str(exc), delay))

        cfg = RetryConfig(max_attempts=5, base_delay=0.01)
        result = execute_with_retry(
            fail_twice, cfg, on_retry=on_retry_cb
        )
        assert result == "done"
        assert len(retry_log) == 2
        # Verify callback received correct attempt numbers
        assert retry_log[0][0] == 0
        assert retry_log[1][0] == 1
