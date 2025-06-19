"""
Module for retriever implementations, including hybrid retrieval strategies.

This module provides various retriever implementations for knowledge base search,
including BM25 for keyword search and ensemble retrieval that combines multiple retrievers.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Sequence

from langchain_community.vectorstores import Chroma
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.schema import Document
import numpy as np

logger = logging.getLogger(__name__)


class BM25KeywordRetriever:
    """
    A wrapper class for BM25 retriever that helps with document preparation.
    """

    @classmethod
    def from_chroma(cls, chroma_db: Chroma, **kwargs):
        """
        Create a BM25Retriever from a Chroma database.

        Args:
            chroma_db: The Chroma database
            **kwargs: Additional keyword arguments for BM25Retriever

        Returns:
            A BM25Retriever instance
        """
        # Extract documents from Chroma
        docs = cls._extract_docs_from_chroma(chroma_db)

        # Create a BM25Retriever from the documents
        return BM25Retriever.from_documents(docs, **kwargs)

    @staticmethod
    def _extract_docs_from_chroma(chroma_db: Chroma) -> List[Document]:
        """
        Extract documents from a Chroma database.

        Args:
            chroma_db: The Chroma database

        Returns:
            A list of langchain Documents
        """
        # Get all ids from the collection
        collection = chroma_db._collection
        all_data = collection.get(include=["documents", "metadatas"])

        documents = []
        if all_data["documents"]:
            for i, doc_text in enumerate(all_data["documents"]):
                # Create a Document with page_content and metadata
                metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}
                documents.append(Document(page_content=doc_text, metadata=metadata))

        logger.info(
            f"Extracted {len(documents)} documents from Chroma for BM25 indexing"
        )
        return documents


def create_ensemble_retriever(
    chroma_db: Chroma,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
    search_kwargs: Dict[str, Any] = None,
) -> EnsembleRetriever:
    """
    Create an ensemble retriever that combines vector-based and keyword-based retrieval.

    Args:
        chroma_db: The Chroma database for vector retrieval
        vector_weight: Weight for vector-based retrieval (default: 0.7)
        keyword_weight: Weight for keyword-based retrieval (default: 0.3)
        search_kwargs: Additional search parameters for the vector retriever

    Returns:
        An EnsembleRetriever that combines both approaches
    """
    if search_kwargs is None:
        search_kwargs = {"k": 5}

    # Create the vector-based retriever from ChromaDB
    vector_retriever = chroma_db.as_retriever(search_kwargs=search_kwargs)

    # Create the keyword-based BM25 retriever
    keyword_retriever = BM25KeywordRetriever.from_chroma(
        chroma_db, k=search_kwargs.get("k", 5)
    )

    # Combine them in an ensemble with specified weights
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, keyword_retriever],
        weights=[vector_weight, keyword_weight],
    )

    logger.info(
        "Created ensemble retriever with vector weight %.2f and keyword weight %.2f",
        vector_weight,
        keyword_weight,
    )

    return ensemble_retriever
