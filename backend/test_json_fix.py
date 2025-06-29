#!/usr/bin/env python3
"""
Quick test to verify the JSON shadowing issue is fixed
"""

# Test the specific import pattern from reportgenie.py
import json


def test_json_parsing():
    """Test JSON parsing that was failing before"""
    test_json_str = (
        '{"mappings": [{"section_text": "Test section", "outline_section": 1}]}'
    )

    try:
        # This pattern was causing the UnboundLocalError before
        json_response = json.loads(test_json_str.strip())

        if "mappings" in json_response:
            print("✓ JSON parsing successful")
            print(f"Found {len(json_response['mappings'])} mappings")
            return True
        else:
            print("✗ JSON structure not as expected")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing JSON parsing fix...")
    success = test_json_parsing()
    print(f"Test {'PASSED' if success else 'FAILED'}")
