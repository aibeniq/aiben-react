# Chatbot Full Document Scan Mode - Chunking and Rate Limiting Analysis

## Overview

This document analyzes how the AIben chatbot processes documents in Full Document Scan mode, examining the chunking strategy, LLM call patterns, and rate limiting behavior based on the actual codebase.

## Document Processing Flow

### 1. Document Chunking Strategy

**Sequential Processing - One Chunk at a Time**

The chatbot processes documents using a **sequential chunking approach**, not batch processing:

```python
# From chatbot.py lines 402-430
chunks = chunk_text(
    full_text, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE
)

# Analyze each chunk for this file
file_chunk_analyses = []
file_source_citations = []

for i, chunk in enumerate(chunks):
    try:
        chunk_analysis = invoke_llm(
            llm,
            settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
            {"chunk": chunk, "question": rephrased_question},
        )
        # Process result...
    except Exception as e:
        print(f"Error analyzing chunk {i} in file {file.filename}: {e}")
        continue
```

**Key Finding**: Each chunk is sent as a **separate LLM call**, not batched together.

### 2. Chunk Size Configuration

From `config.py`:
```python
FULL_SCAN_DOCUMENT_CHUNK_SIZE: int = 100000  # 100K tokens per chunk
```

**This is the root cause of your rate limiting issues**:
- Each chunk can be up to **100,000 tokens**
- With prompt templates and question context, actual requests reach **~80K tokens**
- Your global rate limiter has a limit of **120,000 tokens per minute**
- A single chunk consumes **66% of your entire per-minute token budget**

## Rate Limiting Implementation

### 3. Global Rate Limiter Behavior

From `global_rate_limiter.py`:

```python
class GlobalOpenAIRateLimiter:
    def __init__(self, tokens_per_minute: int = 120000, requests_per_minute: int = 300):
        # Ultra-conservative limits: 120k tokens (60% of OpenAI's 200k limit)
        
    def wait_for_capacity(self, estimated_tokens: int, max_wait_time: float = 120) -> bool:
        # Maximum wait time is 120 seconds, but logs show 60s timeout
```

**Current Settings**:
- **Token limit**: 120,000 tokens/minute (60% of OpenAI's limit)
- **Max wait time**: 120 seconds (but logs show 60s timeout being used)
- **Request limit**: 300 requests/minute

### 4. LLM Call Pattern with Rate Limiting

From `llms.py`:

```python
# Each invoke_llm call goes through this process:
def invoke_llm(llm, prompt, variables=None):
    # 1. Estimate tokens
    estimated_tokens = estimate_tokens(formatted_text)
    
    # 2. Wait for capacity (60s timeout in your logs)
    if not global_rate_limiter.wait_for_capacity(estimated_tokens, max_wait_time=120):
        raise Exception("Rate limiter timeout - could not obtain capacity within 60 seconds")
    
    # 3. Make the request
    # 4. Record actual usage
```

## The Inefficiency Problem

### 5. Why Failed Requests Make Everything SLOWER

**Yes, failed requests are making your system significantly slower** for these reasons:

#### A. Token Reservation Without Release
When a request fails due to timeout:
1. **Tokens are reserved** during `can_make_request()`
2. **Request times out** after 60 seconds
3. **Tokens remain reserved** in the rate limiter
4. **Next chunk immediately tries** with the same large token count
5. **Cascading failures** occur as each chunk hits the same problem

#### B. No Backoff Between Chunks
```python
for i, chunk in enumerate(chunks):
    try:
        chunk_analysis = invoke_llm(...)  # If this fails...
    except Exception as e:
        continue  # Immediately tries next chunk!
```

**Problem**: No delay between chunk processing means failed chunks immediately compete with subsequent chunks for the same limited token capacity.

#### C. Cumulative Wait Time Explosion
From your logs:
```
19:46:50 - Chunk 1: Wait 57.46s → Success
19:47:55 - Chunk 2: Wait 52.90s → Success  
19:48:48 - Chunk 3: Wait 60s → TIMEOUT
19:49:48 - Chunk 4: Wait 60s → TIMEOUT
19:50:48 - Chunk 5: Wait 60s → TIMEOUT
```

**Total processing time**: ~11 minutes for what should be a 2-3 minute operation.

## Performance Impact Analysis

### 6. Current vs Optimal Timing

**Current Reality** (from your logs):
- 1 successful chunk = ~1 minute (wait + processing)
- 1 failed chunk = 60+ seconds of pure waiting
- Total time for 10 chunks = 8-15 minutes

**Optimal Scenario** (with proper chunking):
- Smaller chunks (20K tokens each) = ~15 second waits
- No timeouts = consistent processing
- Total time for same content = 2-3 minutes

## Root Cause Summary

1. **Chunk size too large**: 100K tokens per chunk consumes 66% of rate limit
2. **No chunk-level backoff**: Failed chunks immediately retry
3. **Rate limiter timeout too short**: 60s timeout for 80K token requests
4. **Sequential processing amplifies delays**: Each failure blocks all subsequent chunks

## Recommended Solutions

### Immediate Fix
```python
# Reduce chunk size in config.py
FULL_SCAN_DOCUMENT_CHUNK_SIZE: int = 30000  # Reduce from 100K to 30K

# Add delays between chunks in chatbot.py
import asyncio
for i, chunk in enumerate(chunks):
    if i > 0:
        await asyncio.sleep(10)  # 10 second delay between chunks
    # Process chunk...
```

### Long-term Optimization
1. **Implement chunk-level queuing** with exponential backoff
2. **Increase rate limiter timeout** to 300 seconds
3. **Add circuit breaker pattern** to pause processing during rate limit periods
4. **Consider parallel processing** with smaller chunks and intelligent scheduling

**Answer to your question**: Yes, failed requests are making your system significantly slower by creating cascading timeouts and consuming rate limit capacity without successful processing.