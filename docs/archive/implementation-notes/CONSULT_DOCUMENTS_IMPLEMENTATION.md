# Consult Documents Toggle Implementation

## Overview

This implementation ensures that the "Consult documents" toggle for each checklist question in the VeraDoc review functionality works as intended. When toggled OFF, the review process will NOT search the reference database for policy context for that specific question.

## Implementation Details

### Backend Support (Already Implemented)

- The backend in `backend/app/api/routes/veradoc.py` already supports structured questions with `consultDocuments` flags
- When `consultDocuments` is `false`, the backend skips the knowledge base retrieval and uses only the document content
- Questions are parsed as JSON with the structure: `[{"text": "question", "consultDocuments": true/false}, ...]`

### Frontend Changes Made

#### 1. ChecklistTable.tsx

- Added `QuestionData` interface with `id`, `text`, and `consultDocuments` fields
- Updated all question management functions to maintain unique IDs and structured data
- Added `onStructuredQuestionsChange` prop to pass structured question data to parent components
- Modified checklist selection logic to parse stored questions and provide structured data
- Updated save logic to serialize questions as structured JSON (excluding IDs) for backend compatibility

#### 2. ChecklistModal.tsx

- Updated `QuestionData` interface to include `id` field
- Modified `handleConsultDocumentsChange` to use question IDs for toggle operations
- Updated all question management to work with structured data

#### 3. QuestionItem.tsx

- Added `id` prop and uses it for `consultDocuments` toggle operations
- Passes unique question ID to toggle handler

#### 4. review.tsx (routes/\_layout/review.tsx)

- Added `QuestionData` interface
- Added `structuredQuestions` state to maintain structured question data
- Updated `ChecklistTable` usage to include `onStructuredQuestionsChange` prop
- Modified review request logic in both `handleRun` and `handleProcessBatch` to send structured questions as JSON when available
- Falls back to plain text questions for legacy compatibility

## How It Works

### Data Flow

1. **Checklist Storage**: Questions are stored as JSON with structure: `[{"text": "question", "consultDocuments": boolean}, ...]`
2. **Checklist Selection**: When a checklist is selected, questions are parsed into structured format with unique runtime IDs
3. **Toggle Operations**: Each question has a unique ID for toggle operations, maintaining consultDocuments flags
4. **Review Submission**: Structured questions (without IDs) are sent as JSON to the backend
5. **Backend Processing**: Backend respects the `consultDocuments` flag for each question

### Toggle Behavior

- **ON (true)**: Question will search the knowledge base for policy context and include citations
- **OFF (false)**: Question will only use the uploaded document content, no knowledge base search

## Testing Instructions

### Manual Testing

1. Navigate to the Review page (VeraDoc)
2. Select a knowledge base
3. Create or select a checklist with multiple questions
4. Toggle "Consult documents" OFF for specific questions
5. Upload a test document
6. Run the review process
7. Verify that questions with "Consult documents" OFF do not include policy context or citations in their answers

### Expected Results

- Questions with "Consult documents" ON: Include policy context and citations from the knowledge base
- Questions with "Consult documents" OFF: Only reference the uploaded document content, no external policy context

### Backend Verification

You can verify backend behavior by checking the console logs when processing questions:

- Look for: `Processing question: [question text]... (consult documents: true/false)`
- Questions with `consult documents: false` should skip the knowledge base retrieval step

## Legacy Compatibility

The implementation maintains backward compatibility:

- Existing checklists with plain text questions are automatically converted to structured format
- Legacy questions default to `consultDocuments: true`
- The system gracefully handles both structured and plain text question formats

## Files Modified

1. `frontend/src/components/Review/ChecklistTable.tsx`
2. `frontend/src/components/Review/ChecklistModal.tsx`
3. `frontend/src/components/Review/QuestionItem.tsx`
4. `frontend/src/routes/_layout/review.tsx`

## Backend Files (Already Supporting This Feature)

- `backend/app/api/routes/veradoc.py` - Contains the logic to respect `consultDocuments` flags
