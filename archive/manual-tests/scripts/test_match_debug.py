#!/usr/bin/env python3
"""
Debug Match Form endpoint
"""
import sys
from test_all_processing_settings import login, BASE_URL, TEST_FILE
from pathlib import Path

session = login()

url = f"{BASE_URL}/formconnect/process"

with open(TEST_FILE, "rb") as f:
    files = {"digitized_files": (Path(TEST_FILE).name, f, "application/pdf")}

    data = {
        "fields": "Product Name\nIngredients\nNutritional Information",
        "search_mode": "vector",
        "vision_analysis_override": "true",
        "pdf_parsing_override": "enhanced",
    }

    print("Sending request...")
    response = session.post(url, files=files, data=data)

print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse JSON:")
import json

print(json.dumps(response.json(), indent=2))
