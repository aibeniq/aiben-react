# ReportGenie Progress Bars Implementation

## Summary
Implemented comprehensive progress tracking for ReportGenie functionalities (Review/Generate, Generate Outline, Match, and Compare/Optimize) using the same approach as Knowledge Base creation. The implementation provides real-time progress updates to the frontend through a polling mechanism.

## Endpoints Modified

### 1. **POST `/reportgenie/generate`** (Review/Generate Reports)
**Stages:**
- `setup` (10%): Initializing report generation
- `generating` (80%): Processing each section and generating content
  - Updates progress for each section individually
  - Shows current section being processed
- `finalizing` (10%): Compiling final report

**New Parameters:**
- `task_id` (Optional[str]): Task ID from pre-created task or will create new one

**Progress Updates:**
- Section-by-section progress (e.g., "Processing section 3/10: Executive Summary...")
- Async sleep calls to allow progress API to respond

---

### 2. **POST `/reportgenie/generate-outline`** (Generate Outline)
**Stages:**
- `processing_files` (20%): Processing uploaded example documents
  - Updates for each file being processed
  - Handles vision-enhanced text extraction
- `generating` (70%): Generating outline sections
  - If chunking is needed, updates per chunk
  - Shows LLM generation progress
- `finalizing` (10%): Parsing and finalizing sections

**New Parameters:**
- `task_id` (Optional[str]): Task ID from pre-created task or will create new one

**Progress Updates:**
- File processing: "Processing file 1/3: example.pdf..."
- Chunk processing: "Analyzing chunk 2/5..."
- LLM generation: "Generating outline sections with LLM..."

---

### 3. **POST `/reportgenie/optimize-outline`** (Compare/Match/Optimize)
**Stages:**
- `setup` (10%): Initializing optimization
- `processing_document` (10%): Processing ground-truth document
- `generating` (40%): Generating content for each section
  - Updates for each section being generated
- `matching` (20%): Matching document chunks to sections
  - Updates for each chunk being matched
- `comparing` (15%): Comparing generated content to ground truth
  - Updates for each section being compared
- `finalizing` (5%): Compiling optimization results

**New Parameters:**
- `task_id` (Optional[str]): Task ID from pre-created task or will create new one

**Progress Updates:**
- Section generation: "Generating section 2/8: Introduction..."
- Matching: "Matching chunk 15/42..."
- Comparing: "Comparing section 5/8..."

---

## New Endpoints Created

### 1. **POST `/reportgenie/generate/task`**
Creates a progress task for report generation before actual generation starts.
```json
Response: {"task_id": "uuid-string"}
```

### 2. **POST `/reportgenie/generate-outline/task`**
Creates a progress task for outline generation before actual generation starts.
```json
Response: {"task_id": "uuid-string"}
```

### 3. **POST `/reportgenie/optimize-outline/task`**
Creates a progress task for outline optimization before actual optimization starts.
```json
Response: {"task_id": "uuid-string"}
```

### 4. **GET `/reportgenie/progress/{task_id}`**
Polls the current progress status for any ReportGenie operation.
```json
Response: {
  "task_id": "uuid-string",
  "operation": "Generating report",
  "percentage": 45.5,
  "status": "in_progress",
  "message": "Processing section 5/10: Market Analysis...",
  "current_stage": "generating",
  "stages": {
    "setup": {
      "name": "setup",
      "weight": 0.1,
      "current": 1,
      "total": 1,
      "message": "Setup complete",
      "completed": true,
      "percentage": 100
    },
    "generating": {
      "name": "generating",
      "weight": 0.8,
      "current": 5,
      "total": 10,
      "message": "Processing section 5/10: Market Analysis...",
      "completed": false,
      "percentage": 50
    },
    ...
  }
}
```

---

## Implementation Details

### Progress Tracker Usage
All implementations use the existing `progress_tracker` service from Knowledge Base creation:

```python
from app.services.progress_tracker import progress_tracker

# Create task with weighted stages
task_id = progress_tracker.create_task(
    "Operation name",
    {
        "stage1": 0.3,  # 30% of total
        "stage2": 0.5,  # 50% of total
        "stage3": 0.2   # 20% of total
    }
)

# Update progress within a stage
progress_tracker.update_stage_progress(
    task_id, "stage1", current=5, total=10, 
    message="Processing item 5/10..."
)

# Complete a stage
progress_tracker.complete_stage(
    task_id, "stage1", "Stage 1 complete!"
)

# Mark task as failed
progress_tracker.fail_task(task_id, "Error message")
```

### Error Handling
All endpoints include proper error handling with progress tracker cleanup:

```python
except Exception as e:
    # Mark progress as failed if task_id exists
    if 'task_id' in locals() and task_id:
        progress_tracker.fail_task(task_id, f"Operation failed: {str(e)}")
    raise HTTPException(status_code=500, detail=str(e))
```

### Async Yielding
Critical async sleep calls added throughout to prevent blocking:

```python
await asyncio.sleep(0.01)  # Allow progress API to respond
```

This ensures the progress polling endpoint can respond while long-running operations are executing.

---

## Frontend Integration Guide

### 1. Pre-create Task (Recommended)
```javascript
// Create task first
const taskResponse = await fetch('/api/reportgenie/generate/task', {
  method: 'POST'
});
const { task_id } = await taskResponse.json();

// Start polling
const pollInterval = setInterval(async () => {
  const progress = await fetch(`/api/reportgenie/progress/${task_id}`);
  const data = await progress.json();
  
  // Update UI with data.percentage, data.message, etc.
  updateProgressBar(data.percentage, data.message);
  
  if (data.status === 'completed' || data.status === 'failed') {
    clearInterval(pollInterval);
  }
}, 1000);

// Submit the actual form with task_id
const formData = new FormData();
formData.append('task_id', task_id);
formData.append('knowledge_base_id', kbId);
// ... other fields

await fetch('/api/reportgenie/generate', {
  method: 'POST',
  body: formData
});
```

### 2. Auto-create Task (Alternative)
```javascript
// Submit form without task_id - will auto-create
const response = await fetch('/api/reportgenie/generate', {
  method: 'POST',
  body: formData
});

const { results } = await response.json();
const task_id = results.task_id;

// Start polling with returned task_id
// ... polling logic
```

---

## Response Models Updated

### GenerateOutlineResponse
```python
class GenerateOutlineResponse(BaseModel):
    sections: List[str]
    description_analysis: str
    task_id: Optional[str] = None  # NEW
```

### OptimizedOutlineResponse
```python
class OptimizedOutlineResponse(BaseModel):
    original_sections: List[str]
    suggestions: List[OutlineSuggestion]
    optimized_sections: List[str]
    analysis_summary: str
    task_id: Optional[str] = None  # NEW
```

### ReportGenieResponse result
The `results` dict now includes `task_id`:
```python
result = {
    "full_report": full_report,
    "sections": sections,
    "task_id": task_id  # NEW
}
```

---

## Testing Checklist

- [ ] Test `/reportgenie/generate` with progress tracking
- [ ] Test `/reportgenie/generate-outline` with file upload and progress tracking
- [ ] Test `/reportgenie/optimize-outline` with progress tracking for all stages
- [ ] Test task pre-creation endpoints
- [ ] Test progress polling endpoint
- [ ] Test error scenarios with proper progress cleanup
- [ ] Test with multiple concurrent operations
- [ ] Verify progress percentages are accurate
- [ ] Verify stage messages are clear and informative
- [ ] Test client disconnect handling (operations should mark progress as cancelled)

---

## Benefits

1. **Real-time Feedback**: Users see exactly what's happening during long operations
2. **Better UX**: No more "black box" waiting - users know progress
3. **Consistent Experience**: Same progress tracking pattern as Knowledge Base creation
4. **Debugging**: Progress messages help identify where operations slow down
5. **Cancellation Support**: Foundation for future cancellation feature
6. **Scalable**: Easy to add more stages or operations using the same pattern

---

## Technical Notes

- Progress tracking uses Redis for state storage (via `session_manager`)
- TTL is 1 hour for progress data
- Progress data is cleaned up automatically after TTL
- All percentages are calculated based on weighted stages
- Async sleep calls prevent blocking the event loop
- Error states are properly tracked and reported

---

## Future Enhancements

1. Add WebSocket support for push-based progress updates (instead of polling)
2. Add cancellation endpoints to stop operations in progress
3. Add progress estimates based on historical data
4. Add detailed sub-stage tracking for complex operations
5. Add progress visualization components to frontend
6. Add progress export/logging for debugging

---

## Files Modified

1. `/home/ec2-user/aiben-react/backend/app/api/routes/reportgenie.py`
   - Added progress_tracker import
   - Modified `/generate` endpoint with progress tracking
   - Modified `/generate-outline` endpoint with progress tracking
   - Modified `/optimize-outline` endpoint with progress tracking
   - Added 4 new endpoints for task creation and progress polling

2. Response models implicitly updated to include `task_id` field

---

**Date Implemented**: October 7, 2025
**Implementation Approach**: Same pattern as Knowledge Base creation for consistency
