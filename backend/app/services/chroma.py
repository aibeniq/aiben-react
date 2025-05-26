import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

import chromadb
from chromadb.utils import embedding_functions
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHROMADB_HOST = os.getenv("CHROMADB_HOST", "chromadb")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", 8000))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

_chroma_client: Optional[chromadb.HttpClient] = None
_chroma_instances: Dict[str, Chroma] = {}
_embedding_function: Optional[embedding_functions.SentenceTransformerEmbeddingFunction] = None
_text_splitter: Optional[RecursiveCharacterTextSplitter] = None


class ChromaDBService:
    def __init__(self):
        self.client = self._get_chroma_client()
        self.embedding_function = self._get_embedding_function()
        self.text_splitter = self._get_text_splitter()
    
    def _get_chroma_client(self) -> chromadb.HttpClient:
        """Initialize and return the ChromaDB client."""
        global _chroma_client
        if _chroma_client is None:
            try:
                _chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
                _chroma_client.heartbeat()
                logger.info(f"ChromaDB: Successfully connected to http://{CHROMADB_HOST}:{CHROMADB_PORT}")
            except Exception as e:
                logger.error(f"ChromaDB: Error connecting to ChromaDB at http://{CHROMADB_HOST}:{CHROMADB_PORT}: {e}")
                raise ConnectionError(f"Could not connect to ChromaDB: {e}") from e
        return _chroma_client
    
    def _get_embedding_function(self) -> embedding_functions.SentenceTransformerEmbeddingFunction:
        # TODO: figure out how to integrate OpenAI/Ollama/HF embedding models
        """Initialize and return the embedding function."""
        global _embedding_function
        if _embedding_function is None:
            try:
                _embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=EMBEDDING_MODEL_NAME
                )
                logger.info(f"ChromaDB: Initialized embedding function with model '{EMBEDDING_MODEL_NAME}'")
            except ImportError:
                logger.error("ChromaDB: 'sentence-transformers' not installed. Install with `pip install sentence-transformers`.")
                raise
            except Exception as e:
                logger.error(f"ChromaDB: Error initializing embedding function: {e}")
                raise
        return _embedding_function
    
    def _get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Initialize and return the text splitter."""
        global _text_splitter
        if _text_splitter is None:
            _text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
        return _text_splitter
    
    def _get_collection(self, collection_name: str = "main_documents") -> Chroma:
        """Get or create a collection."""
        global _chroma_instances
        if collection_name not in _chroma_instances:
            try:
                _chroma_instances[collection_name] = Chroma(
                    client=self.client,
                    collection_name=collection_name,
                    embedding_function=self.embedding_function,
                )
                logger.info(f"ChromaDB: Collection '{collection_name}' ready.")
            except Exception as e:
                logger.error(f"ChromaDB: Error initializing collection '{collection_name}': {e}")
                raise RuntimeError(f"Failed to initialize collection: {e}") from e
        return _chroma_instances[collection_name]
    
    def _generate_content_hash(self, text: str) -> str:
        """Generate a SHA256 hash of the input text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _generate_chunk_id(self, content_hash: str, chunk_index: int) -> str:
        """Generate a unique ID for a document chunk."""
        return f"{content_hash}_chunk_{chunk_index}"
    
    def _format_datetime(self, dt: Any) -> str:
        """Convert datetime object or ISO string to ISO format string."""
        if isinstance(dt, datetime):
            return dt.isoformat()
        elif isinstance(dt, str):
            return dt
        else:
            return datetime.now(datetime.timezone.utc).isoformat()
    
    def _create_base_metadata(self, source_id: str, creator_id: str, knowledge_base_id: str, 
                            additional_metadata: Optional[Dict[str, Any]] = None,
                            created_date: Optional[Any] = None) -> Dict[str, Any]:
        """Create base metadata with required fields."""
        now = datetime.now(datetime.timezone.utc).isoformat()
        metadata = {
            "source_ids": [source_id],
            "created_date": self._format_datetime(created_date) if created_date else now,
            "modified_date": now,
            "creator_id": creator_id,
            "knowledge_base_ids": [knowledge_base_id],
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        return metadata
    
    def add_document(
        self,
        source_id: str,
        document_content: str,
        creator_id: str,
        knowledge_base_id: str,
        additional_metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = "main_documents"
    ) -> Tuple[bool, str, List[str]]:
        """
        Add a source document to the collection with automatic chunking and knowledge base management.
        
        Args:
            source_id: Unique identifier for the source document
            document_content: The text content of the source document
            creator_id: ID of the user who created the source document
            knowledge_base_id: ID of the knowledge base this source document belongs to
            additional_metadata: Optional additional metadata to store with the source document
            collection_name: Name of the collection to add to
            
        Returns:
            Tuple of (success, message, list_of_chunk_ids)
        """
        try:
            collection = self._get_collection(collection_name)
            content_hash = self._generate_content_hash(document_content)
            
            # Check if source document already exists by hash (for deduplication)
            existing_chunks = self._get_document_chunks_by_hash(content_hash, collection_name)
            
            if existing_chunks:
                # Source document exists, add knowledge_base_id to existing chunks
                return self._add_to_existing_document(
                    existing_chunks, source_id, knowledge_base_id, collection_name
                )
            
            # Split source document into chunks
            chunks = self.text_splitter.split_text(document_content)
            if not chunks:
                return False, "Source document could not be split into chunks", []
            
            # Prepare chunks and IDs for batch insertion
            documents_to_add = []
            chunk_ids = []
            
            base_metadata = self._create_base_metadata(source_id, creator_id, knowledge_base_id, additional_metadata)
            
            for i, chunk_content in enumerate(chunks):
                chunk_id = self._generate_chunk_id(content_hash, i)
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "content_hash": content_hash,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                })
                
                doc = Document(page_content=chunk_content, metadata=chunk_metadata)
                documents_to_add.append(doc)
                chunk_ids.append(chunk_id)
            
            # Add all chunks to the collection
            collection.add_documents(documents_to_add, ids=chunk_ids)
            
            logger.info(f"ChromaDB: Added source document {source_id} with {len(chunks)} chunks. Content hash: {content_hash}")
            return True, f"Source document added with {len(chunks)} chunks", chunk_ids
            
        except Exception as e:
            logger.error(f"ChromaDB: Error adding source document {source_id}: {e}")
            return False, f"Error adding source document: {e}", []
    
    def _get_document_chunks_by_hash(self, content_hash: str, collection_name: str) -> List[Dict[str, Any]]:
        """Get all chunks for a source document by its content hash."""
        try:
            collection = self._get_collection(collection_name)
            results = collection._collection.get(
                where={"content_hash": content_hash},
                include=["metadatas", "documents"]
            )
            
            chunks = []
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    chunks.append({
                        'id': chunk_id,
                        'metadata': results['metadatas'][i],
                        'content': results['documents'][i]
                    })
            return chunks
        except Exception as e:
            logger.error(f"ChromaDB: Error getting chunks for source document by hash: {e}")
            return []
    
    def _get_document_chunks_by_source_id(self, source_id: str, collection_name: str) -> List[Dict[str, Any]]:
        """Get all chunks for a source document by its source_id."""
        try:
            collection = self._get_collection(collection_name)
            results = collection._collection.get(
                where={"source_ids": {"$in": [source_id]}},
                include=["metadatas", "documents"]
            )
            
            chunks = []
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    chunks.append({
                        'id': chunk_id,
                        'metadata': results['metadatas'][i],
                        'content': results['documents'][i]
                    })
            return chunks
        except Exception as e:
            logger.error(f"ChromaDB: Error getting chunks for source document by source_id: {e}")
            return []
    
    def _add_to_existing_document(
        self, 
        existing_chunks: List[Dict[str, Any]], 
        source_id: str,
        knowledge_base_id: str, 
        collection_name: str
    ) -> Tuple[bool, str, List[str]]:
        """Add a source_id and knowledge base ID to existing chunks of a source document."""
        try:
            collection = self._get_collection(collection_name)
            chunk_ids = []
            
            for chunk in existing_chunks:
                chunk_id = chunk['id']
                metadata = chunk['metadata']
                
                # Get current source IDs
                current_source_ids = metadata.get('source_ids', [])
                if isinstance(current_source_ids, str):
                    current_source_ids = [current_source_ids]
                
                # Get current knowledge base IDs
                current_kb_ids = metadata.get('knowledge_base_ids', [])
                if isinstance(current_kb_ids, str):
                    current_kb_ids = [current_kb_ids]
                
                # Add new source ID if not already present
                if source_id not in current_source_ids:
                    current_source_ids.append(source_id)
                    metadata['source_ids'] = current_source_ids
                
                # Add new knowledge base ID if not already present
                if knowledge_base_id not in current_kb_ids:
                    current_kb_ids.append(knowledge_base_id)
                    metadata['knowledge_base_ids'] = current_kb_ids
                
                metadata['modified_date'] = datetime.now(datetime.timezone.utc).isoformat()
                
                # Update the chunk metadata
                collection._collection.update(
                    ids=[chunk_id],
                    metadatas=[metadata]
                )
                
                chunk_ids.append(chunk_id)
            
            logger.info(f"ChromaDB: Added source {source_id} and knowledge base {knowledge_base_id} to existing source document")
            return True, f"Added source and knowledge base to existing source document with {len(chunk_ids)} chunks", chunk_ids
            
        except Exception as e:
            logger.error(f"ChromaDB: Error adding source and knowledge base to existing source document: {e}")
            return False, f"Error updating existing source document: {e}", []
    
    def remove_document(
        self,
        source_id: str,
        knowledge_base_id: str,
        collection_name: str = "main_documents"
    ) -> Tuple[bool, str]:
        """
        Remove a source_id and knowledge base ID from all chunks of a source document, 
        or remove all chunks entirely if no source_ids and knowledge bases remain.
        
        Args:
            source_id: Unique identifier for the source document
            knowledge_base_id: Knowledge base ID to remove
            collection_name: Name of the collection
            
        Returns:
            Tuple of (success, message)
        """
        try:
            collection = self._get_collection(collection_name)
            
            # Get all chunks for this source document
            chunks = self._get_document_chunks_by_source_id(source_id, collection_name)
            
            if not chunks:
                return False, f"No source document found with source_id: {source_id}"
            
            chunks_to_delete = []
            chunks_to_update = []
            
            for chunk in chunks:
                chunk_id = chunk['id']
                metadata = chunk['metadata']
                
                # Get current source IDs
                current_source_ids = metadata.get('source_ids', [])
                if isinstance(current_source_ids, str):
                    current_source_ids = [current_source_ids]
                
                # Get current knowledge base IDs
                current_kb_ids = metadata.get('knowledge_base_ids', [])
                if isinstance(current_kb_ids, str):
                    current_kb_ids = [current_kb_ids]
                
                # Remove the source ID
                if source_id in current_source_ids:
                    current_source_ids.remove(source_id)
                
                # Remove the knowledge base ID
                if knowledge_base_id in current_kb_ids:
                    current_kb_ids.remove(knowledge_base_id)
                
                if not current_source_ids and not current_kb_ids:
                    # No source IDs or knowledge bases left, mark chunk for deletion
                    chunks_to_delete.append(chunk_id)
                else:
                    # Update chunk metadata with remaining IDs
                    metadata['source_ids'] = current_source_ids
                    metadata['knowledge_base_ids'] = current_kb_ids
                    metadata['modified_date'] = datetime.now(datetime.timezone.utc).isoformat()
                    chunks_to_update.append((chunk_id, metadata))
            
            # Delete chunks with no remaining source IDs or knowledge bases
            if chunks_to_delete:
                collection._collection.delete(ids=chunks_to_delete)
                logger.info(f"ChromaDB: Deleted {len(chunks_to_delete)} chunks with no remaining source IDs or knowledge bases")
            
            # Update chunks with remaining IDs
            if chunks_to_update:
                for chunk_id, metadata in chunks_to_update:
                    collection._collection.update(
                        ids=[chunk_id],
                        metadatas=[metadata]
                    )
                logger.info(f"ChromaDB: Updated {len(chunks_to_update)} chunks, removed source {source_id} and knowledge base {knowledge_base_id}")
            
            return True, f"Processed source document {source_id}: {len(chunks_to_delete)} chunks deleted, {len(chunks_to_update)} chunks updated"
            
        except Exception as e:
            logger.error(f"ChromaDB: Error removing source document {source_id}: {e}")
            return False, f"Error removing source document: {e}"
    
    def query_documents(
        self,
        query_text: Optional[str] = None,
        chunk_ids: Optional[List[str]] = None,
        source_ids: Optional[List[str]] = None,
        knowledge_base_ids: Optional[List[str]] = None,
        creator_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        n_results: int = 5,
        collection_name: str = "main_documents"
    ) -> List[Tuple[Document, float]]:
        """
        Query chunks from source documents with various filters.
        
        Args:
            query_text: Text to search for (semantic search)
            chunk_ids: Specific chunk IDs to retrieve
            source_ids: Filter by source document IDs
            knowledge_base_ids: Filter by knowledge base IDs
            creator_id: Filter by creator ID
            date_from: Filter source documents created after this date (ISO format)
            date_to: Filter source documents created before this date (ISO format)
            n_results: Maximum number of chunks to return
            collection_name: Name of the collection to query
            
        Returns:
            List of (Document, score) tuples representing chunks
        """
        try:
            collection = self._get_collection(collection_name)
            
            # Build metadata filter
            where_filter = {}
            
            if source_ids:
                # Use $in operator for source_ids array
                where_filter["source_ids"] = {"$in": source_ids}
            
            if knowledge_base_ids:
                # Use $in operator for knowledge_base_ids array
                where_filter["knowledge_base_ids"] = {"$in": knowledge_base_ids}
            
            if creator_id:
                where_filter["creator_id"] = creator_id
            
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = date_from
                if date_to:
                    date_filter["$lte"] = date_to
                where_filter["created_date"] = date_filter
            
            # Query by specific chunk IDs
            if chunk_ids:
                results = collection._collection.get(
                    ids=chunk_ids,
                    where=where_filter if where_filter else None,
                    include=["documents", "metadatas", "distances"]
                )
                
                documents_with_scores = []
                if results['ids']:
                    for i, doc_id in enumerate(results['ids']):
                        doc = Document(
                            page_content=results['documents'][i],
                            metadata=results['metadatas'][i]
                        )
                        # For direct ID queries, we don't have similarity scores
                        documents_with_scores.append((doc, 0.0))
                
                return documents_with_scores
            
            # Semantic search with text query
            if query_text:
                results = collection.similarity_search_with_score(
                    query=query_text,
                    k=n_results,
                    filter=where_filter if where_filter else None
                )
                return results
            
            # If no query text and no specific IDs, return recent chunks
            results = collection._collection.get(
                where=where_filter if where_filter else None,
                limit=n_results,
                include=["documents", "metadatas"]
            )
            
            documents_with_scores = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    doc = Document(
                        page_content=results['documents'][i],
                        metadata=results['metadatas'][i]
                    )
                    documents_with_scores.append((doc, 0.0))
            
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"ChromaDB: Error querying chunks: {e}")
            raise RuntimeError(f"Failed to query ChromaDB: {e}") from e
    
    def get_document_by_hash(
        self, 
        content_hash: str, 
        collection_name: str = "main_documents"
    ) -> Optional[str]:
        """
        Reconstruct the original source document from its chunks.
        
        Args:
            content_hash: Hash of the source document content
            collection_name: Name of the collection
            
        Returns:
            The reconstructed source document content or None if not found
        """
        try:
            chunks = self._get_document_chunks_by_hash(content_hash, collection_name)
            if not chunks:
                return None
            
            # Sort chunks by index
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            
            # Reconstruct the source document
            reconstructed_content = ""
            for chunk in chunks:
                reconstructed_content += chunk['content']
            
            return reconstructed_content
            
        except Exception as e:
            logger.error(f"ChromaDB: Error reconstructing source document: {e}")
            return None
    
    def get_document_by_source_id(
        self, 
        source_id: str, 
        collection_name: str = "main_documents"
    ) -> Optional[str]:
        """
        Reconstruct the original source document from its chunks using source_id.
        
        Args:
            source_id: Unique identifier for the source document
            collection_name: Name of the collection
            
        Returns:
            The reconstructed source document content or None if not found
        """
        try:
            chunks = self._get_document_chunks_by_source_id(source_id, collection_name)
            if not chunks:
                return None
            
            # Sort chunks by index
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            
            # Reconstruct the source document
            reconstructed_content = ""
            for chunk in chunks:
                reconstructed_content += chunk['content']
            
            return reconstructed_content
            
        except Exception as e:
            logger.error(f"ChromaDB: Error reconstructing source document {source_id}: {e}")
            return None
    
    def update_document_metadata(
        self,
        source_id: str,
        new_metadata: Dict[str, Any],
        collection_name: str = "main_documents"
    ) -> Tuple[bool, str]:
        """
        Update metadata for all chunks of a source document.
        
        Args:
            source_id: Unique identifier for the source document
            new_metadata: New metadata to merge with existing metadata
            collection_name: Name of the collection
            
        Returns:
            Tuple of (success, message)
        """
        try:
            collection = self._get_collection(collection_name)
            
            # Get all chunks for this source document
            chunks = self._get_document_chunks_by_source_id(source_id, collection_name)
            
            if not chunks:
                return False, f"No source document found with source_id: {source_id}"
            
            chunks_updated = 0
            
            for chunk in chunks:
                chunk_id = chunk['id']
                metadata = chunk['metadata']
                
                # Update metadata while preserving required fields
                metadata.update(new_metadata)
                metadata['modified_date'] = datetime.now(datetime.timezone.utc).isoformat()
                
                # Update the chunk metadata
                collection._collection.update(
                    ids=[chunk_id],
                    metadatas=[metadata]
                )
                chunks_updated += 1
            
            logger.info(f"ChromaDB: Updated metadata for {chunks_updated} chunks of source document {source_id}")
            return True, f"Updated metadata for {chunks_updated} chunks"
            
        except Exception as e:
            logger.error(f"ChromaDB: Error updating metadata for source document {source_id}: {e}")
            return False, f"Error updating metadata: {e}"
    
    def count_documents(self, collection_name: str = "main_documents") -> int:
        """Return the total number of chunks in the collection."""
        try:
            collection = self._get_collection(collection_name)
            return collection._collection.count()
        except Exception as e:
            logger.error(f"ChromaDB: Error counting chunks: {e}")
            raise RuntimeError(f"Failed to count chunks in ChromaDB: {e}") from e
    
    def list_collections(self) -> List[str]:
        """List all collection names."""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"ChromaDB: Error listing collections: {e}")
            raise RuntimeError(f"Failed to list collections from ChromaDB: {e}") from e
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire collection."""
        try:
            self.client.delete_collection(name=collection_name)
            # Remove from global instances cache
            global _chroma_instances
            if collection_name in _chroma_instances:
                del _chroma_instances[collection_name]
            logger.info(f"ChromaDB: Collection '{collection_name}' deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"ChromaDB: Error deleting collection '{collection_name}': {e}")
            raise RuntimeError(f"Failed to delete collection '{collection_name}': {e}") from e
