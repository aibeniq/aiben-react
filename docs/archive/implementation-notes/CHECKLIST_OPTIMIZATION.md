# Checklist Optimization Feature

## Overview

The checklist optimization feature allows users to improve their VeraDoc review checklists by testing them against documents that should meet all requirements. When the system identifies checklist questions that result in negative answers (indicating the document doesn't meet a requirement), it suggests revised versions of those questions that are less stringent while maintaining the original intent.

## How It Works

### Backend Implementation

1. **Endpoint**: `/api/v1/veradoc/optimize-checklist`
2. **Method**: POST with multipart/form-data
3. **Parameters**:
   - `knowledge_base_id`: ID of the knowledge base to use for evaluation
   - `questions`: Current checklist questions (newline-separated)
   - `files`: Test document that should meet all requirements

### Process Flow

1. User uploads a document that should ideally meet all checklist requirements
2. System runs the standard VeraDoc review process using the current checklist
3. For each question that results in a negative answer ("no", "insufficient", "missing", etc.), the system:
   - Uses an LLM to generate a suggested revision
   - Provides reasoning for the suggested change
   - Marks whether the question needs revision
4. Returns suggestions for all questions, with optimization suggestions for problematic ones

### Frontend Implementation

- **Component**: `OptimizeChecklistModal.tsx`
- **Integration**: Accessible from the ChecklistTable component via an "Optimize" button
- **Features**:
  - File upload for test document
  - Real-time optimization progress
  - Review and accept/reject individual suggestions
  - Apply selected optimizations to the checklist

## Key Components

### Backend Models

- `OptimizeChecklistRequest`: Input model for optimization requests
- `ChecklistSuggestion`: Individual suggestion with original/suggested questions and reasoning
- `OptimizedChecklistResponse`: Complete response with all suggestions and analysis

### Utility Functions

- `needs_optimization(answer: str)`: Detects if an answer indicates a requirement wasn't met
- `parse_optimization_response(llm_response: str)`: Parses LLM suggestions into structured format

### LLM Prompt Template

The optimization uses `VERADOC_OPTIMIZE_PROMPT_TEMPLATE` which instructs the LLM to:

- Analyze the original question and its negative answer
- Consider the document context
- Suggest a less stringent but meaningful revision
- Provide clear reasoning for changes

## Usage Instructions

1. **Access the Feature**:

   - Navigate to the Review page
   - Select a knowledge base and checklist
   - Click the "Optimize" button in the checklist table

2. **Upload Test Document**:

   - Choose a document that should ideally meet all checklist requirements
   - This could be a known good document or a document that represents your quality standards

3. **Review Suggestions**:

   - The system will show which questions need optimization
   - Review each suggestion and its reasoning
   - Accept or reject individual suggestions

4. **Apply Changes**:
   - Click "Apply X Suggestions" to update your checklist
   - The checklist will be updated with your accepted suggestions

## Benefits

- **Improved Accuracy**: Makes checklists more realistic and achievable
- **Better User Experience**: Reduces false negatives in document reviews
- **Maintains Intent**: Keeps the core purpose of requirements while adjusting specificity
- **Data-Driven**: Uses actual document evaluation results to guide improvements

## Technical Notes

- The feature requires an active LLM connection for generating suggestions
- Optimization runs asynchronously with progress feedback
- The system preserves the original questions and allows selective application of changes
- All suggestions include reasoning to help users make informed decisions

## Future Enhancements

- Batch optimization across multiple test documents
- Historical tracking of optimization changes
- A/B testing of different question variations
- Machine learning-based suggestion refinement
