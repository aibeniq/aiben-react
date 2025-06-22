## TODOS
# TODO: use embedding service
# TODO: add types to chunks
# TODO: use environment variables
# TODO: modularize
# TODO: search methods
# TODO: better filtering
# TODO: initialize on fastapi startup
# TODO: add auth?

## Milvus client

from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional

# Initialize clients
client = MilvusClient("http://localhost:19530")
embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Collection name
COLLECTION_NAME = "knowledge_base_collection"

## Schema
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

schema = CollectionSchema(fields=fields, description="schema for base collection")


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    text = text.replace("\n", " ")
    return (
        embedding_client.embeddings.create(input=[text], model=model).data[0].embedding
    )


def init_collection() -> bool:
    """Initialize the collection if it doesn't exist and set up indexes."""
    try:
        # Check if collection exists
        if client.has_collection(collection_name=COLLECTION_NAME):
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            return True

        print(f"Creating collection '{COLLECTION_NAME}'...")

        # Create collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=schema,
        )

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
            collection_name=COLLECTION_NAME, index_params=index_params, sync=True
        )

        print(f"Collection '{COLLECTION_NAME}' created successfully with indexes.")
        return True

    except Exception as e:
        print(f"Error initializing collection: {e}")
        return False


def add_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add chunks to the collection.

    Args:
        chunks: List of dictionaries containing chunk data. Each chunk should have:
            - knowledge_base_id: str
            - content: str
            - tags: List[str] (optional, defaults to [])
            - title: str (optional, defaults to "")
            - summary: str (optional, defaults to "")
            - author: str (optional, defaults to "")
            - url: str (optional, defaults to "")
            - created_at: int (timestamp)
            - updated_at: int (timestamp)

    Returns:
        Dictionary with insertion results
    """
    try:
        # Ensure collection exists and is loaded
        if not client.has_collection(collection_name=COLLECTION_NAME):
            if not init_collection():
                return {"success": False, "error": "Failed to initialize collection"}

        # Load collection if not already loaded
        client.load_collection(collection_name=COLLECTION_NAME)

        # Prepare data for insertion
        data_to_insert = []
        for chunk in chunks:
            # Generate embedding for content
            embedding = get_embedding(chunk["content"])

            # Prepare chunk data with defaults
            chunk_data = {
                "knowledge_base_id": chunk["knowledge_base_id"],
                "vector": embedding,
                "content": chunk["content"],
                "tags": chunk.get("tags", []),
                "title": chunk.get("title", ""),
                "summary": chunk.get("summary", ""),
                "author": chunk.get("author", ""),
                "url": chunk.get("url", ""),
                "created_at": chunk["created_at"],
                "updated_at": chunk["updated_at"],
            }
            data_to_insert.append(chunk_data)

        # Insert data
        result = client.insert(
            collection_name=COLLECTION_NAME,
            data=data_to_insert,
        )

        return {
            "success": True,
            "inserted_count": len(data_to_insert),
            "result": result,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def search_chunks(
    query: str,
    knowledge_base_id: Optional[str] = None,
    limit: int = 10,
    output_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Search for similar chunks in the collection.

    Args:
        query: Search query text
        knowledge_base_id: Optional filter by knowledge base ID
        limit: Maximum number of results to return
        output_fields: List of fields to return in results

    Returns:
        Dictionary with search results
    """
    try:
        # Ensure collection is loaded
        client.load_collection(collection_name=COLLECTION_NAME)

        # Generate embedding for query
        query_embedding = get_embedding(query)

        # Prepare filter
        filter_expr = None
        if knowledge_base_id:
            filter_expr = f"knowledge_base_id == '{knowledge_base_id}'"

        # Set default output fields
        if output_fields is None:
            output_fields = ["content", "tags", "title", "knowledge_base_id"]

        # Perform search
        results = client.search(
            collection_name=COLLECTION_NAME,
            data=[query_embedding],
            filter=filter_expr,
            limit=limit,
            output_fields=output_fields,
        )

        return {"success": True, "results": results[0] if results else []}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Initialize collection on module import
if __name__ == "__main__":
    init_collection()
