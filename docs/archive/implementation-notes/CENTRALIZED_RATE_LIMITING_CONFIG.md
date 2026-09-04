# Centralized Rate Limiting and Processing Configuration

## Overview

This document describes the centralized rate limiting and processing delay configuration implemented to prevent OpenAI API rate limit issues across all AIben services.

## Configuration Location

All rate limiting settings are centralized in `/backend/app/core/config.py` under the "CENTRALIZED RATE LIMITING CONFIGURATION" section.

## Global Rate Limiting Settings

### OpenAI API Limits
- **`OPENAI_TOKENS_PER_MINUTE`**: 180,000 tokens/minute (90% of typical 200k limit)
- **`OPENAI_REQUESTS_PER_MINUTE`**: 500 requests/minute (conservative but practical)
- **`OPENAI_RATE_LIMIT_MAX_WAIT`**: 300 seconds (5 minutes maximum wait for capacity)

### Processing Delays
- **`PROCESSING_DELAY_BETWEEN_CHUNKS`**: 0.5 seconds (delay between processing chunks)
- **`PROCESSING_DELAY_BETWEEN_QUESTIONS`**: 2.0 seconds (delay between questions in VeraDoc)
- **`PROCESSING_DELAY_BETWEEN_DOCUMENTS`**: 1.0 seconds (delay between document processing)
- **`PROCESSING_DELAY_BETWEEN_REQUESTS`**: 0.1 seconds (minimum delay between any LLM requests)

### Chunk Processing Settings
- **`CHUNK_PROCESSING_PROMPT_RESERVE_SMALL`**: 5,000 tokens (reserve for smaller operations)
- **`CHUNK_PROCESSING_PROMPT_RESERVE_LARGE`**: 20,000 tokens (reserve for large operations)
- **`CHUNK_PROCESSING_SIZE_THRESHOLD`**: 50,000 tokens (threshold for small vs large reserve)

### Service-Specific Toggles
- **`CHATBOT_ENABLE_CHUNK_DELAYS`**: True (enable delays between chatbot chunks)
- **`VERADOC_ENABLE_PROCESSING_DELAYS`**: True (enable delays in VeraDoc processing)
- **`TWINCHECK_ENABLE_PROCESSING_DELAYS`**: True (enable delays in TwinCheck processing)
- **`REPORTGENIE_ENABLE_PROCESSING_DELAYS`**: True (enable delays in ReportGenie processing)

## Services Using Centralized Configuration

### 1. Global Rate Limiter (`global_rate_limiter.py`)
- Uses `OPENAI_TOKENS_PER_MINUTE` and `OPENAI_REQUESTS_PER_MINUTE`
- Uses `OPENAI_RATE_LIMIT_MAX_WAIT` for timeout settings

### 2. LLM Service (`llms.py`)
- Uses `OPENAI_RATE_LIMIT_MAX_WAIT` for all OpenAI API calls
- Applies centralized timeout to both retry utils and direct invocations

### 3. Text Processing (`text_processing.py`)
- Uses `CHUNK_PROCESSING_SIZE_THRESHOLD` to determine reserve size
- Uses `CHUNK_PROCESSING_PROMPT_RESERVE_SMALL/LARGE` for token reserves

### 4. Chatbot (`chatbot.py`)
- Uses `PROCESSING_DELAY_BETWEEN_CHUNKS` for chunk processing delays
- Controlled by `CHATBOT_ENABLE_CHUNK_DELAYS` toggle
- Applies to both document upload and knowledge base processing

### 5. VeraDoc (`veradoc.py`)
- Uses `PROCESSING_DELAY_BETWEEN_QUESTIONS` for question prefetch delays
- Uses `PROCESSING_DELAY_BETWEEN_REQUESTS` for question processing delays
- Controlled by `VERADOC_ENABLE_PROCESSING_DELAYS` toggle

### 6. TwinCheck (`twincheck.py`)
- Uses `PROCESSING_DELAY_BETWEEN_CHUNKS` for chunk processing in generate topics
- Uses `PROCESSING_DELAY_BETWEEN_REQUESTS` for topic comparison processing
- Controlled by `TWINCHECK_ENABLE_PROCESSING_DELAYS` toggle

### 7. ReportGenie (`reportgenie.py`)
- Uses `PROCESSING_DELAY_BETWEEN_CHUNKS` for outline generation chunk processing
- Uses `PROCESSING_DELAY_BETWEEN_REQUESTS` for section generation
- Uses `PROCESSING_DELAY_BETWEEN_CHUNKS` for report generation chunk processing
- Controlled by `REPORTGENIE_ENABLE_PROCESSING_DELAYS` toggle

### 8. FormConnect (`formconnect.py`)
- Uses `PROCESSING_DELAY_BETWEEN_DOCUMENTS` for file processing delays
- Applies to both document processing and reference file processing
- Uses centralized rate limiting for field generation

## Benefits of Centralized Configuration

1. **Single Source of Truth**: All rate limiting settings in one place
2. **Easy Adjustment**: Change settings without modifying multiple files
3. **Consistent Behavior**: All services use the same rate limiting logic
4. **Environment-Specific Settings**: Can be overridden via environment variables
5. **Service Toggles**: Can disable delays for specific services if needed

## Usage Examples

### Adjusting Rate Limits
```python
# In config.py - increase token limit for higher-tier accounts
OPENAI_TOKENS_PER_MINUTE: int = 300000  # Increase from 180k to 300k

# Decrease delays for faster processing
PROCESSING_DELAY_BETWEEN_CHUNKS: float = 0.1  # Reduce from 0.5s to 0.1s
```

### Disabling Delays for Testing
```python
# Disable all delays for faster testing
CHATBOT_ENABLE_CHUNK_DELAYS: bool = False
VERADOC_ENABLE_PROCESSING_DELAYS: bool = False
```

### Environment Variable Overrides
```bash
# Override in .env file
OPENAI_TOKENS_PER_MINUTE=250000
PROCESSING_DELAY_BETWEEN_CHUNKS=0.2
```

## Monitoring and Tuning

### Key Metrics to Watch
1. **Rate limit timeout errors**: Should be eliminated with proper settings
2. **Processing time**: Should be reasonable with optimized delays
3. **Success rate**: Should be near 100% for normal usage

### Tuning Guidelines
- **High rate limit errors**: Increase delays or decrease token limits
- **Slow processing**: Decrease delays (but monitor error rates)
- **Specific service issues**: Use service-specific toggles to disable delays

## Migration Notes

All previous hardcoded rate limiting values have been replaced with references to these centralized settings. This includes:

- VeraDoc-specific delays → `PROCESSING_DELAY_BETWEEN_QUESTIONS`
- Chatbot hardcoded 2-second delays → `PROCESSING_DELAY_BETWEEN_CHUNKS`
- Global rate limiter hardcoded 180k limit → `OPENAI_TOKENS_PER_MINUTE`
- LLM service hardcoded 300s timeout → `OPENAI_RATE_LIMIT_MAX_WAIT`

## Future Enhancements

Potential additions to the centralized configuration:
1. **Service-specific token limits** (different limits per service)
2. **Dynamic rate limiting** (adjust based on current usage)
3. **Circuit breaker patterns** (pause processing during extended rate limits)
4. **Usage analytics** (track and optimize based on actual usage patterns)