"""
API tests for TwinCheck endpoints.
Tests document comparison, CRUD operations, topic generation, and history functionalities.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from sqlmodel import Session
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.models import KnowledgeBase, Source, SourceData, TwinCheckTopicList, User


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing."""
    # Create a minimal PDF-like content for testing
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n72 720 Td\n/F0 12 Tf\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000200 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n284\n%%EOF"


@pytest.fixture
def sample_comparison_data():
    """Sample comparison data for testing."""
    import json

    return {
        "name": "Test Comparison",
        "description": "A test comparison for API testing",
        "topics": json.dumps(
            [
                {
                    "topic": "Topic 1",
                    "similarity": 0.8,
                    "differences": ["Difference 1"],
                },
                {
                    "topic": "Topic 2",
                    "similarity": 0.6,
                    "differences": ["Difference 2"],
                },
            ]
        ),
    }


@pytest.fixture
def sample_compare_request():
    """Sample document comparison request data."""
    return {
        "documents": [
            {"content": "Document 1 content", "filename": "doc1.pdf"},
            {"content": "Document 2 content", "filename": "doc2.pdf"},
        ],
        "comparison_type": "detailed",
        "focus_areas": ["content", "structure"],
    }


class TestTwinCheckCompare:
    """Test suite for TwinCheck comparison functionality."""

    @patch("app.api.routes.twincheck.progress_tracker")
    @patch("app.api.routes.twincheck.invoke_llm_async")
    @pytest.mark.asyncio
    async def test_compare_documents_success(
        self,
        mock_invoke_llm,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_pdf_bytes,
    ):
        """Test successful document comparison."""
        # Mock LLM response
        mock_invoke_llm.return_value = {
            "comparison_result": "Documents compared successfully",
            "similarities": ["Similar content found"],
            "differences": ["Different content found"],
        }

        # Mock progress tracker
        mock_progress_tracker.get_progress.return_value = {
            "status": "completed",
            "progress": 100,
            "message": "Comparison completed",
        }

        # Prepare form data as expected by the endpoint
        files = {
            "document1": ("doc1.pdf", BytesIO(sample_pdf_bytes), "application/pdf"),
            "document2": ("doc2.pdf", BytesIO(sample_pdf_bytes), "application/pdf"),
        }
        data = {
            "comparison_topics": "content similarity, structural differences",
            "topic_list_name": "Test Comparison",
        }

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/compare",
            headers=superuser_token_headers,
            files=files,
            data=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "results" in content
        assert "interaction_id" in content["results"]
        assert "summary" in content["results"]
        assert "topic_analysis" in content["results"]

    @patch("app.api.routes.twincheck.progress_tracker")
    def test_create_optimize_outline_task_success(
        self,
        mock_progress_tracker,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful creation of optimize outline task."""
        # Mock progress tracker
        mock_progress_tracker.create_task.return_value = "test_task_456"

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/optimize-outline/task",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert "task_id" in content
        assert content["task_id"] == "test_task_456"

    def test_get_progress_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test getting progress for a task."""
        # Mock the progress tracker directly in the route
        with patch("app.api.routes.twincheck.progress_tracker") as mock_tracker:
            mock_tracker.get_progress.return_value = {
                "status": "running",
                "progress": 75,
                "message": "Comparing documents",
            }

            response = client.get(
                f"{settings.API_V1_STR}/twincheck/progress/test_task_456",
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            content = response.json()
            assert content["status"] == "running"
            assert content["progress"] == 75

    def test_compare_documents_unauthorized(
        self, client: TestClient, sample_compare_request
    ):
        """Test document comparison without authentication."""
        response = client.post(
            f"{settings.API_V1_STR}/twincheck/compare",
            json=sample_compare_request,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided

    def test_compare_documents_invalid_data(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test document comparison with invalid data."""
        invalid_request = {"invalid": "data"}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/compare",
            headers=superuser_token_headers,
            json=invalid_request,
        )

        assert response.status_code == 422  # Pydantic validation error


class TestTwinCheckComparisons:
    """Test suite for TwinCheck comparisons CRUD operations."""

    def test_create_comparison_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_comparison_data,
        db: Session,
        test_superuser,
    ):
        """Test successful comparison creation."""
        # Add owner_id to the test data
        test_data = sample_comparison_data.copy()
        test_data["owner_id"] = str(test_superuser.id)

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/comparisons",
            headers=superuser_token_headers,
            json=test_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == "Test Comparison"
        assert content["description"] == "A test comparison for API testing"
        # Topics are returned as JSON string, parse to check length
        import json

        topics_list = json.loads(content["topics"])
        assert len(topics_list) == 2

    def test_get_comparisons_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_comparison_data,
        db: Session,
        test_superuser,
    ):
        """Test getting all comparisons."""
        # Create a test comparison first
        test_data = sample_comparison_data.copy()
        test_data["owner_id"] = test_superuser.id
        comparison = TwinCheckTopicList(**test_data)
        db.add(comparison)
        db.commit()
        db.refresh(comparison)

        response = client.get(
            f"{settings.API_V1_STR}/twincheck/comparisons",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)
        assert len(content) >= 1

    def test_get_comparison_by_id_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_comparison_data,
        db: Session,
        test_superuser,
    ):
        """Test getting a specific comparison by ID."""
        # Create a test comparison first
        test_data = sample_comparison_data.copy()
        test_data["owner_id"] = test_superuser.id
        comparison = TwinCheckTopicList(**test_data)
        db.add(comparison)
        db.commit()
        db.refresh(comparison)

        response = client.get(
            f"{settings.API_V1_STR}/twincheck/comparisons/{comparison.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["id"] == str(comparison.id)
        assert content["name"] == "Test Comparison"

    def test_update_comparison_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_comparison_data,
        db: Session,
        test_superuser,
    ):
        """Test successful comparison update."""
        # Create a test comparison first
        test_data = sample_comparison_data.copy()
        test_data["owner_id"] = test_superuser.id
        comparison = TwinCheckTopicList(**test_data)
        db.add(comparison)
        db.commit()
        db.refresh(comparison)

        update_data = {
            "name": "Updated Test Comparison",
            "description": "Updated description",
            "topics": sample_comparison_data["topics"],
        }

        response = client.put(
            f"{settings.API_V1_STR}/twincheck/comparisons/{comparison.id}",
            headers=superuser_token_headers,
            json=update_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["name"] == "Updated Test Comparison"
        assert content["description"] == "Updated description"

    def test_delete_comparison_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        sample_comparison_data,
        db: Session,
        test_superuser,
    ):
        """Test successful comparison deletion."""
        # Create a test comparison first
        test_data = sample_comparison_data.copy()
        test_data["owner_id"] = test_superuser.id
        comparison = TwinCheckTopicList(**test_data)
        db.add(comparison)
        db.commit()
        db.refresh(comparison)

        response = client.delete(
            f"{settings.API_V1_STR}/twincheck/comparisons/{comparison.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert "message" in content

    def test_get_comparison_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test getting a non-existent comparison."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client.get(
            f"{settings.API_V1_STR}/twincheck/comparisons/{fake_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404

    def test_comparisons_unauthorized(self, client: TestClient):
        """Test comparisons endpoints without authentication."""
        response = client.get(f"{settings.API_V1_STR}/twincheck/comparisons")

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestTwinCheckHistory:
    """Test suite for TwinCheck history functionality."""

    def test_get_history_success(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test getting comparison history."""
        response = client.get(
            f"{settings.API_V1_STR}/twincheck/history",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert isinstance(content, list)

    def test_get_history_detail_success(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test getting detailed history for a specific comparison."""
        # Use a valid UUID format
        import uuid

        fake_comparison_id = str(uuid.uuid4())

        response = client.get(
            f"{settings.API_V1_STR}/twincheck/history/{fake_comparison_id}",
            headers=superuser_token_headers,
        )

        # This should return 404 for non-existent comparison
        assert response.status_code == 404

    def test_history_unauthorized(self, client: TestClient):
        """Test history endpoints without authentication."""
        response = client.get(f"{settings.API_V1_STR}/twincheck/history")

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestTwinCheckGenerateTopics:
    """Test suite for TwinCheck topic generation functionality."""

    @patch("app.api.routes.twincheck.invoke_llm_async")
    @pytest.mark.asyncio
    async def test_generate_topics_success(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful topic generation."""
        # Mock LLM response with expected format
        mock_invoke_llm.return_value = """TOPICS:
1. Content Similarity
2. Structural Differences

ANALYSIS:
These topics are commonly used for document comparison."""

        # Send form data as expected by the endpoint
        data = {
            "description": "Generate topics for document comparison",
            "comparison_type": "general",
            "num_topics": 2,
        }

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate-topics",
            headers=superuser_token_headers,
            data=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "topics" in content
        assert len(content["topics"]) == 2

    @patch("app.api.routes.twincheck.invoke_llm_async")
    @pytest.mark.asyncio
    async def test_generate_topics_json_success(
        self,
        mock_invoke_llm,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful topic generation with JSON response."""
        # Mock LLM response with valid JSON
        mock_invoke_llm.return_value = """{
            "topics": [
                {"topic": "Advanced Topic", "description": "Complex topic"}
            ]
        }"""

        request_data = {"documents": ["Advanced document content"], "topic_count": 1}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate-topics-json",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "topics" in content

    def test_generate_topics_unauthorized(self, client: TestClient):
        """Test topic generation without authentication."""
        request_data = {"documents": ["Test document"], "topic_count": 1}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate-topics",
            json=request_data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided

    def test_generate_topics_invalid_request(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ):
        """Test topic generation with invalid request data."""
        invalid_request = {"invalid": "data"}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate-topics",
            headers=superuser_token_headers,
            json=invalid_request,
        )

        assert response.status_code == 422  # Pydantic validation error


class TestTwinCheckGenerateDocx:
    """Test suite for TwinCheck DOCX generation functionality."""

    def test_generate_docx_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful DOCX generation."""
        request_data = {
            "content": "# Test Comparison Report\n\nThis is a test comparison report content.",
            "title": "Test Comparison",
            "language": "en",
        }

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate/docx",
            headers=superuser_token_headers,
            json=request_data,
        )

        # Should return a streaming response
        assert response.status_code == 200
        assert (
            response.headers.get("content-type")
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_generate_docx_unauthorized(
        self, client: TestClient, sample_comparison_data
    ):
        """Test DOCX generation without authentication."""
        request_data = {"comparison_data": sample_comparison_data}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate/docx",
            json=request_data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided


class TestTwinCheckGenerateCsv:
    """Test suite for TwinCheck CSV generation functionality."""

    def test_generate_csv_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ):
        """Test successful CSV generation."""
        request_data = {
            "content": '{"summary": "Test comparison summary", "topic_results": [{"topic": "Test Topic", "similarity": 0.8}]}',
            "title": "Test Comparison",
            "language": "en",
        }

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate/csv",
            headers=superuser_token_headers,
            json=request_data,
        )

        # Should return a streaming response
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    def test_generate_csv_unauthorized(
        self, client: TestClient, sample_comparison_data
    ):
        """Test CSV generation without authentication."""
        request_data = {"comparison_data": sample_comparison_data}

        response = client.post(
            f"{settings.API_V1_STR}/twincheck/generate/csv",
            json=request_data,
        )

        assert response.status_code == 401  # Unauthorized when no auth provided
