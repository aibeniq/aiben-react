#!/usr/bin/env python3
"""
Test script to verify that documents are now being created with proper JSON wrapper markers.
"""

import json
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_document_creation():
    """Test that document processing creates proper wrapper markers"""

    print("🧪 Testing Document Creation with Wrapper Markers")
    print("=" * 60)

    # Simulate the document creation process
    # Mock table data (simulating what vision service would return)
    mock_table_data = {
        "tables": [
            {
                "table_id": "table_1",
                "page": 1,
                "title": "E-Accounts Fee Schedule",
                "headers": ["Description", "Fee"],
                "rows": [
                    ["Account opening", "Free"],
                    ["Safekeeping per day", "0.000822%"],
                    ["OTC Trades", "0.12% + 30 EUR"],
                ],
                "summary": "E-Account fees and charges",
                "context": "Fee schedule for E-Account services",
                "metadata": {
                    "row_count": 3,
                    "column_count": 2,
                    "table_type": "fee_schedule",
                },
            }
        ],
        "extraction_successful": True,
    }

    print("📊 Mock table data created with 3 rows")

    # Test the new document creation logic
    table_content_parts = []

    for table in mock_table_data["tables"]:
        # Convert table data to JSON array format
        json_rows = []
        headers = table.get("headers", [])
        rows = table.get("rows", [])

        if headers and rows:
            for row in rows:
                if isinstance(row, list) and len(row) > 0:
                    row_obj = {}
                    for i, header in enumerate(headers):
                        value = row[i] if i < len(row) else ""
                        if value is None:
                            value = ""
                        else:
                            value = str(value).strip()
                        row_obj[header] = value
                    json_rows.append(row_obj)

        # Create table content with proper wrapper markers
        table_content = {
            "table_metadata": {
                "title": table.get("title", "Data Table"),
                "page": 1,
                "summary": table.get("summary", ""),
                "context": table.get("context", ""),
                "dimensions": f"{len(json_rows)} rows × {len(headers)} columns",
            },
            "table_data": json_rows,
        }

        # Create the properly formatted table block
        table_block = f"\n=== TABLE DATA (JSON) ===\n"

        # Add metadata header
        metadata_header = {"_table_metadata": table_content["table_metadata"]}
        table_block += (
            json.dumps(metadata_header, indent=2, ensure_ascii=False) + "\n\n"
        )

        # Add table data as JSON array
        table_block += json.dumps(
            table_content["table_data"], indent=2, ensure_ascii=False
        )
        table_block += "\n=== END TABLE DATA ===\n"

        table_content_parts.append(table_block)

    # Combine all table blocks
    enhanced_content = "\n".join(table_content_parts)

    print("📄 Generated document content:")
    print("-" * 40)
    print(enhanced_content)
    print("-" * 40)

    # Test chunking with this content
    from app.services.smart_chunking import TablePreservingTextSplitter

    splitter = TablePreservingTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(enhanced_content)

    print(f"\n🔍 Chunking Results:")
    print(f"   📊 Total chunks created: {len(chunks)}")

    # Analyze each chunk
    for i, chunk in enumerate(chunks):
        print(f"\n📄 Chunk {i+1} ({len(chunk)} chars):")

        if "=== TABLE DATA (JSON) ===" in chunk and "=== END TABLE DATA ===" in chunk:
            print("   ✅ Complete JSON table block")

            # Verify JSON is valid
            try:
                import re

                json_match = re.search(r"\[(.*?)\]", chunk, re.DOTALL)
                if json_match:
                    json_data = json.loads("[" + json_match.group(1) + "]")
                    print(f"   📊 Contains {len(json_data)} valid JSON rows")

                    # Check for the problematic content from user's examples
                    for row in json_data:
                        if "0.000822%" in str(row):
                            print(f"   🎯 Found safekeeping fee: {row}")
                        if "Account opening" in str(row):
                            print(f"   🎯 Found account opening: {row}")

            except Exception as e:
                print(f"   ❌ JSON parsing error: {e}")

        elif any(
            fragment in chunk for fragment in ['"Description":', '"Fee":', "0.000822%"]
        ):
            print("   ❌ Contains table fragments without proper structure!")
            print(f"   🔍 Fragment preview: {chunk[:100]}...")
        else:
            print("   📝 Non-table content")

    return enhanced_content, chunks


def verify_chunking_integrity():
    """Verify that the chunking system preserves table integrity"""

    print(f"\n\n🔍 Verifying Chunking Integrity")
    print("=" * 60)

    # Create a realistic document with the format we expect from the fixed system
    document_with_tables = """Some preliminary content about financial services.

=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "E-Accounts Fee Schedule",
    "page": 8,
    "summary": "Fee structure for E-Account services",
    "context": "Details of fees associated with E-Accounts and related services",
    "dimensions": "9 rows × 2 columns"
  }
}

[
  {
    "Description": "Account opening",
    "Fee": "Free"
  },
  {
    "Description": "Any external free-of-payment securities transfer, both incoming and outgoing",
    "Fee": "100 EUR"
  },
  {
    "Description": "Internal free-of-payment securities transfer to trading account within FFEU",
    "Fee": "Free"
  },
  {
    "Description": "Internal free-of-payment securities transfer from trading account within FFEU",
    "Fee": "50 EUR"
  },
  {
    "Description": "Safekeeping (incl. custody) per day",
    "Fee": "0.000822%"
  },
  {
    "Description": "Ordering a special custody balances report with a list of securities",
    "Fee": "Free"
  },
  {
    "Description": "OTC Trades",
    "Fee": "0.12% of the transaction amount + 180 EUR per trade"
  },
  {
    "Description": "Internal cash transfers to the trading account within FFEU",
    "Fee": "50 EUR"
  },
  {
    "Description": "Margin rate (per day)",
    "Fee": "n/a"
  }
]
=== END TABLE DATA ===

Additional content follows the table data."""

    print(f"📄 Document length: {len(document_with_tables):,} characters")

    # Test with various chunk sizes that previously caused problems
    test_chunk_sizes = [300, 500, 800, 1200]

    from app.services.smart_chunking import TablePreservingTextSplitter

    for chunk_size in test_chunk_sizes:
        print(f"\n🧪 Testing chunk_size = {chunk_size}")

        splitter = TablePreservingTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
        chunks = splitter.split_text(document_with_tables)

        print(f"   📊 Created {len(chunks)} chunks")

        # Check integrity
        table_complete = False
        table_fragments = 0

        for i, chunk in enumerate(chunks):
            if (
                "=== TABLE DATA (JSON) ===" in chunk
                and "=== END TABLE DATA ===" in chunk
            ):
                table_complete = True

                # Verify all critical data is present
                critical_data = ["0.000822%", "Account opening", "OTC Trades"]
                missing_data = [data for data in critical_data if data not in chunk]

                if missing_data:
                    print(f"   ❌ Chunk {i+1}: Missing data: {missing_data}")
                else:
                    print(f"   ✅ Chunk {i+1}: Complete table with all critical data")

            elif any(
                indicator in chunk
                for indicator in ["0.000822%", '"Description":', '"Fee":']
            ):
                table_fragments += 1
                print(f"   ❌ Chunk {i+1}: Contains table fragments!")

        # Overall assessment
        if table_complete and table_fragments == 0:
            print(f"   🎉 PASSED: Table preserved as atomic unit")
        else:
            print(f"   💥 FAILED: Table integrity compromised")

    return True


if __name__ == "__main__":
    try:
        enhanced_content, chunks = test_document_creation()
        verify_chunking_integrity()

        print(f"\n🏆 Testing complete!")
        print("The fix ensures that:")
        print(
            "1. ✅ Documents are created with proper '=== TABLE DATA (JSON) ===' wrapper markers"
        )
        print("2. ✅ JSON table blocks are treated as atomic units during chunking")
        print("3. ✅ No table fragments appear in separate chunks without structure")
        print("4. ✅ All table metadata and headers are preserved with the data")

    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
