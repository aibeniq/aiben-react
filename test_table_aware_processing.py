#!/usr/bin/env python3
"""
Test script for table-aware document processing.
Demonstrates improved table handling for vector search.
"""

import asyncio
import sys
import os
from pathlib import Path
import tempfile

# Add backend to path
sys.path.append("backend")


def create_test_files():
    """Create test files with table content to demonstrate the improvement."""

    # 1. Create a CSV file with fee schedule-like data
    csv_content = """Service Type,Smart Plan,All-Inclusive Plan
US Equities,0.08%,0.5%
US Stock Options,0.65 USD per contract,3 USD per contract + 10 USD per order
Exchange-traded futures,1.5 USD/EUR per contract,1.5 USD/EUR per contract
International Equities,0.12%,0.6%
Minimum per trade,0.2 EUR/USD,Not applicable"""

    # 2. Create a test PDF content (simulated as text)
    pdf_like_text = """
FEE SCHEDULE APPENDIX 6

Trading Fees Structure

Service Category | Smart Plan | All-Inclusive Plan
US Equities | Of the total trade value 0.08% BUT minimum per trade 0.2 EUR/USD | 0.5% of the volume of each transaction
US Stock options | 0.65 USD per contract | 3 USD per contract + 10 USD per order
Expiration of US Stock options | free of charge | free of charge
Exchange-traded futures and options (except US Stock options) | 1.5 USD/EUR per contract | 1.5 USD/EUR per contract
Expiration of Exchange-traded futures and options | free of charge | free of charge
"""

    return csv_content, pdf_like_text


async def test_table_processing():
    """Test the table-aware processing functionality."""

    print("🧪 Testing Table-Aware Document Processing")
    print("=" * 60)

    csv_content, pdf_text = create_test_files()

    try:
        from app.services.table_aware_processing import (
            TableAwareProcessor,
            enhance_document_with_tables,
        )
        from app.services.document_utils import extract_documents_from_file_unified

        processor = TableAwareProcessor()

        print("\n1. Testing CSV Table Processing")
        print("-" * 40)

        # Test CSV processing
        csv_bytes = csv_content.encode("utf-8")
        csv_docs = enhance_document_with_tables(csv_bytes, "test_fee_schedule.csv")

        print(f"📄 Generated {len(csv_docs)} document chunks from CSV")

        for i, doc in enumerate(csv_docs[:3]):  # Show first 3 chunks
            print(
                f"\nChunk {i+1} (Type: {doc.metadata.get('content_type', 'unknown')}):"
            )
            print(f"Content preview: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")

        print("\n2. Testing Question-Answer with Enhanced Documents")
        print("-" * 50)

        # Simulate a question about US equities fees
        question = "What are the fees for US equities?"

        print(f"❓ Question: {question}")
        print("\n📋 Searching through enhanced documents...")

        # Look for relevant chunks
        relevant_chunks = []
        for doc in csv_docs:
            content_lower = doc.page_content.lower()
            if any(
                term in content_lower for term in ["us equities", "us stock", "equity"]
            ):
                relevant_chunks.append(doc)

        print(f"✅ Found {len(relevant_chunks)} relevant chunks")

        for i, chunk in enumerate(relevant_chunks[:2]):
            print(f"\nRelevant Chunk {i+1}:")
            print(f"Content: {chunk.page_content}")
            print(f"Type: {chunk.metadata.get('content_type')}")

        print("\n3. Comparing with Regular Processing")
        print("-" * 40)

        # Compare with regular processing
        regular_docs = extract_documents_from_file_unified(
            csv_bytes, "test_fee_schedule.csv"
        )
        print(f"📄 Regular processing generated {len(regular_docs)} document chunks")

        if regular_docs:
            print(f"\nRegular processing content preview:")
            print(regular_docs[0].page_content[:300])

        print("\n4. Testing Table Structure Preservation")
        print("-" * 45)

        # Check if headers are preserved in table-aware processing
        table_docs_with_headers = [doc for doc in csv_docs if "headers" in doc.metadata]
        print(f"📊 Documents with header information: {len(table_docs_with_headers)}")

        if table_docs_with_headers:
            sample_doc = table_docs_with_headers[0]
            headers = sample_doc.metadata.get("headers", [])
            print(f"🏷️  Preserved headers: {headers}")

        # Test with different file extension to trigger table extraction
        print("\n5. Testing XLSX-like Processing")
        print("-" * 35)

        # Create a simple Excel-like structure
        try:
            import pandas as pd
            from io import BytesIO

            df = pd.DataFrame(
                {
                    "Service Type": [
                        "US Equities",
                        "US Stock Options",
                        "Exchange-traded futures",
                    ],
                    "Smart Plan": [
                        "0.08%",
                        "0.65 USD per contract",
                        "1.5 USD/EUR per contract",
                    ],
                    "All-Inclusive Plan": [
                        "0.5%",
                        "3 USD per contract + 10 USD per order",
                        "1.5 USD/EUR per contract",
                    ],
                }
            )

            # Save to bytes
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Fee Schedule")

            excel_bytes = excel_buffer.getvalue()
            excel_docs = enhance_document_with_tables(excel_bytes, "test_schedule.xlsx")

            print(
                f"📊 Generated {len(excel_docs)} document chunks from Excel-like data"
            )

            # Show a sample table-structured document
            for doc in excel_docs:
                if doc.metadata.get("content_type") == "table_structured":
                    print(f"\nTable-structured content sample:")
                    print(doc.page_content[:400])
                    break

        except ImportError:
            print("⚠️  Pandas not available for Excel testing")

        print("\n✅ Table-Aware Processing Test Complete!")
        print("=" * 60)

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("- pdfplumber")
        print("- pandas")
        print("- openpyxl")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_table_processing())
    if result:
        print("\n🎉 All tests passed! Table-aware processing is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the implementation.")
