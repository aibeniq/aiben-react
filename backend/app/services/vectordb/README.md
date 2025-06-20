# Vector Database Service

## 🎯 TLDR

```python
# Initialize service
vector_service = VectorDBService(client=weaviate_client, org_id="your_org_id")

# Add a document
response = await vector_service.add_source(AddSourceRequest(
    content="Your document content",
    source_type="document",
    created_by_user_id="user123",
    access_users=["user123"],
    embedding_models=["text-embedding-3-small"]
))

# Search documents (filters are required)
results = await vector_service.search_chunks(SearchRequest(
    query_vector=your_vector,
    embedding_model="text-embedding-3-small",
    filter_params=FilterParams(
        access_users=["user123"]
    ),
    limit=5
))
```

## 🎯 Overview

This service provides straightforward CRUD operations for vector-based document storage and retrieval, optimized for simplicity and performance rather than enterprise abstractions.

### Key Features

- **Simple CRUD Operations**: Add, search, and remove documents with embeddings
- **Semantic Search**: Vector-based similarity search using multiple embedding models
- **Multi-Model Support**: Use different embedding models simultaneously
- **Automatic Chunking**: Smart text splitting with configurable overlap
- **Deduplication**: Prevents duplicate content storage
- **Access Control**: User-based filtering and permissions
- **Batch Processing**: Efficient handling of large document sets

## 🏗️ Architecture

```
vectordb/
├── core/
│   ├── vector_service.py    # Main VectorDBService class
│   ├── models.py           # Request/response models
│   └── exceptions.py       # Custom exceptions
├── config/
│   ├── settings.py        # Configuration management
│   └── schemas.py         # Weaviate schema definitions
└── utils/
    └── chunking.py        # Text chunking utilities
```

## 🚀 Quick Start

### Basic Usage

```python
from app.services.vectordb import VectorDBService, AddSourceRequest, SearchRequest
import weaviate

# Initialize Weaviate client
client = weaviate.connect_to_local()  # or appropriate connection method

# Initialize service
vector_service = VectorDBService(client=client, org_id="your_org_id")

# Add a document
add_request = AddSourceRequest(
    content="Your document content here...",
    source_type="document",
    created_by_user_id="user123",
    access_users=["user123"],
    embedding_models=["text-embedding-3-small"]
)

response = await vector_service.add_source(add_request)
print(f"Added source: {response.source_id}")

# Search documents
search_request = SearchRequest(
    query_vector=[0.1, 0.2, ...],  # Your query vector
    embedding_model="text-embedding-3-small",
    limit=5
)

results = await vector_service.search_chunks(search_request)
for chunk in results.chunks:
    print(f"Score: {chunk['score']:.3f} - {chunk['content'][:100]}...")
```

## 📋 API Reference

### VectorDBService

The main service class providing all vector database operations.

#### Methods

##### `add_source(request: AddSourceRequest) -> AddSourceResponse`

Add a new document source with automatic chunking and embedding generation. If the source already exists (based on content hash), it will be reused.

**Required Parameters:**

- `content`: Text content to be indexed
- `source_type`: Type of the source (e.g., "document", "webpage")
- `created_by_user_id`: User adding the content
- `access_users`: List of users with access to the content
- `embedding_models`: List of embedding models to use

**Optional Parameters:**

- `source_path`: Path to the source file (if applicable)
- `file_size`: File size in bytes
- `mime_type`: MIME type of the content
- `title`: Document title
- `author`: Document author
- `description`: Document description
- `tags`: List of tags
- `custom_metadata`: Additional metadata as key-value pairs
- `chunk_size`: Chunk size in words (default: 1000)

**Returns:**

- `success`: Whether the operation succeeded
- `source_id`: Generated unique identifier
- `message`: Status message

##### `search_chunks(request: SearchRequest) -> SearchResponse`

Search through indexed content using vector similarity. Filters are required to ensure proper access control and result relevance.

**Required Parameters:**

- `query_vector`: Vector representation of the query
- `embedding_model`: Model used for semantic search
- `filter_params`: Filter parameters for access control and result filtering
  - `source_ids`: Optional list of specific source IDs to search in
  - `created_by_user_id`: Optional user ID that created the content
  - `access_users`: Optional list of users with access to the content
  - `tags`: Optional list of tags to filter by

**Optional Parameters:**

- `limit`: Maximum results (default: 10)
- `offset`: Result offset for pagination

**Returns:**

- `success`: Whether the search succeeded
- `chunks`: List of matching chunks with scores
- `total`: Total number of results
- `message`: Status message

**Example:**

```python
# Search with filters
search_request = SearchRequest(
    query_vector=your_vector,
    embedding_model="text-embedding-3-small",
    filter_params=FilterParams(
        created_by_user_id="user123",
        access_users=["user123"],
        tags=["important"]
    ),
    limit=5
)

results = await vector_service.search_chunks(search_request)
```

##### `remove_source(request: RemoveSourceRequest) -> RemoveSourceResponse`

Remove a source and all its associated chunks.

**Parameters:**

- `source_id`: Source to remove

**Returns:**

- `success`: Whether removal succeeded
- `message`: Status message

##### `health_check() -> HealthCheckResponse`

Check service health and connectivity.

**Returns:**

- `status`: Overall health status
- `message`: Status message
- `details`: Additional health check details

## 🎛️ Configuration

### Environment Variables

```bash
# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_api_key

# Embedding Configuration
OPENAI_API_KEY=your_openai_key
AWS_REGION=eu-north-1
OLLAMA_BASE_URL=http://ollama:11434
REPLICATE_API_TOKEN=your_replicate_token
```

### Supported Embedding Models

The service uses the external embeddings service which supports:

- **OpenAI Models**

  - `text-embedding-3-small` (1536 dims)
  - `text-embedding-3-large` (3072 dims)
  - `text-embedding-ada-002` (1536 dims)

- **HuggingFace Models**

  - Any model from HuggingFace's model hub

- **AWS Bedrock Models**

  - Amazon Titan Embedding models

- **Ollama Models**

  - Any model available in your Ollama instance

- **Replicate Models**
  - Any embedding model available on Replicate

## 🔒 Access Control & Filtering

### Filter Options

Filters are required for all search operations to ensure proper access control and result relevance. The `FilterParams` class provides the following options:

```python
from app.services.vectordb.core.models import FilterParams

# Basic access control
filters = FilterParams(
    created_by_user_id="user123",
    access_users=["user123"]
)

# Advanced filtering
filters = FilterParams(
    source_ids=["source1", "source2"],  # Search in specific sources
    created_by_user_id="user123",       # Content created by specific user
    access_users=["user1", "user2"],    # Content accessible to specific users
    tags=["tag1", "tag2"]              # Content with specific tags
)

search_request = SearchRequest(
    query_vector=your_vector,
    embedding_model="text-embedding-3-small",
    filter_params=filters
)
```

### Filter Best Practices

1. **Access Control**

   - Always include `access_users` to ensure users can only access content they're authorized to view
   - Use `created_by_user_id` to filter content by creator

2. **Performance**

   - Use `source_ids` to limit search scope when you know which sources to search in
   - Combine multiple filters for more precise results

3. **Organization**
   - Use tags to categorize and filter content
   - Consider using consistent tag naming conventions

## 📊 Performance Considerations

### Batch Processing

- Documents are processed in configurable batches
- Automatic retry logic with exponential backoff
- Efficient chunk management and deduplication

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
    RetryableError
)

try:
    response = await vector_service.add_source(request)
except RetryableError:
    # Handle retryable errors
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
from app.services.embeddings.embeddings import load_embeddings_model
embedding_model = load_embeddings_model(
    provider=ModelProvider.OPENAI,
    model_id="text-embedding-3-small"
)
```

## 📈 Monitoring

Key metrics to monitor:

- Document ingestion rate and processing times
- Search latency and result quality
- Embedding model usage and costs
- Storage utilization and chunk distribution
- Error rates and failed operations
