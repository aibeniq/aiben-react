"""
Core models for Vector Database Service
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ChunkingConfig(BaseModel):
    """Configuration for text chunking strategy"""

    chunk_size: int = Field(default=1000, ge=100, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    chunking_method: str = Field(default="recursive_character")
    separators: Optional[List[str]] = Field(default=None)


class FilterParams(BaseModel):
    """Filter parameters for search queries"""

    source_data_ids: Optional[List[str]] = None
    knowledge_base_ids: Optional[List[str]] = None
    created_by_user_id: Optional[str] = None
    access_users: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    @field_validator("access_users")
    @classmethod
    def validate_access_users(cls, v):
        """Ensure at least one access user is provided"""
        if v is None or len(v) == 0:
            raise ValueError("At least one access user must be provided")
        return v


class SearchRequest(BaseModel):
    """Request model for searching chunks"""

    query_vector: List[float]
    embedding_model: str
    filter_params: FilterParams
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("query_vector")
    @classmethod
    def validate_query_vector(cls, v):
        """Ensure query vector is not empty"""
        if not v:
            raise ValueError("Query vector cannot be empty")
        return v

    @field_validator("embedding_model")
    @classmethod
    def validate_embedding_model(cls, v):
        """Ensure embedding model is provided"""
        if not v:
            raise ValueError("Embedding model must be provided")
        return v


class AddSourceRequest(BaseModel):
    """Request model for adding a source"""

    content: str
    source_data_id: str  # Direct reference to SourceData
    source_type: str
    created_by_user_id: str
    access_users: List[str]
    embedding_models: List[str]
    chunking_config: Optional[ChunkingConfig] = None
    # Optional metadata
    source_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class RemoveSourceRequest(BaseModel):
    """Request model for removing a source"""

    source_data_id: str  # Remove by source_data_id


class SearchResponse(BaseModel):
    """Response model for search results"""

    success: bool
    chunks: List[Dict[str, Any]]
    total: int
    message: str


class AddSourceResponse(BaseModel):
    """Response model for adding a source"""

    success: bool
    source_data_id: Optional[str]
    chunks_created: int
    chunks_reused: int
    message: str


class RemoveSourceResponse(BaseModel):
    """Response model for removing a source"""

    success: bool
    chunks_removed: int
    message: str


class HealthCheckResponse(BaseModel):
    """Response model for health check"""

    status: str
    message: str
    details: Dict[str, Any]
