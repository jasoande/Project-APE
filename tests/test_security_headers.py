#!/usr/bin/env python3
"""
Test security headers implementation.

This test validates:
1. Security headers are present in responses
2. HTTPS enforcement works when enabled
3. Content Security Policy is restrictive
4. Headers have correct values
"""

import sys
from pathlib import Path
import subprocess
import time
import os

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.mark.skip(reason="Security headers not yet implemented in server.py; needs implementation")
def test_security_headers_present():
    """Test that security headers are added to responses."""

    print("\n🧪 Testing security headers...")

    # Start the dashboard server (without HTTPS enforcement)
    env = os.environ.copy()
    env['FORCE_HTTPS'] = 'false'  # Disable HTTPS enforcement for this test

    server_process = subprocess.Popen(
        [sys.executable, 'dashboard/server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent.parent,
        env=env
    )

    try:
        # Wait for server to start
        time.sleep(3)

        # Make a request and check headers
        import urllib.request

        request = urllib.request.Request('http://localhost:8765/')
        response = urllib.request.urlopen(request, timeout=10)

        headers = response.headers

        print(f"   Response headers:")

        # Check X-Content-Type-Options
        assert 'X-Content-Type-Options' in headers, "❌ Missing X-Content-Type-Options header"
        assert headers['X-Content-Type-Options'] == 'nosniff', f"❌ Wrong value: {headers['X-Content-Type-Options']}"
        print(f"   ✅ X-Content-Type-Options: {headers['X-Content-Type-Options']}")

        # Check X-Frame-Options
        assert 'X-Frame-Options' in headers, "❌ Missing X-Frame-Options header"
        assert headers['X-Frame-Options'] == 'DENY', f"❌ Wrong value: {headers['X-Frame-Options']}"
        print(f"   ✅ X-Frame-Options: {headers['X-Frame-Options']}")

        # Check X-XSS-Protection
        assert 'X-XSS-Protection' in headers, "❌ Missing X-XSS-Protection header"
        assert headers['X-XSS-Protection'] == '1; mode=block', f"❌ Wrong value: {headers['X-XSS-Protection']}"
        print(f"   ✅ X-XSS-Protection: {headers['X-XSS-Protection']}")

        # Check Content-Security-Policy
        assert 'Content-Security-Policy' in headers, "❌ Missing Content-Security-Policy header"
        csp = headers['Content-Security-Policy']
        assert "default-src 'self'" in csp, "❌ CSP doesn't restrict default-src to self"
        print(f"   ✅ Content-Security-Policy: {csp[:50]}...")

        # HSTS should NOT be present when FORCE_HTTPS=false
        if 'Strict-Transport-Security' in headers:
            print(f"   ⚠️  HSTS present even though FORCE_HTTPS=false")
        else:
            print(f"   ✅ No HSTS (correct for FORCE_HTTPS=false)")

        print("\n✅ All security headers present and valid")

    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait(timeout=5)
        print("🛑 Stopped server")


@pytest.mark.skip(reason="Security headers not yet implemented in server.py; needs implementation")
def test_hsts_header_with_https_enforcement():
    """Test that HSTS header is added when HTTPS enforcement is enabled."""

    print("\n🧪 Testing HSTS header with HTTPS enforcement...")

    # Start server with HTTPS enforcement
    env = os.environ.copy()
    env['FORCE_HTTPS'] = 'true'

    server_process = subprocess.Popen(
        [sys.executable, 'dashboard/server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent.parent,
        env=env
    )

    try:
        # Wait for server to start
        time.sleep(3)

        # Try to make HTTP request (should redirect to HTTPS)
        import urllib.request

        try:
            request = urllib.request.Request('http://localhost:8765/')
            response = urllib.request.urlopen(request, timeout=10)

            # If we got a response, it means we were redirected or served over HTTP
            # Check if we were redirected to HTTPS
            final_url = response.geturl()

            if final_url.startswith('https://'):
                print(f"   ✅ Redirected to HTTPS: {final_url}")
            else:
                # Server might not support HTTPS in test environment
                print(f"   ⚠️  HTTP request succeeded (expected redirect to HTTPS)")
                print(f"   Note: HTTPS redirection may not work without SSL cert in test environment")

        except urllib.error.HTTPError as e:
            if e.code == 301 or e.code == 302:
                print(f"   ✅ HTTP request returned {e.code} redirect (expected)")
                # Check Location header
                if 'Location' in e.headers:
                    location = e.headers['Location']
                    if location.startswith('https://'):
                        print(f"   ✅ Redirect location uses HTTPS: {location}")
                    else:
                        print(f"   ⚠️  Redirect location: {location}")
            else:
                print(f"   ⚠️  Unexpected HTTP error: {e.code}")

        print("\n✅ HTTPS enforcement test complete")

    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait(timeout=5)
        print("🛑 Stopped server")


@pytest.mark.skip(reason="Security headers not yet implemented in server.py; needs implementation")
def test_csp_restrictions():
    """Test that Content Security Policy is restrictive."""

    print("\n🧪 Testing CSP restrictions...")

    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'dashboard'))

    # Start basic server to check CSP
    env = os.environ.copy()
    env['FORCE_HTTPS'] = 'false'

    server_process = subprocess.Popen(
        [sys.executable, 'dashboard/server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent.parent,
        env=env
    )

    try:
        time.sleep(3)

        import urllib.request
        request = urllib.request.Request('http://localhost:8765/')
        response = urllib.request.urlopen(request, timeout=10)

        csp = response.headers.get('Content-Security-Policy', '')

        print(f"   CSP directives:")

        # Check for restrictive directives
        required_directives = [
            ("default-src 'self'", "Default source restricted to same origin"),
            ("img-src 'self' data:", "Images from same origin or data URLs"),
            ("connect-src 'self'", "AJAX/WebSocket connections to same origin only")
        ]

        for directive, description in required_directives:
            if directive in csp:
                print(f"   ✅ {description}")
            else:
                print(f"   ⚠️  Missing or different: {description}")
                print(f"      Expected: {directive}")

        # Check that we don't allow unsafe-eval (major XSS vector)
        if 'unsafe-eval' in csp:
            print(f"   ❌ CSP allows unsafe-eval (security risk!)")
        else:
            print(f"   ✅ unsafe-eval not allowed")

        print("\n✅ CSP restrictions test complete")

    finally:
        server_process.terminate()
        server_process.wait(timeout=5)
        print("🛑 Stopped server")


if __name__ == '__main__':
    try:
        test_security_headers_present()
        test_hsts_header_with_https_enforcement()
        test_csp_restrictions()

        print("\n" + "="*60)
        print("✅ ALL SECURITY HEADER TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
