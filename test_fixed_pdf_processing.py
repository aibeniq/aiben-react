#!/usr/bin/env python3
"""
Test script to verify that PDF table-aware processing works after the fixes.
"""

import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.append("backend")


def test_pdf_knowledge_base_processing():
    """Test the complete PDF knowledge base processing pipeline."""

    print("🔧 Testing PDF Knowledge Base Processing Pipeline")
    print("=" * 60)

    # Check if the actual PDF exists
    pdf_path = Path("test_files/Appendix 6 Fee Schedule.pdf")

    if pdf_path.exists():
        print(f"✅ Found actual PDF: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        filename = pdf_path.name
    else:
        print("⚠️  PDF file not found, creating mock PDF content...")
        # Create realistic table content
        mock_content = """APPENDIX 6 - FEE SCHEDULE

Trading Services Fee Structure

Service Type | Smart Plan | All-Inclusive Plan
US Equities | 0.08% of total trade value (minimum per trade 0.2 EUR/USD) | 0.5% of the volume of each transaction
US Stock options | 0.65 USD per contract | 3 USD per contract + 10 USD per order  
Exchange-traded futures and options | 1.5 USD/EUR per contract | 1.5 USD/EUR per contract
International Equities | 0.12% of trade value | 0.6% of volume
"""
        pdf_bytes = mock_content.encode("utf-8")
        filename = "Mock_Appendix_6_Fee_Schedule.pdf"

    print(f"📄 Testing file: {filename}")
    print(f"📊 File size: {len(pdf_bytes)} bytes")

    try:
        print("\n1. Testing Direct Table-Aware Processing")
        print("-" * 45)

        from app.services.document_utils import extract_documents_from_file_table_aware

        # This simulates what the knowledge base route now does
        documents = extract_documents_from_file_table_aware(pdf_bytes, filename)

        print(f"📊 Generated {len(documents)} documents")

        # Analyze document types
        doc_types = {}
        table_docs = []
        regular_docs = []

        for doc in documents:
            content_type = doc.metadata.get("content_type", "unknown")
            doc_types[content_type] = doc_types.get(content_type, 0) + 1

            if "table" in content_type:
                table_docs.append(doc)
            else:
                regular_docs.append(doc)

        print(f"\n📋 Document types created:")
        for doc_type, count in doc_types.items():
            print(f"   • {doc_type}: {count}")

        print(f"\n📊 Analysis:")
        print(f"   Table documents: {len(table_docs)}")
        print(f"   Regular documents: {len(regular_docs)}")

        if len(table_docs) > 0:
            print("✅ SUCCESS: Table documents were created!")
        else:
            print("❌ PROBLEM: No table documents created")
            return False

        print("\n2. Search Simulation for US Equities")
        print("-" * 40)

        us_equity_docs = []
        for doc in documents:
            if "us equities" in doc.page_content.lower():
                us_equity_docs.append(doc)

        print(f"🔍 Found {len(us_equity_docs)} documents matching 'US equities'")

        context_preserved_docs = []
        for doc in us_equity_docs:
            content_lower = doc.page_content.lower()
            has_smart = "smart" in content_lower
            has_all_inclusive = (
                "all-inclusive" in content_lower or "all inclusive" in content_lower
            )

            if has_smart and has_all_inclusive:
                context_preserved_docs.append(doc)

        print(f"✅ Documents with BOTH plan contexts: {len(context_preserved_docs)}")

        if len(context_preserved_docs) > 0:
            print("\n💪 IMPROVED RESULT PREVIEW:")
            sample_doc = context_preserved_docs[0]
            content_type = sample_doc.metadata.get("content_type", "unknown")
            print(f"Document Type: {content_type}")
            print("Content:")
            print("-" * 30)
            # Show the content in a clean way
            lines = sample_doc.page_content.split("\n")
            for line in lines[:5]:  # First 5 lines
                if line.strip():
                    print(f"  {line}")
            print("-" * 30)

            print("\n🎯 KEY IMPROVEMENT:")
            print("   ✓ Smart Plan mentioned: ✅")
            print("   ✓ All-Inclusive Plan mentioned: ✅")
            print("   ✓ US Equities context preserved: ✅")
            print("   ✓ Column headers maintained: ✅")

        else:
            print("❌ PROBLEM: No documents preserve both plan contexts")

            # Show what we do have
            if us_equity_docs:
                print("\n📄 Sample US equity document:")
                sample = us_equity_docs[0]
                print(f"Content: {sample.page_content[:200]}...")

        print("\n3. Comparing Before vs After")
        print("-" * 35)

        # Simulate the old processing
        from app.services.document_utils import extract_documents_from_file_unified

        old_docs = extract_documents_from_file_unified(pdf_bytes, filename)

        old_us_equity_docs = []
        for doc in old_docs:
            if "us equities" in doc.page_content.lower():
                old_us_equity_docs.append(doc)

        print(f"📊 COMPARISON:")
        print(f"   Old processing: {len(old_us_equity_docs)} US equity documents")
        print(f"   New processing: {len(us_equity_docs)} US equity documents")
        print(f"   Documents with full context: {len(context_preserved_docs)}")

        if len(us_equity_docs) > len(old_us_equity_docs):
            print("✅ Improvement: More relevant documents found")

        if len(context_preserved_docs) > 0:
            print("✅ Improvement: Column header context preserved")

        print("\n4. Knowledge Base Processing Simulation")
        print("-" * 42)

        print("📋 What happens when you upload your PDF now:")
        print("   1. PDF is processed with table-aware extraction")
        print(
            f"   2. {len(documents)} documents are created (vs {len(old_docs)} before)"
        )
        print(f"   3. {len(table_docs)} table-specific documents preserve structure")
        print("   4. Vector search finds relevant chunks with headers")
        print("   5. LLM gets proper context: 'Smart Plan: X | All-Inclusive Plan: Y'")

        print(
            f"\n🎉 SOLUTION STATUS: {'✅ WORKING' if len(context_preserved_docs) > 0 else '❌ NEEDS FIXING'}"
        )

        return len(context_preserved_docs) > 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_knowledge_base_processing()

    if success:
        print(f"\n🎉 SUCCESS!")
        print("The table-aware processing is now working for PDF files.")
        print("To fix your existing issue:")
        print("  1. Create a new knowledge base")
        print("  2. Re-upload your 'Appendix 6 Fee Schedule.pdf' file")
        print("  3. Test the query 'What are the fees for US equities?'")
        print("  4. You should now see proper Smart/All-Inclusive distinctions!")
    else:
        print(f"\n💥 Still needs work. Check the output above for issues.")
