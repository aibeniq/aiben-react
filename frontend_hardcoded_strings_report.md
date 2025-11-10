# Frontend Hard-coded English Strings Report

This report contains all hard-coded English strings found in the frontend codebase that should be translated. The strings are organized by category and include file paths and line numbers for easy reference.

## Summary

- **Total hard-coded strings found**: 50+
- **Categories**: Toast messages, error messages, button defaults, console messages, and UI text
- **Impact**: These strings will not be translated when users switch languages

## 1. Toast Messages (showErrorToast/showSuccessToast)

### ChecklistModal.tsx

- **File**: `frontend/src/components/Review/ChecklistModal.tsx`
- **Line 118**: `showErrorToast(firstError)` - Variable error message
- **Line 190**: `showErrorToast("No questions to copy")`
- **Line 199**: `showErrorToast("Failed to copy questions to clipboard")`
- **Line 205**: `showErrorToast("Please select a knowledge base first to optimize the checklist.")`
- **Line 210**: `showErrorToast("Please add some questions to the checklist before optimizing.")`
- **Line 225**: `showSuccessToast(`Applied ${optimizedQuestions.length} optimized questions`)`
- **Line 230**: `showErrorToast("Please enter a description")`
- **Line 235**: `showErrorToast("Description must be at least 10 characters")`
- **Line 327**: `showSuccessToast(successMessage)` - Variable success message
- **Line 329**: `showErrorToast("No questions were suggested. Please try a different description.")`
- **Line 333**: `showErrorToast(`Failed to suggest questions: ${error.message || "Unknown error"}`)`

### ChatPanel.tsx

- **File**: `frontend/src/components/Chat/ChatPanel.tsx`
- **Line 127**: `showToast({ title: "Error sending message", status: "error" })`

### FormTemplateModal.tsx

- **File**: `frontend/src/components/Match/FormTemplateModal.tsx`
- **Line 282**: `showErrorToast(`Failed to suggest fields: ${error.message || "Unknown error"}`)`

### Model Selection Page

- **File**: `frontend/src/routes/_layout/model-selection.tsx`
- **Line 159**: `showErrorToast(`Error adding model: ${error.message}`)`
- **Line 173**: `showErrorToast(t("toast.ollamaNotAvailable"))` - Already translated
- **Line 209**: `showErrorToast(t("toast.llmAddFailed", { error: error.message }))` - Already translated
- **Line 223**: `showErrorToast(t("toast.llmDeleteFailed", { error: error.message }))` - Already translated
- **Line 238**: `showErrorToast(t("toast.llmDeleteFailed", { error: error.message }))` - Already translated
- **Line 250**: `showErrorToast(`Error updating model: ${error.message}`)`
- **Line 300**: `showErrorToast("Please fill in all required fields")`
- **Line 306**: `showErrorToast(`Error validating model: ${error.message}`)`
- **Line 799**: `showErrorToast(`Error adding model: ${error.message}`)`
- **Line 842**: `showErrorToast(`Error updating default model: ${error.message}`)`

### Match Page

- **File**: `frontend/src/routes/_layout/match.tsx`
- **Line 278**: `showSuccessToast(`Failed to download CSV: ${err.message || "Unknown error"}`)`

## 2. Error Messages and Console Logs

### Review Page

- **File**: `frontend/src/routes/_layout/review.tsx`
- **Line 301**: `console.error("Failed to copy report:", err)`
- **Line 396**: `console.error("Failed to download report:", err)`
- **Line 398**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 405**: `error: err.message || "Unknown error"`
- **Line 462**: `console.error("Failed to download CSV:", err)`

### Match Page

- **File**: `frontend/src/routes/_layout/match.tsx`
- **Line 149**: `console.error("Failed to copy results:", err)`
- **Line 207**: `console.error("Failed to download results:", err)`
- **Line 209**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 216**: `error: err.message || "Unknown error"`
- **Line 271**: `console.error("Failed to download CSV:", err)`
- **Line 273**: `message: err instanceof Error ? err.message : "Unknown error"`

### Generate Page

- **File**: `frontend/src/routes/_layout/generate.tsx`
- **Line 210**: `console.error("Failed to copy document:", err)`
- **Line 270**: `console.error("Failed to download document:", err)`
- **Line 272**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 279**: `error: err.message || "Unknown error"`
- **Line 326**: `console.error("Failed to download CSV:", err)`
- **Line 329**: `error: err.message || "Unknown error"`

### Compare Page

- **File**: `frontend/src/routes/_layout/compare.tsx`
- **Line 162**: `console.error("Failed to copy report:", err)`
- **Line 231**: `console.error("Failed to download report:", err)`
- **Line 233**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 240**: `error: err.message || "Unknown error"`
- **Line 303**: `console.error("Failed to download CSV:", err)`
- **Line 305**: `message: err instanceof Error ? err.message : "Unknown error"`

### Archive Page

- **File**: `frontend/src/routes/_layout/archive.tsx`
- **Line 95**: `console.error("Failed to copy report:", err)`
- **Line 96**: `const errorMessage = err instanceof Error ? err.message : "Unknown error"`
- **Line 125**: `console.error("Failed to fetch full QA pairs for DOCX:", error)`
- **Line 243**: `console.error("Failed to download report:", err)`
- **Line 245**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 250**: `const errorMessage = err instanceof Error ? err.message : "Unknown error"`
- **Line 305**: `console.error("Failed to fetch full QA pairs for CSV:", error)`
- **Line 405**: `message: err instanceof Error ? err.message : "Unknown error"`
- **Line 410**: `const errorMessage = err instanceof Error ? err.message : "Unknown error"`

### Model Selection Page

- **File**: `frontend/src/routes/_layout/model-selection.tsx`
- **Line 108**: `console.error("Failed to fetch available providers:", error)`
- **Line 696**: `console.error("Failed to fetch available providers:", error)`

## 3. Button Default Text

### CancelButton Component

- **File**: `frontend/src/components/ui/cancel-button.tsx`
- **Line 19**: `children = "Cancel"` - Default button text

## 4. UI Text and Messages

### ChecklistModal.tsx

- **File**: `frontend/src/components/Review/ChecklistModal.tsx`
- **Line 504**: `"No Knowledge Bases available. Create one first to use this feature."`

### Utils Files

- **File**: `frontend/src/utils.ts`
- **Line 56**: `showErrorToast(errorMessage)` - Variable error message

## 5. Test Files (May not need translation but included for completeness)

### User Tests

- **File**: `frontend/tests/user-settings.spec.ts`
- **Lines**: Multiple references to button names like "Save", "Edit", "Cancel" in test assertions

## 6. Migration Scripts (Reference only)

### Migration Scripts

- **File**: `migration_scripts/add_missing_keys.js`
- **Lines**: Contains translation key definitions (not hard-coded UI text)

## Recommendations for Translation

### High Priority (User-Facing Messages)

1. All `showErrorToast` and `showSuccessToast` messages should be moved to translation keys
2. Error messages like "Unknown error", "Failed to...", "Please..." should be translated
3. Button default text should use translation keys

### Medium Priority (Developer Messages)

1. Console.error messages could be translated for better developer experience in non-English environments
2. Test file strings are less critical but could be updated for consistency

### Implementation Approach

1. Add new translation keys to `frontend/src/locales/*/common.json` files
2. Replace hard-coded strings with `t("new.translation.key")` calls
3. Update all language files with appropriate translations
4. Test that translations work correctly in different languages

### Example Translation Keys to Add

```json
{
  "errors": {
    "noQuestionsToCopy": "No questions to copy",
    "failedToCopyQuestions": "Failed to copy questions to clipboard",
    "selectKnowledgeBaseFirst": "Please select a knowledge base first to optimize the checklist.",
    "addQuestionsBeforeOptimizing": "Please add some questions to the checklist before optimizing.",
    "enterDescription": "Please enter a description",
    "descriptionTooShort": "Description must be at least 10 characters",
    "noQuestionsSuggested": "No questions were suggested. Please try a different description.",
    "failedToSuggestQuestions": "Failed to suggest questions: {{error}}",
    "unknownError": "Unknown error",
    "noKnowledgeBasesAvailable": "No Knowledge Bases available. Create one first to use this feature.",
    "failedToDownloadCsv": "Failed to download CSV: {{error}}"
  },
  "success": {
    "questionsCopied": "Questions copied to clipboard",
    "optimizedQuestionsApplied": "Applied {{count}} optimized questions"
  }
}
```

This report provides a comprehensive overview of all hard-coded English strings that need translation. The most critical ones are the toast messages that users see directly in the UI.</content>
<parameter name="filePath">c:\miniconda\aibeniq-react\frontend_hardcoded_strings_report.md
