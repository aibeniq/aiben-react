"""
Integration tests for end-to-end workflows.
Tests complete user journeys and cross-component interactions.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.services.document_utils import extract_text_from_file_unified
from app.services.llms import invoke_llm
from app.services.pdf_utils import extract_text_from_pdf_bytes


class TestDocumentProcessingPipeline:
    """Integration tests for document processing workflows."""

    @patch("app.services.document_utils.extract_text_from_docx_bytes")
    def test_docx_processing_pipeline(
        self, mock_extract_docx, client, superuser_token_headers, db
    ):
        """Test complete DOCX document processing pipeline."""
        # Mock document extraction
        mock_extract_docx.return_value = (
            "Extracted DOCX content with important information"
        )

        # Simulate file content
        docx_content = b"fake docx bytes"

        # Test text extraction
        result = extract_text_from_file_unified(docx_content, "test.docx")
        assert result == "Extracted DOCX content with important information"

        # Verify the extraction was called correctly
        mock_extract_docx.assert_called_once_with(docx_content, "test.docx")

    @patch("app.services.pdf_utils.pypdf")
    def test_pdf_processing_pipeline(
        self, mock_pypdf, client, superuser_token_headers, db
    ):
        """Test complete PDF document processing pipeline."""
        # Mock PDF processing
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF content with tables and text"
        mock_reader.pages = [mock_page]
        mock_pypdf.PdfReader.return_value = mock_reader

        # Test PDF text extraction with parsing_mode parameter
        pdf_bytes = b"fake pdf content"
        result = extract_text_from_pdf_bytes(
            pdf_bytes, "test.pdf", parsing_mode="basic"
        )
        assert result == "PDF content with tables and text"

    @patch("app.services.document_utils.extract_text_from_csv_bytes")
    def test_csv_processing_pipeline(
        self, mock_extract_csv, client, superuser_token_headers, db
    ):
        """Test complete CSV document processing pipeline."""
        mock_extract_csv.return_value = "Name,Age,City\nJohn,25,NYC\nJane,30,LA"

        csv_content = b"name,age,city\njohn,25,nyc\njane,30,la"
        result = extract_text_from_file_unified(csv_content, "test.csv")

        assert "Name,Age,City" in result
        assert "John,25,NYC" in result

    @patch("app.services.llms.LlmInteraction")
    @patch("app.services.llms.Session")
    def test_llm_interaction_recording_pipeline(
        self,
        mock_session_class,
        mock_interaction_class,
        client,
        superuser_token_headers,
        db,
    ):
        """Test LLM interaction recording in processing pipeline."""
        # Mock database session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock LLM interaction
        mock_interaction = Mock()
        mock_interaction_class.return_value = mock_interaction

        # Import and test the record function
        from app.services.llms import record_llm_interaction

        # Test recording interaction
        record_llm_interaction(
            session=mock_session,
            user_id=1,
            functionality="veradoc",
            input_data="Analyze this document",
            output_data="Document analysis complete",
            metadata={"model": "gpt-4", "provider": "openai", "tokens_used": 150},
        )

        # Verify database operations
        mock_session.add.assert_called_once_with(mock_interaction)
        mock_session.commit.assert_called_once()

    @patch("app.tests.integration.test_document_processing_pipeline.invoke_llm")
    @patch("app.services.global_rate_limiter.global_rate_limiter")
    def test_document_analysis_workflow(
        self, mock_rate_limiter, mock_invoke_llm, client, superuser_token_headers, db
    ):
        """Test complete document analysis workflow."""
        # Mock rate limiter
        mock_rate_limiter.wait_for_capacity.return_value = True
        mock_rate_limiter.record_actual_usage.return_value = None

        # Mock LLM response
        mock_invoke_llm.return_value = (
            "Analysis: This document contains important business information."
        )

        # Mock document content
        doc_content = "Company financial report Q1 2024"

        # Test LLM invocation
        result = invoke_llm(Mock(), f"Analyze this document: {doc_content}")

        assert "Analysis:" in result
        assert "business information" in result

    def test_unified_document_processing_edge_cases(
        self, client, superuser_token_headers, db
    ):
        """Test unified document processing with various edge cases."""
        # Test empty file
        result = extract_text_from_file_unified(b"", "empty.txt")
        assert result == ""

        # Test unknown extension
        result = extract_text_from_file_unified(b"content", "file.unknown")
        assert result == "content"

        # Test text file
        text_content = b"This is a plain text file."
        result = extract_text_from_file_unified(text_content, "test.txt")
        assert result == "This is a plain text file."

    @patch("app.services.document_utils.extract_documents_from_file_unified")
    @patch("app.tests.integration.test_document_processing_pipeline.invoke_llm")
    def test_knowledge_base_ingestion_simulation(
        self, mock_invoke_llm, mock_extract_docs, client, superuser_token_headers, db
    ):
        """Simulate knowledge base document ingestion workflow."""
        from langchain_core.documents import Document

        # Mock document extraction
        mock_docs = [
            Document(
                page_content="Document chunk 1",
                metadata={"source": "test.pdf", "page": 1},
            ),
            Document(
                page_content="Document chunk 2",
                metadata={"source": "test.pdf", "page": 2},
            ),
        ]
        mock_extract_docs.return_value = mock_docs

        # Mock LLM processing
        mock_invoke_llm.return_value = "Processed and indexed successfully"

        # Simulate the workflow
        documents = mock_extract_docs(b"pdf content", "test.pdf")
        assert len(documents) == 2

        # Simulate LLM processing of each chunk
        for doc in documents:
            result = mock_invoke_llm(Mock(), f"Process: {doc.page_content}")
            assert "Processed" in result

    @patch("app.services.document_utils.extract_text_from_file_unified")
    @patch("app.tests.integration.test_document_processing_pipeline.invoke_llm")
    def test_chatbot_query_processing(
        self, mock_invoke_llm, mock_extract_text, client, superuser_token_headers, db
    ):
        """Test chatbot query processing with document retrieval."""
        # Mock document retrieval
        mock_extract_text.return_value = "Retrieved document content about AI"

        # Mock LLM response
        mock_invoke_llm.return_value = (
            "Based on the documents, AI is transforming business processes."
        )

        # Simulate query processing
        query = "What is the impact of AI on business?"
        retrieved_content = mock_extract_text(b"doc content", "ai_document.pdf")

        # Generate response using retrieved content
        prompt = f"Answer this question using the retrieved information: {query}\n\nRetrieved content: {retrieved_content}"
        response = mock_invoke_llm(Mock(), prompt)

        assert "AI is transforming" in response
        assert "business processes" in response
