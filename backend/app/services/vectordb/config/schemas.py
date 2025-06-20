"""
Weaviate schema definitions for Vector Database Service
"""

from weaviate.classes.config import Configure, Property, DataType, ReferenceProperty
from typing import List, Dict
from .settings import get_model_config
from weaviate.classes.query import Filter


def get_sources_schema() -> Dict:
    """Get schema definition for sources collection"""
    return {
        "properties": [
            Property(name="source_path", data_type=DataType.TEXT),
            Property(name="content_hash", data_type=DataType.TEXT),
            Property(name="source_type", data_type=DataType.TEXT),
            Property(name="created_by_user_id", data_type=DataType.TEXT),
            Property(name="created_at", data_type=DataType.DATE),
            Property(name="updated_at", data_type=DataType.DATE),
            Property(name="access_users", data_type=DataType.TEXT_ARRAY),
            Property(name="file_size", data_type=DataType.INT),
            Property(name="mime_type", data_type=DataType.TEXT),
            # Source metadata
            Property(name="title", data_type=DataType.TEXT),
            Property(name="author", data_type=DataType.TEXT),
            Property(name="description", data_type=DataType.TEXT),
            Property(name="tags", data_type=DataType.TEXT_ARRAY),
            Property(name="custom_metadata", data_type=DataType.OBJECT),
        ],
        "inverted_index_config": Configure.inverted_index(
            bm25_b=0.75,
            bm25_k1=1.2,
            cleanup_interval_seconds=60,
            index_timestamps=True,
            index_property_length=True,
            index_null_state=True,
        ),
    }


def get_chunks_schema(embedding_models: List[str]) -> Dict:
    """Get schema definition for chunks collection with named vectors"""

    # Build vectorizer configs for each embedding model
    vectorizer_configs = []

    for model_name in embedding_models:
        model_config = get_model_config(model_name)

        if model_config["provider"] == "openai":
            # Use Weaviate's built-in OpenAI vectorizer
            vectorizer_configs.append(
                Configure.NamedVectors.text2vec_openai(
                    name=f"vector_{model_name.replace('-', '_')}",
                    source_properties=["content"],
                    model=model_name,
                    dimensions=model_config["dimensions"],
                )
            )
        else:
            # For custom models, use none vectorizer (manual vectors)
            vectorizer_configs.append(
                Configure.NamedVectors.none(
                    name=f"vector_{model_name.replace('-', '_')}"
                )
            )

    return {
        "properties": [
            Property(name="content", data_type=DataType.TEXT),
            Property(name="source_id", data_type=DataType.TEXT),
            Property(name="chunk_index", data_type=DataType.INT),
            Property(name="chunk_size", data_type=DataType.INT),
            Property(name="created_by_user_id", data_type=DataType.TEXT),
            Property(name="created_at", data_type=DataType.DATE),
            Property(name="access_users", data_type=DataType.TEXT_ARRAY),
            Property(name="content_hash", data_type=DataType.TEXT),
            Property(name="embedding_models", data_type=DataType.TEXT_ARRAY),
            Property(name="tags", data_type=DataType.TEXT_ARRAY),
            Property(name="custom_metadata", data_type=DataType.OBJECT),
            # Auto-generated metadata
            Property(name="section", data_type=DataType.TEXT),
            Property(name="page_number", data_type=DataType.INT),
            Property(name="line_number", data_type=DataType.INT),
        ],
        "references": [
            ReferenceProperty(name="belongsToSource", target_collection="sources")
        ],
        "vectorizer_config": vectorizer_configs,
        "inverted_index_config": Configure.inverted_index(
            bm25_b=0.75,
            bm25_k1=1.2,
            cleanup_interval_seconds=60,
            index_timestamps=True,
            index_property_length=True,
            index_null_state=True,
        ),
    }


def get_collection_names(org_id: str) -> Dict[str, str]:
    """Get collection names for an organization"""
    return {"sources": f"org_{org_id}_sources", "chunks": f"org_{org_id}_chunks"}


def get_vector_name(embedding_model: str) -> str:
    """Get the vector name for a specific embedding model"""
    return f"vector_{embedding_model.replace('-', '_')}"


def create_collections_for_org(client, org_id: str, embedding_models: List[str]):
    """Create collections for a new organization"""
    collection_names = get_collection_names(org_id)

    # Create sources collection
    sources_schema = get_sources_schema()
    client.collections.create(
        name=collection_names["sources"],
        properties=sources_schema["properties"],
        inverted_index_config=sources_schema["inverted_index_config"],
    )

    # Create chunks collection with named vectors
    chunks_schema = get_chunks_schema(embedding_models)
    client.collections.create(
        name=collection_names["chunks"],
        properties=chunks_schema["properties"],
        references=chunks_schema["references"],
        vectorizer_config=chunks_schema["vectorizer_config"],
        inverted_index_config=chunks_schema["inverted_index_config"],
    )


def add_embedding_model_to_collection(client, org_id: str, embedding_model: str):
    """Add a new embedding model to an existing chunks collection"""
    collection_names = get_collection_names(org_id)
    chunks_collection = client.collections.get(collection_names["chunks"])

    model_config = get_model_config(embedding_model)
    vector_name = get_vector_name(embedding_model)

    # Add new named vector configuration
    if model_config["provider"] == "openai":
        new_vectorizer = Configure.NamedVectors.text2vec_openai(
            name=vector_name,
            source_properties=["content"],
            model=embedding_model,
            dimensions=model_config["dimensions"],
        )
    else:
        new_vectorizer = Configure.NamedVectors.none(name=vector_name)

    # Update collection configuration
    config = chunks_collection.config.get()
    current_vectors = (
        config.vectorizer_config if hasattr(config, "vectorizer_config") else []
    )

    # Add new vectorizer to existing configuration
    updated_vectors = list(current_vectors) + [new_vectorizer]

    # Update collection with new vectorizer configuration
    chunks_collection.config.update(vectorizer_config=updated_vectors)

    # Update existing chunks to include new embedding model
    chunks_collection.data.update_many(
        where=Filter.by_property("embedding_models").not_contains(embedding_model),
        properties={
            "embedding_models": [embedding_model]  # This will append to existing models
        },
    )


def validate_collections_exist(client, org_id: str) -> Dict[str, bool]:
    """Check if collections exist for an organization"""
    collection_names = get_collection_names(org_id)

    return {
        "sources": client.collections.exists(collection_names["sources"]),
        "chunks": client.collections.exists(collection_names["chunks"]),
    }


def get_collection_info(client, org_id: str) -> Dict:
    """Get information about organization's collections"""
    collection_names = get_collection_names(org_id)
    info = {"org_id": org_id, "collections": {}}

    for collection_type, collection_name in collection_names.items():
        if client.collections.exists(collection_name):
            collection = client.collections.get(collection_name)
            config = collection.config.get()

            info["collections"][collection_type] = {
                "name": collection_name,
                "exists": True,
                "properties": [prop.name for prop in config.properties],
            }
        else:
            info["collections"][collection_type] = {
                "name": collection_name,
                "exists": False,
            }

    return info
