"""
API tests for VeraDoc endpoints.
Tests review, checklist, and optimization functionalities with both vector search and full document scan modes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from sqlmodel import Session
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.models import KnowledgeBase, Source, SourceData, VeraDocChecklist, User


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Create a minimal PDF-like content for testing
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"


@pytest.fixture
def sample_checklist_data():
    """Sample checklist data for testing."""
    return {
        "name": "Test Checklist",
        "description": "A test checklist for API testing",
        "questions": [
            "Is the document complete?",
            "Are all sections present?",
            "Is the formatting correct?",
        ],
    }


class TestVeraDocReview:
    """Test suite for VeraDoc review functionality."""

    @patch("app.api.routes.veradoc.progress_tracker")
    @patch("app.api.routes.veradoc.invoke_llm")
    def test_create_review_task_success(
        self,
        mock_invoke_llm,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful creation of review task."""
        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/review/task",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert "task_id" in content
        assert content["task_id"] == "test-task-id"
        mock_progress_tracker.create_task.assert_called_once()

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely")
    @patch("app.api.routes.veradoc.Chroma")
    @patch("app.api.routes.veradoc.zipfile.ZipFile")
    @patch("app.api.routes.veradoc.progress_tracker")
    @patch("app.api.routes.veradoc.invoke_llm_async")
    @patch("app.api.routes.veradoc.SmartRetrieverFactory")
    @patch("app.api.routes.veradoc.extract_text_from_file_async")
    @patch("app.api.routes.veradoc.prefetch_knowledge_base_context")
    @patch("app.api.routes.veradoc.get_default_llm")
    @patch("app.api.routes.veradoc.record_llm_interaction")
    @patch("app.services.vision_service.VisionService.is_vision_enabled")
    def test_process_rag_checklist_vector_search_success(
        self,
        mock_vision_enabled,
        mock_record_interaction,
        mock_get_default_llm,
        mock_prefetch_context,
        mock_extract_text,
        mock_retriever_factory,
        mock_invoke_llm_async,
        mock_progress_tracker,
        mock_zipfile,
        mock_chroma,
        mock_execute_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
        db: Session,
    ):
        """Test successful RAG checklist processing with vector search mode."""
        # Mock LLM response - invoke_llm_async returns a string directly
        mock_invoke_llm_async.return_value = (
            "Analysis complete for checklist questions."
        )

        # Mock execute_llm_request_safely to return a proper result object
        mock_result = Mock()
        mock_result.content = "Analysis complete for checklist questions."
        mock_execute_llm.return_value = mock_result

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock retriever factory
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [
            Mock(page_content="Test document content", metadata={"source": "test.pdf"})
        ]
        mock_retriever_factory.create_academic_paper_retriever.return_value = (
            mock_retriever
        )

        # Mock Chroma database
        mock_chroma_instance = Mock()
        mock_chroma_instance.get.return_value = {
            "documents": ["test doc"],
            "metadatas": [{"source": "test.pdf"}],
            "ids": ["1"],
        }
        mock_chroma.return_value = mock_chroma_instance

        # Mock other dependencies
        mock_extract_text.return_value = "Extracted text from PDF"
        mock_prefetch_context.return_value = {}
        mock_llm = Mock()
        mock_llm.model_name = "gpt-4o-mini"
        mock_get_default_llm.return_value = mock_llm
        mock_record_interaction.return_value = Mock(id="test-interaction-id")
        mock_vision_enabled.return_value = False

        # Mock zipfile
        mock_zipfile.return_value.__enter__.return_value.extractall.return_value = None
        mock_zipfile.return_value.__exit__.return_value = None

        # Create test source data
        source_data = SourceData(
            data=sample_pdf_bytes,
            content_type="application/pdf",
            file_hash="dummy_hash_for_test",
        )
        db.add(source_data)
        db.commit()

        # Set up knowledge base with dummy vector data
        test_knowledge_base.data = b"dummy_vector_data"
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
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "questions": "Is the document complete?\nAre all sections present?",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/process-rag",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        content = response.json()
        assert "results" in content
        assert "filename" in content["results"]

    @patch("app.api.routes.veradoc.progress_tracker")
    def test_process_rag_checklist_missing_knowledge_base(
        self,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test RAG checklist processing with missing knowledge base ID."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {"questions": "Is the document complete?", "search_mode": "vector"}

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/process-rag",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 422  # Pydantic validation error
        content = response.json()
        assert "Field required" in str(content)

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely")
    @patch("app.api.routes.veradoc.Chroma")
    @patch("app.api.routes.veradoc.zipfile.ZipFile")
    @patch("app.api.routes.veradoc.progress_tracker")
    @patch("app.api.routes.veradoc.invoke_llm_async")
    @patch("app.api.routes.veradoc.SmartRetrieverFactory")
    @patch("app.api.routes.veradoc.extract_text_from_file_async")
    @patch("app.api.routes.veradoc.prefetch_knowledge_base_context")
    @patch("app.api.routes.veradoc.get_default_llm")
    @patch("app.api.routes.veradoc.record_llm_interaction")
    @patch("app.services.vision_service.VisionService.is_vision_enabled")
    def test_process_rag_checklist_invalid_search_mode(
        self,
        mock_vision_enabled,
        mock_record_interaction,
        mock_get_default_llm,
        mock_prefetch_context,
        mock_extract_text,
        mock_retriever_factory,
        mock_invoke_llm_async,
        mock_progress_tracker,
        mock_zipfile,
        mock_chroma,
        mock_execute_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
        db: Session,
    ):
        """Test RAG checklist processing with invalid search mode."""
        # Mock LLM response - invoke_llm_async returns a string directly
        mock_invoke_llm_async.return_value = (
            "Analysis complete for checklist questions."
        )

        # Mock execute_llm_request_safely to return a proper result object
        mock_result = Mock()
        mock_result.content = "Analysis complete for checklist questions."
        mock_execute_llm.return_value = mock_result

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock retriever factory
        mock_retriever = Mock()
        mock_retriever.get_relevant_documents.return_value = [
            Mock(page_content="Test document content", metadata={"source": "test.pdf"})
        ]
        mock_retriever_factory.create_academic_paper_retriever.return_value = (
            mock_retriever
        )

        # Mock Chroma database
        mock_chroma_instance = Mock()
        mock_chroma_instance.get.return_value = {
            "documents": ["test doc"],
            "metadatas": [{"source": "test.pdf"}],
            "ids": ["1"],
        }
        mock_chroma.return_value = mock_chroma_instance

        # Mock other dependencies
        mock_extract_text.return_value = "Extracted text from PDF"
        mock_prefetch_context.return_value = {}
        mock_llm = Mock()
        mock_llm.model_name = "gpt-4o-mini"
        mock_get_default_llm.return_value = mock_llm
        mock_record_interaction.return_value = Mock(id="test-interaction-id")
        mock_vision_enabled.return_value = False

        # Mock zipfile
        mock_zipfile.return_value.__enter__.return_value.extractall.return_value = None
        mock_zipfile.return_value.__exit__.return_value = None

        # Create test source data
        source_data = SourceData(
            data=sample_pdf_bytes,
            content_type="application/pdf",
            file_hash="dummy_hash_for_test",
        )
        db.add(source_data)
        db.commit()

        # Set up knowledge base with dummy vector data
        test_knowledge_base.data = b"dummy_vector_data"
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
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "questions": "Is the document complete?\nAre all sections present?",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "invalid_mode",
        }

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/process-rag",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200  # Should process with default mode
        content = response.json()
        assert "results" in content
        assert "filename" in content["results"]

    def test_process_rag_checklist_missing_questions(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
    ):
        """Test RAG checklist processing with missing questions."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/process-rag",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 422  # Pydantic validation error
        content = response.json()
        assert "Field required" in str(
            content
        )  # Should still work but default to vector search
        assert response.status_code == 200

    def test_process_rag_checklist_unauthorized(
        self, client: TestClient, test_knowledge_base, sample_pdf_bytes
    ):
        """Test RAG checklist processing without authentication."""
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "questions": "Is the document complete?",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/process-rag",
            data=data,
            files=files,
        )

        assert (
            response.status_code == 404
        )  # Route not found when no auth in test environment


class TestVeraDocChecklists:
    """Test suite for VeraDoc checklist management."""

    def test_create_checklist_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful checklist creation."""
        response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == sample_checklist_data["name"]
        assert content["description"] == sample_checklist_data["description"]
        # Questions are returned in a specific JSON format from database
        assert (
            content["questions"]
            == '{"Is the document complete?","Are all sections present?","Is the formatting correct?"}'
        )

    def test_create_checklist_duplicate_name(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test checklist creation with duplicate name."""
        # Create first checklist
        client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )

        # Try to create duplicate
        response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )

        assert response.status_code == 400
        content = response.json()
        assert "already exists" in content["detail"]

    def test_get_checklists_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful retrieval of checklists."""
        # Create a checklist first
        client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )

        response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)
        assert len(content) >= 1
        assert content[0]["name"] == sample_checklist_data["name"]

    def test_get_checklist_by_id_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful retrieval of specific checklist."""
        # Create a checklist first
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == sample_checklist_data["name"]
        assert content["id"] == checklist_id

    def test_get_checklist_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test retrieval of non-existent checklist."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists/{fake_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404
        content = response.json()
        assert "Checklist not found" in content["detail"]

    def test_update_checklist_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful checklist update."""
        # Create a checklist first
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        # Update the checklist
        updated_data = sample_checklist_data.copy()
        updated_data["name"] = "Updated Test Checklist"
        updated_data["description"] = "Updated description"

        response = client.put(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
            json=updated_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == "Updated Test Checklist"
        assert content["description"] == "Updated description"

    def test_delete_checklist_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful checklist deletion."""
        # Create a checklist first
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        # Delete the checklist
        response = client.delete(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404

    def test_checklist_operations_unauthorized(
        self, client: TestClient, sample_checklist_data
    ):
        """Test checklist operations without authentication."""
        # Test create
        response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            json=sample_checklist_data,
        )
        assert (
            response.status_code == 404
        )  # Route not found when no auth in test environment

        # Test get
        response = client.get(f"{settings.API_V1_STR}/veradoc/checklists")
        assert (
            response.status_code == 404
        )  # Route not found when no auth in test environment


class TestVeraDocOptimizeChecklist:
    """Test suite for VeraDoc optimize checklist functionality."""

    @patch("app.services.universal_llm_wrapper.execute_llm_request_safely")
    @patch("app.api.routes.veradoc.Chroma")
    @patch("app.api.routes.veradoc.zipfile.ZipFile")
    @patch("app.api.routes.veradoc.progress_tracker")
    @patch("app.api.routes.veradoc.invoke_llm")
    def test_optimize_checklist_success(
        self,
        mock_invoke_llm,
        mock_progress_tracker,
        mock_zipfile,
        mock_chroma,
        mock_execute_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        test_knowledge_base,
        sample_pdf_bytes,
        db: Session,
    ):
        """Test successful checklist optimization."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = (
            '{"optimized_questions": ["Optimized question 1", "Optimized question 2"]}'
        )
        mock_invoke_llm.return_value = mock_response

        # Mock execute_llm_request_safely to return a proper result object
        mock_result = Mock()
        mock_result.content = (
            '{"optimized_questions": ["Optimized question 1", "Optimized question 2"]}'
        )
        mock_execute_llm.return_value = mock_result

        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test-task-id"
        mock_progress_tracker.update_stage_progress.return_value = None
        mock_progress_tracker.complete_stage.return_value = None

        # Mock Chroma database
        mock_chroma_instance = Mock()
        mock_chroma_instance.get.return_value = {
            "documents": ["test doc"],
            "metadatas": [{"source": "test.pdf"}],
            "ids": ["1"],
        }
        mock_chroma.return_value = mock_chroma_instance

        # Mock zipfile
        mock_zipfile.return_value.__enter__.return_value.extractall.return_value = None
        mock_zipfile.return_value.__exit__.return_value = None

        # Create test source data
        source_data = SourceData(
            data=sample_pdf_bytes,
            content_type="application/pdf",
            file_hash="dummy_hash_for_test",
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
        files = {"files": ("test.pdf", BytesIO(sample_pdf_bytes), "application/pdf")}

        data = {
            "questions": "Is the document complete?\nAre all sections present?",
            "knowledge_base_id": str(test_knowledge_base.id),
            "search_mode": "vector",
        }

        response = client.post(
            f"{settings.API_V1_STR}/veradoc/optimize-checklist",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        content = response.json()
        assert "original_questions" in content
        assert "suggestions" in content
        assert "optimized_questions" in content
        assert "analysis_summary" in content
        assert len(content["original_questions"]) == 2  # Two questions provided

    def test_get_checklists_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful retrieval of checklists."""
        # Create a test checklist
        client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )

        response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)
        assert len(content) >= 1

    def test_get_checklist_by_id_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful retrieval of a specific checklist."""
        # Create a test checklist
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == sample_checklist_data["name"]
        assert content["description"] == sample_checklist_data["description"]

    def test_update_checklist_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful checklist update."""
        # Create a test checklist
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        # Update the checklist
        update_data = {
            "name": "Updated Test Checklist",
            "description": "Updated description",
            "questions": ["Updated question 1", "Updated question 2"],
        }

        response = client.put(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
            json=update_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == update_data["name"]
        assert content["description"] == update_data["description"]
        assert content["questions"] == '{"Updated question 1","Updated question 2"}'

    def test_delete_checklist_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_checklist_data,
        db: Session,
    ):
        """Test successful checklist deletion."""
        # Create a test checklist
        create_response = client.post(
            f"{settings.API_V1_STR}/veradoc/checklists",
            headers=superuser_token_headers,
            json=sample_checklist_data,
        )
        checklist_id = create_response.json()["id"]

        # Delete the checklist
        response = client.delete(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/veradoc/checklists/{checklist_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404
