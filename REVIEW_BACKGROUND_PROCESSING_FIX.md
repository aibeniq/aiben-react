# Review Background Processing Fix

## Problem
The Review functionality was getting stuck with constant progress polling showing:
- Status: `in_progress` at 10%
- Message: "Starting document review..."
- No actual LLM calls or document processing happening

## Root Cause
The previous implementation had a flawed architecture:
1. Frontend called `createReviewTask()` to get a task_id
2. Frontend then called `processRagChecklist()` with that task_id
3. `processRagChecklist()` was a synchronous endpoint that blocked while processing
4. The progress got stuck at the initial state because the function was waiting for the entire HTTP request to complete

## Solution Implemented

### Backend Changes (`backend/app/api/routes/veradoc.py`)

1. **Added BackgroundTasks import**:
   ```python
   from fastapi import BackgroundTasks
   ```

2. **Created `_process_review_background()` function**:
   - Async function that runs in the background
   - Creates its own database session
   - Updates progress throughout processing
   - Currently has TODO placeholders for the actual processing logic

3. **Modified `process_rag_checklist()` endpoint**:
   - Now accepts `BackgroundTasks` parameter
   - Creates a task_id immediately
   - Reads all file data into memory
   - Schedules `_process_review_background()` to run in background
   - Returns immediately with task_id
   - Frontend can start polling for progress right away

4. **Kept `/veradoc/progress/{task_id}` endpoint**:
   - Same as before, returns progress updates
   - Now actually receives progress from the background task

### Frontend Changes (`frontend/src/routes/_layout/review.tsx`)

1. **Simplified the mutation flow**:
   - Now only calls `VeradocService.processRagChecklist()`
   - Extracts `task_id` from the response
   - Sets the task_id for progress polling
   - The `useVeradocProgress` hook handles polling automatically

2. **Removed separate `createReviewTask()` call**:
   - No longer needed - task creation happens inside `processRagChecklist()`

## Current State

### ✅ COMPLETED - Full Implementation

**Backend (`backend/app/api/routes/veradoc.py`)**:
- ✅ `_process_review_background()` function - Complete with all 800+ lines of processing logic
- ✅ Knowledge Base loading and ChromaDB extraction
- ✅ Retriever setup (vector search vs full scan with FullScanRetriever class)
- ✅ LLM initialization with vision support detection
- ✅ Context pre-fetching optimization for all questions
- ✅ File processing loop with progress updates
- ✅ Question processing with pre-fetched context
- ✅ Vision analysis integration for images
- ✅ Translation support
- ✅ Final evaluation generation
- ✅ LLM interaction recording
- ✅ Results storage in progress_tracker metadata
- ✅ Progress updates at every stage with `await asyncio.sleep(0.01)`

**Progress Tracker (`backend/app/services/progress_tracker.py`)**:
- ✅ Added `complete_task()` method
- ✅ Added `update_task_metadata()` method to store results
- ✅ Added `get_task_metadata()` method to retrieve results

**New Results Endpoint (`backend/app/api/routes/veradoc.py`)**:
- ✅ `GET /veradoc/results/{task_id}` endpoint
- ✅ Returns results stored in metadata after task completion
- ✅ Validates task exists and is completed

**Frontend (`frontend/src/hooks/useVeradocProgress.ts`)**:
- ✅ Updated to automatically fetch results when status='completed'
- ✅ Calls `VeradocService.getVeradocResults()` when task completes
- ✅ Stores results in progress state for access by components
- ✅ Added error handling for results fetching

**Frontend (`frontend/src/routes/_layout/review.tsx`)**:
- ✅ Simplified to only call `processRagChecklist()` once
- ✅ Extracts task_id from response
- ✅ Relies on `useVeradocProgress` hook for polling and results retrieval

**OpenAPI Client SDK**:
- ✅ Regenerated with new `/veradoc/results/{task_id}` endpoint
- ✅ TypeScript client includes `getVeradocResults()` method

### ⏳ TODO - Next Steps

**Testing Required**:
1. Test with a single document review
2. Test with multiple documents  
3. Verify progress updates show correctly
4. Verify LLM calls appear in backend logs
5. Verify results are displayed when complete
6. Test error handling (invalid KB, empty file, etc.)
7. Test cancellation (navigate away mid-processing)
8. Test with both vector search and full scan modes
9. Test with vision-enabled documents (PDFs with images)
10. Test translation functionality

**Frontend Results Display**:
The `useVeradocProgress` hook now provides `progress.results` when the task completes. The review page needs to be updated to:
- Extract results from `progress.results` instead of mutation response
- Display them in the UI when `progress.completed === true`
- Handle the new format where results come asynchronously via progress polling

**Potential Optimizations**:
- Add caching of results to avoid re-fetching
- Add cleanup of old task data from Redis
- Consider streaming results as they're generated (advanced)

## Pattern Reference: Knowledge Base Creation

The implementation should follow the same pattern as Knowledge Base creation:

```python
# In knowledgebases.py:

@router.post("/create")
async def create_knowledge_base(
    background_tasks: BackgroundTasks,
    ...
):
    # Create task
    task_id = progress_tracker.create_task(...)
    
    # Read file data
    file_data = [await file.read() for file in files]
    
    # Schedule background processing
    background_tasks.add_task(
        process_knowledge_base_background,
        knowledge_base_id=kb.id,
        task_id=task_id,
        file_data=file_data,
        ...
    )
    
    # Return immediately
    return {"task_id": task_id}


async def process_knowledge_base_background(...):
    with Session(engine) as session:
        # Do all the processing
        # Update progress throughout
        await asyncio.sleep(0.01)  # Yield for progress polling
```

## Testing Checklist

After completing the TODO items:

- [ ] Upload a document and submit for review
- [ ] Verify progress bar updates from 0% to 100%
- [ ] Verify messages change: "Initializing..." → "Reviewing file 1/X: filename" → "Finalizing..." → "Complete"
- [ ] Verify LLM calls appear in backend logs
- [ ] Verify results are displayed when processing completes
- [ ] Test with multiple files
- [ ] Test cancellation (navigate away mid-processing)
- [ ] Test error handling (invalid KB, empty file, etc.)

## Key Insights

1. **BackgroundTasks vs Threading**: FastAPI's BackgroundTasks is simpler and cleaner than manual threading
2. **Yielding Control**: `await asyncio.sleep(0.01)` is critical to allow the progress API to respond
3. **Session Management**: Background tasks need their own database session (`with Session(engine)`)
4. **File Data Handling**: Read file data into memory before scheduling background task (UploadFile objects can't be passed to background tasks)

## References

- Original issue: Backend logs showing only progress polling, no LLM calls
- Similar working implementation: `/backend/app/api/routes/knowledgebases.py` lines 886-1050
- Progress tracking service: `/backend/app/services/progress_tracker.py`
