# TwinCheck Chunking Enhancement

## Overview

The TwinCheck document comparison functionality has been enhanced to handle large documents that would otherwise exceed context window limits or rate limits. When the diff between two documents is too large, it now automatically splits the comparison into smaller chunks and processes them individually.

## How It Works

### 1. Token Estimation

- Uses `tiktoken` library for accurate token counting
- Supports different model encodings (GPT-4, GPT-3.5, etc.)
- Falls back to character-based estimation if tiktoken fails

### 2. Chunking Logic

- Splits diff text at line boundaries to preserve diff context
- Configurable token limits (default: 150K tokens per chunk)
- Reserves tokens for prompt templates (default: 5K tokens)
- Only chunks when necessary - single documents remain unprocessed

### 3. Processing Flow

#### Single Chunk (Original Behavior)

1. Generate diff between documents
2. If diff fits in token limit, process normally
3. Generate topic analyses directly from full diff
4. Create summary from full diff

#### Multi-Chunk (New Behavior)

1. Generate diff between documents
2. If diff exceeds token limit, split into chunks
3. Process each chunk separately for each topic
4. Synthesize chunk results for each topic
5. Create summary from synthesized topic analyses

### 4. Configuration

New settings in `app/core/config.py`:

```python
# TwinCheck chunk processing settings
TWINCHECK_MAX_TOKENS_PER_CHUNK: int = 150000
TWINCHECK_PROMPT_RESERVE_TOKENS: int = 5000
```

## API Response Changes

The TwinCheck API response now includes additional processing information:

```json
{
  "results": {
    "summary": "...",
    "topic_analysis": [...],
    "interaction_id": "...",
    "processing_info": {
      "was_chunked": true,
      "chunk_count": 3,
      "estimated_tokens": 425000
    }
  }
}
```

## Benefits

1. **Handles Large Documents**: Can now process document comparisons that would previously fail due to token limits
2. **Rate Limit Resilience**: Reduces the likelihood of hitting API rate limits by processing smaller chunks
3. **Preserves Quality**: Synthesis step ensures coherent analysis across chunks
4. **Backward Compatible**: Small documents continue to use the original, faster processing path
5. **Transparent**: Users can see when chunking was used and how many chunks were processed

## Example Use Cases

- Comparing large policy documents
- Analyzing extensive technical manuals
- Reviewing comprehensive reports
- Comparing legal documents with many sections

## Dependencies

- Added `tiktoken>=0.5.0,<1.0.0` for accurate token counting

## Performance Considerations

- Chunked processing takes longer due to multiple LLM calls
- Each chunk requires a separate API call for each topic
- Synthesis step adds an additional LLM call per topic
- Memory usage scales with document size during chunking

## Logging

Enhanced logging provides visibility into the chunking process:

```
Generated diff text with 425000 estimated tokens
Split diff into 3 chunks
Processing topic: Technical Requirements
  Processing chunk 1/3 for topic: Technical Requirements
  Processing chunk 2/3 for topic: Technical Requirements
  Processing chunk 3/3 for topic: Technical Requirements
  Synthesizing 3 chunk results for topic: Technical Requirements
```
