# Fix for Optimize Outline Validation Error

## Problem

The Optimize Outline functionality was returning a 422 Validation Error with the message "Invalid request. Please check your inputs and try again."

## Root Cause

The backend endpoint was using `request_data: OptimizeOutlineRequest = Depends()` to parse multipart form data with files, but FastAPI's `Depends()` with Pydantic models doesn't work properly with multipart/form-data that includes both files and form fields.

## Solution

### Backend Changes (reportgenie.py)

**Before:**

```python
@router.post("/optimize-outline", response_model=OptimizedOutlineResponse)
async def optimize_outline(
    session: SessionDep,
    current_user: CurrentUser,
    request_data: OptimizeOutlineRequest = Depends(),
    files: List[UploadFile] = File(...),
    request: FastAPIRequest = None,
):
```

**After:**

```python
@router.post("/optimize-outline", response_model=OptimizedOutlineResponse)
async def optimize_outline(
    session: SessionDep,
    current_user: CurrentUser,
    knowledge_base_id: str = Form(...),
    outline_id: str = Form(...),
    sections: str = Form(...),
    custom_instructions: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    request: FastAPIRequest = None,
):
```

### Changes Made:

1. **Added Form import** to FastAPI imports
2. **Added Optional import** to typing imports
3. **Replaced Pydantic model dependency** with individual Form parameters
4. **Updated parameter references** in function body:
   - `request_data.knowledge_base_id` → `knowledge_base_id`
   - `request_data.sections` → `sections`
   - Removed references to `request_data.custom_instructions` (parameter is now direct)

### Why This Fixes the Issue:

- FastAPI's `Form(...)` parameters properly handle multipart form data
- Individual form fields are correctly parsed instead of trying to deserialize a complex object
- The frontend's FormData approach now aligns with the backend's parameter expectations
- File uploads and form data are handled separately and correctly

### Frontend (Already Fixed):

The frontend was already correctly sending data as FormData with proper field names:

```typescript
formData.append("knowledge_base_id", data.knowledgeBaseId)
formData.append("outline_id", data.outlineId)
formData.append("sections", JSON.stringify(data.sections))
formData.append("custom_instructions", data.customInstructions)
```

This now matches the backend's individual Form parameters.

## Result

- ✅ 422 Validation Error resolved
- ✅ Multipart form data properly parsed
- ✅ File uploads work correctly
- ✅ All form fields accessible in backend
- ✅ No breaking changes to frontend code
