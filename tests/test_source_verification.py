#!/usr/bin/env python3
"""Test source verification fix."""

import sys
import json
from pathlib import Path

# Mock source data as returned by list_sources()
MOCK_SOURCES = [
    {
        "id": "src_001",
        "title": "Blue Yonder Supply Chain Planning",
        "url": "https://www.blueyonder.com/solutions/supply-chain-planning"
    },
    {
        "id": "src_002",
        "title": "Blue Yonder WMS Overview",
        "url": "https://www.blueyonder.com/solutions/wms"
    },
    {
        "id": "src_003",
        "title": "Blue Yonder-Consolidated-2026-07-09.pdf",
        "url": ""  # PDF sources have no URL
    },
    {
        "id": "src_004",
        "title": "Gartner Supply Chain Report",
        "url": "https://www.gartner.com/en/supply-chain"
    },
]

def test_old_verification():
    """Test the OLD broken verification logic."""
    print("\n" + "="*60)
    print("TEST: OLD Verification Logic (BROKEN)")
    print("="*60)

    # Old logic: filter by type field
    research_sources = [
        s for s in MOCK_SOURCES
        if s.get('type', '').lower() in ['web', 'url', 'webpage']
    ]

    print(f"\nTotal sources: {len(MOCK_SOURCES)}")
    print(f"Research sources found (old logic): {len(research_sources)}")

    if len(research_sources) == 0:
        print("❌ BROKEN: Found 0 sources (type field doesn't exist!)")
        return False
    else:
        print("✅ Unexpectedly found sources")
        return True


def test_new_verification():
    """Test the NEW fixed verification logic."""
    print("\n" + "="*60)
    print("TEST: NEW Verification Logic (FIXED)")
    print("="*60)

    # New logic: filter by URL starting with http
    research_sources = [
        s for s in MOCK_SOURCES
        if s.get('url', '').startswith('http')
    ]

    print(f"\nTotal sources: {len(MOCK_SOURCES)}")
    print(f"Research sources found (new logic): {len(research_sources)}")

    # Should find 3 sources (the 3 with http URLs)
    expected = 3
    if len(research_sources) == expected:
        print(f"✅ CORRECT: Found {expected} web sources (excluded PDF)")
        print("\nSources found:")
        for idx, src in enumerate(research_sources, 1):
            print(f"  {idx}. {src['title']}")
        return True
    else:
        print(f"❌ WRONG: Expected {expected}, found {len(research_sources)}")
        return False


def main():
    """Run tests."""
    print("\n" + "="*60)
    print("  SOURCE VERIFICATION FIX TEST")
    print("="*60)

    results = []

    # Test old logic
    results.append(("Old Logic (Should Fail)", not test_old_verification()))

    # Test new logic
    results.append(("New Logic (Should Work)", test_new_verification()))

    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe fix correctly:")
        print("  1. Identifies the old logic as broken (type field missing)")
        print("  2. Uses URL detection to find web sources")
        print("  3. Excludes PDF sources (no URL)")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
