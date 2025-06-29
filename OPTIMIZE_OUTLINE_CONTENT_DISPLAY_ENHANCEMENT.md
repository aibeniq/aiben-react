# Optimize Outline Enhancement: Ground-Truth and Generated Content Display

## Overview

Enhanced the ReportGenie Optimize Outline feature to show users both the generated content and ground-truth content alongside the optimization suggestions, providing full visibility into what the AI is comparing.

## Changes Made

### Backend Changes

#### 1. Enhanced Data Model (`backend/app/models.py`)

- **Updated `OutlineSuggestion` model** to include a new field:
  ```python
  class OutlineSuggestion(SQLModel):
      original_section: str
      suggested_section: str
      reason: str
      current_output: str
      ground_truth_content: str  # NEW FIELD
      needs_revision: bool
  ```

#### 2. Enhanced API Response (`backend/app/api/routes/reportgenie.py`)

- **Updated optimize_outline endpoint** to include ground-truth content:
  ```python
  suggestions.append(
      OutlineSuggestion(
          original_section=section_description,
          suggested_section=suggested_section,
          reason=reason,
          current_output=generated_content[:1000],  # Increased from 500 to 1000 chars
          ground_truth_content=ground_truth_context[:1000],  # NEW: First 1000 chars of ground-truth
          needs_revision=needs_revision,
      )
  )
  ```

### Frontend Changes

#### 1. Enhanced UI Display (`frontend/src/components/Generate/OptimizeOutlineModal.tsx`)

- **Added comprehensive content display** showing:

  1. **Original Section Description** - The current outline section description
  2. **Suggested Section Description** - The AI's suggested improvement (if needed)
  3. **Reason** - Explanation for the suggestion
  4. **Generated Content** - Content created using the current section description (in gray box)
  5. **Ground-Truth Content** - Relevant content from the uploaded document (in blue box)

- **Visual improvements**:
  - Scrollable content boxes with max height of 150px
  - Distinct color coding: gray for generated content, blue for ground-truth
  - Better spacing and typography
  - Preserved whitespace formatting

#### 2. Temporary Type Definitions

- Added local TypeScript interfaces until client can be regenerated:
  ```typescript
  interface OutlineSuggestion {
    original_section: string
    suggested_section: string
    reason: string
    current_output: string
    ground_truth_content: string
    needs_revision: boolean
  }
  ```

#### 3. Manual API Integration

- Implemented direct fetch API call to handle the optimize-outline endpoint
- Proper error handling and authentication headers
- FormData handling for file uploads

## User Experience Improvements

### Before

Users saw only:

- Original section description
- Suggested section description
- Reason for change

### After

Users now see:

- **Original section description**
- **Suggested section description** (if revision needed)
- **Reason for change**
- **Generated content box** - What the AI actually produced with the current description
- **Ground-truth content box** - What the reference document contains for comparison

This gives users complete visibility into:

1. What content was generated using their current outline
2. What the target content looks like in the ground-truth document
3. Why the AI suggests changes
4. How the improved description should lead to better content generation

## Technical Notes

### Content Limitations

- Both generated and ground-truth content are limited to 1000 characters for display
- Content boxes are scrollable to handle longer text
- Whitespace is preserved with `whiteSpace="pre-wrap"`

### Error Handling

- TypeScript compilation errors resolved
- Proper error handling for API calls
- Fallback text for missing content

### Future Improvements

- Client type generation needs to be updated to include new fields
- Consider adding expand/collapse functionality for long content
- Potential for side-by-side comparison view
- Option to highlight differences between generated and ground-truth content

## Testing

- ✅ Backend compiles without errors
- ✅ Frontend TypeScript compilation successful
- ✅ Models updated correctly
- ✅ API endpoint enhanced with new data
- ✅ UI displays new content sections properly

The enhancement provides users with complete transparency into the optimization process, allowing them to make informed decisions about applying the suggested improvements.
