"""
Tests for request size limit middleware.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.request_size_limit import RequestSizeLimitMiddleware


class TestRequestSizeLimitMiddleware:
    """Test request size limit functionality."""

    @pytest.fixture
    def app_with_middleware(self):
        """Create a test app with the request size limit middleware."""
        app = FastAPI()

        # Add the middleware with a small limit for testing
        app.add_middleware(RequestSizeLimitMiddleware, max_size=1024)  # 1KB limit

        @app.post("/test")
        async def test_endpoint():
            return JSONResponse(content={"message": "success"})

        return app

    @pytest.fixture
    def client(self, app_with_middleware):
        """Create a test client."""
        return TestClient(app_with_middleware)

    def test_small_request_allowed(self, client):
        """Test that small requests are allowed through."""
        # Small payload should be allowed
        response = client.post("/test", json={"data": "small"})
        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_large_request_blocked(self, client):
        """Test that large requests are blocked."""
        # Create a large payload that exceeds the 1KB limit
        large_data = {"data": "x" * 2000}  # This will be > 1KB when JSON encoded

        response = client.post("/test", json=large_data)
        assert response.status_code == 413
        assert response.text == "Request too large"

    def test_request_without_content_length_allowed(self, client):
        """Test that requests without Content-Length header are allowed."""
        # GET requests typically don't have Content-Length
        response = client.get("/test")
        # This will fail because we only have a POST endpoint, but the middleware should pass it through
        assert response.status_code == 405  # Method not allowed, not 413

    def test_invalid_content_length_allowed(self, client):
        """Test that invalid Content-Length headers are allowed through."""
        # The middleware should handle invalid content-length gracefully
        response = client.post(
            "/test",
            json={"data": "test"},
            headers={"Content-Length": "invalid"}
        )
        assert response.status_code == 200  # Should pass through despite invalid header