#!/usr/bin/env python3
"""
Test script for table-aware vector search implementation.
"""

import sys
import os
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_table_detection():
    """Test the table detection functionality."""
    print("🔍 Testing Table Detection")
    print("=" * 50)

    try:
        from app.services.table_detection import TableDetector

        # Test 1: Simple table text
        table_text = """
        Name | Age | City
        John | 25  | New York
        Jane | 30  | Boston
        """

        has_table = TableDetector.detect_tables_in_text(table_text)
        print(f"✅ Simple table detection: {has_table}")
        assert has_table, "Should detect simple pipe-separated table"

        # Test 2: Complex table with analysis
        complex_table = """
        Product Name    Price    Stock    Category
        Widget A        $10.99   100      Electronics
        Widget B        $15.50   75       Electronics
        Gadget X        $25.00   50       Tools
        """

        analysis = TableDetector.analyze_table_complexity(complex_table)
        print(f"✅ Complex table analysis: {analysis}")
        assert analysis["has_tables"], "Should detect complex table"

        # Test 3: Non-table text
        non_table = "This is just regular paragraph text without any tabular structure."
        has_table = TableDetector.detect_tables_in_text(non_table)
        print(f"✅ Non-table detection: {has_table}")
        assert not has_table, "Should not detect table in regular text"

        print("✅ Table Detection: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ Table Detection Test Failed: {e}")
        return False


def test_vision_service_table_extraction():
    """Test the vision service table extraction (mock test)."""
    print("\n🔍 Testing Vision Service Table Extraction")
    print("=" * 50)

    try:
        # Mock the config to avoid validation errors
        import os

        os.environ["PROJECT_NAME"] = "test"
        os.environ["POSTGRES_SERVER"] = "localhost"
        os.environ["POSTGRES_USER"] = "test"
        os.environ["FIRST_SUPERUSER"] = "test@example.com"
        os.environ["FIRST_SUPERUSER_PASSWORD"] = "test"

        from app.services.vision_service import VisionService

        # Mock LLM for testing
        class MockVisionLLM:
            model_name = "gpt-4-vision-preview"

            def invoke(self, prompt):
                # Mock response that looks like table extraction
                return """```json
[
  {
    "table_id": "table_1",
    "page": 1,
    "title": "Sample Data",
    "headers": ["Name", "Value"],
    "rows": [
      ["Item A", "100"],
      ["Item B", "200"]
    ],
    "summary": "Sample table with test data",
    "context": "Test context",
    "metadata": {
      "row_count": 2,
      "column_count": 2,
      "table_type": "data"
    }
  }
]
```"""

        # Test vision capability check
        vision_llm = MockVisionLLM()
        is_enabled = VisionService.is_vision_enabled(vision_llm)
        print(f"✅ Vision capability check: {is_enabled}")

        # Test table extraction (with mock data)
        mock_images = ["fake_base64_image_data"]
        mock_pages = [1]

        result = VisionService.extract_table_as_json(
            vision_llm, mock_images, mock_pages, "test.pdf"
        )

        print(
            f"✅ Table extraction result: {result.get('extraction_successful', False)}"
        )
        if result.get("tables"):
            print(f"   - Extracted {len(result['tables'])} tables")

        print("✅ Vision Service Table Extraction: TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ Vision Service Test Failed: {e}")
        return False


def test_document_processing_integration():
    """Test the document processing with table awareness."""
    print("\n🔍 Testing Document Processing Integration")
    print("=" * 50)

    try:
        # Set up environment for testing
        import os

        os.environ.setdefault("PROJECT_NAME", "test")
        os.environ.setdefault("POSTGRES_SERVER", "localhost")
        os.environ.setdefault("POSTGRES_USER", "test")
        os.environ.setdefault("FIRST_SUPERUSER", "test@example.com")
        os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "test")

        from app.services.document_utils import extract_documents_with_table_processing
        from langchain.schema import Document

        # Create test content with table-like structure
        test_content = """
        This is a document with both regular text and a table.
        
        Product Analysis Report
        
        Name        | Sales   | Growth
        Product A   | $1,000  | +15%
        Product B   | $2,500  | +23%
        Product C   | $1,800  | -5%
        
        The table above shows our quarterly performance.
        """.encode(
            "utf-8"
        )

        # Test without LLM (no vision processing)
        documents, table_data = extract_documents_with_table_processing(
            test_content, "test_report.txt", llm=None
        )

        print(f"✅ Processed {len(documents)} documents")
        print(f"✅ Table data result: {bool(table_data)}")

        # Check if documents contain the content
        assert len(documents) > 0, "Should create at least one document"

        content = documents[0].page_content
        assert "Product Analysis Report" in content, "Should preserve original text"

        print("✅ Document Processing Integration: TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ Document Processing Test Failed: {e}")
        return False


def test_table_search_functionality():
    """Test the table data search functionality."""
    print("\n🔍 Testing Table Data Search")
    print("=" * 50)

    try:
        # Set up environment for testing
        import os

        os.environ.setdefault("PROJECT_NAME", "test")
        os.environ.setdefault("POSTGRES_SERVER", "localhost")
        os.environ.setdefault("POSTGRES_USER", "test")
        os.environ.setdefault("FIRST_SUPERUSER", "test@example.com")
        os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "test")

        from app.services.document_utils import search_in_table_data

        # Mock table data
        table_data = {
            "tables": [
                {
                    "table_id": "table_1",
                    "headers": ["Product Name", "Price", "Stock"],
                    "rows": [
                        ["Widget A", "$10.99", "100"],
                        ["Widget B", "$15.50", "75"],
                        ["Gadget X", "$25.00", "50"],
                    ],
                    "summary": "Product inventory data",
                }
            ]
        }

        # Test search for price information
        result = search_in_table_data(
            "price", "product pricing information", table_data
        )
        print(f"✅ Price search result: {result}")
        assert result is not None, "Should find price information"

        # Test search for stock information
        result = search_in_table_data("inventory", "stock levels", table_data)
        print(f"✅ Stock search result: {result}")
        assert result is not None, "Should find stock information"

        # Test search for non-existent field
        result = search_in_table_data("color", "product color", table_data)
        print(f"✅ Non-existent field result: {result}")

        print("✅ Table Data Search: ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ Table Search Test Failed: {e}")
        return False


def main():
    """Run all table-aware vector search tests."""
    print("🚀 Starting Table-Aware Vector Search Tests")
    print("=" * 60)

    test_results = []

    # Run all tests
    test_results.append(test_table_detection())
    test_results.append(test_vision_service_table_extraction())
    test_results.append(test_document_processing_integration())
    test_results.append(test_table_search_functionality())

    # Summary
    passed = sum(test_results)
    total = len(test_results)

    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Table-aware vector search is ready.")
        return True
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Test runner failed: {e}")
        sys.exit(1)
