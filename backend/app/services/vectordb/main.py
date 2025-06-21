## Milvus client

from pymilvus import MilvusClient

client = MilvusClient("http://localhost:19530")  # TODO: add auth

if client.has_collection(collection_name="test_collection"):
    client.drop_collection(collection_name="test_collection")

## Schema
from pymilvus import CollectionSchema, FieldSchema, DataType

fields = [
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
        dim=1536,  # dimension for text-embedding-3-small
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

schema = CollectionSchema(fields=fields, description="schema for test_collection")

## Collection
client.create_collection(
    collection_name="test_collection",
    schema=schema,
    # consistency_level="Strong",
)

## Embedding
import os
from openai import OpenAI

embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return (
        embedding_client.embeddings.create(input=[text], model=model).data[0].embedding
    )


## Documents
docs = [
    (
        "KB1",
        "Artificial intelligence was founded as an academic discipline in 1956.",
        ["AI", "academic", "discipline"],
        1718851200,
        1718851200,
    ),
    (
        "KB2",
        "Alan Turing was the first person to conduct substantial research in AI.",
        ["AI", "research", "Turing"],
        1718851200,
        1718851200,
    ),
    (
        "KB1",
        "Born in Maida Vale, London, Turing was raised in southern England.",
        ["London", "Turing", "England"],
        1718851200,
        1718851200,
    ),
]

res = client.insert(
    collection_name="test_collection",
    data=[
        {
            "knowledge_base_id": knowledge_base_id,
            "vector": get_embedding(doc),
            "content": doc,
            "tags": tags,
            "created_at": created_at,
            "updated_at": updated_at,
        }
        for knowledge_base_id, doc, tags, created_at, updated_at in docs
    ],
)
print(res)


# Create index parameters
index_params = client.prepare_index_params()

# Add indexes
index_params.add_index(field_name="id", index_type="STL_SORT")

index_params.add_index(
    field_name="vector",
    index_type="HNSW",
    metric_type="COSINE",
    params={"M": 16, "efConstruction": 500},
)

# Create indexes
client.create_index(
    collection_name="test_collection", index_params=index_params, sync=False
)

## Load collection before searching
client.load_collection(collection_name="test_collection")

## Search

res = client.search(
    collection_name="test_collection",
    data=[get_embedding("Alan Turing")],
    filter="knowledge_base_id == 'KB1'",
    limit=2,
    output_fields=["content", "tags"],
)
print(res)
