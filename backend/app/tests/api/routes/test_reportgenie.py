"""
API tests for ReportGenie endpoints.
Tests generate, suggest outline, and optimize outline functionalities with both vector search and full document scan modes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from sqlmodel import Session
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.models import KnowledgeBase, Source, SourceData, ReportGenieOutline, User


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Create a minimal PDF-like content for testing
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"


@pytest.fixture
def sample_outline_data():
    """Sample outline data for testing."""
    import json

    return {
        "name": "Test Outline",
        "description": "A test outline for API testing",
        "sections": json.dumps(
            [
                {"title": "Introduction", "description": "Introduction section"},
                {"title": "Main Content", "description": "Main content section"},
                {"title": "Conclusion", "description": "Conclusion section"},
            ]
        ),
    }


class TestReportGenieGenerate:
    """Test suite for ReportGenie generate functionality."""

    @patch("app.api.routes.reportgenie.KnowledgeBaseCache.get_retriever")
    @patch("app.api.routes.reportgenie.get_default_llm")
    @patch("app.api.routes.reportgenie.progress_tracker")
    @patch("app.api.routes.reportgenie.invoke_llm")
    def test_generate_report_vector_search_success(
        self,
        mock_invoke_llm,
        mock_progress_tracker,
        mock_get_default_llm,
        mock_get_retriever,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
        db: Session,
    ):
        """Test successful report generation with vector search mode."""
        # Mock LLM response
        mock_invoke_llm.return_value = "Generated report content based on sections."

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock LLM
        mock_llm = Mock()
        mock_get_default_llm.return_value = mock_llm

        # Mock retriever
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [
            Mock(
                page_content="Relevant document content",
                metadata={"source": "test.pdf"},
            )
        ]
        mock_get_retriever.return_value = mock_retriever

        # Create test source data
        import hashlib

        file_hash = hashlib.sha256(sample_pdf_bytes).hexdigest()
        source_data = SourceData(
            data=sample_pdf_bytes, file_hash=file_hash, content_type="application/pdf"
        )
        db.add(source_data)
        db.commit()

        # Create test source
        source = Source(
            name="test_document.pdf",
            source_data_id=source_data.id,
            knowledge_base_id=test_knowledge_base.id,
            owner_id=test_knowledge_base.owner_id,
        )
        db.add(source)
        db.commit()

        data = {
            "knowledge_base_id": str(test_knowledge_base.id),
            "sections": '[{"text": "Introduction section to generate", "consultDocuments": true}, {"text": "Conclusion section to generate", "consultDocuments": true}]',
            "outline_id": "",
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "results" in content
        assert "task_id" in content["results"]
        assert content["results"]["task_id"] == "test-task-id"

    @patch("app.api.routes.reportgenie.progress_tracker")
    def test_generate_report_missing_knowledge_base(
        self,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test report generation with missing knowledge base ID."""
        data = {
            "sections": '[{"title": "Introduction", "content": "Intro content"}]',
            "outline_id": "test-outline-id",
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 422  # Pydantic validation error

    @patch("app.api.routes.reportgenie.KnowledgeBaseCache.get_retriever")
    @patch("app.api.routes.reportgenie.get_default_llm")
    @patch("app.api.routes.reportgenie.progress_tracker")
    @patch("app.api.routes.reportgenie.invoke_llm")
    def test_generate_report_invalid_search_mode(
        self,
        mock_invoke_llm,
        mock_progress_tracker,
        mock_get_default_llm,
        mock_get_retriever,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
    ):
        """Test report generation with invalid search mode."""
        # Mock LLM response
        mock_invoke_llm.return_value = "Generated report content based on sections."

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock LLM
        mock_llm = Mock()
        mock_get_default_llm.return_value = mock_llm

        # Mock retriever
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [
            Mock(
                page_content="Relevant document content",
                metadata={"source": "test.pdf"},
            )
        ]
        mock_get_retriever.return_value = mock_retriever

        data = {
            "knowledge_base_id": str(test_knowledge_base.id),
            "sections": '[{"title": "Introduction", "content": "Intro content"}]',
            "outline_id": "",
            "search_mode": "invalid_mode",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate",
            headers=superuser_token_headers,
            data=data,
        )

        # Should still work but may default to vector search
        assert response.status_code == 200

    def test_generate_report_unauthorized(
        self, client: TestClient, test_knowledge_base
    ):
        """Test report generation without authentication."""
        data = {
            "knowledge_base_id": str(test_knowledge_base.id),
            "sections": '[{"title": "Introduction", "content": "Intro content"}]',
            "outline_id": "test-outline-id",
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate",
            data=data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestReportGenieOutline:
    """Test suite for ReportGenie outline management."""

    def test_create_outline_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_outline_data,
        db: Session,
    ):
        """Test successful outline creation."""
        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
            json=sample_outline_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == sample_outline_data["name"]
        assert content["description"] == sample_outline_data["description"]
        assert content["sections"] == sample_outline_data["sections"]

    def test_get_outlines_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_outline_data,
        db: Session,
    ):
        """Test successful retrieval of outlines."""
        # Create an outline first
        client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
            json=sample_outline_data,
        )

        response = client.get(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)
        assert len(content) >= 1
        assert content[0]["name"] == sample_outline_data["name"]

    def test_get_outline_by_id_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_outline_data,
        db: Session,
    ):
        """Test successful retrieval of specific outline."""
        # Create an outline first
        create_response = client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
            json=sample_outline_data,
        )
        outline_id = create_response.json()["id"]

        response = client.get(
            f"{settings.API_V1_STR}/reportgenie/outlines/{outline_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == sample_outline_data["name"]
        assert content["id"] == outline_id

    def test_update_outline_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_outline_data,
        db: Session,
    ):
        """Test successful outline update."""
        # Create an outline first
        create_response = client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
            json=sample_outline_data,
        )
        outline_id = create_response.json()["id"]

        # Update the outline
        updated_data = sample_outline_data.copy()
        updated_data["name"] = "Updated Test Outline"
        updated_data["description"] = "Updated description"

        response = client.put(
            f"{settings.API_V1_STR}/reportgenie/outlines/{outline_id}",
            headers=superuser_token_headers,
            json=updated_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == "Updated Test Outline"
        assert content["description"] == "Updated description"

    def test_delete_outline_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_outline_data,
        db: Session,
    ):
        """Test successful outline deletion."""
        # Create an outline first
        create_response = client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            headers=superuser_token_headers,
            json=sample_outline_data,
        )
        outline_id = create_response.json()["id"]

        # Delete the outline
        response = client.delete(
            f"{settings.API_V1_STR}/reportgenie/outlines/{outline_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/reportgenie/outlines/{outline_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404

    def test_outline_operations_unauthorized(
        self, client: TestClient, sample_outline_data
    ):
        """Test outline operations without authentication."""
        # Test create
        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/outlines",
            json=sample_outline_data,
        )
        assert response.status_code == 401

        # Test get
        response = client.get(f"{settings.API_V1_STR}/reportgenie/outlines")
        assert response.status_code == 401


class TestReportGenieSuggestOutline:
    """Test suite for ReportGenie suggest outline functionality."""

    @patch("app.api.routes.reportgenie.get_default_llm")
    @patch("app.api.routes.reportgenie.progress_tracker")
    @patch("app.api.routes.reportgenie.invoke_llm")
    @patch("app.services.document_utils.extract_text_with_vision_enhancement")
    @patch("app.api.routes.reportgenie.extract_text_from_file")
    def test_generate_outline_success(
        self,
        mock_extract_text_from_file,
        mock_extract_text,
        mock_invoke_llm,
        mock_progress_tracker,
        mock_get_default_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test successful outline generation."""
        # Mock LLM response
        mock_invoke_llm.return_value = """SECTIONS:
1. Introduction: This section provides an overview of the business report, including the purpose, scope, and methodology used in preparing the document.
2. Executive Summary: A concise summary of the key findings, conclusions, and recommendations presented in the business report.
3. Conclusion: This final section summarizes the main points discussed throughout the report and provides final thoughts or recommendations.

ANALYSIS:
Generated 3 sections based on the business report description to ensure comprehensive coverage of essential report components."""

        # Mock file extraction
        mock_extract_text.return_value = (
            "Sample document content for outline generation"
        )
        mock_extract_text_from_file.return_value = "Ground truth document content"

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock LLM
        mock_llm = Mock()
        mock_get_default_llm.return_value = mock_llm

        # Create test file
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "description": "Generate an outline for a business report",
            "report_type": "business",
            "num_sections": 3,
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate-outline",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        content = response.json()
        assert "sections" in content
        assert "description_analysis" in content

    @patch("app.api.routes.reportgenie.progress_tracker")
    def test_generate_outline_missing_description(
        self,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test outline generation with missing description."""
        data = {"report_type": "business", "num_sections": 3}

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate-outline",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_generate_outline_unauthorized(self, client: TestClient):
        """Test outline generation without authentication."""
        data = {
            "description": "Generate an outline for a business report",
            "report_type": "business",
            "num_sections": 3,
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/generate-outline",
            data=data,
        )

        assert response.status_code == 401


class TestReportGenieOptimizeOutline:
    """Test suite for ReportGenie optimize outline functionality."""

    @patch("app.api.routes.reportgenie.KnowledgeBaseCache.get_retriever")
    @patch("app.api.routes.reportgenie.get_default_llm")
    @patch("app.api.routes.reportgenie.progress_tracker")
    @patch("app.api.routes.reportgenie.invoke_llm")
    @patch("app.services.document_utils.extract_text_with_vision_enhancement")
    @patch("app.api.routes.reportgenie.Chroma")
    @patch("app.api.routes.reportgenie.load_embeddings_model")
    @patch("app.api.routes.reportgenie.create_ensemble_retriever")
    @patch("app.api.routes.reportgenie.extract_text_from_file")
    @patch("sqlmodel.Session.get")
    @patch("zipfile.ZipFile")
    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely_sync")
    def test_optimize_outline_success(
        self,
        mock_execute_llm,
        mock_zipfile,
        mock_session_get,
        mock_extract_text_from_file,
        mock_create_retriever,
        mock_load_embeddings,
        mock_chroma,
        mock_extract_text,
        mock_invoke_llm,
        mock_progress_tracker,
        mock_get_default_llm,
        mock_get_retriever,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
        db: Session,
    ):
        """Test successful outline optimization."""
        # Create mock knowledge base with data
        mock_kb = Mock()
        mock_kb.id = test_knowledge_base.id
        mock_kb.data = b"mock vector data"
        mock_kb.storage_type = "database"
        mock_kb.embedding_model_id = None
        mock_session_get.return_value = mock_kb

        # Mock zipfile
        mock_zip_instance = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zipfile.return_value.__exit__.return_value = None
        mock_zip_instance.extractall = Mock()

        # Mock LLM response
        mock_invoke_llm.return_value = (
            "Optimized outline content based on ground truth document."
        )

        # Mock execute_llm_request_safely_sync to return a response object
        mock_response = Mock()
        mock_response.content = '{"mappings": [{"section_content": "Ground truth document content", "outline_section": 1, "boundary_reasoning": "This content matches the introduction section"}]}'
        mock_response.usage_metadata = Mock()
        mock_response.usage_metadata.total_tokens = 100
        mock_execute_llm.return_value = mock_response

        # Mock file extraction
        mock_extract_text.return_value = (
            "Sample document content for outline generation"
        )
        mock_extract_text_from_file.return_value = "Ground truth document content"

        # Mock vector database components
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance
        mock_load_embeddings.return_value = Mock()
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [
            Mock(
                page_content="Relevant document content",
                metadata={"source": "test.pdf"},
            )
        ]
        mock_create_retriever.return_value = mock_retriever

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock LLM
        mock_llm = Mock()
        mock_get_default_llm.return_value = mock_llm

        # Mock retriever for KnowledgeBaseCache
        mock_kb_retriever = Mock()
        mock_kb_retriever.get_relevant_documents.return_value = [
            Mock(
                page_content="Relevant document content",
                metadata={"source": "test.pdf"},
            )
        ]
        mock_get_retriever.return_value = mock_kb_retriever

        # Create test source data
        import hashlib

        file_hash = hashlib.sha256(sample_pdf_bytes).hexdigest()
        source_data = SourceData(
            data=sample_pdf_bytes, file_hash=file_hash, content_type="application/pdf"
        )
        db.add(source_data)
        db.commit()

        # Create test source
        source = Source(
            name="test_document.pdf",
            source_data_id=source_data.id,
            knowledge_base_id=test_knowledge_base.id,
            owner_id=test_knowledge_base.owner_id,
        )
        db.add(source)
        db.commit()

        # Create test file
        files = {
            "files": ("ground_truth.pdf", BytesIO(sample_pdf_bytes), "application/pdf")
        }

        data = {
            "outline_id": "test-outline-id",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "full_text",
            "sections": '[{"title": "Introduction", "text": "Intro content"}, {"title": "Conclusion", "text": "Conclusion content"}]',
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/optimize-outline",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        content = response.json()
        assert "optimized_sections" in content
        assert "original_sections" in content
        assert "suggestions" in content
        assert "analysis_summary" in content

    @patch("app.api.routes.reportgenie.progress_tracker")
    def test_optimize_outline_missing_outline_id(
        self,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
    ):
        """Test outline optimization with missing outline ID."""
        data = {
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/optimize-outline",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_optimize_outline_unauthorized(
        self, client: TestClient, test_knowledge_base
    ):
        """Test outline optimization without authentication."""
        data = {
            "outline_id": "test-outline-id",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/reportgenie/optimize-outline",
            data=data,
        )

        assert response.status_code == 401
