"""
Cross-Encoder Reranker for improved RAG retrieval relevance.

This module provides advanced reranking using cross-encoder models that score
query-document pairs directly for better relevance than simple vector similarity.
"""

from typing import List, Tuple, Optional
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """
    Advanced reranking using cross-encoder models for better relevance scoring.
    
    Cross-encoders jointly encode the query and document, providing more accurate
    relevance scores compared to bi-encoder approaches used in initial retrieval.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model for reranking. Options:
                - cross-encoder/ms-marco-MiniLM-L-6-v2: Fast, good for general use (default)
                - cross-encoder/ms-marco-MiniLM-L-12-v2: Better accuracy, slower
                - BAAI/bge-reranker-base: Good multilingual support
                - BAAI/bge-reranker-large: Best accuracy, slowest
        """
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
            self.model_name = model_name
            logger.info(f"✓ Initialized CrossEncoderReranker with {model_name}")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize CrossEncoderReranker: {e}")
            raise
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on relevance to query.
        
        Args:
            query: Search query
            documents: Retrieved documents to rerank
            top_k: Return top K documents (None = all)
            
        Returns:
            List of (document, score) tuples sorted by relevance (highest first)
        """
        if not documents:
            return []
        
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = [[query, doc.page_content] for doc in documents]
            
            # Get relevance scores from cross-encoder
            scores = self.model.predict(pairs)
            
            # Combine documents with scores
            doc_scores = list(zip(documents, scores))
            
            # Sort by score (descending - highest relevance first)
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Limit to top_k if specified
            if top_k:
                doc_scores = doc_scores[:top_k]
            
            logger.info(
                f"Reranked {len(documents)} documents, "
                f"score range: {min(scores):.3f} to {max(scores):.3f}"
            )
            
            return doc_scores
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback: return original order with neutral scores
            return [(doc, 0.5) for doc in documents]
    
    def rerank_with_quality_fusion(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
        quality_weight: float = 0.3
    ) -> List[Document]:
        """
        Combine cross-encoder reranking with existing quality scores.
        
        This method fuses the cross-encoder relevance score with your existing
        quality_score metadata to get the best of both approaches.
        
        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of top results to return
            quality_weight: Weight for quality score (0-1), default 0.3
                - 0.0 = only use cross-encoder scores
                - 1.0 = only use quality scores
                - 0.3 = 70% cross-encoder, 30% quality (recommended)
            
        Returns:
            Reranked documents (sorted by fused score)
        """
        if not documents:
            return []
        
        # Get cross-encoder scores
        doc_scores = self.rerank(query, documents)
        
        # Normalize cross-encoder scores to 0-1 range
        scores = [s for _, s in doc_scores]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score if max_score > min_score else 1.0
        
        # Fuse with quality scores
        fused_scores = []
        for doc, ce_score in doc_scores:
            # Normalize cross-encoder score
            normalized_ce = (ce_score - min_score) / score_range
            
            # Get quality score from metadata (default 0.5 if not present)
            quality_score = doc.metadata.get("quality_score", 0.5)
            
            # Weighted combination
            fused_score = (
                (1 - quality_weight) * normalized_ce +
                quality_weight * quality_score
            )
            
            fused_scores.append((doc, fused_score))
        
        # Sort by fused score
        fused_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Extract documents
        result = [doc for doc, _ in fused_scores]
        
        # Limit to top_k if specified
        if top_k:
            result = result[:top_k]
        
        logger.debug(
            f"Fused cross-encoder + quality scores for {len(documents)} documents, "
            f"returning top {len(result)}"
        )
        
        return result
    
    def rerank_with_metadata_boost(
        self,
        query: str,
        documents: List[Document],
        top_k: Optional[int] = None,
        content_type_boost: float = 0.1,
        recency_boost: float = 0.05
    ) -> List[Document]:
        """
        Rerank with additional boosts for content type and recency.
        
        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of top results to return
            content_type_boost: Boost for main_content vs bibliography (default 0.1)
            recency_boost: Boost for more recent documents (default 0.05)
            
        Returns:
            Reranked documents with metadata boosts applied
        """
        if not documents:
            return []
        
        # Get cross-encoder scores
        doc_scores = self.rerank(query, documents)
        
        # Normalize scores
        scores = [s for _, s in doc_scores]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score if max_score > min_score else 1.0
        
        # Apply metadata boosts
        boosted_scores = []
        for doc, ce_score in doc_scores:
            normalized_ce = (ce_score - min_score) / score_range
            
            # Content type boost
            content_boost = (
                content_type_boost
                if doc.metadata.get("content_type") == "main_content"
                else 0.0
            )
            
            # Quality score boost
            quality_score = doc.metadata.get("quality_score", 0.5)
            
            # Combined score
            final_score = (
                0.7 * normalized_ce +      # Cross-encoder relevance (70%)
                0.2 * quality_score +      # Content quality (20%)
                0.1 * content_boost        # Content type bonus (10%)
            )
            
            boosted_scores.append((doc, final_score))
        
        # Sort by final score
        boosted_scores.sort(key=lambda x: x[1], reverse=True)
        
        result = [doc for doc, _ in boosted_scores]
        if top_k:
            result = result[:top_k]
        
        return result


# Convenience function for quick reranking
def rerank_documents(
    query: str,
    documents: List[Document],
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    top_k: Optional[int] = None
) -> List[Document]:
    """
    Quick reranking function without needing to instantiate the class.
    
    Args:
        query: Search query
        documents: Documents to rerank
        model_name: Cross-encoder model to use
        top_k: Number of top results to return
        
    Returns:
        Reranked documents
    """
    reranker = CrossEncoderReranker(model_name=model_name)
    doc_scores = reranker.rerank(query, documents, top_k=top_k)
    return [doc for doc, _ in doc_scores]
