#!/usr/bin/env python3
"""
Script to fix existing users' embedding models when ENABLE_MODEL_SELECTION is False.
This ensures all users use the configured FORCE_DEFAULT_EMBEDDING model.
"""

import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.core.config import settings
from app.core.db import engine
from app.models import User, EmbeddingModel, ModelProvider


def fix_user_embedding_models():
    """Fix existing users to use the correct default embedding model."""
    
    if settings.ENABLE_MODEL_SELECTION:
        print("Model selection is enabled. No need to fix user embedding models.")
        return
    
    print(f"Model selection is disabled. Forcing all users to use: {settings.FORCE_DEFAULT_EMBEDDING}")
    
    with Session(engine) as session:
        # Get the correct OpenAI embedding model
        openai_model = session.exec(
            select(EmbeddingModel).where(
                EmbeddingModel.owner_id.is_(None),
                EmbeddingModel.model_id == settings.FORCE_DEFAULT_EMBEDDING
            )
        ).first()
        
        if not openai_model:
            print(f"❌ Error: Forced embedding model '{settings.FORCE_DEFAULT_EMBEDDING}' not found in database!")
            print("Available system embedding models:")
            system_models = session.exec(
                select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
            ).all()
            for model in system_models:
                print(f"  - {model.model_id} (provider: {model.provider})")
            return
        
        print(f"✅ Found target embedding model: {openai_model.model_id} (ID: {openai_model.id})")
        
        # Get all users
        users = session.exec(select(User)).all()
        print(f"Found {len(users)} users to update")
        
        updated_count = 0
        for user in users:
            old_model_id = user.default_embedding_model
            
            if old_model_id != openai_model.id:
                # Get old model info for logging
                old_model = None
                if old_model_id:
                    old_model = session.get(EmbeddingModel, old_model_id)
                
                old_model_name = old_model.model_id if old_model else "None"
                
                # Update to correct model
                user.default_embedding_model = openai_model.id
                session.add(user)
                updated_count += 1
                
                print(f"  Updated user {user.email}: {old_model_name} → {openai_model.model_id}")
            else:
                print(f"  User {user.email}: Already using correct model ({openai_model.model_id})")
        
        if updated_count > 0:
            session.commit()
            print(f"✅ Successfully updated {updated_count} users to use {settings.FORCE_DEFAULT_EMBEDDING}")
        else:
            print("✅ All users already using the correct embedding model")


if __name__ == "__main__":
    fix_user_embedding_models()
