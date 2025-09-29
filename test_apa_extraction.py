#!/usr/bin/env python3
"""
Test script to analyze the APA table example and debug the vision extraction issues.
"""

import sys
import os
import json
import base64

# Add the backend to the path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

try:
    from backend.app.services.vision_service import VisionService
    from backend.app.services.document_utils import (
        extract_documents_and_images_from_file_unified,
    )
    from backend.app.services.llms import get_llm
    from backend.app.core.config import settings

    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def test_apa_table_extraction():
    """Test the vision extraction on the actual APA table file"""

    # Load the test file
    test_file_path = "test_files/APA table example.pdf"

    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        return

    print(f"📄 Testing file: {test_file_path}")

    # Read the file
    with open(test_file_path, "rb") as f:
        file_content = f.read()

    print(f"📦 File size: {len(file_content)} bytes")

    # Extract images from the PDF
    try:
        documents, images = extract_documents_and_images_from_file_unified(
            file_content, "APA table example.pdf"
        )

        print(f"📄 Extracted documents: {len(documents)}")
        print(f"🖼️ Extracted images: {len(images)}")

        if not images:
            print("❌ No images extracted from PDF")
            return

        # Show first few characters of each image
        for i, img_b64 in enumerate(images):
            print(
                f"  Image {i+1}: {len(img_b64)} characters, starts with: {img_b64[:50]}..."
            )

    except Exception as e:
        print(f"❌ Error extracting images: {e}")
        import traceback

        traceback.print_exc()
        return

    # Get LLM for vision processing
    try:
        llm = get_llm()
        print(f"🤖 LLM: {type(llm).__name__}")

        # Check if vision is enabled
        vision_enabled = VisionService.is_vision_enabled(llm)
        print(f"👁️ Vision enabled: {vision_enabled}")

        if not vision_enabled:
            print("❌ Vision not enabled for current LLM")
            return

    except Exception as e:
        print(f"❌ Error getting LLM: {e}")
        return

    # Test table extraction with current method
    print("\n" + "=" * 60)
    print("TESTING CURRENT TABLE EXTRACTION")
    print("=" * 60)

    try:
        # Use the current vision service method
        page_numbers = list(range(1, len(images) + 1))

        result = VisionService.extract_table_as_json(
            llm=llm,
            page_images=images,
            page_numbers=page_numbers,
            filename="APA table example.pdf",
        )

        print(f"📊 Extraction result type: {type(result)}")
        print(
            f"📊 Extraction keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

        if result.get("tables"):
            tables = result["tables"]
            print(f"📋 Found {len(tables)} tables")

            for i, table in enumerate(tables):
                print(f"\n--- TABLE {i+1} ---")
                print(f"ID: {table.get('table_id', 'Unknown')}")
                print(f"Page: {table.get('page', 'Unknown')}")
                print(f"Title: {table.get('title', 'No title')}")

                headers = table.get("headers", [])
                print(f"Headers ({len(headers)}): {headers}")

                rows = table.get("rows", [])
                print(f"Rows: {len(rows)}")

                if rows:
                    print("First few rows:")
                    for j, row in enumerate(rows[:5]):
                        print(f"  Row {j+1}: {row}")

                # Also check for new structured format
                category_sections = table.get("category_sections", [])
                standalone_rows = table.get("standalone_rows", [])

                if category_sections:
                    print(f"Category sections: {len(category_sections)}")
                    for section in category_sections:
                        print(
                            f"  Section '{section.get('category', 'Unknown')}': {len(section.get('rows', []))} rows"
                        )

                if standalone_rows:
                    print(f"Standalone rows: {len(standalone_rows)}")
        else:
            print("❌ No tables found in extraction result")

    except Exception as e:
        print(f"❌ Error in table extraction: {e}")
        import traceback

        traceback.print_exc()

    # Test with improved prompt
    print("\n" + "=" * 60)
    print("TESTING IMPROVED TABLE EXTRACTION")
    print("=" * 60)

    try:
        # Create a more specific prompt for demographic tables
        improved_prompt = """Analyze this image containing a demographic characteristics table.

This appears to be a research table with multiple treatment groups. Extract ALL data as JSON with this EXACT structure:

{
  "table_id": "table_1", 
  "page": 1,
  "title": "exact table title from image",
  "headers": {
    "Group1Name": ["n", "%"],
    "Group2Name": ["n", "%"], 
    "Group3Name": ["n", "%"],
    "Group4Name": ["n", "%"]
  },
  "rows": [
    {
      "Baseline characteristic": "category name",
      "is_subheader": true/false,
      "values": {
        "Group1Name": {"n": number, "%": number},
        "Group2Name": {"n": number, "%": number},
        "Group3Name": {"n": number, "%": number},
        "Group4Name": {"n": number, "%": number}
      }
    }
  ]
}

CRITICAL REQUIREMENTS:
1. **Multi-column structure**: This table has 4 treatment groups, each with 'n' and '%' columns
2. **Exact numbers**: Extract EVERY number precisely as shown
3. **Group names**: Extract the exact column headers for each treatment group
4. **Category detection**: Rows like "Gender", "Employment" are category headers (is_subheader: true)
5. **Data rows**: Rows like "Female", "Male" contain actual data (is_subheader: false)
6. **All values**: Every cell must have both 'n' and '%' values extracted correctly

Return ONLY the JSON in ```json``` blocks. Do not summarize or explain.
"""

        # Test with the improved prompt
        vision_images = []
        for i, img_b64 in enumerate(images):
            vision_images.append(
                {
                    "image_data": img_b64,
                    "metadata": {
                        "source": "APA table example.pdf",
                        "page": i + 1,
                        "content_type": "demographic_table",
                    },
                }
            )

        result = VisionService.safe_vision_analysis(
            llm=llm,
            prompt_template=improved_prompt,
            variables={"filename": "APA table example.pdf"},
            images=vision_images,
        )

        print(f"📝 Improved extraction result length: {len(result)}")
        print("Raw result:")
        print(result)

        # Try to parse JSON from the result
        import re

        json_match = re.search(
            r"```(?:json)?\s*\n?(\{.*?\})\s*\n?```", result, re.DOTALL | re.IGNORECASE
        )

        if json_match:
            try:
                extracted_json = json_match.group(1)
                parsed_table = json.loads(extracted_json)

                print("\n🎯 SUCCESSFULLY PARSED IMPROVED EXTRACTION:")
                print(f"Title: {parsed_table.get('title', 'Unknown')}")
                print(f"Headers: {parsed_table.get('headers', {})}")
                print(f"Rows: {len(parsed_table.get('rows', []))}")

                # Show detailed row analysis
                rows = parsed_table.get("rows", [])
                for i, row in enumerate(rows):
                    characteristic = row.get("Baseline characteristic", "Unknown")
                    is_subheader = row.get("is_subheader", False)
                    values = row.get("values", {})

                    print(
                        f"\nRow {i+1}: '{characteristic}' (subheader: {is_subheader})"
                    )
                    if not is_subheader and values:
                        for group, data in values.items():
                            if isinstance(data, dict):
                                n_val = data.get("n", "Missing")
                                pct_val = data.get("%", "Missing")
                                print(f"  {group}: n={n_val}, %={pct_val}")
                            else:
                                print(f"  {group}: {data}")

                # Compare with expected data
                print("\n" + "=" * 40)
                print("VALIDATION AGAINST EXPECTED DATA")
                print("=" * 40)

                # Check if we got the right structure
                expected_groups = [
                    "Guided self-help",
                    "Unguided self-help",
                    "Wait-list control",
                    "Full sample",
                ]
                headers = parsed_table.get("headers", {})

                found_groups = list(headers.keys())
                print(f"Expected groups: {expected_groups}")
                print(f"Found groups: {found_groups}")

                # Check specific values for validation
                rows = parsed_table.get("rows", [])
                female_row = next(
                    (
                        row
                        for row in rows
                        if "Female" in row.get("Baseline characteristic", "")
                    ),
                    None,
                )

                if female_row:
                    print(f"\nFemale row validation:")
                    values = female_row.get("values", {})

                    # Expected: Guided=25/50%, Unguided=20/40%, Wait-list=23/46%, Full=68/45%
                    expected_female = {
                        "Guided self-help": {"n": 25, "%": 50},
                        "Unguided self-help": {"n": 20, "%": 40},
                        "Wait-list control": {"n": 23, "%": 46},
                        "Full sample": {"n": 68, "%": 45},
                    }

                    for group, expected in expected_female.items():
                        if group in values:
                            actual = values[group]
                            exp_n, exp_pct = expected["n"], expected["%"]
                            act_n = (
                                actual.get("n")
                                if isinstance(actual, dict)
                                else "Unknown"
                            )
                            act_pct = (
                                actual.get("%")
                                if isinstance(actual, dict)
                                else "Unknown"
                            )

                            match = act_n == exp_n and act_pct == exp_pct
                            status = "✅" if match else "❌"
                            print(
                                f"  {status} {group}: Expected n={exp_n},%= {exp_pct} | Got n={act_n},%={act_pct}"
                            )
                        else:
                            print(f"  ❌ {group}: Missing from extraction")
                else:
                    print("❌ Could not find 'Female' row for validation")

            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse improved extraction JSON: {e}")
                print(f"Raw JSON: {extracted_json[:500]}...")
        else:
            print("❌ No JSON found in improved extraction result")

    except Exception as e:
        print(f"❌ Error in improved table extraction: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_apa_table_extraction()
