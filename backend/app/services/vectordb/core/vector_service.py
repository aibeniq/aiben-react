"""
Core Vector Database Service Implementation
"""

import hashlib
from typing import List, Dict, Optional, Callable
from datetime import datetime
import logging
import weaviate
from weaviate.classes.query import Filter
import functools
import backoff

from .models import (
    SearchRequest,
    AddSourceRequest,
    RemoveSourceRequest,
    SearchResponse,
    AddSourceResponse,
    RemoveSourceResponse,
    HealthCheckResponse,
)
from .exceptions import (
    VectorDBError,
    RetryableError,
)
from ..config.settings import (
    SUPPORTED_EMBEDDING_MODELS,
)
from ..config.schemas import (
    get_collection_names,
    get_vector_name,
    create_collections_for_org,
    validate_collections_exist,
    get_collection_info,
    add_embedding_model_to_collection,
)
from ..utils.chunking import chunk_text
from app.services.embeddings.embeddings import load_embeddings_model
from app.models import ModelProvider

logger = logging.getLogger(__name__)


def with_retry(max_retries: int = 3, max_time: int = 30):
    """Decorator for retrying operations on retryable errors"""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            @backoff.on_exception(
                backoff.expo,
                RetryableError,
                max_tries=max_retries,
                max_time=max_time,
                giveup=lambda e: not isinstance(e, RetryableError),
            )
            async def _retry():
                return await func(*args, **kwargs)

            try:
                return await _retry()
            except RetryableError as e:
                logger.error(f"Operation failed after {max_retries} retries: {e}")
                raise VectorDBError(f"Operation failed after retries: {str(e)}")
            except Exception as e:
                raise e

        return wrapper

    return decorator


class VectorDBService:
    """Core Vector Database Service"""

    def __init__(self, client: weaviate.Client, org_id: str):
        self.client = client
        self.org_id = org_id
        self.collection_names = get_collection_names(org_id)
        self._ensure_collections_exist()

    def _ensure_collections_exist(self):
        """Ensure collections exist for the organization"""
        collections_exist = validate_collections_exist(self.client, self.org_id)
        if not all(collections_exist.values()):
            create_collections_for_org(
                self.client, self.org_id, SUPPORTED_EMBEDDING_MODELS
            )

    def _get_sources_collection(self) -> weaviate.Collection | None:
        """Get sources collection"""
        return self.client.collections.get(self.collection_names["sources"])

    def _get_chunks_collection(self) -> weaviate.Collection | None:
        """Get chunks collection"""
        return self.client.collections.get(self.collection_names["chunks"])

    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_source_by_hash(self, content_hash: str) -> Optional[Dict]:
        """Get source by content hash"""
        sources = self._get_sources_collection()
        result = sources.query.fetch_objects(
            filters=Filter.by_property("content_hash").equal(content_hash),
            limit=1,
        )
        return result.objects[0] if result.objects else None

    def _get_chunks_by_source(self, source_id: str) -> List[Dict]:
        """Get all chunks for a source"""
        chunks = self._get_chunks_collection()
        result = chunks.query.fetch_objects(
            filters=Filter.by_property("source_id").equal(source_id),
            limit=1000,  # Adjust based on your needs
        )
        return result.objects

    def _determine_provider(self, model_name: str) -> ModelProvider:
        """Determine provider from model name"""
        if model_name.startswith("text-embedding"):
            return ModelProvider.OPENAI
        elif "claude" in model_name.lower():
            return ModelProvider.ANTHROPIC
        elif model_name.startswith("embed"):
            return ModelProvider.HUGGINGFACE
        else:
            return ModelProvider.OPENAI  # Default fallback

    @with_retry()
    async def add_source(self, request: AddSourceRequest) -> AddSourceResponse:
        """Add a new source to the vector database"""
        try:
            # Generate content hash
            content_hash = self._generate_content_hash(request.content)

            # Check if source already exists
            existing_source = self._get_source_by_hash(content_hash)
            if existing_source:
                return AddSourceResponse(
                    success=True,
                    source_id=existing_source["id"],
                    message="Source already exists",
                )

            # Create source
            sources = self._get_sources_collection()
            source_data = {
                "content_hash": content_hash,
                "source_type": request.source_type,
                "source_path": request.source_path,
                "created_by_user_id": request.created_by_user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "access_users": request.access_users,
                "file_size": request.file_size,
                "mime_type": request.mime_type,
                "title": request.title,
                "author": request.author,
                "description": request.description,
                "tags": request.tags,
            }

            source_result = sources.data.insert(source_data)
            source_id = source_result.uuid

            # Chunk content
            chunks = chunk_text(request.content, request.chunk_size)

            # Add chunks with embeddings
            chunks_collection = self._get_chunks_collection()
            chunk_objects = []

            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "content": chunk,
                    "source_id": source_id,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "created_by_user_id": request.created_by_user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "access_users": request.access_users,
                    "content_hash": self._generate_content_hash(chunk),
                    "embedding_models": request.embedding_models,
                    "section": request.section,
                    "page_number": request.page_number,
                    "line_number": request.line_number,
                    "tags": request.tags,
                }

                # Get embeddings for each model
                for model in request.embedding_models:
                    vector_name = get_vector_name(model)
                    provider = self._determine_provider(model)
                    embedding_model = load_embeddings_model(
                        provider=provider,
                        model_id=model,
                    )
                    embeddings = embedding_model.embed_documents([chunk])[0]
                    chunk_data[vector_name] = embeddings

                chunk_objects.append(chunk_data)

            # Batch insert chunks
            chunks_collection.data.insert_many(chunk_objects)

            return AddSourceResponse(
                success=True,
                source_id=source_id,
                message="Source added successfully",
            )

        except Exception as e:
            return AddSourceResponse(
                success=False,
                source_id=None,
                message=f"Error adding source: {str(e)}",
            )

    @with_retry()
    async def remove_source(self, request: RemoveSourceRequest) -> RemoveSourceResponse:
        """Remove a source and its chunks from the vector database"""
        try:
            sources = self._get_sources_collection()
            chunks = self._get_chunks_collection()

            # Delete chunks first
            chunks.query.delete_many(
                filters=Filter.by_property("source_id").equal(request.source_id)
            )

            # Delete source
            sources.query.delete_many(
                filters=Filter.by_property("id").equal(request.source_id)
            )

            return RemoveSourceResponse(
                success=True,
                message="Source and chunks removed successfully",
            )

        except Exception as e:
            return RemoveSourceResponse(
                success=False,
                message=f"Error removing source: {str(e)}",
            )

    @with_retry()
    async def search_chunks(self, request: SearchRequest) -> SearchResponse:
        """Search for chunks in the vector database"""
        try:
            chunks = self._get_chunks_collection()
            vector_name = get_vector_name(request.embedding_model)

            # Build filter
            filters = []
            if request.filter_params:
                if request.filter_params.source_ids:
                    filters.append(
                        Filter.by_property("source_id").contains_any(
                            request.filter_params.source_ids
                        )
                    )
                if request.filter_params.created_by_user_id:
                    filters.append(
                        Filter.by_property("created_by_user_id").equal(
                            request.filter_params.created_by_user_id
                        )
                    )
                if request.filter_params.access_users:
                    filters.append(
                        Filter.by_property("access_users").contains_any(
                            request.filter_params.access_users
                        )
                    )
                if request.filter_params.tags:
                    filters.append(
                        Filter.by_property("tags").contains_any(
                            request.filter_params.tags
                        )
                    )

            # Combine filters
            combined_filter = Filter.all_of(*filters) if filters else None

            # Perform search
            result = chunks.query.near_vector(
                near_vector=request.query_vector,
                target_vector=vector_name,
                filters=combined_filter,
                limit=request.limit,
                offset=request.offset,
            )

            # Format response
            chunks = []
            for obj in result.objects:
                chunk = {
                    "id": obj.uuid,
                    "content": obj.properties["content"],
                    "source_id": obj.properties["source_id"],
                    "chunk_index": obj.properties["chunk_index"],
                    "score": obj.score,
                    "metadata": {
                        "created_by_user_id": obj.properties["created_by_user_id"],
                        "created_at": obj.properties["created_at"],
                        "access_users": obj.properties["access_users"],
                        "section": obj.properties.get("section"),
                        "page_number": obj.properties.get("page_number"),
                        "line_number": obj.properties.get("line_number"),
                        "tags": obj.properties.get("tags", []),
                        "custom_metadata": obj.properties.get("custom_metadata", {}),
                    },
                }
                chunks.append(chunk)

            return SearchResponse(
                success=True,
                chunks=chunks,
                total=len(chunks),
                message="Search completed successfully",
            )

        except Exception as e:
            return SearchResponse(
                success=False,
                chunks=[],
                total=0,
                message=f"Error searching chunks: {str(e)}",
            )

    @with_retry()
    async def health_check(self) -> HealthCheckResponse:
        """Check the health of the vector database service"""
        try:
            # Check if collections exist
            collections_exist = validate_collections_exist(self.client, self.org_id)
            if not all(collections_exist.values()):
                return HealthCheckResponse(
                    status="error",
                    message="One or more collections do not exist",
                    details={"collections_exist": collections_exist},
                )

            # Get collection info
            collection_info = get_collection_info(self.client, self.org_id)

            return HealthCheckResponse(
                status="healthy",
                message="Service is healthy",
                details={
                    "collections": collection_info["collections"],
                    "org_id": self.org_id,
                },
            )

        except Exception as e:
            return HealthCheckResponse(
                status="error",
                message=f"Health check failed: {str(e)}",
                details={},
            )

    async def add_embedding_model(self, embedding_model: str) -> bool:
        """Add a new embedding model to the chunks collection"""
        try:
            if embedding_model not in SUPPORTED_EMBEDDING_MODELS:
                raise ValueError(f"Unsupported embedding model: {embedding_model}")

            add_embedding_model_to_collection(self.client, self.org_id, embedding_model)
            return True

        except Exception as e:
            logger.error(f"Error adding embedding model: {str(e)}")
            return False

    async def close(self):
        """Close the Weaviate client connection"""
        if self.client:
            self.client.close()
