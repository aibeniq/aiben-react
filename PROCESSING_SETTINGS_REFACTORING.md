# Processing Settings Refactoring - Implementation Summary

## Date: November 4, 2025

## Overview

Major refactoring to consolidate document processing settings into a unified interface with per-function overrides.

## Changes Implemented

### Backend Changes

#### 1. Database Schema (✅ Complete)

- **File**: `backend/app/models.py`

  - Added `default_processing_mode` field to User model
  - Created `ProcessingDefaultsUpdate` model for unified updates
  - Updated `UserPublic`, `UserUpdate`, and `UserUpdateMe` models

- **File**: `backend/app/alembic/versions/add_default_processing_mode.py`
  - Migration to add `default_processing_mode` column with default value "vector"

#### 2. API Endpoints (✅ Complete)

- **File**: `backend/app/api/routes/users.py`
  - Added `/me/processing-defaults` endpoint to update all three settings at once
  - Validates search mode ("vector" or "full_scan")
  - Validates PDF parsing mode ("enhanced" or "basic")
  - Updates vision_analysis_enabled, pdf_parsing_preference, and default_processing_mode

### Frontend Changes

#### 1. Components (✅ Complete)

**ProcessingSettingsPopup.tsx** - NEW

- Gear icon button that opens a popup dialog
- Allows users to configure 3 settings per-function:
  1. Search Mode (vector/full_scan)
  2. Vision Analysis (enabled/disabled)
  3. PDF Parsing (enhanced/basic)
- Displays descriptions for each option
- Shows note that settings override defaults

**ProcessingDefaultsSettings.tsx** - NEW

- Unified settings tab component
- Replaces separate Vision Analysis and PDF Parsing tabs
- Includes all 3 processing parameters:
  1. Default Search Mode
  2. Vision Analysis
  3. PDF Parsing
- Auto-saves changes to backend
- Shows comparison information

#### 2. Settings Page (✅ Complete)

- **File**: `frontend/src/routes/_layout/settings.tsx`
  - Replaced two tabs (vision-analysis, pdf-parsing) with one: "processing-defaults"
  - Uses ProcessingDefaultsSettings component

#### 3. Feature Pages (⏳ Partial - Review page updated)

- **File**: `frontend/src/routes/_layout/review.tsx` (✅ Complete)
  - Replaced SearchModeToggle with ProcessingSettingsPopup
  - Initialize processing settings from user defaults
  - Pass settings to backend
- **Still TODO**: Update these pages similarly:
  - `generate.tsx` - ReportGenie
  - `match.tsx` - FormConnect
  - `compare.tsx` - TwinCheck
  - Modal components (ChecklistModal, OutlineModal, TopicListModal, FormTemplateModal)
  - Chatbot components

#### 4. Translations (✅ Complete)

- **File**: `frontend/src/locales/en/common.json`
  - Added `settings.processingDefaults` section with all labels
  - Added `processingSettings` section for popup labels
  - Added "apply" button text

## Still TODO

### 1. Update Backend Routes to Accept Override Parameters

Currently, backend routes accept these parameters:

- `search_mode` (for vector vs full_scan)
- Files are processed based on user's `vision_analysis_enabled` and `pdf_parsing_preference`

**Need to update these routes to accept OPTIONAL override parameters:**

- `backend/app/api/routes/veradoc.py` - processRagChecklist endpoint
- `backend/app/api/routes/reportgenie.py` - generateReport endpoint
- `backend/app/api/routes/formconnect.py` - extractFields endpoint
- `backend/app/api/routes/twincheck.py` - compare endpoint
- `backend/app/api/routes/chatbot.py` - queryDocument endpoint

**Each should accept:**

```python
vision_analysis_override: Optional[bool] = Form(None)
pdf_parsing_override: Optional[str] = Form(None)  # "enhanced" or "basic"
```

**Logic:**

```python
# Use override if provided, otherwise fall back to user's default
vision_enabled = vision_analysis_override if vision_analysis_override is not None else current_user.vision_analysis_enabled
pdf_mode = pdf_parsing_override if pdf_parsing_override else current_user.pdf_parsing_preference
```

### 2. Update Remaining Frontend Pages

Copy the pattern from review.tsx to:

- `frontend/src/routes/_layout/generate.tsx`
- `frontend/src/routes/_layout/match.tsx`
- `frontend/src/routes/_layout/compare.tsx`
- `frontend/src/components/Review/ChecklistModal.tsx`
- `frontend/src/components/Generate/OutlineModal.tsx`
- `frontend/src/components/Compare/TopicListModal.tsx`
- `frontend/src/components/Match/FormTemplateModal.tsx`

**Pattern:**

1. Import ProcessingSettingsPopup and useAuth
2. Replace searchMode state with processingSettings state
3. Initialize from user defaults
4. Replace SearchModeToggle with gear icon + ProcessingSettingsPopup
5. Send all 3 parameters to backend (searchMode, visionAnalysis override, pdfParsing override)

### 3. Update Frontend API Services

- **File**: `frontend/src/client/services.gen.ts`
  - Will be auto-generated when you run: `npm run generate-client`
  - This will add the new `/me/processing-defaults` endpoint
  - Will add `default_processing_mode` to User type

### 4. Run Database Migration

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Add Translations for Other Languages

- Run the translation script to add [TODO] markers for all other language files
- Or manually copy the English translations and mark them for translation

## Testing Checklist

1. ✅ User can update processing defaults in Settings tab
2. ⏳ User can see gear icon on all feature pages
3. ⏳ Clicking gear icon opens popup with current settings
4. ⏳ Changing settings in popup overrides defaults for that operation
5. ⏳ Backend receives correct override parameters
6. ⏳ Vision analysis is enabled/disabled based on user choice
7. ⏳ PDF parsing mode is used based on user choice
8. ⏳ Search mode (vector/full_scan) works correctly

## Benefits

### User Experience

- **Single Place for Defaults**: All processing preferences in one Settings tab
- **Per-Function Overrides**: Can customize settings for individual operations
- **Clear UI**: Gear icon is discoverable, popup is self-explanatory
- **Consistent**: Same pattern across all features

### Code Quality

- **Unified Model**: ProcessingSettings type used everywhere
- **Less Duplication**: One popup component used by all pages
- **Better State Management**: Settings initialized from user defaults
- **Type Safety**: TypeScript enforces correct settings structure

## Migration Path for Users

1. **Existing users**: Will have new `default_processing_mode` set to "vector" (current default)
2. **Vision analysis**: Existing setting preserved
3. **PDF parsing**: Existing setting preserved
4. **First time users see UI**:
   - Settings tab shows new unified "Processing Defaults"
   - Old tabs (Vision Analysis, PDF Parsing) are gone
   - Gear icon appears on all processing pages

## Notes

- The old SearchModeToggle component can be deprecated after all pages are updated
- VisionAnalysisSettings and PdfParsingSettings components are no longer used
- Backend routes maintain backward compatibility (override parameters are optional)
- Default behavior unchanged if user doesn't change settings
