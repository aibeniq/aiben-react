"""
Test with realistic production table markers
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.smart_chunking import TablePreservingTextSplitter


def test_production_markers():
    """Test with actual production table markers"""

    # Create test content with production markers
    test_content = """
This document contains fee schedule information.

=== STRUCTURED TABLE DATA ===
{
    "table_number": 1,
    "title": "Consultation Fees",
    "columns": ["Service Type", "Base Fee", "Additional Notes"],
    "rows": [
        ["Initial Consultation", "$150.00", "Includes comprehensive assessment"],
        ["Follow-up Visit", "$100.00", "Standard follow-up within 30 days"],
        ["Emergency Consultation", "$300.00", "After-hours or urgent care"]
    ],
    "source_page": 1,
    "extraction_confidence": 0.95
}
=== END STRUCTURED TABLE DATA ===

The table above shows the basic consultation structure. Additional fees may apply for specialized services.

=== STRUCTURED TABLE DATA ===
{
    "table_number": 2,
    "title": "Diagnostic Procedures",
    "columns": ["Procedure", "Duration", "Cost", "Prerequisites"],
    "rows": [
        ["Basic Screening", "15 min", "$50", "None"],
        ["Comprehensive Exam", "45 min", "$200", "Consultation required"],
        ["Specialized Testing", "60 min", "$350", "Referral needed"]
    ],
    "source_page": 2,
    "extraction_confidence": 0.88
}
=== END STRUCTURED TABLE DATA ===

These procedures are available by appointment only. Please note that insurance coverage varies.

=== RAW TABLE CONTENT ===
Fee Schedule - Emergency Services
┌─────────────────┬──────────────┬─────────────────────┐
│ Service         │ Base Rate    │ After Hours Rate    │
├─────────────────┼──────────────┼─────────────────────┤
│ Urgent Care     │ $200         │ $300                │
│ Critical Care   │ $500         │ $750                │
│ Life Support    │ $1000        │ $1500               │
└─────────────────┴──────────────┴─────────────────────┘
=== END RAW TABLE CONTENT ===

Emergency services require immediate payment or valid insurance authorization.
"""

    # Initialize the splitter with small chunk size to test splitting
    splitter = TablePreservingTextSplitter(
        chunk_size=300, chunk_overlap=50  # Force multiple chunks
    )

    # Split the content
    chunks = splitter.split_text(test_content)

    print("=== PRODUCTION TABLE PRESERVATION TEST ===")
    print(f"Original content length: {len(test_content)}")
    print(f"Number of chunks created: {len(chunks)}")
    print()

    # Analyze each chunk
    table_markers = [
        ("=== STRUCTURED TABLE DATA ===", "=== END STRUCTURED TABLE DATA ==="),
        ("=== RAW TABLE CONTENT ===", "=== END RAW TABLE CONTENT ==="),
        ("=== SEARCHABLE SUMMARY ===", "=== END SEARCHABLE SUMMARY ==="),
    ]

    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(f"Length: {len(chunk)}")

        # Check for each type of table marker
        has_complete_table = False
        has_broken_table = False

        for start_marker, end_marker in table_markers:
            has_start = start_marker in chunk
            has_end = end_marker in chunk

            if has_start and has_end:
                has_complete_table = True
                print(f"✅ COMPLETE: Contains complete table ({start_marker[:20]}...)")
            elif has_start or has_end:
                has_broken_table = True
                if has_start:
                    print(f"❌ BROKEN: Contains {start_marker[:20]}... without end")
                if has_end:
                    print(f"❌ BROKEN: Contains {end_marker[:20]}... without start")

        if not has_complete_table and not has_broken_table:
            print("ℹ️ REGULAR: No table content")

        # Show preview
        preview = chunk.strip()[:150].replace("\n", " ")
        if len(chunk.strip()) > 150:
            preview += "..."
        print(f"Preview: {preview}")
        print()

    # Final validation
    broken_count = sum(
        1
        for chunk in chunks
        for start_marker, end_marker in table_markers
        if (start_marker in chunk) != (end_marker in chunk)
    )

    complete_count = sum(
        1
        for chunk in chunks
        for start_marker, end_marker in table_markers
        if start_marker in chunk and end_marker in chunk
    )

    print("=== FINAL RESULTS ===")
    print(f"Complete table blocks: {complete_count}")
    print(f"Broken table blocks: {broken_count}")

    if broken_count == 0:
        print("✅ SUCCESS: All production table structures preserved!")
        return True
    else:
        print(f"❌ FAILURE: {broken_count} table block(s) were broken")
        return False


if __name__ == "__main__":
    success = test_production_markers()
    sys.exit(0 if success else 1)
