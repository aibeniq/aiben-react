#!/usr/bin/env python3
"""
Full 8-combination test for Match Form and Optimize Checklist
"""
import sys
from test_all_processing_settings import (
    login,
    test_match_form,
    test_optimize_checklist,
    analyze_results,
)

session = login()

print("\n" + "=" * 80)
print("TESTING: Match Form (8 combinations)")
print("=" * 80)

results_match = []
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

for search, vision, pdf in test_cases:
    result, time = test_match_form(session, search, vision, pdf)
    if result:
        results_match.append(result)

print("\n" + "-" * 80)
print(
    f"Match Form Results: {len(set(r['hash'] for r in results_match))}/8 unique hashes"
)
for i, result in enumerate(results_match, 1):
    print(f"  {i}. {result['combo']}: hash={result['hash']}")

print("\n" + "=" * 80)
print("TESTING: Optimize Checklist (8 combinations)")
print("=" * 80)

results_opt = []
for search, vision, pdf in test_cases:
    result, time = test_optimize_checklist(session, search, vision, pdf)
    if result:
        results_opt.append(result)

print("\n" + "-" * 80)
print(
    f"Optimize Checklist Results: {len(set(r['hash'] for r in results_opt))}/8 unique hashes"
)
for i, result in enumerate(results_opt, 1):
    print(f"  {i}. {result['combo']}: hash={result['hash']}")
