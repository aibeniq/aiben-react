#!/usr/bin/env python3
"""
Test script to validate that JSON table chunks are never split.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.smart_chunking import TablePreservingTextSplitter


def test_json_table_atomicity():
    """Test that JSON table blocks are never split across chunks"""

    print("🧪 Testing JSON Table Atomicity")
    print("=" * 50)

    # Create a long document with JSON table that might be tempting to split
    large_json_table = (
        """
=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "Large Fee Schedule",
    "page": 1,
    "summary": "Comprehensive trading fees for different instruments",
    "context": "Fee information for various trading options",
    "dimensions": "50 rows × 3 columns"
  }
}

[
"""
        + ",\n".join(
            [
                f'  {{"Product": "Item{i}", "Smart Plan": "0.{i:02d} USD", "All-inclusive": "{i} USD"}}'
                for i in range(1, 51)
            ]
        )
        + """
]
=== END TABLE DATA ==="""
    )

    sample_content = f"""This is some regular text before the table.

{large_json_table}

This is some regular text after the table that should be in a separate chunk."""

    print(f"📄 Document length: {len(sample_content):,} characters")
    print(f"📊 JSON table length: {len(large_json_table):,} characters")

    # Test with small chunk size to force splitting
    small_chunk_size = 500  # Much smaller than the table

    splitter = TablePreservingTextSplitter(
        chunk_size=small_chunk_size, chunk_overlap=100
    )

    chunks = splitter.split_text(sample_content)

    print(f"\n📝 Created {len(chunks)} chunks with chunk_size={small_chunk_size}")

    # Analyze each chunk
    json_table_chunks = []
    partial_json_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} characters):")
        print("-" * 30)

        if "=== TABLE DATA (JSON) ===" in chunk and "=== END TABLE DATA ===" in chunk:
            print("🎯 COMPLETE JSON TABLE CHUNK ✅")
            json_table_chunks.append(i + 1)
        elif "=== TABLE DATA (JSON) ===" in chunk or "=== END TABLE DATA ===" in chunk:
            print("❌ PARTIAL JSON TABLE CHUNK - THIS IS BAD!")
            partial_json_chunks.append(i + 1)
        elif '"Product"' in chunk or '"Smart Plan"' in chunk:
            print("❌ JSON TABLE DATA WITHOUT MARKERS - THIS IS BAD!")
            partial_json_chunks.append(i + 1)
        else:
            print("📄 Regular text chunk")

        # Show preview
        preview = chunk[:200].replace("\n", "\\n")
        print(f"Preview: {preview}...")

    # Validate results
    print(f"\n📊 Analysis Results:")
    print(f"   Complete JSON table chunks: {len(json_table_chunks)}")
    print(f"   Partial/broken JSON chunks: {len(partial_json_chunks)}")

    if len(json_table_chunks) == 1 and len(partial_json_chunks) == 0:
        print("✅ SUCCESS: JSON table remained atomic!")
        return True
    else:
        print("❌ FAILURE: JSON table was split or corrupted!")
        if partial_json_chunks:
            print(f"   Broken chunks: {partial_json_chunks}")
        return False


def test_multiple_json_tables():
    """Test multiple JSON tables in same document"""

    print("\n\n🧪 Testing Multiple JSON Tables")
    print("=" * 50)

    content_with_multiple_tables = """Introduction text here.

=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "Table 1",
    "page": 1,
    "dimensions": "3 rows × 2 columns"
  }
}
[
  {"Column1": "A1", "Column2": "B1"},
  {"Column1": "A2", "Column2": "B2"},
  {"Column1": "A3", "Column2": "B3"}
]
=== END TABLE DATA ===

Some text between tables.

=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "Table 2", 
    "page": 2,
    "dimensions": "2 rows × 2 columns"
  }
}
[
  {"Name": "Alice", "Age": 30},
  {"Name": "Bob", "Age": 25}
]
=== END TABLE DATA ===

Conclusion text here."""

    splitter = TablePreservingTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_text(content_with_multiple_tables)

    print(f"📝 Created {len(chunks)} chunks")

    complete_tables = 0
    broken_tables = 0

    for i, chunk in enumerate(chunks):
        if "=== TABLE DATA (JSON) ===" in chunk:
            if "=== END TABLE DATA ===" in chunk:
                complete_tables += 1
                print(f"✅ Chunk {i+1}: Complete table")
            else:
                broken_tables += 1
                print(f"❌ Chunk {i+1}: Broken table (missing end marker)")

    print(f"\n📊 Multi-table Results:")
    print(f"   Complete tables: {complete_tables}")
    print(f"   Broken tables: {broken_tables}")

    success = complete_tables == 2 and broken_tables == 0
    print(f"   Status: {'✅ SUCCESS' if success else '❌ FAILURE'}")

    return success


if __name__ == "__main__":
    try:
        test1_success = test_json_table_atomicity()
        test2_success = test_multiple_json_tables()

        print(f"\n🎉 Final Results:")
        print(f"   Single table atomicity: {'✅ PASS' if test1_success else '❌ FAIL'}")
        print(
            f"   Multiple table atomicity: {'✅ PASS' if test2_success else '❌ FAIL'}"
        )

        if test1_success and test2_success:
            print("🏆 ALL TESTS PASSED - JSON tables remain atomic!")
        else:
            print("💥 SOME TESTS FAILED - JSON tables are being split!")

    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
