"""
Main Vector Database Service that integrates with existing embeddings service
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter, MetadataQuery, HybridFusion
from contextlib import asynccontextmanager

from ..core.models import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchType,
    AddSourceRequest,
    AddSourceResponse,
    RemoveSourceRequest,
    RemoveSourceResponse,
    FilterParams,
    ChunkMetadata,
    SourceMetadata,
)
from ..core.exceptions import VectorDBError, CollectionNotFoundError, EmbeddingError
from ..config.settings import settings
from ..config.schemas import (
    get_collection_names,
    create_collections_for_org,
    validate_collections_exist,
    get_vector_name,
)
from ..embeddings import EmbeddingService, generate_content_hash, split_text_into_chunks
from app.models import ModelProvider

logger = logging.getLogger(__name__)


class VectorDBService:
    """Main Vector Database Service"""

    def __init__(self):
        self.client = None
        self.embedding_service = EmbeddingService()

    @asynccontextmanager
    async def get_client(self):
        """Async context manager for Weaviate client lifecycle"""
        if not self.client:
            self.client = weaviate.connect_to_local()
        try:
            yield self.client
        except Exception as e:
            logger.error(f"Weaviate client error: {e}")
            raise

    def _determine_provider(self, model_name: str) -> ModelProvider:
        """Determine provider from model name"""
        return self.embedding_service.determine_provider(model_name)

    async def _ensure_collections_exist(self, org_id: str, embedding_models: List[str]):
        """Ensure collections exist for the organization"""
        async with self.get_client() as client:
            collections_exist = validate_collections_exist(client, org_id)

            if not all(collections_exist.values()):
                if settings.auto_create_collections:
                    create_collections_for_org(client, org_id, embedding_models)
                    logger.info(f"Created collections for organization: {org_id}")
                else:
                    raise CollectionNotFoundError(
                        f"Collections do not exist for organization: {org_id}"
                    )

    async def add_source(self, request: AddSourceRequest) -> AddSourceResponse:
        """Add a source with deduplication and batch chunk processing"""
        start_time = time.time()

        try:
            # Ensure collections exist
            await self._ensure_collections_exist(
                request.org_id, request.embedding_models
            )

            # Generate content hash for deduplication
            content_hash = generate_content_hash(request.content)

            # Check if source already exists
            existing_source_id = await self._check_source_exists(
                request.org_id, content_hash
            )

            if existing_source_id:
                # Update embedding models for existing chunks if needed
                await self._update_chunk_embeddings(
                    request.org_id, existing_source_id, request.embedding_models
                )

                processing_time = (time.time() - start_time) * 1000
                return AddSourceResponse(
                    source_id=existing_source_id,
                    chunks_created=0,
                    embedding_models_used=request.embedding_models,
                    processing_time_ms=processing_time,
                    was_duplicate=True,
                    message="Source already exists, updated embedding models if needed",
                )

            # Create new source
            async with self.get_client() as client:
                collection_names = get_collection_names(request.org_id)
                sources_collection = client.collections.get(collection_names["sources"])

                source_properties = {
                    "source_path": request.source_path,
                    "content_hash": content_hash,
                    "source_type": request.source_type.value,
                    "knowledge_base_id": request.knowledge_base_id,
                    "created_by_user_id": request.user_id,
                    "created_at": datetime.utcnow(),
                    "access_users": request.access_users or [request.user_id],
                    "file_size": len(request.content),
                    "mime_type": "text/plain",  # Could be enhanced to detect actual mime type
                }

                # Add source metadata
                if request.metadata:
                    source_properties.update(
                        {
                            "title": request.metadata.title,
                            "author": request.metadata.author,
                            "description": request.metadata.description,
                            "tags": request.metadata.tags,
                            "custom_metadata": request.metadata.custom_fields,
                        }
                    )

                source_id = sources_collection.data.insert(source_properties)

                # Split content into chunks
                chunks = self._create_chunks(
                    content=request.content,
                    source_id=source_id,
                    chunk_size=request.chunk_size or settings.default_chunk_size,
                    chunk_overlap=request.chunk_overlap
                    or settings.default_chunk_overlap,
                )

                # Batch process chunks with embeddings
                chunks_created = await self._batch_add_chunks(
                    request.org_id,
                    chunks,
                    request.embedding_models,
                    request.user_id,
                    request.knowledge_base_id,
                    request.access_users or [request.user_id],
                )

                processing_time = (time.time() - start_time) * 1000
                return AddSourceResponse(
                    source_id=source_id,
                    chunks_created=chunks_created,
                    embedding_models_used=request.embedding_models,
                    processing_time_ms=processing_time,
                    was_duplicate=False,
                    message="Source added successfully",
                )

        except Exception as e:
            logger.error(f"Error adding source: {e}")
            raise VectorDBError(f"Failed to add source: {str(e)}")

    def _create_chunks(
        self, content: str, source_id: str, chunk_size: int, chunk_overlap: int
    ) -> List[Dict]:
        """Create chunks from content"""
        chunk_texts = split_text_into_chunks(
            content=content, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        chunks = []
        for index, text in enumerate(chunk_texts):
            chunks.append(
                {
                    "content": text,
                    "source_id": source_id,
                    "chunk_index": index,
                    "chunk_size": len(text.split()),
                    "content_hash": generate_content_hash(text),
                }
            )

        return chunks

    async def _check_source_exists(
        self, org_id: str, content_hash: str
    ) -> Optional[str]:
        """Check if a source with the given content hash already exists"""
        try:
            async with self.get_client() as client:
                collection_names = get_collection_names(org_id)
                sources_collection = client.collections.get(collection_names["sources"])

                result = sources_collection.query.fetch_objects(
                    where=Filter.by_property("content_hash").equal(content_hash),
                    limit=1,
                )

                if result.objects:
                    return str(result.objects[0].uuid)

                return None
        except Exception as e:
            logger.error(f"Error checking source existence: {e}")
            return None

    def _build_filters(self, filter_params: Optional[FilterParams]) -> Optional[Filter]:
        """Build Weaviate filters from filter parameters"""
        if not filter_params:
            return None

        filters = []

        if filter_params.user_id:
            filters.append(
                Filter.by_property("created_by_user_id").equal(filter_params.user_id)
            )

        if filter_params.knowledge_base_ids:
            filters.append(
                Filter.by_property("knowledge_base_id").contains_any(
                    filter_params.knowledge_base_ids
                )
            )

        if filter_params.source_ids:
            filters.append(
                Filter.by_property("source_id").contains_any(filter_params.source_ids)
            )

        if filter_params.access_users:
            filters.append(
                Filter.by_property("access_users").contains_any(
                    filter_params.access_users
                )
            )

        if not filters:
            return None

        # Combine filters with AND
        result_filter = filters[0]
        for f in filters[1:]:
            result_filter = result_filter & f

        return result_filter

    async def _batch_add_chunks(
        self,
        org_id: str,
        chunks: List[Dict],
        embedding_models: List[str],
        user_id: str,
        knowledge_base_id: str,
        access_users: List[str],
    ) -> int:
        """Batch process chunks with multiple embedding models"""

        async with self.get_client() as client:
            collection_names = get_collection_names(org_id)
            chunks_collection = client.collections.get(collection_names["chunks"])

            # Process chunks in batches
            chunks_created = 0
            batch_size = settings.batch_size

            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i : i + batch_size]

                # Generate embeddings for all models
                batch_data = []
                for chunk in batch_chunks:
                    # Generate embeddings for all models
                    vectors = {}
                    for model_name in embedding_models:
                        try:
                            provider = self._determine_provider(model_name)
                            vector = await self.embedding_service.get_single_embedding(
                                text=chunk["content"],
                                model_name=model_name,
                                provider=provider,
                            )
                            vectors[get_vector_name(model_name)] = vector
                        except Exception as e:
                            logger.error(
                                f"Error generating embedding with {model_name}: {e}"
                            )
                            # Skip this model for this chunk
                            continue

                    if not vectors:
                        logger.warning(
                            f"No embeddings generated for chunk {chunk['chunk_index']}"
                        )
                        continue

                    batch_data.append(
                        {
                            "properties": {
                                "content": chunk["content"],
                                "source_id": chunk["source_id"],
                                "chunk_index": chunk["chunk_index"],
                                "chunk_size": chunk["chunk_size"],
                                "knowledge_base_id": knowledge_base_id,
                                "created_by_user_id": user_id,
                                "created_at": datetime.utcnow(),
                                "access_users": access_users,
                                "content_hash": chunk["content_hash"],
                                "embedding_models": list(vectors.keys()),
                                **chunk.get("metadata", {}),
                            },
                            "vector": vectors,
                        }
                    )

                # Batch insert
                with chunks_collection.batch.fixed_size(
                    batch_size=len(batch_data)
                ) as batch:
                    for item in batch_data:
                        batch.add_object(
                            properties=item["properties"], vector=item["vector"]
                        )

                    if batch.number_errors > 0:
                        logger.error(f"Batch insert errors: {batch.failed_objects}")
                    else:
                        chunks_created += len(batch_data)

            return chunks_created

    def _determine_provider(self, model_name: str) -> ModelProvider:
        """Determine provider from model name"""
        if model_name.startswith("text-embedding"):
            return ModelProvider.OPENAI
        elif "huggingface" in model_name.lower():
            return ModelProvider.HUGGINGFACE
        elif "ollama" in model_name.lower():
            return ModelProvider.OLLAMA
        elif "bedrock" in model_name.lower() or "aws" in model_name.lower():
            return ModelProvider.AWS
        elif "replicate" in model_name.lower():
            return ModelProvider.REPLICATE
        else:
            # Default to OpenAI for unknown models
            return ModelProvider.OPENAI

    async def search_chunks(self, request: SearchRequest) -> SearchResponse:
        """Search chunks with pre-filtering and structured output"""
        start_time = time.time()

        try:
            async with self.get_client() as client:
                collection_names = get_collection_names(request.org_id)
                chunks_collection = client.collections.get(collection_names["chunks"])

                # Build filters
                weaviate_filters = self._build_filters(request.filters)

                # Determine vector name for the embedding model
                vector_name = get_vector_name(request.embedding_model)

                # Execute search based on type
                if request.search_type == SearchType.SEMANTIC:
                    response = chunks_collection.query.near_text(
                        query=request.query,
                        target_vector=vector_name,
                        filters=weaviate_filters,
                        limit=request.limit,
                        return_metadata=MetadataQuery(
                            distance=True, score=True, creation_time=True
                        ),
                    )
                elif request.search_type == SearchType.KEYWORD:
                    response = chunks_collection.query.bm25(
                        query=request.query,
                        query_properties=["content"],
                        filters=weaviate_filters,
                        limit=request.limit,
                        return_metadata=MetadataQuery(score=True, creation_time=True),
                    )
                elif request.search_type == SearchType.HYBRID:
                    response = chunks_collection.query.hybrid(
                        query=request.query,
                        target_vector=vector_name,
                        alpha=request.alpha,
                        filters=weaviate_filters,
                        limit=request.limit,
                        return_metadata=MetadataQuery(
                            distance=True, score=True, creation_time=True
                        ),
                    )

                # Convert to structured results
                results = []
                for obj in response.objects:
                    results.append(
                        SearchResult(
                            content=obj.properties["content"],
                            source_id=obj.properties["source_id"],
                            chunk_index=obj.properties["chunk_index"],
                            score=obj.metadata.score or 0.0,
                            distance=obj.metadata.distance,
                            metadata=ChunkMetadata(
                                section=obj.properties.get("section"),
                                page_number=obj.properties.get("page_number"),
                                line_number=obj.properties.get("line_number"),
                                tags=obj.properties.get("tags", []),
                                custom_fields=obj.properties.get("custom_metadata", {}),
                            ),
                            source_metadata=SourceMetadata(),  # Could be populated with join
                            embedding_model=request.embedding_model,
                            created_at=obj.metadata.creation_time,
                            chunk_id=obj.uuid,
                        )
                    )

                processing_time = (time.time() - start_time) * 1000

                return SearchResponse(
                    results=results,
                    total_results=len(results),
                    query=request.query,
                    search_type=request.search_type,
                    embedding_model=request.embedding_model,
                    processing_time_ms=processing_time,
                    filters_applied=request.filters,
                )

        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            raise VectorDBError(f"Search failed: {str(e)}")

    async def remove_source(self, request: RemoveSourceRequest) -> RemoveSourceResponse:
        """Remove source and all associated chunks"""
        start_time = time.time()

        try:
            async with self.get_client() as client:
                collection_names = get_collection_names(request.org_id)

                # Delete all chunks first
                chunks_collection = client.collections.get(collection_names["chunks"])
                chunks_deleted = chunks_collection.data.delete_many(
                    filters=Filter.by_property("source_id").equal(request.source_id)
                )

                # Delete source
                sources_collection = client.collections.get(collection_names["sources"])
                sources_collection.data.delete_by_id(request.source_id)

                processing_time = (time.time() - start_time) * 1000

                return RemoveSourceResponse(
                    success=True,
                    chunks_removed=chunks_deleted.matches if chunks_deleted else 0,
                    message="Source and chunks removed successfully",
                    processing_time_ms=processing_time,
                )

        except Exception as e:
            logger.error(f"Error removing source {request.source_id}: {e}")
            processing_time = (time.time() - start_time) * 1000
            return RemoveSourceResponse(
                success=False,
                chunks_removed=0,
                message=f"Failed to remove source: {str(e)}",
                processing_time_ms=processing_time,
            )

    async def _update_chunk_embeddings(
        self, org_id: str, source_id: str, embedding_models: List[str]
    ):
        """Update embeddings for existing chunks with new models"""
        # Implementation for updating existing chunks with new embedding models
        # This would involve checking which models are missing and generating those embeddings
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the vector database service"""
        health_status = {
            "status": "healthy",
            "weaviate_connected": False,
            "embedding_services": {},
            "timestamp": datetime.utcnow(),
        }

        try:
            # Check Weaviate connection
            async with self.get_client() as client:
                # Try to list collections to verify connection
                collections = client.collections.list_all()
                health_status["weaviate_connected"] = True

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status

    async def close(self):
        """Clean up resources"""
        if self.client:
            self.client.close()
