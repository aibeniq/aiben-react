# Optimize Outline - Editable UI Implementation

## Overview

Successfully implemented editable UI for the Optimize Outline functionality that matches the Veradoc/Review experience. Users can now manually edit suggested revisions and accept/reject them individually.

## Key Features

### 1. Manual Editing of Suggestions

- **Edit Icon**: Click the edit icon (FiEdit3) next to any suggested section description
- **Textarea Mode**: Switches to an editable textarea for inline editing
- **Save/Cancel**: Save changes with FiSave icon or cancel with FiX icon
- **Click to Edit**: Can also click directly on the suggestion text to start editing

### 2. Accept/Reject Toggle

- **Accept Button**: Toggle between "Accept" and "Accepted" states
- **Visual Feedback**: Accepted suggestions show green solid button with checkmark
- **Selective Application**: Only accepted suggestions are applied to the outline

### 3. Enhanced Content Display

- **Expandable Content**: Long generated content can be expanded/collapsed with "Show More/Less" buttons
- **Card Layout**: Clean card-based layout similar to OptimizeChecklistModal
- **Color Coding**: Blue highlighting for suggested changes, consistent with existing patterns

### 4. Improved State Management

- **Persistent Edits**: Edited suggestions are preserved until explicitly reset
- **Default Acceptance**: All suggestions that need revision are accepted by default
- **Clean State Reset**: All editing state cleared when modal is closed

## UI Components Used

### Icons (from react-icons/fi)

- `FiCheck`: Accept/accepted state indicator
- `FiEdit3`: Edit mode trigger
- `FiSave`: Save edited suggestion
- `FiX`: Cancel editing

### Chakra UI Components

- `Card.Root` and `Card.Body`: Clean card layout for suggestions
- `IconButton`: Edit/save/cancel actions
- `Button`: Accept/reject toggles and expand/collapse
- `Textarea`: Inline editing interface
- `HStack`/`VStack`: Layout structure

## State Variables

```tsx
const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<number>>(new Set())
const [editingSuggestions, setEditingSuggestions] = useState<Map<number, string>>(new Map())
const [editingModes, setEditingModes] = useState<Set<number>>(new Set())
const [expandedContent, setExpandedContent] = useState<Set<number>>(new Set())
```

## Key Functions

### `toggleSuggestion(index: number)`

Toggles the acceptance state of a suggestion.

### `startEditingSuggestion(index: number)`

Enters edit mode for a specific suggestion and initializes the editing state.

### `saveEditedSuggestion(index: number)`

Saves the edited suggestion and exits edit mode.

### `cancelEditingSuggestion(index: number)`

Cancels editing and reverts to the original suggestion.

### `getSuggestionText(index: number)`

Gets the current text for a suggestion (edited version if available, otherwise original).

### `handleApplyOptimizations()`

Applies only the accepted suggestions to create the optimized outline.

## User Experience

1. **Upload Document**: User uploads a ground-truth document for comparison
2. **Review Suggestions**: System presents suggestions with reasons and context
3. **Edit as Needed**: User can click edit icons or suggestion text to modify
4. **Accept/Reject**: Toggle acceptance for each suggestion individually
5. **Apply Selected**: Only accepted (and optionally edited) suggestions are applied

## Consistency with Veradoc/Review

The implementation follows the exact same patterns as `OptimizeChecklistModal.tsx`:

- Same icon usage and placement
- Same editing interaction patterns
- Same color schemes and visual feedback
- Same state management approach
- Same card-based layout structure

## Files Modified

- `frontend/src/components/Generate/OptimizeOutlineModal.tsx`

## Backend Compatibility

The implementation works with the existing backend API without requiring changes. The edited suggestions are processed client-side and sent as the final optimized sections.

## Testing Recommendations

1. Upload a ground-truth document
2. Verify suggestions appear with edit icons
3. Test editing functionality (click edit, modify text, save/cancel)
4. Test accept/reject toggles
5. Verify only accepted suggestions are applied
6. Test state cleanup on modal close
