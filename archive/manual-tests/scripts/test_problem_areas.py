#!/usr/bin/env python3
"""
Quick test for Match Form and Optimize Checklist parameter effectiveness
"""
import sys
from test_all_processing_settings import (
    login,
    test_match_form,
    test_optimize_checklist,
)

session = login()

print("\n" + "=" * 80)
print("TESTING: Match Form")
print("=" * 80)

# Test Match Form with different parameters
results_match = []
test_cases = [
    ("vector", True, "enhanced"),
    ("vector", False, "enhanced"),
    ("vector", True, "basic"),
    ("full_scan", True, "enhanced"),
]

for search, vision, pdf in test_cases:
    result, time = test_match_form(session, search, vision, pdf)
    if result:
        results_match.append(result)
        print(f"  {search}+vision_{vision}+pdf_{pdf}: hash={result['hash']}")

print(
    f"\nUnique hashes: {len(set(r['hash'] for r in results_match))}/{len(results_match)}"
)

print("\n" + "=" * 80)
print("TESTING: Optimize Checklist")
print("=" * 80)

# Test Optimize Checklist with different parameters
results_opt = []
for search, vision, pdf in test_cases:
    result, time = test_optimize_checklist(session, search, vision, pdf)
    if result:
        results_opt.append(result)
        print(f"  {search}+vision_{vision}+pdf_{pdf}: hash={result['hash']}")

print(f"\nUnique hashes: {len(set(r['hash'] for r in results_opt))}/{len(results_opt)}")
