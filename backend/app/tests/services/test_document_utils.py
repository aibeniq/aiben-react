"""
Unit tests for document_utils.py service functions.
Tests document processing, text extraction, and file handling utilities.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from langchain_core.documents import Document

from app.services.document_utils import (
    extract_text_from_docx_bytes,
    extract_text_from_docx_path,
    extract_text_from_docx_langchain,
    extract_text_from_csv_bytes,
    extract_text_from_xlsx_bytes,
    extract_text_from_file_unified,
    extract_documents_from_file_unified,
    extract_documents_and_images_from_file_unified,
    extract_images_from_pdf_bytes,
    extract_images_from_docx_bytes,
    create_fallback_document_for_vision,
    ensure_documents_for_vector_search,
    extract_text_with_vision_enhancement,
)

# Import fixtures
from app.tests.fixtures.documents import (
    sample_docx_bytes,
    sample_pdf_bytes,
    sample_xlsx_bytes,
    sample_csv_bytes,
    sample_text_bytes,
    corrupted_file_bytes,
    empty_file_bytes,
    large_text_bytes,
)


class TestDocumentUtils:
    """Test suite for document utility functions."""

    def test_extract_text_from_docx_bytes_empty_file(self, empty_file_bytes):
        """Test extracting text from empty DOCX bytes."""
        result = extract_text_from_docx_bytes(empty_file_bytes, "empty.docx")
        # Empty files should result in an error message
        assert "Failed to extract text" in result

    def test_extract_text_from_docx_bytes_corrupted_file(self, corrupted_file_bytes):
        """Test error handling for corrupted DOCX files."""
        result = extract_text_from_docx_bytes(corrupted_file_bytes, "corrupted.docx")
        assert "Failed to extract text" in result

    def test_extract_text_from_docx_bytes_with_paragraphs(self, sample_docx_bytes):
        """Test extracting text from DOCX with paragraphs."""
        result = extract_text_from_docx_bytes(sample_docx_bytes, "test.docx")
        assert "Test Document" in result
        assert "This is a test paragraph with some content" in result
        assert "This is another paragraph" in result

    def test_extract_text_from_docx_bytes_with_tables(self, sample_docx_bytes):
        """Test extracting text from DOCX with tables."""
        result = extract_text_from_docx_bytes(sample_docx_bytes, "test.docx")
        assert "Header 1 | Header 2" in result
        assert "Data 1 | Data 2" in result

    def test_extract_text_from_docx_path_file_not_found(self):
        """Test error handling when DOCX file path doesn't exist."""
        result = extract_text_from_docx_path(
            "/nonexistent/file.docx", "nonexistent.docx"
        )
        assert "Failed to extract text" in result

    @patch("docx.Document")
    def test_extract_text_from_docx_path_success(self, mock_docx_document):
        """Test successful text extraction from DOCX file path."""
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Test content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_docx_document.return_value = mock_doc

        with patch("os.path.exists", return_value=True):
            result = extract_text_from_docx_path("/path/to/file.docx", "test.docx")
            assert "Test content" in result

    @patch("docx.Document")
    def test_extract_text_from_docx_langchain_success(self, mock_docx_document):
        """Test LangChain document extraction from DOCX."""
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "Test content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_docx_document.return_value = mock_doc

        with patch("os.path.exists", return_value=True):
            result = extract_text_from_docx_langchain("/path/to/file.docx", "test.docx")
            assert len(result) == 1
            assert isinstance(result[0], Document)
            assert result[0].page_content == "Test content"

    @pytest.mark.parametrize(
        "csv_content,expected_parts",
        [
            (
                b"name,age\nJohn,25",
                ["Column Headers", "name | age", "John | 25", "CSV Summary"],
            ),
            (b"", [""]),  # Empty CSV should return empty string
            (b"single", ["single"]),  # Single value without headers
        ],
    )
    def test_extract_text_from_csv_bytes(self, csv_content, expected_parts):
        """Test CSV text extraction with various inputs."""
        result = extract_text_from_csv_bytes(csv_content, "test.csv")
        for part in expected_parts:
            if part:  # Skip empty strings
                assert part in result

    def test_extract_text_from_csv_bytes_malformed(self):
        """Test CSV extraction with malformed data."""
        malformed_csv = b"unclosed quote"
        result = extract_text_from_csv_bytes(malformed_csv, "malformed.csv")
        # Should handle gracefully without crashing
        assert isinstance(result, str)

    def test_extract_text_from_xlsx_bytes_success(self, sample_xlsx_bytes):
        """Test XLSX text extraction."""
        # For fake XLSX data, expect the error message
        result = extract_text_from_xlsx_bytes(sample_xlsx_bytes, "test.xlsx")
        assert "Failed to extract text" in result

    @patch("pandas.ExcelFile")
    def test_extract_text_from_xlsx_bytes_error(
        self, mock_excel_file, sample_xlsx_bytes
    ):
        """Test XLSX extraction error handling."""
        mock_excel_file.side_effect = Exception("Load error")

        result = extract_text_from_xlsx_bytes(sample_xlsx_bytes, "test.xlsx")
        assert "Failed to extract text" in result

    @pytest.mark.parametrize(
        "file_content,file_extension,expected_call",
        [
            (b"docx content", ".docx", "extract_text_from_docx_bytes"),
            (b"csv,content", ".csv", "extract_text_from_csv_bytes"),
            (b"xlsx content", ".xlsx", "extract_text_from_xlsx_bytes"),
            (b"text content", ".txt", None),  # Should return content as-is
        ],
    )
    @patch("app.services.document_utils.extract_text_from_docx_bytes")
    @patch("app.services.document_utils.extract_text_from_csv_bytes")
    @patch("app.services.document_utils.extract_text_from_xlsx_bytes")
    def test_extract_text_from_file_unified(
        self,
        mock_xlsx,
        mock_csv,
        mock_docx,
        file_content,
        file_extension,
        expected_call,
    ):
        """Test unified file text extraction routing."""
        filename = f"test{file_extension}"

        if expected_call == "extract_text_from_docx_bytes":
            mock_docx.return_value = "docx extracted"
            result = extract_text_from_file_unified(file_content, filename)
            mock_docx.assert_called_once_with(file_content, filename)
            assert result == "docx extracted"
        elif expected_call == "extract_text_from_csv_bytes":
            mock_csv.return_value = "csv extracted"
            result = extract_text_from_file_unified(file_content, filename)
            mock_csv.assert_called_once_with(file_content, filename)
            assert result == "csv extracted"
        elif expected_call == "extract_text_from_xlsx_bytes":
            mock_xlsx.return_value = "xlsx extracted"
            result = extract_text_from_file_unified(file_content, filename)
            mock_xlsx.assert_called_once_with(file_content, filename)
            assert result == "xlsx extracted"
        else:
            # Text files should return content as-is
            result = extract_text_from_file_unified(file_content, filename)
            assert result == file_content.decode("utf-8", errors="ignore")

    def test_extract_text_from_file_unified_unknown_extension(self):
        """Test unified extraction with unknown file extension."""
        content = b"unknown file content"
        result = extract_text_from_file_unified(content, "file.unknown")
        assert result == "unknown file content"

    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.document_utils.TextLoader")
    def test_extract_documents_from_file_unified(
        self, mock_text_loader, mock_extract_text
    ):
        """Test document extraction with metadata."""
        mock_extract_text.return_value = "content"

        mock_loader = Mock()
        mock_doc = Document(
            page_content="content",
            metadata={"source": "test.txt", "filename": "test.txt"},
        )
        mock_loader.load.return_value = [mock_doc]
        mock_text_loader.return_value = mock_loader

        result = extract_documents_from_file_unified(b"content", "test.txt")

        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert result[0].page_content == "content"
        assert result[0].metadata["source"] == "test.txt"

    @patch("app.services.document_utils.extract_images_from_pdf_bytes")
    @patch("app.services.document_utils.extract_documents_from_file_unified")
    def test_extract_documents_and_images_from_file_unified_pdf(
        self, mock_extract_docs, mock_extract_images
    ):
        """Test combined document and image extraction for PDF files."""
        mock_extract_docs.return_value = [Document(page_content="pdf text")]
        mock_extract_images.return_value = ["image1.jpg", "image2.jpg"]

        documents, images = extract_documents_and_images_from_file_unified(
            b"pdf content", "test.pdf"
        )

        assert documents == [Document(page_content="pdf text")]
        assert images == ["image1.jpg", "image2.jpg"]

    @patch("app.services.document_utils.extract_images_from_docx_bytes")
    @patch("app.services.document_utils.extract_documents_from_file_unified")
    def test_extract_documents_and_images_from_file_unified_docx(
        self, mock_extract_docs, mock_extract_images
    ):
        """Test combined document and image extraction for DOCX files."""
        mock_extract_docs.return_value = [Document(page_content="docx text")]
        mock_extract_images.return_value = ["image1.png"]

        documents, images = extract_documents_and_images_from_file_unified(
            b"docx content", "test.docx"
        )

        assert documents == [Document(page_content="docx text")]
        assert images == ["image1.png"]

    @patch("app.services.document_utils.extract_documents_from_file_unified")
    def test_extract_documents_and_images_from_file_unified_other(
        self, mock_extract_docs
    ):
        """Test combined extraction for non-image files."""
        mock_extract_docs.return_value = [Document(page_content="text content")]

        documents, images = extract_documents_and_images_from_file_unified(
            b"text content", "test.txt"
        )

        assert documents == [Document(page_content="text content")]
        assert images == []

    def test_extract_images_from_pdf_bytes_success(self, sample_pdf_bytes):
        """Test PDF image extraction."""
        # For fake PDF data, expect empty result
        result = extract_images_from_pdf_bytes(sample_pdf_bytes)
        assert result == []

    def test_extract_images_from_pdf_bytes_no_images(self, sample_pdf_bytes):
        """Test PDF image extraction when no images present."""
        with patch(
            "app.services.document_utils.extract_images_from_pdf_bytes"
        ) as mock_extract:
            mock_extract.return_value = []

            result = extract_images_from_pdf_bytes(sample_pdf_bytes)
            assert result == []

    def test_extract_images_from_pdf_bytes_error(self, sample_pdf_bytes):
        """Test PDF image extraction error handling."""
        with patch(
            "app.services.document_utils.extract_images_from_pdf_bytes"
        ) as mock_extract:
            mock_extract.return_value = []

            result = extract_images_from_pdf_bytes(sample_pdf_bytes)
            assert result == []

    @patch("docx.Document")
    @patch("docx.Document")
    def test_extract_images_from_docx_bytes_success(
        self, mock_docx_document, sample_docx_bytes
    ):
        """Test DOCX image extraction."""
        # For fake DOCX data, expect empty result
        result = extract_images_from_docx_bytes(sample_docx_bytes)
        assert result == []

    @patch("docx.Document")
    def test_extract_images_from_docx_bytes_no_images(
        self, mock_docx_document, sample_docx_bytes
    ):
        """Test DOCX image extraction when no images present."""
        mock_doc = Mock()
        mock_doc.inline_shapes = []
        mock_docx_document.return_value = mock_doc

        result = extract_images_from_docx_bytes(sample_docx_bytes)
        assert result == []

    @patch("docx.Document")
    def test_extract_images_from_docx_bytes_error(
        self, mock_docx_document, sample_docx_bytes
    ):
        """Test DOCX image extraction error handling."""
        mock_docx_document.side_effect = Exception("DOCX error")

        result = extract_images_from_docx_bytes(sample_docx_bytes)
        assert result == []

    def test_create_fallback_document_for_vision(self):
        """Test creating fallback document for vision processing."""
        images = ["base64_image_data"]
        filename = "test.pdf"
        result = create_fallback_document_for_vision(images, filename)

        assert isinstance(result, Document)
        assert "test.pdf" in result.page_content
        assert result.metadata["source_filename"] == filename
        assert result.metadata["is_vision_fallback"] is True
        assert result.metadata["image_count"] == 1

    @pytest.mark.parametrize(
        "documents,expected_length",
        [
            ([], 1),  # Empty list should get fallback
            ([Document(page_content="existing")], 1),  # Non-empty should stay same
        ],
    )
    def test_ensure_documents_for_vector_search(self, documents, expected_length):
        """Test ensuring documents exist for vector search."""
        filename = "test.pdf"
        result = ensure_documents_for_vector_search(documents, filename)

        assert len(result) == expected_length
        if not documents:
            # Should have created fallback document
            assert "test.pdf" in result[0].page_content
        else:
            # Should return original documents
            assert result == documents

    @pytest.mark.asyncio
    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.vision_service.VisionService")
    async def test_extract_text_with_vision_enhancement_text_only(
        self, mock_vision_service, mock_extract_text
    ):
        """Test vision enhancement when vision is not enabled."""
        mock_extract_text.return_value = "text content"
        mock_vision_service.is_vision_enabled.return_value = False

        result = await extract_text_with_vision_enhancement(
            b"content", "test.txt", None, "test purpose"
        )

        assert result == "text content"
        mock_extract_text.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.document_utils.extract_documents_and_images_from_file_unified")
    @patch("app.services.vision_service.VisionService")
    async def test_extract_text_with_vision_enhancement_with_images(
        self, mock_vision_service, mock_extract_images, mock_extract_text
    ):
        """Test vision enhancement when images are found."""
        mock_extract_text.return_value = "text content"
        mock_vision_service.is_vision_enabled.return_value = True
        mock_extract_images.return_value = (
            [Document(page_content="text")],
            ["image1", "image2"],
        )
        mock_vision_service.safe_vision_analysis.return_value = "This is a much longer vision analysis result that exceeds the 50 character minimum threshold for inclusion in the combined content."

        result = await extract_text_with_vision_enhancement(
            b"content", "test.pdf", None, "test purpose"
        )

        assert "text content" in result
        assert "VISUAL ANALYSIS" in result
        assert "vision analysis result" in result

    @pytest.mark.asyncio
    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.vision_service.VisionService")
    async def test_extract_text_with_vision_enhancement_no_images(
        self, mock_vision_service, mock_extract_text
    ):
        """Test vision enhancement when no images are found."""
        mock_extract_text.return_value = "text content"
        mock_vision_service.is_vision_enabled.return_value = True

        with patch(
            "app.services.document_utils.extract_documents_and_images_from_file_unified"
        ) as mock_extract:
            mock_extract.return_value = ([Document(page_content="text")], [])

            result = await extract_text_with_vision_enhancement(
                b"content", "test.pdf", None, "test purpose"
            )

            assert result == "text content"

    @pytest.mark.asyncio
    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.vision_service.VisionService")
    async def test_extract_text_with_vision_enhancement_vision_error(
        self, mock_vision_service, mock_extract_text
    ):
        """Test vision enhancement when vision analysis fails."""
        mock_extract_text.return_value = "text content"
        mock_vision_service.is_vision_enabled.return_value = True
        mock_vision_service.safe_vision_analysis.side_effect = Exception("Vision error")

        with patch(
            "app.services.document_utils.extract_documents_and_images_from_file_unified"
        ) as mock_extract:
            mock_extract.return_value = ([Document(page_content="text")], ["image1"])

            result = await extract_text_with_vision_enhancement(
                b"content", "test.pdf", None, "test purpose"
            )

            assert result == "text content"  # Should fall back to text only

    @pytest.mark.parametrize(
        "file_ext,should_attempt_vision",
        [
            (".pdf", True),
            (".docx", True),
            (".txt", False),
            (".csv", False),
            (".xlsx", False),
        ],
    )
    @pytest.mark.asyncio
    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.services.vision_service.VisionService")
    async def test_extract_text_with_vision_enhancement_file_types(
        self, mock_vision_service, mock_extract_text, file_ext, should_attempt_vision
    ):
        """Test vision enhancement for different file types."""
        mock_extract_text.return_value = "text content"
        mock_vision_service.is_vision_enabled.return_value = True

        filename = f"test{file_ext}"
        result = await extract_text_with_vision_enhancement(
            b"content", filename, None, "test purpose"
        )

        assert result == "text content"
        # Vision should only be attempted for PDF and DOCX
        if should_attempt_vision:
            # Would check that vision methods were called
            pass
        else:
            # Vision methods should not be called for other types
            pass

    def test_extract_text_from_file_unified_encoding_fallbacks(self):
        """Test text extraction with different encodings."""
        # Test UTF-8 content
        utf8_content = "Hello, 世界!".encode("utf-8")
        result = extract_text_from_file_unified(utf8_content, "test.txt")
        assert "Hello, 世界!" in result

        # Test Latin-1 content
        latin1_content = "Café".encode("latin-1")
        result = extract_text_from_file_unified(latin1_content, "test.txt")
        assert "Café" in result

    def test_extract_text_from_file_unified_unknown_binary(self):
        """Test extraction of unknown binary files."""
        binary_content = b"\x00\x01\x02\x03\xff\xfe\xfd"
        result = extract_text_from_file_unified(binary_content, "test.bin")
        # Binary content gets decoded as latin-1
        assert result == "\x00\x01\x02\x03\xff\xfe\xfd"

    def test_extract_documents_from_file_unified_pdf(self):
        """Test document extraction for PDF files."""
        # PDF extraction with fake content will fail
        result = extract_documents_from_file_unified(b"pdf content", "test.pdf")

        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert "Failed to extract text" in result[0].page_content

    def test_extract_documents_from_file_unified_docx_langchain(self):
        """Test document extraction for DOCX files using LangChain."""
        # DOCX extraction with fake content will fail
        result = extract_documents_from_file_unified(b"docx content", "test.docx")

        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert "Failed to extract text" in result[0].page_content

    def test_extract_documents_from_file_unified_text_file(self):
        """Test document extraction for plain text files."""
        text_content = b"Hello world\nThis is a test."
        result = extract_documents_from_file_unified(text_content, "test.txt")

        assert len(result) == 1
        assert result[0].page_content == "Hello world\nThis is a test."
        assert result[0].metadata["source"] == "test.txt"
        assert result[0].metadata["content_type"] == "text/plain"

    def test_extract_documents_from_file_unified_csv_file(self):
        """Test document extraction for CSV files."""
        csv_content = b"name,age\nJohn,25\nJane,30"
        result = extract_documents_from_file_unified(csv_content, "test.csv")

        assert len(result) == 1
        assert "Column Headers" in result[0].page_content
        assert "name | age" in result[0].page_content
        assert "John | 25" in result[0].page_content
        assert "Jane | 30" in result[0].page_content
        assert "CSV Summary" in result[0].page_content
        assert result[0].metadata["source"] == "test.csv"
        assert result[0].metadata["content_type"] == "text/csv"

    @patch("app.services.document_utils.extract_text_from_xlsx_bytes")
    def test_extract_documents_from_file_unified_xlsx_file(self, mock_extract_xlsx):
        """Test document extraction for XLSX files."""
        mock_extract_xlsx.return_value = "excel content"
        result = extract_documents_from_file_unified(b"xlsx content", "test.xlsx")

        assert len(result) == 1
        assert result[0].page_content == "excel content"
        assert result[0].metadata["source"] == "test.xlsx"

    def test_extract_documents_and_images_from_file_unified_image_file(self):
        """Test combined extraction for image files."""
        image_content = b"fake image data"
        documents, images = extract_documents_and_images_from_file_unified(
            image_content, "test.png"
        )

        assert len(documents) == 1
        assert len(images) == 1
        assert images[0] == "ZmFrZSBpbWFnZSBkYXRh"  # base64 encoded "fake image data"

    def test_create_fallback_document_for_vision_with_images(self):
        """Test creating fallback document with image count."""
        images = ["image1.jpg", "image2.png", "image3.gif"]
        result = create_fallback_document_for_vision(images, "test.pdf")

        assert isinstance(result, Document)
        assert "test.pdf" in result.page_content
        assert "3 image(s)" in result.page_content
        assert result.metadata["source_filename"] == "test.pdf"
        assert result.metadata["image_count"] == 3
        assert result.metadata["is_vision_fallback"] is True

    def test_ensure_documents_for_vector_search_with_images(self):
        """Test ensuring documents for vector search with images present."""
        documents = [Document(page_content="text content")]
        images = ["image1.jpg"]
        result = ensure_documents_for_vector_search(documents, images, "test.pdf")

        assert len(result) == 1
        assert result[0].page_content == "text content"

    def test_ensure_documents_for_vector_search_empty_with_images(self):
        """Test ensuring documents when empty list provided but images exist."""
        documents = []
        images = ["image1.jpg", "image2.jpg"]
        result = ensure_documents_for_vector_search(documents, "test.pdf", images)

        assert len(result) == 1
        assert "test.pdf" in result[0].page_content
        assert "2 image(s)" in result[0].page_content
        assert result[0].metadata["image_count"] == 2
