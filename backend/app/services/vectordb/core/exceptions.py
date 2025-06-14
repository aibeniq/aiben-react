"""
Custom exceptions for Vector Database Service
"""


class VectorDBError(Exception):
    """Base exception for Vector Database Service"""

    pass


class CollectionNotFoundError(VectorDBError):
    """Raised when a required collection doesn't exist"""

    pass


class EmbeddingError(VectorDBError):
    """Raised when embedding generation fails"""

    pass


class ConfigurationError(VectorDBError):
    """Raised when configuration is invalid"""

    pass


class ValidationError(VectorDBError):
    """Raised when input validation fails"""

    pass


class ConnectionError(VectorDBError):
    """Raised when connection to Weaviate fails"""

    pass


class DeduplicationError(VectorDBError):
    """Raised when deduplication process fails"""

    pass


class ChunkingError(VectorDBError):
    """Raised when text chunking fails"""

    pass
