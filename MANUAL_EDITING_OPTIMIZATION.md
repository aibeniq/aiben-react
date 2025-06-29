# Manual Editing for Optimization Suggestions

## Overview

The Optimize Checklist feature now allows users to manually edit the suggested question text before accepting optimization suggestions. This provides greater flexibility and control over the final optimized questions.

## New Features

### Manual Editing in OptimizeChecklistModal

- **Edit Icon**: Each suggested question now has a small edit icon (pencil) next to it
- **Inline Editing**: Click the edit icon or the suggestion text to enable editing mode
- **Textarea Input**: The suggestion becomes editable in a resizable textarea
- **Save/Cancel**: Use the save (checkmark) or cancel (X) buttons to confirm or discard changes
- **Hover Effects**: Suggestions have hover effects to indicate they're clickable

### Manual Editing in ChecklistModal

- **Embedded Optimization**: The same editing functionality is available in the checklist modal's optimization section
- **Real-time Updates**: Edited suggestions are applied directly to the checklist when accepted
- **Persistent Edits**: Edited text is preserved until the optimization session is closed

## User Experience

1. **Start Optimization**: Upload a test document and run optimization analysis
2. **Review Suggestions**: Each suggestion shows:
   - Original question
   - Suggested question (editable)
   - Reason for change
   - Current answer that triggered the suggestion
3. **Edit Suggestions**:
   - Click the edit icon or suggestion text to start editing
   - Modify the suggested question as needed
   - Save changes or cancel to revert
4. **Accept/Reject**: Use the Accept button to select which suggestions to apply
5. **Apply Changes**: Apply all accepted suggestions (including edited ones) to the checklist

## Technical Implementation

### State Management

- `editingSuggestions`: Map<number, string> - Stores edited suggestion text by index
- `editingModes`: Set<number> - Tracks which suggestions are currently being edited

### Key Functions

- `startEditingSuggestion(index)`: Enables editing mode for a suggestion
- `cancelEditingSuggestion(index)`: Cancels editing and reverts to original
- `saveEditedSuggestion(index)`: Saves the edited text and exits editing mode
- `updateEditingSuggestion(index, value)`: Updates the editing text in real-time
- `getSuggestionText(index)`: Returns edited text if available, otherwise original suggestion

### UI Components

- **Textarea**: Resizable input for editing suggestions
- **IconButton**: Edit, save, and cancel buttons with appropriate icons
- **Hover States**: Visual feedback for interactive elements

## Benefits

1. **Improved Control**: Users can fine-tune AI suggestions to match their specific needs
2. **Flexibility**: No need to choose between accepting or rejecting - users can modify
3. **Better Outcomes**: Combines AI intelligence with human expertise
4. **User Satisfaction**: Reduces friction in the optimization process

## Usage Tips

- **Click to Edit**: Both the edit icon and the suggestion text are clickable
- **Save Changes**: Remember to save your edits before accepting suggestions
- **Review Carefully**: Edited suggestions will be applied exactly as written
- **Cancel Anytime**: Use the cancel button to revert unwanted changes

## Future Enhancements

- **Undo/Redo**: Add undo/redo functionality for edited suggestions
- **Suggestion Templates**: Provide common editing patterns or templates
- **Validation**: Add validation to ensure edited questions maintain their intent
- **History**: Track editing history for learning and improvement
