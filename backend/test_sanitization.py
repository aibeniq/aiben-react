#!/usr/bin/env python3
"""
Test the sanitization function for special characters.
"""

import re

def sanitize_text_for_json(text: str) -> str:
    """Sanitize text to prevent JSON parsing issues with control characters."""
    # Replace smart quotes and apostrophes with regular ones
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('ʼ', "'")  # This specific character from the logs
    
    # Remove control characters (characters 0-31 except tab, newline, carriage return)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Replace any remaining problematic Unicode characters
    text = text.encode('ascii', errors='ignore').decode('ascii')
    
    return text

if __name__ == "__main__":
    # Test cases based on the error logs
    test_cases = [
        "Parkinsonʼs Disease",  # The problematic apostrophe
        "This has "smart quotes" in it",
        "Text with — em dashes and – en dashes",
        "Normal text should work fine",
        "Text\x08with\x0Ccontrol\x1Fcharacters",  # Control characters
    ]
    
    print("Testing sanitization function:")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"  Original: {repr(test_text)}")
        try:
            sanitized = sanitize_text_for_json(test_text)
            print(f"  Sanitized: {repr(sanitized)}")
            
            # Test if it's valid in JSON
            import json
            test_json = json.dumps({"text": sanitized})
            print(f"  JSON valid: ✓")
        except Exception as e:
            print(f"  Error: {e}")
        print()
    
    print("All tests completed!")
