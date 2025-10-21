"""
Test PyMuPDF4LLM integration for PDF table parsing.
"""

import pytest
from pathlib import Path
from app.services.pdf_utils import (
    load_pdf_with_pypdf,
    extract_pdf_with_pymupdf4llm,
    PYMUPDF4LLM_AVAILABLE,
)


def test_pymupdf4llm_availability():
    """Test if PyMuPDF4LLM is available."""
    assert PYMUPDF4LLM_AVAILABLE, "PyMuPDF4LLM should be available for testing"


def test_enhanced_pdf_parsing():
    """Test enhanced PDF parsing with table detection."""
    # Use a test PDF with tables
    test_pdf = Path("test_files/sample_table.pdf")
    if test_pdf.exists():
        documents = extract_pdf_with_pymupdf4llm(str(test_pdf), "sample_table.pdf")

        # Check for table markers in content
        has_tables = any("|" in doc.page_content for doc in documents)
        assert has_tables, "Should detect tables in PDF content"


def test_fallback_behavior():
    """Test fallback to pypdf when PyMuPDF4LLM fails."""
    test_pdf = Path("test_files/sample.pdf")
    if test_pdf.exists():
        # Should work regardless of PyMuPDF4LLM availability
        documents = load_pdf_with_pypdf(
            str(test_pdf), "sample.pdf", use_enhanced_parsing=True
        )
        assert len(documents) > 0
        assert all(doc.page_content.strip() for doc in documents)


def test_extract_text_from_pdf_bytes_enhanced():
    """Test enhanced text extraction from PDF bytes."""
    from app.services.pdf_utils import extract_text_from_pdf_bytes

    # Create a simple test PDF content (this would normally be actual PDF bytes)
    # For this test, we'll use a mock or skip if no test file exists
    test_pdf = Path("test_files/sample.pdf")
    if test_pdf.exists():
        with open(test_pdf, "rb") as f:
            pdf_bytes = f.read()

        # Test enhanced parsing
        text_enhanced = extract_text_from_pdf_bytes(
            pdf_bytes, "sample.pdf", use_enhanced_parsing=True
        )
        assert isinstance(text_enhanced, str)
        assert len(text_enhanced.strip()) > 0

        # Test basic parsing
        text_basic = extract_text_from_pdf_bytes(
            pdf_bytes, "sample.pdf", use_enhanced_parsing=False
        )
        assert isinstance(text_basic, str)
        assert len(text_basic.strip()) > 0


def test_document_utils_integration():
    """Test integration with document_utils functions."""
    from app.services.document_utils import (
        extract_documents_from_file_unified,
        extract_text_from_file_unified,
    )

    # Test with a sample PDF if available
    test_pdf = Path("test_files/sample.pdf")
    if test_pdf.exists():
        with open(test_pdf, "rb") as f:
            pdf_bytes = f.read()

        # Test document extraction with enhanced parsing
        documents = extract_documents_from_file_unified(
            pdf_bytes, "sample.pdf", use_enhanced_pdf_parsing=True
        )
        assert len(documents) > 0
        assert all(doc.page_content.strip() for doc in documents)

        # Test text extraction with enhanced parsing
        text = extract_text_from_file_unified(
            pdf_bytes, "sample.pdf", use_enhanced_pdf_parsing=True
        )
        assert isinstance(text, str)
        assert len(text.strip()) > 0
