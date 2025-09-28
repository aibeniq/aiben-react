"""
Debug the table detection regex
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import re


def test_regex():
    test_content = """
This is some regular content before the table.

<TABLE_START>
{
    "table_number": 1,
    "columns": ["Fee Type", "Amount", "Description"],
    "rows": [
        ["Consultation", "$150", "Initial consultation fee"],
        ["Follow-up", "$100", "Subsequent visit fee"],
        ["Emergency", "$300", "After-hours emergency fee"]
    ]
}
<TABLE_END>

This is content between tables.

<TABLE_START>
{
    "table_number": 2,
    "columns": ["Service", "Duration", "Cost"],
    "rows": [
        ["Diagnostic", "30 min", "$200"],
        ["Treatment", "60 min", "$350"]
    ]
}
<TABLE_END>

This is content after the tables.
"""

    pattern = r"<TABLE_START>.*?<TABLE_END>"
    matches = re.finditer(pattern, test_content, re.DOTALL)

    print("=== REGEX DEBUG ===")
    print(f"Pattern: {pattern}")
    print(f"Content length: {len(test_content)}")
    print()

    match_count = 0
    for match in matches:
        match_count += 1
        print(f"Match {match_count}:")
        print(f"  Start: {match.start()}")
        print(f"  End: {match.end()}")
        print(f"  Content: {match.group()[:100]}...")
        print()

    if match_count == 0:
        print("❌ No matches found!")
        # Try alternative patterns
        print("\nTesting alternative patterns:")

        alt_patterns = [
            r"<TABLE_START>[^<]*<TABLE_END>",
            r"<TABLE_START>[\s\S]*?<TABLE_END>",
            r"<TABLE_START>.*?<TABLE_END>",
        ]

        for i, pattern in enumerate(alt_patterns):
            print(f"\nPattern {i+1}: {pattern}")
            matches = re.finditer(pattern, test_content, re.DOTALL)
            count = len(list(matches))
            print(f"  Found {count} matches")
    else:
        print(f"✅ Found {match_count} table blocks")


if __name__ == "__main__":
    test_regex()
