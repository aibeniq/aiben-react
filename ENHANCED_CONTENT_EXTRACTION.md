# Enhanced Content Extraction for Optimize Outline

## Overview

The optimize outline feature has been enhanced to extract **actual text content** from the ground-truth document instead of just descriptions. This provides much more precise comparison and optimization suggestions.

## Key Changes

### 1. Updated LLM Mapping Prompt

The mapping prompt now instructs the LLM to:

- Identify discrete sections within each document chunk
- **Extract the actual text content** for each section (not just a description)
- Map each section to the appropriate outline section

**New Response Format:**

```json
{
  "mappings": [
    {
      "section_content": "the actual text content extracted from the document section",
      "outline_section": 1
    },
    {
      "section_content": "the actual text content from another document section",
      "outline_section": 2
    }
  ]
}
```

### 2. Enhanced Data Collection

Two data structures now track mapping results:

- `section_to_chunks`: Maps outline sections to document chunks (existing)
- `section_to_content`: **NEW** - Maps outline sections to actual extracted text content

### 3. Improved Content Analysis

The section analysis now:

1. **Prioritizes actual extracted content** over full chunks
2. Falls back to chunk-level content if no specific content was extracted
3. Provides detailed logging of content extraction results

### 4. Enhanced Logging and Debugging

New logging includes:

- Character count of extracted content after each chunk
- Content extraction summary showing sections with mapped content
- Detailed mapping summaries showing chunk → content extraction ratios

## Example Output

```
✓ JSON parsing successful. Found 3 document sections mapping to 2 outline sections
✓ Extracted 1247 characters of actual section content
Mapped content to section: Introduction and Background... Mapped 1 chunks → 1 extracted sections (total: 45,231 chars → 423 chars)
Content extraction summary: 8 total sections extracted, 6/10 outline sections have mapped content
```

## Benefits

1. **More Precise Comparison**: Instead of comparing generated content to entire chunks, the system now compares to the specific, relevant text from the document.

2. **Better Optimization Suggestions**: The LLM can provide more targeted suggestions when it has access to the exact text that should be covered.

3. **Cleaner Analysis**: Reduces noise from irrelevant content in large chunks, focusing only on the text that's actually relevant to each outline section.

4. **Improved Reliability**: The JSON-only response format with robust parsing handles edge cases better than previous approaches.

## Technical Implementation

The key changes are in `backend/app/api/routes/reportgenie.py`:

1. **Prompt Update**: Changed from requesting "section_text" (description) to "section_content" (actual text)
2. **Response Parsing**: Updated to extract and store `section_content`
3. **Content Usage**: Modified section analysis to use extracted content preferentially
4. **Fallback Logic**: Maintains chunk-level fallback for cases where content extraction fails

This enhancement significantly improves the quality and precision of the optimize outline feature while maintaining backward compatibility and robust error handling.
