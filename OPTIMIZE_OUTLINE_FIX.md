# Fix for Optimize Outline Server Error

## Problem

The Optimize Outline functionality was sending a massive amount of text as URL query parameters, causing the server to return 500 errors due to URL length limits. The error logs showed URL-encoded sections data being sent as query parameters instead of form data.

## Root Cause

1. **Parameter naming mismatch**: The frontend was sending parameters with snake_case names (`knowledge_base_id`, `outline_id`, `custom_instructions`) but the TypeScript SDK expected camelCase names (`knowledgeBaseId`, `outlineId`, `customInstructions`).

2. **Sections data serialization**: The `sections` parameter (which contains large arrays of section objects) needed to be JSON stringified before being sent as form data.

## Solution

### Frontend Changes (OptimizeOutlineModal.tsx)

Fixed the parameter names in the ReportgenieService.optimizeOutline() call:

```typescript
// Before (incorrect snake_case):
const result = await ReportgenieService.optimizeOutline({
  formData: { files: [selectedFile] },
  knowledge_base_id: knowledgeBaseId, // ❌ Wrong
  outline_id: outlineId, // ❌ Wrong
  sections: currentSections,
  custom_instructions: customInstructions.trim() || undefined, // ❌ Wrong
})

// After (correct camelCase):
const result = await ReportgenieService.optimizeOutline({
  formData: { files: [selectedFile] },
  knowledgeBaseId: knowledgeBaseId, // ✅ Correct
  outlineId: outlineId, // ✅ Correct
  sections: currentSections,
  customInstructions: customInstructions.trim() || undefined, // ✅ Correct
})
```

### SDK Changes (sdk.gen.ts)

Fixed the sections parameter to be properly JSON stringified:

```typescript
// Before:
formData.append("sections", data.sections)

// After:
formData.append("sections", JSON.stringify(data.sections))
```

## Verification

- ✅ TypeScript compilation passes with no errors
- ✅ All parameters are sent as form data (not query parameters)
- ✅ Large sections data is properly serialized as JSON string
- ✅ Backend correctly parses the JSON string with `json.loads(request_data.sections)`

## Result

The Optimize Outline feature now properly sends all data via form fields in a multipart/form-data request, avoiding URL length limits and server errors. The large sections data is efficiently transferred as a JSON string in the request body rather than being URL-encoded in query parameters.
