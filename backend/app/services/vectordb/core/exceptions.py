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


class SearchError(VectorDBError):
    """Raised when there is an error during search operations"""

    pass


class BatchOperationError(VectorDBError):
    """Raised when there is an error during batch operations"""

    pass


class ConnectionError(VectorDBError):
    """Raised when there is an error connecting to Weaviate"""

    pass


class ValidationError(VectorDBError):
    """Raised when input validation fails"""

    pass


class AccessControlError(VectorDBError):
    """Raised when access control checks fail"""

    pass


class RateLimitError(VectorDBError):
    """Raised when rate limits are exceeded"""

    pass


class RetryableError(VectorDBError):
    """Base class for errors that can be retried"""

    pass


class TemporaryConnectionError(RetryableError):
    """Raised for temporary connection issues"""

    pass


class EmbeddingServiceUnavailable(RetryableError):
    """Raised when embedding service is temporarily unavailable"""

    pass


class WeaviateServiceUnavailable(RetryableError):
    """Raised when Weaviate service is temporarily unavailable"""

    pass


class BatchProcessingError(RetryableError):
    """Raised when batch processing encounters temporary issues"""

    pass


class ConfigurationError(VectorDBError):
    """Raised when configuration is invalid"""

    pass


class DeduplicationError(VectorDBError):
    """Raised when deduplication process fails"""

    pass


class ChunkingError(VectorDBError):
    """Raised when text chunking fails"""

    pass
