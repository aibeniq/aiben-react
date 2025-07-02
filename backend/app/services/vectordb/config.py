from pymilvus import FieldSchema, DataType, Function, FunctionType
import os


# bm25 function for keyword search
BM25_FUNCTION = Function(
    name="text_bm25_emb",
    input_field_names=["content"],
    output_field_names=["sparse"],
    function_type=FunctionType.BM25,
)

# milvus URL
MILVUS_URL = os.getenv("MILVUS_URL", "http://localhost:19530")

# milvus schema without dense vector field (added separately for each embedding model & collection)
MILVUS_SCHEMA_TEMPLATE = [
    FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    ),
    FieldSchema(
        name="sparse",
        dtype=DataType.SPARSE_FLOAT_VECTOR,
        description="sparse vector for BM25 search",
        nullable=False,
    ),
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
]
