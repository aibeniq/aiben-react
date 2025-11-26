# Restrict "All Users" Toggle to Superusers Only - Implementation Plan

## 📋 Overview

This document outlines the plan to restrict the "All Users" toggle functionality to superusers only. Currently, ANY logged-in user can see and use the "All Users" toggle in various parts of the application, allowing them to view other users' Knowledge Bases and Archive history. This change will limit this capability to superusers only.

## 🎯 Objectives

1. Hide the "All Users" toggle UI from non-superuser users
2. Prevent non-superusers from accessing all-users data via API calls
3. Maintain backward compatibility for superusers
4. Apply changes consistently across all affected features

## 📍 Current State Analysis

### Where "All Users" Toggles Currently Appear

#### 1. **Knowledge Bases Tab** (`frontend/src/routes/_layout/knowledge-bases.tsx`)

- **Location**: Top-right corner of the Knowledge Bases table
- **Component**: Uses `useKnowledgeBases` hook
- **Visibility**: Currently visible to ALL users
- **Function**: Switches between showing only user's own KBs vs. all users' KBs

#### 2. **Archive Page - All Tabs** (`frontend/src/routes/_layout/archive.tsx`)

- **Location**: History panel on the left side of each tool tab
- **Component**: `HistoryPanel` component within `ToolTab` component
- **Tabs Affected**:
  - Review (VeraDoc)
  - Generate (ReportGenie)
  - Compare (TwinCheck)
  - Match (FormConnect)
- **Visibility**: Currently visible to ALL users
- **Function**: Switches between showing only user's own history vs. all users' history

#### 3. **Knowledge Base Selection Modals** (Used across multiple tools)

- **Component**: `KnowledgeBaseSelectionModal` (`frontend/src/components/Common/KnowledgeBaseSelectionModal.tsx`)
- **Used By**:
  - Review tool (checklist creation/editing)
  - Generate tool (outline creation/editing)
  - Compare tool (topic list creation/editing)
  - Match tool (form template creation/editing)
  - Chatbot component
- **Visibility**: Currently visible to ALL users
- **Function**: Switches between showing only user's own KBs vs. all users' KBs

### User Authentication & Superuser Status

#### Backend User Model (`backend/app/models.py`)

```python
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False  # ← Superuser flag
    full_name: str | None = Field(default=None, max_length=255)
```

#### Frontend User Access (`frontend/src/hooks/useAuth.ts`)

- Hook: `useAuth()`
- Returns: `user` object with `is_superuser` property
- Usage example: `const { user: currentUser } = useAuth()`
- Access: `currentUser?.is_superuser` (boolean)

#### Existing Superuser-Only Features

The app already uses superuser checks for:

- Admin panel visibility (`frontend/src/components/Common/SidebarItems.tsx` line 207)
- Settings tabs visibility (`frontend/src/routes/_layout/settings.tsx` line 59)

### Backend API Endpoints with `show_all` Parameter

#### 1. **Knowledge Bases API** (`backend/app/api/routes/knowledgebases.py`)

```python
@router.get("/", response_model=KnowledgeBasesPublic)
def read_knowledge_bases(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(100, ge=1, le=1000),
    show_all: bool = Query(False),  # ← Parameter
) -> Any:
    # ...
    if show_all or current_user.is_superuser:
        # Show all knowledge bases
        count_statement = select(func.count()).select_from(KnowledgeBase)
        count = session.exec(count_statement).one()
        query = query.offset(skip).limit(limit)
    else:
        # Show only user's own knowledge bases
        count_statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(KnowledgeBase.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        query = (
            query.filter(KnowledgeBase.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
```

**Current Behavior**: Accepts `show_all` from ANY user and honors it (superuser check is only an OR condition)

#### 2. **VeraDoc History API** (`backend/app/api/routes/veradoc.py`)

```python
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_veradoc_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    show_all: bool = Query(False),  # ← Parameter
):
    """Retrieve past VeraDoc evaluation history for the current user or all users."""
    query = select(LlmInteraction).where(LlmInteraction.functionality == "veradoc")

    if not show_all:
        query = query.where(LlmInteraction.user_id == current_user.id)
```

**Current Behavior**: Accepts `show_all` from ANY user; no superuser check

#### 3. **ReportGenie History API** (`backend/app/api/routes/reportgenie.py`)

```python
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_report_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    show_all: bool = Query(False),  # ← Parameter
):
    """Retrieve past ReportGenie generation history for the current user or all users."""
    query = select(LlmInteraction).where(LlmInteraction.functionality == "reportgenie")

    if not show_all:
        query = query.where(LlmInteraction.user_id == current_user.id)
```

**Current Behavior**: Accepts `show_all` from ANY user; no superuser check

#### 4. **TwinCheck History API** (`backend/app/api/routes/twincheck.py`)

```python
@router.get("/history")
async def get_comparison_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    show_all: bool = Query(False),  # ← Parameter
):
    """Retrieve past document comparison history for the current user or all users."""
    query = select(LlmInteraction).where(LlmInteraction.functionality == "twincheck")

    if not show_all:
        query = query.where(LlmInteraction.user_id == current_user.id)
```

**Current Behavior**: Accepts `show_all` from ANY user; no superuser check

#### 5. **FormConnect History API** (`backend/app/api/routes/formconnect.py`)

```python
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_form_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(20, ge=1, le=100),
    show_all: bool = Query(False),  # ← Parameter
):
    """Retrieve past form processing history for the current user or all users."""
    query = select(LlmInteraction).where(LlmInteraction.functionality == "formconnect")

    if not show_all:
        query = query.where(LlmInteraction.user_id == current_user.id)
```

**Current Behavior**: Accepts `show_all` from ANY user; no superuser check

## 🔧 Implementation Plan

### Phase 1: Backend Security Hardening

**Goal**: Prevent non-superusers from using `show_all=true` at the API level

#### Changes Required:

**1. Knowledge Bases API** (`backend/app/api/routes/knowledgebases.py`)

- **File**: `backend/app/api/routes/knowledgebases.py`
- **Function**: `read_knowledge_bases()`
- **Line**: ~732

**Current Code**:

```python
if show_all or current_user.is_superuser:
    # Show all knowledge bases
```

**Change To**:

```python
# Only superusers can view all users' knowledge bases
if show_all and not current_user.is_superuser:
    raise HTTPException(
        status_code=403,
        detail="Only superusers can view all users' knowledge bases"
    )

if show_all or current_user.is_superuser:
    # Show all knowledge bases
```

**2. VeraDoc History API** (`backend/app/api/routes/veradoc.py`)

- **File**: `backend/app/api/routes/veradoc.py`
- **Function**: `get_veradoc_history()`
- **Line**: ~2433

**Add at the beginning of the function**:

```python
# Only superusers can view all users' history
if show_all and not current_user.is_superuser:
    raise HTTPException(
        status_code=403,
        detail="Only superusers can view all users' history"
    )
```

**3. ReportGenie History API** (`backend/app/api/routes/reportgenie.py`)

- **File**: `backend/app/api/routes/reportgenie.py`
- **Function**: `get_report_history()`
- **Line**: ~1220

**Add at the beginning of the function**:

```python
# Only superusers can view all users' history
if show_all and not current_user.is_superuser:
    raise HTTPException(
        status_code=403,
        detail="Only superusers can view all users' history"
    )
```

**4. TwinCheck History API** (`backend/app/api/routes/twincheck.py`)

- **File**: `backend/app/api/routes/twincheck.py`
- **Function**: `get_comparison_history()`
- **Line**: ~1052

**Add at the beginning of the function**:

```python
# Only superusers can view all users' history
if show_all and not current_user.is_superuser:
    raise HTTPException(
        status_code=403,
        detail="Only superusers can view all users' history"
    )
```

**5. FormConnect History API** (`backend/app/api/routes/formconnect.py`)

- **File**: `backend/app/api/routes/formconnect.py`
- **Function**: `get_form_history()`
- **Line**: ~1798

**Add at the beginning of the function**:

```python
# Only superusers can view all users' history
if show_all and not current_user.is_superuser:
    raise HTTPException(
        status_code=403,
        detail="Only superusers can view all users' history"
    )
```

### Phase 2: Frontend UI Restrictions

**Goal**: Hide the "All Users" toggle from non-superusers in the UI

#### Changes Required:

**1. Knowledge Bases Hook** (`frontend/src/hooks/useKnowledgeBases.ts`)

- **File**: `frontend/src/hooks/useKnowledgeBases.ts`
- **Modification**: Add `isSuperuser` parameter to control toggle availability

**Current Interface**:

```typescript
interface UseKnowledgeBasesReturn {
  knowledgeBases: any[]
  isLoading: boolean
  showAllUsers: boolean
  toggleShowAllUsers: () => void
}
```

**Change To**:

```typescript
interface UseKnowledgeBasesReturn {
  knowledgeBases: any[]
  isLoading: boolean
  showAllUsers: boolean
  toggleShowAllUsers: () => void
  canViewAllUsers: boolean // ← NEW: Indicates if user can use toggle
}

export const useKnowledgeBases = (): UseKnowledgeBasesReturn => {
  const { user: currentUser } = useAuth() // ← ADD: Get current user
  const [showAllUsers, setShowAllUsers] = useState(false)

  const canViewAllUsers = currentUser?.is_superuser ?? false // ← NEW

  // Rest of hook implementation...

  return {
    knowledgeBases: knowledgeBasesQuery.data || [],
    isLoading: knowledgeBasesQuery.isLoading,
    showAllUsers,
    toggleShowAllUsers,
    canViewAllUsers, // ← NEW: Return permission flag
  }
}
```

**2. Knowledge Bases Page** (`frontend/src/routes/_layout/knowledge-bases.tsx`)

- **File**: `frontend/src/routes/_layout/knowledge-bases.tsx`
- **Line**: ~210-260 (Toggle UI section)

**Current Code**:

```tsx
const { knowledgeBases, isLoading, showAllUsers, toggleShowAllUsers } = useKnowledgeBases()

// ... later in JSX:
<HStack justifyContent="flex-end" mb={4}>
  <Tooltip content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}>
    <HStack gap={2}>
      <HStack gap={1} align="center">
        <Text fontSize="xs" color="gray.500">
          {t("archive.allUsers")}
        </Text>
        <HelpTooltip helpKey="allUsersToggle" />
      </HStack>
      <Switch.Root /* ... */ >
        {/* Switch controls */}
      </Switch.Root>
    </HStack>
  </Tooltip>
</HStack>
```

**Change To**:

```tsx
const { knowledgeBases, isLoading, showAllUsers, toggleShowAllUsers, canViewAllUsers } =
  useKnowledgeBases()

// ... later in JSX:
{
  canViewAllUsers && ( // ← ADD: Conditional rendering
    <HStack justifyContent="flex-end" mb={4}>
      <Tooltip
        content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
      >
        <HStack gap={2}>
          <HStack gap={1} align="center">
            <Text fontSize="xs" color="gray.500">
              {t("archive.allUsers")}
            </Text>
            <HelpTooltip helpKey="allUsersToggle" />
          </HStack>
          <Switch.Root /* ... */>{/* Switch controls */}</Switch.Root>
        </HStack>
      </Tooltip>
    </HStack>
  )
}
```

**Locations to Update** (repeat the same pattern in all three places where toggle appears):

- Line ~120-160: Loading state section
- Line ~175-210: Empty state section
- Line ~220-260: Data loaded section

**3. Archive Hook** (`frontend/src/hooks/useToolArchive.ts`)

- **File**: `frontend/src/hooks/useToolArchive.ts`
- **Modification**: Add superuser check to control toggle availability

**Current Interface**:

```typescript
interface UseToolArchiveReturn {
  veradoc: ToolState & ToolActions
  reportgenie: ToolState & ToolActions
  twincheck: ToolState & ToolActions
  formconnect: ToolState & ToolActions
  activeTab: string
  setActiveTab: (tab: string) => void
  copySuccess: boolean
  setCopySuccess: (success: boolean) => void
  loadingDownload: boolean
  setLoadingDownload: (loading: boolean) => void
  showAllUsers: boolean
  toggleShowAllUsers: () => void
}
```

**Change To**:

```typescript
interface UseToolArchiveReturn {
  veradoc: ToolState & ToolActions
  reportgenie: ToolState & ToolActions
  twincheck: ToolState & ToolActions
  formconnect: ToolState & ToolActions
  activeTab: string
  setActiveTab: (tab: string) => void
  copySuccess: boolean
  setCopySuccess: (success: boolean) => void
  loadingDownload: boolean
  setLoadingDownload: (loading: boolean) => void
  showAllUsers: boolean
  toggleShowAllUsers: () => void
  canViewAllUsers: boolean // ← NEW
}

export const useToolArchive = (): UseToolArchiveReturn => {
  const { user: currentUser } = useAuth() // ← ADD: Get current user
  const [showAllUsers, setShowAllUsers] = useState(false)

  const canViewAllUsers = currentUser?.is_superuser ?? false // ← NEW

  // Rest of hook implementation...

  return {
    // ... other return values
    showAllUsers,
    toggleShowAllUsers,
    canViewAllUsers, // ← NEW
  }
}
```

**4. Archive Page** (`frontend/src/routes/_layout/archive.tsx`)

- **File**: `frontend/src/routes/_layout/archive.tsx`
- **Line**: ~32-50

**Current Code**:

```tsx
const {
  veradoc,
  reportgenie,
  twincheck,
  formconnect,
  activeTab,
  setActiveTab,
  copySuccess,
  setCopySuccess,
  loadingDownload,
  setLoadingDownload,
  showAllUsers,
  toggleShowAllUsers,
} = useToolArchive()
```

**Change To**:

```tsx
const {
  veradoc,
  reportgenie,
  twincheck,
  formconnect,
  activeTab,
  setActiveTab,
  copySuccess,
  setCopySuccess,
  loadingDownload,
  setLoadingDownload,
  showAllUsers,
  toggleShowAllUsers,
  canViewAllUsers, // ← ADD
} = useToolArchive()
```

**Then update all ToolTab usages** (lines ~583, ~615, ~633, ~651):

```tsx
<ToolTab
  reportHistory={veradoc.history}
  selectedHistoryReport={veradoc.selectedReport}
  isHistoryLoading={veradoc.isLoading}
  onLoadReport={veradoc.loadReport}
  onDeleteReport={veradoc.deleteReport}
  emptyMessage={t("archive.emptyMessages.review")}
  showAllUsers={showAllUsers}
  onToggleShowAllUsers={toggleShowAllUsers}
  canViewAllUsers={canViewAllUsers} // ← ADD
>
  {renderResults()}
</ToolTab>
```

**5. ToolTab Component** (`frontend/src/components/Archive/ToolTab.tsx`)

- **File**: `frontend/src/components/Archive/ToolTab.tsx`
- **Modification**: Add canViewAllUsers prop and pass to HistoryPanel

**Current Interface**:

```typescript
interface ToolTabProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage: string
  children: ReactNode
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}
```

**Change To**:

```typescript
interface ToolTabProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage: string
  children: ReactNode
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
  canViewAllUsers?: boolean // ← NEW
}

const ToolTab = ({
  /* ... other props ... */
  showAllUsers,
  onToggleShowAllUsers,
  canViewAllUsers, // ← ADD
}: ToolTabProps) => {
  return (
    // ...
    <HistoryPanel
      reportHistory={reportHistory}
      selectedHistoryReport={selectedHistoryReport}
      isHistoryLoading={isHistoryLoading}
      onLoadReport={onLoadReport}
      onDeleteReport={onDeleteReport}
      emptyMessage={emptyMessage}
      showAllUsers={showAllUsers}
      onToggleShowAllUsers={onToggleShowAllUsers}
      canViewAllUsers={canViewAllUsers} // ← ADD
    />
    // ...
  )
}
```

**6. HistoryPanel Component** (`frontend/src/components/Archive/HistoryPanel.tsx`)

- **File**: `frontend/src/components/Archive/HistoryPanel.tsx`
- **Line**: ~20-40 (Interface) and ~140-180 (Toggle UI)

**Current Interface**:

```typescript
interface HistoryPanelProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage?: string
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
}
```

**Change To**:

```typescript
interface HistoryPanelProps {
  reportHistory: any[]
  selectedHistoryReport: any | null
  isHistoryLoading: boolean
  onLoadReport: (reportId: string) => void
  onDeleteReport?: (reportId: string) => void
  emptyMessage?: string
  showAllUsers?: boolean
  onToggleShowAllUsers?: () => void
  canViewAllUsers?: boolean  // ← NEW
}

const HistoryPanel = ({
  /* ... other props ... */
  showAllUsers = false,
  onToggleShowAllUsers,
  canViewAllUsers = false,  // ← ADD with default
}: HistoryPanelProps) => {
```

**Update Toggle UI** (line ~140-180):

```tsx
{
  onToggleShowAllUsers &&
    canViewAllUsers && ( // ← ADD canViewAllUsers check
      <Tooltip
        content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
      >
        <HStack gap={2}>{/* ... rest of toggle UI ... */}</HStack>
      </Tooltip>
    )
}
```

**7. Knowledge Base Selection Modal** (`frontend/src/components/Common/KnowledgeBaseSelectionModal.tsx`)

- **File**: `frontend/src/components/Common/KnowledgeBaseSelectionModal.tsx`
- **Line**: ~9-20 (Interface) and ~50-80 (Toggle UI)

**Current Interface**:

```typescript
interface KnowledgeBaseSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBase: KnowledgeBasePublic | null
  onSelectionChange: (kb: KnowledgeBasePublic | null) => void
  showAllUsers: boolean
  toggleShowAllUsers: () => void
}
```

**Change To**:

```typescript
interface KnowledgeBaseSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  knowledgeBases: KnowledgeBasePublic[]
  selectedKnowledgeBase: KnowledgeBasePublic | null
  onSelectionChange: (kb: KnowledgeBasePublic | null) => void
  showAllUsers: boolean
  toggleShowAllUsers: () => void
  canViewAllUsers?: boolean  // ← NEW
}

const KnowledgeBaseSelectionModal = ({
  /* ... other props ... */
  showAllUsers,
  toggleShowAllUsers,
  canViewAllUsers = false,  // ← ADD with default
}: KnowledgeBaseSelectionModalProps) => {
```

**Update Toggle UI** (line ~50-80):

```tsx
{
  /* All Users Toggle */
}
{
  canViewAllUsers && ( // ← ADD: Conditional rendering
    <HStack justifyContent="flex-end" mt={2}>
      <Tooltip
        content={showAllUsers ? t("archive.viewingAllUsers") : t("archive.viewingMyHistory")}
        contentProps={{ zIndex: 3200 }}
      >
        {/* ... rest of toggle UI ... */}
      </Tooltip>
    </HStack>
  )
}
```

**8. Update All Components That Use KnowledgeBaseSelectionModal**

The following components need to pass the `canViewAllUsers` prop:

**a) ChatbotPanel** (`frontend/src/components/Chatbot/ChatbotPanel.tsx`)

- **File**: `frontend/src/components/Chatbot/ChatbotPanel.tsx`
- **Line**: ~74 and ~269

**Current Code**:

```tsx
const { knowledgeBases, showAllUsers, toggleShowAllUsers } = useKnowledgeBases()

// ... later:
<KnowledgeBaseSelectionModal
  isOpen={isKbModalOpen}
  onClose={handleKbModalClose}
  title={t("chatbot.selectKnowledgeBase")}
  knowledgeBases={knowledgeBases}
  selectedKnowledgeBase={selectedKnowledgeBase}
  onSelectionChange={setSelectedKnowledgeBase}
  showAllUsers={showAllUsers}
  toggleShowAllUsers={toggleShowAllUsers}
/>
```

**Change To**:

```tsx
const { knowledgeBases, showAllUsers, toggleShowAllUsers, canViewAllUsers } = useKnowledgeBases()

// ... later:
<KnowledgeBaseSelectionModal
  isOpen={isKbModalOpen}
  onClose={handleKbModalClose}
  title={t("chatbot.selectKnowledgeBase")}
  knowledgeBases={knowledgeBases}
  selectedKnowledgeBase={selectedKnowledgeBase}
  onSelectionChange={setSelectedKnowledgeBase}
  showAllUsers={showAllUsers}
  toggleShowAllUsers={toggleShowAllUsers}
  canViewAllUsers={canViewAllUsers}  // ← ADD
/>
```

**b-e) Review, Generate, Compare, and Match Tool Pages**

Apply the same pattern to:

- `frontend/src/routes/_layout/review.tsx`
- `frontend/src/routes/_layout/generate.tsx`
- `frontend/src/routes/_layout/compare.tsx`
- `frontend/src/routes/_layout/match.tsx`

Each needs:

1. Extract `canViewAllUsers` from `useKnowledgeBases` hook
2. Pass it to any `KnowledgeBaseSelectionModal` components

## 📊 Summary of Changes

### Backend Files to Modify (5 files):

1. ✅ `backend/app/api/routes/knowledgebases.py` - Add superuser check
2. ✅ `backend/app/api/routes/veradoc.py` - Add superuser check
3. ✅ `backend/app/api/routes/reportgenie.py` - Add superuser check
4. ✅ `backend/app/api/routes/twincheck.py` - Add superuser check
5. ✅ `backend/app/api/routes/formconnect.py` - Add superuser check

### Frontend Files to Modify (11+ files):

1. ✅ `frontend/src/hooks/useKnowledgeBases.ts` - Add canViewAllUsers
2. ✅ `frontend/src/hooks/useToolArchive.ts` - Add canViewAllUsers
3. ✅ `frontend/src/routes/_layout/knowledge-bases.tsx` - Conditional toggle rendering
4. ✅ `frontend/src/routes/_layout/archive.tsx` - Pass canViewAllUsers
5. ✅ `frontend/src/components/Archive/ToolTab.tsx` - Add prop and pass through
6. ✅ `frontend/src/components/Archive/HistoryPanel.tsx` - Conditional toggle rendering
7. ✅ `frontend/src/components/Common/KnowledgeBaseSelectionModal.tsx` - Conditional toggle rendering
8. ✅ `frontend/src/components/Chatbot/ChatbotPanel.tsx` - Pass canViewAllUsers
9. ✅ `frontend/src/routes/_layout/review.tsx` - Pass canViewAllUsers
10. ✅ `frontend/src/routes/_layout/generate.tsx` - Pass canViewAllUsers
11. ✅ `frontend/src/routes/_layout/compare.tsx` - Pass canViewAllUsers
12. ✅ `frontend/src/routes/_layout/match.tsx` - Pass canViewAllUsers

## 🔒 Security Considerations

### Defense in Depth

This implementation follows a **defense-in-depth** approach:

1. **Backend Layer**: API endpoints reject `show_all=true` requests from non-superusers with 403 Forbidden
2. **Frontend Layer**: UI hides the toggle from non-superusers, preventing confusion and accidental API calls

### Backward Compatibility

- Superusers will see no change in functionality
- The toggle remains visible and functional for superusers
- API responses remain the same format for all users

### Security Benefits

- **Prevents data leakage**: Non-superusers cannot view other users' data
- **Clear access control**: Superuser status clearly defines who can see all data
- **Audit trail**: 403 errors in logs can help identify unauthorized access attempts
- **Future-proof**: Centralized permission check can be extended later

## 🧪 Testing Strategy

### Backend Testing

1. Test with non-superuser account:
   - Call KB API with `show_all=true` → Should return 403
   - Call history APIs with `show_all=true` → Should return 403
2. Test with superuser account:
   - Call KB API with `show_all=true` → Should return all KBs
   - Call history APIs with `show_all=true` → Should return all history

### Frontend Testing

1. Test with non-superuser account:
   - Knowledge Bases tab → Toggle should be hidden
   - Archive tabs → Toggle should be hidden in all history panels
   - Tool modals → Toggle should be hidden in KB selection modals
2. Test with superuser account:
   - All toggles should be visible and functional
   - Switching toggle should fetch appropriate data

### Integration Testing

1. Test transition: Switch between regular user and superuser accounts
2. Test edge cases: Network errors, timeout scenarios
3. Test UI responsiveness: Layout should adapt properly when toggle is hidden

## 📝 Implementation Order

1. **Start with Backend** (ensures security first)

   - Implement all 5 backend API changes
   - Test with API client (Postman/Insomnia)

2. **Update Core Hooks** (centralized state management)

   - Update `useKnowledgeBases.ts`
   - Update `useToolArchive.ts`

3. **Update Primary Pages** (main user-facing features)

   - Update Knowledge Bases page
   - Update Archive page

4. **Update Components** (reusable UI pieces)

   - Update ToolTab component
   - Update HistoryPanel component
   - Update KnowledgeBaseSelectionModal component

5. **Update Tool Pages** (features using KB selection modal)

   - Update ChatbotPanel
   - Update Review, Generate, Compare, Match pages

6. **Test End-to-End**
   - Test with both regular and superuser accounts
   - Verify all toggles are hidden/shown appropriately
   - Verify API security works correctly

## ✅ Success Criteria

- [ ] Backend: Non-superusers receive 403 when using `show_all=true`
- [ ] Backend: Superusers can still use `show_all=true` successfully
- [ ] Frontend: Toggle is hidden from non-superusers in all locations
- [ ] Frontend: Toggle is visible and functional for superusers
- [ ] No console errors or warnings
- [ ] All existing functionality works for superusers
- [ ] Documentation updated (this file serves as documentation)

## 📚 References

### Key Patterns from Existing Codebase

- **Superuser Check Pattern**: See `SidebarItems.tsx` line 207 for admin panel visibility
- **Settings Tab Pattern**: See `settings.tsx` line 59 for conditional tab visibility
- **Toggle UI Pattern**: See `knowledge-bases.tsx` lines 220-260 for toggle implementation
- **Hook Pattern**: See `useKnowledgeBases.ts` for state management approach

### Files for Reference

- User Model: `backend/app/models.py` (lines 1-160)
- Auth Hook: `frontend/src/hooks/useAuth.ts` (lines 1-150)
- Knowledge Bases API: `backend/app/api/routes/knowledgebases.py` (line 709+)
- Archive APIs: See routes in `backend/app/api/routes/` directory

---

**Document Version**: 1.0  
**Created**: 2025-11-26  
**Status**: Planning Complete - Ready for Implementation
