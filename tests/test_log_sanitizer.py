#!/usr/bin/env python3
"""
Test log sanitization.

This test validates:
1. Sensitive data is redacted from logs
2. Sanitizing formatter works with all patterns
3. Normal log content is preserved
4. setup_sanitized_logging applies to all handlers
"""

import sys
from pathlib import Path
import logging
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.log_sanitizer import SanitizingFormatter, setup_sanitized_logging


def test_oauth_token_redaction():
    """Test that OAuth tokens are redacted."""

    print("\n🧪 Test 1: OAuth token redaction...")

    formatter = SanitizingFormatter('%(message)s')

    # Create a mock log record
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Token: {"access_token": "ya29.a0AfH6SMBx"}',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert 'ya29.a0AfH6SMBx' not in formatted, "❌ OAuth token not redacted"
    assert '***REDACTED***' in formatted, "❌ Redaction marker not present"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ OAuth token redacted")


def test_api_key_redaction():
    """Test that API keys are redacted."""

    print("\n🧪 Test 2: API key redaction...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='API Key: {"api_key": "AIzaSyB1234567890"}',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert 'AIzaSyB1234567890' not in formatted, "❌ API key not redacted"
    assert '***REDACTED***' in formatted, "❌ Redaction marker not present"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ API key redacted")


def test_bearer_token_redaction():
    """Test that Bearer tokens are redacted."""

    print("\n🧪 Test 3: Bearer token redaction...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Authorization: Bearer eyJhbGciOiJSUzI1NiIs',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert 'eyJhbGciOiJSUzI1NiIs' not in formatted, "❌ Bearer token not redacted"
    assert 'Bearer ***REDACTED***' in formatted, "❌ Bearer prefix or redaction missing"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Bearer token redacted")


def test_drive_folder_id_redaction():
    """Test that Drive folder IDs are redacted."""

    print("\n🧪 Test 4: Drive folder ID redaction...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Folder URL: https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert '1A2B3C4D5E6F7G8H9I0J' not in formatted, "❌ Folder ID not redacted"
    assert '***FOLDER_ID***' in formatted, "❌ Folder ID redaction marker not present"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Drive folder ID redacted")


def test_email_redaction():
    """Test that email addresses are partially redacted."""

    print("\n🧪 Test 5: Email address redaction...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='User: john.doe@example.com logged in',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert 'john.doe' not in formatted, "❌ Email local part not redacted"
    assert '***@example.com' in formatted, "❌ Email domain not preserved or marker missing"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Email address redacted (domain preserved)")


def test_password_redaction():
    """Test that passwords are redacted."""

    print("\n🧪 Test 6: Password redaction...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Credentials: {"password": "MySecretPassword123"}',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert 'MySecretPassword123' not in formatted, "❌ Password not redacted"
    assert '***REDACTED***' in formatted, "❌ Redaction marker not present"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Password redacted")


def test_normal_content_preserved():
    """Test that normal log content is preserved."""

    print("\n🧪 Test 7: Normal content preservation...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Processing client XYZ with 100 records',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    assert formatted == 'Processing client XYZ with 100 records', "❌ Normal content was modified"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Normal content preserved")


def test_multiple_redactions():
    """Test that multiple sensitive items in one message are all redacted."""

    print("\n🧪 Test 8: Multiple redactions in one message...")

    formatter = SanitizingFormatter('%(message)s')

    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='Login: user@example.com with {"api_key": "KEY123"} to folder/ABC123DEF456GHI789',
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)

    # Check email redacted
    assert 'user@example.com' not in formatted, "❌ Email not redacted"
    assert '***@example.com' in formatted, "❌ Email redaction marker missing"

    # Check API key redacted
    assert 'KEY123' not in formatted, "❌ API key not redacted"

    print(f"   Input:  {record.msg}")
    print(f"   Output: {formatted}")
    print("   ✅ Multiple items redacted in single message")


def test_setup_sanitized_logging():
    """Test that setup_sanitized_logging applies to all handlers."""

    print("\n🧪 Test 9: setup_sanitized_logging function...")

    # Save existing handlers
    existing_handlers = logging.root.handlers[:]

    # Clear root handlers for clean test
    logging.root.handlers = []

    try:
        # Add a handler that writes to a string buffer
        buffer = io.StringIO()
        handler = logging.StreamHandler(buffer)
        handler.setLevel(logging.INFO)

        # Add handler to root logger (where setup_sanitized_logging will find it)
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)

        # Apply sanitization (should affect the handler we just added)
        setup_sanitized_logging()

        # Log something sensitive using root logger
        logging.info('Token: {"access_token": "SECRET123"}')

        # Get the logged output
        output = buffer.getvalue()

        assert 'SECRET123' not in output, f"❌ Token not redacted: {output}"
        assert '***REDACTED***' in output, f"❌ Redaction marker not present: {output}"

        print(f"   Logged: {output.strip()}")
        print("   ✅ setup_sanitized_logging works correctly")

    finally:
        # Restore original handlers
        logging.root.handlers = existing_handlers


if __name__ == '__main__':
    try:
        test_oauth_token_redaction()
        test_api_key_redaction()
        test_bearer_token_redaction()
        test_drive_folder_id_redaction()
        test_email_redaction()
        test_password_redaction()
        test_normal_content_preserved()
        test_multiple_redactions()
        test_setup_sanitized_logging()

        print("\n" + "="*60)
        print("✅ ALL LOG SANITIZATION TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
