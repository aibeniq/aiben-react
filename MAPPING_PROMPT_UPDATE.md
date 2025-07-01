# Mapping Prompt Update - One-to-One Document Section Mapping

## Overview

Updated the mapping prompt in the `optimize_outline()` function to clarify the one-to-one mapping approach between document sections and outline sections.

## Key Changes Made

### 1. Enhanced Task Description

- Changed from generic "Map sections within this ground-truth document chunk" to specific "Map individual document sections within this ground-truth chunk to outline section descriptions using a one-to-one mapping approach"

### 2. Added Critical Understanding Section

- Explicitly states that each chunk contains SEVERAL DISTINCT SECTIONS
- Clarifies that each document section maps to EXACTLY ONE outline section
- Emphasizes document order preservation in mapping

### 3. Restructured Instructions

- Replaced "SEQUENTIAL MAPPING INSTRUCTIONS" with "ONE-TO-ONE MAPPING APPROACH"
- Provided step-by-step process:
  1. Identify Document Sections
  2. Sequential Order processing
  3. Match to Outline sections
  4. One-to-One Rule enforcement
  5. Logical Progression maintenance
  6. Content Priority matching
  7. Position Awareness

### 4. Added Concrete Example

- Included an example mapping process showing:
  - Document Section A (introduction) → Outline Section 1
  - Document Section B (methodology) → Outline Section 3
  - Document Section C (results) → Outline Section 5

### 5. Enhanced Response Format

- Updated SECTION_MAPPINGS to be more descriptive with content themes
- Maintained SECTIONS, REASONING, and CONFIDENCE fields
- Added more detailed examples in the format specification

## Benefits of Updated Prompt

1. **Clarity**: Makes it crystal clear that each document section should map to exactly one outline section
2. **Structure**: Provides a clear step-by-step approach for the LLM to follow
3. **Examples**: Concrete examples help the LLM understand the expected mapping format
4. **Consistency**: Emphasizes maintaining logical progression and document flow
5. **Precision**: More specific language about what constitutes a "section" and how to handle the mapping

## Implementation Details

- Updated in `backend/app/api/routes/reportgenie.py` in the `optimize_outline()` function
- Maintains all existing response parsing logic
- No changes needed to response processing code
- Backward compatible with existing mapping response format

## Expected Impact

- More consistent and accurate mappings between document content and outline sections
- Better preservation of document structure and logical flow
- Clearer instructions should reduce mapping errors and improve confidence scores
- Enhanced ability to handle complex documents with multiple distinct sections per chunk
