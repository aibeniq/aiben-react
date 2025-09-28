#!/usr/bin/env python3
"""
Test script to simulate the exact splitting scenario the user reported.
"""

import sys
import os
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_real_world_scenario():
    """Test with realistic table data similar to what user reported"""

    print("🧪 Testing Real-World Table Splitting Scenario")
    print("=" * 60)

    # Simulate the kind of JSON table that was being split
    realistic_table = """=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "E-Accounts Fee Schedule",
    "page": 8,
    "summary": "Fee structure for E-Accounts and related services",
    "context": "Details on fees for account management and transactions",
    "dimensions": "8 rows × 2 columns"
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
=== END TABLE DATA ==="""

    # Create document with table and surrounding content
    document_content = f"""
This is a document about fee schedules and account management.

{realistic_table}

Additional information about the fee structure and terms and conditions.
"""

    print(f"📄 Document length: {len(document_content):,} characters")
    print(f"📊 Table length: {len(realistic_table):,} characters")

    # Test with various chunk sizes to simulate embedding constraints
    chunk_sizes = [500, 800, 1200, 1500]

    from app.services.smart_chunking import TablePreservingTextSplitter

    for chunk_size in chunk_sizes:
        print(f"\n🔍 Testing with chunk_size = {chunk_size}")
        print("-" * 40)

        splitter = TablePreservingTextSplitter(chunk_size=chunk_size, chunk_overlap=100)

        chunks = splitter.split_text(document_content)

        print(f"   Created {len(chunks)} chunks")

        # Analyze each chunk
        table_integrity_check = True
        headers_present = True

        for i, chunk in enumerate(chunks):
            if "=== TABLE DATA (JSON) ===" in chunk:
                # This should be a complete table
                if "=== END TABLE DATA ===" not in chunk:
                    print(f"   ❌ Chunk {i+1}: Incomplete table (missing end marker)")
                    table_integrity_check = False
                else:
                    # Check if headers (metadata + column names) are present
                    if '"Description"' not in chunk or '"Fee"' not in chunk:
                        print(f"   ❌ Chunk {i+1}: Table missing column headers!")
                        headers_present = False
                    elif '"_table_metadata"' not in chunk:
                        print(f"   ❌ Chunk {i+1}: Table missing metadata!")
                        headers_present = False
                    else:
                        print(f"   ✅ Chunk {i+1}: Complete table with headers")
            elif any(
                fragment in chunk
                for fragment in ['"Description":', '"Fee":', "0.000822%"]
            ):
                print(f"   ❌ Chunk {i+1}: Contains table fragments without structure!")
                table_integrity_check = False

        # Overall result for this chunk size
        if table_integrity_check and headers_present:
            print(f"   🎉 SUCCESS: Table remained intact with headers")
        else:
            print(f"   💥 FAILURE: Table was corrupted or split")

    return True


def test_json_parsing_in_chunks():
    """Test that JSON in chunks can still be parsed"""

    print(f"\n\n🧪 Testing JSON Parseability in Chunks")
    print("=" * 60)

    sample_json_table = """=== TABLE DATA (JSON) ===
{
  "_table_metadata": {
    "title": "Simple Table",
    "page": 1,
    "dimensions": "2 rows × 2 columns"
  }
}

[
  {"Name": "Alice", "Age": 30},
  {"Name": "Bob", "Age": 25}
]
=== END TABLE DATA ==="""

    document = f"Some text.\n\n{sample_json_table}\n\nMore text."

    from app.services.smart_chunking import TablePreservingTextSplitter

    splitter = TablePreservingTextSplitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_text(document)

    print(f"📝 Created {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        if "=== TABLE DATA (JSON) ===" in chunk:
            print(f"\n🔍 Analyzing JSON chunk {i+1}:")

            # Extract JSON array part
            try:
                import re

                array_match = re.search(r"\[(.*?)\]", chunk, re.DOTALL)
                if array_match:
                    array_content = "[" + array_match.group(1) + "]"
                    parsed_data = json.loads(array_content)
                    print(f"   ✅ Successfully parsed {len(parsed_data)} rows")
                    print(f"   📊 Data: {parsed_data}")
                else:
                    print("   ❌ Could not find JSON array")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing failed: {e}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

    return True


if __name__ == "__main__":
    try:
        test_real_world_scenario()
        test_json_parsing_in_chunks()
        print(f"\n🏆 All tests completed!")

    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
