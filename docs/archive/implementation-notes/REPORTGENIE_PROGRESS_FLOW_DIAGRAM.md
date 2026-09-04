# ReportGenie Progress Flow Diagram

## Complete Flow Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND CLIENT                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
┌───────────────────────────────────┼────────────────────────────────────┐
│                                   │                                    │
│  STEP 1: Create Task (Optional)   │                                    │
│  POST /reportgenie/{type}/task    │                                    │
│                                   │                                    │
│           ┌───────────────────────┴────────────────────┐              │
│           │   Response: { "task_id": "uuid-123" }      │              │
│           └───────────────────────┬────────────────────┘              │
│                                   │                                    │
│  STEP 2: Start Polling            │                                    │
│  GET /reportgenie/progress/uuid-123  (every 1 second)                 │
│                                   │                                    │
│           ┌───────────────────────┴────────────────────┐              │
│           │   Progress Updates:                        │              │
│           │   - percentage: 0 → 100                    │              │
│           │   - message: "Processing..."               │              │
│           │   - current_stage: "setup" → "finalizing"  │              │
│           │   - status: "started" → "completed"        │              │
│           └───────────────────────┬────────────────────┘              │
│                                   │                                    │
│  STEP 3: Submit Form              │                                    │
│  POST /reportgenie/{operation}    │                                    │
│  FormData: task_id=uuid-123       │                                    │
│                                   │                                    │
│           ┌───────────────────────┴────────────────────┐              │
│           │   Response includes task_id                │              │
│           │   { results: { ..., task_id: "uuid-123"}}  │              │
│           └───────────────────────┬────────────────────┘              │
│                                   │                                    │
│  STEP 4: Wait for Completion      │                                    │
│  (Polling continues until status = "completed"/"failed")              │
│                                   │                                    │
└───────────────────────────────────┴────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVER                               │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
  OPERATION: GENERATE REPORT (Review)
═══════════════════════════════════════════════════════════════════════

Stage 1: SETUP (10%)
├── Initialize report generation
├── Parse sections
├── Load knowledge base
└── Update: "Initializing report generation..."
    ✓ Complete: "Setup complete"

Stage 2: GENERATING (80%)
├── For each section (1 to N):
│   ├── Update: "Processing section {i}/{N}: {section_name}..."
│   ├── Search knowledge base (vector or full_text)
│   ├── Generate content with LLM
│   ├── Collect citations
│   └── await asyncio.sleep(0.01)  ← Allow progress API to respond
└── Update: "All sections generated successfully"
    ✓ Complete: "All sections generated successfully"

Stage 3: FINALIZING (10%)
├── Compile final report
├── Store interaction
└── Update: "Compiling final report..."
    ✓ Complete: "Report generation complete!"


═══════════════════════════════════════════════════════════════════════
  OPERATION: GENERATE OUTLINE
═══════════════════════════════════════════════════════════════════════

Stage 1: PROCESSING_FILES (20%)
├── If files uploaded:
│   ├── For each file (1 to N):
│   │   ├── Update: "Processing file {i}/{N}: {filename}..."
│   │   ├── Extract text with vision enhancement
│   │   └── await asyncio.sleep(0.01)
│   └── ✓ Complete: "Processed {N} files"
└── Else:
    └── ✓ Complete: "No files to process"

Stage 2: GENERATING (70%)
├── If document needs chunking:
│   ├── Create chunks
│   ├── Update: "Processing {N} document chunks..."
│   ├── For each chunk (1 to N):
│   │   ├── Update: "Analyzing chunk {i}/{N}..."
│   │   ├── Generate sections with LLM
│   │   └── await asyncio.sleep(0.01)
│   └── Deduplicate and refine sections
└── Else:
    ├── Update: "Generating outline sections with LLM..."
    ├── Invoke LLM
    └── await asyncio.sleep(0.01)
    ✓ Complete: "Outline generated successfully"

Stage 3: FINALIZING (10%)
├── Parse LLM response
├── Extract sections
├── Record interaction
└── Update: "Parsing and finalizing sections..."
    ✓ Complete: "Outline generation complete!"


═══════════════════════════════════════════════════════════════════════
  OPERATION: OPTIMIZE OUTLINE (Match + Compare)
═══════════════════════════════════════════════════════════════════════

Stage 1: SETUP (10%)
├── Initialize optimization
├── Retrieve knowledge base
└── Update: "Initializing outline optimization..."
    ✓ Complete: "Setup complete"

Stage 2: PROCESSING_DOCUMENT (10%)
├── Extract ChromaDB
├── Load embeddings
├── Read ground-truth file
├── Sanitize text
└── Update: "Processing ground-truth document..."
    ✓ Complete: "Ground-truth document processed"

Stage 3: GENERATING (40%)
├── Parse sections
├── Update: "Starting section generation..."
├── For each section (1 to N):
│   ├── Update: "Generating section {i}/{N}: {section_name}..."
│   ├── If consults documents:
│   │   ├── Search knowledge base
│   │   └── Generate with LLM
│   └── await asyncio.sleep(0.01)
└── ✓ Complete: "All sections generated"

Stage 4: MATCHING (20%)  ← This is the "Match" functionality
├── Split ground-truth into chunks
├── Update: "Starting document matching..."
├── For each chunk (1 to N):
│   ├── Update: "Matching chunk {i}/{N}..."
│   ├── Use LLM to map chunk to section
│   ├── Extract boundary reasoning
│   ├── Store mapping
│   └── await asyncio.sleep(0.01)
└── ✓ Complete: "Document matching complete"

Stage 5: COMPARING (15%)  ← This is the "Compare" functionality
├── Update: "Starting section comparison..."
├── For each consulting section (1 to N):
│   ├── Update: "Comparing section {i}/{N}..."
│   ├── Get generated content
│   ├── Get matched ground-truth chunks
│   ├── Use LLM to analyze quality gap
│   ├── Generate suggestions
│   └── await asyncio.sleep(0.01)
└── ✓ Complete: "Section comparison complete"

Stage 6: FINALIZING (5%)
├── Compile optimization results
├── Calculate statistics
└── Update: "Finalizing optimization results..."
    ✓ Complete: "Optimization complete!"


═══════════════════════════════════════════════════════════════════════
  PROGRESS TRACKING SERVICE (Redis-backed)
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│  ProgressTracker Service                                        │
│  ────────────────────────────────────────────────────────────── │
│                                                                  │
│  create_task(operation, stages_dict)                            │
│    ↓                                                             │
│  Returns: task_id (UUID)                                        │
│  Stores in Redis: progress:{task_id}                            │
│  TTL: 1 hour                                                    │
│                                                                  │
│  update_stage_progress(task_id, stage, current, total, msg)    │
│    ↓                                                             │
│  Calculates percentage based on weighted stages                │
│  Updates Redis with latest progress                             │
│                                                                  │
│  complete_stage(task_id, stage, message)                        │
│    ↓                                                             │
│  Marks stage as completed (100%)                                │
│  Moves to next stage                                            │
│                                                                  │
│  fail_task(task_id, error_message)                              │
│    ↓                                                             │
│  Sets status = "failed"                                         │
│  Stores error_message                                           │
│                                                                  │
│  get_progress(task_id)                                          │
│    ↓                                                             │
│  Returns current progress state from Redis                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
  PROGRESS DATA STRUCTURE
═══════════════════════════════════════════════════════════════════════

{
  "task_id": "uuid-123",
  "operation": "Generating report",
  "percentage": 45.5,                    ← Overall weighted percentage
  "status": "in_progress",               ← started | in_progress | completed | failed
  "message": "Processing section 5/10...", ← Current operation message
  "current_stage": "generating",         ← Active stage
  "created_at": "2025-10-07T10:30:00",
  "updated_at": "2025-10-07T10:30:45",
  "error_message": null,                 ← Only if status === "failed"
  
  "stages": {
    "setup": {
      "name": "setup",
      "weight": 0.1,                     ← 10% of total
      "current": 1,
      "total": 1,
      "message": "Setup complete",
      "completed": true,
      "percentage": 100                  ← 100% of this stage
    },
    "generating": {
      "name": "generating",
      "weight": 0.8,                     ← 80% of total
      "current": 5,                      ← Current item
      "total": 10,                       ← Total items
      "message": "Processing section 5/10...",
      "completed": false,
      "percentage": 50                   ← 50% of this stage (5/10)
    },
    "finalizing": {
      "name": "finalizing",
      "weight": 0.1,                     ← 10% of total
      "current": 0,
      "total": 1,
      "message": "",
      "completed": false,
      "percentage": 0                    ← Not started yet
    }
  }
}


═══════════════════════════════════════════════════════════════════════
  PERCENTAGE CALCULATION
═══════════════════════════════════════════════════════════════════════

Overall Percentage = Σ (stage_weight × stage_percentage) for all stages

Example with 3 stages:
- setup: 10% weight, 100% complete    = 0.1 × 1.0   = 0.10
- generating: 80% weight, 50% complete = 0.8 × 0.5  = 0.40
- finalizing: 10% weight, 0% complete  = 0.1 × 0.0  = 0.00
                                        ─────────────────
                                  Total = 0.50 = 50%


═══════════════════════════════════════════════════════════════════════
  ERROR HANDLING FLOW
═══════════════════════════════════════════════════════════════════════

try:
    # Create task
    task_id = progress_tracker.create_task(...)
    
    # Update progress through stages
    progress_tracker.update_stage_progress(...)
    
    # If successful
    progress_tracker.complete_stage(...)
    
except Exception as e:
    # Mark task as failed
    if task_id:
        progress_tracker.fail_task(task_id, f"Error: {str(e)}")
    
    # Raise HTTP exception
    raise HTTPException(status_code=500, detail=str(e))


═══════════════════════════════════════════════════════════════════════
  KEY IMPLEMENTATION PATTERNS
═══════════════════════════════════════════════════════════════════════

✓ Always await asyncio.sleep(0.01) in loops
  → Prevents blocking the event loop
  → Allows progress API to respond

✓ Update progress before LLM calls
  → Shows what's about to happen
  → Better user feedback

✓ Use descriptive messages
  → "Processing section 3/10: Executive Summary..."
  → Not just "Processing..."

✓ Clean up on errors
  → Always call fail_task in exception handler
  → Prevents stuck progress states

✓ Optional task_id parameter
  → Backward compatible
  → Allows pre-creation or auto-creation

✓ Return task_id in responses
  → Frontend can extract and use
  → Supports both workflows


═══════════════════════════════════════════════════════════════════════
  FRONTEND UI EXAMPLE
═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│  Report Generation Progress                                     │
│  ───────────────────────────────────────────────────────────── │
│                                                                  │
│  [████████████████████████░░░░░░░░░░░░░░░░] 60%                │
│                                                                  │
│  Status: Processing section 6/10: Market Analysis...            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Stage Progress:                                         │  │
│  │                                                           │  │
│  │  ✓ Setup               [████████████████] 100%          │  │
│  │  ⟳ Generating          [████████████░░░░] 60%   ← Active│  │
│  │  ○ Finalizing          [░░░░░░░░░░░░░░░░] 0%            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Current Stage: Generating (Section 6 of 10)                   │
│  ───────────────────────────────────────────────────────────── │
│  [██████████████████░░░░░░░░░░░░░░░░░░░░] 60%                  │
│  Processing section 6/10: Market Analysis...                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
  END OF FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════
```

## Summary

This implementation provides:
- ✅ **Real-time progress** for all ReportGenie operations
- ✅ **Detailed stage tracking** with weighted percentages  
- ✅ **Clear user feedback** with descriptive messages
- ✅ **Consistent pattern** matching Knowledge Base creation
- ✅ **Error handling** with proper cleanup
- ✅ **Backend complete** - ready for frontend integration

All operations now have the same smooth, transparent progress experience!
