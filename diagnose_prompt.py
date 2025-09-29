#!/usr/bin/env python3
"""Diagnose the vision processing issue by testing prompt formatting"""

# Test the prompt formatting that might be causing the KeyError
template = """Extract all table data from the images as JSON.

For each table found, return:
{{
  "table_id": "table_N", 
  "page": N,
  "title": "table title/caption",
  "headers": ["col1", "col2", "col3"],
  "rows": [["data1", "data2", "data3"]],
  "summary": "what table shows"
}}

Document: {filename}
Pages: {batch_pages}

Return JSON array in ```json``` blocks.
"""

# Test variables like the vision service would use
variables = {"filename": "APA table example.pdf", "batch_pages": "1"}

print("=== Prompt Template Formatting Test ===")
print("Template length:", len(template))
print("Variables:", variables)

try:
    formatted = template.format(**variables)
    print("✅ Formatting successful!")
    print("Formatted length:", len(formatted))
    print("Formatted preview:")
    print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
except Exception as e:
    print("❌ Formatting failed!")
    print("Error:", e)
    print("Error type:", type(e).__name__)
    import traceback

    print("Traceback:", traceback.format_exc())

# Also test with the problematic string from the logs
print("\n=== Testing Problematic String ===")
test_string = '\n  "table_id"'
print(f"Test string: {repr(test_string)}")
print(f"Length: {len(test_string)}")
print(f"As dict key: trying to access dict[{repr(test_string)}]")

test_dict = {"normal_key": "value"}
try:
    result = test_dict[test_string]
    print("Unexpected: found the key!")
except KeyError as ke:
    print(f"Expected KeyError: {ke}")
    print(f"KeyError repr: {repr(ke)}")
    print(f"KeyError str: {str(ke)}")
