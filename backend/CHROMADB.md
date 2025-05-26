# ChromaDB Service

This document describes the ChromaDB service that provides advanced source document management with knowledge base support, automatic chunking, and comprehensive metadata tracking.

## Features

### Core Functionality

- **Document Chunking**: Automatically splits large source documents into manageable chunks using LangChain's RecursiveCharacterTextSplitter
- **Knowledge Base Management**: Source documents can belong to multiple knowledge bases simultaneously
- **Metadata Tracking**: Comprehensive metadata including creation/modification dates, creator ID, source_id, and knowledge base associations
- **Deduplication**: Intelligent handling of duplicate source documents across knowledge bases using content hashes
- **Semantic Search**: Vector-based similarity search with metadata filtering

### Required Metadata Fields

Every chunk includes the following metadata:

- `source_ids`: List of unique identifiers for source documents
- `created_date`: ISO timestamp of when the source document was first added
- `modified_date`: ISO timestamp of the last modification
- `creator_id`: ID of the user who created the source document
- `knowledge_base_ids`: List of all knowledge base IDs the source document belongs to

## Data Model

### Document Storage Structure

Source documents are stored as chunks in ChromaDB with the following structure:

#### Chunk Identification

- **Chunk ID**: `{content_hash}_chunk_{index}` (e.g., `abc123def456_chunk_0`)
- **Source IDs**: List of unique identifiers linking to source documents
- **Content Hash**: SHA256 hash of the original source document content (used for deduplication)
- **Chunk Index**: Sequential number starting from 0

#### Document Object Structure

Each chunk is stored as a LangChain `Document` object with:

```python
Document(
    page_content="The actual text content of this chunk...",
    metadata={
        # Required fields
        "source_ids": ["doc_12345", "doc_67890"],
        "created_date": "2024-01-15T10:30:00.123456+00:00",
        "modified_date": "2024-01-15T10:30:00.123456+00:00",
        "creator_id": "user123",
        "knowledge_base_ids": ["kb001", "kb002"],  # All associated KBs

        # Chunk-specific fields
        "content_hash": "abc123def456...",  # SHA256 of original source document (for deduplication)
        "chunk_index": 0,  # Position in the original source document
        "total_chunks": 5,  # Total number of chunks for this source document

        # Optional metadata
        "title": "Document Title",
        "category": "research",
        "source": "upload",
        # ... any additional metadata
    }
)
```

#### Metadata Field Details

| Field                | Type         | Required | Description                                                                  |
| -------------------- | ------------ | -------- | ---------------------------------------------------------------------------- |
| `source_ids`         | list[string] | Yes      | List of unique identifiers linking to source documents                       |
| `created_date`       | string       | Yes      | ISO 8601 timestamp with timezone when source document was first added        |
| `modified_date`      | string       | Yes      | ISO 8601 timestamp with timezone of last modification                        |
| `creator_id`         | string       | Yes      | Identifier of the user who created the source document                       |
| `knowledge_base_ids` | list[string] | Yes      | List of all knowledge base IDs this source document belongs to               |
| `content_hash`       | string       | Yes      | SHA256 hash of the original source document content (for deduplication only) |
| `chunk_index`        | integer      | Yes      | Zero-based index of this chunk in the source document                        |
| `total_chunks`       | integer      | Yes      | Total number of chunks the source document was split into                    |
| `*`                  | any          | No       | Additional user-provided metadata fields                                     |

#### Document Lifecycle

1. **Source Document Addition**:

   - Original source document is hashed (SHA256) for deduplication check
   - If hash exists, source_id and knowledge_base_id are added to existing chunks' lists
   - If new, source document is split into chunks using RecursiveCharacterTextSplitter
   - Each chunk gets a unique ID: `{hash}_chunk_{index}`
   - Metadata is attached to each chunk
   - All chunks are stored in batch

2. **Duplicate Handling**:

   - If same content hash exists, knowledge_base_id & source_id is added to existing chunks
   - No new chunks are created for duplicate source document content
   - `modified_date` is updated on existing chunks

3. **Knowledge Base Management**:

   - Source documents can belong to multiple knowledge bases
   - `knowledge_base_ids` field tracks all associations
   - Removing from one KB doesn't affect others

4. **Source Document Removal**:
   - Knowledge base ID is removed from `knowledge_base_ids` list in all chunks
   - Source ID is removed from `source_ids` list in all chunks
   - If list becomes empty, all chunks are deleted entirely
   - `modified_date` is updated during removal process

#### Chunking Strategy

The service uses `RecursiveCharacterTextSplitter` with:

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Separators**: `["\n\n", "\n", " ", ""]` (paragraph, line, word, character)

This ensures:

- Semantic coherence within chunks
- Context preservation across chunk boundaries
- Optimal size for embedding models
- Efficient retrieval performance

#### Vector Embeddings

- Each chunk's `page_content` is converted to embeddings using the configured model
- Default model: `all-MiniLM-L6-v2` (384 dimensions)
- Embeddings enable semantic similarity search
- ChromaDB automatically handles embedding generation and indexing

## API Reference

### ChromaDBService Class

#### Initialization

```python
from app.services.chroma import get_chroma_service

service = get_chroma_service()
```

#### Methods

##### `add_document(source_id, document_content, creator_id, knowledge_base_id, additional_metadata=None, collection_name="main_documents")`

Adds a source document to the collection with automatic chunking and knowledge base management.

**Parameters:**

- `source_id` (str): Unique identifier for the source document
- `document_content` (str): The text content of the source document
- `creator_id` (str): ID of the user who created the source document
- `knowledge_base_id` (str): ID of the knowledge base this source document belongs to
- `additional_metadata` (dict, optional): Additional metadata to store with the source document
- `collection_name` (str, optional): Name of the collection to add to

**Returns:**

- `Tuple[bool, str, List[str]]`: (success, message, list_of_chunk_ids)

**Behavior:**

- If the source document content already exists (same content hash), adds the knowledge base ID to existing chunks
- If it's a new source document, splits it into chunks and stores each chunk with metadata including source_id

**Example:**

```python
from datetime import datetime

success, msg, chunk_ids = service.add_document(
    source_id="doc_12345",
    document_content="Your source document content here...",
    creator_id="user123",
    knowledge_base_id="kb001",
    additional_metadata={"title": "My Document", "category": "research"}
)
```

##### `remove_document(source_id, knowledge_base_id, collection_name="main_documents")`

Removes a knowledge base ID from all chunks of a source document, or removes all chunks entirely if no knowledge bases remain.

**Parameters:**

- `source_id` (str): Unique identifier for the source document
- `knowledge_base_id` (str): Knowledge base ID to remove
- `collection_name` (str, optional): Name of the collection

**Returns:**

- `Tuple[bool, str]`: (success, message)

**Behavior:**

- Removes the specified knowledge base ID from all chunks of the source document
- If no knowledge bases remain for any chunk, deletes all chunks entirely
- Updates modification timestamps

**Example:**

```python
# Remove source document from knowledge base
success, msg = service.remove_document(
    source_id="doc_12345",
    knowledge_base_id="kb001"
)
```

##### `update_document_metadata(source_id, new_metadata, collection_name="main_documents")`

Updates metadata for all chunks of a source document.

**Parameters:**

- `source_id` (str): Unique identifier for the source document
- `new_metadata` (dict): New metadata to merge with existing metadata
- `collection_name` (str, optional): Name of the collection

**Returns:**

- `Tuple[bool, str]`: (success, message)

**Example:**

```python
# Update metadata for a source document
success, msg = service.update_document_metadata(
    source_id="doc_12345",
    new_metadata={"title": "Updated Title", "category": "updated_research"}
)
```

##### `query_documents(query_text=None, chunk_ids=None, source_ids=None, knowledge_base_ids=None, creator_id=None, date_from=None, date_to=None, n_results=5, collection_name="main_documents")`

Query chunks from source documents with various filters and search methods.

**Parameters:**

- `query_text` (str, optional): Text to search for (semantic search)
- `chunk_ids` (List[str], optional): Specific chunk IDs to retrieve
- `source_ids` (List[str], optional): Filter by source document IDs
- `knowledge_base_ids` (List[str], optional): Filter by knowledge base IDs
- `creator_id` (str, optional): Filter by creator ID
- `date_from` (str, optional): Filter source documents created after this date (ISO format)
- `date_to` (str, optional): Filter source documents created before this date (ISO format)
- `n_results` (int, optional): Maximum number of chunks to return
- `collection_name` (str, optional): Name of the collection to query

**Returns:**

- `List[Tuple[Document, float]]`: List of (Document, similarity_score) tuples representing chunks

**Examples:**

```python
# Semantic search within specific knowledge bases
results = service.query_documents(
    query_text="machine learning algorithms",
    knowledge_base_ids=["kb001", "kb002"],
    n_results=10
)

# Get chunks from specific source documents
results = service.query_documents(
    source_ids=["doc_12345", "doc_67890"],
    n_results=20
)

# Get chunks by specific creator
results = service.query_documents(
    creator_id="user123",
    n_results=20
)

# Date range query
results = service.query_documents(
    date_from="2024-01-01T00:00:00",
    date_to="2024-12-31T23:59:59",
    knowledge_base_ids=["kb001"]
)

# Get specific chunks by ID
results = service.query_documents(
    chunk_ids=["doc1_chunk_0", "doc2_chunk_1"]
)
```

##### `get_document_by_source_id(source_id, collection_name="main_documents")`

Reconstructs the original source document from its chunks using source_id.

**Parameters:**

- `source_id` (str): Unique identifier for the source document
- `collection_name` (str, optional): Name of the collection

**Returns:**

- `Optional[str]`: The reconstructed source document content or None if not found

##### `count_documents(collection_name="main_documents")`

Returns the total number of chunks in the collection.

##### `list_collections()`

Lists all collection names.

##### `delete_collection(collection_name)`

Deletes an entire collection.

## Configuration

### Environment Variables

- `CHROMADB_HOST`: ChromaDB server host (default: "chromadb")
- `CHROMADB_PORT`: ChromaDB server port (default: 8000)
- `EMBEDDING_MODEL_NAME`: Sentence transformer model name (default: "all-MiniLM-L6-v2")

### Text Splitter Configuration

The service uses `RecursiveCharacterTextSplitter` with the following default settings:

- `chunk_size`: 1000 characters
- `chunk_overlap`: 200 characters
- `separators`: ["\n\n", "\n", " ", ""]

## Docker Configuration

The ChromaDB service is configured in `docker-compose.yml`:

```yaml
chromadb:
  image: chromadb/chroma:latest
  ports:
    - "8001:8000" # External port 8001 maps to internal port 8000
  volumes:
    - chromadb_data:/chroma/chroma
  environment:
    - IS_PERSISTENT=TRUE
    - ANONYMIZED_TELEMETRY=FALSE
  restart: unless-stopped
```

## Usage Examples

### Basic Source Document Management

```python
from app.services.chroma import get_chroma_service
from datetime import datetime

service = get_chroma_service()

# Add a source document
success, msg, chunk_ids = service.add_document(
    source_id="doc_12345",
    document_content="Long source document content...",
    creator_id="user123",
    knowledge_base_id="research_kb",
    additional_metadata={"title": "Research Paper", "year": 2024}
)

# Query chunks from source documents
results = service.query_documents(
    query_text="research findings",
    knowledge_base_ids=["research_kb"],
    n_results=5
)

# Update metadata for a source document
success, msg = service.update_document_metadata(
    source_id="doc_12345",
    new_metadata={"title": "Updated Research Paper", "status": "reviewed"}
)

# Remove source document from knowledge base
success, msg = service.remove_document(
    source_id="doc_12345",
    knowledge_base_id="research_kb"
)

# Reconstruct original document
original_content = service.get_document_by_source_id("doc_12345")
```

### Multi-Knowledge Base Source Document

```python
# Add source document to first knowledge base
service.add_document(
    source_id="doc_shared_123",
    document_content="Shared source document content...",
    creator_id="user1",
    knowledge_base_id="kb1"
)

# Add same source document to second knowledge base (content hash matches)
service.add_document(
    source_id="doc_shared_123",  # Same source_id
    document_content="Shared source document content...",  # Same content
    creator_id="user2",
    knowledge_base_id="kb2"
)

# Query each knowledge base separately
kb1_results = service.query_documents(knowledge_base_ids=["kb1"])
kb2_results = service.query_documents(knowledge_base_ids=["kb2"])

# Query specific source documents
source_results = service.query_documents(source_ids=["doc_shared_123"])

# Remove from one knowledge base (source document remains in the other)
service.remove_document(source_id="doc_shared_123", knowledge_base_id="kb1")
```

## Testing

To test the service functionality, you can create a simple test script or use it interactively:

```python
from app.services.chroma import get_chroma_service

# Initialize service
service = get_chroma_service()

# Test adding a source document
success, msg, chunk_ids = service.add_document(
    source_id="test_doc_001",
    document_content="This is a test source document with some content to verify chunking works properly.",
    creator_id="test_user",
    knowledge_base_id="test_kb",
    additional_metadata={"title": "Test Document"}
)
print(f"Add result: {success}, {msg}")

# Test querying chunks
results = service.query_documents(
    query_text="test document",
    knowledge_base_ids=["test_kb"],
    n_results=5
)
print(f"Found {len(results)} chunks")

# Test metadata update
success, msg = service.update_document_metadata(
    source_id="test_doc_001",
    new_metadata={"title": "Updated Test Document", "status": "tested"}
)
print(f"Update result: {success}, {msg}")

# Test document reconstruction
original_content = service.get_document_by_source_id("test_doc_001")
print(f"Reconstructed document length: {len(original_content) if original_content else 0}")

# Test removal
success, msg = service.remove_document(
    source_id="test_doc_001",
    knowledge_base_id="test_kb"
)
print(f"Remove result: {success}, {msg}")
```

Key areas to test:

1. Source document addition with chunking
2. Multi-knowledge base functionality
3. Query with various filters (source_ids, knowledge_base_ids, etc.)
4. Metadata updates by source_id
5. Source document removal by source_id
6. Source document reconstruction by source_id
7. Collection statistics

## Error Handling

The service includes comprehensive error handling and logging:

- Connection errors to ChromaDB
- Source document processing errors
- Query execution errors
- Metadata validation errors

All errors are logged using Python's logging module with appropriate log levels.

## Performance Considerations

- **Chunking**: Large source documents are automatically split into 1000-character chunks with 200-character overlap
- **Batch Operations**: Multiple chunks are added in batch operations for efficiency
- **Caching**: Collection instances are cached to avoid repeated initialization
- **Indexing**: ChromaDB automatically indexes embeddings for fast similarity search

## Security Notes

- Content hashes are used for deduplication and source document identification
- Metadata is stored alongside chunks
- No sensitive information should be stored in metadata
- Access control should be implemented at the application level
