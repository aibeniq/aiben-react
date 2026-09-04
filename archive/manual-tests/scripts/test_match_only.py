#!/usr/bin/env python3
"""
Test ONLY Match Form with 2 files for comparison
"""
import sys
from test_all_processing_settings import (
    login,
    test_match_form,
)

session = login()

print("\n" + "=" * 80)
print("TESTING: Match Form with 2 files (Swedish Fish + Karelian Pasty)")
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
print("-" * 80)

for i, result in enumerate(results_match, 1):
    print(f"  {i}. {result['combo']}: hash={result['hash']}")

# Analyze parameter effectiveness
unique_hashes = set(r["hash"] for r in results_match)
print(f"\n{'='*80}")
print(f"ANALYSIS")
print(f"{'='*80}")
print(f"Overall Uniqueness: {len(unique_hashes)}/8 ({len(unique_hashes)/8*100:.1f}%)")

# Search mode analysis
vector_hashes = set(r["hash"] for r in results_match if r["search_mode"] == "vector")
full_scan_hashes = set(
    r["hash"] for r in results_match if r["search_mode"] == "full_scan"
)
search_different = len(vector_hashes.intersection(full_scan_hashes)) < len(
    vector_hashes
)
print(
    f"Search Mode Effectiveness: {'✓ WORKING' if search_different else '✗ NOT WORKING'}"
)

# Vision analysis
vision_true = set(r["hash"] for r in results_match if r["vision"])
vision_false = set(r["hash"] for r in results_match if not r["vision"])
vision_different = len(vision_true.intersection(vision_false)) < len(vision_true)
print(
    f"Vision Analysis Effectiveness: {'✓ WORKING' if vision_different else '✗ NOT WORKING'}"
)

# PDF parsing
pdf_enhanced = set(r["hash"] for r in results_match if r["pdf_parsing"] == "enhanced")
pdf_basic = set(r["hash"] for r in results_match if r["pdf_parsing"] == "basic")
pdf_different = len(pdf_enhanced.intersection(pdf_basic)) < len(pdf_enhanced)
print(f"PDF Parsing Effectiveness: {'✓ WORKING' if pdf_different else '✗ NOT WORKING'}")

print(f"\n{'='*80}")
if len(unique_hashes) == 8:
    print("✅ PERFECT: All 8 combinations produce unique results!")
elif len(unique_hashes) >= 6:
    print("✅ EXCELLENT: High parameter effectiveness")
elif len(unique_hashes) >= 4:
    print("⚠️ GOOD: Partial parameter effectiveness")
else:
    print("⚠️ LIMITED: Low parameter effectiveness")
print(f"{'='*80}")
