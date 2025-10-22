"""
Test script to verify the fast table detection optimization.

This script demonstrates the performance improvement of using vanilla PyMuPDF
for table detection before invoking the heavier PyMuPDF4LLM processor.
"""

import sys
import os
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.pdf_utils import (
    has_tables_fast,
    load_pdf_with_pypdf,
    extract_pdf_with_pymupdf4llm,
    PYMUPDF4LLM_AVAILABLE,
)


def test_fast_table_detection(pdf_path: str):
    """Test the fast table detection function."""
    print(f"\n{'='*70}")
    print(f"Testing Fast Table Detection")
    print(f"{'='*70}")
    print(f"PDF: {pdf_path}\n")

    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return

    # Test 1: Fast table detection
    print("1. Running fast table detection (vanilla PyMuPDF)...")
    start_time = time.time()
    has_tables, table_count = has_tables_fast(pdf_path)
    fast_detection_time = time.time() - start_time

    print(f"   ✓ Completed in {fast_detection_time:.3f} seconds")
    print(
        f"   Result: {'Tables found' if has_tables else 'No tables'} ({table_count} table(s))\n"
    )

    # Test 2: Load with enhanced parsing (will use fast check internally)
    if PYMUPDF4LLM_AVAILABLE:
        print("2. Loading PDF with enhanced parsing (includes fast check)...")
        start_time = time.time()
        documents = load_pdf_with_pypdf(
            pdf_path, os.path.basename(pdf_path), use_enhanced_parsing=True
        )
        enhanced_time = time.time() - start_time

        print(f"   ✓ Completed in {enhanced_time:.3f} seconds")
        print(f"   Extracted {len(documents)} document(s)")
        if documents:
            print(
                f"   Extraction method: {documents[0].metadata.get('extraction_method', 'unknown')}\n"
            )
    else:
        print("2. PyMuPDF4LLM not available - skipping enhanced parsing test\n")

    # Test 3: Load without enhanced parsing (baseline)
    print("3. Loading PDF with basic pypdf (baseline)...")
    start_time = time.time()
    documents_basic = load_pdf_with_pypdf(
        pdf_path, os.path.basename(pdf_path), use_enhanced_parsing=False
    )
    basic_time = time.time() - start_time

    print(f"   ✓ Completed in {basic_time:.3f} seconds")
    print(f"   Extracted {len(documents_basic)} document(s)\n")

    # Summary
    print(f"{'='*70}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*70}")
    print(f"Fast table detection:  {fast_detection_time:.3f}s")
    print(f"Basic pypdf:           {basic_time:.3f}s")
    if PYMUPDF4LLM_AVAILABLE:
        print(f"With optimization:     {enhanced_time:.3f}s")
        if has_tables:
            print(f"\n✓ Tables detected - PyMuPDF4LLM was used for better extraction")
        else:
            print(f"\n✓ No tables - PyMuPDF4LLM was skipped, saving processing time!")
    print(f"{'='*70}\n")


def main():
    """Main test function."""
    print("\n" + "=" * 70)
    print("Fast Table Detection Optimization Test")
    print("=" * 70)
    print("\nThis test demonstrates the performance improvement from checking")
    print("for tables before invoking heavy PyMuPDF4LLM processing.\n")

    # Check if a PDF path was provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_fast_table_detection(pdf_path)
    else:
        print("Usage: python test_fast_table_detection.py <path_to_pdf>")
        print("\nExample:")
        print("  python test_fast_table_detection.py sample.pdf")
        print("\nTo test with multiple PDFs:")
        print("  python test_fast_table_detection.py document_with_tables.pdf")
        print("  python test_fast_table_detection.py document_without_tables.pdf")


if __name__ == "__main__":
    main()
