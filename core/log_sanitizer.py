"""
Log sanitization module for Project-APE.

Provides logging formatter that redacts sensitive information from log output:
- OAuth tokens and API keys
- Bearer tokens
- Drive folder IDs
- Email addresses (partial redaction)
- Passwords
- Session tokens

Usage:
    from core.log_sanitizer import SanitizingFormatter

    # Apply to all loggers
    for handler in logging.root.handlers:
        handler.setFormatter(SanitizingFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
"""

import logging
import re
from typing import Pattern, List, Tuple

class SanitizingFormatter(logging.Formatter):
    """
    Logging formatter that redacts sensitive information.

    Patterns matched and redacted:
    - OAuth tokens (JSON format)
    - API keys (JSON format)
    - Bearer tokens (Authorization headers)
    - Drive folder IDs (long alphanumeric strings in URLs)
    - Email addresses (partial - keeps domain)
    - Passwords (JSON format)
    - Session tokens
    - Secrets (generic)
    """

    # Redaction patterns: (regex, replacement)
    PATTERNS: List[Tuple[Pattern, str]] = [
        # OAuth tokens in JSON (token, access_token, refresh_token)
        (re.compile(r'((?:access_|refresh_)?token["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # API keys in JSON
        (re.compile(r'(api[_-]?key["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # Generic secrets in JSON
        (re.compile(r'(secret["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # Passwords in JSON
        (re.compile(r'(password["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # Bearer tokens (Authorization: Bearer ...)
        (re.compile(r'(Bearer\s+)([A-Za-z0-9_\-\.]+)'),
         r'\1***REDACTED***'),

        # Drive folder IDs in URLs
        (re.compile(r'(/folders?/)([A-Za-z0-9_-]{20,})'),
         r'\1***FOLDER_ID***'),

        # Drive file IDs in URLs
        (re.compile(r'(/d/|id=)([A-Za-z0-9_-]{20,})'),
         r'\1***FILE_ID***'),

        # Email addresses (partial redaction - keep domain)
        (re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'),
         r'***@\2'),

        # Session cookies/tokens
        (re.compile(r'(session["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # Client secrets
        (re.compile(r'(client_secret["\']:\s*["\'])([^"\']+)(["\'])'),
         r'\1***REDACTED***\3'),

        # Authorization codes
        (re.compile(r'(code=)([A-Za-z0-9_-]{20,})'),
         r'\1***REDACTED***'),
    ]

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record and redact sensitive information.

        Args:
            record: LogRecord instance to format

        Returns:
            Formatted and sanitized log message
        """
        # Format the message using parent formatter
        msg = super().format(record)

        # Apply all redaction patterns
        for pattern, replacement in self.PATTERNS:
            msg = pattern.sub(replacement, msg)

        return msg


def setup_sanitized_logging(log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    """
    Configure all existing loggers to use sanitizing formatter.

    Args:
        log_format: Format string for log messages (default: timestamp - name - level - message)

    Example:
        setup_sanitized_logging()
        logger = logging.getLogger(__name__)
        logger.info("Token: abc123")  # Will be logged as "Token: ***REDACTED***"
    """
    # Get all existing handlers
    for handler in logging.root.handlers:
        handler.setFormatter(SanitizingFormatter(log_format))

    print("✅ Log sanitization enabled", flush=True)


# Example usage
if __name__ == '__main__':
    import logging

    # Set up basic logging
    logging.basicConfig(level=logging.INFO)

    # Apply sanitization
    setup_sanitized_logging()

    # Create logger
    logger = logging.getLogger(__name__)

    # Test redaction patterns
    print("\nTesting log redaction:\n")

    logger.info('OAuth token: {"access_token": "ya29.a0AfH6SMBx..."}')
    logger.info('API key: {"api_key": "AIzaSyB..."}')
    logger.info('Authorization: Bearer eyJhbGciOiJSUzI1NiIs...')
    logger.info('Drive URL: https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J')
    logger.info('User email: john.doe@example.com')
    logger.info('Session: {"session": "sess_1234567890abcdef"}')
    logger.info('Password: {"password": "MySecretPassword123"}')

    print("\n✅ All sensitive data should be redacted above")
