# Per-User PyMuPDF4LLM Advanced Parsing Setting - Implementation Plan

## 📋 Overview

This document describes the planned implementation for adding a per-user setting to control whether PyMuPDF4LLM advanced parsing is enabled for PDF document processing. This feature mirrors the recently implemented per-user vision analysis setting and addresses performance vs. quality trade-offs for different user needs.

**Date**: October 29, 2025  
**Status**: Planning Phase - Code Implementation Pending  
**Related Feature**: Vision Analysis Setting (recently implemented)

---

## 🎯 Problem Statement

Currently, PyMuPDF4LLM advanced parsing is controlled **globally** via the `PDF_PARSING_MODE` environment variable setting, which applies the same behavior to all users.

### Current System Behavior

**Configuration** (`backend/app/core/config.py`):

```python
PDF_PARSING_MODE: str = Field(
    default="enhanced",  # Global default
    description="PDF parsing mode: 'auto', 'enhanced', 'basic'"
)
```

**Modes Available**:

- `auto`: Fast table detection, uses PyMuPDF4LLM only if tables detected (intelligent)
- `enhanced`: Always uses PyMuPDF4LLM for all PDFs (best quality, slowest)
- `basic`: Always uses pypdf only (fastest, may miss table structure)

### Pain Points

- **No per-user control** - all users get the same parsing behavior
- **One-size-fits-all approach** - can't customize for different user workflows
- **Performance vs. Quality trade-off** applies to everyone equally
- **Cost implications** - PyMuPDF4LLM processing can be slower and more resource-intensive
- **Different use cases** - some users need table accuracy, others need speed

### Use Case Examples

**User A: Financial Analyst**

- Processes PDFs with complex financial tables daily
- Needs accurate table extraction (PyMuPDF4LLM)
- Quality more important than speed
- Should use: `enhanced` mode

**User B: Legal Researcher**

- Processes text-heavy legal documents
- Rarely has tables, needs fast processing
- Speed more important than advanced parsing
- Should use: `basic` mode

**User C: General Business User**

- Mix of document types
- Wants intelligent detection
- Should use: `auto` mode

---

## 💡 Proposed Solution

Add a **per-user setting** called `pdf_parsing_preference` that works similarly to the existing `vision_analysis_enabled` setting, giving users control over their PDF parsing behavior.

### Key Principles

1. **User Control**: Users explicitly choose their preferred parsing mode
2. **Default Behavior**: New users will default to `"auto"` (intelligent detection)
3. **Consistent Application**: Setting applies across all features (Knowledge Bases, Chatbot, VeraDoc, FormConnect, TwinCheck)
4. **Clear UI**: Settings page clearly explains the trade-offs
5. **Backward Compatible**: Existing global setting preserved as fallback
6. **Mirrors Vision Setting**: Uses same UX patterns as vision analysis setting

---

## 🏗️ Implementation Details

### 1. Database Changes

#### User Model Update

**File**: `backend/app/models.py`

Add new field to `User` model:

```python
class User(UserBase, table=True):
    # ... existing fields ...
    preferred_language: str = Field(default="en", max_length=10)
    vision_analysis_enabled: bool = Field(default=False)

    # NEW FIELD
    pdf_parsing_preference: str = Field(
        default="auto",  # Intelligent default
        max_length=20,
        description="PDF parsing mode preference: 'auto', 'enhanced', or 'basic'"
    )
```

#### Migration Script

**File**: `backend/app/alembic/versions/add_pdf_parsing_preference.py`

```python
"""Add pdf_parsing_preference to user

Revision ID: add_pdf_parsing_preference
Revises: <latest_revision>
Create Date: 2025-10-29

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "pdf_parsing_preference",
            sa.String(length=20),
            nullable=False,
            server_default="auto",  # Intelligent default
        ),
    )

def downgrade():
    op.drop_column("user", "pdf_parsing_preference")
```

---

### 2. Backend API Changes

#### Update User Models

**File**: `backend/app/models.py`

```python
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)
    preferred_language: str | None = Field(default=None, max_length=10)
    vision_analysis_enabled: bool | None = None
    pdf_parsing_preference: str | None = Field(default=None, max_length=20)  # NEW

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    preferred_language: str | None = Field(default=None, max_length=10)
    vision_analysis_enabled: bool | None = None
    pdf_parsing_preference: str | None = Field(default=None, max_length=20)  # NEW

class UserPublic(UserBase):
    id: uuid.UUID
    status: UserStatus
    registration_date: datetime
    approved_date: datetime | None
    preferred_language: str
    vision_analysis_enabled: bool
    pdf_parsing_preference: str  # NEW

class PdfParsingPreferenceUpdate(SQLModel):
    """Dedicated update model for PDF parsing preference."""
    pdf_parsing_preference: str = Field(
        max_length=20,
        description="PDF parsing mode: 'auto', 'enhanced', or 'basic'"
    )
```

#### Add API Endpoint

**File**: `backend/app/api/routes/users.py`

```python
@router.put("/me/pdf-parsing-preference", response_model=UserPublic)
def update_pdf_parsing_preference(
    parsing_update: PdfParsingPreferenceUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update current user's PDF parsing preference."""

    # Validate mode
    valid_modes = ["auto", "enhanced", "basic"]
    if parsing_update.pdf_parsing_preference not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parsing mode. Must be one of: {', '.join(valid_modes)}"
        )

    user = session.get(User, current_user.id)
    user.pdf_parsing_preference = parsing_update.pdf_parsing_preference
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

---

### 3. Document Utils Enhancement

#### Update Extraction Functions

**File**: `backend/app/services/document_utils.py`

**Current Implementation**:

```python
def extract_text_from_file_unified(
    file_content: bytes, filename: str, pdf_parsing_mode: str = None
) -> str:
    """
    Args:
        pdf_parsing_mode: PDF parsing mode ('auto', 'enhanced', 'basic').
                         If None, uses settings.PDF_PARSING_MODE
    """
    # ...
    mode = (
        pdf_parsing_mode
        if pdf_parsing_mode is not None
        else settings.PDF_PARSING_MODE
    )
```

**New Implementation**:

```python
def extract_text_from_file_unified(
    file_content: bytes,
    filename: str,
    pdf_parsing_mode: str = None,
    current_user = None  # NEW parameter
) -> str:
    """
    Unified file text extraction function.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file
        pdf_parsing_mode: PDF parsing mode ('auto', 'enhanced', 'basic').
                         Priority order:
                         1. Explicit pdf_parsing_mode parameter
                         2. User's preference (current_user.pdf_parsing_preference)
                         3. Global setting (settings.PDF_PARSING_MODE)
        current_user: Current user object (optional)

    Returns:
        Extracted text content as string
    """
    # Determine file type from extension
    file_ext = Path(filename).suffix.lower()

    if file_ext == ".pdf":
        from app.services.pdf_utils import extract_text_from_pdf_bytes
        from app.core.config import settings

        # Priority order for mode selection
        if pdf_parsing_mode is not None:
            # Explicit parameter takes highest priority
            mode = pdf_parsing_mode
        elif current_user is not None:
            # User preference takes second priority
            mode = getattr(current_user, "pdf_parsing_preference", settings.PDF_PARSING_MODE)
            logger.info(
                f"Using user {current_user.id} PDF parsing preference: {mode}"
            )
        else:
            # Global setting is fallback
            mode = settings.PDF_PARSING_MODE

        return extract_text_from_pdf_bytes(
            file_content, filename, parsing_mode=mode
        )

    # ... rest of function unchanged ...
```

**Same update needed for**:

```python
def extract_documents_from_file_unified(
    file_content: bytes,
    filename: str,
    pdf_parsing_mode: str = None,
    current_user = None  # NEW parameter
) -> List[Document]:
    """
    Similar priority logic for document extraction.
    """
    # ... same priority logic as above ...
```

---

### 4. Update All Call Sites

Need to update all API endpoints that process PDFs to pass `current_user`:

#### Locations to Update:

1. **Knowledge Bases** (`backend/app/api/routes/knowledgebases.py`)

   Current calls to `extract_documents_from_file_unified()`:

   ```python
   # Update to pass current_user
   documents = extract_documents_from_file_unified(
       file_content,
       file.filename,
       current_user=current_user  # NEW
   )
   ```

2. **Chatbot** (`backend/app/api/routes/chatbot.py`)

   Multiple locations where files are processed:

   ```python
   # File upload processing
   text_content = extract_text_from_file_unified(
       file_content,
       file.filename,
       current_user=current_user  # NEW
   )
   ```

3. **VeraDoc** (`backend/app/api/routes/veradoc.py`)

   Text extraction for review/compare:

   ```python
   text_content = extract_text_from_file_unified(
       file_content,
       filename,
       current_user=current_user  # NEW
   )
   ```

4. **FormConnect** (`backend/app/api/routes/formconnect.py`)

   PDF processing for form field extraction:

   ```python
   documents = extract_documents_from_file_unified(
       file_content,
       filename,
       current_user=current_user  # NEW
   )
   ```

5. **TwinCheck** (`backend/app/api/routes/twincheck.py`)

   Document comparison processing:

   ```python
   text_content = extract_text_from_file_unified(
       file_content,
       filename,
       current_user=current_user  # NEW
   )
   ```

**Note**: All these endpoints already have `current_user` available via their function signatures (using `CurrentUser` dependency).

---

### 5. Frontend Changes

#### TypeScript Type Updates

**File**: `frontend/src/client/types.gen.ts`

```typescript
export type UserPublic = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  id: string
  status: UserStatus
  registration_date: string
  approved_date: string | null
  preferred_language: string
  vision_analysis_enabled: boolean
  pdf_parsing_preference: string // NEW
}

export type UserUpdate = {
  email?: string | null
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password?: string | null
  preferred_language?: string | null
  vision_analysis_enabled?: boolean
  pdf_parsing_preference?: string // NEW
}

export type UserUpdateMe = {
  full_name?: string | null
  email?: string | null
  preferred_language?: string | null
  vision_analysis_enabled?: boolean
  pdf_parsing_preference?: string // NEW
}

export type PdfParsingPreferenceUpdate = {
  pdf_parsing_preference: string // NEW
}
```

#### API Service Updates

**File**: `frontend/src/client/sdk.gen.ts`

```typescript
export class UsersService {
  // ... existing methods ...

  /**
   * Update PDF Parsing Preference
   * Update current user's PDF parsing mode preference.
   */
  public static updatePdfParsingPreference(
    data: UpdatePdfParsingPreferenceData,
  ): CancelablePromise<UserPublic> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/users/me/pdf-parsing-preference",
      body: data.requestBody,
      mediaType: "application/json",
    })
  }
}
```

#### New Settings Component

**File**: `frontend/src/components/UserSettings/PdfParsingSettings.tsx`

```tsx
import { Button } from "@/components/ui/button"
import { Radio, RadioGroup } from "@/components/ui/radio"
import { Field } from "@/components/ui/field"
import { Alert } from "@/components/ui/alert"
import { Box, Card, VStack, Text, Stack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { useState } from "react"
import { useTranslation } from "react-i18next"

const PdfParsingSettings = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [mode, setMode] = useState(user?.pdf_parsing_preference ?? "auto")

  const updateMutation = useMutation({
    mutationFn: (parsingMode: string) =>
      UsersService.updatePdfParsingPreference({
        requestBody: { pdf_parsing_preference: parsingMode },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const handleModeChange = (newMode: string) => {
    setMode(newMode)
    updateMutation.mutate(newMode)
  }

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={4}>
          <Box>
            <Text fontSize="lg" fontWeight="semibold">
              {t("settings.pdfParsing.title")}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={2}>
              {t("settings.pdfParsing.description")}
            </Text>
          </Box>

          <Alert status="info">
            <Text fontSize="sm">{t("settings.pdfParsing.explanation")}</Text>
          </Alert>

          <Field label={t("settings.pdfParsing.modeLabel")}>
            <RadioGroup value={mode} onValueChange={(e) => handleModeChange(e.value)}>
              <Stack gap={4}>
                <Radio value="auto" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">{t("settings.pdfParsing.autoMode")}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.pdfParsing.autoDescription")}
                    </Text>
                  </Box>
                </Radio>

                <Radio value="enhanced" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">{t("settings.pdfParsing.enhancedMode")}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.pdfParsing.enhancedDescription")}
                    </Text>
                  </Box>
                </Radio>

                <Radio value="basic" disabled={updateMutation.isPending}>
                  <Box>
                    <Text fontWeight="semibold">{t("settings.pdfParsing.basicMode")}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {t("settings.pdfParsing.basicDescription")}
                    </Text>
                  </Box>
                </Radio>
              </Stack>
            </RadioGroup>
          </Field>

          <Box fontSize="xs" color="gray.500" bg="gray.50" p={4} borderRadius="md">
            <Text fontWeight="semibold" mb={2}>
              {t("settings.pdfParsing.comparison.title")}
            </Text>

            <VStack align="start" gap={3}>
              <Box>
                <Text fontWeight="semibold" color="blue.600">
                  {t("settings.pdfParsing.comparison.autoTitle")}
                </Text>
                <Text>✓ {t("settings.pdfParsing.comparison.autoFeature1")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.autoFeature2")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.autoFeature3")}</Text>
              </Box>

              <Box>
                <Text fontWeight="semibold" color="green.600">
                  {t("settings.pdfParsing.comparison.enhancedTitle")}
                </Text>
                <Text>✓ {t("settings.pdfParsing.comparison.enhancedFeature1")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.enhancedFeature2")}</Text>
                <Text>⚠ {t("settings.pdfParsing.comparison.enhancedWarning")}</Text>
              </Box>

              <Box>
                <Text fontWeight="semibold" color="purple.600">
                  {t("settings.pdfParsing.comparison.basicTitle")}
                </Text>
                <Text>✓ {t("settings.pdfParsing.comparison.basicFeature1")}</Text>
                <Text>✓ {t("settings.pdfParsing.comparison.basicFeature2")}</Text>
                <Text>⚠ {t("settings.pdfParsing.comparison.basicWarning")}</Text>
              </Box>
            </VStack>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default PdfParsingSettings
```

#### Add to Settings Route

**File**: `frontend/src/routes/_layout/settings.tsx`

```tsx
import PdfParsingSettings from "@/components/UserSettings/PdfParsingSettings"

const tabsConfig = [
  {
    value: "my-profile",
    title: "My profile",
    titleKey: "navigation.myProfile",
    component: UserInformation,
  },
  {
    value: "language",
    title: "Language",
    titleKey: "settings.language",
    component: LanguageSettings,
  },
  {
    value: "vision-analysis",
    title: "Vision Analysis",
    titleKey: "settings.visionAnalysis.tab",
    component: VisionAnalysisSettings,
  },
  {
    value: "pdf-parsing", // NEW TAB
    title: "PDF Parsing",
    titleKey: "settings.pdfParsing.tab",
    component: PdfParsingSettings,
  },
  {
    value: "password",
    title: "Password",
    titleKey: "settings.changePassword",
    component: ChangePassword,
  },
  // ... rest of tabs
]
```

#### Translation Updates

**File**: `frontend/src/locales/en/common.json`

```json
{
  "settings": {
    "pdfParsing": {
      "tab": "PDF Parsing",
      "title": "PDF Parsing Preferences",
      "description": "Control how the system processes PDF documents. Choose the mode that best fits your workflow and document types.",
      "explanation": "💡 Different parsing modes offer different trade-offs between speed and accuracy. Choose based on your typical document types.",
      "modeLabel": "PDF Parsing Mode",

      "autoMode": "Auto (Recommended)",
      "autoDescription": "Intelligently detects tables and uses advanced parsing only when needed. Best balance of speed and quality.",

      "enhancedMode": "Enhanced (Best Quality)",
      "enhancedDescription": "Always uses PyMuPDF4LLM for superior table extraction. Best for documents with complex tables, but slower.",

      "basicMode": "Basic (Fastest)",
      "basicDescription": "Uses fast pypdf extraction only. Best for text-only documents without tables.",

      "comparison": {
        "title": "Mode Comparison:",

        "autoTitle": "Auto Mode",
        "autoFeature1": "Fast table detection runs first",
        "autoFeature2": "Advanced parsing only if tables found",
        "autoFeature3": "Best for mixed document types",

        "enhancedTitle": "Enhanced Mode",
        "enhancedFeature1": "Always uses PyMuPDF4LLM",
        "enhancedFeature2": "Best table structure preservation",
        "enhancedWarning": "Slower processing time",

        "basicTitle": "Basic Mode",
        "basicFeature1": "Fastest processing speed",
        "basicFeature2": "Lower resource usage",
        "basicWarning": "May miss table formatting"
      }
    }
  }
}
```

---

## 🔄 User Experience Flow

### Initial Setup (New Users)

1. User registers and creates account
2. `pdf_parsing_preference` defaults to `"auto"`
3. User sees "Auto" selected in Settings → PDF Parsing
4. Documents processed with intelligent table detection
5. User can change preference at any time

### Changing PDF Parsing Mode

1. User navigates to Settings → PDF Parsing tab
2. Sees current mode selected (e.g., "Auto")
3. Reads explanation of each mode
4. Selects different mode (e.g., "Enhanced")
5. Setting saved immediately to backend
6. Confirmation shown: "PDF parsing preference updated"
7. Future PDF processing will use selected mode

### Document Processing Behavior

#### Auto Mode (Default - Recommended)

```
User uploads PDF with tables
↓
System checks: current_user.pdf_parsing_preference = "auto"
↓
Fast table detection runs (PyMuPDF)
  → Tables found: Yes (3 tables detected)
↓
Uses PyMuPDF4LLM for enhanced parsing
↓
Tables preserved in Markdown format
```

```
User uploads text-only PDF
↓
System checks: current_user.pdf_parsing_preference = "auto"
↓
Fast table detection runs (PyMuPDF)
  → Tables found: No
↓
Uses fast pypdf extraction
↓
Quick text extraction, no overhead
```

#### Enhanced Mode (Always Advanced)

```
User uploads ANY PDF
↓
System checks: current_user.pdf_parsing_preference = "enhanced"
↓
Skips table detection
↓
Uses PyMuPDF4LLM directly
↓
Best quality extraction (slower)
```

#### Basic Mode (Always Fast)

```
User uploads ANY PDF
↓
System checks: current_user.pdf_parsing_preference = "basic"
↓
Skips table detection
↓
Uses pypdf directly
↓
Fastest extraction (may miss tables)
```

---

## 📊 Impact Analysis

### Features Affected

All features that process PDFs will respect the user's preference:

1. **Knowledge Bases** (`knowledgebases.py`)

   - PDF upload and indexing
   - Vector search quality depends on parsing mode

2. **Chatbot** (`chatbot.py`)

   - PDF file uploads for conversation context
   - Document-based question answering

3. **VeraDoc** (`veradoc.py`)

   - PDF review and comparison
   - Text extraction for matching

4. **FormConnect** (`formconnect.py`)

   - PDF form field extraction
   - Table-based form detection

5. **TwinCheck** (`twincheck.py`)
   - Document comparison
   - Difference detection

### Performance Implications

#### Example: 100-page PDF with 20 complex tables

**Basic Mode** (Always pypdf):

- Processing time: ~5 seconds
- Table quality: Poor (structure lost)
- Use case: Quick text search, no tables needed

**Auto Mode** (Intelligent):

- Table detection: ~0.5 seconds
- PyMuPDF4LLM processing: ~15 seconds
- Total: ~15.5 seconds
- Table quality: Excellent (Markdown tables)
- Use case: **Recommended for most users**

**Enhanced Mode** (Always PyMuPDF4LLM):

- Processing time: ~15 seconds (same as auto when tables present)
- Table quality: Excellent
- Use case: User knows document has tables, wants to skip detection

#### Example: 100-page text-only PDF (no tables)

**Basic Mode**:

- Processing time: ~5 seconds
- Quality: Good (text-only)

**Auto Mode** (Intelligent):

- Table detection: ~0.5 seconds
- pypdf processing: ~5 seconds
- Total: ~5.5 seconds
- Quality: Good (text-only)
- **Smart choice**: Minimal overhead

**Enhanced Mode**:

- Processing time: ~15 seconds
- Quality: Good (but wasted processing time)
- **Inefficient** for this document type

---

## 🧪 Testing Requirements

### Backend Tests

1. **Model Tests** (`test_user_model.py`)

   - Test default value is `"auto"`
   - Test field accepts valid modes
   - Test field rejects invalid modes

2. **API Tests** (`test_users.py`)

   - Test GET `/api/v1/users/me` includes `pdf_parsing_preference`
   - Test PUT `/api/v1/users/me/pdf-parsing-preference` updates setting
   - Test invalid modes rejected (400 error)
   - Test valid modes accepted ("auto", "enhanced", "basic")

3. **Document Utils Tests** (`test_document_utils.py`)

   - Test mode priority: explicit > user preference > global setting
   - Test `extract_text_from_file_unified()` with user preference
   - Test `extract_documents_from_file_unified()` with user preference
   - Test fallback to global setting when user is None

4. **Integration Tests**
   - Test Knowledge Base respects user preference
   - Test Chatbot respects user preference
   - Test VeraDoc respects user preference
   - Test FormConnect respects user preference
   - Test TwinCheck respects user preference

### Frontend Tests

1. **Component Tests**

   - PDF parsing mode selector renders correctly
   - Radio buttons work properly
   - Mode descriptions display
   - Selection updates user preference

2. **Integration Tests**
   - Settings page includes new tab
   - Radio selection syncs with backend
   - User data refreshes after update

---

## 🚀 Deployment Plan

### Phase 1: Database Migration

1. Run Alembic migration to add `pdf_parsing_preference` column
2. Verify all existing users have `pdf_parsing_preference = "auto"`
3. Monitor database for issues

### Phase 2: Backend Deployment

1. Deploy backend code with updated document_utils
2. Deploy new API endpoint
3. Verify backward compatibility (global setting still works)
4. Test priority order (explicit > user > global)

### Phase 3: Frontend Deployment

1. Deploy updated frontend with new settings UI
2. Verify settings page loads correctly
3. Test radio selection functionality
4. Verify mode descriptions are clear

### Phase 4: User Communication

1. Send email to existing users about new feature
2. Update documentation
3. Add in-app notification about customization option

---

## 📝 Migration Strategy for Existing Users

### Approach: Safe Intelligent Default

- All existing users will have `pdf_parsing_preference = "auto"` by default
- This matches the **recommended mode** for most users
- Provides best balance of performance and quality
- Users who need different behavior can easily change

### Why "Auto" as Default?

1. **Intelligent**: Only uses advanced parsing when needed
2. **Efficient**: Fast for text-only documents
3. **Quality**: Preserves tables when present
4. **Safe**: Works well for all document types
5. **Matches Current Behavior**: Global default is already "enhanced", but auto is smarter

### Communication Plan

```
Subject: New Feature: Customize Your PDF Processing

We've added a new setting to let you control how PDFs are processed!

What's New:
- You can now choose your preferred PDF parsing mode
- Three modes available: Auto (recommended), Enhanced, or Basic
- Setting applies to all your PDF uploads and processing

Your Current Setting:
- Automatically set to "Auto" mode (intelligent detection)
- This provides the best balance for most users

Want to Change It?
1. Go to Settings → PDF Parsing
2. Choose your preferred mode:
   - Auto: Smart detection (recommended for most users)
   - Enhanced: Always use advanced parsing (best for table-heavy PDFs)
   - Basic: Fast mode (best for text-only PDFs)

Why This Matters:
Different document types benefit from different processing approaches.
Now you can customize the behavior to match your workflow!

Questions? Contact support@yourapp.com
```

---

## 🔐 Security & Privacy Considerations

### No Impact

This feature only controls **how** PDFs are processed, not what data is collected.

- No new data collection
- No new data storage
- No new API permissions required
- No access to other users' preferences

### User Control

- Users have full control over their parsing preference
- Setting can be changed at any time
- No admin override (respects user choice)
- Preference stored securely in user record

---

## ⚠️ Edge Cases & Considerations

### 1. Global Setting Override

**Scenario**: Admin sets global `PDF_PARSING_MODE=basic`, user sets preference to `enhanced`
**Behavior**: User preference takes priority
**Rationale**: Per-user settings should override global defaults

### 2. Explicit Parameter Override

**Scenario**: Code explicitly passes `pdf_parsing_mode="enhanced"`, user preference is `basic`
**Behavior**: Explicit parameter takes highest priority
**Rationale**: Allows special cases where specific mode is required

### 3. Priority Order

```python
# Priority (highest to lowest):
1. Explicit pdf_parsing_mode parameter in function call
2. current_user.pdf_parsing_preference
3. settings.PDF_PARSING_MODE (global default)
```

### 4. Missing User Object

**Scenario**: Function called without `current_user` parameter
**Behavior**: Falls back to global setting
**Backward Compatibility**: ✅ Existing code continues to work

### 5. Invalid Mode in Database

**Scenario**: User record somehow has invalid mode (e.g., "invalid")
**Behavior**: Should validate and fall back to "auto"
**Implementation**: Add validation in model or getter

### 6. Background Jobs

**Scenario**: System background job processes PDFs
**Behavior**: Uses global setting (no user context)
**Alternative**: Could use special "system user" with default preferences

---

## 📚 Documentation Updates Required

1. **User Guide**

   - Add section on PDF parsing preferences
   - Explain mode differences with examples
   - Show how to change preference
   - Include performance comparisons

2. **API Documentation**

   - Document new `/me/pdf-parsing-preference` endpoint
   - Update user model schema
   - Add examples of mode selection
   - Document priority order

3. **Developer Documentation**

   - Update `extract_text_from_file_unified()` usage examples
   - Document passing `current_user` parameter
   - Add migration notes
   - Explain priority order for modes

4. **FAQ**
   - "Which mode should I choose?" → Use case guide
   - "Why is my PDF processing slow?" → Check mode setting
   - "Can I set different modes for different documents?" → Not yet (future feature)
   - "What's the difference between modes?" → Performance comparison

---

## 🎯 Success Metrics

### Quantitative

- **User Adoption**: Track % of users who change from default "auto"
- **Mode Distribution**: Monitor which modes users prefer
- **Performance Impact**: Track average processing times per mode
- **User Satisfaction**: Reduction in processing speed complaints

### Qualitative

- **User Feedback**: Positive sentiment about customization
- **Feature Awareness**: Users understand mode differences
- **Ease of Use**: Radio selection is intuitive and clear

---

## 🔮 Future Enhancements

### Document-Level Control

Allow users to specify mode per document:

```typescript
{
  global_pdf_preference: "auto",
  document_overrides: {
    "financial_reports": "enhanced",  // Always use enhanced for financial PDFs
    "meeting_notes": "basic"          // Fast mode for notes
  }
}
```

### Knowledge Base-Level Control

Different settings for different knowledge bases:

```python
class KnowledgeBase:
    pdf_parsing_mode: str = "auto"  # KB-specific override
```

### Smart Recommendations

Suggest mode based on document characteristics:

```python
if table_density > 0.3:
    recommended_mode = "enhanced"
elif file_size < 1_000_000:  # < 1MB
    recommended_mode = "basic"
else:
    recommended_mode = "auto"
```

### Performance Analytics

Show users their processing stats:

```typescript
{
  documents_processed: 150,
  avg_processing_time: "8.5s",
  mode_breakdown: {
    auto: { count: 100, avg_time: "7.2s" },
    enhanced: { count: 30, avg_time: "15.1s" },
    basic: { count: 20, avg_time: "3.8s" }
  }
}
```

---

## ✅ Checklist Before Implementation

- [ ] Review and approve this plan
- [ ] Create database migration script
- [ ] Update backend models and API
- [ ] Add validation for mode values
- [ ] Update document_utils with priority logic
- [ ] Update all API endpoint call sites
- [ ] Create frontend settings component
- [ ] Add translations for all supported languages
- [ ] Write backend unit tests
- [ ] Write backend integration tests
- [ ] Write frontend component tests
- [ ] Update API documentation
- [ ] Update user documentation
- [ ] Prepare user communication email
- [ ] Plan deployment schedule
- [ ] Set up monitoring for mode usage
- [ ] Create rollback plan

---

## 📞 Questions & Clarifications Needed

Before implementation, please confirm:

1. **Default Behavior**: Agree that `"auto"` should be the default for new users?
2. **Existing Users**: Confirm existing users should get `"auto"` as default?
3. **Priority Order**: Confirm priority: explicit parameter > user preference > global setting?
4. **Validation**: Should invalid modes be rejected (400 error) or auto-corrected to "auto"?
5. **UI Placement**: Should this be a separate tab or combined with vision analysis?
6. **Admin Override**: Should admins be able to see/modify user preferences?

---

## 📅 Estimated Timeline

- **Planning & Design**: 1 day (COMPLETE)
- **Backend Implementation**: 2-3 days
  - Database migration: 0.5 day
  - API updates: 1 day
  - Document utils refactor: 1 day
  - Testing: 0.5 day
- **Frontend Implementation**: 2 days
  - Settings component: 1 day
  - Translations: 0.5 day
  - Testing: 0.5 day
- **Documentation**: 1 day
- **Testing & QA**: 1-2 days
- **Deployment**: 0.5 day

**Total**: 7-9 days

---

## 🏁 Summary

This implementation will:

- ✅ Give users control over PDF parsing behavior
- ✅ Default to intelligent "auto" mode for best balance
- ✅ Provide clear UI for understanding mode differences
- ✅ Apply consistently across all features
- ✅ Maintain backward compatibility with global setting
- ✅ Follow same patterns as vision analysis setting
- ✅ Include comprehensive testing and documentation

**Key Advantages**:

- **User Empowerment**: Users choose what works for their workflow
- **Performance Flexibility**: Fast mode for simple docs, advanced for complex ones
- **Intelligent Default**: Auto mode provides best of both worlds
- **Consistent UX**: Mirrors vision analysis setting patterns
- **Future-Proof**: Easy to extend with additional features

**Next Step**: Approval to proceed with implementation

---

## 🔗 Related Documentation

- `PER_USER_VISION_ANALYSIS_SETTING.md` - Sister feature (similar implementation)
- `PYMUPDF4LLM_INTEGRATION_GUIDE.md` - PyMuPDF4LLM technical details
- `PDF_PARSING_MODE_IMPLEMENTATION.md` - Current global mode system
- `PYMUPDF4LLM_OPTIMIZATION.md` - Table detection optimization details
