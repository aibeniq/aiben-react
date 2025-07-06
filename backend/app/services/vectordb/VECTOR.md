# vectordb service

the vectordb service provides an interface for managing document embeddings and performing searches using milvus as the underlying vector database.

# initialization

the vectordb service is initialized automatically on fastapi startup and made available through dependency injection. just import it from `app.api.deps import VectorDBDep` and use it as a dependency in your routes.

```python
@router.post("/<your-route>", response_model=<response_model>)
async def example(vectordb_service: VectorDBDep)
```

# available methods

#### `add_source(file, knowledge_base_id, user_id, source_id, embedding_model_id)`

adds a source to the vector database

**parameters**

- `file: UploadFile` - The uploaded file to process
- `knowledge_base_id: str` - ID of the knowledge base
- `user_id: str` - ID of the user uploading the file
- `source_id: str` - Unique identifier for the source document
- `embedding_model_id: str` - ID of the embedding model to use

**supported file types**

- PDF files (.pdf)
- Word documents (.docx)
- Text files (.txt)

**logic**

1. loads and extracts text from the uploaded file
2. splits the document into chunks
3. generates embeddings for each chunk
4. stores chunks with metadata in the vector database

---

#### `delete_source(source_id, embedding_model_id)`

deletes all chunks associated with a specific source document.

**parameters**

- `source_id: str` - ID of the source to delete
- `embedding_model_id: str` - ID of the embedding model collection

---

#### `delete_knowledge_base(knowledge_base_id, embedding_model_id)`

deletes all chunks associated with a specific knowledge base.

**parameters**

- `knowledge_base_id: str` - ID of the knowledge base to delete
- `embedding_model_id: str` - ID of the embedding model collection

---

#### `search_semantic(query, embedding_model_id, ...)`

performs semantic similarity search using dense vector embeddings.

**parameters**

- `query: str` - Search query text
- `embedding_model_id: str` - ID of the embedding model to use
- `knowledge_base_id: Optional[str]` - Filter by knowledge base ID
- `user_id: Optional[str]` - Filter by user ID
- `source_id: Optional[str]` - Filter by source ID
- `limit: int` - Maximum number of results (default: 10)
- `output_fields: Optional[List[str]]` - Fields to return in results

**constraints**

at least one of `knowledge_base_id`, `user_id`, or `source_id` must be provided

**returns**

```python
{
    "success": bool,
    "results": List[Dict] or "error": str
}
```

**usage**

```python
results = vector_service.search_semantic(
    query="machine learning algorithms",
    embedding_model_id="openai_text_embedding_3_small",
    knowledge_base_id="kb_123",
    limit=5
)
```

---

#### `search_keyword(query, embedding_model_id, ...)`

performs keyword search using BM25 sparse vector search.

**parameters**

same as `search_semantic`

**usage**

```python
results = vector_service.search_keyword(
    query="neural networks deep learning",
    embedding_model_id="openai_text_embedding_3_small",
    knowledge_base_id="kb_123",
    limit=10
)
```

---

#### `search_hybrid(query, embedding_model_id, alpha=0.5, rerank_k=20, ...)`

performs hybrid search combining semantic and keyword search with weighted ranking.

**parameters**

all parameters from `search_semantic` plus:

- `alpha: float` - Weight for semantic search results (0.0-1.0, default: 0.5)
- `rerank_k: int` - Number of candidates to retrieve before reranking (default: 20)

**usage**

```python
results = vector_service.search_hybrid(
    query="artificial intelligence applications",
    embedding_model_id="openai_text_embedding_3_small",
    knowledge_base_id="kb_123",
    alpha=0.7,  # favors semantic search
    rerank_k=30,
    limit=10
)
```

# schema

#### `ChunkData`

base schema for chunk data after extraction from the source document.

```python
class ChunkData(BaseModel):
    knowledge_base_id: str          # knowledge base ID
    source_id: str                  # source document ID
    user_id: str                    # user ID who uploaded the document
    content: str                    # text content of the chunk
    tags: List[str] = []            # associated tags
    title: str = ""                 # document title
    summary: str = ""               # document summary
    author: str = ""                # document author
    url: str = ""                   # document URL
    created_at: int                 # creation timestamp
    updated_at: int                 # last update timestamp
```

#### `EmbeddedChunkData`

extends `ChunkData` with dense embedding vector for storage.

```python
class EmbeddedChunkData(ChunkData):
    dense: List[float]              # dense embedding vector
    # a sparse field is added automatically by milvus for keyword search
```

---

#### milvus schema

the vector database uses the following schema template:

```python
MILVUS_SCHEMA_TEMPLATE = [
    # primary key (auto-generated)
    FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    ),

    # bm25 sparse vector for keyword search (auto-generated)
    FieldSchema(
        name="sparse",
        dtype=DataType.SPARSE_FLOAT_VECTOR,
        description="sparse vector for BM25 search",
        nullable=False,
    ),

    # content and metadata fields
    FieldSchema(
        name="content",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="content of the chunk",
        nullable=False,
        enable_analyzer=True,
    ),

    FieldSchema(
        name="knowledge_base_id",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="knowledge base id",
        nullable=False,
    ),

    FieldSchema(
        name="source_id",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="source id",
        nullable=False,
    ),

    FieldSchema(
        name="user_id",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="user id",
        nullable=False,
    ),

    FieldSchema(
        name="tags",
        dtype=DataType.ARRAY,
        element_type=DataType.VARCHAR,
        max_length=65535,
        max_capacity=10,
        description="tags",
    ),

    FieldSchema(
        name="title",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="title of the document",
        default_value="",
    ),

    FieldSchema(
        name="summary",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="summary of the document",
        default_value="",
    ),

    FieldSchema(
        name="author",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="author of the document",
        default_value="",
    ),

    FieldSchema(
        name="url",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="url of the document",
        default_value="",
    ),

    FieldSchema(
        name="created_at",
        dtype=DataType.INT64,
        description="created at",
        nullable=False,
    ),

    FieldSchema(
        name="updated_at",
        dtype=DataType.INT64,
        description="updated at",
        nullable=False,
    ),

    # dense embedding vector (dimensions vary by model)
    FieldSchema(
        name="dense",
        dtype=DataType.FLOAT_VECTOR,
        description="dense embedding vector",
        dim=<model_specific_dimensions>,
        nullable=False,
    )
]
```

---

#### configuration

##### connection settings

```python
MILVUS_URL = os.getenv("MILVUS_URL", "http://milvus:19530")
```

##### bm25 function

```python
BM25_FUNCTION = Function(
    name="text_bm25_emb",
    input_field_names=["content"],
    output_field_names=["sparse"],
    function_type=FunctionType.BM25,
)
```

---

#### indexes

the service automatically creates the following indexes:

- **primary key index**: `STL_SORT` on `id` field
- **dense vector index**: `HNSW` with COSINE metric on `dense` field
- **sparse vector index**: `SPARSE_INVERTED_INDEX` with BM25 metric on `sparse` field
- **filter indexes**: standard indexes on `knowledge_base_id`, `user_id`, and `source_id`

##### HNSW Parameters

- `M`: 16 (number of connections)
- `efConstruction`: 500 (construction parameter)

##### sparse index parameters

- `inverted_index_algo`: "DAAT_MAXSCORE"

---

#### collection naming

collections are automatically named based on the embedding model:

- format: `{provider}_{model_name}_{dimensions}`
- example: `openai_textembedding3small_1536`
- special characters are removed for safety

---

#### default output fields

when no specific output fields are requested, the service returns:

```python
default_output_fields = [
    "content",
    "tags",
    "title",
    "url",
    "knowledge_base_id",
    "user_id",
    "source_id"
]
```

---

#### error handling

> TODO: add descriptive errors

currently, the service returns booleans with error messages, but can also raise exceptions.
