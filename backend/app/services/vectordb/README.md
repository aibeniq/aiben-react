# Vector Database Service

## 🎯 Overview

This service provides straightforward CRUD operations for vector-based document storage and retrieval, optimized for simplicity and performance rather than enterprise abstractions.

### Key Features

- **Simple CRUD Operations**: Add, search, and remove documents with embeddings
- **Multiple Search Types**: Semantic, keyword, and hybrid search capabilities
- **Multi-Model Support**: Use different embedding models simultaneously
- **Automatic Chunking**: Smart text splitting with configurable overlap
- **Deduplication**: Prevents duplicate content storage
- **Access Control**: User-based filtering and permissions
- **Batch Processing**: Efficient handling of large document sets

## 🏗️ Architecture

```
vectordb/
├── services/vector_service.py    # Main VectorDBService class
├── embeddings.py                 # Simplified embedding integration
├── core/models.py               # Request/response models
├── config/settings.py           # Configuration management
└── config/schemas.py            # Weaviate schema definitions
```

## 🚀 Quick Start

### Basic Usage

```python
from app.services.vectordb import VectorDBService, AddSourceRequest, SearchRequest

# Initialize service
vector_service = VectorDBService()

# Add a document
add_request = AddSourceRequest(
    org_id="your_org_id",
    source_path="document.pdf",
    content="Your document content here...",
    embedding_models=["text-embedding-3-small"],
    user_id="user123",
    knowledge_base_id="kb456"
)

response = await vector_service.add_source(add_request)
print(f"Added source: {response.source_id} with {response.chunks_created} chunks")

# Search documents
search_request = SearchRequest(
    query="What is machine learning?",
    org_id="your_org_id",
    embedding_model="text-embedding-3-small",
    limit=5
)

results = await vector_service.search_chunks(search_request)
for result in results.results:
    print(f"Score: {result.score:.3f} - {result.content[:100]}...")
```

## 📋 API Reference

### VectorDBService

The main service class providing all vector database operations.

#### Methods

##### `add_source(request: AddSourceRequest) -> AddSourceResponse`

Add a new document source with automatic chunking and embedding generation.

**Parameters:**

- `org_id`: Organization identifier
- `source_path`: Path or identifier for the source
- `content`: Text content to be indexed
- `embedding_models`: List of embedding models to use
- `user_id`: User adding the content
- `knowledge_base_id`: Knowledge base identifier
- `metadata`: Optional source metadata
- `chunk_size`: Chunk size in words (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)

**Returns:**

- `source_id`: Generated unique identifier
- `chunks_created`: Number of chunks created
- `processing_time_ms`: Processing time
- `was_duplicate`: Whether content was already present

##### `search_chunks(request: SearchRequest) -> SearchResponse`

Search through indexed content using various search strategies.

**Parameters:**

- `query`: Search query text
- `org_id`: Organization identifier
- `embedding_model`: Model used for semantic search
- `search_type`: `SEMANTIC`, `KEYWORD`, or `HYBRID`
- `filters`: Optional filtering parameters
- `limit`: Maximum results (1-100)
- `alpha`: Hybrid search weighting (0.0-1.0)

**Returns:**

- `results`: List of search results with scores
- `total_results`: Number of results found
- `processing_time_ms`: Search time

##### `remove_source(request: RemoveSourceRequest) -> RemoveSourceResponse`

Remove a source and all associated chunks.

**Parameters:**

- `org_id`: Organization identifier
- `source_id`: Source to remove
- `user_id`: User requesting removal

**Returns:**

- `success`: Whether removal succeeded
- `chunks_removed`: Number of chunks deleted
- `processing_time_ms`: Processing time

##### `health_check() -> Dict[str, Any]`

Check service health and connectivity.

**Returns:**

- `status`: Overall health status
- `weaviate_connected`: Database connectivity
- `embedding_services`: Model availability
- `timestamp`: Check timestamp

## 🔍 Search Types

### Semantic Search

Uses embedding vectors for contextual similarity matching.

```python
SearchRequest(
    query="machine learning algorithms",
    search_type=SearchType.SEMANTIC,
    embedding_model="text-embedding-3-small"
)
```

### Keyword Search

Traditional BM25-based text matching.

```python
SearchRequest(
    query="neural networks",
    search_type=SearchType.KEYWORD
)
```

### Hybrid Search

Combines semantic and keyword search with configurable weighting.

```python
SearchRequest(
    query="deep learning",
    search_type=SearchType.HYBRID,
    alpha=0.7  # 70% semantic, 30% keyword
)
```

## 🎛️ Configuration

### Environment Variables

```bash
# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_api_key

# Embedding Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Chunking Configuration
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
MAX_CHUNK_SIZE=8000

# Performance Settings
BATCH_SIZE=50
MAX_CONCURRENT_EMBEDDINGS=10
RETRY_ATTEMPTS=3
```

### Supported Embedding Models

```python
# OpenAI Models (recommended)
"text-embedding-3-small"    # 1536 dims, cost-effective
"text-embedding-3-large"    # 3072 dims, higher quality
"text-embedding-ada-002"    # 1536 dims, legacy

# Custom models supported via existing embeddings service
```

## 🔒 Access Control & Filtering

### Filter Options

```python
from app.services.vectordb.core.models import FilterParams

filters = FilterParams(
    user_id="specific_user",
    knowledge_base_ids=["kb1", "kb2"],
    source_ids=["source1", "source2"],
    access_users=["user1", "user2"]
)

search_request = SearchRequest(
    query="your query",
    org_id="org_id",
    filters=filters
)
```

## 📊 Performance Considerations

### Batch Processing

- Documents are processed in configurable batches
- Concurrent embedding generation with rate limiting
- Automatic retry logic with exponential backoff

### Optimization Tips

- Use smaller chunk sizes (500-1000 words) for better precision
- Implement chunk overlap (150-200 words) for context continuity
- Choose appropriate embedding models based on use case
- Monitor processing times and adjust batch sizes accordingly

## 🔧 Error Handling

The service uses structured exceptions:

```python
from app.services.vectordb.core.exceptions import (
    VectorDBError,
    CollectionNotFoundError,
    EmbeddingError
)

try:
    response = await vector_service.add_source(request)
except CollectionNotFoundError:
    # Handle missing collections
    pass
except EmbeddingError:
    # Handle embedding generation failures
    pass
except VectorDBError as e:
    # Handle general vector DB errors
    print(f"Vector DB error: {e}")
```

## 🏃‍♂️ Development

### Local Setup

1. Start Weaviate instance
2. Configure environment variables
3. Initialize service and create collections

### Testing

```python
# Health check
health = await vector_service.health_check()
print(f"Service status: {health['status']}")

# Test embedding generation
from app.services.vectordb.embeddings import EmbeddingService
embedding_service = EmbeddingService()
# Test basic functionality
```

## 📈 Monitoring

Key metrics to monitor:

- Document ingestion rate and processing times
- Search latency and result quality
- Embedding model usage and costs
- Storage utilization and chunk distribution
- Error rates and failed operations
