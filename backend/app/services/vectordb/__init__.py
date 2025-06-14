"""
Vector Database Service Package
"""

from .services.vector_service import VectorDBService
from .embeddings import EmbeddingService
from .core.models import (
    SearchRequest,
    SearchResponse,
    AddSourceRequest,
    AddSourceResponse,
    RemoveSourceRequest,
    RemoveSourceResponse,
    SearchType,
    SourceType,
)

__version__ = "1.0.0"

__all__ = [
    "VectorDBService",
    "EmbeddingService",
    "SearchRequest",
    "SearchResponse",
    "AddSourceRequest",
    "AddSourceResponse",
    "RemoveSourceRequest",
    "RemoveSourceResponse",
    "SearchType",
    "SourceType",
]
