# Advanced RAG Enhancement Implementation Guide

## Overview

This guide outlines how to enhance your existing RAG (Retrieval-Augmented Generation) system with advanced techniques recommended for production-grade GenAI applications:

1. **Hybrid Search** ✅ (Already Implemented)
2. **Reranker** 🔶 (Partially Implemented)
3. **Query Expansion** ⚠️ (Not Implemented)
4. **HyDE (Hypothetical Document Embeddings)** ⚠️ (Not Implemented)
5. **RAG Fusion** ⚠️ (Not Implemented)

---

## Current Implementation Status

### ✅ 1. Hybrid Search (IMPLEMENTED)

**Location:** `backend/app/services/retrievers.py`

Your system already implements hybrid search by combining:

- **Vector Search:** Semantic similarity using embeddings (ChromaDB)
- **Keyword Search:** BM25 algorithm for exact term matching

**Current Implementation:**

```python
def create_ensemble_retriever(
    chroma_db: Chroma,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
    search_kwargs: Dict[str, Any] = None,
) -> EnsembleRetriever:
```

**Weights:**

- Vector: 70% (semantic understanding)
- BM25 Keyword: 30% (exact term matching)

**Usage Across Codebase:**

- ✅ `chatbot.py` - Knowledge base queries
- ✅ `veradoc.py` - Document review
- ✅ `formconnect.py` - Field extraction (80% vector, 20% keyword)
- ✅ `reportgenie.py` - Report generation

**Recommendations:**

- ✓ Well-implemented
- Consider making weights configurable per use case
- Add user-level weight customization for power users

---

### 🔶 2. Reranker (PARTIALLY IMPLEMENTED)

**Location:** `backend/app/services/enhanced_retrieval.py`

You have a **quality-based reranking system** that:

- Filters bibliography content
- Assigns quality scores based on content type
- Re-ranks by combining relevance + quality + content type

**Current Reranking Logic:**

```python
def _rerank_by_quality(documents, query):
    combined_score = (
        0.6 * relevance_score      # Original retrieval position
        + 0.3 * quality_score       # Content quality
        + 0.1 * content_type_bonus  # Main content vs bibliography
    )
```

**What's Missing:**
This is a **lightweight heuristic reranker**. Production systems typically use:

#### Option A: Cross-Encoder Reranker (Recommended)

**Benefits:**

- More accurate relevance scoring
- Better handling of semantic nuances
- Industry-standard approach

**Implementation:**

```python
# backend/app/services/reranker.py
from sentence_transformers import CrossEncoder
from typing import List, Tuple
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Advanced reranking using cross-encoder models for better relevance scoring.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the cross-encoder reranker.

        Args:
            model_name: HuggingFace model for reranking
                - ms-marco-MiniLM-L-6-v2: Fast, good for general use
                - ms-marco-MiniLM-L-12-v2: Better accuracy, slower
                - bge-reranker-large: Best accuracy, slowest
        """
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
        logger.info(f"Initialized CrossEncoderReranker with {model_name}")

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents based on relevance to query.

        Args:
            query: Search query
            documents: Retrieved documents to rerank
            top_k: Return top K documents (None = all)

        Returns:
            List of (document, score) tuples sorted by relevance
        """
        if not documents:
            return []

        # Prepare pairs for cross-encoder
        pairs = [[query, doc.page_content] for doc in documents]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Combine documents with scores
        doc_scores = list(zip(documents, scores))

        # Sort by score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top_k if specified
        if top_k:
            doc_scores = doc_scores[:top_k]

        logger.info(
            f"Reranked {len(documents)} docs, "
            f"score range: {min(scores):.3f} to {max(scores):.3f}"
        )

        return doc_scores

    def rerank_with_quality_fusion(
        self,
        query: str,
        documents: List[Document],
        top_k: int = None,
        quality_weight: float = 0.3
    ) -> List[Document]:
        """
        Combine cross-encoder reranking with existing quality scores.

        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of top results to return
            quality_weight: Weight for quality score (0-1)

        Returns:
            Reranked documents
        """
        doc_scores = self.rerank(query, documents)

        # Normalize cross-encoder scores to 0-1 range
        scores = [s for _, s in doc_scores]
        min_score, max_score = min(scores), max(scores)
        score_range = max_score - min_score if max_score > min_score else 1.0

        # Fuse with quality scores
        fused_scores = []
        for doc, ce_score in doc_scores:
            normalized_ce = (ce_score - min_score) / score_range
            quality_score = doc.metadata.get("quality_score", 0.5)

            # Weighted combination
            fused_score = (
                (1 - quality_weight) * normalized_ce +
                quality_weight * quality_score
            )
            fused_scores.append((doc, fused_score))

        # Sort by fused score
        fused_scores.sort(key=lambda x: x[1], reverse=True)

        result = [doc for doc, _ in fused_scores]
        if top_k:
            result = result[:top_k]

        return result
```

**Integration into Enhanced Retriever:**

```python
# Modify backend/app/services/enhanced_retrieval.py

from app.services.reranker import CrossEncoderReranker

class EnhancedRetriever(BaseRetriever):
    def __init__(
        self,
        base_retriever: BaseRetriever,
        use_cross_encoder: bool = True,
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        **kwargs
    ):
        self.use_cross_encoder = use_cross_encoder
        if use_cross_encoder:
            self.reranker = CrossEncoderReranker(cross_encoder_model)
        # ... rest of init

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        # Get initial results
        initial_results = self.base_retriever.get_relevant_documents(query)

        # Apply content filtering
        filtered_results = self._apply_content_filtering(initial_results, query)

        # Apply cross-encoder reranking
        if self.use_cross_encoder and filtered_results:
            filtered_results = self.reranker.rerank_with_quality_fusion(
                query, filtered_results, quality_weight=0.3
            )
        elif self.rerank_by_quality and filtered_results:
            # Fallback to existing quality-based reranking
            filtered_results = self._rerank_by_quality(filtered_results, query)

        return filtered_results
```

**Configuration:**

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # Reranker settings
    RAG_USE_RERANKER: bool = True
    RAG_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RAG_RERANKER_TOP_K: int = 10
    RAG_RERANKER_QUALITY_WEIGHT: float = 0.3
```

#### Option B: LLM-Based Reranking (Already Partially Implemented)

You already use LLM filtering in some places:

**Location:** `backend/app/api/routes/chatbot.py` line 1854+

```python
if settings.RAG_ENABLE_LLM_RELEVANCE_FILTER and docs:
    # Use LLM to check relevance of each chunk
    for doc in docs:
        relevance_check = invoke_llm(...)
```

**Recommendation:**

- Keep this as an **optional** fallback for critical queries
- Use cross-encoder reranking as the default (faster, more cost-effective)
- LLM reranking is expensive and slow but most accurate

---

### ⚠️ 3. Query Expansion (NOT IMPLEMENTED)

**What It Does:**
Transforms a single query into multiple related queries to capture different aspects of user intent.

**Benefits:**

- Captures synonyms and related terms
- Handles ambiguous queries better
- Improves recall for complex questions

**Implementation:**

```python
# backend/app/services/query_expansion.py

from typing import List
from app.services.llm import create_llm
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class QueryExpander:
    """
    Expands user queries into multiple variations to improve retrieval.
    """

    EXPANSION_PROMPT = """Given the following question, generate {num_variations} variations
that capture different ways to ask the same thing or related aspects of the question.

Each variation should:
- Use different wording but maintain the core intent
- Include relevant synonyms and related terms
- Be self-contained and understandable on its own

Original Question: {question}

Generate {num_variations} variations (one per line):
"""

    def __init__(self, llm=None, provider: str = "openai", model_id: str = "gpt-4o-mini"):
        """
        Initialize query expander.

        Args:
            llm: Pre-initialized LLM (optional)
            provider: LLM provider if llm not provided
            model_id: Model ID if llm not provided
        """
        if llm:
            self.llm = llm
        else:
            from app.services.llm import create_llm
            self.llm = create_llm(provider=provider, model_id=model_id, temperature=0.7)

        logger.info("Initialized QueryExpander")

    def expand_query(self, question: str, num_variations: int = 3) -> List[str]:
        """
        Expand a query into multiple variations.

        Args:
            question: Original user question
            num_variations: Number of variations to generate

        Returns:
            List of query variations (including original)
        """
        try:
            prompt = self.EXPANSION_PROMPT.format(
                question=question,
                num_variations=num_variations
            )

            response = self.llm.invoke(prompt)

            # Parse response
            variations = [
                line.strip().lstrip('0123456789.-) ')
                for line in response.content.strip().split('\n')
                if line.strip()
            ]

            # Always include original question
            all_queries = [question] + variations[:num_variations]

            logger.info(f"Expanded query into {len(all_queries)} variations")
            logger.debug(f"Variations: {all_queries}")

            return all_queries

        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return [question]  # Fallback to original

    def expand_with_keywords(self, question: str) -> List[str]:
        """
        Expand query by extracting and combining key concepts.

        Args:
            question: Original question

        Returns:
            List of query variations
        """
        keyword_prompt = f"""Extract 3-5 key concepts/keywords from this question,
then create 2 alternative search queries using different combinations of these concepts.

Question: {question}

Format:
Keywords: [list]
Query 1: [alternative query]
Query 2: [alternative query]
"""

        try:
            response = self.llm.invoke(keyword_prompt)

            # Parse response to extract queries
            lines = response.content.strip().split('\n')
            queries = [question]  # Original

            for line in lines:
                if line.startswith('Query'):
                    query = line.split(':', 1)[1].strip()
                    queries.append(query)

            return queries

        except Exception as e:
            logger.error(f"Keyword expansion failed: {e}")
            return [question]
```

**Integration Example:**

```python
# Modify backend/app/services/enhanced_retrieval.py or create new retriever

class QueryExpandingRetriever(BaseRetriever):
    """
    Retriever that expands queries and aggregates results.
    """

    def __init__(
        self,
        base_retriever: BaseRetriever,
        query_expander: QueryExpander,
        num_variations: int = 2,
        fusion_mode: str = "reciprocal_rank"  # or "simple_aggregate"
    ):
        self.base_retriever = base_retriever
        self.query_expander = query_expander
        self.num_variations = num_variations
        self.fusion_mode = fusion_mode

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        # Expand query
        query_variations = self.query_expander.expand_query(
            query, self.num_variations
        )

        # Retrieve for each variation
        all_results = []
        for var_query in query_variations:
            results = self.base_retriever.get_relevant_documents(var_query)
            all_results.append((var_query, results))

        # Fuse results
        fused_docs = self._fuse_results(all_results)

        return fused_docs

    def _fuse_results(self, query_results: List[Tuple[str, List[Document]]]) -> List[Document]:
        """Combine results from multiple queries using Reciprocal Rank Fusion."""
        # Implementation in RAG Fusion section below
        pass
```

**Configuration:**

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    RAG_ENABLE_QUERY_EXPANSION: bool = False
    RAG_QUERY_EXPANSION_VARIATIONS: int = 2
    RAG_QUERY_EXPANSION_MODEL: str = "gpt-4o-mini"
```

---

### ⚠️ 4. HyDE - Hypothetical Document Embeddings (NOT IMPLEMENTED)

**What It Does:**
Instead of searching with the user's question directly, HyDE:

1. Uses LLM to generate a hypothetical answer to the question
2. Embeds the hypothetical answer
3. Searches for documents similar to the hypothetical answer

**Why It Works:**

- Documents are more similar to answers than to questions
- Reduces semantic gap between query and content
- Particularly effective for technical/domain-specific queries

**Implementation:**

```python
# backend/app/services/hyde.py

from typing import List
from langchain.schema import Document
from langchain_core.documents import Document as LangchainDocument
import logging

logger = logging.getLogger(__name__)

class HyDERetriever:
    """
    Hypothetical Document Embeddings (HyDE) retriever.
    Generates hypothetical answers and uses them for retrieval.
    """

    HYDE_PROMPT = """Given the following question, write a hypothetical answer
that would be found in a relevant document. The answer should be:
- Factual and detailed
- Written in a document/article style (not conversational)
- 2-3 paragraphs long
- Include technical terms and concepts that would appear in source documents

Question: {question}

Hypothetical Document Passage:
"""

    def __init__(
        self,
        vector_store,
        llm,
        num_hypothetical_docs: int = 1,
        fallback_to_original: bool = True
    ):
        """
        Initialize HyDE retriever.

        Args:
            vector_store: ChromaDB or other vector store
            llm: Language model for generating hypothetical documents
            num_hypothetical_docs: Number of hypothetical docs to generate
            fallback_to_original: Also search with original query if True
        """
        self.vector_store = vector_store
        self.llm = llm
        self.num_hypothetical_docs = num_hypothetical_docs
        self.fallback_to_original = fallback_to_original
        logger.info("Initialized HyDERetriever")

    def generate_hypothetical_document(self, question: str) -> str:
        """
        Generate a hypothetical document that would answer the question.

        Args:
            question: User's question

        Returns:
            Hypothetical document text
        """
        try:
            prompt = self.HYDE_PROMPT.format(question=question)
            response = self.llm.invoke(prompt)

            hypothetical_doc = response.content.strip()

            logger.debug(
                f"Generated hypothetical doc ({len(hypothetical_doc)} chars) "
                f"for question: {question[:50]}..."
            )

            return hypothetical_doc

        except Exception as e:
            logger.error(f"HyDE generation failed: {e}")
            return question  # Fallback to original question

    def get_relevant_documents(
        self,
        question: str,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve documents using HyDE approach.

        Args:
            question: User's question
            k: Number of documents to retrieve

        Returns:
            Retrieved documents
        """
        results = []

        # Generate and search with hypothetical document(s)
        for i in range(self.num_hypothetical_docs):
            hypothetical_doc = self.generate_hypothetical_document(question)

            # Search using hypothetical document
            hyde_results = self.vector_store.similarity_search(
                hypothetical_doc,
                k=k
            )

            # Tag results as HyDE-retrieved
            for doc in hyde_results:
                doc.metadata['retrieval_method'] = 'hyde'

            results.extend(hyde_results)

        # Optionally also search with original question
        if self.fallback_to_original:
            original_results = self.vector_store.similarity_search(question, k=k//2)
            for doc in original_results:
                doc.metadata['retrieval_method'] = 'direct'
            results.extend(original_results)

        # Deduplicate while preserving order
        seen = set()
        unique_results = []
        for doc in results:
            doc_id = doc.page_content[:100]  # Use first 100 chars as ID
            if doc_id not in seen:
                seen.add(doc_id)
                unique_results.append(doc)

        logger.info(
            f"HyDE retrieval: {len(unique_results)} unique docs "
            f"from {len(results)} total results"
        )

        return unique_results[:k]
```

**Integration:**

```python
# Create HyDE-enhanced retriever factory

def create_hyde_retriever(
    chroma_db,
    llm,
    k: int = 5,
    use_hybrid: bool = True
):
    """Create retriever with HyDE support."""

    if use_hybrid:
        # Combine HyDE with hybrid search
        hyde_retriever = HyDERetriever(
            vector_store=chroma_db,
            llm=llm,
            num_hypothetical_docs=1,
            fallback_to_original=True
        )
        return hyde_retriever
    else:
        # Standard retriever
        return chroma_db.as_retriever(search_kwargs={"k": k})
```

**Configuration:**

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    RAG_ENABLE_HYDE: bool = False
    RAG_HYDE_NUM_DOCS: int = 1
    RAG_HYDE_FALLBACK_TO_ORIGINAL: bool = True
    RAG_HYDE_MODEL: str = "gpt-4o-mini"
```

**When to Use HyDE:**

- ✅ Technical/domain-specific questions
- ✅ When you have high-quality source documents
- ✅ Questions where answer format is predictable
- ❌ Simple factual lookups
- ❌ When LLM latency is critical
- ❌ Open-ended exploratory queries

---

### ⚠️ 5. RAG Fusion (NOT IMPLEMENTED)

**What It Does:**
Combines multiple retrieval strategies and fuses their results using **Reciprocal Rank Fusion (RRF)**.

**Benefits:**

- Leverages strengths of different retrieval methods
- More robust than any single approach
- Particularly effective when combined with query expansion

**Core Algorithm - Reciprocal Rank Fusion:**

```
For each document appearing in results:
RRF_score = Σ (1 / (k + rank_in_query_i))

Where:
- k = constant (typically 60)
- rank_in_query_i = position of document in results for query i
- Sum across all queries that returned this document
```

**Implementation:**

```python
# backend/app/services/rag_fusion.py

from typing import List, Dict, Tuple
from langchain.schema import Document
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RAGFusion:
    """
    RAG Fusion: Combines multiple retrieval strategies using Reciprocal Rank Fusion.
    """

    def __init__(self, k: int = 60):
        """
        Initialize RAG Fusion.

        Args:
            k: Constant for RRF formula (typically 60)
        """
        self.k = k
        logger.info(f"Initialized RAGFusion with k={k}")

    def reciprocal_rank_fusion(
        self,
        ranked_lists: List[List[Document]],
        top_k: int = None
    ) -> List[Tuple[Document, float]]:
        """
        Fuse multiple ranked lists using Reciprocal Rank Fusion.

        Args:
            ranked_lists: List of document lists (each list is from one retrieval)
            top_k: Return top K results

        Returns:
            List of (document, rrf_score) tuples sorted by score
        """
        # Document scores accumulator
        doc_scores = defaultdict(float)
        doc_objects = {}  # Store actual document objects

        for ranked_list in ranked_lists:
            for rank, doc in enumerate(ranked_list):
                # Create document ID (using content hash or metadata)
                doc_id = self._get_doc_id(doc)

                # Store document object (first occurrence)
                if doc_id not in doc_objects:
                    doc_objects[doc_id] = doc

                # RRF score: 1 / (k + rank)
                # rank is 0-indexed, so rank 0 gets highest score
                rrf_score = 1.0 / (self.k + rank + 1)
                doc_scores[doc_id] += rrf_score

        # Convert to list of (doc, score) tuples
        scored_docs = [
            (doc_objects[doc_id], score)
            for doc_id, score in doc_scores.items()
        ]

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Limit to top_k if specified
        if top_k:
            scored_docs = scored_docs[:top_k]

        logger.info(
            f"Fused {len(ranked_lists)} result lists into "
            f"{len(scored_docs)} unique documents"
        )

        return scored_docs

    def _get_doc_id(self, doc: Document) -> str:
        """
        Generate unique ID for a document.

        Args:
            doc: Document object

        Returns:
            Unique document identifier
        """
        # Use source + chunk_index if available
        if 'source' in doc.metadata and 'chunk_index' in doc.metadata:
            return f"{doc.metadata['source']}_{doc.metadata['chunk_index']}"

        # Fallback to content hash
        import hashlib
        content_hash = hashlib.md5(
            doc.page_content.encode()
        ).hexdigest()
        return content_hash


class RAGFusionRetriever:
    """
    Complete RAG Fusion retriever combining query expansion and result fusion.
    """

    def __init__(
        self,
        vector_retriever,
        keyword_retriever,
        query_expander=None,
        llm=None,
        num_query_variations: int = 3,
        k: int = 5,
        rrf_k: int = 60
    ):
        """
        Initialize RAG Fusion retriever.

        Args:
            vector_retriever: Vector-based retriever
            keyword_retriever: BM25/keyword retriever
            query_expander: Query expansion service (created if None)
            llm: LLM for query expansion
            num_query_variations: Number of query variations to generate
            k: Number of documents to retrieve per query
            rrf_k: RRF constant
        """
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.k = k
        self.fusion = RAGFusion(k=rrf_k)

        # Initialize query expander
        if query_expander:
            self.query_expander = query_expander
        elif llm:
            from app.services.query_expansion import QueryExpander
            self.query_expander = QueryExpander(llm=llm)
        else:
            self.query_expander = None

        self.num_query_variations = num_query_variations

        logger.info("Initialized RAGFusionRetriever")

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve documents using RAG Fusion approach.

        Args:
            query: User query

        Returns:
            Fused and ranked documents
        """
        # Step 1: Generate query variations
        if self.query_expander:
            queries = self.query_expander.expand_query(
                query,
                self.num_query_variations
            )
        else:
            queries = [query]

        logger.info(f"Processing {len(queries)} query variations")

        # Step 2: Retrieve with multiple methods for each query
        all_results = []

        for q in queries:
            # Vector search
            vector_results = self.vector_retriever.get_relevant_documents(q)
            all_results.append(vector_results[:self.k])

            # Keyword search
            if self.keyword_retriever:
                keyword_results = self.keyword_retriever.get_relevant_documents(q)
                all_results.append(keyword_results[:self.k])

        # Step 3: Apply Reciprocal Rank Fusion
        fused_results = self.fusion.reciprocal_rank_fusion(
            all_results,
            top_k=self.k
        )

        # Extract documents (discard scores)
        documents = [doc for doc, score in fused_results]

        logger.info(
            f"RAG Fusion: Retrieved {len(documents)} documents "
            f"from {len(all_results)} result sets"
        )

        return documents
```

**Integration Example:**

```python
# backend/app/services/enhanced_retrieval.py

from app.services.rag_fusion import RAGFusionRetriever
from app.services.query_expansion import QueryExpander

def create_rag_fusion_retriever(
    chroma_db,
    llm,
    search_kwargs: Dict[str, Any] = None,
    num_query_variations: int = 3,
    rrf_k: int = 60
):
    """
    Create a RAG Fusion retriever combining multiple strategies.

    Args:
        chroma_db: ChromaDB instance
        llm: Language model for query expansion
        search_kwargs: Search parameters
        num_query_variations: Number of query variations
        rrf_k: Reciprocal Rank Fusion constant

    Returns:
        RAGFusionRetriever instance
    """
    from app.core.config import settings

    if search_kwargs is None:
        search_kwargs = {"k": settings.RAG_NUM_CHUNKS}

    # Create base retrievers
    vector_retriever = chroma_db.as_retriever(search_kwargs=search_kwargs)

    from app.services.retrievers import BM25KeywordRetriever
    keyword_retriever = BM25KeywordRetriever.from_chroma(
        chroma_db,
        k=search_kwargs.get("k", settings.RAG_NUM_CHUNKS)
    )

    # Create query expander
    query_expander = QueryExpander(llm=llm)

    # Create RAG Fusion retriever
    fusion_retriever = RAGFusionRetriever(
        vector_retriever=vector_retriever,
        keyword_retriever=keyword_retriever,
        query_expander=query_expander,
        num_query_variations=num_query_variations,
        k=search_kwargs.get("k", settings.RAG_NUM_CHUNKS),
        rrf_k=rrf_k
    )

    return fusion_retriever
```

**Configuration:**

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    RAG_ENABLE_FUSION: bool = False
    RAG_FUSION_QUERY_VARIATIONS: int = 3
    RAG_FUSION_RRF_K: int = 60
    RAG_FUSION_RESULTS_PER_QUERY: int = 5
```

---

## Complete Implementation Strategy

### Phase 1: Foundation (Week 1-2)

**Priority: High**

1. **Add Cross-Encoder Reranker**

   - Install dependencies: `sentence-transformers`
   - Implement `CrossEncoderReranker` class
   - Integrate with `EnhancedRetriever`
   - Add configuration settings
   - Test with existing queries

2. **Create Service Modules**
   - `backend/app/services/reranker.py`
   - `backend/app/services/query_expansion.py`
   - `backend/app/services/hyde.py`
   - `backend/app/services/rag_fusion.py`

### Phase 2: Query Enhancement (Week 3-4)

**Priority: Medium**

3. **Implement Query Expansion**

   - Create `QueryExpander` class
   - Add LLM-based expansion
   - Add keyword-based expansion
   - Make it configurable per endpoint

4. **Add HyDE Support**
   - Implement `HyDERetriever`
   - Create hypothetical document prompts
   - Test on technical queries

### Phase 3: Advanced Fusion (Week 5-6)

**Priority: Medium-Low**

5. **Implement RAG Fusion**

   - Create `RAGFusion` core algorithm
   - Implement `RAGFusionRetriever`
   - Combine with query expansion
   - Benchmark against baseline

6. **Create Retriever Factory**
   - Unified retriever creation interface
   - Strategy selection based on query type
   - Configuration-driven approach

### Phase 4: Integration & Optimization (Week 7-8)

7. **Update Existing Endpoints**

   - Add retriever strategy selection to chatbot
   - Update VeraDoc with new options
   - Add strategy selection UI

8. **Performance Optimization**

   - Cache query expansions
   - Batch reranking where possible
   - Add async support for parallel retrieval

9. **Monitoring & Analytics**
   - Track retrieval strategy performance
   - Log query expansion effectiveness
   - A/B test different configurations

---

## Recommended Architecture

```python
# backend/app/services/retriever_factory.py

from enum import Enum
from typing import Optional
from langchain.schema import BaseRetriever

class RetrievalStrategy(str, Enum):
    BASIC_VECTOR = "basic_vector"
    HYBRID = "hybrid"  # Current default
    HYBRID_RERANKED = "hybrid_reranked"  # Hybrid + cross-encoder
    QUERY_EXPANSION = "query_expansion"
    HYDE = "hyde"
    RAG_FUSION = "rag_fusion"  # Full stack


class SmartRetrieverFactory:
    """
    Factory for creating retrievers with different strategies.
    """

    @staticmethod
    def create_retriever(
        strategy: RetrievalStrategy,
        chroma_db,
        llm=None,
        search_kwargs: Optional[dict] = None,
        **kwargs
    ) -> BaseRetriever:
        """
        Create a retriever based on strategy.

        Args:
            strategy: Retrieval strategy to use
            chroma_db: Vector database
            llm: Language model (required for some strategies)
            search_kwargs: Search parameters
            **kwargs: Strategy-specific parameters

        Returns:
            Configured retriever
        """

        if strategy == RetrievalStrategy.BASIC_VECTOR:
            return chroma_db.as_retriever(search_kwargs=search_kwargs)

        elif strategy == RetrievalStrategy.HYBRID:
            return create_ensemble_retriever(
                chroma_db,
                vector_weight=kwargs.get('vector_weight', 0.7),
                keyword_weight=kwargs.get('keyword_weight', 0.3),
                search_kwargs=search_kwargs
            )

        elif strategy == RetrievalStrategy.HYBRID_RERANKED:
            base_retriever = create_ensemble_retriever(
                chroma_db, search_kwargs=search_kwargs
            )
            return EnhancedRetriever(
                base_retriever=base_retriever,
                use_cross_encoder=True,
                cross_encoder_model=kwargs.get(
                    'reranker_model',
                    'cross-encoder/ms-marco-MiniLM-L-6-v2'
                )
            )

        elif strategy == RetrievalStrategy.QUERY_EXPANSION:
            if not llm:
                raise ValueError("LLM required for query expansion")

            from app.services.query_expansion import QueryExpander
            expander = QueryExpander(llm=llm)
            base_retriever = create_ensemble_retriever(
                chroma_db, search_kwargs=search_kwargs
            )
            return QueryExpandingRetriever(
                base_retriever=base_retriever,
                query_expander=expander,
                num_variations=kwargs.get('num_variations', 2)
            )

        elif strategy == RetrievalStrategy.HYDE:
            if not llm:
                raise ValueError("LLM required for HyDE")

            from app.services.hyde import HyDERetriever
            return HyDERetriever(
                vector_store=chroma_db,
                llm=llm,
                num_hypothetical_docs=kwargs.get('num_hypothetical_docs', 1),
                fallback_to_original=kwargs.get('fallback_to_original', True)
            )

        elif strategy == RetrievalStrategy.RAG_FUSION:
            if not llm:
                raise ValueError("LLM required for RAG Fusion")

            return create_rag_fusion_retriever(
                chroma_db=chroma_db,
                llm=llm,
                search_kwargs=search_kwargs,
                num_query_variations=kwargs.get('num_query_variations', 3),
                rrf_k=kwargs.get('rrf_k', 60)
            )

        else:
            raise ValueError(f"Unknown strategy: {strategy}")
```

---

## Configuration Management

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ====== RAG Retrieval Strategy Configuration ======

    # Default strategy per use case
    RAG_DEFAULT_STRATEGY: str = "hybrid"  # Options: see RetrievalStrategy enum
    RAG_CHATBOT_STRATEGY: str = "hybrid_reranked"
    RAG_VERADOC_STRATEGY: str = "rag_fusion"
    RAG_FORMCONNECT_STRATEGY: str = "hybrid"

    # ====== Hybrid Search Configuration ======
    RAG_HYBRID_VECTOR_WEIGHT: float = 0.7
    RAG_HYBRID_KEYWORD_WEIGHT: float = 0.3

    # ====== Reranker Configuration ======
    RAG_ENABLE_RERANKER: bool = True
    RAG_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    # Options:
    # - cross-encoder/ms-marco-MiniLM-L-6-v2 (fast, good)
    # - cross-encoder/ms-marco-MiniLM-L-12-v2 (better, slower)
    # - BAAI/bge-reranker-large (best, slowest)
    RAG_RERANKER_TOP_K: int = 10
    RAG_RERANKER_QUALITY_WEIGHT: float = 0.3

    # ====== Query Expansion Configuration ======
    RAG_ENABLE_QUERY_EXPANSION: bool = False
    RAG_QUERY_EXPANSION_VARIATIONS: int = 2
    RAG_QUERY_EXPANSION_MODEL: str = "gpt-4o-mini"
    RAG_QUERY_EXPANSION_TEMPERATURE: float = 0.7

    # ====== HyDE Configuration ======
    RAG_ENABLE_HYDE: bool = False
    RAG_HYDE_NUM_DOCS: int = 1
    RAG_HYDE_FALLBACK_TO_ORIGINAL: bool = True
    RAG_HYDE_MODEL: str = "gpt-4o-mini"

    # ====== RAG Fusion Configuration ======
    RAG_ENABLE_FUSION: bool = False
    RAG_FUSION_QUERY_VARIATIONS: int = 3
    RAG_FUSION_RRF_K: int = 60
    RAG_FUSION_RESULTS_PER_QUERY: int = 5

    # ====== Performance & Caching ======
    RAG_CACHE_QUERY_EXPANSIONS: bool = True
    RAG_CACHE_TTL_SECONDS: int = 3600
    RAG_ENABLE_PARALLEL_RETRIEVAL: bool = True
```

---

## Performance Considerations

### Latency Impact

| Strategy          | Latency | Cost | Accuracy |
| ----------------- | ------- | ---- | -------- |
| Basic Vector      | ~50ms   | $    | ★★★☆☆    |
| Hybrid (current)  | ~80ms   | $    | ★★★★☆    |
| + Cross-Encoder   | ~150ms  | $$   | ★★★★★    |
| + Query Expansion | ~500ms  | $$$  | ★★★★★    |
| + HyDE            | ~400ms  | $$$  | ★★★★☆    |
| RAG Fusion (all)  | ~800ms  | $$$$ | ★★★★★    |

### Cost Optimization

1. **Use smaller models for non-critical paths**

   - `gpt-4o-mini` for query expansion
   - Smaller cross-encoders for high-volume queries

2. **Cache aggressively**

   - Query expansions
   - Hypothetical documents
   - Reranker results

3. **Adaptive strategy selection**
   - Simple queries → basic retrieval
   - Complex queries → RAG fusion
   - Use query complexity classifier

---

## Testing & Validation

### Create Evaluation Dataset

```python
# backend/tests/test_retrieval_strategies.py

import pytest
from app.services.retriever_factory import SmartRetrieverFactory, RetrievalStrategy

# Test queries with known good results
TEST_CASES = [
    {
        "query": "What are the symptoms of diabetes?",
        "expected_docs": ["diabetes_symptoms.pdf"],
        "difficulty": "easy"
    },
    {
        "query": "Compare treatment protocols for type 1 vs type 2",
        "expected_docs": ["diabetes_treatment.pdf", "protocols.pdf"],
        "difficulty": "medium"
    },
    # Add more test cases
]

@pytest.mark.parametrize("strategy", [
    RetrievalStrategy.HYBRID,
    RetrievalStrategy.HYBRID_RERANKED,
    RetrievalStrategy.RAG_FUSION
])
def test_retrieval_quality(strategy, chroma_db, llm):
    """Test retrieval quality across strategies."""

    factory = SmartRetrieverFactory()
    retriever = factory.create_retriever(
        strategy=strategy,
        chroma_db=chroma_db,
        llm=llm
    )

    for test_case in TEST_CASES:
        docs = retriever.get_relevant_documents(test_case["query"])

        # Check if expected docs are in top results
        retrieved_sources = [d.metadata.get("source") for d in docs[:5]]

        for expected_source in test_case["expected_docs"]:
            assert any(
                expected_source in source
                for source in retrieved_sources
            ), f"Expected {expected_source} not found for query: {test_case['query']}"
```

---

## User-Facing Integration

### API Updates

```python
# backend/app/api/routes/chatbot.py

from app.services.retriever_factory import SmartRetrieverFactory, RetrievalStrategy

@router.post("/knowledge-base/{kb_id}")
async def query_knowledge_base(
    session: SessionDep,
    current_user: CurrentUser,
    kb_id: str,
    question: str,
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID_RERANKED,
    # ... other params
):
    """
    Query knowledge base with configurable retrieval strategy.
    """

    # Create retriever based on strategy
    retriever = SmartRetrieverFactory.create_retriever(
        strategy=retrieval_strategy,
        chroma_db=chroma_db,
        llm=llm,
        search_kwargs={"k": settings.RAG_NUM_CHUNKS}
    )

    # Rest of implementation...
```

### Frontend Updates

```typescript
// Add retrieval strategy selector in UI
export enum RetrievalStrategy {
  Hybrid = "hybrid",
  HybridReranked = "hybrid_reranked",
  QueryExpansion = "query_expansion",
  HyDE = "hyde",
  RAGFusion = "rag_fusion",
}

// In chatbot settings
;<Select
  label="Retrieval Strategy"
  value={retrievalStrategy}
  onChange={(e) => setRetrievalStrategy(e.target.value)}
>
  <option value="hybrid">Hybrid (Fast)</option>
  <option value="hybrid_reranked">Hybrid + Reranker (Balanced)</option>
  <option value="query_expansion">Query Expansion (Thorough)</option>
  <option value="rag_fusion">RAG Fusion (Most Accurate)</option>
</Select>
```

---

## Monitoring & Analytics

```python
# backend/app/services/retrieval_analytics.py

import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RetrievalAnalytics:
    """Track retrieval strategy performance."""

    @staticmethod
    def log_retrieval(
        strategy: str,
        query: str,
        num_results: int,
        latency_ms: float,
        user_id: str
    ):
        """Log retrieval event for analytics."""

        logger.info(
            "retrieval_event",
            extra={
                "strategy": strategy,
                "query_length": len(query),
                "num_results": num_results,
                "latency_ms": latency_ms,
                "user_id": user_id,
                "timestamp": time.time()
            }
        )

    @staticmethod
    def log_user_feedback(
        strategy: str,
        query: str,
        was_helpful: bool,
        user_id: str
    ):
        """Log user feedback on retrieval quality."""

        logger.info(
            "retrieval_feedback",
            extra={
                "strategy": strategy,
                "query": query,
                "was_helpful": was_helpful,
                "user_id": user_id,
                "timestamp": time.time()
            }
        )
```

---

## Summary & Recommendations

### What You Already Have ✅

1. **Hybrid Search** - Excellent foundation combining vector + BM25
2. **Quality-based Reranking** - Good heuristic approach
3. **Content Filtering** - Bibliography filtering improves results
4. **Query Rephrasing** - Context-aware question reformulation

### What to Add First 🎯

**Priority 1: Cross-Encoder Reranker**

- Biggest accuracy improvement for least effort
- ~100ms latency increase
- Drop-in replacement for current reranking

**Priority 2: Query Expansion**

- Significant improvement for complex questions
- Relatively easy to implement
- Pairs well with existing hybrid search

**Priority 3: RAG Fusion**

- Best overall accuracy
- Higher latency and cost
- Ideal for critical use cases (VeraDoc, ReportGenie)

### Recommended Implementation Order

1. **Week 1-2:** Cross-Encoder Reranker
2. **Week 3-4:** Query Expansion
3. **Week 5-6:** RAG Fusion (combines expansion + fusion)
4. **Week 7-8:** HyDE (for specialized technical queries)

### When to Use Each Strategy

- **Hybrid (current):** Default for most queries, fast, good balance
- **Hybrid + Reranked:** High-quality results, acceptable latency
- **Query Expansion:** Complex/ambiguous questions, exploratory queries
- **HyDE:** Technical queries, domain-specific content
- **RAG Fusion:** Mission-critical accuracy, worth the cost/latency

---

## Additional Resources

### Research Papers

- **Hybrid Search:** "The Best of Both Worlds: Combining Sparse and Dense Retrieval"
- **Reranking:** "MS MARCO: A Human Generated MAchine Reading COmprehension Dataset"
- **HyDE:** "Precise Zero-Shot Dense Retrieval without Relevance Labels" (Gao et al., 2022)
- **RAG Fusion:** "Forget RAG, the Future is RAG-Fusion" (Rackauckas, 2023)

### Libraries

- `sentence-transformers` - Cross-encoder models
- `langchain` - Already using, has retriever abstractions
- `rank-bm25` - BM25 implementation (already using via LangChain)

### Benchmarking Tools

- BEIR (Benchmarking Information Retrieval)
- MTEB (Massive Text Embedding Benchmark)

---

**Next Steps:**

1. Review this guide with your team
2. Decide on implementation priorities
3. Set up development branch for RAG enhancements
4. Create evaluation dataset for testing
5. Implement cross-encoder reranker first
6. Measure improvements before moving to next phase

Let me know if you need detailed implementation help for any specific component!
