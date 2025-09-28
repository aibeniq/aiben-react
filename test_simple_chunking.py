"""
Simple test to validate table preservation during chunking
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.smart_chunking import TablePreservingTextSplitter


def test_table_preservation():
    """Test that table markers are preserved during chunking"""

    # Create test content with table markers
    test_content = """
This is some regular content before the table.

<TABLE_START>
{
    "table_number": 1,
    "columns": ["Fee Type", "Amount", "Description"],
    "rows": [
        ["Consultation", "$150", "Initial consultation fee"],
        ["Follow-up", "$100", "Subsequent visit fee"],
        ["Emergency", "$300", "After-hours emergency fee"]
    ]
}
<TABLE_END>

This is content between tables.

<TABLE_START>
{
    "table_number": 2,
    "columns": ["Service", "Duration", "Cost"],
    "rows": [
        ["Diagnostic", "30 min", "$200"],
        ["Treatment", "60 min", "$350"]
    ]
}
<TABLE_END>

This is content after the tables.
"""

    # Initialize the splitter
    splitter = TablePreservingTextSplitter(
        chunk_size=200, chunk_overlap=50  # Small chunks to force splitting
    )

    # Split the content
    chunks = splitter.split_text(test_content)

    print("=== TABLE PRESERVATION TEST ===")
    print(f"Original content length: {len(test_content)}")
    print(f"Number of chunks created: {len(chunks)}")
    print()

    # Check each chunk
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(f"Length: {len(chunk)}")

        # Check for broken table markers
        if "<TABLE_START>" in chunk and "<TABLE_END>" not in chunk:
            print("❌ BROKEN: Contains TABLE_START without TABLE_END")
        elif "<TABLE_END>" in chunk and "<TABLE_START>" not in chunk:
            print("❌ BROKEN: Contains TABLE_END without TABLE_START")
        elif "<TABLE_START>" in chunk and "<TABLE_END>" in chunk:
            print("✅ COMPLETE: Contains complete table")
        else:
            print("ℹ️ REGULAR: No table content")

        # Show first 100 chars for preview
        preview = chunk.strip()[:100].replace("\n", " ")
        if len(chunk.strip()) > 100:
            preview += "..."
        print(f"Preview: {preview}")
        print()

    # Final validation
    broken_tables = 0
    complete_tables = 0

    for chunk in chunks:
        if ("<TABLE_START>" in chunk) != ("<TABLE_END>" in chunk):
            broken_tables += 1
        elif "<TABLE_START>" in chunk and "<TABLE_END>" in chunk:
            complete_tables += 1

    print("=== RESULTS ===")
    print(f"Complete tables: {complete_tables}")
    print(f"Broken tables: {broken_tables}")

    if broken_tables == 0:
        print("✅ SUCCESS: All table structures preserved!")
    else:
        print(f"❌ FAILURE: {broken_tables} table(s) were broken during chunking")

    return broken_tables == 0


if __name__ == "__main__":
    success = test_table_preservation()
    sys.exit(0 if success else 1)
