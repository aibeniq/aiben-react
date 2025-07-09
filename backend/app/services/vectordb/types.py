# NOTE: when adding new fields, update both the ChunkData and Milvus schema

import time
from typing import Any

from pydantic import BaseModel, Field


class ChunkData(BaseModel):
    """Schema for chunk data to be inserted into the vector database."""

    knowledge_base_id: str = Field(..., description="Knowledge base ID")
    source_id: str = Field(..., description="Source ID")
    user_id: str = Field(..., description="User ID")
    content: str = Field(..., description="Content of the chunk")
    tags: list[str] = Field(
        default_factory=list, description="Tags associated with the chunk"
    )
    title: str = Field(default="", description="Title of the document")
    summary: str = Field(default="", description="Summary of the document")
    author: str = Field(default="", description="Author of the document")
    url: str = Field(default="", description="URL of the document")
    created_at: int = Field(
        default_factory=lambda: int(time.time()), description="Created timestamp"
    )
    updated_at: int = Field(
        default_factory=lambda: int(time.time()), description="Updated timestamp"
    )


class EmbeddedChunkData(ChunkData):
    dense: list[float] = Field(..., description="Dense embedding vector")
    # no sparse field as milvus adds it on insertion


# Search result entity type
class SearchEntity(BaseModel):
    """Entity data returned from vector database search."""

    content: str = Field(..., description="Content of the chunk")
    knowledge_base_id: str = Field(..., description="Knowledge base ID")
    source_id: str = Field(..., description="Source ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(default="", description="Title of the document")
    author: str = Field(default="", description="Author of the document")
    url: str = Field(default="", description="URL of the document")
    tags: list[str] = Field(
        default_factory=list, description="Tags associated with the chunk"
    )
    summary: str = Field(default="", description="Summary of the document")
    created_at: int = Field(default=0, description="Created timestamp")
    updated_at: int = Field(default=0, description="Updated timestamp")


# Search result types
class SearchHit(BaseModel):
    """A single search result hit from the vector database."""

    id: str = Field(..., description="Unique identifier for the chunk")
    distance: float = Field(..., description="Distance/similarity score")
    entity: SearchEntity = Field(
        ..., description="Entity data containing all returned fields"
    )


class SearchResults(BaseModel):
    """Results from a vector database search operation."""

    hits: list[SearchHit] = Field(
        default_factory=list, description="List of search hits"
    )


# Exception types for vectordb operations
class VectorDBError(Exception):
    """Base exception for vector database operations."""

    pass


class EmbeddingModelError(VectorDBError):
    """Exception raised when there's an issue with the embedding model."""

    pass
