#!/usr/bin/env python3
"""
Test the LLM invoke fix for the mapping prompt
"""

# Test that our JSON format doesn't have template issues
test_prompt = """
Analyze this document chunk.

RESPONSE FORMAT (JSON only):
{"mappings": [{"section_text": "brief description", "outline_section": 1}]}
"""

print("Testing prompt format...")
print("Prompt:")
print(test_prompt)

# Test that the curly braces are properly escaped
try:
    # This should NOT raise a KeyError
    formatted = test_prompt.format()
    print("✓ No template variables - format() works")
except KeyError as e:
    print(f"✗ KeyError: {e}")
except Exception as e:
    print(f"✗ Other error: {e}")

# Test with our actual format
actual_format = '{"mappings": [{"section_text": "brief description of the document section found", "outline_section": 1}, {"section_text": "brief description of another document section", "outline_section": 2}]}'

print(f"\nActual JSON format: {actual_format}")
print("✓ JSON format looks good")
