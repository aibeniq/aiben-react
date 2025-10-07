# Veradoc Full Document Scan - Citation Filtering Implementation

**Date:** October 6, 2025  
**Feature:** LLM-based relevance filtering for Full Document Scan citations

## Problem Solved

### Original Issue
When using Veradoc/Review with **Full Document Scan** mode, the ENTIRE knowledge base was being included as citations, regardless of relevance.

**Example:**
- Knowledge base: 150 documents, 500 chunks total
- User question: "Does the policy comply with coverage requirements?"
- **Before:** All 500 chunks appeared as citations (60+ MB)
- **After:** Only ~10-20 relevant chunks appear as citations (~1-2 MB)

### Why This Happened

The `FullScanRetriever` returns ALL documents from the knowledge base:
```python
class FullScanRetriever:
    def get_relevant_documents(self, query):
        all_data = self.chroma_db.get()  # Gets EVERYTHING
        return documents  # Returns ALL 500 chunks
```

The old `prefetch_knowledge_base_context` function included all retrieved chunks as citations without checking relevance:
```python
for doc in docs:  # docs = ALL 500 chunks
    source_citations.append(source)  # Added all to citations
```

## Solution Implemented

### LLM-Based Relevance Filtering

Added intelligent filtering that analyzes each chunk for relevance before including it in citations:

```python
# Detect Full Document Scan mode
is_full_scan = len(docs) > settings.RAG_NUM_CHUNKS  # More than 20 chunks = Full Scan

if is_full_scan:
    print(f"🔍 Full Document Scan detected: Filtering {len(docs)} chunks for relevance...")
    
    filtered_docs = []
    
    for doc_idx, doc in enumerate(docs):
        # Use LLM to check relevance
        relevance_check = invoke_llm(
            llm,
            settings.VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE,
            {"chunk": doc.page_content, "question": question_text},
        )
        
        # Filter based on response
        if "No relevant information found" not in relevance_check:
            print(f"✅ Chunk {doc_idx + 1} is relevant")
            filtered_docs.append(doc)
        else:
            print(f"❌ Chunk {doc_idx + 1} is not relevant - excluding")
    
    docs = filtered_docs  # Only relevant chunks proceed to citations
```

## How It Works

### 1. Detection Phase
```python
# Automatically detect Full Document Scan mode
is_full_scan = len(docs) > settings.RAG_NUM_CHUNKS

# RAG mode: retriever returns ~20 chunks (top-K)
# Full Scan: retriever returns ALL chunks (100s-1000s)
```

### 2. Filtering Phase (Only for Full Scan)
```python
for each chunk in knowledge_base:
    ├─ Ask LLM: "Is this chunk relevant to the question?"
    ├─ If LLM says "No relevant information found" → EXCLUDE
    └─ If LLM provides analysis → INCLUDE
```

### 3. Policy Context Generation
```python
# Generate policy context summary from FILTERED chunks only
question_context = invoke_llm(
    llm,
    settings.VERADOC_CONTEXT_PROMPT_TEMPLATE,
    {"context": filtered_context, "question": question_text}
)
```

### 4. Citation Storage
```python
# Only filtered chunks become citations
source_citations = []
for doc in filtered_docs:  # filtered_docs, not all_docs
    source_citations.append(source)
```

## Prompt Template

### New: VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE

```python
VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE: str = """
You are an AI assistant analyzing a policy text chunk to determine if it contains information relevant to a specific question.

TEXT CHUNK:
{chunk}

QUESTION: {question}

INSTRUCTIONS:
1. Carefully analyze the text chunk to determine if it contains information directly relevant to answering the question.
2. If the chunk contains relevant policy information, procedures, requirements, or context that would help answer the question, respond with a brief summary of the relevant information.
3. If the chunk does NOT contain information relevant to the question, respond EXACTLY with: "No relevant information found in this chunk."
4. Do not make assumptions or infer relevance that is not clearly present in the text.
5. Consider information relevant if it provides requirements, procedures, definitions, or context that would help answer the question.

ANALYSIS:
"""
```

**Key Elements:**
- Clear instructions for relevance determination
- Specific string to identify irrelevant chunks: `"No relevant information found in this chunk."`
- Guidance on what constitutes "relevant" (requirements, procedures, definitions, context)

## Comparison: Before vs After

### Before (No Filtering)

| Scenario | Chunks Retrieved | Chunks in Citations | Policy Context |
|----------|-----------------|---------------------|----------------|
| **Vector Search (RAG)** | 20 (top-K) | 20 | From all 20 |
| **Full Document Scan** | 500 (ALL) | 500 | From all 500 |

**Problem:** Full Scan citations included everything, even irrelevant chunks like table of contents, bibliography, unrelated sections.

### After (LLM Filtering)

| Scenario | Chunks Retrieved | Chunks Analyzed | Chunks in Citations | Policy Context |
|----------|-----------------|----------------|---------------------|----------------|
| **Vector Search (RAG)** | 20 (top-K) | 0 (no filtering) | 20 | From all 20 |
| **Full Document Scan** | 500 (ALL) | 500 (LLM checks each) | 10-20 (relevant only) | From 10-20 filtered |

**Improvement:** Full Scan now filters down to only relevant chunks, similar to RAG but with exhaustive search.

## Performance Impact

### Processing Time

**Full Scan with 500 chunks:**
- **Before:** ~5 seconds (no filtering, just retrieval + context generation)
- **After:** ~60-90 seconds (500 LLM calls to filter + context generation)
- **Trade-off:** Slower processing, but much better quality

### Bandwidth Impact

**Example: 500 chunk knowledge base, 10 relevant chunks:**
- **Before:** 60 MB of citations downloaded by frontend
- **After:** 1.2 MB of citations downloaded by frontend
- **Savings:** ~98% reduction in citation data

### Cost Impact

**LLM API Costs:**
- **Before:** 1-2 LLM calls per question (context generation + answer)
- **After:** 501-502 LLM calls per question (500 filtering + context + answer)
- **Cost increase:** ~500x more LLM calls for Full Scan mode

**Note:** This only affects Full Document Scan. Vector Search (RAG) mode is unchanged.

## Configuration Options

### Enable/Disable Filtering

Currently automatic based on chunk count. To control manually:

```python
# In veradoc.py, modify detection logic:

# Option 1: Always filter (even RAG mode)
is_full_scan = True

# Option 2: Never filter (old behavior)
is_full_scan = False

# Option 3: Use a setting
is_full_scan = settings.VERADOC_ENABLE_CITATION_FILTERING and len(docs) > settings.RAG_NUM_CHUNKS
```

### Adjust Filtering Threshold

```python
# Current detection
is_full_scan = len(docs) > settings.RAG_NUM_CHUNKS  # 20

# Make more aggressive (filter even smaller result sets)
is_full_scan = len(docs) > 10

# Make less aggressive (only filter very large result sets)
is_full_scan = len(docs) > 100
```

### Processing Delays

Rate limiting is already built in:
```python
if doc_idx > 0 and settings.VERADOC_ENABLE_PROCESSING_DELAYS:
    await asyncio.sleep(settings.PROCESSING_DELAY_BETWEEN_CHUNKS)
```

Default delay: `PROCESSING_DELAY_BETWEEN_CHUNKS = 0.1` (100ms between chunks)

## Comparison with Chatbot Full Scan

### Similarities
- Both use LLM to check each chunk for relevance
- Both look for "No relevant information found" string
- Both exclude irrelevant chunks from citations
- Both use similar prompt structures

### Differences

| Feature | Chatbot Full Scan | Veradoc Full Scan |
|---------|------------------|-------------------|
| **Trigger** | User selects "Full Document Scan" mode | Automatically detected (chunk count > 20) |
| **Scope** | Entire knowledge base | Entire knowledge base |
| **Analysis** | Per-chunk with dedicated analysis | Per-chunk with relevance check |
| **Synthesis** | Synthesizes all relevant analyses | Generates policy context from filtered chunks |
| **Output** | Final answer + filtered citations | Policy context + QA pair + filtered citations |

## Error Handling

### Filtering Errors
```python
except Exception as filter_error:
    print(f"Error filtering chunk {doc_idx + 1}: {filter_error}")
    # On error, include the chunk to be safe
    filtered_docs.append(doc)
```

**Strategy:** If filtering fails for a chunk, include it rather than exclude it. Better to have false positives than false negatives.

### Cancellation Handling
```python
# Check for client disconnection during filtering
if request and await request.is_disconnected():
    raise HTTPException(
        status_code=408,
        detail="Request cancelled during relevance filtering"
    )
```

## Logging Output

### Console Logs

**When filtering is triggered:**
```
Retrieved 500 documents for question: Does the policy comply...
🔍 Full Document Scan detected: Filtering 500 chunks for relevance...
Analyzing chunk 1/500 for relevance...
✅ Chunk 1 is relevant
Analyzing chunk 2/500 for relevance...
❌ Chunk 2 is not relevant - excluding from citations
...
📊 Relevance filtering: 15/500 chunks are relevant
Final context length: 12500 characters from 15 documents
```

**When filtering is NOT triggered (RAG mode):**
```
Retrieved 20 documents for question: Does the policy comply...
Final context length: 8000 characters from 20 documents
```

## Files Modified

### Backend Changes

**File:** `backend/app/api/routes/veradoc.py`

**Function:** `prefetch_knowledge_base_context()` (lines ~90-300)

**Changes:**
1. Added Full Document Scan detection
2. Added LLM-based filtering loop
3. Added delay between chunk analyses
4. Added cancellation handling during filtering
5. Modified to use `filtered_docs` instead of `docs` for citations

**File:** `backend/app/core/config.py`

**Addition:** New prompt template (after line 323)
```python
VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE: str = """..."""
```

## Testing

### Manual Test

1. **Create a Veradoc evaluation with Full Document Scan:**
   - Upload documents to knowledge base
   - Create checklist with questions
   - Run Veradoc with "Full Document Scan" search mode

2. **Check console logs:**
   ```bash
   docker-compose logs -f backend | grep -E "Full Document Scan|Filtering|✅|❌"
   ```

3. **Verify filtering occurred:**
   - Look for "🔍 Full Document Scan detected"
   - Look for "📊 Relevance filtering: X/Y chunks are relevant"
   - Verify X << Y (much fewer relevant than total)

4. **Check citations in UI:**
   - Open archived Veradoc result
   - Expand a question to see citations
   - Verify citations are relevant to the question

### Automated Test

```bash
# Test with a known knowledge base
curl -X POST http://localhost:8000/api/v1/veradoc/process \
  -H "Authorization: Bearer $TOKEN" \
  -F "kb_id=$KB_ID" \
  -F "checklist_id=$CHECKLIST_ID" \
  -F "files=@test.pdf" \
  -F "search_mode=full_scan"

# Check response size
# Before filtering: ~60 MB
# After filtering: ~2-5 MB
```

## Benefits

### For Users
- ✅ **Relevant citations only** - No more scrolling through 500 irrelevant chunks
- ✅ **Better quality** - Citations actually help answer the question
- ✅ **Faster UI** - Smaller payload = faster loading

### For System
- ✅ **Bandwidth savings** - 98% reduction in citation data
- ✅ **Better UX** - Users see what matters
- ✅ **Exhaustive search** - Still checks all documents, just filters intelligently

### Trade-offs
- ❌ **Slower processing** - ~500x more LLM calls for Full Scan
- ❌ **Higher costs** - More API calls to LLM
- ❌ **Potential false negatives** - LLM might incorrectly exclude relevant chunks

## Future Enhancements

### 1. Parallel Filtering
```python
# Current: Sequential (slow but rate-limit friendly)
for doc in docs:
    relevance_check = invoke_llm(...)

# Future: Parallel (faster but needs rate limit management)
import asyncio
tasks = [check_relevance_async(doc, question) for doc in docs]
results = await asyncio.gather(*tasks)
```

### 2. Caching
```python
# Cache relevance checks by question + chunk hash
cache_key = f"{question_hash}_{chunk_hash}"
if cache_key in relevance_cache:
    is_relevant = relevance_cache[cache_key]
else:
    is_relevant = check_with_llm(chunk, question)
    relevance_cache[cache_key] = is_relevant
```

### 3. Hybrid Approach
```python
# Use embeddings for first-pass filtering, LLM for second-pass
embedding_scores = get_embedding_similarity(chunks, question)
top_50_chunks = chunks_with_score_above_threshold(0.3)
filtered_chunks = llm_filter(top_50_chunks, question)  # Fewer LLM calls
```

### 4. User Control
```python
# Let users choose filtering aggressiveness
if user_preference == "strict":
    threshold = "respond only if highly relevant"
elif user_preference == "moderate":
    threshold = "respond if somewhat relevant"
elif user_preference == "lenient":
    threshold = "respond if minimally relevant"
```

## Conclusion

The LLM-based citation filtering for Veradoc Full Document Scan mode solves the problem of irrelevant citations flooding the UI. By intelligently analyzing each chunk for relevance, we reduce citation data by ~98% while maintaining exhaustive search coverage.

**Key takeaway:** Full Document Scan now provides the best of both worlds:
- **Exhaustive search** (checks all documents)
- **Intelligent filtering** (only includes relevant citations)

This brings Full Document Scan up to par with the chatbot's filtering quality! 🎯
