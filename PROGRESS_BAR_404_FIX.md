# Knowledge Base Progress Bar 404 Fix

**Date**: October 13, 2025  
**Status**: ✅ FIXED

## Problem

The Knowledge Base creation progress bar was returning **404 errors** continuously. The frontend was polling `/api/v1/knowledge-bases/progress/{task_id}` every 2 seconds, but all requests were failing with 404, preventing users from seeing upload progress.

### Symptoms
- Frontend logs showed continuous 404 errors when polling for progress
- Backend logs showed middleware executing but the progress endpoint handler never being reached
- No debug messages from the progress endpoint (`🔍 PROGRESS API: Getting progress for task_id`) appeared in logs
- The route appeared to exist but was never matched

## Root Cause

**FastAPI Route Ordering Issue**

The problem was caused by incorrect route ordering in `backend/app/api/routes/knowledgebases.py`:

```python
# BEFORE (BROKEN):
@router.get("/", response_model=KnowledgeBasesPublic)  # Line 768
def read_knowledge_bases(...):
    ...

@router.get("/{id}", response_model=KnowledgeBasePublic)  # Line 842 - TOO GENERAL
def read_knowledge_base(...):
    ...

# ... many lines later ...

@router.get("/progress/{task_id}")  # Line 2101 - NEVER REACHED
async def get_knowledge_base_progress(...):
    ...
```

### Why This Caused 404s

FastAPI matches routes **in the order they are defined**. When a request came to `/knowledge-bases/progress/8c649fe7-...`:

1. The router first encountered `@router.get("/{id}")` (line 842)
2. This route has a path parameter `{id}` that matches **ANY** single path segment
3. FastAPI matched this route, treating "progress" as the `id` parameter
4. The handler tried to parse "progress" as a UUID, which failed
5. The handler raised a 404 because no knowledge base with ID "progress" exists
6. The actual `/progress/{task_id}` route at line 2101 was **never evaluated**

## Solution

**Move specific routes BEFORE generic path parameter routes:**

```python
# AFTER (FIXED):
@router.get("/", response_model=KnowledgeBasesPublic)  # Line 768
def read_knowledge_bases(...):
    ...

@router.get("/progress/{task_id}")  # Line 842 - NOW FIRST (specific path)
async def get_knowledge_base_progress(...):
    ...

@router.get("/{id}", response_model=KnowledgeBasePublic)  # Line 876 - NOW AFTER (generic)
def read_knowledge_base(...):
    ...
```

### Files Changed
- `backend/app/api/routes/knowledgebases.py`: Moved progress endpoint from line 2101 to line 842 (before the `/{id}` route)

## FastAPI Route Ordering Best Practices

1. **Most Specific First**: Routes with literal path segments should come before routes with path parameters
2. **Static Before Dynamic**: `/progress/{task_id}` should come before `/{id}`
3. **Longer Before Shorter**: `/users/me` should come before `/users/{id}`
4. **Order Matters**: FastAPI uses the first matching route, not the "best" match

### Examples

```python
# ✅ CORRECT ORDER
@router.get("/users/me")           # Most specific
@router.get("/users/active")       # Also specific
@router.get("/users/{user_id}")    # Generic - comes last

# ❌ WRONG ORDER
@router.get("/users/{user_id}")    # Will match "/users/me" and "/users/active"
@router.get("/users/me")           # Never reached
@router.get("/users/active")       # Never reached
```

## Verification

After the fix, you should see:
1. No more 404 errors in the frontend console
2. Backend logs showing: `🔍 PROGRESS API: Getting progress for task_id: ...`
3. Progress bar updating in real-time during knowledge base creation

## Related Files

- `backend/app/api/routes/knowledgebases.py` - Route definitions
- `frontend/src/hooks/useKnowledgeBaseProgress.ts` - Frontend polling hook
- `backend/app/services/progress_tracker.py` - Progress tracking service

## Testing

To verify the fix works:
1. Navigate to Knowledge Bases page
2. Click "Create Knowledge Base"
3. Upload files
4. Observe the progress bar updating (no 404 errors in console)
5. Backend logs should show progress updates being retrieved

---

**Key Takeaway**: In FastAPI, always define specific routes before generic path parameter routes to avoid route shadowing issues.
