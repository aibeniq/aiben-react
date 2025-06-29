# Optimize Outline Feature Implementation Summary

## Overview

Successfully implemented the "Optimize Outline" feature for the Generate/ReportGenie functionality, similar to the existing "Optimize Checklist" modal in Review/VeraDoc. This feature allows users to upload a ground-truth (good) report, and the system generates a report using the current knowledge base and outline, compares outputs to the ground-truth, and suggests improved section descriptions for the outline.

## Backend Changes

### 1. Models (backend/app/models.py)

Added new models for outline optimization:

- `OptimizeOutlineRequest`: Request model with knowledge_base_id, outline_id, sections, and custom_instructions
- `OutlineSuggestion`: Individual suggestion with original_section, suggested_section, reason, current_output, and needs_revision flag
- `OptimizedOutlineResponse`: Response model with original_sections, suggestions, optimized_sections, and analysis_summary

### 2. Prompt Template (backend/app/core/config.py)

Added `REPORTGENIE_OPTIMIZE_OUTLINE_PROMPT_TEMPLATE` for LLM-powered outline optimization:

- Compares generated content to ground-truth content
- Identifies gaps and deficiencies
- Suggests improved section descriptions
- Provides detailed analysis and reasoning

### 3. API Endpoint (backend/app/api/routes/reportgenie.py)

Implemented `/optimize-outline` endpoint:

- Accepts file upload (ground-truth document) and form data
- Supports PDF, DOCX, DOC, and TXT files
- Uses same infrastructure as report generation (ChromaDB, embeddings, LLM)
- Generates content for each section using current outline
- Compares generated content to ground-truth using retrieval
- Returns optimization suggestions with detailed analysis
- Includes proper error handling and client disconnect monitoring

### 4. Utilities

Added `extract_text_from_file` function to reportgenie.py for handling various file formats.

## Frontend Changes

### 1. Types and SDK (frontend/src/client/)

Updated types.gen.ts and sdk.gen.ts:

- Added `OptimizeOutlineRequest`, `OutlineSuggestion`, `OptimizedOutlineResponse` types
- Added `Body_reportgenie_optimize_outline` for file upload
- Added `ReportgenieOptimizeOutlineData` and `ReportgenieOptimizeOutlineResponse` endpoint types
- Added `optimizeOutline` method to ReportgenieService

### 2. Component Updates

**OutlineModal (frontend/src/components/Generate/OutlineModal.tsx):**

- Added `selectedKnowledgeBase` prop to access knowledge base information
- Added "Optimize" button next to existing "Generate Outline" button
- Integrated OptimizeOutlineModal with proper state management
- Added validation for optimize functionality (requires KB, saved outline, and sections)

**OutlineTable (frontend/src/components/Generate/OutlineTable.tsx):**

- Added `selectedKnowledgeBase` prop and passed it through to OutlineModal
- Updated component interface and function signature

**Generate Page (frontend/src/routes/\_layout/generate.tsx):**

- Updated OutlineTable usage to pass `selectedKnowledgeBase` prop

### 3. New Component: OptimizeOutlineModal

Created `frontend/src/components/Generate/OptimizeOutlineModal.tsx`:

- File upload interface for ground-truth documents
- Custom instructions field (optional)
- Progress indication during optimization
- Results display showing:
  - Original vs suggested sections
  - Revision recommendations with reasons
  - Visual indicators for sections needing optimization
- Apply optimizations functionality
- Comprehensive error handling

## Key Features

### 1. File Upload Support

- Supports PDF, DOCX, DOC, and TXT files
- File size display and validation
- Clean file selection interface

### 2. Intelligent Analysis

- Generates content using current outline and knowledge base
- Uses retrieval to find relevant ground-truth content for each section
- LLM-powered comparison and suggestion generation
- Detailed reasoning for each suggestion

### 3. User Experience

- Clear visual indicators for sections needing optimization
- "Good as is" vs "Needs Revision" categorization
- One-click application of all optimizations
- Proper validation and error messages
- Loading states and progress indication

### 4. Integration

- Seamlessly integrated into existing outline editing workflow
- Maintains consistency with existing "Optimize Checklist" feature
- Respects user permissions and knowledge base access

## Usage Flow

1. User selects a knowledge base and creates/edits an outline
2. User clicks "Optimize" button in the outline editor
3. System validates prerequisites (KB selected, outline saved, sections exist)
4. User uploads a ground-truth document and optionally adds custom instructions
5. System generates content for each section using current outline
6. System compares generated content to ground-truth document
7. LLM analyzes differences and suggests improvements
8. User reviews suggestions and applies optimizations
9. Optimized outline sections are updated in the editor

## Error Handling

### Backend

- File processing errors
- LLM invocation failures
- Knowledge base access validation
- Client disconnect monitoring
- Comprehensive error messages

### Frontend

- File selection validation
- Permission checking
- Network error handling
- User-friendly error messages
- Loading state management

## Testing Recommendations

1. **End-to-End Testing:**

   - Upload various document types (PDF, DOCX, TXT)
   - Test with different knowledge bases and outline types
   - Verify optimization suggestions quality

2. **Error Scenarios:**

   - Invalid file formats
   - Network interruptions
   - Permission issues
   - Empty or invalid outlines

3. **User Experience:**
   - Button enablement/disablement logic
   - Modal navigation flow
   - Results display and interaction

## Future Enhancements

1. **Batch Processing:** Support multiple ground-truth documents
2. **Comparison Metrics:** Quantitative similarity scores
3. **Version History:** Track optimization iterations
4. **Templates:** Save and reuse optimization templates
5. **Advanced Analytics:** Success metrics and improvement tracking

The implementation is complete and ready for testing. The feature maintains consistency with existing patterns while providing powerful outline optimization capabilities.
