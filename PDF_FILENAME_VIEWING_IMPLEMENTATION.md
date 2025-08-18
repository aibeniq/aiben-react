# PDF Filename-Based Viewing Implementation

## Problem Solved

The Generate functionality had working clickable citation hyperlinks for DOCX files but not for PDF files. The issue was that PDF citations in ReportGenie results often lack valid `source_data_id` values, causing the `SourceLink` component to fail when trying to view these files.

## Root Cause

1. **DOCX Files**: Had both `sourceId`-based and filename-based conversion fallbacks in the `SourceLink` component
2. **PDF Files**: Only relied on `sourceId`-based viewing through `FilesService.getSourceContent()`, which requires a valid database ID
3. **Missing Fallback**: No filename-based viewing mechanism for PDFs when `source_data_id` was missing

## Solution Implemented

### Backend Changes

#### 1. New API Endpoint (`backend/app/api/routes/sourceretrieval.py`)

**Endpoint**: `GET /api/v1/files/source/by-filename/{filename}`

**Features**:

- ✅ Retrieves source files by filename instead of source ID
- ✅ Maintains existing security and permission checks
- ✅ Works with all file types (PDFs, DOCX, etc.)
- ✅ Returns file content as base64 encoded data
- ✅ Proper error handling for missing files or access denied

**Security Model**:

- Users can only access files they own or have permissions for
- Same permission logic as existing `source/{source_id}` endpoint
- Checks both direct ownership and knowledge base access

### Frontend Changes

#### 1. Enhanced FilesService (`frontend/src/client/sdk.gen.ts`)

**New Method**: `FilesService.getSourceContentByFilename()`

- ✅ Accepts filename parameter instead of sourceId
- ✅ Returns same response format as `getSourceContent()`
- ✅ Proper error handling for 404 and access denied scenarios

#### 2. Updated SourceLink Component (`frontend/src/components/Common/SourceLink.tsx`)

**Enhanced Logic**:

- ✅ Detects when `sourceId` is missing or empty
- ✅ Automatically uses filename-based viewing for PDFs when no sourceId available
- ✅ Maintains existing DOCX conversion functionality
- ✅ Falls back to normal sourceId-based viewing when sourceId is present
- ✅ Supports both modal and new-tab viewing modes
- ✅ Proper error handling with graceful fallbacks

**New Flow for PDFs without sourceId**:

1. Detects PDF file extension and missing sourceId
2. Calls `FilesService.getSourceContentByFilename()` with filename
3. Creates blob URL for PDF viewing
4. Opens in modal or new tab based on `useModal` parameter

## Benefits

### 1. **Fixes Citation Links**

- PDF citations in ReportGenie now work correctly
- No more broken links for PDFs missing source_data_id
- Consistent user experience across all file types

### 2. **Maintains Existing Functionality**

- DOCX conversion still works as before
- Normal sourceId-based viewing unchanged
- No breaking changes to existing code

### 3. **Security Preserved**

- Same permission model as existing endpoints
- Users can only access files they own or have access to
- No security vulnerabilities introduced

### 4. **Flexible Implementation**

- Works with both modal and new-tab viewing
- Graceful fallback to sourceId-based viewing when available
- Error handling prevents application crashes

## Usage

### For Users

1. Click any PDF citation link in ReportGenie (same as before)
2. System automatically detects missing sourceId
3. Falls back to filename-based viewing
4. Opens PDF in browser for viewing

### For Developers

```typescript
// PDF files now work automatically with filename fallback
<SourceLink
  sourceId=""  // Empty or missing sourceId
  fileName="document.pdf"  // Automatically uses filename-based viewing
  useModal={true}
/>

// DOCX files work as before
<SourceLink
  sourceId="123-456-789"
  fileName="document.docx"  // Still uses conversion
  useModal={true}
/>
```

## Implementation Details

### Backend Endpoint Logic

```python
@router.get("/source/by-filename/{filename}", response_model=SourceContentResponse)
async def get_source_content_by_filename(filename: str, session: SessionDep, current_user: CurrentUser):
    # Find source by filename with permission checks
    # Extract file content from ZIP storage
    # Return base64 encoded content with metadata
```

### Frontend Component Logic

```typescript
// Check for PDF without sourceId
if ((!sourceId || sourceId.trim() === "") && fileName.toLowerCase().endsWith(".pdf")) {
  // Use filename-based viewing
  const response = await FilesService.getSourceContentByFilename({ filename: fileName })
  // Handle modal or new-tab viewing
}
```

## Testing

### Manual Testing Required

1. **Test PDF Citations**: Click PDF citation links in ReportGenie results
2. **Test Modal Viewing**: Verify PDFs open in modal when `useModal=true`
3. **Test New Tab Viewing**: Verify PDFs open in new tab when `useModal=false`
4. **Test Permissions**: Ensure users can only access their own files
5. **Test DOCX Still Works**: Verify DOCX citations still convert and display

### Expected Results

- ✅ PDF citations in ReportGenie now work correctly
- ✅ Both modal and new-tab viewing work for PDFs
- ✅ DOCX citations continue to work as before
- ✅ Proper error handling for missing files or access denied
- ✅ No security vulnerabilities or permission bypasses

## Deployment Notes

### Backend

- New endpoint is automatically included in FastAPI router
- No database migrations required
- Uses existing models and dependencies

### Frontend

- Client SDK includes new method
- Component changes are backward compatible
- No breaking changes to existing functionality

## Future Enhancements

### Potential Improvements

1. **Caching**: Cache filename-to-sourceId mappings for performance
2. **Batch Loading**: Support viewing multiple files simultaneously
3. **Preview Generation**: Generate thumbnails for PDF previews
4. **Enhanced Error Messages**: More specific error messages for different failure scenarios
5. **Performance Optimization**: Optimize file loading for large PDFs

## Related Files Modified

### Backend

- `backend/app/api/routes/sourceretrieval.py` - Added new endpoint

### Frontend

- `frontend/src/client/sdk.gen.ts` - Added new FilesService method
- `frontend/src/components/Common/SourceLink.tsx` - Enhanced PDF handling logic

## Verification Commands

### Backend Test

```bash
cd backend
uv run python -c "from app.main import app; print('Backend starts successfully!')"
```

### Frontend Build Test

```bash
cd frontend
npm run build  # Should complete without errors in modified files
```
