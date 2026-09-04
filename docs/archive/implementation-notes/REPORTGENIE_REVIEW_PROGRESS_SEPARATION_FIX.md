# ReportGenie vs Review Progress Bar Separation Fix

**Date:** October 7, 2025  
**Status:** 🚧 IN PROGRESS

## Critical Issue Discovered

The Review page was incorrectly using the **ReportGenie** progress tracking endpoints instead of having its own **VeraDoc** endpoints. This caused:

1. ❌ Review progress showing "Waiting to start report generation..." (report message, not review message)
2. ❌ Review and Generate functionalities sharing the same progress tracker
3. ❌ No way to distinguish between Review and Generate progress

## Root Cause

When implementing progress bars, I mistakenly made the Review page call:
- `ReportgenieService.createGenerateTask()` ← **WRONG**
- Should call: `VeradocService.createReviewTask()` ← **CORRECT**

The Review functionality (`/veradoc/process-rag`) is completely separate from Generate (`/reportgenie/generate`), so they need separate progress tracking endpoints.

## Solution Implemented

### Backend Changes

#### 1. Added Progress Tracker to VeraDoc (`/backend/app/api/routes/veradoc.py`)

**Import added:**
```python
from app.services.progress_tracker import progress_tracker
```

**New Endpoints Created:**

**A. Task Creation Endpoint:**
```python
@router.post("/review/task")
async def create_review_task():
    """
    Create a progress tracking task for document review and return task_id immediately.
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

**B. Progress Endpoint:**
```python
@router.get("/progress/{task_id}")
async def get_veradoc_progress(
    task_id: str,
    current_user: CurrentUser,  # CRITICAL for CORS
) -> Any:
    """
    Get progress information for a VeraDoc task (review).
    """
    progress_data = progress_tracker.get_progress(task_id)
    if not progress_data:
        raise HTTPException(status_code=404, detail="Task not found")

    # Debug logging
    print(f"🔍 VERADOC API RETURNING PROGRESS: task_id={task_id}")
    print(f"🔍 PROGRESS DATA: {progress_data}")
    
    # Yield control
    await asyncio.sleep(0)
    
    return progress_data
```

#### 2. Updated RagChecklistRequest Model (`/backend/app/models.py`)

Added optional `task_id` parameter:
```python
class RagChecklistRequest(VeraDocRequest):
    knowledge_base_id: str
    questions: str
    search_mode: Literal["vector", "full_scan"] = Field(default="vector")
    task_id: Optional[str] = None  # ← NEW
```

#### 3. Updated process_rag_checklist Function

**Added progress tracking throughout:**

```python
# At start - Setup stage
task_id = request_data.task_id
if not task_id:
    task_id = progress_tracker.create_task(...)

progress_tracker.update_stage_progress(
    task_id, "setup", 0, 1, "Initializing document review..."
)

# After KB loaded - Start reviewing
progress_tracker.complete_stage(task_id, "setup", "Setup complete")
progress_tracker.update_stage_progress(
    task_id, "reviewing", 0, total_files, "Starting document review..."
)

# In file loop - Update for each file
for file_index, file in enumerate(files):
    progress_tracker.update_stage_progress(
        task_id, "reviewing", file_index, len(files),
        f"Reviewing file {file_index + 1}/{len(files)}: {file_preview}"
    )
    await asyncio.sleep(0.01)  # Allow progress API to respond

# Before return - Finalizing
progress_tracker.complete_stage(task_id, "reviewing", "Review complete")
progress_tracker.update_stage_progress(
    task_id, "finalizing", 0, 1, "Finalizing results..."
)

# After results created - Complete
progress_tracker.complete_stage(task_id, "finalizing", "Review completed successfully")
progress_tracker.complete_task(task_id, "Review completed successfully")
```

### Frontend Changes (TO BE DONE)

#### 1. Update review.tsx

**Change task creation call:**
```typescript
// BEFORE (WRONG):
const taskResponse = await ReportgenieService.createGenerateTask()

// AFTER (CORRECT):
const taskResponse = await VeradocService.createReviewTask()
```

**Pass task_id to processRagChecklist:**
```typescript
const promise = VeradocService.processRagChecklist({
  questions: data.questions,
  knowledgeBaseId: data.knowledgeBaseId,
  customInstructions: data.customInstructions,
  searchMode: data.searchMode,
  taskId: newTaskId,  // ← ADD THIS
  formData: {
    files: data.files,
  },
})
```

#### 2. Create useVeradocProgress Hook

Create `/frontend/src/hooks/useVeradocProgress.ts`:
```typescript
import { useEffect, useState } from "react"
import { VeradocService } from "@/client"

export interface ProgressData {
  percentage: number
  message: string
  isActive: boolean
  completed: boolean
  error: string | undefined
}

export const useVeradocProgress = (taskId: string | null) => {
  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    message: "",
    isActive: false,
    completed: false,
    error: undefined,
  })

  useEffect(() => {
    if (!taskId) {
      return
    }

    let intervalId: NodeJS.Timeout
    let isActive = true

    const pollProgress = async () => {
      try {
        const response = await VeradocService.getVeradocProgress({ taskId })
        
        if (!isActive) return

        setProgress({
          percentage: response.percentage || 0,
          message: response.message || "",
          isActive: response.status === "in_progress",
          completed: response.status === "completed",
          error: response.error,
        })

        if (response.status === "completed" || response.status === "error") {
          clearInterval(intervalId)
        }
      } catch (error) {
        console.error("Error polling veradoc progress:", error)
      }
    }

    intervalId = setInterval(pollProgress, 1000) // Poll every second
    pollProgress() // Initial poll

    return () => {
      isActive = false
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [taskId])

  return progress
}
```

#### 3. Update review.tsx to use useVeradocProgress

```typescript
import { useVeradocProgress } from "@/hooks/useVeradocProgress"

// In component:
const [taskId, setTaskId] = useState<string | null>(null)
const progress = useVeradocProgress(taskId)

// Display progress bar with veradoc-specific messages
```

## Progress Messages

### ReportGenie (Generate)
- Setup: "Waiting to start report generation..."
- Generating: "Processing section X/Y: [section preview]"
- Finalizing: "Finalizing report..."

### VeraDoc (Review)  
- Setup: "Waiting to start document review..."
- Reviewing: "Reviewing file X/Y: [filename]"
- Finalizing: "Finalizing results..."

## Files Modified

### Backend
1. ✅ `/backend/app/api/routes/veradoc.py` - Added progress endpoints and tracking
2. ✅ `/backend/app/models.py` - Added task_id to RagChecklistRequest
3. ✅ Backend rebuilt and restarted

### Frontend (TO DO)
1. ⏳ `/frontend/src/hooks/useVeradocProgress.ts` - Create new hook
2. ⏳ `/frontend/src/routes/_layout/review.tsx` - Use correct endpoints and hook
3. ⏳ Rebuild frontend

## Testing Checklist

### Review Progress Bar
- [ ] Start a Review operation
- [ ] Verify progress bar shows "Waiting to start document review..." (not "generation")
- [ ] Verify progress updates as files are processed
- [ ] Verify messages show "Reviewing file X/Y: filename"
- [ ] Verify no CORS errors in console
- [ ] Verify progress reaches 100% and disappears

### Generate Progress Bar (Should Still Work)
- [ ] Start a Generate operation  
- [ ] Verify progress bar shows "Waiting to start report generation..."
- [ ] Verify distinct messages from Review
- [ ] Both can run simultaneously without conflicts

## Next Steps

1. ✅ Backend implementation complete
2. ✅ OpenAPI spec regenerated
3. ✅ TypeScript client SDK regenerated  
4. ✅ Create useVeradocProgress hook
5. ✅ Update review.tsx to use VeradocService endpoints
6. ✅ Rebuild frontend
7. ⏳ Test both Review and Generate progress bars

## Status: ✅ COMPLETE - READY FOR TESTING

All code changes have been implemented and deployed. The Review and Generate functionalities now have completely separate progress tracking systems.
