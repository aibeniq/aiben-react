"""
Enhanced retriever with content filtering and quality-based re-ranking.
Improves RAG retrieval by prioritizing main content over bibliography and low-quality text.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain.schema import BaseRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma
from pydantic import Field
from app.services.content_filtering import content_filter
from app.services.retrievers import create_ensemble_retriever

logger = logging.getLogger(__name__)


class EnhancedRetriever(BaseRetriever):
    """
    Enhanced retriever that filters out bibliography content and re-ranks results by quality.
    Now supports optional cross-encoder reranking for improved relevance scoring.
    """

    base_retriever: BaseRetriever = Field(description="The underlying retriever")
    filter_bibliography: bool = Field(
        default=True, description="Whether to filter out bibliography content"
    )
    min_quality_score: float = Field(
        default=0.3, description="Minimum quality score for results"
    )
    max_bibliography_results: int = Field(
        default=1, description="Maximum number of bibliography results"
    )
    rerank_by_quality: bool = Field(
        default=True, description="Whether to re-rank results by quality"
    )
    use_cross_encoder: bool = Field(
        default=False, description="Whether to use cross-encoder reranking"
    )
    cross_encoder_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model name"
    )
    reranker_top_k: Optional[int] = Field(
        default=None, description="Top K results after reranking"
    )
    reranker_quality_weight: float = Field(
        default=0.3, description="Weight for quality score in fusion"
    )

    def __init__(
        self,
        base_retriever: BaseRetriever,
        filter_bibliography: bool = True,
        min_quality_score: float = 0.3,
        max_bibliography_results: int = 1,
        rerank_by_quality: bool = True,
        use_cross_encoder: bool = False,
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        reranker_top_k: Optional[int] = None,
        reranker_quality_weight: float = 0.3,
        **kwargs,
    ):
        """
        Initialize the enhanced retriever.

        Args:
            base_retriever: The underlying retriever (ensemble, vector, etc.)
            filter_bibliography: Whether to filter out bibliography content
            min_quality_score: Minimum quality score for results
            max_bibliography_results: Maximum number of bibliography results to include
            rerank_by_quality: Whether to re-rank results by content quality (heuristic)
            use_cross_encoder: Whether to use cross-encoder reranking (more accurate)
            cross_encoder_model: Cross-encoder model to use
            reranker_top_k: Top K results to return after reranking
            reranker_quality_weight: Weight for quality score in fusion (0-1)
        """
        super().__init__(
            base_retriever=base_retriever,
            filter_bibliography=filter_bibliography,
            min_quality_score=min_quality_score,
            max_bibliography_results=max_bibliography_results,
            rerank_by_quality=rerank_by_quality,
            use_cross_encoder=use_cross_encoder,
            cross_encoder_model=cross_encoder_model,
            reranker_top_k=reranker_top_k,
            reranker_quality_weight=reranker_quality_weight,
            **kwargs,
        )
        
        # Initialize cross-encoder reranker if enabled
        self._reranker = None
        if use_cross_encoder:
            try:
                from app.services.reranker import CrossEncoderReranker
                self._reranker = CrossEncoderReranker(model_name=cross_encoder_model)
                logger.info(f"✓ Cross-encoder reranking enabled with {cross_encoder_model}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize cross-encoder reranker: {e}. "
                    f"Falling back to quality-based reranking."
                )
                self.use_cross_encoder = False

    def _get_relevant_documents(
        self, query: str, *, run_manager=None
    ) -> List[Document]:
        """
        Get relevant documents with enhanced filtering and re-ranking.

        Args:
            query: Search query
            run_manager: Optional run manager

        Returns:
            List of filtered and ranked documents
        """
        # Get initial results from base retriever
        initial_results = self.base_retriever.get_relevant_documents(
            query, run_manager=run_manager
        )

        if not initial_results:
            return []

        logger.debug(f"Initial retrieval returned {len(initial_results)} documents")

        # Enhance metadata if not already present
        enhanced_results = []
        for doc in initial_results:
            if "quality_score" not in doc.metadata:
                enhanced_doc = content_filter.enhance_document_metadata([doc])[0]
                enhanced_results.append(enhanced_doc)
            else:
                enhanced_results.append(doc)

        # Apply filtering
        filtered_results = self._apply_content_filtering(enhanced_results, query)

        # Apply reranking based on configuration
        if self.use_cross_encoder and self._reranker and filtered_results:
            # Use cross-encoder reranking (more accurate)
            logger.debug("Applying cross-encoder reranking...")
            filtered_results = self._reranker.rerank_with_quality_fusion(
                query=query,
                documents=filtered_results,
                top_k=self.reranker_top_k,
                quality_weight=self.reranker_quality_weight
            )
        elif self.rerank_by_quality and filtered_results:
            # Fallback to heuristic quality-based reranking
            logger.debug("Applying heuristic quality-based reranking...")
            filtered_results = self._rerank_by_quality(filtered_results, query)

        logger.info(
            f"Enhanced retrieval: {len(initial_results)} -> {len(filtered_results)} documents after filtering"
        )

        return filtered_results

    def _apply_content_filtering(
        self, documents: List[Document], query: str
    ) -> List[Document]:
        """
        Apply content filtering to remove low-quality and bibliography content.

        Args:
            documents: Documents to filter
            query: Original search query

        Returns:
            Filtered documents
        """
        main_content_docs = []
        bibliography_docs = []
        filtered_out_docs = []

        for doc in documents:
            content_type = doc.metadata.get("content_type", "unknown")
            quality_score = doc.metadata.get("quality_score", 0.5)

            # Skip documents that don't meet quality threshold
            if quality_score < self.min_quality_score:
                filtered_out_docs.append(
                    {
                        "reason": f"Low quality (score: {quality_score:.2f})",
                        "content": (
                            doc.page_content[:200] + "..."
                            if len(doc.page_content) > 200
                            else doc.page_content
                        ),
                        "source": doc.metadata.get("source", "unknown"),
                    }
                )
                logger.debug(
                    f"Filtering low-quality document (score: {quality_score:.2f})"
                )
                continue

            # Categorize documents
            if content_type == "bibliography" or doc.metadata.get(
                "is_bibliography", False
            ):
                if (
                    len(bibliography_docs) < self.max_bibliography_results
                    and not self.filter_bibliography
                ):
                    bibliography_docs.append(doc)
                else:
                    filtered_out_docs.append(
                        {
                            "reason": "Bibliography content filtered",
                            "content": (
                                doc.page_content[:200] + "..."
                                if len(doc.page_content) > 200
                                else doc.page_content
                            ),
                            "source": doc.metadata.get("source", "unknown"),
                        }
                    )
            else:
                main_content_docs.append(doc)

        # Track bibliography docs that weren't included in final result
        excluded_bibliography = []

        # Prioritize main content, but include some bibliography if no main content found
        if main_content_docs:
            result = main_content_docs
            # Add limited bibliography only if specifically requested or very few main results
            if (
                len(main_content_docs) < 3
                and bibliography_docs
                and not self.filter_bibliography
            ):
                included_bib = bibliography_docs[: self.max_bibliography_results]
                excluded_bib = bibliography_docs[self.max_bibliography_results :]
                result.extend(included_bib)

                # Add excluded bibliography to filtered out list
                for doc in excluded_bib:
                    filtered_out_docs.append(
                        {
                            "reason": "Bibliography limit exceeded",
                            "content": (
                                doc.page_content[:200] + "..."
                                if len(doc.page_content) > 200
                                else doc.page_content
                            ),
                            "source": doc.metadata.get("source", "unknown"),
                        }
                    )
            else:
                # All bibliography docs were excluded
                for doc in bibliography_docs:
                    filtered_out_docs.append(
                        {
                            "reason": "Bibliography not needed (sufficient main content)",
                            "content": (
                                doc.page_content[:200] + "..."
                                if len(doc.page_content) > 200
                                else doc.page_content
                            ),
                            "source": doc.metadata.get("source", "unknown"),
                        }
                    )
        elif bibliography_docs:
            # Fallback to bibliography if no main content found
            included_bib = bibliography_docs[: self.max_bibliography_results * 2]
            excluded_bib = bibliography_docs[self.max_bibliography_results * 2 :]
            result = included_bib

            # Add excluded bibliography to filtered out list
            for doc in excluded_bib:
                filtered_out_docs.append(
                    {
                        "reason": "Bibliography fallback limit exceeded",
                        "content": (
                            doc.page_content[:200] + "..."
                            if len(doc.page_content) > 200
                            else doc.page_content
                        ),
                        "source": doc.metadata.get("source", "unknown"),
                    }
                )

            logger.warning(
                "No main content found, using bibliography results as fallback"
            )
        else:
            result = []

        # Log filtered out documents if any
        if filtered_out_docs:
            logger.info(f"Filtered out {len(filtered_out_docs)} documents:")
            for i, doc_info in enumerate(filtered_out_docs, 1):
                logger.info(
                    f"  {i}. [{doc_info['reason']}] From '{doc_info['source']}': {doc_info['content']}"
                )

        return result

    def _rerank_by_quality(
        self, documents: List[Document], query: str
    ) -> List[Document]:
        """
        Re-rank documents by combining original relevance with quality score.

        Args:
            documents: Documents to re-rank
            query: Original search query

        Returns:
            Re-ranked documents
        """
        # Calculate combined scores
        scored_docs = []
        for i, doc in enumerate(documents):
            # Original relevance score (higher position = lower relevance)
            relevance_score = 1.0 - (i / len(documents))

            # Quality score
            quality_score = doc.metadata.get("quality_score", 0.5)

            # Bonus for main content vs bibliography
            content_type_bonus = (
                0.2 if doc.metadata.get("content_type") == "main_content" else 0.0
            )

            # Combined score (weighted combination)
            combined_score = (
                0.6 * relevance_score  # Original relevance
                + 0.3 * quality_score  # Content quality
                + 0.1 * content_type_bonus  # Content type preference
            )

            scored_docs.append((doc, combined_score))

        # Sort by combined score (highest first)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return re-ranked documents
        reranked_docs = [doc for doc, score in scored_docs]

        logger.debug(f"Re-ranked {len(documents)} documents by quality")

        return reranked_docs


def create_enhanced_retriever(
    chroma_db: Chroma,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
    search_kwargs: Dict[str, Any] = None,
    filter_bibliography: bool = True,
    min_quality_score: float = 0.3,
    max_bibliography_results: int = 1,
    use_cross_encoder: bool = False,
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    reranker_top_k: Optional[int] = None,
    reranker_quality_weight: float = 0.3,
) -> EnhancedRetriever:
    """
    Create an enhanced retriever with content filtering and quality re-ranking.

    Args:
        chroma_db: ChromaDB instance
        vector_weight: Weight for vector search
        keyword_weight: Weight for keyword search
        search_kwargs: Additional search parameters
        filter_bibliography: Whether to filter bibliography content
        min_quality_score: Minimum quality score for results
        max_bibliography_results: Maximum bibliography results to include
        use_cross_encoder: Whether to use cross-encoder reranking
        cross_encoder_model: Cross-encoder model to use
        reranker_top_k: Top K results after reranking
        reranker_quality_weight: Weight for quality score in fusion

    Returns:
        Enhanced retriever instance
    """
    try:
        # Create base ensemble retriever
        base_retriever = create_ensemble_retriever(
            chroma_db=chroma_db,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
            search_kwargs=search_kwargs,
        )
    except Exception as e:
        logger.error(f"Failed to create ensemble retriever: {e}")
        # Fallback to basic vector retriever
        logger.info("Falling back to basic vector retriever")
        base_retriever = chroma_db.as_retriever(search_kwargs=search_kwargs or {"k": 5})

    # Wrap with enhanced functionality
    enhanced_retriever = EnhancedRetriever(
        base_retriever=base_retriever,
        filter_bibliography=filter_bibliography,
        min_quality_score=min_quality_score,
        max_bibliography_results=max_bibliography_results,
        rerank_by_quality=True,
        use_cross_encoder=use_cross_encoder,
        cross_encoder_model=cross_encoder_model,
        reranker_top_k=reranker_top_k,
        reranker_quality_weight=reranker_quality_weight,
    )

    logger.info(
        f"Created enhanced retriever with bibliography filtering: {filter_bibliography}, "
        f"cross-encoder reranking: {use_cross_encoder}"
    )

    return enhanced_retriever


class SmartRetrieverFactory:
    """
    Factory for creating different types of smart retrievers based on use case.
    """

    @staticmethod
    def create_academic_paper_retriever(
        chroma_db: Chroma,
        search_kwargs: Dict[str, Any] = None,
        use_cross_encoder: bool = False,
    ) -> EnhancedRetriever:
        """
        Create a retriever optimized for academic papers.
        Heavily filters bibliography content and prioritizes main content.
        
        Args:
            chroma_db: ChromaDB instance
            search_kwargs: Search parameters
            use_cross_encoder: Whether to enable cross-encoder reranking
        """
        try:
            return create_enhanced_retriever(
                chroma_db=chroma_db,
                vector_weight=0.8,  # Higher weight on semantic similarity
                keyword_weight=0.2,
                search_kwargs=search_kwargs or {"k": 5},
                filter_bibliography=True,  # Aggressive bibliography filtering
                min_quality_score=0.4,  # Higher quality threshold
                max_bibliography_results=0,  # No bibliography results
                use_cross_encoder=use_cross_encoder,
            )
        except Exception as e:
            logger.error(f"Failed to create academic paper retriever: {e}")
            # Create a simple enhanced retriever with just vector search as fallback
            base_retriever = chroma_db.as_retriever(
                search_kwargs=search_kwargs or {"k": 5}
            )
            return EnhancedRetriever(
                base_retriever=base_retriever,
                filter_bibliography=True,
                min_quality_score=0.4,
                max_bibliography_results=0,
                use_cross_encoder=use_cross_encoder,
            )

    @staticmethod
    def create_general_document_retriever(
        chroma_db: Chroma,
        search_kwargs: Dict[str, Any] = None,
        use_cross_encoder: bool = False,
    ) -> EnhancedRetriever:
        """
        Create a retriever for general documents.
        Balanced approach with moderate filtering.
        
        Args:
            chroma_db: ChromaDB instance
            search_kwargs: Search parameters
            use_cross_encoder: Whether to enable cross-encoder reranking
        """
        try:
            return create_enhanced_retriever(
                chroma_db=chroma_db,
                vector_weight=0.7,
                keyword_weight=0.3,
                search_kwargs=search_kwargs or {"k": 5},
                filter_bibliography=True,
                min_quality_score=0.3,
                max_bibliography_results=1,
                use_cross_encoder=use_cross_encoder,
            )
        except Exception as e:
            logger.error(f"Failed to create general document retriever: {e}")
            # Create a simple enhanced retriever with just vector search as fallback
            base_retriever = chroma_db.as_retriever(
                search_kwargs=search_kwargs or {"k": 5}
            )
            return EnhancedRetriever(
                base_retriever=base_retriever,
                filter_bibliography=True,
                use_cross_encoder=use_cross_encoder,
                min_quality_score=0.3,
                max_bibliography_results=1,
            )

    @staticmethod
    def create_comprehensive_retriever(
        chroma_db: Chroma, search_kwargs: Dict[str, Any] = None
    ) -> EnhancedRetriever:
        """
        Create a retriever that includes all content types.
        Minimal filtering for comprehensive coverage.
        """
        try:
            return create_enhanced_retriever(
                chroma_db=chroma_db,
                vector_weight=0.6,
                keyword_weight=0.4,
                search_kwargs=search_kwargs or {"k": 5},
                filter_bibliography=False,  # Include bibliography
                min_quality_score=0.2,  # Lower quality threshold
                max_bibliography_results=3,
            )
        except Exception as e:
            logger.error(f"Failed to create comprehensive retriever: {e}")
            # Create a simple enhanced retriever with just vector search as fallback
            base_retriever = chroma_db.as_retriever(
                search_kwargs=search_kwargs or {"k": 5}
            )
            return EnhancedRetriever(
                base_retriever=base_retriever,
                filter_bibliography=False,
                min_quality_score=0.2,
                max_bibliography_results=3,
            )
