#!/usr/bin/env python3
"""
Debug script to test the actual table processing pipeline with the user's file.
This will help identify why the JSON embedding isn't working as expected.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import asyncio
from pathlib import Path


async def debug_actual_file_processing():
    """Debug the actual file processing with the user's PDF."""

    print("🧪 DEBUGGING ACTUAL FILE PROCESSING")
    print("=" * 60)

    # Load the actual file
    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"📄 Loading file: {file_path}")

    try:
        # Read the file
        with open(file_path, "rb") as f:
            file_content = f.read()

        print(f"✅ File loaded: {len(file_content)} bytes")

        # Import the table processing function
        from app.services.document_utils import extract_documents_with_table_processing
        from app.services.llms import get_default_llm
        from app.core.config import settings

        # We need to create a mock LLM for this test since we don't have full session context
        # Let's check what happens without LLM first
        print("\n🔍 STEP 1: Testing table processing without LLM")

        try:
            processed_documents, table_data = extract_documents_with_table_processing(
                file_content, file_path, llm=None
            )

            print(f"📊 Processed documents: {len(processed_documents)}")
            print(
                f"📋 Table data keys: {list(table_data.keys()) if table_data else 'No table data'}"
            )

            if table_data and table_data.get("tables"):
                print(f"✅ Found {len(table_data['tables'])} tables")
                for i, table in enumerate(table_data["tables"]):
                    print(
                        f"  Table {i+1}: {table.get('title', 'No title')} on page {table.get('page', 'unknown')}"
                    )
            else:
                print("❌ No tables found in table_data")

            # Check document content for JSON embedding
            print("\n🔍 STEP 2: Checking document content for JSON embedding")

            json_embedded_docs = 0
            for i, doc in enumerate(processed_documents):
                content = doc.page_content
                if "=== STRUCTURED TABLE DATA ===" in content:
                    json_embedded_docs += 1
                    print(f"✅ Document {i+1} contains JSON table data")

                    # Extract a sample of the JSON
                    start_idx = content.find("=== STRUCTURED TABLE DATA ===")
                    end_idx = content.find("=== END STRUCTURED TABLE DATA ===")
                    if start_idx >= 0 and end_idx > start_idx:
                        json_sample = content[start_idx : end_idx + 35]
                        print(f"📊 JSON sample (first 500 chars):")
                        print(
                            json_sample[:500] + "..."
                            if len(json_sample) > 500
                            else json_sample
                        )
                else:
                    print(f"❌ Document {i+1} does not contain JSON table data")
                    print(f"📄 Content sample: {content[:200]}...")

            print(f"\n📈 SUMMARY:")
            print(f"  Total documents: {len(processed_documents)}")
            print(f"  Documents with JSON tables: {json_embedded_docs}")
            print(
                f"  Table data found: {'Yes' if table_data and table_data.get('tables') else 'No'}"
            )

            if json_embedded_docs == 0 and table_data and table_data.get("tables"):
                print("\n🚨 PROBLEM IDENTIFIED:")
                print("  Tables were detected but JSON embedding failed!")
                print(
                    "  This explains why users see raw text instead of structured data."
                )
            elif json_embedded_docs > 0:
                print("\n✅ JSON EMBEDDING WORKING:")
                print(
                    "  Tables are being properly embedded as JSON in document content."
                )
                print("  The issue might be elsewhere in the pipeline.")

        except Exception as e:
            print(f"❌ Error during document processing: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error loading file: {e}")
        import traceback

        traceback.print_exc()


def test_with_mock_llm():
    """Test with a mock LLM to see vision processing behavior."""

    print("\n" + "=" * 60)
    print("🧪 TESTING WITH MOCK LLM (Vision Processing)")

    class MockLLM:
        def __init__(self):
            self.model_name = "gpt-4o"  # Vision-enabled model name

    try:
        # Load file
        file_path = "test_files/Appendix 6 Fee Schedule.pdf"
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Import required modules
        from app.services.document_utils import extract_documents_with_table_processing

        mock_llm = MockLLM()

        print(f"🔍 Testing with mock LLM: {mock_llm.model_name}")

        processed_documents, table_data = extract_documents_with_table_processing(
            file_content, file_path, llm=mock_llm
        )

        print(f"📊 Results with mock LLM:")
        print(f"  Processed documents: {len(processed_documents)}")
        print(f"  Table data: {list(table_data.keys()) if table_data else 'None'}")

        if table_data and table_data.get("tables"):
            print(f"  Tables found: {len(table_data['tables'])}")

        # Check for JSON embedding
        json_docs = sum(
            1
            for doc in processed_documents
            if "=== STRUCTURED TABLE DATA ===" in doc.page_content
        )
        print(f"  Documents with JSON: {json_docs}")

        if json_docs > 0:
            print("✅ Vision processing + JSON embedding is working!")
        else:
            print("❌ Vision processing failed or JSON embedding not working")

    except Exception as e:
        print(f"❌ Mock LLM test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the async function
    asyncio.run(debug_actual_file_processing())

    # Run mock LLM test
    test_with_mock_llm()
