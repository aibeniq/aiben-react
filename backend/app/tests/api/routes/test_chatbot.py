"""
API tests for chatbot endpoints.
Tests chatbot functionality with uploaded documents and knowledge bases,
covering both vector search and full document scan modes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from sqlmodel import Session
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.models import KnowledgeBase, Source, SourceData, User
from app.services.llms import invoke_llm


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Create a minimal PDF-like content for testing
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"


@pytest.fixture
def sample_docx_bytes():
    """Sample DOCX bytes for testing."""
    # Create minimal DOCX-like content (ZIP with XML)
    import zipfile
    import io

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add minimal content types
        zip_file.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        )
        # Add minimal document
        zip_file.writestr(
            "word/document.xml",
            '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test DOCX Content</w:t></w:r></w:p></w:body></w:document>',
        )
        zip_file.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        )

    return zip_buffer.getvalue()


class TestChatbotKnowledgeBase:
    """Test suite for chatbot knowledge base queries."""

    @patch("app.api.routes.chatbot.invoke_llm")
    @patch("app.api.routes.chatbot.session_manager")
    def test_query_knowledge_base_full_text_search_success(
        self,
        mock_session_manager,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        db: Session,
    ):
        """Test successful knowledge base query with full text search mode."""
        # Mock LLM response
        mock_invoke_llm.return_value = "This is a test answer from the knowledge base."

        # Mock session manager with cached session data
        mock_retriever = Mock()
        mock_llm = Mock()

        # Mock retriever to return test documents
        mock_doc = Mock()
        mock_doc.page_content = "Test document content"
        mock_doc.metadata = {"source": "test_document.txt"}
        mock_retriever.get_relevant_documents.return_value = [mock_doc]

        mock_session_data = {
            "kb_id": str(test_knowledge_base.id),
            "retriever": mock_retriever,
            "llm": mock_llm,
            "temp_dir": "/tmp/test",
        }
        mock_session_manager.get_session.return_value = mock_session_data
        mock_session_manager.session_needs_rebuild.return_value = False

        # Create test source data
        source_data = SourceData(
            data=b"Test document content", file_hash="dummy_hash_for_test"
        )
        db.add(source_data)
        db.commit()

        # Create test source
        source = Source(
            name="test_document.txt",
            source_data_id=source_data.id,
            knowledge_base_id=test_knowledge_base.id,
            owner_id=test_knowledge_base.owner_id,
        )
        db.add(source)
        db.commit()

        data = {"question": "What is the test content?", "search_mode": "full_text"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/knowledge-base/{test_knowledge_base.id}",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "sources" in content
        assert "session_id" in content
        assert content["answer"] == "This is a test answer from the knowledge base."

    @patch("app.api.routes.chatbot.invoke_llm")
    @patch("app.api.routes.chatbot.session_manager")
    def test_query_knowledge_base_full_text_scan_success(
        self,
        mock_session_manager,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        db: Session,
    ):
        """Test successful knowledge base query with full text scan mode."""
        # Mock LLM responses for chunk analysis and synthesis
        mock_invoke_llm.return_value = "Found relevant information about test content."

        # Create test source data
        source_data = SourceData(
            data=b"Test document content for full text scanning",
            content_type="text/plain",
            file_hash="test_hash_for_full_text_scan",
        )
        db.add(source_data)
        db.commit()

        # Create test source
        source = Source(
            name="test_document.txt",
            source_data_id=source_data.id,
            knowledge_base_id=test_knowledge_base.id,
            owner_id=test_knowledge_base.owner_id,
        )
        db.add(source)
        db.commit()

        data = {"question": "What is the test content?", "search_mode": "full_text"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/knowledge-base/{test_knowledge_base.id}",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "sources" in content
        assert "session_id" in content

    def test_query_knowledge_base_invalid_search_mode(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
    ):
        """Test knowledge base query with invalid search mode."""
        data = {"question": "What is the test content?", "search_mode": "invalid_mode"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/knowledge-base/{test_knowledge_base.id}",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 400
        content = response.json()
        assert "Invalid search mode" in content["detail"]

    def test_query_knowledge_base_unauthorized(
        self, client: TestClient, test_knowledge_base
    ):
        """Test knowledge base query without authentication."""
        data = {"question": "What is the test content?", "search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/knowledge-base/{test_knowledge_base.id}",
            params=data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided

    def test_query_knowledge_base_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test knowledge base query with non-existent knowledge base."""
        import uuid

        fake_kb_id = str(uuid.uuid4())

        data = {"question": "What is the test content?", "search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/knowledge-base/{fake_kb_id}",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 404


class TestChatbotDocument:
    """Test suite for chatbot document queries."""

    @patch("app.api.routes.chatbot.invoke_llm")
    @patch("app.api.routes.chatbot.session_manager")
    def test_query_document_vector_search_success(
        self,
        mock_session_manager,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test successful document query with vector search mode."""
        # Mock LLM response for final answer generation
        mock_invoke_llm.return_value = (
            "This is a test answer from the uploaded document."
        )

        # Mock session manager
        mock_session_manager.get_session.return_value = None
        mock_session_manager.session_needs_rebuild.return_value = False

        # Create test file
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {"search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document?question=What+is+in+this+document%3F",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        # Test now works with proper mocking
        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "sources" in content
        assert "session_id" in content
        assert content["answer"] == "This is a test answer from the uploaded document."

    @patch("app.api.routes.chatbot.invoke_llm")
    @patch("app.api.routes.chatbot.session_manager")
    def test_query_document_full_text_search_success(
        self,
        mock_session_manager,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test successful document query with full text scan mode."""
        # Mock LLM responses for chunk analysis and synthesis
        mock_invoke_llm.side_effect = [
            "Found relevant information in the document.",  # For chunk analysis
            "This is a test answer from the uploaded document.",  # For final synthesis
        ]

        # Create test file
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {"search_mode": "full_text"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document?question=What+is+in+this+document%3F",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "sources" in content
        assert "session_id" in content

    def test_query_document_no_question(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test document query without providing a question."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {"search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 400
        content = response.json()
        assert "Question is required" in content["detail"]

    def test_query_document_no_files_initial_query(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test document query without files for initial query."""
        data = {"search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document?question=What+is+in+this+document%3F",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 400
        content = response.json()
        assert "At least one file is required" in content["detail"]

    def test_query_document_invalid_search_mode(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test document query with invalid search mode."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {"question": "What is in this document?"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document?question=What+is+in+this+document%3F&search_mode=invalid_mode",
            headers=superuser_token_headers,
            files=files,
        )

        assert response.status_code == 400
        content = response.json()
        assert "Invalid search mode" in content["detail"]

    def test_query_document_full_text_no_files(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test document query with full text scan but no files."""
        data = {"search_mode": "full_text"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document?question=What+is+in+this+document%3F",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 400
        content = response.json()
        assert (
            "At least one file is required for initial questions" in content["detail"]
        )

    def test_query_document_unauthorized(self, client: TestClient, sample_pdf_bytes):
        """Test document query without authentication."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}
        data = {"question": "What is in this document?"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/document",
            data=data,
            files=files,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestChatbotText:
    """Test suite for chatbot text queries."""

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_query_text_success(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful text query."""
        # Mock LLM response
        mock_invoke_llm.return_value = (
            "This is a test answer based on the provided text."
        )

        data = {
            "question": "What is this text about?",
        }

        response = client.post(
            f"{settings.API_V1_STR}/chat/text",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "session_id" in content
        assert "rephrased_question" in content
        assert content["answer"] == "This is a test answer based on the provided text."

    def test_query_text_no_question(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test text query without providing a question."""
        data = {}

        response = client.post(
            f"{settings.API_V1_STR}/chat/text",
            headers=superuser_token_headers,
            params=data,
        )

        assert response.status_code == 422
        content = response.json()
        assert len(content["detail"]) > 0  # Pydantic validation errors

    def test_query_text_unauthorized(self, client: TestClient):
        """Test text query without authentication."""
        data = {"question": "What is artificial intelligence?"}
        response = client.post(
            f"{settings.API_V1_STR}/chat/text",
            params=data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestChatbotGeneral:
    """Test suite for general chatbot endpoints."""

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_query_general_success(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful general chatbot query."""
        # Mock LLM response
        mock_invoke_llm.return_value = "This is a general chatbot response."

        data = {"prompt": "Tell me about artificial intelligence."}

        response = client.post(
            f"{settings.API_V1_STR}/chat/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "answer" in content
        assert "sources" in content
        assert "session_id" in content
        assert content["answer"] == "This is a general chatbot response."

    def test_query_general_no_prompt(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test general chatbot query without providing a prompt."""
        data = {}

        response = client.post(
            f"{settings.API_V1_STR}/chat/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_query_general_unauthorized(self, client: TestClient):
        """Test general chatbot query without authentication."""
        data = {"prompt": "Tell me about artificial intelligence."}

        response = client.post(
            f"{settings.API_V1_STR}/chat/",
            json=data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestChatbotAssistant:
    """Test suite for chatbot assistant endpoints."""

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_detect_assistant_intent_success(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful assistant intent detection."""
        # Mock LLM response with valid JSON
        mock_invoke_llm.return_value = """{
            "primary_intent": "generate",
            "suggestion_type": "outline",
            "is_multistep": true,
            "steps": [
                {"action": "suggest_outline", "description": "Generate outline"},
                {"action": "run_generate", "description": "Generate report"}
            ],
            "parameters": {
                "custom_instructions": "about canned sardines",
                "search_mode": "vector",
                "consult_docs": true
            },
            "confidence": 0.9,
            "reasoning": "User wants to generate content with outline first"
        }"""

        data = {
            "message": "Generate a report about canned sardines",
            "file_names": ["report.pdf", "data.xlsx"],
        }

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["primary_intent"] == "generate"
        assert content["suggestion_type"] == "outline"
        assert content["is_multistep"] is True
        assert len(content["steps"]) == 2
        assert content["parameters"]["custom_instructions"] == "about canned sardines"
        assert content["confidence"] == 0.9
        assert "reasoning" in content

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_detect_assistant_intent_no_files(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test assistant intent detection without file names."""
        # Mock LLM response
        mock_invoke_llm.return_value = """{
            "primary_intent": "chatbot",
            "suggestion_type": null,
            "is_multistep": false,
            "steps": [{"action": "chat", "description": "Have a conversation"}],
            "parameters": {},
            "confidence": 0.7,
            "reasoning": "Simple conversational request"
        }"""

        data = {"message": "Tell me about artificial intelligence"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["primary_intent"] == "chatbot"
        assert content["is_multistep"] is False
        assert len(content["steps"]) == 1

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_detect_assistant_intent_llm_error_fallback(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test assistant intent detection with LLM error fallback."""
        # Mock LLM to raise an exception
        mock_invoke_llm.side_effect = Exception("LLM service unavailable")

        data = {"message": "Generate something"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["primary_intent"] == "chatbot"
        assert content["confidence"] == 0.1
        assert "Error in intent detection" in content["reasoning"]

    @patch("app.api.routes.chatbot.invoke_llm")
    def test_detect_assistant_intent_invalid_json_fallback(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test assistant intent detection with invalid JSON response fallback."""
        # Mock LLM to return invalid JSON
        mock_invoke_llm.return_value = "This is not JSON, just plain text response"

        data = {"message": "Do something"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["primary_intent"] == "chatbot"
        assert content["confidence"] == 0.5
        assert "Could not parse LLM response" in content["reasoning"]

    def test_detect_assistant_intent_unauthorized(self, client: TestClient):
        """Test assistant intent detection without authentication."""
        data = {"message": "Generate a report"}

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            json=data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided

    def test_detect_assistant_intent_no_message(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test assistant intent detection without providing a message."""
        data = {"file_names": ["test.pdf"]}

        response = client.post(
            f"{settings.API_V1_STR}/chat/assistant/detect-intent",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 422  # Pydantic validation error
