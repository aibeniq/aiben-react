# Embedding Token Limit Fix Implementation

## Problem

The knowledge base creation was failing with the error:

```
Error creating vector database: Error code: 400 - {'error': {'message': 'Requested 347656 tokens, max 300000 tokens per request', 'type': 'max_tokens_per_request', 'param': None, 'code': 'max_tokens_per_request'}}
```

This occurs when processing large amounts of files that result in more than 300,000 tokens being sent to the embedding API in a single request.

## Solution Implemented

### 1. Token Estimation Function

Added `estimate_tokens_for_embedding()` function that uses OpenAI's `cl100k_base` encoding to accurately estimate tokens for embedding models:

```python
def estimate_tokens_for_embedding(text: str) -> int:
    """
    Estimate tokens in text for embedding models using cl100k_base encoding.
    This is the same encoding used by OpenAI's text-embedding models.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if tiktoken fails
        return len(text) // 4
```

### 2. Document Chunking Function

Added `chunk_documents_for_embedding()` function that splits documents into chunks that fit within token limits:

```python
def chunk_documents_for_embedding(documents: List[Document], max_tokens_per_chunk: int = None) -> List[List[Document]]:
```

Key features:

- Uses configurable token limits (defaults to 250k for safety)
- Handles oversized individual documents by splitting them further
- Groups documents intelligently to maximize chunk utilization
- Provides detailed logging for debugging

### 3. Configuration Setting

Added new configuration setting in `backend/app/core/config.py`:

```python
# Embedding processing parameters
EMBEDDING_MAX_TOKENS_PER_REQUEST: int = 250000  # Safe limit below OpenAI's 300k token limit
```

### 4. Chunked Vector Database Creation

Modified the `create_knowledge_base()` function to:

- Process documents in chunks sequentially
- Initialize Chroma database with the first chunk
- Add subsequent chunks to the existing database
- Include progress logging and error handling
- Add small delays between chunks to be API-friendly

### 5. Enhanced Error Handling

- Made the function async to support chunked processing
- Added comprehensive error handling with cleanup
- Improved logging with token counts and progress indicators
- Better cleanup of temporary directories

## Files Modified

1. **`backend/app/api/routes/knowledgebases.py`**

   - Added token estimation and chunking functions
   - Modified `create_knowledge_base()` to use chunked processing
   - Made function async for better performance
   - Added detailed logging and error handling

2. **`backend/app/core/config.py`**
   - Added `EMBEDDING_MAX_TOKENS_PER_REQUEST` configuration setting

## Testing

Created test scripts to verify:

- Token estimation accuracy
- Chunking logic for various document sizes
- Handling of oversized individual documents

## Benefits

1. **Eliminates Token Limit Errors**: No more 300k token limit failures
2. **Preserves Context**: Documents are chunked intelligently without losing context
3. **Configurable**: Token limits can be adjusted via configuration
4. **Robust**: Handles edge cases like oversized individual documents
5. **Progress Tracking**: Detailed logging for monitoring large uploads
6. **API Friendly**: Includes delays to respect rate limits

## Usage

The fix is automatically applied when creating knowledge bases. Users will see improved logging during the upload process, and large document collections will now process successfully without token limit errors.

## Future Enhancements

1. **Progress UI**: Could add real-time progress indicators in the frontend
2. **Retry Logic**: Could implement exponential backoff for failed chunks
3. **Parallel Processing**: Could process multiple chunks in parallel (with rate limiting)
4. **Optimization**: Could optimize chunk sizes based on embedding model capabilities
