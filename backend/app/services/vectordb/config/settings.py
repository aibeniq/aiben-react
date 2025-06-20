"""
Configuration settings for Vector Database Service
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Weaviate settings
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", None)

# Model configurations
MODEL_CONFIGS = {
    "text-embedding-3-small": {
        "provider": "openai",
        "dimensions": 1536,
        "max_tokens": 8191,
        "cost_per_1k": 0.00002,
    },
    "text-embedding-3-large": {
        "provider": "openai",
        "dimensions": 3072,
        "max_tokens": 8191,
        "cost_per_1k": 0.00013,
    },
    "text-embedding-ada-002": {
        "provider": "openai",
        "dimensions": 1536,
        "max_tokens": 8191,
        "cost_per_1k": 0.0001,
    },
}

SUPPORTED_EMBEDDING_MODELS = list(MODEL_CONFIGS.keys())

# Chunking settings
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# Performance settings
BATCH_SIZE = 100
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Access control settings
DEFAULT_ACCESS_USERS = ["*"]  # Allow access to all users by default


def get_model_config(model_name: str) -> Dict:
    """Get configuration for a specific embedding model"""
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Unsupported embedding model: {model_name}")
    return MODEL_CONFIGS[model_name]


def validate_model_support(model_name: str) -> bool:
    """Validate if a model is supported"""
    return model_name in SUPPORTED_EMBEDDING_MODELS


def get_default_embedding_model() -> str:
    """Get the default embedding model"""
    return SUPPORTED_EMBEDDING_MODELS[0]


def get_chunking_settings(
    chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None
) -> Dict:
    """Get chunking settings with defaults"""
    return {
        "chunk_size": chunk_size or DEFAULT_CHUNK_SIZE,
        "chunk_overlap": chunk_overlap or DEFAULT_CHUNK_OVERLAP,
    }


def get_batch_settings() -> Dict:
    """Get batch processing settings"""
    return {
        "batch_size": BATCH_SIZE,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
    }
