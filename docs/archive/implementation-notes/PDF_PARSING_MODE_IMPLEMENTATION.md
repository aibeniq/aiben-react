# PDF Parsing Mode Implementation Summary

## Overview

Successfully implemented the `PDF_PARSING_MODE` configuration setting to provide flexible control over PDF parsing behavior throughout the application. This replaces the previous hardcoded boolean approach with a more sophisticated mode-based system.

## Changes Made

### 1. Configuration (`backend/app/core/config.py`)

- **Removed**: `USE_ENHANCED_PDF_PARSING` boolean setting (deprecated)
- **Updated**: `PDF_PARSING_MODE` string setting with improved documentation
  - Default changed from `"basic"` to `"auto"` for better performance
  - Supports three modes: `"auto"`, `"enhanced"`, `"basic"`

```python
PDF_PARSING_MODE: str = Field(
    default="auto",
    description="PDF parsing mode: 'auto' (detect tables automatically), 'enhanced' (always use PyMuPDF4LLM), 'basic' (always use pypdf)"
)
```

### 2. Core PDF Utils (`backend/app/services/pdf_utils.py`)

Updated functions to use string-based mode parameter:

- **`load_pdf_with_pypdf()`**: Changed `use_enhanced_parsing: bool` → `parsing_mode: str`

  - `"auto"`: Detects tables first, uses enhanced parsing only if tables found (best performance)
  - `"enhanced"`: Always uses PyMuPDF4LLM if available (best quality)
  - `"basic"`: Always uses pypdf (fastest, may miss table structure)

- **`extract_text_from_pdf_bytes()`**: Changed `use_enhanced_parsing: bool` → `parsing_mode: str`
  - Same mode logic as above
  - Includes graceful fallback when PyMuPDF4LLM unavailable

### 3. Document Utils (`backend/app/services/document_utils.py`)

Updated unified extraction functions:

- **`extract_text_from_file_unified()`**:
  - Parameter: `pdf_parsing_mode: str = None`
  - Automatically uses `settings.PDF_PARSING_MODE` if not specified
- **`extract_documents_from_file_unified()`**:
  - Parameter: `pdf_parsing_mode: str = None`
  - Automatically uses `settings.PDF_PARSING_MODE` if not specified

### 4. API Endpoints

Updated all API routes to use the new settings:

#### Knowledge Bases (`backend/app/api/routes/knowledgebases.py`)

- `load_uploaded_file()`: Now uses `settings.PDF_PARSING_MODE`
- Direct processing: Removed hardcoded `use_enhanced_pdf_parsing=True`

#### Chatbot (`backend/app/api/routes/chatbot.py`)

- File upload processing: Now uses `settings.PDF_PARSING_MODE` by default

#### VeraDoc (`backend/app/api/routes/veradoc.py`)

- `extract_text_from_file()`: Now uses `settings.PDF_PARSING_MODE` by default

### 5. Tests (`backend/test_pymupdf4llm_integration.py`)

Updated test cases to use new mode parameter:

- `parsing_mode="enhanced"` for testing enhanced parsing
- `parsing_mode="basic"` for testing basic parsing
- `parsing_mode="auto"` for testing auto-detection

### 6. Documentation (`PYMUPDF4LLM_INTEGRATION_GUIDE.md`)

- Updated configuration examples
- Added detailed mode descriptions
- Updated usage examples with environment variable configuration
- Added examples for per-file mode overrides

## Usage

### Global Configuration (Recommended)

Set in your `.env` file:

```bash
# Auto mode (default) - best balance of performance and quality
PDF_PARSING_MODE=auto

# Enhanced mode - highest quality, slower
PDF_PARSING_MODE=enhanced

# Basic mode - fastest, may miss table structure
PDF_PARSING_MODE=basic
```

### Per-File Override

Override the global setting for specific files:

```python
# Force enhanced parsing for a specific file
documents = extract_documents_from_file_unified(
    file_content, filename, pdf_parsing_mode="enhanced"
)

# Force basic parsing
text = extract_text_from_file_unified(
    file_content, filename, pdf_parsing_mode="basic"
)
```

## Mode Comparison

| Mode         | Description                                        | When to Use                      | Performance | Quality |
| ------------ | -------------------------------------------------- | -------------------------------- | ----------- | ------- |
| **auto**     | Detects tables first, uses enhanced only if needed | Default, best for most cases     | Fast        | High    |
| **enhanced** | Always uses PyMuPDF4LLM                            | PDFs with complex tables/forms   | Slower      | Highest |
| **basic**    | Always uses pypdf                                  | Simple text PDFs, speed critical | Fastest     | Good    |

## Benefits

1. **Flexibility**: Can configure PDF parsing behavior globally or per-file
2. **Performance**: Auto mode provides intelligent table detection
3. **Control**: Three modes give fine-grained control over quality vs. speed tradeoff
4. **Backward Compatibility**: Existing code continues to work with sensible defaults
5. **Environment-Aware**: Can configure different modes for different deployments

## Migration Notes

- The old `USE_ENHANCED_PDF_PARSING` boolean setting has been removed
- All hardcoded `use_enhanced_pdf_parsing=True` calls have been replaced
- Default mode is `"auto"` which provides intelligent behavior
- No changes needed to existing `.env` files if default behavior is acceptable

## Testing

All existing tests have been updated and pass with the new implementation:

- Table detection tests
- Enhanced parsing tests
- Basic parsing tests
- Fallback behavior tests
- Integration tests

## Next Steps

To take advantage of this feature:

1. Set `PDF_PARSING_MODE` in your `.env` file based on your needs
2. Monitor PDF processing performance
3. Adjust mode based on your document types and performance requirements
