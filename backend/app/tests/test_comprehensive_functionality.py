import pytest
import json
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.tests.utils.utils import get_superuser_token_headers
from app.main import app
from io import BytesIO


class TestComprehensiveFunctionality:
    """Test all app functionalities across different configurations"""

    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient, superuser_token_headers: dict):
        self.client = client
        self.headers = superuser_token_headers

        # Create test files
        self.test_txt_content = "This is a test document with sample content for testing purposes. It contains key information about testing methodologies and comprehensive analysis."
        self.test_txt = BytesIO(self.test_txt_content.encode())

    def _reset_file_pointer(self):
        """Reset file pointer for reuse"""
        self.test_txt = BytesIO(self.test_txt_content.encode())

    # CHATBOT (ASK) FUNCTIONALITY TESTS

    def test_ask_vector_upload(self):
        """Test ask functionality with vector search and uploaded document"""
        self._reset_file_pointer()
        response = self.client.post(
            "/api/v1/chat/document",
            headers=self.headers,
            data={"question": "What is this document about?", "search_mode": "vector"},
            files={"file": ("test.txt", self.test_txt, "text/plain")},
        )
        # Should succeed or give meaningful error (not 500)
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            result = response.json()
            assert "answer" in result or "response" in result

    def test_ask_full_scan_upload(self):
        """Test ask functionality with full document scan and uploaded document"""
        self._reset_file_pointer()
        response = self.client.post(
            "/api/v1/chat/document",
            headers=self.headers,
            data={
                "question": "What is this document about?",
                "search_mode": "full_scan",
            },
            files={"file": ("test.txt", self.test_txt, "text/plain")},
        )
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            result = response.json()
            assert "answer" in result or "response" in result

    # VERADOC (REVIEW) FUNCTIONALITY TESTS

    def test_review_vector_upload_main_functionality(self):
        """Test review functionality with vector search and uploaded document"""
        self._reset_file_pointer()
        response = self.client.post(
            "/api/v1/veradoc/process-rag",
            headers=self.headers,
            data={
                "questions": "What are the key findings?\nWhat evidence supports the conclusions?",
                "search_mode": "vector",
            },
            files={"files": ("test.txt", self.test_txt, "text/plain")},
        )
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            result = response.json()
            assert "results" in result

    # TWINCHECK (COMPARE) FUNCTIONALITY TESTS

    def test_compare_vector_upload_main_functionality(self):
        """Test compare functionality with vector search and uploaded documents"""
        self._reset_file_pointer()
        file1 = self.test_txt
        file2 = BytesIO(
            "This is a second test document with different content for comparison purposes.".encode()
        )

        response = self.client.post(
            "/api/v1/twincheck/compare",
            headers=self.headers,
            data={
                "comparison_topics": "Content accuracy\nStructural differences\nKey themes",
                "search_mode": "vector",
            },
            files=[
                ("document1", ("doc1.txt", file1, "text/plain")),
                ("document2", ("doc2.txt", file2, "text/plain")),
            ],
        )
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            result = response.json()
            assert "results" in result or "comparison" in result

    # FORMCONNECT (MATCH) FUNCTIONALITY TESTS

    def test_match_vector_upload_main_functionality(self):
        """Test match functionality with vector search and uploaded document"""
        form_content = BytesIO(
            "Name: John Doe\nAge: 30\nAddress: 123 Main St\nPhone: 555-0123\nEmail: john@example.com".encode()
        )

        response = self.client.post(
            "/api/v1/formconnect/process",
            headers=self.headers,
            data={
                "fields": "Full Name\nAge\nAddress\nPhone Number\nEmail Address",
                "search_mode": "vector",
            },
            files={"digitized_files": ("form.txt", form_content, "text/plain")},
        )
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            result = response.json()
            assert "results" in result or "extracted_data" in result

    # PARAMETRIC TESTS FOR CRITICAL COMBINATIONS

    @pytest.mark.parametrize("search_mode", ["vector", "full_scan"])
    def test_ask_search_modes(self, search_mode):
        """Test ask functionality with different search modes"""
        self._reset_file_pointer()

        response = self.client.post(
            "/api/v1/chat/document",
            headers=self.headers,
            data={
                "question": f"Test question with {search_mode} mode",
                "search_mode": search_mode,
            },
            files={"file": ("test.txt", self.test_txt, "text/plain")},
        )

        # Should succeed or give meaningful error (not 500)
        assert response.status_code in [
            200,
            422,
            400,
        ], f"Failed ask with {search_mode}: {response.status_code}, {response.text}"

    def test_health_check(self):
        """Test that the API is responsive"""
        response = self.client.get("/health")
        assert response.status_code == 200

    def test_api_docs_accessible(self):
        """Test that API documentation is accessible"""
        response = self.client.get("/docs")
        assert response.status_code == 200
