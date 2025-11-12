# Document Query Token Limit Fix Summary

## Problem
The chatbot document query feature was failing with:
```
BadRequestError: Requested 304603 tokens, max 300000 tokens per request
```

## Root Cause
The chatbot.py `query_document` function was directly calling `Chroma.from_documents()` without respecting the `EMBEDDING_MAX_TOKENS_PER_REQUEST` setting (200,000 tokens) from config.py. This caused all document chunks to be sent to OpenAI's embedding API in a single request, exceeding the 300,000 token limit.

## Solution
Modified `/backend/app/api/routes/chatbot.py` to:

1. **Import the existing chunking function**: Added import for `chunk_documents_for_embedding` from `app.api.routes.knowledgebases`

2. **Apply token-aware chunking**: Before creating embeddings, split documents into batches that respect the `EMBEDDING_MAX_TOKENS_PER_REQUEST` limit

3. **Process embeddings in batches**: Create the vector store by processing document chunks in batches, avoiding token limit violations

## Changes Made

### Import Addition (line ~23):
```python
from app.api.routes.knowledgebases import chunk_documents_for_embedding
```

### Logic Replacement (lines ~1332-1348):
**Before:**
```python
vector_store = Chroma.from_documents(
    documents=chunks, embedding=embeddings, persist_directory=vector_dir
)
```

**After:**
```python
# Chunk documents for embedding to respect token limits
document_chunks = chunk_documents_for_embedding(
    chunks, max_tokens_per_chunk=settings.EMBEDDING_MAX_TOKENS_PER_REQUEST
)

# Create vector store by processing chunks in batches to avoid token limits
vector_store = None
for i, chunk_batch in enumerate(document_chunks):
    print(f"Processing embedding batch {i+1}/{len(document_chunks)} with {len(chunk_batch)} documents")
    if vector_store is None:
        # Create the initial vector store
        vector_store = Chroma.from_documents(
            documents=chunk_batch, embedding=embeddings, persist_directory=vector_dir
        )
    else:
        # Add to existing vector store
        vector_store.add_documents(documents=chunk_batch)
```

## Result
- Document queries now respect the 200,000 token limit per embedding request
- Large documents are processed in multiple batches instead of failing
- Maintains the same functionality while preventing token limit errors
- Uses the same proven chunking logic already used in knowledge base creation

## Files Modified
- `/backend/app/api/routes/chatbot.py`

The fix ensures consistency between knowledge base creation and document query processes, both now using the same token-aware chunking approach.