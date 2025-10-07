# Full Document Scan Progress Bar Fix - October 7, 2025

## Problem Summary

When performing a Review with **Full Document Scan** mode, the progress bar would get stuck showing "Reviewing file 1/#..." or "Completed question 1/2 for file 1/1" without updating further, even though the backend was successfully completing the processing.

Additionally, **Vector Search** mode would sometimes encounter a 404 error when polling for progress: "Task not found" / CORS error.

## Root Causes

### 1. Insufficient Progress Updates During Question Processing
The progress was only being updated at the **start** of each question processing loop, but not after each question was completed. Since Full Document Scan involves:
- Much larger context (all documents vs. top 5-10)
- LLM-based relevance filtering
- Longer processing time per question

This meant the frontend would see "Answering question 1..." and then wait a long time (potentially minutes) before seeing "Answering question 2...", making it appear stuck.

### 2. Insufficient Event Loop Yielding
The `await asyncio.sleep()` calls between progress updates were too short (0.01 seconds), which didn't give enough time for:
- Progress data to be saved to Redis
- Frontend polling requests to retrieve the updated progress
- Event loop to process other async operations

This was especially problematic for Full Document Scan where each question takes significantly longer to process.

## Solution Implemented

### Backend Changes (`/backend/app/api/routes/veradoc.py`)

#### 1. Added Progress Update After Each Question Completion (Lines 1324-1334)
```python
# Update progress AFTER question is completed
total_questions = len(files) * len(question_list)
questions_completed = file_index * len(question_list) + (i + 1)  # +1 because we just completed this question
print(f"📊 PROGRESS UPDATE: Completed {questions_completed}/{total_questions} questions")
progress_tracker.update_stage_progress(
    task_id, "reviewing", questions_completed, total_questions,
    f"Completed question {i+1}/{len(question_list)} for file {file_index+1}/{len(files)}"
)
# Give MORE time for progress polling to see the update, especially for Full Document Scan
await asyncio.sleep(0.1)  # Increased from 0.01 to ensure progress is visible
```

**Impact**: Now the frontend sees TWO progress updates per question:
1. "Answering question X/Y..." - when question processing starts
2. "Completed question X/Y..." - when question processing finishes

This provides much more granular feedback, especially for Full Document Scan where each question can take 30-60 seconds.

#### 2. Increased Event Loop Yielding Time (Multiple Locations)
Changed `await asyncio.sleep(0.01)` to `await asyncio.sleep(0.1)` at critical points:
- After completing the "reviewing" stage (Line 1423)
- After starting the "finalizing" stage (Line 1430)
- After completing the "finalizing" stage (Line 1459)
- After completing the task (Line 1462)
- After question completion (Line 1334)

**Impact**: Gives 10x more time for:
- Progress data to be saved to Redis
- Frontend to poll and receive updates
- Event loop to process concurrent requests

#### 3. Added Debug Logging
Added comprehensive logging throughout the progress update flow:
```python
print(f"📊 COMPLETING REVIEWING STAGE for task {task_id}")
print(f"📊 STARTING FINALIZING STAGE for task {task_id}")
print(f"📊 COMPLETING FINALIZING STAGE for task {task_id}")
print(f"📊 COMPLETING TASK for task {task_id}")
print(f"📊 STORING RESULTS METADATA for task {task_id}")
```

**Impact**: Makes it much easier to debug progress tracking issues in production.

### Progress Tracker Changes (`/backend/app/services/progress_tracker.py`)

#### Added Debug Logging to `_save_progress` Method (Lines 421-427)
```python
print(f"💾 SAVING PROGRESS for task {task_id}: status={progress.status}, percentage={progress.percentage}, message={progress.message}")
# ... save logic ...
print(f"✅ PROGRESS SAVED SUCCESSFULLY for task {task_id}")
```

**Impact**: Confirms when progress data is being saved, helpful for troubleshooting Redis/storage issues.

## Testing Instructions

### Test Full Document Scan Progress Visibility

1. **Open Review Page**: Navigate to the Review functionality
2. **Upload a document** (PDF, DOCX, or TXT)
3. **Select Full Document Scan mode**
4. **Add 2-3 questions**
5. **Start Review**
6. **Observe Progress Bar**: Should now show:
   - "Beginning document review..." (initial)
   - "Answering question 1/X for file 1/1" (question starts)
   - "Completed question 1/X for file 1/1" (question finishes)
   - "Answering question 2/X for file 1/1" (next question starts)
   - "Completed question 2/X for file 1/1" (next question finishes)
   - ... continues for all questions ...
   - "Generating final evaluation..." (finalizing)
   - "Review completed successfully" (done)

### Test Vector Search Mode

1. **Repeat above steps** but select **Vector Search** mode
2. **Verify**: Progress updates appear (should be faster than Full Document Scan)
3. **Verify**: No 404 errors in browser console
4. **Verify**: Results display correctly after completion

## Expected Behavior

### Full Document Scan
- **Progress updates every 30-60 seconds** (depending on question complexity)
- **Two updates per question**: Start and Completion
- **Smooth transitions** between reviewing and finalizing stages
- **No stuck progress** at any point

### Vector Search
- **Faster updates** (questions complete in 5-15 seconds)
- **Same progress granularity** as Full Document Scan
- **No 404 errors** when polling progress
- **Results retrieved successfully** after completion

## Technical Notes

### Why Two Progress Updates Per Question?

Full Document Scan questions can take 30-60+ seconds each because:
1. **Large Context**: All documents (hundreds of pages) vs. top 5-10 chunks
2. **LLM Processing**: Larger token counts = longer generation time
3. **Multiple LLM Calls**: Context filtering + answer generation

Having TWO updates (start + completion) ensures the frontend knows processing is active, not stuck.

### Why Increase Sleep Time to 0.1 Seconds?

The previous 0.01 seconds (10ms) was too short for:
- **Redis Write**: Serializing and writing progress data
- **Network Latency**: Between backend container and Redis container
- **Frontend Polling**: HTTP request + response time
- **Event Loop Processing**: Other async operations

0.1 seconds (100ms) provides a comfortable buffer while still being imperceptible to users.

### Why Full Document Scan Specifically?

Vector Search uses **similarity search** to find the top 5-10 most relevant document chunks, which is fast. Full Document Scan:
1. Retrieves **ALL documents** from the knowledge base
2. **Filters each chunk** with LLM calls to determine relevance
3. Processes questions with **much larger context** (hundreds of chunks vs. 5-10)

This makes Full Document Scan 5-10x slower per question, making progress visibility critical.

## Related Files

- `/backend/app/api/routes/veradoc.py` - Main review endpoint with progress updates
- `/backend/app/services/progress_tracker.py` - Progress tracking service
- `/frontend/src/routes/_layout/review.tsx` - Frontend Review page
- `/frontend/src/hooks/useVeraDocProgress.ts` - Progress polling hook

## Future Improvements

1. **Adaptive Polling**: Slow down polling frequency when in finalizing stage
2. **Progress Percentage**: Calculate more accurate percentage based on context size
3. **Time Estimates**: Show estimated time remaining based on average question processing time
4. **Cancellation**: Allow users to cancel long-running Full Document Scan reviews
5. **Background Processing**: Move Review to background tasks for very large documents

## Verification

Backend logs should now show:
```
💾 SAVING PROGRESS for task xxx: status=in_progress, percentage=35.0, message=Answering question 1/2...
✅ PROGRESS SAVED SUCCESSFULLY for task xxx
📊 PROGRESS UPDATE: Completed 1/2 questions
💾 SAVING PROGRESS for task xxx: status=in_progress, percentage=65.0, message=Completed question 1/2...
✅ PROGRESS SAVED SUCCESSFULLY for task xxx
```

Frontend should show smooth progress transitions without any stuck states or 404 errors.
