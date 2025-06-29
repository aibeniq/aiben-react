# Fix Implementation: Optimize Outline Validation Error

## Changes Made

### 1. Backend Changes (reportgenie.py)

**Reverted to VeraDoc Pattern:**

- Changed from individual `Form(...)` parameters back to `request_data: OptimizeOutlineRequest = Depends()`
- Updated function body to use `request_data.knowledge_base_id` instead of `knowledge_base_id`
- Updated sections parsing to use `request_data.sections` instead of `sections`
- Removed unused `Form` import from FastAPI imports

**Before:**

```python
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

**After:**

```python
async def optimize_outline(
    session: SessionDep,
    current_user: CurrentUser,
    request_data: OptimizeOutlineRequest = Depends(),
    files: List[UploadFile] = File(...),
    request: FastAPIRequest = None,
):
```

### 2. Frontend SDK Changes (sdk.gen.ts)

**Aligned with VeraDoc Pattern:**

- Removed manual FormData construction
- Use query parameters for non-file data (like the working checklist optimization)
- Use formData property for file uploads
- Matches the exact pattern used by `optimizeChecklist`

**Before:**

```typescript
public static optimizeOutline(data: ReportgenieOptimizeOutlineData): CancelablePromise<ReportgenieOptimizeOutlineResponse> {
    const formData = new FormData();
    // Manual FormData construction...
    return __request(OpenAPI, {
        method: 'POST',
        url: '/api/v1/reportgenie/optimize-outline',
        formData: formData as any,
        mediaType: 'multipart/form-data',
    });
}
```

**After:**

```typescript
public static optimizeOutline(data: ReportgenieOptimizeOutlineData): CancelablePromise<ReportgenieOptimizeOutlineResponse> {
    return __request(OpenAPI, {
        method: 'POST',
        url: '/api/v1/reportgenie/optimize-outline',
        query: {
            knowledge_base_id: data.knowledgeBaseId,
            outline_id: data.outlineId,
            sections: data.sections,
            custom_instructions: data.customInstructions
        },
        formData: data.formData,
        mediaType: 'multipart/form-data',
    });
}
```

## Why This Works

1. **Proven Pattern**: This is the exact same approach used by the working VeraDoc `optimizeChecklist` functionality
2. **FastAPI Compatibility**: `Depends()` with Pydantic models correctly handles query parameters + file uploads
3. **Separation of Concerns**: Query parameters for metadata, formData for files
4. **Automatic Validation**: FastAPI automatically validates and converts query parameters to the Pydantic model

## Expected Result

The optimize outline functionality should now work without validation errors:

- ✅ No more "Field required" errors for `knowledge_base_id`, `outline_id`, `sections`, `files`
- ✅ Proper handling of multipart form data with files
- ✅ Consistent behavior with other optimization endpoints

## Status

**READY FOR TESTING** - The implementation now matches the working VeraDoc pattern.
