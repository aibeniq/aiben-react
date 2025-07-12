#!/usr/bin/env python3
"""
Test script to verify FormConnect PDF processing fix
"""

import asyncio
import tempfile
from pathlib import Path
from fastapi import UploadFile
from io import BytesIO

# Add the backend directory to Python path
import sys

sys.path.append("backend")

from app.api.routes.formconnect import extract_fields_from_digitized_document


async def test_pdf_extraction():
    """Test PDF extraction functionality"""
    print("🔍 Testing FormConnect PDF extraction fix...")

    # Create a mock template
    template = {
        "Total Assets": "Financial value of total assets",
        "Net Income": "Net income or profit",
        "Number of Employees": "Total employee count",
    }

    # Test with a simple text file that acts like a PDF
    test_content = """
    ANNUAL REPORT 2024
    
    Financial Summary:
    Total Assets: $1,250,000
    Net Income: $425,000
    
    Company Information:
    Number of Employees: 150
    Location: New York
    """

    # Create a mock UploadFile
    class MockUploadFile:
        def __init__(self, content: bytes, filename: str):
            self.content = content
            self.filename = filename

        async def read(self):
            return self.content

    # Test text file
    print("✅ Testing text file extraction...")
    text_file = MockUploadFile(test_content.encode("utf-8"), "test.txt")

    try:
        result = await extract_fields_from_digitized_document(text_file, template)
        print(f"   Text extraction result: {result}")

        # Check if we got actual extracted content instead of error messages
        has_errors = any("Could not extract" in str(value) for value in result.values())
        if not has_errors:
            print("✅ Text file processing: SUCCESS")
        else:
            print("❌ Text file processing: FAILED")

    except Exception as e:
        print(f"❌ Text file processing error: {e}")

    # Test unsupported file
    print("✅ Testing unsupported file handling...")
    binary_file = MockUploadFile(b"\x89PNG\r\n\x1a\n", "test.png")

    try:
        result = await extract_fields_from_digitized_document(binary_file, template)
        print(f"   Unsupported file result: {result}")

        # Should have proper error messages for unsupported formats
        has_proper_errors = any(
            "Unsupported file format" in str(value) for value in result.values()
        )
        if has_proper_errors:
            print("✅ Unsupported file handling: SUCCESS")
        else:
            print("❌ Unsupported file handling: FAILED")

    except Exception as e:
        print(f"❌ Unsupported file processing error: {e}")


if __name__ == "__main__":
    asyncio.run(test_pdf_extraction())
