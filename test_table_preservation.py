#!/usr/bin/env python3
"""
Test script to validate that table structures are preserved during chunking.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_table_preservation():
    """Test that table markers are preserved during document splitting."""

    print("🧪 Testing Table Preservation During Chunking\n")

    try:
        from app.services.smart_chunking import TablePreservingTextSplitter
        from langchain_core.documents import Document

        # Create a test document with structured table data
        test_content = """
This is some regular text before the table.

=== STRUCTURED TABLE DATA ===
{
  "table_id": "table_1_0",
  "page": 1,
  "title": "Fee Schedule - Trading Fees",
  "headers": ["Service", "Fee Amount", "Currency"],
  "rows": [
    ["Options trading", "1.5 USD/EUR per contract", "USD/EUR"],
    ["Futures expiration", "1.5 USD/EUR per contract", "USD/EUR"],
    ["NANOS options", "0.01 USD per contract", "USD"],
    ["Margin rate (per day)", "0.049315%", "Percentage"]
  ],
  "summary": "Fee schedule for various trading options and markets.",
  "context": "Details on fees for trading in different markets and options.",
  "metadata": {
    "row_count": 4,
    "column_count": 3,
    "table_type": "fee_schedule",
    "processing_method": "vision_enhanced",
    "source_filename": "Appendix 6 Fee Schedule.pdf",
    "extraction_timestamp": ""
  }
}
=== END STRUCTURED TABLE DATA ===

=== SEARCHABLE SUMMARY ===
Table: Fee Schedule - Trading Fees
Columns: Service, Fee Amount, Currency
Service: Options trading, Futures expiration, NANOS options
Fee Amount: 1.5 USD/EUR per contract, 0.01 USD per contract, 0.049315%
Currency: USD/EUR, USD, Percentage
Dimensions: 4 rows × 3 columns
=== END SEARCHABLE SUMMARY ===

This is some text after the table that should be in a separate chunk.
More text here to make it longer and test the chunking behavior properly.
Even more text to ensure we have enough content for meaningful chunk testing.
""".strip()

        # Create a document
        doc = Document(
            page_content=test_content,
            metadata={
                "source": "test_document.pdf",
                "page": 1,
                "has_processed_tables": True,
            },
        )

        # Test with TablePreservingTextSplitter
        print("📊 Testing TablePreservingTextSplitter...")
        table_splitter = TablePreservingTextSplitter(chunk_size=800, chunk_overlap=100)
        table_chunks = table_splitter.split_documents([doc])

        print(f"   Created {len(table_chunks)} chunks")

        # Analyze chunks
        table_intact = False
        broken_table = False

        for i, chunk in enumerate(table_chunks):
            content = chunk.page_content
            print(f"\n--- Chunk {i+1} ({len(content)} chars) ---")

            # Check for complete table structures
            if (
                "=== STRUCTURED TABLE DATA ===" in content
                and "=== END STRUCTURED TABLE DATA ===" in content
            ):
                print("✅ Contains COMPLETE structured table data")
                table_intact = True

                # Verify JSON is complete
                if (
                    '"table_id"' in content
                    and '"rows"' in content
                    and '"metadata"' in content
                ):
                    print("✅ JSON structure appears complete")
                else:
                    print("⚠️  JSON structure may be incomplete")

            elif "=== STRUCTURED TABLE DATA ===" in content:
                print("❌ Contains PARTIAL structured table data (BROKEN)")
                broken_table = True

            elif "table_id" in content or '"rows"' in content:
                print("❌ Contains FRAGMENTED table JSON (BROKEN)")
                broken_table = True

            else:
                print("📝 Regular text content")

            # Show preview
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"Preview: {preview}")

        # Test results
        print(f"\n🎯 Test Results:")
        print(f"   • Table intact in chunk: {'✅' if table_intact else '❌'}")
        print(f"   • Broken table detected: {'❌' if broken_table else '✅'}")

        if table_intact and not broken_table:
            print("\n🎉 SUCCESS: Table preservation is working correctly!")
            print("   ✅ Structured table data kept intact during chunking")
            return True
        else:
            print("\n❌ FAILURE: Table preservation needs improvement")
            if broken_table:
                print("   ❌ Table was split across chunks")
            if not table_intact:
                print("   ❌ No complete table structure found")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_comparison():
    """Compare old vs new splitter behavior."""

    print("\n🔄 Comparison Test: Old vs New Splitter\n")

    try:
        from app.services.smart_chunking import (
            StructureAwareTextSplitter,
            TablePreservingTextSplitter,
        )
        from langchain_core.documents import Document

        # Simple test content with table
        test_content = """Regular text before.

=== STRUCTURED TABLE DATA ===
{"table_id": "test", "rows": [["Fee", "Amount"], ["Trading", "$1.50"]]}
=== END STRUCTURED TABLE DATA ===

Regular text after."""

        doc = Document(page_content=test_content, metadata={"source": "test"})

        # Test old splitter
        print("📋 StructureAwareTextSplitter:")
        old_splitter = StructureAwareTextSplitter(chunk_size=100, chunk_overlap=20)
        old_chunks = old_splitter.split_documents([doc])

        for i, chunk in enumerate(old_chunks):
            has_partial = (
                "=== STRUCTURED TABLE DATA ===" in chunk.page_content
                and "=== END STRUCTURED TABLE DATA ===" not in chunk.page_content
            )
            status = "❌ BROKEN" if has_partial else "✅ OK"
            print(f"   Chunk {i+1}: {len(chunk.page_content)} chars {status}")

        # Test new splitter
        print(f"\n📊 TablePreservingTextSplitter:")
        new_splitter = TablePreservingTextSplitter(chunk_size=100, chunk_overlap=20)
        new_chunks = new_splitter.split_documents([doc])

        for i, chunk in enumerate(new_chunks):
            has_complete = (
                "=== STRUCTURED TABLE DATA ===" in chunk.page_content
                and "=== END STRUCTURED TABLE DATA ===" in chunk.page_content
            )
            status = (
                "✅ INTACT"
                if has_complete
                else ("📝 Regular" if "===" not in chunk.page_content else "❌ BROKEN")
            )
            print(f"   Chunk {i+1}: {len(chunk.page_content)} chars {status}")

        return True

    except Exception as e:
        print(f"❌ Comparison test error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Table Preservation Chunking Test\n")

    success1 = test_table_preservation()
    success2 = test_comparison()

    if success1 and success2:
        print("\n✅ All tests passed! Table preservation is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
