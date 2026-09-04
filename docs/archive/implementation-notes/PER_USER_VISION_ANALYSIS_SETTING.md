# Per-User Vision Analysis Setting - Implementation Plan

## 📋 Overview

This document describes the planned implementation for adding a per-user setting to control whether vision analysis of embedded images in documents is enabled. This feature addresses cost concerns for users processing documents with many images.

**Date**: October 29, 2025  
**Status**: Planning Phase - Code Implementation Pending

---

## 🎯 Problem Statement

Currently, the application performs vision analysis on images embedded in documents **by default** whenever:

1. A vision-capable model is selected (e.g., GPT-4o, Claude-3-Sonnet)
2. Documents contain embedded images (PDFs, DOCX files)
3. Processing occurs in features like Chatbot, FormConnect, VeraDoc, TwinCheck

### Pain Points

- **High API costs** for documents with many images (up to 500 images per document)
- **No user control** - vision analysis happens automatically if model supports it
- **Unnecessary processing** when users only need text analysis
- **Unpredictable costs** - users don't know when vision analysis will occur

---

## 💡 Proposed Solution

Add a **per-user setting** called `vision_analysis_enabled` that works similarly to the existing `preferred_language` setting, giving users control over whether vision analysis should be performed on their documents.

### Key Principles

1. **User Control**: Users explicitly enable/disable vision analysis
2. **Default Behavior**: New users will have vision analysis **disabled by default** (opt-in)
3. **Consistent Application**: Setting applies across all features (Chatbot, FormConnect, VeraDoc, TwinCheck)
4. **Clear UI**: Settings page clearly explains the cost implications
5. **Backward Compatible**: Existing logic preserved, just adds an additional check

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

    # NEW FIELD
    vision_analysis_enabled: bool = Field(default=False)  # Opt-in by default
```

#### Migration Script

**File**: `backend/app/alembic/versions/add_vision_analysis_setting.py`

```python
"""Add vision_analysis_enabled to user

Revision ID: add_vision_analysis_enabled
Revises: <latest_revision>
Create Date: 2025-10-29

"""

def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "vision_analysis_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",  # Disabled by default for cost control
        ),
    )

def downgrade():
    op.drop_column("user", "vision_analysis_enabled")
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
    vision_analysis_enabled: bool | None = None  # NEW

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    preferred_language: str | None = Field(default=None, max_length=10)
    vision_analysis_enabled: bool | None = None  # NEW

class UserPublic(UserBase):
    id: uuid.UUID
    status: UserStatus
    registration_date: datetime
    approved_date: datetime | None
    preferred_language: str
    vision_analysis_enabled: bool  # NEW

class VisionAnalysisUpdate(SQLModel):
    vision_analysis_enabled: bool  # NEW - dedicated update model
```

#### Add API Endpoint

**File**: `backend/app/api/routes/users.py`

```python
@router.put("/me/vision-analysis", response_model=User)
def update_vision_analysis_setting(
    vision_update: VisionAnalysisUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update current user's vision analysis preference."""

    user = session.get(User, current_user.id)
    user.vision_analysis_enabled = vision_update.vision_analysis_enabled
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

---

### 3. VisionService Enhancement

#### Update Vision Check Logic

**File**: `backend/app/services/vision_service.py`

**Current Logic**:

```python
@staticmethod
def is_vision_enabled(llm) -> bool:
    """Check if the LLM supports multimodal/vision capabilities."""
    # Only checks if model supports vision
    if not llm:
        return False

    model_name = getattr(llm, "model_name", "") or getattr(llm, "model", "")
    # ... model checking logic ...
    return any(vision_model in model_name.lower()
               for vision_model in settings.VISION_ENABLED_MODELS)
```

**New Logic**:

```python
@staticmethod
def is_vision_enabled(llm, current_user=None) -> bool:
    """
    Check if vision analysis should be performed.

    Args:
        llm: The LLM instance to check
        current_user: Current user object (optional for backward compatibility)

    Returns:
        bool: True if BOTH model supports vision AND user has enabled it
    """
    if not llm:
        return False

    # Check 1: Does the model support vision?
    model_name = getattr(llm, "model_name", "") or getattr(llm, "model", "")
    # ... existing model checking logic ...
    model_supports_vision = any(
        vision_model in model_name.lower()
        for vision_model in settings.VISION_ENABLED_MODELS
    )

    if not model_supports_vision:
        return False

    # Check 2: Has the user enabled vision analysis?
    if current_user is not None:
        user_enabled_vision = getattr(current_user, "vision_analysis_enabled", False)
        if not user_enabled_vision:
            logger.info(
                f"Vision analysis disabled by user {current_user.id} preference"
            )
            return False

    return True
```

---

### 4. Update All Vision Check Call Sites

Need to update all locations where `VisionService.is_vision_enabled()` is called to pass `current_user`:

#### Locations to Update:

1. **`backend/app/services/document_utils.py`** - Line 765

   ```python
   vision_enabled = VisionService.is_vision_enabled(llm, current_user)
   ```

2. **`backend/app/api/routes/chatbot.py`** - Lines 149, 559, 1313, 1950

   ```python
   vision_enabled = VisionService.is_vision_enabled(llm, current_user)
   ```

3. **`backend/app/api/routes/formconnect.py`** - Lines 226, 255, 558

   ```python
   vision_enabled = VisionService.is_vision_enabled(llm, current_user)
   ```

4. **`backend/app/api/routes/twincheck.py`** - Line 256

   ```python
   vision_enabled = VisionService.is_vision_enabled(llm, current_user)
   ```

5. **`backend/app/api/routes/veradoc.py`** - Line 1213
   ```python
   vision_enabled = VisionService.is_vision_enabled(llm, current_user)
   ```

**Note**: All these functions already have access to `current_user` via their function signatures.

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
  vision_analysis_enabled: boolean // NEW
}

export type UserUpdate = {
  email?: string | null
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password?: string | null
  preferred_language?: string | null
  vision_analysis_enabled?: boolean // NEW
}

export type UserUpdateMe = {
  full_name?: string | null
  email?: string | null
  preferred_language?: string | null
  vision_analysis_enabled?: boolean // NEW
}

export type VisionAnalysisUpdate = {
  vision_analysis_enabled: boolean // NEW
}
```

#### API Service Updates

**File**: `frontend/src/client/sdk.gen.ts`

```typescript
export class UsersService {
  // ... existing methods ...

  /**
   * Update Vision Analysis Setting
   * Update current user's vision analysis preference.
   */
  public static updateVisionAnalysis(data: UpdateVisionAnalysisData): CancelablePromise<User> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/users/me/vision-analysis",
      body: data.requestBody,
      mediaType: "application/json",
    })
  }
}
```

#### New Settings Component

**File**: `frontend/src/components/UserSettings/VisionAnalysisSettings.tsx`

```tsx
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Field } from "@/components/ui/field"
import { Alert } from "@/components/ui/alert"
import { Box, Card, VStack, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import { useState } from "react"
import { useTranslation } from "react-i18next"

const VisionAnalysisSettings = () => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [enabled, setEnabled] = useState(user?.vision_analysis_enabled ?? false)

  const updateMutation = useMutation({
    mutationFn: (visionEnabled: boolean) =>
      UsersService.updateVisionAnalysis({
        requestBody: { vision_analysis_enabled: visionEnabled },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const handleToggle = (checked: boolean) => {
    setEnabled(checked)
    updateMutation.mutate(checked)
  }

  return (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={4}>
          <Box>
            <Text fontSize="lg" fontWeight="semibold">
              {t("settings.visionAnalysis.title")}
            </Text>
            <Text fontSize="sm" color="gray.600" mt={2}>
              {t("settings.visionAnalysis.description")}
            </Text>
          </Box>

          <Alert status="info">
            <Text fontSize="sm">{t("settings.visionAnalysis.costWarning")}</Text>
          </Alert>

          <Field label={t("settings.visionAnalysis.enableLabel")}>
            <Switch
              checked={enabled}
              onCheckedChange={(e) => handleToggle(e.checked)}
              disabled={updateMutation.isPending}
            />
          </Field>

          <Box fontSize="xs" color="gray.500">
            <Text fontWeight="semibold" mb={2}>
              {t("settings.visionAnalysis.whenEnabled")}
            </Text>
            <VStack align="start" gap={1} pl={4}>
              <Text>• {t("settings.visionAnalysis.feature1")}</Text>
              <Text>• {t("settings.visionAnalysis.feature2")}</Text>
              <Text>• {t("settings.visionAnalysis.feature3")}</Text>
              <Text>• {t("settings.visionAnalysis.feature4")}</Text>
            </VStack>

            <Text fontWeight="semibold" mt={3} mb={2}>
              {t("settings.visionAnalysis.whenDisabled")}
            </Text>
            <VStack align="start" gap={1} pl={4}>
              <Text>• {t("settings.visionAnalysis.disabled1")}</Text>
              <Text>• {t("settings.visionAnalysis.disabled2")}</Text>
            </VStack>
          </Box>
        </VStack>
      </Card.Body>
    </Card.Root>
  )
}

export default VisionAnalysisSettings
```

#### Add to Settings Route

**File**: `frontend/src/routes/_layout/settings.tsx`

```tsx
import VisionAnalysisSettings from "@/components/UserSettings/VisionAnalysisSettings"

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
    value: "vision-analysis", // NEW TAB
    title: "Vision Analysis",
    titleKey: "settings.visionAnalysis.tab",
    component: VisionAnalysisSettings,
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
    "visionAnalysis": {
      "tab": "Vision Analysis",
      "title": "Vision Analysis Settings",
      "description": "Control whether the AI analyzes images embedded in your documents. Disabling this can significantly reduce API costs for documents with many images.",
      "enableLabel": "Enable Vision Analysis",
      "costWarning": "⚠️ Vision analysis can be expensive for documents with many images. Each image analyzed incurs additional API costs. Consider disabling if you primarily work with text-only documents.",
      "whenEnabled": "When enabled:",
      "feature1": "Images in PDFs and DOCX files will be analyzed",
      "feature2": "Charts, diagrams, and visual content will be extracted",
      "feature3": "Form fields in images can be detected (FormConnect)",
      "feature4": "More comprehensive document understanding",
      "whenDisabled": "When disabled:",
      "disabled1": "Only text content will be analyzed (lower cost)",
      "disabled2": "Visual elements in documents will be ignored"
    }
  }
}
```

---

## 🔄 User Experience Flow

### Initial Setup (New Users)

1. User registers and creates account
2. `vision_analysis_enabled` defaults to `False`
3. User sees vision analysis as disabled in Settings
4. If user selects vision-capable model, no vision processing occurs
5. User can opt-in via Settings if needed

### Enabling Vision Analysis

1. User navigates to Settings → Vision Analysis tab
2. Reads explanation and cost warning
3. Toggles switch to enable
4. Setting saved immediately to backend
5. Confirmation shown: "Vision analysis enabled"
6. Future document processing will include image analysis

### Document Processing Behavior

#### Vision Analysis Disabled (Default)

```
User uploads PDF with 100 images
↓
System checks: VisionService.is_vision_enabled(llm, current_user)
  → Model supports vision: ✓
  → User enabled setting: ✗
  → Result: False
↓
Only text content extracted and processed
↓
Lower API costs, faster processing
```

#### Vision Analysis Enabled (Opt-in)

```
User uploads PDF with 100 images
↓
System checks: VisionService.is_vision_enabled(llm, current_user)
  → Model supports vision: ✓
  → User enabled setting: ✓
  → Result: True
↓
Text AND image content extracted and analyzed
↓
Higher API costs, more comprehensive results
```

---

## 📊 Impact Analysis

### Features Affected

All features that currently use vision analysis will respect the new setting:

1. **Chatbot** (`chatbot.py`)

   - Full text document query with vision fallback
   - Image-only document processing

2. **FormConnect** (`formconnect.py`)

   - PDF image extraction for field detection
   - Image-only form processing
   - Enhanced vector search with images

3. **VeraDoc** (`veradoc.py`)

   - Image-only PDF support
   - Visual content analysis

4. **TwinCheck** (`twincheck.py`)

   - Document comparison with visual elements
   - Image-based difference detection

5. **Document Utilities** (`document_utils.py`)
   - Vision-enhanced text extraction
   - Suggestion generation (questions, outlines, form fields)

### Cost Implications

#### Example Document: 50-page PDF with 200 images

**Vision Enabled** (Current Default):

- Text extraction: ~$0.10
- Image analysis (200 images × $0.01): ~$2.00
- **Total**: ~$2.10

**Vision Disabled** (New Default):

- Text extraction: ~$0.10
- Image analysis: $0.00
- **Total**: ~$0.10

**Savings**: ~95% cost reduction for image-heavy documents

---

## 🧪 Testing Requirements

### Backend Tests

1. **Model Tests** (`test_user_model.py`)

   - Test default value is `False`
   - Test field accepts `True/False`

2. **API Tests** (`test_users.py`)

   - Test GET `/api/v1/users/me` includes `vision_analysis_enabled`
   - Test PUT `/api/v1/users/me/vision-analysis` updates setting
   - Test invalid values rejected

3. **Vision Service Tests** (`test_vision_service.py`)

   - Test `is_vision_enabled()` with user setting disabled
   - Test `is_vision_enabled()` with user setting enabled
   - Test backward compatibility (no user passed)

4. **Integration Tests**
   - Test FormConnect respects setting
   - Test Chatbot respects setting
   - Test VeraDoc respects setting
   - Test TwinCheck respects setting

### Frontend Tests

1. **Component Tests**

   - Vision analysis toggle renders correctly
   - Toggle updates user preference
   - Warning message displays

2. **Integration Tests**
   - Settings page includes new tab
   - Toggle state syncs with backend
   - User data refreshes after update

---

## 🚀 Deployment Plan

### Phase 1: Database Migration

1. Run Alembic migration to add `vision_analysis_enabled` column
2. Verify all existing users have `vision_analysis_enabled = False`
3. Monitor database for issues

### Phase 2: Backend Deployment

1. Deploy backend code with updated VisionService
2. Deploy new API endpoint
3. Verify backward compatibility (vision still works when enabled)

### Phase 3: Frontend Deployment

1. Deploy updated frontend with new settings UI
2. Verify settings page loads correctly
3. Test toggle functionality

### Phase 4: User Communication

1. Send email to existing users about new feature
2. Update documentation
3. Add in-app notification about cost savings

---

## 📝 Migration Strategy for Existing Users

### Approach: Conservative Default

- All existing users will have `vision_analysis_enabled = False` by default
- This is the **safest approach** to prevent unexpected cost increases
- Users who want vision analysis must explicitly opt-in

### Alternative Approach (Not Recommended)

- Set existing users to `True` (preserve current behavior)
- Risk: Users may not realize they're incurring vision costs
- Could lead to billing complaints

### Communication Plan

```
Subject: New Cost-Saving Feature: Control Vision Analysis

We've added a new setting to help you control API costs!

What's New:
- You can now enable/disable vision analysis of images in documents
- Vision analysis is now OPT-IN (disabled by default)
- This can save up to 95% on API costs for image-heavy documents

Action Required:
If you want the AI to analyze images in your documents:
1. Go to Settings → Vision Analysis
2. Enable the "Vision Analysis" toggle
3. That's it! The AI will now process images when you use vision-capable models

Why This Matters:
Documents with many images (charts, diagrams, photos) can be expensive to process.
With this setting, you have full control over when vision analysis happens.

Questions? Contact support@yourapp.com
```

---

## 🔐 Security & Privacy Considerations

### No Impact

This feature only controls **when** vision analysis occurs, not what data is processed.

- No new data collection
- No new data storage
- No new API permissions required

### User Control

- Users have full control over their vision analysis preference
- Setting can be changed at any time
- No admin override (respects user choice)

---

## ⚠️ Edge Cases & Considerations

### 1. Model Switch Edge Case

**Scenario**: User has vision disabled, switches from text-only model to vision model
**Behavior**: No vision processing (setting still disabled)
**User Action**: Must explicitly enable vision analysis setting

### 2. Shared Documents

**Scenario**: Multiple users access same document with different vision settings
**Behavior**: Each user's processing respects their own setting
**Caching**: Vision results not cached (user-specific processing)

### 3. Admin Users

**Scenario**: Admin wants to override user setting
**Behavior**: No override mechanism (respects user autonomy)
**Alternative**: Admin can contact user to suggest enabling vision

### 4. System Processing

**Scenario**: Background jobs need vision analysis
**Behavior**: Use system default or require explicit vision flag
**Implementation**: Add optional `force_vision=True` parameter

---

## 📚 Documentation Updates Required

1. **User Guide**

   - Add section on vision analysis settings
   - Explain cost implications
   - Show how to enable/disable

2. **API Documentation**

   - Document new `/me/vision-analysis` endpoint
   - Update user model schema
   - Add examples

3. **Developer Documentation**

   - Update VisionService usage examples
   - Document passing `current_user` parameter
   - Add migration notes

4. **FAQ**
   - "Why isn't vision analysis working?" → Check settings
   - "How much does vision analysis cost?" → Pricing examples
   - "Can I enable vision for specific documents?" → Not yet (future feature)

---

## 🎯 Success Metrics

### Quantitative

- **Cost Reduction**: 50%+ reduction in average user API costs
- **User Adoption**: Track % of users who enable vision analysis
- **Support Tickets**: Reduction in cost-related complaints

### Qualitative

- **User Feedback**: Positive sentiment about cost control
- **Feature Awareness**: Users understand when vision is active
- **Ease of Use**: Toggle is intuitive and clear

---

## 🔮 Future Enhancements

### Document-Level Control

Allow users to enable vision for specific documents:

```typescript
{
  global_vision_enabled: false,
  document_vision_overrides: {
    "doc_123": true,  // Enable vision for this document only
    "doc_456": false
  }
}
```

### Feature-Level Control

Different settings for different features:

```python
{
  chatbot_vision_enabled: true,
  formconnect_vision_enabled: false,
  veradoc_vision_enabled: true,
  twincheck_vision_enabled: false
}
```

### Cost Budgets

Set monthly vision analysis budgets:

```python
{
  vision_analysis_enabled: true,
  monthly_vision_budget_usd: 10.00,
  vision_budget_exceeded_action: "disable_until_next_month"
}
```

### Smart Vision

Automatically decide whether vision is needed:

```python
if image_count < 10 and user.smart_vision_enabled:
    # Auto-enable vision for documents with few images
    vision_enabled = True
```

---

## ✅ Checklist Before Implementation

- [ ] Review and approve this plan
- [ ] Create database migration script
- [ ] Update backend models and API
- [ ] Update VisionService with user check
- [ ] Update all vision check call sites
- [ ] Create frontend settings component
- [ ] Add translations for all supported languages
- [ ] Write backend tests
- [ ] Write frontend tests
- [ ] Update API documentation
- [ ] Update user documentation
- [ ] Prepare user communication email
- [ ] Plan deployment schedule
- [ ] Set up monitoring for new setting usage
- [ ] Create rollback plan

---

## 📞 Questions & Clarifications Needed

Before implementation, please confirm:

1. **Default Behavior**: Agree that vision should be **disabled by default** for new users?
2. **Existing Users**: Confirm existing users should also have vision **disabled by default**?
3. **Communication**: When should we notify users about this change?
4. **Pricing Page**: Should we update pricing page to mention this feature?
5. **Admin Dashboard**: Should admins see vision usage statistics per user?

---

## 📅 Estimated Timeline

- **Planning & Design**: 1 day (COMPLETE)
- **Backend Implementation**: 2-3 days
  - Database migration: 0.5 day
  - API updates: 1 day
  - VisionService refactor: 1 day
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

- ✅ Give users control over vision analysis costs
- ✅ Default to cost-effective text-only processing
- ✅ Maintain all existing vision capabilities for those who opt-in
- ✅ Provide clear UI for understanding and managing the setting
- ✅ Apply consistently across all features (Chatbot, FormConnect, VeraDoc, TwinCheck)
- ✅ Include comprehensive testing and documentation

**Next Step**: Approval to proceed with implementation
