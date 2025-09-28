#!/usr/bin/env python3
"""
Focused test to debug the exact content stored in document chunks.
This will help identify if JSON is being embedded or if raw text is being preserved.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_document_content_debugging():
    """Test what content actually gets stored in document chunks."""

    print("🔍 DEBUGGING DOCUMENT CONTENT STORAGE")
    print("=" * 60)

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

        # Create a mock LLM that should trigger vision processing
        class MockVisionLLM:
            def __init__(self):
                self.model_name = "gpt-4o"  # This should trigger vision processing

        mock_llm = MockVisionLLM()

        print(
            f"\n🔍 Testing table processing with mock vision LLM: {mock_llm.model_name}"
        )

        # Process the document
        processed_documents, table_data = extract_documents_with_table_processing(
            file_content, file_path, llm=mock_llm
        )

        print(f"\n📊 PROCESSING RESULTS:")
        print(f"  Total documents: {len(processed_documents)}")
        print(f"  Table data keys: {list(table_data.keys()) if table_data else 'None'}")

        if table_data and table_data.get("tables"):
            print(f"  Tables found: {len(table_data['tables'])}")
            for i, table in enumerate(table_data["tables"]):
                print(
                    f"    Table {i+1}: {table.get('title', 'No title')} (Page {table.get('page')})"
                )

        # Now examine the actual document content
        print(f"\n🔍 EXAMINING DOCUMENT CONTENT:")

        json_embedded_count = 0
        raw_text_count = 0

        for i, doc in enumerate(processed_documents):
            content = doc.page_content
            metadata = doc.metadata

            print(f"\n--- Document {i+1} ---")
            print(f"Page: {metadata.get('page', 'unknown')}")
            print(
                f"Has processed tables: {metadata.get('has_processed_tables', False)}"
            )
            print(f"Processing method: {metadata.get('processing_method', 'none')}")
            print(f"Content length: {len(content)} chars")

            # Check if this document contains JSON table data
            if "=== STRUCTURED TABLE DATA ===" in content:
                json_embedded_count += 1
                print("✅ Contains JSON table data")

                # Extract the JSON portion to verify it's valid
                start_marker = "=== STRUCTURED TABLE DATA ==="
                end_marker = "=== END STRUCTURED TABLE DATA ==="

                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker)

                if start_idx >= 0 and end_idx > start_idx:
                    json_start = start_idx + len(start_marker)
                    json_content = content[json_start:end_idx].strip()

                    print(f"📊 JSON sample (first 300 chars):")
                    print(
                        json_content[:300] + "..."
                        if len(json_content) > 300
                        else json_content
                    )

                    # Try to parse the JSON
                    try:
                        import json

                        parsed = json.loads(json_content)
                        print(
                            f"✅ JSON is valid - Table: {parsed.get('title', 'No title')}"
                        )
                        print(f"   Headers: {len(parsed.get('headers', []))} columns")
                        print(f"   Rows: {len(parsed.get('rows', []))} data rows")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed: {e}")

            else:
                # Check if this looks like raw table text
                if any(
                    indicator in content.lower()
                    for indicator in [
                        "per trade",
                        "contract",
                        "commission",
                        "margin rate",
                        "eur/usd",
                        "minimum per",
                        "expiration",
                        "exchange-traded",
                    ]
                ):
                    raw_text_count += 1
                    print("⚠️  Contains raw table text (no JSON)")
                    print(f"📄 Sample content (first 300 chars):")
                    print(content[:300] + "..." if len(content) > 300 else content)
                else:
                    print("📄 Regular document content")
                    if len(content) > 0:
                        print(f"📄 Sample (first 150 chars): {content[:150]}...")

        print(f"\n📈 FINAL ANALYSIS:")
        print(f"  Documents with JSON embedding: {json_embedded_count}")
        print(f"  Documents with raw table text: {raw_text_count}")
        print(
            f"  Total table-related documents: {json_embedded_count + raw_text_count}"
        )

        if json_embedded_count > 0:
            print("✅ SUCCESS: JSON table embedding is working!")
        elif raw_text_count > 0:
            print("❌ PROBLEM: Only raw text found, JSON embedding failed")
        else:
            print("⚠️  No table-related content found in documents")

        # Check if the issue might be that we're getting the wrong documents during retrieval
        print(f"\n🔍 CHECKING RETRIEVAL SIMULATION:")

        # Simulate what would happen during vector search
        table_related_docs = [
            doc
            for doc in processed_documents
            if any(
                indicator in doc.page_content.lower()
                for indicator in [
                    "per trade",
                    "contract",
                    "commission",
                    "margin rate",
                    "eur/usd",
                    "minimum per",
                    "expiration",
                    "exchange-traded",
                    "structured table data",
                ]
            )
        ]

        print(
            f"Documents that would be retrieved for table queries: {len(table_related_docs)}"
        )

        for i, doc in enumerate(table_related_docs[:3]):  # Show first 3
            has_json = "=== STRUCTURED TABLE DATA ===" in doc.page_content
            print(f"  Doc {i+1}: Page {doc.metadata.get('page')}, JSON: {has_json}")

            if not has_json:
                print(f"    ❌ This doc would show raw text to user")
                print(f"    📄 Content preview: {doc.page_content[:200]}...")

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_document_content_debugging()
