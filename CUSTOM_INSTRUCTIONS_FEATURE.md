# Custom Instructions Feature Implementation

## Overview

This document describes the implementation of the Custom Instructions feature for the VeraDoc Review functionality. This feature allows users to provide additional context or instructions that will be appended to each checklist question during document evaluation.

## Feature Description

The Custom Instructions feature adds a text box to the Review UI where users can enter optional instructions that will be considered when answering individual checklist questions. These instructions are appended to the prompt template when using the `VERADOC_QA_PROMPT_TEMPLATE`.

## Implementation Details

### Backend Changes

1. **Model Updates**: The `VeraDocRequest` base model already included the `custom_instructions` field:

   ```python
   class VeraDocRequest(SQLModel):
       questions: str
       custom_instructions: Optional[str] = Field(default=None, max_length=2000)
   ```

2. **Prompt Template**: The `VERADOC_QA_PROMPT_TEMPLATE` already includes a `{custom_instructions_section}` placeholder for injecting custom instructions.

3. **API Endpoint**: The `/process-rag` endpoint already supports `custom_instructions` as a query parameter through the `RagChecklistRequest` model inheritance.

### Frontend Changes

1. **UI Component**: Added a `Textarea` component in the Review UI (`frontend/src/routes/_layout/review.tsx`):

   - Positioned after the file upload component
   - Includes character count (max 2000 characters)
   - Provides clear placeholder text explaining the feature
   - Uses responsive design and proper styling

2. **State Management**: Added `customInstructions` state variable to track user input.

3. **API Integration**: Updated API calls to include `custom_instructions` parameter:

   - Modified both single file processing and batch processing functions
   - Updated the mutation function type definition

4. **Type Updates**: Updated frontend client types to include `customInstructions` in:
   - `VeradocProcessRagChecklistData` type definition
   - SDK request configuration to pass it as a query parameter

## User Experience

### UI Layout

- The custom instructions text box appears after the file upload section
- Clear labeling: "Custom Instructions (Optional)"
- Helpful placeholder text explaining the feature
- Character counter showing usage out of 2000 maximum
- Visual feedback with hover and focus states

### Functionality

- Instructions are sent with each review request
- If no instructions are provided, the field is omitted from the API call
- Instructions are trimmed of whitespace before sending
- Works with both single file and batch processing modes

## Usage Example

1. User selects a knowledge base and checklist
2. User uploads document(s) for review
3. User enters optional custom instructions such as:
   - "Consider this is a pediatric study when evaluating age-related requirements"
   - "This protocol is for a low-risk intervention, apply appropriate risk assessment criteria"
   - "Focus on international regulatory requirements rather than US-specific guidelines"
4. User clicks "Review" to process the documents with the custom instructions applied

## Technical Notes

### Parameter Passing

- Custom instructions are passed as a query parameter (`custom_instructions`) to the backend
- The backend automatically includes them in the prompt template if provided
- Empty or whitespace-only instructions are converted to `undefined` to avoid sending unnecessary parameters

### Character Limits

- Maximum 2000 characters to prevent overly long prompts
- Real-time character counter provides immediate feedback
- Backend validation ensures compliance with the limit

### Backward Compatibility

- The feature is fully optional and backward compatible
- Existing API calls without custom instructions continue to work normally
- The UI gracefully handles the absence of custom instructions

## Files Modified

### Frontend

- `frontend/src/routes/_layout/review.tsx`: Main UI implementation
- `frontend/src/client/types.gen.ts`: Type definitions
- `frontend/src/client/sdk.gen.ts`: API client updates

### Backend

- No backend changes were required as the infrastructure was already in place

## Testing

The implementation has been tested to ensure:

- No TypeScript compilation errors
- Successful frontend build process
- Proper parameter passing to the backend API
- UI responsiveness and proper styling
- Character limit enforcement

## Future Enhancements

Potential future improvements could include:

- Preset instruction templates for common use cases
- Instruction history/favorites for frequently used instructions
- Integration with the checklist optimization feature
- Rich text formatting support for complex instructions
