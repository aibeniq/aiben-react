# Cross-Encoder Reranker Implementation

## Overview

This implementation adds cross-encoder reranking to improve RAG retrieval quality. Cross-encoders provide more accurate relevance scoring than bi-encoder approaches by jointly encoding query-document pairs.

## What Was Implemented

### 1. Core Reranker Service (`backend/app/services/reranker.py`)

**CrossEncoderReranker Class:**
- Uses sentence-transformers library
- Default model: `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast, good accuracy)
- Alternative models supported (see configuration)
- Three reranking methods:
  - `rerank()` - Basic relevance scoring
  - `rerank_with_quality_fusion()` - Combines cross-encoder scores with quality metadata
  - `rerank_with_metadata_boost()` - Adds content type and recency boosts

### 2. Enhanced Retriever Updates (`backend/app/services/enhanced_retrieval.py`)

**EnhancedRetriever Class:**
- Added cross-encoder support as optional enhancement
- Graceful fallback to heuristic reranking if cross-encoder fails
- Quality fusion combines both approaches
- Updated `create_enhanced_retriever()` factory function
- Updated `SmartRetrieverFactory` methods

### 3. Configuration (`backend/app/core/config.py`)

New settings added:
```python
RAG_USE_RERANKER: bool = False  # Enable/disable
RAG_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RAG_RERANKER_TOP_K: int = 10
RAG_RERANKER_QUALITY_WEIGHT: float = 0.3
```

### 4. Dependencies (`backend/pyproject.toml`)

Added optional dependency:
```toml
[project.optional-dependencies]
reranker = [
    "sentence-transformers>=2.2.0,<4.0.0"
]
```

## Installation

### Option 1: Install as Optional Dependency (Recommended)

```bash
# Navigate to backend directory
cd backend

# Install with reranker support
uv sync --extra reranker
```

### Option 2: Install Directly

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install sentence-transformers
uv pip install sentence-transformers
```

## Testing

### Run Test Script

```bash
cd backend
python test_reranker.py
```

This will run 4 tests:
1. Basic reranking
2. Quality fusion reranking
3. Convenience function usage
4. Different model comparison

Expected output:
```
✓ All tests completed successfully!
```

### Manual Testing

```python
from app.services.reranker import CrossEncoderReranker
from langchain_core.documents import Document

# Initialize reranker
reranker = CrossEncoderReranker()

# Create test documents
docs = [
    Document(page_content="Python is a programming language."),
    Document(page_content="Python snakes are reptiles."),
]

# Rerank
query = "python programming"
results = reranker.rerank(query, docs)

for doc, score in results:
    print(f"Score: {score:.3f} - {doc.page_content}")
```

## Configuration

### Enable Reranking

Update `.env` file or environment variables:

```bash
# Enable cross-encoder reranking
RAG_USE_RERANKER=True

# Choose model (optional, default shown)
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Top K results after reranking
RAG_RERANKER_TOP_K=10

# Quality fusion weight (0-1)
RAG_RERANKER_QUALITY_WEIGHT=0.3
```

### Model Options

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | 82MB | Fast | Good | Default, general use |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | 133MB | Medium | Better | Higher accuracy needed |
| `BAAI/bge-reranker-base` | 279MB | Medium | Good | Multilingual support |
| `BAAI/bge-reranker-large` | 1.11GB | Slow | Best | Maximum accuracy |

### Performance Tuning

**Quality Weight (0-1):**
- `0.0` = Only use cross-encoder scores (pure relevance)
- `0.3` = 70% cross-encoder + 30% quality (recommended)
- `0.5` = Balanced fusion
- `1.0` = Only use quality scores (ignore cross-encoder)

**Top K:**
- Lower values (5-10) for precise results
- Higher values (15-20) for comprehensive coverage

## Integration Examples

### Example 1: Using in Existing Retrievers

The reranker is automatically integrated when you enable it:

```python
from app.services.enhanced_retrieval import create_enhanced_retriever
from app.core.config import settings

# Create retriever with reranking enabled
retriever = create_enhanced_retriever(
    chroma_db=chroma_db,
    use_cross_encoder=settings.RAG_USE_RERANKER,
    cross_encoder_model=settings.RAG_RERANKER_MODEL,
    reranker_quality_weight=settings.RAG_RERANKER_QUALITY_WEIGHT,
)

# Use normally - reranking happens automatically
docs = retriever.get_relevant_documents("your query")
```

### Example 2: SmartRetrieverFactory

```python
from app.services.enhanced_retrieval import SmartRetrieverFactory
from app.core.config import settings

# Academic paper retriever with reranking
retriever = SmartRetrieverFactory.create_academic_paper_retriever(
    chroma_db=chroma_db,
    use_cross_encoder=settings.RAG_USE_RERANKER,
)
```

### Example 3: Direct Reranker Usage

```python
from app.services.reranker import rerank_documents

# Quick reranking without instantiating class
reranked_docs = rerank_documents(
    query="your query",
    documents=retrieved_docs,
    top_k=5
)
```

## How It Works

### Retrieval + Reranking Pipeline

```
1. Initial Retrieval (Hybrid Search)
   ↓
   [Vector Search (70%) + BM25 Keyword (30%)]
   ↓
   Retrieved 20 chunks

2. Content Filtering
   ↓
   [Remove bibliography, low quality content]
   ↓
   Filtered to ~15 chunks

3. Cross-Encoder Reranking ✨ NEW
   ↓
   [Joint query-document encoding]
   ↓
   Relevance scores computed

4. Quality Fusion
   ↓
   [70% cross-encoder + 30% quality metadata]
   ↓
   Final ranking

5. Top K Results
   ↓
   Return best 10 chunks
```

### Why Cross-Encoders Are Better

**Bi-Encoder (Traditional Vector Search):**
- Encodes query and document separately
- Fast (can pre-compute document embeddings)
- Good for initial retrieval
- Semantic similarity may miss relevance nuances

**Cross-Encoder (Reranking):**
- Encodes query + document together
- Slower (must compute for each pair)
- Very accurate relevance scoring
- Better at understanding query-document relationship
- Used for re-ranking top candidates

## Performance Impact

### Latency

| Configuration | Latency | Quality |
|--------------|---------|---------|
| Hybrid only | ~80ms | ★★★★☆ |
| + Cross-encoder (L-6) | ~150ms | ★★★★★ |
| + Cross-encoder (L-12) | ~250ms | ★★★★★+ |

### Memory Usage

First query will download the model:
- L-6 model: ~82MB download
- L-12 model: ~133MB download
- Models cached in `~/.cache/huggingface/`

## Monitoring

### Log Messages

When enabled, you'll see:
```
✓ Initialized CrossEncoderReranker with cross-encoder/ms-marco-MiniLM-L-6-v2
✓ Cross-encoder reranking enabled with cross-encoder/ms-marco-MiniLM-L-6-v2
Applying cross-encoder reranking...
Reranked 15 documents, score range: -8.234 to 5.678
```

### Fallback Behavior

If reranker fails (missing dependency, model load error):
```
⚠ Failed to initialize cross-encoder reranker: [error]. Falling back to quality-based reranking.
```

System continues with heuristic reranking.

## Troubleshooting

### Issue: `ImportError: No module named 'sentence_transformers'`

**Solution:**
```bash
cd backend
uv sync --extra reranker
```

### Issue: Model download fails

**Solution:**
```bash
# Pre-download model manually
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

### Issue: High memory usage

**Solution:**
- Use smaller model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Reduce `RAG_RERANKER_TOP_K`
- Increase `RAG_NUM_CHUNKS` initial retrieval less

### Issue: Slow performance

**Solution:**
- Use faster model (L-6 instead of L-12)
- Reduce number of documents to rerank
- Consider disabling for simple queries

## Next Steps

### Phase 2: Query Expansion (Planned)
- Implement multi-query generation
- LLM-based query expansion
- Keyword extraction

### Phase 3: RAG Fusion (Planned)
- Reciprocal Rank Fusion
- Multi-strategy aggregation
- Advanced query processing

## Benchmarking

Create benchmark script:

```python
import time
from app.services.enhanced_retrieval import create_enhanced_retriever

# Test queries
queries = [
    "What are the symptoms of diabetes?",
    "Machine learning algorithms explained",
    "Climate change effects on agriculture",
]

# Test with and without reranking
for use_reranker in [False, True]:
    print(f"\nReranker: {'Enabled' if use_reranker else 'Disabled'}")
    
    retriever = create_enhanced_retriever(
        chroma_db=chroma_db,
        use_cross_encoder=use_reranker
    )
    
    total_time = 0
    for query in queries:
        start = time.time()
        docs = retriever.get_relevant_documents(query)
        elapsed = time.time() - start
        total_time += elapsed
        print(f"  {query[:40]:40s} {elapsed*1000:6.1f}ms")
    
    print(f"  Average: {total_time/len(queries)*1000:.1f}ms")
```

## References

- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [MS MARCO Cross-Encoders](https://huggingface.co/cross-encoder)
- [Advanced RAG Guide](../ADVANCED_RAG_ENHANCEMENT_GUIDE.md)

## Support

For issues or questions:
1. Check this README
2. Review test script output
3. Check application logs
4. Consult ADVANCED_RAG_ENHANCEMENT_GUIDE.md
