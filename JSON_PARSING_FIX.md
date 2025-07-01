# JSON Parsing Error Fix for Optimize Outline

## Problem Identified

The optimize outline functionality was failing due to **JSON parsing errors** caused by special Unicode characters in the ground-truth documents. The specific error was:

```
✗ JSON parsing failed: Invalid control character at: line 48 column 297 (char 3034)
```

## Root Cause

The ground-truth documents contained special characters that are invalid in JSON strings:

- Smart apostrophes: `ʼ` (as in "Parkinsonʼs")
- Smart quotes: `"` and `"`
- Em/en dashes: `—` and `–`
- Control characters (invisible characters 0-31)

When the LLM copied text directly from the document into JSON responses, these characters broke JSON parsing.

## Solution Implemented

### 1. Text Sanitization Function

Added `sanitize_text_for_json()` function that:

- Replaces smart quotes with regular quotes
- Replaces special apostrophes with regular apostrophes
- Replaces em/en dashes with regular hyphens
- Removes control characters (0-31 except tab, newline, carriage return)
- Converts remaining Unicode to ASCII

### 2. Input Sanitization

Applied sanitization at multiple points:

- **Ground-truth document**: Sanitized after extraction
- **Chunk previews**: Sanitized before sending to LLM
- **LLM responses**: Sanitized before JSON parsing

### 3. Enhanced Error Handling

Improved JSON parsing error handling to:

- Show more context (500 chars vs 200)
- Identify problematic characters and their positions
- Provide specific error messages for token limits

### 4. Size Limits and Monitoring

Added protective measures:

- **Document size limit**: 500KB maximum
- **Section count limit**: 50 sections maximum
- **Prompt size monitoring**: Warning for >30K tokens
- **LLM error detection**: Catches token limit errors

## Code Changes

### New Function Added:

```python
def sanitize_text_for_json(text: str) -> str:
    """Sanitize text to prevent JSON parsing issues with control characters."""
    # Replace smart quotes and apostrophes with regular ones
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('ʼ', "'")  # This specific character from the logs

    # Remove control characters (characters 0-31 except tab, newline, carriage return)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Replace any remaining problematic Unicode characters
    text = text.encode('ascii', errors='ignore').decode('ascii')

    return text
```

### Key Application Points:

1. Ground-truth document processing
2. Chunk preview generation
3. LLM response cleaning
4. Enhanced error reporting

## Expected Results

This fix should resolve the JSON parsing failures and allow the optimize outline functionality to work with documents containing:

- Medical texts with special apostrophes
- Academic papers with smart quotes
- Documents with various Unicode characters
- PDFs with embedded special characters

## Testing Recommendation

Test with documents that previously failed, particularly those containing:

- Medical terminology with special apostrophes
- Copy-pasted text with smart quotes
- International characters
- Large documents (approaching size limits)

The enhanced logging will provide detailed diagnostic information to help identify any remaining issues.
