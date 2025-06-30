# NOTE: uses text-embedding-3-small for embeddings
# NOTE: when adding new fields, update both the ChunkData and Milvus schema

from pymilvus import FieldSchema, DataType
from typing import List
from pydantic import BaseModel, Field
import time


class ChunkData(BaseModel):
    """Schema for chunk data to be inserted into the vector database."""

    knowledge_base_id: str = Field(..., description="Knowledge base ID")
    source_id: str = Field(..., description="Source ID")
    user_id: str = Field(..., description="User ID")
    content: str = Field(..., description="Content of the chunk")
    tags: List[str] = Field(
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
    vector: List[float] = Field(..., description="Embedding vector")
