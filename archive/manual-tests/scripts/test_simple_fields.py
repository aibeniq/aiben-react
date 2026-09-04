#!/usr/bin/env python3
"""
Test Match Form with simpler fields
"""
import sys
from test_all_processing_settings import login, BASE_URL, TEST_FILE
from pathlib import Path
import json

session = login()

url = f"{BASE_URL}/formconnect/process"

# Try different field sets
field_sets = [
    "Product\nIngredients\nPrice",
    "Name\nDescription\nDetails",
    "Title\nContent\nSummary",
]

for fields in field_sets:
    print(f"\n{'='*80}")
    print(f"Testing with fields: {fields.replace(chr(10), ', ')}")
    print("=" * 80)

    with open(TEST_FILE, "rb") as f:
        files = {"digitized_files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "fields": fields,
            "search_mode": "full_scan",  # Use full_scan for better extraction
            "vision_analysis_override": "true",
            "pdf_parsing_override": "enhanced",
        }

        response = session.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        extracted = result.get("results", {}).get("extracted_data", {})
        print(f"\nExtracted Data:")
        for key, value in extracted.items():
            value_preview = value[:100] if len(str(value)) > 100 else value
            print(f"  {key}: {value_preview}")
    else:
        print(f"ERROR: {response.status_code}")
