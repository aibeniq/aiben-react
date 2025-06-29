#!/usr/bin/env python3
"""
Test the robust JSON parsing logic for handling markdown code blocks
"""

import json


def test_json_parsing():
    """Test JSON parsing that handles markdown code blocks"""

    # Test cases that should all work
    test_cases = [
        # Plain JSON
        '{"mappings": [{"section_text": "Test", "outline_section": 1}]}',
        # JSON with markdown code blocks
        '```json\n{"mappings": [{"section_text": "Test", "outline_section": 1}]}\n```',
        # JSON with just ```
        '```\n{"mappings": [{"section_text": "Test", "outline_section": 1}]}\n```',
        # JSON with extra whitespace
        '  ```json  \n  {"mappings": [{"section_text": "Test", "outline_section": 1}]}  \n  ```  ',
    ]

    for i, test_case in enumerate(test_cases):
        print(f"Test case {i + 1}: {test_case[:50]}...")

        try:
            # Apply the same logic as in the code
            response_text = test_case.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            elif response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```

            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove closing ```

            response_text = response_text.strip()

            json_response = json.loads(response_text)

            if "mappings" in json_response:
                print(f"✓ SUCCESS: Found {len(json_response['mappings'])} mappings")
            else:
                print("✗ FAIL: No mappings found")

        except Exception as e:
            print(f"✗ FAIL: {e}")

        print()


if __name__ == "__main__":
    print("Testing robust JSON parsing logic...")
    test_json_parsing()
    print("Test complete!")
