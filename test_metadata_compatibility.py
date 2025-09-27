#!/usr/bin/env python3
"""Test the fixed metadata handling for Chroma compatibility"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


def test_metadata_compatibility():
    """Test that our documents have Chroma-compatible metadata"""
    print("=== Chroma Metadata Compatibility Test ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Test the table-aware processing with our fixes
    print(f"\n🔍 Testing table-aware processing with Chroma-compatible metadata")

    try:
        from app.services.table_aware_processing import TableAwareProcessor

        processor = TableAwareProcessor()
        documents = processor.create_table_aware_documents(pdf_bytes, "test.pdf")

        print(f"   ✅ Created {len(documents)} documents")

        # Check metadata types in first few documents
        print(f"\n📊 Metadata Type Analysis:")
        for i, doc in enumerate(documents[:5]):
            metadata = doc.metadata
            print(f"\n   Document {i+1} ({metadata.get('content_type', 'unknown')}):")

            # Check each metadata value type
            for key, value in metadata.items():
                value_type = type(value).__name__
                chroma_compatible = value_type in [
                    "str",
                    "int",
                    "float",
                    "bool",
                    "NoneType",
                ]
                status = "✅" if chroma_compatible else "❌"
                print(f"      {key}: {value_type} {status}")

                if key == "headers" and isinstance(value, str):
                    print(f"         Value: '{value}'")

        # Test filter_complex_metadata function
        print(f"\n🔍 Testing filter_complex_metadata function")
        try:
            from langchain_community.vectorstores.utils import filter_complex_metadata

            filtered_docs = filter_complex_metadata(documents[:3])
            print(f"   ✅ Filtered {len(filtered_docs)} documents successfully")

            # Check if any metadata was changed
            original_doc = documents[0]
            filtered_doc = filtered_docs[0]

            print(f"   Original metadata keys: {list(original_doc.metadata.keys())}")
            print(f"   Filtered metadata keys: {list(filtered_doc.metadata.keys())}")

            if "headers" in filtered_doc.metadata:
                print(f"   Headers value: '{filtered_doc.metadata['headers']}'")

        except ImportError as e:
            print(f"   ❌ Could not import filter_complex_metadata: {e}")
        except Exception as e:
            print(f"   ❌ Error testing filter_complex_metadata: {e}")

    except Exception as e:
        print(f"❌ Error in metadata compatibility test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_metadata_compatibility()
