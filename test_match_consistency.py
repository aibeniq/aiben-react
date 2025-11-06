#!/usr/bin/env python3
"""
Run Match Form test 3 times to check consistency
"""
import sys
from test_all_processing_settings import (
    login,
    test_match_form,
)

session = login()

test_cases = [
    ("vector", True, "enhanced"),
    ("vector", True, "basic"),
    ("vector", False, "enhanced"),
    ("vector", False, "basic"),
    ("full_scan", True, "enhanced"),
    ("full_scan", True, "basic"),
    ("full_scan", False, "enhanced"),
    ("full_scan", False, "basic"),
]

for run in range(1, 4):
    print("\n" + "=" * 80)
    print(f"RUN #{run}: Match Form with 2 files")
    print("=" * 80)

    results = []
    for search, vision, pdf in test_cases:
        result, time = test_match_form(session, search, vision, pdf)
        if result:
            results.append(result)

    print(f"\nRun #{run} - Unique hashes: {len(set(r['hash'] for r in results))}/8")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['combo']}: {result['hash']}")
