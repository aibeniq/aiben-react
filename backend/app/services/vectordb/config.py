from pymilvus import FieldSchema, DataType
import os
from app.services.embeddings import load_embeddings_model

# embedding model
EMBEDDING_PROVIDER = "openai"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
EMBEDDING_MODEL = load_embeddings_model(
    provider=EMBEDDING_PROVIDER,
    model_id=EMBEDDING_MODEL,
    api_key=os.getenv("OPENAI_API_KEY"),
)


# this is initialized for every vector db service
BASE_COLLECTION_NAME = "base"

# milvus URL
MILVUS_URL = os.getenv("MILVUS_URL", "http://localhost:19530")

# milvus schema
MILVUS_SCHEMA = [
    FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    ),
    FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        description="embedding vector",
        dim=EMBEDDING_DIM,
        nullable=False,
    ),
    FieldSchema(
        name="content",
        dtype=DataType.VARCHAR,
        max_length=65535,
        description="content of the chunk",
        nullable=False,
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
]
