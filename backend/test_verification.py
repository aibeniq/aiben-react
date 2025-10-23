"""
Simple test runner to verify our testing implementation works.
This can be run independently without complex dependencies.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def test_document_utils_basic():
    """Test basic document utils functionality."""
    try:
        from app.services.document_utils import extract_text_from_file_unified

        # Test text file
        result = extract_text_from_file_unified(b"Hello World", "test.txt")
        assert result == "Hello World", f"Expected 'Hello World', got '{result}'"

        # Test unknown extension
        result = extract_text_from_file_unified(b"content", "file.unknown")
        assert result == "content", f"Expected 'content', got '{result}'"

        print("✓ Document utils basic tests passed")
        return True
    except Exception as e:
        print(f"✗ Document utils test failed: {e}")
        return False


def test_fixtures_import():
    """Test that our fixtures can be imported."""
    try:
        from app.tests.fixtures.documents import sample_csv_bytes, empty_file_bytes

        # Just test that the fixtures are defined (don't call them)
        assert callable(sample_csv_bytes)
        assert callable(empty_file_bytes)

        print("✓ Fixtures import tests passed")
        return True
    except Exception as e:
        print(f"✗ Fixtures import test failed: {e}")
        return False


def main():
    """Run all basic tests."""
    print("Running basic test verification...")

    tests = [
        test_document_utils_basic,
        test_fixtures_import,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! The testing framework is working.")
        return 0
    else:
        print("❌ Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
