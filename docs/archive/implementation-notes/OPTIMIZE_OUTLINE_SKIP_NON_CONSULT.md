# Optimize Outline - Skip Non-Consult-Documents Sections

## Overview

Modified the Optimize Outline functionality to skip optimization for sections that have "Consult Documents" set to false, while still mapping them in the ground truth document for completeness.

## Changes Made

### 1. Section Tracking Enhancement

- **Added `section_consult_settings` dictionary**: Tracks which sections consult documents during the content generation phase
- **Preserved setting**: Stores the `consultDocuments` flag for each section for later use during optimization

### 2. Optimization Logic Update

- **Skip optimization**: Sections with `consultDocuments: false` are not processed through the LLM optimization comparison
- **Add placeholder suggestions**: Non-consulting sections get a suggestion with:
  - `needs_revision: false`
  - Original section kept unchanged
  - Reason: "Section does not consult documents - optimization skipped"
  - Ground truth content: "Not applicable - section does not consult documents"

### 3. Enhanced Analytics

- **Section type statistics**: Analysis summary now shows:
  - Total sections that consult documents vs. those that don't
  - Number of sections actually optimized (excluding skipped ones)
  - Clear distinction between sections working well vs. skipped sections

### 4. Improved Logging

- **Clearer output**: Logs now distinguish between:
  - Sections being analyzed for optimization
  - Sections being skipped due to non-consultation setting
- **Better completion summary**: Shows how many document-consulting sections were optimized vs. skipped

## Technical Details

### Code Changes in `optimize_outline` function:

#### Step 5 - Content Generation:

```python
# Track which sections consult documents
section_consult_settings = {}
for section in current_sections:
    section_description = section["text"].strip()
    consult_documents = section.get("consultDocuments", True)
    section_consult_settings[section_description] = consult_documents
```

#### Step 7 - Optimization Comparison:

```python
for section_description, generated_content in generated_sections.items():
    consults_documents = section_consult_settings.get(section_description, True)

    if not consults_documents:
        # Skip optimization and add placeholder suggestion
        suggestions.append(OutlineSuggestion(
            original_section=section_description,
            suggested_section=section_description,  # Keep original
            reason="Section does not consult documents - optimization skipped",
            needs_revision=False,
        ))
        continue

    # Continue with normal optimization for consulting sections...
```

## Benefits

### 1. **Performance Improvement**

- Reduces LLM calls by skipping unnecessary optimization comparisons
- Faster processing for outlines with many literal text sections

### 2. **Logical Consistency**

- Non-consulting sections (literal text) don't need optimization since they don't use document context
- Focuses optimization efforts on sections that actually benefit from it

### 3. **Maintained Mapping**

- Ground truth document is still fully mapped to all sections
- Complete coverage analysis remains available
- Mapping statistics include all sections for completeness

### 4. **Clear User Feedback**

- UI will show skipped sections with clear reasoning
- Users understand why certain sections weren't optimized
- Analysis summary provides comprehensive statistics

## Example Output

For an outline with 5 sections where 2 have `consultDocuments: false`:

```
Enhanced Content Extraction Analysis:
- Total sections evaluated: 5
- Sections that consult documents: 3
- Sections that don't consult documents (skipped): 2
- Sections needing optimization: 1
- Sections working well: 2
```

This clearly shows that only the 3 document-consulting sections were analyzed, with 1 needing optimization.

## UI Impact

The frontend will display skipped sections with:

- ✓ "This section is already well-optimized" (since `needs_revision: false`)
- Reason explaining that optimization was skipped
- No accept/reject controls needed since no changes are suggested

## Files Modified

- `backend/app/api/routes/reportgenie.py` - Main optimization logic

## Backward Compatibility

- Existing functionality preserved for sections that consult documents
- Default behavior (`consultDocuments: true`) ensures existing outlines work unchanged
- API response format remains the same
