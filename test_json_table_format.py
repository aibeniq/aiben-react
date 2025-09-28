#!/usr/bin/env python3
"""
Test script to validate the new JSON table format implementation.
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.smart_chunking import TablePreservingTextSplitter


def test_json_table_format():
    """Test the new JSON table format processing"""

    # Sample content with new JSON table format
    sample_content = """This is some regular text before the table.

=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "Fee Schedule",
    "page": 1,
    "summary": "Trading fees for different instruments",
    "context": "Fee information for various trading options",
    "dimensions": "3 rows × 3 columns"
  }
}

[
  {
    "Product": "Stocks",
    "Smart Plan": "0.02 USD",
    "All-inclusive": "2 USD"
  },
  {
    "Product": "ETFs", 
    "Smart Plan": "0.02 USD",
    "All-inclusive": "2 USD"
  },
  {
    "Product": "Options",
    "Smart Plan": "Monthly fee",
    "All-inclusive": "free of charge"
  }
]
=== END TABLE DATA ===

This is some regular text after the table."""

    print("🧪 Testing JSON Table Format Processing")
    print("=" * 50)

    # Test table block extraction
    splitter = TablePreservingTextSplitter(chunk_size=500, chunk_overlap=100)
    table_blocks = splitter._extract_table_blocks(sample_content)

    print(f"📊 Found {len(table_blocks)} table blocks:")
    for i, block in enumerate(table_blocks):
        print(
            f"  Block {i+1}: Type='{block['type']}', Length={len(block['content'])} chars"
        )
        print(f"  Content preview: {block['content'][:100]}...")

    # Test chunking with table preservation
    chunks = splitter.split_text(sample_content)

    print(f"\n📝 Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} characters):")
        print("-" * 30)
        if "=== TABLE DATA (JSON) ===" in chunk:
            print("🎯 TABLE CHUNK DETECTED")
            # Try to parse the JSON content
            try:
                # Extract the JSON array part (after metadata)
                import re

                # Find the JSON array pattern (starts with [ and ends with ])
                array_match = re.search(r"\[.*?\]", chunk, re.DOTALL)

                if array_match:
                    array_content = array_match.group(0)
                    parsed_data = json.loads(array_content)
                    print(f"✅ Successfully parsed {len(parsed_data)} table rows")
                    print(
                        f"   First row keys: {list(parsed_data[0].keys()) if parsed_data else 'No data'}"
                    )
                    print(
                        f"   Sample data: {parsed_data[0] if parsed_data else 'No data'}"
                    )
                else:
                    print("⚠️ Could not find JSON array in table chunk")
            except Exception as e:
                print(f"❌ JSON parsing failed: {e}")

        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)

    # Verify table detection
    if any("=== TABLE DATA (JSON) ===" in chunk for chunk in chunks):
        print("\n✅ JSON table format detected successfully!")
    else:
        print("\n❌ JSON table format not found in chunks")

    return True


if __name__ == "__main__":
    try:
        test_json_table_format()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
