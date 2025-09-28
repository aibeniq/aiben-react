#!/usr/bin/env python3
"""
Test script to verify that the JSON table wrapper marker fix works correctly.
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_json_wrapper_markers():
    """Test that JSON tables are created with proper wrapper markers"""

    print("🧪 Testing JSON Wrapper Marker Fix")
    print("=" * 60)

    # Simulate the table content creation process
    table_content = {
        "table_metadata": {
            "title": "Sample Fee Schedule",
            "page": 6,
            "summary": "Fee structure for various services",
            "context": "Details on fees",
            "dimensions": "3 rows × 2 columns",
        },
        "table_data": [
            {"Description": "Service A", "Fee": "100 EUR"},
            {"Description": "Service B", "Fee": "0.25%"},
            {"Description": "Service C", "Fee": "Free"},
        ],
    }

    # Test the NEW corrected format (should have wrapper markers)
    table_block = f"\n=== TABLE DATA (JSON) ===\n"

    # Add metadata header
    metadata_header = {"_table_metadata": table_content["table_metadata"]}
    table_block += json.dumps(metadata_header, indent=2, ensure_ascii=False) + "\n\n"

    # Add table data as JSON array
    table_block += json.dumps(table_content["table_data"], indent=2, ensure_ascii=False)
    table_block += "\n=== END TABLE DATA ===\n"

    print("📄 Generated table block:")
    print("-" * 40)
    print(table_block)
    print("-" * 40)

    # Test with chunking system
    from app.services.smart_chunking import TablePreservingTextSplitter

    # Create document with the table
    document_content = f"""
This is a document about fee schedules.

{table_block}

Additional information follows.
"""

    print(
        f"\n🔍 Testing chunking with document length: {len(document_content):,} chars"
    )
    print(f"📊 Table block length: {len(table_block):,} chars")

    # Test with small chunk size to force splitting if markers don't work
    splitter = TablePreservingTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_text(document_content)

    print(f"\n📋 Created {len(chunks)} chunks")

    # Analyze results
    table_chunks = []
    partial_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"\n📄 Chunk {i+1} ({len(chunk)} chars):")

        if "=== TABLE DATA (JSON) ===" in chunk and "=== END TABLE DATA ===" in chunk:
            print("   ✅ Complete JSON table block")
            table_chunks.append(i + 1)

            # Verify JSON is parseable
            try:
                # Extract JSON data
                import re

                json_match = re.search(r"\[(.*?)\]", chunk, re.DOTALL)
                if json_match:
                    json_data = json.loads("[" + json_match.group(1) + "]")
                    print(f"   📊 Successfully parsed {len(json_data)} rows")

                    # Check for required fields
                    if all("Description" in row and "Fee" in row for row in json_data):
                        print("   ✅ All rows have required fields")
                    else:
                        print("   ❌ Missing required fields in some rows")

            except Exception as e:
                print(f"   ❌ JSON parsing failed: {e}")

        elif any(
            marker in chunk for marker in ["Description", "Fee", "Service A", "0.25%"]
        ):
            print("   ❌ Contains table fragments without proper structure!")
            partial_chunks.append(i + 1)
        else:
            print("   📝 Regular content")

    # Final assessment
    print(f"\n🏆 RESULTS:")
    print(f"   Complete table chunks: {table_chunks}")
    print(f"   Partial/broken chunks: {partial_chunks}")

    if table_chunks and not partial_chunks:
        print("   ✅ SUCCESS: JSON tables remain atomic with proper wrapper markers!")
        return True
    else:
        print("   ❌ FAILURE: Tables are still being split incorrectly!")
        return False


def test_old_vs_new_format():
    """Compare old broken format vs new fixed format"""

    print(f"\n\n🔄 Testing Old vs New Format")
    print("=" * 60)

    # OLD (broken) format - raw JSON without markers
    old_format = json.dumps(
        [
            {"Description": "Service A", "Fee": "100 EUR"},
            {"Description": "Service B", "Fee": "0.25%"},
        ],
        indent=2,
    )

    print("❌ OLD FORMAT (without wrapper markers):")
    print(old_format[:100] + "..." if len(old_format) > 100 else old_format)

    # NEW (fixed) format - with proper markers
    new_format = f"""=== TABLE DATA (JSON) ===
{{
  "_table_metadata": {{
    "title": "Fee Schedule",
    "page": 6,
    "summary": "Service fees",
    "context": "Fee details",
    "dimensions": "2 rows × 2 columns"
  }}
}}

[
  {{"Description": "Service A", "Fee": "100 EUR"}},
  {{"Description": "Service B", "Fee": "0.25%"}}
]
=== END TABLE DATA ==="""

    print(f"\n✅ NEW FORMAT (with wrapper markers):")
    print(new_format[:150] + "..." if len(new_format) > 150 else new_format)

    from app.services.smart_chunking import TablePreservingTextSplitter

    splitter = TablePreservingTextSplitter(chunk_size=200, chunk_overlap=50)

    # Test old format
    old_chunks = splitter.split_text(f"Content before.\n{old_format}\nContent after.")
    old_split = any(
        "Service A" in chunk and "Service B" not in chunk for chunk in old_chunks
    )

    # Test new format
    new_chunks = splitter.split_text(f"Content before.\n{new_format}\nContent after.")
    new_preserved = any(
        "=== TABLE DATA (JSON) ===" in chunk
        and "Service A" in chunk
        and "Service B" in chunk
        for chunk in new_chunks
    )

    print(f"\n📊 Old format chunks: {len(old_chunks)}, Split table: {old_split}")
    print(f"📊 New format chunks: {len(new_chunks)}, Preserved table: {new_preserved}")

    if not old_split and new_preserved:
        print("✅ Format fix is working correctly!")
    else:
        print("❌ Format fix needs more work")

    return not old_split and new_preserved


if __name__ == "__main__":
    try:
        success1 = test_json_wrapper_markers()
        success2 = test_old_vs_new_format()

        if success1 and success2:
            print(f"\n🎉 ALL TESTS PASSED - Wrapper marker fix is working!")
        else:
            print(f"\n💥 Some tests failed - more debugging needed")

    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
