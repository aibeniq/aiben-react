### Summary of Form Fields Generation Fix

**Problem**: Getting 404 error when trying to use a Knowledge Base to generate form fields.

**Root Cause**: The frontend was making API calls to `http://localhost:5173/api/v1/formconnect/generate-fields-json` (frontend dev server) instead of `http://localhost:8000/api/v1/formconnect/generate-fields-json` (backend API server) due to using a relative URL path.

**Solution Applied**:

1. **Fixed API URL**: Modified the fetch call to use the proper base URL from environment variable
2. **Added authentication headers**: Ensured API calls include the proper Authorization header

**Code Changes**:

- Modified `frontend/src/components/Match/FormTemplateModal.tsx` to:

  ```javascript
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
  const apiUrl = `${baseUrl}/api/v1/formconnect/generate-fields-json`

  const token = localStorage.getItem("access_token")
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  ```

**Backend Status**:

- ✅ Backend endpoints `/api/v1/formconnect/generate-fields` and `/generate-fields-json` exist
- ✅ Backend embedding model/provider logic is correctly implemented (same fix as Generate Outline)
- ✅ Backend uses proper fallback logic for knowledge base embedding models
- ✅ Backend imports are correct and use named parameters for `load_embeddings_model`

**Testing Done**:

- ✅ Verified backend server is running and responding (status 200)
- ✅ Verified API endpoint path is correct in backend routing
- ✅ Verified frontend now constructs proper full URL using environment variable

**Expected Result**:
The form field generation should now work properly for both description-only and knowledge base-assisted generation, with API calls going to the correct backend server.

**Files Modified**:

- `frontend/src/components/Match/FormTemplateModal.tsx` - Fixed API URL construction and added authentication headers
