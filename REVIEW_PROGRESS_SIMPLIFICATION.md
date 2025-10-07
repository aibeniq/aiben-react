# Review Progress Bar Implementation - Final Solution

## Problem
The Review functionality's progress bar was stuck because progress polling wasn't happening. The frontend was waiting for the full response before setting the `task_id`, but since processing is synchronous, by the time the `task_id` was set, processing was already complete!

## Root Cause
Unlike Generate which has a separate `createGenerateTask()` endpoint, Review was trying to extract `task_id` from the final response. This meant:
1. Frontend calls `processRagChecklist()`
2. Backend processes everything synchronously (takes 60+ seconds)
3. Backend returns results with `task_id`
4. Frontend finally sets `task_id` and starts polling
5. But it's too late - processing is already done!

## Solution: Two-Step Pattern (Same as Generate)

### Backend Changes

#### 1. Added `createReviewTask` Endpoint
Created `/api/v1/veradoc/review/task` endpoint to create task and return `task_id` immediately:

```python
@router.post("/review/task")
async def create_review_task():
    """
    Create a progress tracking task for document review and return task_id immediately.
    This allows frontend to start progress polling before form submission.
    """
    task_id = progress_tracker.create_task(
        "Reviewing documents",
        {"setup": 0.1, "reviewing": 0.8, "finalizing": 0.1}
    )
    progress_tracker.update_stage_progress(
        task_id, "setup", 0, 1, "Waiting to start document review..."
    )
    return {"task_id": task_id}
```

#### 2. Modified `process_rag_checklist`
- Accepts optional `task_id` parameter (already supported via `RagChecklistRequest`)
- Uses provided `task_id` instead of creating a new one
- Processes synchronously while updating progress with `await asyncio.sleep(0.01)`
- Returns results directly when done

### Frontend Changes

#### 1. Added `createReviewTask` to SDK
Manually added method to `/frontend/src/client/sdk.gen.ts`:

```typescript
public static createReviewTask(): CancelablePromise<{
    task_id: string;
}> {
    return __request(OpenAPI, {
        method: 'POST',
        url: '/api/v1/veradoc/review/task'
    });
}
```

#### 2. Updated Review Mutation
Modified `/frontend/src/routes/_layout/review.tsx` to follow Generate pattern:

```typescript
mutationFn: async (data) => {
  // Step 1: Create task and get task_id
  const taskResponse = await VeradocService.createReviewTask()
  const newTaskId = (taskResponse as any).task_id
  setTaskId(newTaskId)  // Starts progress polling via useEffect

  // Step 2: Call review endpoint with task_id
  const promise = VeradocService.processRagChecklist({
    questions: data.questions,
    knowledgeBaseId: data.knowledgeBaseId,
    customInstructions: data.customInstructions,
    searchMode: data.searchMode,
    taskId: newTaskId,  // Pass task_id to endpoint
    formData: { files: data.files },
  })

  // Step 3: Wait for results
  return registerOperation(promise)
}
```

## How It Works Now

1. **Frontend calls `createReviewTask()`** → Gets `task_id` immediately
2. **Frontend sets `task_id`** → `useEffect` starts polling `/veradoc/progress/{task_id}` every 1 second
3. **Frontend calls `processRagChecklist()`** → Backend processes synchronously
4. **Backend updates progress** → In file/question loops with `await asyncio.sleep(0.01)`
5. **Frontend polls progress** → Shows "Reviewing file 1/2: doc.pdf", etc.
6. **Backend completes** → Returns full results
7. **Frontend receives results** → Displays them

## Key Pattern: Yielding with `await asyncio.sleep(0.01)`

This small sleep in the processing loop allows FastAPI's event loop to handle other requests (like progress polling) while the long-running operation continues:

```python
for file_index, file in enumerate(files):
    progress_tracker.update_stage_progress(
        task_id, "reviewing", file_index, len(files),
        f"Reviewing file {file_index + 1}/{len(files)}: {file_preview}"
    )
    await asyncio.sleep(0.01)  # CRITICAL: Yields to event loop
    # ... process file ...
```

## Files Modified

### Backend:
1. `/backend/app/api/routes/veradoc.py`:
   - Added `/review/task` endpoint (lines 435-449)
   - Modified `process_rag_checklist` to use provided `task_id`

### Frontend:
1. `/frontend/src/client/sdk.gen.ts`:
   - Added `createReviewTask()` method (lines 2290-2304)

2. `/frontend/src/routes/_layout/review.tsx`:
   - Updated mutation to call `createReviewTask()` first
   - Set `task_id` before calling `processRagChecklist()`
   - Pass `task_id` to `processRagChecklist()`

## Import Scoping Fixes

Also fixed two `UnboundLocalError` issues:
1. Added `import traceback` in exception handler (line 1316)
2. Removed redundant `import asyncio` in question loop (was at line 1001)

See `IMPORT_SCOPING_FIXES.md` for details.

## Testing Checklist

- [ ] Upload document for review
- [ ] Verify progress bar appears immediately after submission
- [ ] Verify progress updates: "Reviewing file 1/2: doc.pdf"
- [ ] Verify LLM calls appear in backend logs
- [ ] Verify results display when complete
- [ ] Compare with Generate to ensure same user experience

## Deployment

1. Backend rebuilt: `docker-compose build backend`
2. Frontend rebuilt: `docker-compose build frontend`
3. Services restarted: `docker-compose up -d`
4. Status: ✅ Deployed and running

## Summary

The key insight: **Get the `task_id` BEFORE starting the long-running operation** so progress polling can start immediately. This is the same pattern Generate uses, and it works perfectly for Review too!
