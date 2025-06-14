"""
Configuration settings for Vector Database Service
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Dict


class VectorDBSettings(BaseSettings):
    """Vector Database configuration settings"""

    # Weaviate Configuration
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    weaviate_api_key: str = Field(default="", env="WEAVIATE_API_KEY")
    weaviate_timeout: int = Field(default=60, env="WEAVIATE_TIMEOUT")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(
        default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL"
    )

    # Chunking Configuration
    default_chunk_size: int = Field(default=1000, env="DEFAULT_CHUNK_SIZE")
    default_chunk_overlap: int = Field(default=200, env="DEFAULT_CHUNK_OVERLAP")
    max_chunk_size: int = Field(default=8000, env="MAX_CHUNK_SIZE")

    # Batch Processing
    batch_size: int = Field(default=50, env="BATCH_SIZE")
    max_concurrent_embeddings: int = Field(default=10, env="MAX_CONCURRENT_EMBEDDINGS")

    # Search Configuration
    default_search_limit: int = Field(default=10, env="DEFAULT_SEARCH_LIMIT")
    max_search_limit: int = Field(default=100, env="MAX_SEARCH_LIMIT")
    default_hybrid_alpha: float = Field(default=0.5, env="DEFAULT_HYBRID_ALPHA")

    # Collection Management
    collection_prefix: str = Field(default="org", env="COLLECTION_PREFIX")
    auto_create_collections: bool = Field(default=True, env="AUTO_CREATE_COLLECTIONS")

    # Security
    enable_access_control: bool = Field(default=True, env="ENABLE_ACCESS_CONTROL")
    default_user_access: bool = Field(default=False, env="DEFAULT_USER_ACCESS")

    # Performance
    connection_pool_size: int = Field(default=10, env="CONNECTION_POOL_SIZE")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = VectorDBSettings()

# Supported embedding models configuration
SUPPORTED_EMBEDDING_MODELS = {
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
    "custom": {
        "provider": "custom",
        "dimensions": None,  # Will be determined at runtime
        "max_tokens": None,
        "cost_per_1k": 0,
    },
}


def get_model_config(model_name: str) -> Dict:
    """Get configuration for a specific embedding model"""
    return SUPPORTED_EMBEDDING_MODELS.get(
        model_name, SUPPORTED_EMBEDDING_MODELS["custom"]
    )


def validate_model_support(model_name: str) -> bool:
    """Check if an embedding model is supported"""
    return model_name in SUPPORTED_EMBEDDING_MODELS
