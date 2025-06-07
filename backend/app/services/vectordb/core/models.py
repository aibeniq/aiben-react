"""
Pydantic models for Vector Database Service
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Supported search types"""

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


class SourceType(str, Enum):
    """Supported source types"""

    FILE = "file"
    URL = "url"
    TEXT = "text"


class ChunkMetadata(BaseModel):
    """Metadata associated with a chunk"""

    section: Optional[str] = None
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class SourceMetadata(BaseModel):
    """Metadata associated with a source"""

    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class FilterParams(BaseModel):
    """Parameters for filtering search results"""

    user_id: Optional[str] = None
    knowledge_base_ids: Optional[List[str]] = None
    source_ids: Optional[List[str]] = None
    date_range: Optional[tuple] = None
    access_users: Optional[List[str]] = None
    source_types: Optional[List[SourceType]] = None
    custom_filters: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class SearchRequest(BaseModel):
    """Request model for search operations"""

    query: str = Field(..., min_length=1, max_length=20000)
    org_id: str = Field(..., min_length=1)
    embedding_model: str = Field(default="text-embedding-3-small")
    search_type: SearchType = Field(default=SearchType.HYBRID)
    filters: Optional[FilterParams] = None
    limit: int = Field(default=10, ge=1, le=100)
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)  # For hybrid search
    include_metadata: bool = Field(default=True)

    @field_validator("embedding_model")
    def validate_embedding_model(cls, v):
        from ..config.settings import validate_model_support

        if not validate_model_support(v):
            raise ValueError(f"Unsupported embedding model: {v}")
        return v

    class Config:
        use_enum_values = True


class SearchResult(BaseModel):
    """Individual search result"""

    content: str
    source_id: str
    chunk_index: int
    score: float = Field(ge=0.0)
    distance: Optional[float] = Field(None, ge=0.0)
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata)
    source_metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    embedding_model: str
    created_at: datetime
    chunk_id: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SearchResponse(BaseModel):
    """Response model for search operations"""

    results: List[SearchResult]
    total_results: int
    query: str
    search_type: SearchType
    embedding_model: str
    processing_time_ms: float
    filters_applied: Optional[FilterParams] = None

    class Config:
        use_enum_values = True


class AddSourceRequest(BaseModel):
    """Request model for adding a source"""

    org_id: str = Field(..., min_length=1)
    source_path: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source_type: SourceType = Field(default=SourceType.TEXT)
    embedding_models: List[str] = Field(
        default_factory=lambda: ["text-embedding-3-small"]
    )
    user_id: str = Field(..., min_length=1)
    knowledge_base_id: str = Field(..., min_length=1)
    metadata: Optional[SourceMetadata] = None
    access_users: Optional[List[str]] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=8000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)

    @field_validator("embedding_models")
    def validate_embedding_models(cls, v):
        from ..config.settings import validate_model_support

        for model in v:
            if not validate_model_support(model):
                raise ValueError(f"Unsupported embedding model: {model}")
        return v

    @field_validator("chunk_overlap")
    def validate_chunk_overlap(cls, v, values):
        if (
            v is not None
            and "chunk_size" in values
            and values["chunk_size"] is not None
        ):
            if v >= values["chunk_size"]:
                raise ValueError("Chunk overlap must be less than chunk size")
        return v

    class Config:
        use_enum_values = True


class AddSourceResponse(BaseModel):
    """Response model for adding a source"""

    source_id: str
    chunks_created: int
    embedding_models_used: List[str]
    processing_time_ms: float
    was_duplicate: bool = False
    message: str = "Source added successfully"


class RemoveSourceRequest(BaseModel):
    """Request model for removing a source"""

    org_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)  # For access control


class RemoveSourceResponse(BaseModel):
    """Response model for removing a source"""

    success: bool
    chunks_removed: int
    message: str
    processing_time_ms: float


class ChunkInfo(BaseModel):
    """Information about a chunk"""

    chunk_id: str
    content: str
    source_id: str
    chunk_index: int
    chunk_size: int
    embedding_models: List[str]
    metadata: ChunkMetadata
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SourceInfo(BaseModel):
    """Information about a source"""

    source_id: str
    source_path: str
    source_type: SourceType
    content_hash: str
    knowledge_base_id: str
    created_by_user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: SourceMetadata
    access_users: List[str]
    chunk_count: int
    total_size: int

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str
    weaviate_connected: bool
    embedding_services: Dict[str, bool]
    timestamp: datetime
    version: str = "1.0.0"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BatchOperationStatus(BaseModel):
    """Status of a batch operation"""

    total_items: int
    processed_items: int
    failed_items: int
    errors: List[str] = Field(default_factory=list)
    processing_time_ms: float


class EmbeddingModel(BaseModel):
    """Embedding model information"""

    name: str
    provider: str
    dimensions: int
    max_tokens: int
    cost_per_1k: float
    is_available: bool = True
