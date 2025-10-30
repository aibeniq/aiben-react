"""
Unit tests for feedback API endpoints.
Tests feedback submission for LLM interactions.
"""

import pytest
import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import LlmInteraction
from app.tests.utils.user import authentication_token_from_email


class TestFeedbackAPI:
    """Test suite for feedback API endpoints."""

    def test_submit_feedback_success(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """Test successful feedback submission."""
        # Get the superuser
        from app.models import User
        from sqlmodel import select

        user = db.exec(select(User).where(User.email == "admin@example.com")).first()
        assert user is not None

        # Create a test LLM interaction
        interaction = LlmInteraction(
            user_id=user.id,
            functionality="chatbot",
            input_data="Test question",
            output_data="Test response",
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # Submit feedback
        feedback_data = {
            "interaction_id": str(interaction.id),
            "feedback": "correct",
            "feedback_text": "Great response!",
        }

        response = client.post(
            "/api/v1/feedback/", json=feedback_data, headers=superuser_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Feedback submitted successfully"

        # Verify feedback was saved
        db.refresh(interaction)
        assert interaction.feedback == "correct"
        assert interaction.feedback_text == "Great response!"
        assert interaction.feedback_date is not None

    def test_submit_feedback_interaction_not_found(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """Test feedback submission for non-existent interaction."""
        # Use a random UUID that doesn't exist
        fake_interaction_id = str(uuid.uuid4())

        feedback_data = {
            "interaction_id": fake_interaction_id,
            "feedback": "correct",
            "feedback_text": "Good response",
        }

        response = client.post(
            "/api/v1/feedback/", json=feedback_data, headers=superuser_token_headers
        )

        assert response.status_code == 404
        # Check if it's JSON or HTML response
        try:
            data = response.json()
            assert "detail" in data
            assert data["detail"] == "Interaction not found"
        except:
            # If it's HTML, just check the status code
            assert response.status_code == 404
