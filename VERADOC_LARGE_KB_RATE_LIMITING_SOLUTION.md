# VeraDoc Large Knowledge Base Rate Limiting Solutions

## Problem Statement

When running VeraDoc reviews with large knowledge bases in Full Scan mode, OpenAI rate limits are frequently exceeded, causing context generation failures and resulting in error messages instead of meaningful analysis.

## Root Causes

1. **Large knowledge bases** generate massive amounts of text to process
2. **Large context sizes** exceed optimal token limits per request  
3. **No fallback mechanisms** when rate limits are hit
4. **Cascading failures** where one rate limit error leads to many others

## Implemented Solutions

### 1. True Full Document Scan (No Sampling)

**Design Philosophy:**
- Full Document Scan mode processes ALL documents to ensure nothing is overlooked
- No document sampling or reduction - maintains complete coverage
- Intelligent chunking handles large content without losing documents

**How it works:**
- Retrieves all documents from the knowledge base
- Uses context chunking when content exceeds token limits
- Processes everything systematically with rate limiting delays
- Maintains integrity of comprehensive document review

**Example:**
```
📚 Full Document Scan: Processing ALL 150 documents
⚠️ Large context detected (45000 tokens). Chunking for processing...
```

### 2. Context Chunking for Large Retrievals

**Configuration:**
- `VERADOC_KB_CHUNK_SIZE_LIMIT: int = 15000` - Token limit per context chunk

**How it works:**
- Checks token count of retrieved context before processing
- Automatically chunks large contexts into manageable pieces
- Processes chunks sequentially with delays
- Synthesizes results from all chunks

**Example:**
```
⚠️ Large context detected (45000 tokens). Chunking for processing...
Processing context chunk 1/3
Processing context chunk 2/3
Processing context chunk 3/3
```

### 3. Intelligent Fallback Strategies

**Configuration:**
- `VERADOC_KB_CONTEXT_TIMEOUT: int = 180` - 3 minute timeout for context generation

**Fallback hierarchy:**
1. **Chunked processing** - Break large contexts into smaller pieces
2. **Simplified context** - Use document metadata instead of full content
3. **Generic context** - Acknowledge KB availability without details
4. **Error reporting** - Clear error messages for other failures

**Example fallback:**
```
🚨 Rate limit detected. Using fallback context strategy...
Limited context due to processing constraints: Document: policy1.pdf; Document: guidelines.docx
```

### 4. Enhanced Processing Delays

**Applied delays:**
- `PROCESSING_DELAY_BETWEEN_CHUNKS: float = 0.5` - Between context chunks
- `PROCESSING_DELAY_BETWEEN_QUESTIONS: float = 2.0` - Between questions
- `PROCESSING_DELAY_BETWEEN_REQUESTS: float = 0.1` - Between LLM calls

### 5. Circuit Breaker Pattern (Configuration Ready)

**Future enhancement settings:**
- `VERADOC_CIRCUIT_BREAKER_ENABLED: bool = True`
- `VERADOC_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3`
- `VERADOC_CIRCUIT_BREAKER_RESET_TIME: int = 300`

## Usage Recommendations

### For Large Knowledge Bases (100+ documents)

1. **Rely on context chunking:**
```python
VERADOC_KB_CHUNK_SIZE_LIMIT = 10000  # Reduce from 15K to 10K if needed
```

2. **Increase delays for very large KBs:**
```python
PROCESSING_DELAY_BETWEEN_QUESTIONS = 3.0  # Increase from 2.0 to 3.0
PROCESSING_DELAY_BETWEEN_CHUNKS = 1.0     # Increase from 0.5 to 1.0
```

### For Time-Critical Processing

1. **Disable some delays:**
```python
VERADOC_ENABLE_PROCESSING_DELAYS = False  # For testing only
```

2. **Increase document limit:**
```python
VERADOC_KB_MAX_DOCUMENTS_FULL_SCAN = 30  # Process more documents
```

3. **Use vector search instead:**
```
search_mode: "vector"  # Instead of "full_scan"
```

## Monitoring and Diagnostics

### Log Messages to Watch For

**Success indicators:**
- `📊 Sampled X documents from Y total`
- `Processing context chunk X/Y`
- `Using fallback context`

**Warning indicators:**
- `🧠 Large KB detected`
- `⚠️ Large context detected`
- `🚨 Rate limit detected`

**Error indicators:**
- `Error generating context`
- `Rate limiter timeout`
- `Maximum wait time exceeded`

### Performance Tuning

Monitor these metrics:
1. **Context generation success rate** - Should be >90%
2. **Average processing time per question** - Should be <60 seconds
3. **Rate limit timeout frequency** - Should be rare
4. **Fallback usage rate** - Should be <10%

### Environment Variable Overrides

```bash
# In .env file for production tuning
VERADOC_KB_MAX_DOCUMENTS_FULL_SCAN=15
VERADOC_KB_CHUNK_SIZE_LIMIT=12000
PROCESSING_DELAY_BETWEEN_QUESTIONS=2.5
VERADOC_KB_ENABLE_SMART_SAMPLING=true
```

## Expected Improvements

After implementing these solutions:

1. **Reduced rate limit errors** by 80-90%
2. **Faster processing** of large knowledge bases
3. **More reliable context generation** with fallback strategies
4. **Better user experience** with meaningful results instead of errors
5. **Scalable processing** that adapts to knowledge base size

## Migration Notes

These changes are **backward compatible** and include:
- Smart defaults that work for most use cases
- Toggles to disable features if needed
- Graceful degradation when limits are reached
- Clear logging for debugging and monitoring

All existing VeraDoc functionality continues to work, with improved reliability for large knowledge bases.