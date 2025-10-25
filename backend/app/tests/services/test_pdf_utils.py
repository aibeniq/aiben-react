"""
Unit tests for pdf_utils.py service functions.
Tests PDF processing, table detection, and text extraction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from app.services.pdf_utils import (
    has_tables_fast,
    extract_pdf_with_pymupdf4llm,
    load_pdf_with_pypdf,
    extract_text_from_pdf_bytes,
)


class TestPDFUtils:
    """Test suite for PDF utility functions."""

    @patch("app.services.pdf_utils.fitz")
    def test_has_tables_fast_with_tables(self, mock_fitz):
        """Test fast table detection when tables are present."""
        # Mock PyMuPDF document and page with tables
        mock_page = Mock()
        mock_tables = Mock()
        mock_tables.tables = [Mock(), Mock()]  # Two tables
        mock_page.find_tables.return_value = mock_tables

        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz.open.return_value = mock_doc

        result = has_tables_fast("/path/to/test.pdf")

        assert result == (True, 2)
        mock_fitz.open.assert_called_once_with("/path/to/test.pdf")

    @patch("app.services.pdf_utils.fitz")
    def test_has_tables_fast_no_tables(self, mock_fitz):
        """Test fast table detection when no tables are present."""
        # Mock PyMuPDF document and page without tables
        mock_page = Mock()
        mock_tables = Mock()
        mock_tables.tables = []  # No tables
        mock_page.find_tables.return_value = mock_tables

        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz.open.return_value = mock_doc

        result = has_tables_fast("/path/to/test.pdf")

        assert result == (False, 0)

    @patch("app.services.pdf_utils.fitz")
    def test_has_tables_fast_multiple_pages(self, mock_fitz):
        """Test fast table detection across multiple pages."""
        # Mock multiple pages with tables on different pages
        mock_page1 = Mock()
        mock_tables1 = Mock()
        mock_tables1.tables = [Mock()]  # One table on page 1
        mock_page1.find_tables.return_value = mock_tables1

        mock_page2 = Mock()
        mock_tables2 = Mock()
        mock_tables2.tables = [Mock(), Mock()]  # Two tables on page 2
        mock_page2.find_tables.return_value = mock_tables2

        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=2)
        mock_doc.__getitem__ = Mock(side_effect=[mock_page1, mock_page2])
        mock_fitz.open.return_value = mock_doc

        result = has_tables_fast("/path/to/test.pdf")

        assert result == (True, 3)  # Total of 3 tables

    @patch("app.services.pdf_utils.fitz")
    def test_has_tables_fast_error(self, mock_fitz):
        """Test fast table detection error handling."""
        mock_fitz.open.side_effect = Exception("PDF open error")

        result = has_tables_fast("/path/to/corrupted.pdf")

        # Should assume tables are present for safety
        assert result == (True, 0)

    @patch("app.services.pdf_utils.PYMUPDF4LLM_AVAILABLE", True)
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("pymupdf4llm.to_markdown")
    def test_extract_pdf_with_pymupdf4llm_with_tables(
        self, mock_to_markdown, mock_has_tables
    ):
        """Test PDF extraction with PyMuPDF4LLM when tables are detected."""
        mock_has_tables.return_value = (True, 2)  # Has tables

        # Mock the markdown output with page separators
        mock_to_markdown.return_value = "Page 1 content with table\n---\nPage 2 content"

        result = extract_pdf_with_pymupdf4llm("/path/to/test.pdf", "test.pdf")

        assert len(result) == 2
        assert result[0].page_content == "Page 1 content with table"
        assert result[1].page_content == "Page 2 content"

    @patch("app.services.pdf_utils.PYMUPDF4LLM_AVAILABLE", True)
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("app.services.pdf_utils.load_pdf_with_pypdf")
    def test_extract_pdf_with_pymupdf4llm_no_tables(
        self, mock_load_pypdf, mock_has_tables
    ):
        """Test PDF extraction fallback when no tables detected."""
        mock_has_tables.return_value = (False, 0)  # No tables

        mock_documents = [Mock(page_content="Simple text content")]
        mock_load_pypdf.return_value = mock_documents

        result = extract_pdf_with_pymupdf4llm("/path/to/test.pdf", "test.pdf")

        mock_load_pypdf.assert_called_once_with(
            "/path/to/test.pdf", "test.pdf", parsing_mode="basic"
        )
        assert result == mock_documents

    @patch("app.services.pdf_utils.PYMUPDF4LLM_AVAILABLE", True)
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("pymupdf4llm.to_markdown")
    def test_extract_pdf_with_pymupdf4llm_skip_check(
        self, mock_to_markdown, mock_has_tables
    ):
        """Test PDF extraction when table check is skipped."""
        mock_to_markdown.return_value = "Content"

        result = extract_pdf_with_pymupdf4llm(
            "/path/to/test.pdf", "test.pdf", skip_table_check=True
        )

        # Should not call has_tables_fast when skip_table_check=True
        mock_has_tables.assert_not_called()
        assert len(result) == 1
        assert result[0].page_content == "Content"

    @patch("app.services.pdf_utils.PYMUPDF4LLM_AVAILABLE", False)
    def test_extract_pdf_with_pymupdf4llm_not_available(self):
        """Test PDF extraction when PyMuPDF4LLM is not available."""
        with pytest.raises(ImportError, match="PyMuPDF4LLM is not available"):
            extract_pdf_with_pymupdf4llm("/path/to/test.pdf", "test.pdf")

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("app.services.pdf_utils.pypdf")
    def test_load_pdf_with_pypdf_success(self, mock_pypdf, mock_file):
        """Test PDF loading with pypdf."""
        # Mock pypdf PdfReader
        mock_reader = Mock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader.pages = [mock_page1, mock_page2]
        mock_pypdf.PdfReader.return_value = mock_reader

        result = load_pdf_with_pypdf("/path/to/test.pdf", "test.pdf")

        assert len(result) == 2
        assert result[0].page_content == "Page 1 content"
        assert result[1].page_content == "Page 2 content"
        assert result[0].metadata["source"] == "test.pdf"
        assert result[0].metadata["page"] == 1

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("app.services.pdf_utils.pypdf")
    def test_load_pdf_with_pypdf_empty_pages(self, mock_pypdf, mock_file):
        """Test PDF loading when pages have no extractable text."""
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]
        mock_pypdf.PdfReader.return_value = mock_reader

        result = load_pdf_with_pypdf("/path/to/empty.pdf", "empty.pdf")

        # Should return empty list when pages have no content
        assert len(result) == 0

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake pdf content")
    @patch("app.services.pdf_utils.pypdf")
    def test_load_pdf_with_pypdf_error(self, mock_pypdf, mock_file):
        """Test PDF loading error handling."""
        from fastapi import HTTPException

        mock_pypdf.PdfReader.side_effect = Exception("PDF read error")

        with pytest.raises(HTTPException, match="Error reading PDF: PDF read error"):
            load_pdf_with_pypdf("/path/to/corrupted.pdf", "corrupted.pdf")

    @patch("os.unlink")
    @patch("tempfile.NamedTemporaryFile")
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("app.services.pdf_utils.load_pdf_with_pypdf")
    def test_extract_text_from_pdf_bytes_success(
        self, mock_load_pypdf, mock_has_tables, mock_tempfile, mock_unlink
    ):
        """Test text extraction from PDF bytes."""
        # Mock tempfile as context manager
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp_file.__exit__.return_value = None
        mock_temp_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value = mock_temp_file

        # Mock has_tables_fast to return no tables (so it uses load_pdf_with_pypdf)
        mock_has_tables.return_value = (False, 0)

        # Mock load_pdf_with_pypdf to return documents
        from app.services.pdf_utils import Document

        mock_docs = [
            Document(page_content="Page 1 text", metadata={"page": 1}),
            Document(page_content="Page 2 text", metadata={"page": 2}),
        ]
        mock_load_pypdf.return_value = mock_docs

        pdf_bytes = b"fake pdf content"
        result = extract_text_from_pdf_bytes(pdf_bytes, "test.pdf")

        expected = "Page 1 text\n\nPage 2 text"
        assert result == expected

    @patch("os.unlink")
    @patch("tempfile.NamedTemporaryFile")
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("app.services.pdf_utils.load_pdf_with_pypdf")
    def test_extract_text_from_pdf_bytes_single_page(
        self, mock_load_pypdf, mock_has_tables, mock_tempfile, mock_unlink
    ):
        """Test text extraction from single-page PDF bytes."""
        # Mock tempfile as context manager
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp_file.__exit__.return_value = None
        mock_temp_file.name = "/tmp/single.pdf"
        mock_tempfile.return_value = mock_temp_file

        # Mock has_tables_fast to return no tables
        mock_has_tables.return_value = (False, 0)

        # Mock load_pdf_with_pypdf to return single document
        from app.services.pdf_utils import Document

        mock_docs = [Document(page_content="Single page content", metadata={"page": 1})]
        mock_load_pypdf.return_value = mock_docs

        pdf_bytes = b"single page pdf"
        result = extract_text_from_pdf_bytes(pdf_bytes, "single.pdf")

        assert result == "Single page content"

    @patch("os.unlink")
    @patch("tempfile.NamedTemporaryFile")
    @patch("app.services.pdf_utils.has_tables_fast")
    @patch("app.services.pdf_utils.load_pdf_with_pypdf")
    def test_extract_text_from_pdf_bytes_empty_pdf(
        self, mock_load_pypdf, mock_has_tables, mock_tempfile, mock_unlink
    ):
        """Test text extraction from empty PDF bytes."""
        # Mock tempfile as context manager
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp_file.__exit__.return_value = None
        mock_temp_file.name = "/tmp/empty.pdf"
        mock_tempfile.return_value = mock_temp_file

        # Mock has_tables_fast to return no tables
        mock_has_tables.return_value = (False, 0)

        # Mock load_pdf_with_pypdf to return empty list
        mock_load_pypdf.return_value = []

        pdf_bytes = b"empty pdf"
        result = extract_text_from_pdf_bytes(pdf_bytes, "empty.pdf")

        assert result == ""

    @patch("os.unlink")
    @patch("tempfile.NamedTemporaryFile")
    @patch("app.services.pdf_utils.has_tables_fast")
    def test_extract_text_from_pdf_bytes_error(
        self, mock_has_tables, mock_tempfile, mock_unlink
    ):
        """Test text extraction error handling."""
        from fastapi import HTTPException

        # Mock tempfile as context manager
        mock_temp_file = MagicMock()
        mock_temp_file.__enter__.return_value = mock_temp_file
        mock_temp_file.__exit__.return_value = None
        mock_temp_file.name = "/tmp/corrupted.pdf"
        mock_tempfile.return_value = mock_temp_file

        # Mock has_tables_fast to raise exception
        mock_has_tables.side_effect = Exception("PDF processing error")

        pdf_bytes = b"corrupted pdf content"

        with pytest.raises(
            HTTPException,
            match="Error extracting text from PDF corrupted.pdf: PDF processing error",
        ):
            extract_text_from_pdf_bytes(pdf_bytes, "corrupted.pdf")
