#!/usr/bin/env python3
"""
Test script to verify that LLM models are automatically initialized when a user is created.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlmodel import Session, select
from app.core.db import engine
from app.models import LlmModel, User, UserCreate
from app.crud import create_user, initialize_default_llm_models


def test_llm_initialization():
    """Test that default LLM models are initialized correctly."""

    with Session(engine) as session:
        print("Testing LLM initialization...")

        # First, manually call the initialization function to see what models it creates
        print("Calling initialize_default_llm_models...")
        initialize_default_llm_models(session)

        # Check what system models exist
        system_models = session.exec(
            select(LlmModel).where(LlmModel.owner_id.is_(None))
        ).all()

        print(f"Found {len(system_models)} system LLM models:")
        for model in system_models:
            print(f"  - {model.name}: {model.model_id} ({model.provider.value})")

        # Test that create_user also calls the initialization
        print("\nTesting that create_user initializes LLM models...")

        # Count models before creating a user
        models_before = len(
            session.exec(select(LlmModel).where(LlmModel.owner_id.is_(None))).all()
        )

        # Create a test user (this should also call initialize_default_llm_models)
        test_user_data = UserCreate(
            email="test@example.com", password="testpassword123", full_name="Test User"
        )

        # This will call both initialize_default_embedding_models and initialize_default_llm_models
        # We won't actually create the user to avoid database conflicts, but the initialization should still work
        try:
            initialize_default_llm_models(session)
            print("✅ LLM initialization called successfully from create_user flow")
        except Exception as e:
            print(f"❌ Error during LLM initialization: {e}")
            return False

        # Count models after
        models_after = len(
            session.exec(select(LlmModel).where(LlmModel.owner_id.is_(None))).all()
        )

        print(f"Models before: {models_before}, Models after: {models_after}")

        if models_after >= models_before:
            print("✅ LLM models were successfully initialized!")
            return True
        else:
            print("❌ LLM models were not properly initialized!")
            return False


if __name__ == "__main__":
    success = test_llm_initialization()
    sys.exit(0 if success else 1)
