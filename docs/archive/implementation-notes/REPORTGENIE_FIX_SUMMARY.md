# ReportGenie Full Document Scan Fix

## Problem Description

The Generate functionality was failing with "Internal Server Error" when using the "Full Document Scan" toggle. This was caused by sending large sections data as URL query parameters, which exceeds URL length limits when dealing with extensive outlines and full document scans.

## Root Cause

- The backend endpoint `/api/v1/reportgenie/generate` was expecting data via query parameters using `Depends()` with a Pydantic model
- Large sections data (especially with full document scan) were being sent as URL query parameters
- URLs have length limitations (~2048 characters in many browsers), and large outlines exceeded this limit

## Solution Implemented

Updated both backend and frontend to use form data (multipart/form-data) for large payloads, following the working pattern used in the chatbot's Full Document Scan functionality.

### Backend Changes (`backend/app/api/routes/reportgenie.py`)

1. **Added Form import:**

   ```python
   from fastapi import (
       APIRouter,
       Depends,
       HTTPException,
       UploadFile,
       File,
       Form,  # Added this import
       Request as FastAPIRequest,
   )
   ```

2. **Updated endpoint signature:**

   ```python
   @router.post("/generate", response_model=ReportGenieResponse)
   async def generate_report(
       session: SessionDep,
       current_user: CurrentUser,
       knowledge_base_id: str = Form(...),
       sections: str = Form(...),
       outline_id: str = Form(...),
       search_mode: str = Form("vector"),  # Default to vector search
   ):
   ```

3. **Updated function body:**
   - Replaced all `request.knowledge_base_id` with `knowledge_base_id`
   - Replaced all `request.sections` with `sections`
   - Replaced all `request.outline_id` with `outline_id`
   - Updated the LLM interaction logging to use the new parameter names

### Frontend Changes (`frontend/src/client/sdk.gen.ts`)

1. **Updated service method:**
   ```typescript
   public static generateReport(data: ReportgenieGenerateReportData): CancelablePromise<ReportgenieGenerateReportResponse> {
       return __request(OpenAPI, {
           method: 'POST',
           url: '/api/v1/reportgenie/generate',
           formData: {  // Changed from 'query' to 'formData'
               knowledge_base_id: data.knowledgeBaseId,
               sections: data.sections,
               outline_id: data.outlineId,
               search_mode: data.searchMode
           },
           mediaType: 'multipart/form-data',  // Added this
           errors: {
               422: 'Validation Error'
           }
       });
   }
   ```

## Benefits of the Fix

1. **No URL Length Limitations:** Form data is sent in the request body, not as query parameters
2. **Supports Large Payloads:** Can handle extensive outlines and full document scans without size restrictions
3. **Consistent with Existing Patterns:** Uses the same pattern as the working chatbot Full Document Scan functionality
4. **Backwards Compatible:** Maintains the same API interface from the frontend perspective

## Reference Implementation

This fix follows the same pattern used in the chatbot's Full Document Scan functionality:

- Backend: `backend/app/api/routes/chatbot.py` - `query_document` endpoint uses `files: List[UploadFile] = File(None)`
- Frontend: `frontend/src/client/sdk.gen.ts` - `ChatService.queryDocument` uses `formData` and `multipart/form-data`

## Testing

- Backend imports successfully without errors
- Frontend builds successfully with the new service implementation
- The endpoint now accepts form data instead of query parameters, resolving the URL length limitation issue

## Files Modified

1. `backend/app/api/routes/reportgenie.py`
2. `frontend/src/client/sdk.gen.ts`

## Next Steps

- Test the end-to-end functionality with large outlines and full document scans
- Verify that both vector search and full text scan modes work correctly
- Monitor for any additional performance improvements needed
