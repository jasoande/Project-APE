#!/usr/bin/env python3
"""
Test Gemini Integration
========================
Standalone test script to validate Gemini AI integration before full pipeline run.

Usage:
    python3 test_gemini_integration.py

Requirements:
    - .env file with GEMINI_API_KEY
    - google-genai package installed
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.gemini_manager import GeminiManager


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print('='*70)


def print_result(label: str, value: str):
    """Print a result line."""
    print(f"  {label:20s}: {value}")


def test_gemini_integration():
    """Test Gemini integration with sample companies."""

    print_header("Gemini Integration Test")
    print("  This test validates industry detection and subsegment generation")
    print("  for sample companies using Google's Gemini AI.")

    # Load environment variables
    load_dotenv()

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("  Please add your Gemini API key to the .env file:")
        print("  GEMINI_API_KEY=your-api-key-here")
        sys.exit(1)

    print(f"\n✅ Found GEMINI_API_KEY: {api_key[:20]}...")

    # Configuration matching container-vars.py
    config = {
        'enabled': True,
        'model': 'gemini-2.5-flash',
        'temperature': 0.3,
        'max_retries': 5,
        'retry_base_delay': 10.0,
        'timeout': 60,
        'cache_per_session': True,
    }

    print(f"\n✅ Configuration loaded:")
    print(f"  Model: {config['model']}")
    print(f"  Temperature: {config['temperature']}")
    print(f"  Max retries: {config['max_retries']}")

    # Initialize Gemini Manager
    try:
        gemini = GeminiManager(api_key=api_key, config=config)
        print("\n✅ GeminiManager initialized successfully")
    except Exception as e:
        print(f"\n❌ Failed to initialize GeminiManager: {e}")
        sys.exit(1)

    # Test companies (from container-vars.py)
    test_companies = [
        "Merck",
        "Blue Yonder",
        "Hershey",
        "Lord Abbett",
    ]

    print(f"\n✅ Testing {len(test_companies)} companies...")

    results = []

    for idx, company in enumerate(test_companies, 1):
        print_header(f"Test {idx}/{len(test_companies)}: {company}")

        try:
            # Detect industry
            print(f"\n  🔍 Detecting industry...")
            industry = gemini.detect_industry(company)
            print_result("Industry", industry)

            # Generate subsegments
            print(f"\n  🔍 Generating subsegments...")
            subsegments = gemini.generate_subsegments(company, industry)
            print_result("Subsegments", subsegments)

            # Validate results
            subseg_list = [s.strip() for s in subsegments.split(',')]
            subseg_count = len(subseg_list)

            print(f"\n  ✅ Success!")
            print_result("Subsegment count", str(subseg_count))

            if subseg_count < 2:
                print(f"  ⚠️  Warning: Only {subseg_count} subsegment(s), expected 3-4")

            results.append({
                'company': company,
                'industry': industry,
                'subsegments': subsegments,
                'subseg_count': subseg_count,
                'success': True,
                'error': None
            })

        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            results.append({
                'company': company,
                'industry': None,
                'subsegments': None,
                'subseg_count': 0,
                'success': False,
                'error': str(e)
            })

    # Print summary
    print_header("Test Summary")

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\n  Total tests: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    # Cache statistics
    cache_stats = GeminiManager.get_cache_stats()
    print(f"\n  Cached clients: {cache_stats['cached_clients']}")

    # Detailed results
    print("\n" + "="*70)
    print("  Detailed Results")
    print("="*70)

    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"\n  {status} {r['company']}")
        if r['success']:
            print(f"     Industry: {r['industry']}")
            print(f"     Subsegments: {r['subsegments']}")
            print(f"     Count: {r['subseg_count']}")
        else:
            print(f"     Error: {r['error']}")

    # Final verdict
    print("\n" + "="*70)
    if failed == 0:
        print("  🎉 ALL TESTS PASSED!")
        print("  Gemini integration is working correctly.")
        print("="*70)
        return 0
    else:
        print(f"  ⚠️  {failed} TEST(S) FAILED")
        print("  Please review errors above and check your API key/quota.")
        print("="*70)
        return 1


if __name__ == "__main__":
    try:
        exit_code = test_gemini_integration()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
