#!/usr/bin/env python3
"""Check available embedding models in the database."""

import sys
import os

sys.path.append(".")

from app.main import app
from app.core.db import engine
from sqlmodel import Session, select
from app.models import EmbeddingModel
from app.core.config import settings

if __name__ == "__main__":
    session = Session(engine)

    # Get all system embedding models
    models = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
    ).all()

    print("=== Available System Embedding Models ===")
    for model in models:
        print(f"- {model.model_id} ({model.provider.value})")

    print(f"\n=== Configuration ===")
    print(f"ENABLE_MODEL_SELECTION: {settings.ENABLE_MODEL_SELECTION}")
    print(f"FORCE_DEFAULT_EMBEDDING: {settings.FORCE_DEFAULT_EMBEDDING}")
    print(f"Enabled embedding providers: {settings.embedding_providers}")

    print(f"\n=== Looking for target model ===")
    target_found = False
    for model in models:
        if model.model_id == settings.FORCE_DEFAULT_EMBEDDING:
            print(f"✓ Found target model: {model.model_id} ({model.provider.value})")
            if model.provider.value.lower() in settings.embedding_providers:
                print(f"✓ Provider '{model.provider.value}' is enabled")
                target_found = True
            else:
                print(f"✗ Provider '{model.provider.value}' is NOT enabled")
                print(f"  Enabled providers: {settings.embedding_providers}")
            break

    if not target_found:
        print(
            f"✗ Target model '{settings.FORCE_DEFAULT_EMBEDDING}' not found or provider not enabled"
        )
        print("Available models with enabled providers:")
        for model in models:
            if model.provider.value.lower() in settings.embedding_providers:
                print(f"  - {model.model_id} ({model.provider.value})")

    session.close()
