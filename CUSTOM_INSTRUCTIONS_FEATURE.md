# Custom Instructions Feature Implementation

## Overview

This document describes the implementation of the Custom Instructions feature for the VeraDoc Review functionality. This feature allows users to provide additional context or instructions that will be appended to each checklist question during document evaluation.

## Feature Description

The Custom Instructions feature adds a text box to the Review UI where users can enter optional instructions that will be considered when answering individual checklist questions. These instructions are appended to the prompt template when using the `VERADOC_QA_PROMPT_TEMPLATE`.

**Important Note**: The custom instructions functionality is identical in both Review and Optimization modes. In optimization mode, the custom instructions simulate the exact same review conditions that would be used during actual document reviews, ensuring realistic optimization analysis.

## Implementation Details

### Backend Changes

1. **Model Updates**:

   - The `VeraDocRequest` base model already included the `custom_instructions` field for the main review functionality
   - Updated `OptimizeChecklistRequest` model to include `custom_instructions` field:

   ```python
   class OptimizeChecklistRequest(SQLModel):
       knowledge_base_id: str
       questions: str
       target_answers: str = "yes"
       custom_instructions: Optional[str] = Field(default=None, max_length=2000)
   ```

2. **Prompt Template**: The `VERADOC_QA_PROMPT_TEMPLATE` includes a `{custom_instructions_section}` placeholder for injecting custom instructions.

3. **API Endpoints**:

   - The `/process-rag` endpoint supports `custom_instructions` through the `RagChecklistRequest` model inheritance
   - The `/optimize-checklist` endpoint now supports `custom_instructions` as a query parameter through the updated `OptimizeChecklistRequest` model

4. **Backend Logic Updates**:
   - Updated the optimization logic in `veradoc.py` to include custom instructions when generating answers
   - Custom instructions are formatted and injected into the QA prompt template during optimization analysis

### Frontend Changes

1. **Review UI Component**: Added a `Textarea` component in the Review UI (`frontend/src/routes/_layout/review.tsx`):

   - Positioned after the file upload component
   - Includes character count (max 2000 characters)
   - Provides clear placeholder text explaining the feature
   - Uses responsive design and proper styling

2. **Optimization UI Component**: Added a `Textarea` component in the ChecklistModal (`frontend/src/components/Review/ChecklistModal.tsx`):

   - Positioned after the file upload component in the optimization section
   - Same styling and functionality as the Review UI
   - Integrated with the optimization workflow within the checklist editing interface

3. **State Management**:

   - Added `customInstructions` state variable to both Review and ChecklistModal components
   - Proper cleanup of state when optimization section is hidden or modal is closed

4. **API Integration**: Updated API calls to include `custom_instructions` parameter:

   - Modified both single file processing and batch processing functions in Review
   - Updated the optimization function in ChecklistModal
   - Updated mutation function type definitions

5. **Type Updates**: Updated frontend client types to include `customInstructions` in:
   - `VeradocProcessRagChecklistData` type definition for Review functionality
   - `VeradocOptimizeChecklistData` type definition for Optimization functionality
   - SDK request configurations to pass it as a query parameter for both endpoints

## User Experience

### Review UI Layout

- The custom instructions text box appears after the file upload section
- Clear labeling: "Custom Instructions (Optional)"
- Helpful placeholder text explaining the feature
- Character counter showing usage out of 2000 maximum
- Visual feedback with hover and focus states

### Optimization UI Layout

- Same design and placement as the Review UI
- Appears after the file upload section in the optimization section of the ChecklistModal
- Consistent styling and functionality across both features
- Integrated seamlessly with the existing optimization workflow

### Functionality

- Instructions are sent with each review or optimization request
- If no instructions are provided, the field is omitted from the API call
- Instructions are trimmed of whitespace before sending
- Works with both single file and batch processing modes (Review)
- Works with the checklist optimization analysis process

## Usage Example

### Review Process

1. User selects a knowledge base and checklist
2. User uploads document(s) for review
3. User enters optional custom instructions such as:
   - "Consider this is a pediatric study when evaluating age-related requirements"
   - "This protocol is for a low-risk intervention, apply appropriate risk assessment criteria"
   - "Focus on international regulatory requirements rather than US-specific guidelines"
4. User clicks "Review" to process the documents with the custom instructions applied

### Optimization Process

1. User selects a checklist to optimize
2. User uploads a test document that SHOULD meet all requirements
3. User enters optional custom instructions such as:
   - "Consider this is a pediatric study when evaluating age-related requirements"
   - "This protocol is for a low-risk intervention, apply appropriate risk assessment criteria"
   - "Focus on international regulatory requirements rather than US-specific guidelines"
4. User clicks "Optimize Checklist" to analyze questions with the custom instructions considered
5. System provides suggestions for improving questions that may have generated negative responses

**Note**: The custom instructions in optimization mode are exactly the same as those used in review mode. They simulate realistic review conditions to ensure the optimization analysis reflects how questions would actually perform during document reviews.

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

- `frontend/src/routes/_layout/review.tsx`: Main Review UI implementation
- `frontend/src/components/Review/ChecklistModal.tsx`: Optimization UI implementation
- `frontend/src/client/types.gen.ts`: Type definitions for both Review and Optimization
- `frontend/src/client/sdk.gen.ts`: API client updates for both endpoints

### Backend

- `backend/app/models.py`: Added custom_instructions to OptimizeChecklistRequest model
- `backend/app/api/routes/veradoc.py`: Updated optimization logic to use custom instructions

## Testing

The implementation has been tested to ensure:

- No TypeScript compilation errors
- Successful frontend build process
- Proper parameter passing to the backend API for both Review and Optimization
- UI responsiveness and proper styling in both components
- Character limit enforcement
- State management and cleanup in modal components

## Future Enhancements

Potential future improvements could include:

- Preset instruction templates for common use cases
- Instruction history/favorites for frequently used instructions
- Rich text formatting support for complex instructions
- Context-aware instruction suggestions based on selected knowledge base or checklist type
- Integration with additional AI analysis features beyond Review and Optimization
