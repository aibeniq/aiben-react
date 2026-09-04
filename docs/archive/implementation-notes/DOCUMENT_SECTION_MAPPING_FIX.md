# Document Section Mapping Fix

## Problem Identified

The previous mapping approach had a fundamental flaw: it was treating document chunks (arbitrary divisions for LLM processing) as the units to map to outline sections, rather than identifying the actual discrete document sections within those chunks.

### Issue Example:

```
Document Chunk (for LLM processing):
"EMG- and Movement-Based Monitoring of Parkinsonʼs Disease in Clinical Care
Invitation to Participate in the Study
You are invited to participate in a study investigating the use of a method based on the
measurement and analysis of muscle activity and movement for assessing the motor symptoms
and treatment of Parkinsonʼs disease. This information sheet describes the study and your..."

Previous Approach (INCORRECT):
- Mapped entire chunk → Outline Section X

Correct Approach (FIXED):
- Title: "EMG- and Movement-Based Monitoring..." → Outline Section 1
- Header: "Invitation to Participate..." → Outline Section 2
- Paragraph: "You are invited to participate..." → Outline Section 2
- Paragraph: "This information sheet describes..." → Outline Section 3
```

## Solution Implemented

### 1. Updated Mapping Prompt

- **Before**: Asked LLM to map document chunks to outline sections
- **After**: Asks LLM to identify individual document sections within each chunk and map each one separately

### 2. Enhanced Section Identification

The new prompt specifically instructs the LLM to:

- Identify discrete document sections (headers, paragraphs, content blocks)
- Distinguish between processing chunks and actual document structure
- Map each identified section to exactly one outline section description

### 3. Improved Response Format

New response format includes:

- `DOCUMENT_SECTIONS_IDENTIFIED`: Lists each discrete section found in the chunk
- `SECTION_MAPPINGS`: Shows the one-to-one mapping for each identified section
- `SECTIONS`: Outline section numbers that were mapped to
- `REASONING`: Explains the identification and mapping logic
- `CONFIDENCE`: Assessment of mapping quality

### 4. Enhanced Tracking and Debugging

- Added tracking of identified document sections in metadata
- Improved logging to show what sections were identified within each chunk
- Better context for future chunks based on previous section identification

## Key Benefits

1. **Accurate Mapping**: Now maps actual document structure instead of arbitrary processing chunks
2. **Granular Analysis**: Can identify and map individual headers, paragraphs, and content blocks
3. **Better Alignment**: Document sections align properly with outline section descriptions
4. **Improved Debugging**: Clear visibility into what sections were identified and how they were mapped
5. **Sequential Consistency**: Maintains document flow while respecting actual content boundaries

## Example Workflow

1. **Chunk Processing**: Document divided into large chunks for LLM processing
2. **Section Identification**: Within each chunk, identify:
   - Headers and titles
   - Topic changes
   - Paragraph breaks
   - Distinct content blocks
3. **Individual Mapping**: Each identified section mapped to one outline section
4. **Tracking**: Record what was identified and mapped for context in subsequent chunks
5. **Aggregation**: Build complete mapping of document structure to outline

## Technical Changes

### Files Modified:

- `backend/app/api/routes/reportgenie.py`: Updated mapping prompt and response parsing

### Key Code Changes:

1. **Mapping Prompt**: Completely rewritten to focus on section identification within chunks
2. **Response Parsing**: Added parsing for `DOCUMENT_SECTIONS_IDENTIFIED` field
3. **Logging**: Enhanced to show identified sections and mapping decisions
4. **Metadata**: Extended to track document section identification for debugging

This fix ensures that the optimize outline feature correctly analyzes the actual structure and content organization of reference documents, leading to much more accurate optimization suggestions.
