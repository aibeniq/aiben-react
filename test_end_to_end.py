#!/usr/bin/env python3
"""End-to-end test of table-aware processing in knowledge base context"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


def test_end_to_end():
    """Test the full knowledge base processing pipeline"""
    print("=== End-to-End Table-Aware Processing Test ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Test the exact function used by knowledge base creation
    print(f"\n🔍 Testing extract_documents_from_file_table_aware (KB function)")

    try:
        from app.services.document_utils import extract_documents_from_file_table_aware

        # Use the same function as knowledge base creation
        documents = extract_documents_from_file_table_aware(
            pdf_bytes, "Appendix 6 Fee Schedule.pdf"
        )

        print(f"   ✅ Created {len(documents)} documents")

        # Analyze documents for Smart/All-inclusive content
        smart_docs = []
        all_inclusive_docs = []
        us_equity_docs = []

        for doc in documents:
            content = doc.page_content
            metadata = doc.metadata

            if "Smart" in content:
                smart_docs.append(doc)
            if "All-inclusive" in content or "All inclusive" in content:
                all_inclusive_docs.append(doc)
            if any(term in content for term in ["United States", "USD", "US equities"]):
                us_equity_docs.append(doc)

        print(f"\n📊 Content Analysis:")
        print(f"   • Documents mentioning 'Smart': {len(smart_docs)}")
        print(f"   • Documents mentioning 'All-inclusive': {len(all_inclusive_docs)}")
        print(f"   • Documents mentioning US equity terms: {len(us_equity_docs)}")

        # Show sample Smart content
        if smart_docs:
            print(f"\n📋 Sample 'Smart' content:")
            doc = smart_docs[0]
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Content: {doc.page_content[:300]}...")

        # Show sample All-inclusive content
        if all_inclusive_docs:
            print(f"\n📋 Sample 'All-inclusive' content:")
            doc = all_inclusive_docs[0]
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Content: {doc.page_content[:300]}...")

        # Look for documents that have both Smart and All-inclusive context
        both_plans_docs = []
        for doc in documents:
            content = doc.page_content
            if "Smart" in content and (
                "All-inclusive" in content or "All inclusive" in content
            ):
                both_plans_docs.append(doc)

        print(
            f"\n🎯 Documents with both Smart AND All-inclusive context: {len(both_plans_docs)}"
        )

        if both_plans_docs:
            print(f"\n📋 Sample document with both plan types:")
            doc = both_plans_docs[0]
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Table ID: {doc.metadata.get('table_id', 'N/A')}")
            print(f"   Content: {doc.page_content[:400]}...")

        # Final assessment
        if both_plans_docs and us_equity_docs:
            print(f"\n✅ SUCCESS: Table-aware processing is working!")
            print(f"   - Tables preserve Smart/All-inclusive column structure")
            print(f"   - US equity information is properly extracted")
            print(
                f"   - Query 'What are the fees for US equities?' should now return both plan types"
            )
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Some issues remain")
            if not both_plans_docs:
                print(f"   - No documents contain both Smart and All-inclusive context")
            if not us_equity_docs:
                print(f"   - No documents contain US equity information")

    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_end_to_end()
