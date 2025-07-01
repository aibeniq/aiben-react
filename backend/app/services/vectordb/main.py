# NOTE: uses text-embedding-3-small for embeddings
# NOTE: supports only one collection for now (and thus one embedding model)

# TODO: search methods
# TODO: initialize on fastapi startup
# TODO: add auth?

## Milvus client
from pymilvus import MilvusClient, CollectionSchema
import logging
from typing import List, Dict, Any, Optional
from app.services.vectordb.types import ChunkData, EmbeddedChunkData
from app.services.vectordb.config import (
    MILVUS_SCHEMA,
    BASE_COLLECTION_NAME,
    MILVUS_URL,
    EMBEDDING_MODEL,
    BM25_FUNCTION,
)

logger = logging.getLogger(__name__)


class VectorDBService:
    """Vector database service for managing document chunks and embeddings."""

    def __init__(self):
        """Initialize the vector database service."""
        try:
            # initialize Milvus client using config
            self.client = MilvusClient(MILVUS_URL)
            logger.info(f"Connected to Milvus at {MILVUS_URL}")

            # initialize embedding model
            self.embedding_model = EMBEDDING_MODEL
            logger.info(f"Loaded embedding model: {EMBEDDING_MODEL}")

            # create collection schema
            self.schema = CollectionSchema(
                fields=MILVUS_SCHEMA, description="schema for base collection"
            )
            self.schema.add_function(BM25_FUNCTION)  # for keyword search

            # initialize collection
            self._init_collection()

        except Exception as e:
            logger.error(f"Failed to initialize VectorDBService: {e}")
            raise

    def _init_collection(self) -> bool:
        """Initialize the collection if it doesn't exist and set up indexes."""
        try:
            # check if collection exists
            if self.client.has_collection(collection_name=BASE_COLLECTION_NAME):
                logger.info(f"Collection '{BASE_COLLECTION_NAME}' already exists.")
                return True

            logger.info(f"Creating collection '{BASE_COLLECTION_NAME}'...")

            # create collection
            self.client.create_collection(
                collection_name=BASE_COLLECTION_NAME,
                schema=self.schema,
            )

            # create index parameters
            index_params = self.client.prepare_index_params()

            # add indexes
            index_params.add_index(field_name="id", index_type="STL_SORT")

            index_params.add_index(
                field_name="dense",
                index_type="HNSW",
                metric_type="COSINE",
                params={"M": 16, "efConstruction": 500},
            )

            index_params.add_index(
                field_name="sparse",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",
                params={"inverted_index_algo": "DAAT_MAXSCORE"},
            )

            index_params.add_index(
                field_name="knowledge_base_id",
                index_type="FLAT",
                metric_type="COSINE",
            )

            index_params.add_index(
                field_name="user_id",
                index_type="FLAT",
                metric_type="COSINE",
            )

            index_params.add_index(
                field_name="source_id",
                index_type="FLAT",
                metric_type="COSINE",
            )

            # create indexes
            self.client.create_index(
                collection_name=BASE_COLLECTION_NAME,
                index_params=index_params,
                sync=True,
            )

            logger.info(
                f"Collection '{BASE_COLLECTION_NAME}' created successfully with indexes."
            )
            return True

        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            return False

    def add_chunks(
        self,
        chunks: List[ChunkData],
    ) -> Dict[str, Any]:
        """
        Add chunks to the collection.

        Args:
            chunks: List of ChunkData objects containing chunk data

        Returns:
            Dictionary with insertion results
        """
        try:
            # ensure collection exists and is loaded
            if not self.client.has_collection(collection_name=BASE_COLLECTION_NAME):
                if not self._init_collection():
                    return {
                        "success": False,
                        "error": "Failed to initialize collection",
                    }

            # load collection if not already loaded
            self.client.load_collection(collection_name=BASE_COLLECTION_NAME)

            # prepare data for insertion
            data_to_insert: List[EmbeddedChunkData] = []
            embeddings = self.embedding_model.embed_documents(
                [chunk.content for chunk in chunks]
            )

            for chunk, embedding in zip(chunks, embeddings):
                chunk_data = EmbeddedChunkData(**chunk.model_dump(), dense=embedding)
                data_to_insert.append(chunk_data)

            # insert data
            result = self.client.insert(
                collection_name=BASE_COLLECTION_NAME,
                data=data_to_insert,
            )

            logger.info(f"Successfully inserted {len(data_to_insert)} chunks")
            return {
                "success": True,
                "inserted_count": len(data_to_insert),
                "result": result,
            }

        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            return {"success": False, "error": str(e)}

    def delete_chunks(
        self,
        knowledge_base_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete chunks from the collection."""
        try:
            assert (
                knowledge_base_id or user_id or source_id
            ), "At least one of knowledge_base_id, user_id, or source_id must be provided"

            # ensure collection is loaded
            self.client.load_collection(collection_name=BASE_COLLECTION_NAME)

            # prepare filter
            filter_expr = []
            filter_params = {}
            if knowledge_base_id:
                filter_expr.append("knowledge_base_id == {kb_id}")
                filter_params["kb_id"] = knowledge_base_id
            if user_id:
                filter_expr.append("user_id == {user_id}")
                filter_params["user_id"] = user_id
            if source_id:
                filter_expr.append("source_id == {source_id}")
                filter_params["source_id"] = source_id
            filter_expr = " AND ".join(filter_expr) if filter_expr else None

            # delete chunks
            self.client.delete(
                collection_name=BASE_COLLECTION_NAME,
                filter=filter_expr,
                filter_params=filter_params if filter_params else None,
            )

            logger.info(f"Successfully deleted chunks")
            return {"success": True}

        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
            return {"success": False, "error": str(e)}

    def search_semantic(
        self,
        query: str,
        knowledge_base_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 10,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic similarity search.

        Args:
            query: Search query text
            knowledge_base_id: Optional filter by knowledge base ID
            user_id: Optional filter by user ID
            source_id: Optional filter by source ID
            limit: Maximum number of results to return
            output_fields: List of fields to return in results

        Returns:
            Dictionary with search results
        """
        try:
            assert (
                knowledge_base_id or user_id or source_id
            ), "At least one of knowledge_base_id, user_id, or source_id must be provided"

            # ensure collection is loaded
            self.client.load_collection(collection_name=BASE_COLLECTION_NAME)

            # generate embedding for query
            query_embedding = self.embedding_model.embed_query(query)

            # prepare filter
            filter_expr = []
            filter_params = {}
            if knowledge_base_id:
                filter_expr.append("knowledge_base_id == {kb_id}")
                filter_params["kb_id"] = knowledge_base_id
            if user_id:
                filter_expr.append("user_id == {user_id}")
                filter_params["user_id"] = user_id
            if source_id:
                filter_expr.append("source_id == {source_id}")
                filter_params["source_id"] = source_id
            filter_expr = " AND ".join(filter_expr) if filter_expr else None

            # set default output fields
            if output_fields is None:
                output_fields = [
                    "content",
                    "tags",
                    "title",
                    "knowledge_base_id",
                    "user_id",
                    "source_id",
                ]

            # perform search
            results = self.client.search(
                collection_name=BASE_COLLECTION_NAME,
                data=[query_embedding],
                anns_field="dense",
                filter=filter_expr,
                filter_params=filter_params if filter_params else None,
                limit=limit,
                output_fields=output_fields,
            )

            logger.info(
                f"Search completed with {len(results[0]) if results else 0} results"
            )
            return {"success": True, "results": results[0] if results else []}

        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return {"success": False, "error": str(e)}

    def search_keyword(
        self,
        query: str,
        knowledge_base_id: Optional[str] = None,
        user_id: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 10,
        output_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Keyword search.

        Args:
            query: Search query text
            knowledge_base_id: Optional filter by knowledge base ID
            user_id: Optional filter by user ID
            source_id: Optional filter by source ID
            limit: Maximum number of results to return
            output_fields: List of fields to return in results

        Returns:
            Dictionary with search results
        """
        try:
            assert (
                knowledge_base_id or user_id or source_id
            ), "At least one of knowledge_base_id, user_id, or source_id must be provided"

            # ensure collection is loaded
            self.client.load_collection(collection_name=BASE_COLLECTION_NAME)

            # prepare filter
            filter_expr = []
            filter_params = {}
            if knowledge_base_id:
                filter_expr.append("knowledge_base_id == {kb_id}")
                filter_params["kb_id"] = knowledge_base_id
            if user_id:
                filter_expr.append("user_id == {user_id}")
                filter_params["user_id"] = user_id
            if source_id:
                filter_expr.append("source_id == {source_id}")
                filter_params["source_id"] = source_id
            filter_expr = " AND ".join(filter_expr) if filter_expr else None

            # perform search
            results = self.client.search(
                collection_name=BASE_COLLECTION_NAME,
                data=[query],
                anns_field="sparse",
                filter=filter_expr,
                filter_params=filter_params if filter_params else None,
                limit=limit,
                output_fields=output_fields,
            )

            logger.info(
                f"Search completed with {len(results[0]) if results else 0} results"
            )
            return {"success": True, "results": results[0] if results else []}

        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return {"success": False, "error": str(e)}
