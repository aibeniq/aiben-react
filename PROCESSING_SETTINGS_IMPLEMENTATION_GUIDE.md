# Processing Settings Refactoring - Step-by-Step Implementation Guide

## Quick Reference: Changes Made So Far

✅ Backend database schema updated
✅ Backend API endpoint created  
✅ Frontend ProcessingSettingsPopup component created
✅ Frontend ProcessingDefaultsSettings component created
✅ Settings page updated
✅ Review page updated
✅ English translations added
✅ Database migration run
✅ Client SDK regenerated

## Remaining Steps

### Step 1: Update Generate Page

**File**: `frontend/src/routes/_layout/generate.tsx`

1. **Import changes** (lines 1-10):

```typescript
// Replace:
import SearchModeToggle from "@/components/Common/SearchModeToggle"

// With:
import ProcessingSettingsPopup, {
  type ProcessingSettings,
} from "@/components/Common/ProcessingSettingsPopup"
import useAuth from "@/hooks/useAuth"
```

2. **Component start** (line ~43):

```typescript
const ReportGenie = () => {
  const { t, i18n } = useTranslation()
  const { user } = useAuth()  // ADD THIS LINE
```

3. **Replace searchMode state** (line ~82-84):

```typescript
// Replace:
const [searchMode, setSearchMode] = useState<"vector" | "full_scan">(
  generateInputs?.searchMode || "vector",
)

// With:
const [processingSettings, setProcessingSettings] = useState<ProcessingSettings>({
  searchMode:
    (user?.default_processing_mode as "vector" | "full_scan") ||
    generateInputs?.searchMode ||
    "vector",
  visionAnalysis: user?.vision_analysis_enabled || false,
  pdfParsing: (user?.pdf_parsing_preference as "enhanced" | "basic") || "basic",
})
```

4. **Update useEffect dependencies** (~line 100):

```typescript
// Replace searchMode with processingSettings.searchMode in:
// - setGenerateInputs() call
// - useEffect dependency array
```

5. **Update handleClearResults** (~line 135):

```typescript
// Replace:
setSearchMode("vector")

// With:
setProcessingSettings({
  searchMode: (user?.default_processing_mode as "vector" | "full_scan") || "vector",
  visionAnalysis: user?.vision_analysis_enabled || false,
  pdfParsing: (user?.pdf_parsing_preference as "enhanced" | "basic") || "basic",
})
```

6. **Replace SearchModeToggle in UI** (~line 570):

```tsx
// Replace:
<SearchModeToggle
  searchMode={searchMode}
  onSearchModeChange={setSearchMode}
  helpKey="searchMode"
/>

// With:
<Box width="100%" mt={4}>
  <HStack align="center">
    <Text fontSize="sm" fontWeight="medium">
      {t("processingSettings.title")}
    </Text>
    <ProcessingSettingsPopup
      settings={processingSettings}
      onSettingsChange={setProcessingSettings}
      disabled={loading}
    />
    <HelpTooltip helpKey="searchMode" />
  </HStack>
  <Text fontSize="xs" color="gray.500" mt={1}>
    {t("processingSettings.configure")}
  </Text>
</Box>
```

7. **Update API call** (~line 450):

```typescript
// Update the search_mode parameter to:
search_mode: processingSettings.searchMode
```

### Step 2: Update Match Page

**File**: `frontend/src/routes/_layout/match.tsx`

Follow the same pattern as Generate page above.

### Step 3: Update Compare Page

**File**: `frontend/src/routes/_layout/compare.tsx` (if it has search mode toggle)

Follow the same pattern.

### Step 4: Update Modal Components

**Files**:

- `frontend/src/components/Review/ChecklistModal.tsx`
- `frontend/src/components/Generate/OutlineModal.tsx`
- `frontend/src/components/Compare/TopicListModal.tsx`
- `frontend/src/components/Match/FormTemplateModal.tsx`

For each modal:

1. Import `ProcessingSettingsPopup` and `useAuth`
2. Replace `searchMode` state with `processingSettings`
3. Initialize from user defaults
4. Replace `SearchModeToggle` with gear icon + popup
5. Update API calls to send `processingSettings.searchMode`

### Step 5: Update Backend Routes (CRITICAL)

Currently backend routes only accept `search_mode`. They need to also accept optional override parameters for vision analysis and PDF parsing.

#### 5a. Update VeraDoc Route

**File**: `backend/app/api/routes/veradoc.py`

Find the `process_rag_checklist` function (around line 957):

```python
@router.post("/process-rag", response_model=VeraDocResponse)
async def process_rag_checklist(
    session: SessionDep,
    current_user: CurrentUser,
    questions: Optional[str] = Form(None),
    knowledge_base_id: str = Form(...),
    files: List[UploadFile] = File(...),
    custom_instructions: Optional[str] = Form(None),
    search_mode: str = Form("vector"),
    vision_analysis_override: Optional[bool] = Form(None),  # ADD THIS
    pdf_parsing_override: Optional[str] = Form(None),       # ADD THIS
    task_id: Optional[str] = Form(None),
    request: FastAPIRequest = None,
):
```

Then in the function body, before processing documents:

```python
# Determine vision analysis setting (override takes precedence)
vision_enabled = (
    vision_analysis_override
    if vision_analysis_override is not None
    else current_user.vision_analysis_enabled
)

# Determine PDF parsing mode (override takes precedence)
pdf_parsing_mode = (
    pdf_parsing_override
    if pdf_parsing_override is not None
    else current_user.pdf_parsing_preference
)

print(f"Vision analysis: {vision_enabled} (override: {vision_analysis_override}, user default: {current_user.vision_analysis_enabled})")
print(f"PDF parsing mode: {pdf_parsing_mode} (override: {pdf_parsing_override}, user default: {current_user.pdf_parsing_preference})")
```

Then pass these to document processing functions instead of using `current_user.vision_analysis_enabled` and `current_user.pdf_parsing_preference`.

#### 5b. Update ReportGenie Route

**File**: `backend/app/api/routes/reportgenie.py`

Similar changes around line 355 in the `generate_report` function.

#### 5c. Update FormConnect Route

**File**: `backend/app/api/routes/formconnect.py`

Similar changes around line 1245 in the extract fields function.

#### 5d. Update TwinCheck Route

**File**: `backend/app/api/routes/twincheck.py`

Similar changes in the compare endpoint.

#### 5e. Update Chatbot Route

**File**: `backend/app/api/routes/chatbot.py`

Similar changes in the query endpoint.

### Step 6: Update Frontend API Calls

After adding the override parameters to backend routes, update frontend to send them:

**In Review Page** (~line 540):

```typescript
const promise = VeradocService.processRagChecklist({
  formData: {
    questions: data.questions,
    knowledge_base_id: data.knowledgeBaseId,
    custom_instructions: data.customInstructions,
    search_mode: data.searchMode,
    vision_analysis_override: processingSettings.visionAnalysis, // ADD
    pdf_parsing_override: processingSettings.pdfParsing, // ADD
    task_id: newTaskId,
    files: data.files,
  },
})
```

Repeat for Generate, Match, Compare pages.

### Step 7: Add Translations for Other Languages

You have two options:

#### Option A: Run Translation Script

```bash
python add_remaining_translations.py
```

#### Option B: Manual Copy

Copy the English translations from `frontend/src/locales/en/common.json` sections:

- `settings.processingDefaults`
- `processingSettings`

To all other language files in `frontend/src/locales/*/common.json`, prefixing values with `[TODO: ...]`

### Step 8: Update Chatbot Components

**Files**:

- `frontend/src/components/Chatbot/ChatbotMain.tsx`
- `frontend/src/components/Chatbot/ChatbotPanel.tsx`
- `frontend/src/components/Chat/ChatPanel.tsx`

These use `full_text` instead of `full_scan` for search mode. You may need to:

1. Keep the internal value as `full_text`
2. Convert to `full_scan` when showing in the popup
3. Convert back to `full_text` when sending to backend

OR update the backend chatbot route to use `full_scan` for consistency.

## Testing Steps

### 1. Test Settings Page

1. Navigate to Settings → Processing Defaults
2. Change each setting
3. Verify they save correctly
4. Refresh page and verify settings persist

### 2. Test Review Page

1. Click gear icon
2. Verify popup shows current user defaults
3. Change settings
4. Process documents
5. Verify backend logs show override values

### 3. Test Other Pages

Repeat step 2 for Generate, Match, Compare, modals

### 4. Test Default Behavior

1. Don't click gear icon
2. Process documents
3. Verify user's default settings are used

## Common Issues & Solutions

### Issue: TypeScript errors about `default_processing_mode`

**Solution**: Run `npm run generate-client` to regenerate SDK

### Issue: Database column doesn't exist

**Solution**: Run `alembic upgrade head` in backend

### Issue: Popup doesn't show user defaults

**Solution**: Check that `useAuth()` hook is imported and user object is passed to initialize state

### Issue: Backend doesn't receive override parameters

**Solution**: Check that FormData includes the new fields and backend route accepts them

## Rollback Plan

If you need to rollback:

1. **Database**: Run `alembic downgrade -1`
2. **Frontend**: Restore old files from git
3. **Backend**: Restore old routes from git

## Performance Considerations

- Processing settings popup is lightweight (renders on demand)
- No impact on existing API calls (override parameters are optional)
- Settings tab makes one API call per change (could batch if needed)

## Future Enhancements

1. **Preset Profiles**: Allow users to save multiple preset profiles
2. **Knowledge Base Defaults**: Different defaults per knowledge base
3. **Smart Suggestions**: Recommend settings based on document type
4. **Usage Analytics**: Track which settings combinations are most popular
