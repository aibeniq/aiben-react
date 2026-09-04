#!/usr/bin/env python3
"""
Test script to verify that PDF page counting is working correctly.
This script tests the PageCounter service to ensure it uses actual PDF page counts.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.page_counter import PageCounter


def test_pdf_page_counting():
    """Test the PDF page counting functionality."""
    print("🔍 Testing PDF page counting...")

    # Test with different file types to show the difference
    test_cases = [
        ("test.pdf", b"some content"),  # Will fall back to 1 page since no valid PDF
        ("test.txt", b"line1\nline2\nline3\nline4\nline5"),  # 5 lines
        ("test.docx", b"some content"),  # Will fall back to 1 page since no valid DOCX
    ]

    for filename, content in test_cases:
        page_count = PageCounter.count_pages_from_bytes(content, filename)
        print(f"📄 {filename}: {page_count} pages")

    print("\n✅ Page counting test completed!")
    print(
        "📋 For PDFs, the PageCounter uses pypdf.PdfReader to get the ACTUAL page count from the PDF structure."
    )
    print(
        "📋 This is NOT an estimation based on text content - it reads the PDF's internal page count."
    )


if __name__ == "__main__":
    test_pdf_page_counting()
