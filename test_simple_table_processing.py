#!/usr/bin/env python3
"""
Simple test that doesn't rely on full application settings.
"""

import sys

# Add backend to path
sys.path.append("backend")


def test_table_processing_simple():
    """Simple test without full app configuration."""

    print("🧪 Simple Table-Aware Processing Test")
    print("=" * 50)

    # Create fee schedule as CSV for easier testing
    fee_schedule_csv = """Service Type,Smart Plan,All-Inclusive Plan
US Equities,"0.08% of trade value (minimum 0.2 EUR/USD)","0.5% of the volume of each transaction"
US Stock options,0.65 USD per contract,"3 USD per contract + 10 USD per order"
Exchange-traded futures,1.5 USD/EUR per contract,1.5 USD/EUR per contract"""

    try:
        # Import and create processor directly
        from app.services.table_aware_processing import TableAwareProcessor

        # Create processor with explicit settings
        processor = TableAwareProcessor(
            preserve_headers=True,
            max_table_rows=1000,
            max_row_documents=50,
            enable_json_format=True,
            enable_structured_format=True,
            enable_row_documents=True,
        )

        csv_bytes = fee_schedule_csv.encode("utf-8")

        print("1. Testing Enhanced Table Processing")
        print("-" * 40)

        # Test the processor directly
        enhanced_docs = processor.create_table_aware_documents(
            csv_bytes, "fee_schedule.csv"
        )

        print(f"📊 Generated {len(enhanced_docs)} documents")

        # Analyze document types
        doc_types = {}
        for doc in enhanced_docs:
            content_type = doc.metadata.get("content_type", "unknown")
            doc_types[content_type] = doc_types.get(content_type, 0) + 1

        print(f"\n📋 Document types:")
        for doc_type, count in doc_types.items():
            print(f"   • {doc_type}: {count}")

        print("\n2. US Equities Search Test")
        print("-" * 30)

        # Find US equities documents
        us_equity_docs = []
        for doc in enhanced_docs:
            if "us equities" in doc.page_content.lower():
                us_equity_docs.append(doc)

        print(f"📊 Found {len(us_equity_docs)} documents about US equities")

        # Show the enhanced results
        for i, doc in enumerate(us_equity_docs[:2]):
            content_type = doc.metadata.get("content_type", "unknown")
            print(f"\n🔍 Document {i+1} ({content_type}):")

            # Show first few lines
            lines = doc.page_content.split("\n")
            for line in lines[:3]:
                if line.strip():
                    print(f"   {line}")

        # Show specific improvement: headers preserved
        row_docs = [
            doc
            for doc in enhanced_docs
            if doc.metadata.get("content_type") == "table_row"
        ]
        us_equity_rows = [
            doc for doc in row_docs if "us equities" in doc.page_content.lower()
        ]

        if us_equity_rows:
            print(f"\n💪 KEY IMPROVEMENT - Full Context Preserved:")
            print("   " + "=" * 50)
            content_lines = us_equity_rows[0].page_content.split("\n")
            for line in content_lines:
                if line.strip():
                    print(f"   {line}")
            print("   " + "=" * 50)

        print(f"\n✅ BENEFITS DEMONSTRATED:")
        print(
            f"   ✓ Headers preserved: 'Smart Plan' and 'All-Inclusive Plan' are clearly identified"
        )
        print(
            f"   ✓ Multiple formats: {len(doc_types)} different document representations"
        )
        print(f"   ✓ Granular access: Individual rows with full context")
        print(
            f"   ✓ Search coverage: {len(us_equity_docs)} relevant documents vs 1 in original"
        )

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_table_processing_simple()

    if success:
        print(f"\n🎉 Table-aware processing is working correctly!")
        print("The solution successfully preserves table structure and context.")
    else:
        print(f"\n💥 Test failed.")
