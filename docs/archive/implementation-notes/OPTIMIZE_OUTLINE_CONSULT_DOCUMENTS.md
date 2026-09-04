# Optimize Outline - Consult Documents Integration

## Overview

This document describes the enhancement made to the `optimize_outline` functionality to respect the "Consult Documents" setting for each section, making it consistent with the main `generate_report` functionality.

## Problem

Previously, the optimize outline functionality would always generate content for sections by consulting the knowledge base, regardless of whether the section had "Consult Documents" set to true or false. This was inconsistent with the main report generation functionality where sections with "Consult Documents" set to false would use the section description directly as the content.

## Solution

Updated the optimize outline functionality to check the `consultDocuments` flag for each section and handle them accordingly:

### Code Changes

**File**: `c:\miniconda\aibeniq-react\backend\app\api\routes\reportgenie.py`

**Function**: `optimize_outline` - Section 5 (Generate report content for each section)

### New Logic

```python
for section in current_sections:
    section_description = section["text"].strip()
    consult_documents = section.get("consultDocuments", True)  # Default to True

    if consult_documents:
        # Original behavior: Generate content using knowledge base
        docs = retriever.get_relevant_documents(section_description)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Build report draft and generate content using LLM
        generated_content = invoke_llm(
            llm,
            settings.REPORT_GENIE_PROMPT_TEMPLATE,
            {
                "report_draft": report_draft,
                "context": context,
                "question": section_description,
            },
        )
    else:
        # New behavior: Use section description directly as content
        generated_content = section_description
```

### Key Changes

1. **Extract `consultDocuments` flag**: `consult_documents = section.get("consultDocuments", True)`
2. **Conditional processing**: Only consult knowledge base if `consult_documents` is True
3. **Direct content usage**: When `consult_documents` is False, use `section_description` directly as `generated_content`
4. **Enhanced logging**: Different log messages for consulted vs non-consulted sections

### Benefits

1. **Consistency**: Optimize outline now behaves the same as main report generation
2. **Performance**: Sections with "Consult Documents" disabled skip LLM processing
3. **Accuracy**: Ground-truth comparison is now done against the actual content that would be generated
4. **User Control**: Users can control which sections should consult documents during optimization

### Behavior Alignment

| Section Setting           | Main Generate              | Optimize Outline (Before) | Optimize Outline (After)     |
| ------------------------- | -------------------------- | ------------------------- | ---------------------------- |
| `consultDocuments: true`  | Uses LLM + KB              | Uses LLM + KB             | Uses LLM + KB ✓              |
| `consultDocuments: false` | Uses section text directly | Uses LLM + KB ❌          | Uses section text directly ✓ |

### Example Usage

**Outline with mixed settings**:

```json
[
  {
    "text": "Executive Summary",
    "consultDocuments": true
  },
  {
    "text": "Methodology used in this analysis",
    "consultDocuments": false
  },
  {
    "text": "Key Findings",
    "consultDocuments": true
  }
]
```

**Optimization behavior**:

- "Executive Summary": Will generate content using knowledge base and LLM
- "Methodology used in this analysis": Will use the text directly as content
- "Key Findings": Will generate content using knowledge base and LLM

### Implementation Details

1. **Default behavior**: If `consultDocuments` is not specified, defaults to `true` (maintaining backward compatibility)
2. **Logging**: Clear distinction in logs between sections that consult documents vs those that don't
3. **Performance impact**: Positive performance impact for sections that don't consult documents (no LLM calls)
4. **Memory usage**: Reduced for non-consulted sections (no retrieval or context building)

### Testing Considerations

When testing the optimize outline functionality:

1. **Test with all sections having `consultDocuments: true`** - should behave as before
2. **Test with all sections having `consultDocuments: false`** - should use section text directly
3. **Test with mixed settings** - should handle each section according to its setting
4. **Test backward compatibility** - sections without `consultDocuments` should default to true

### Future Enhancements

1. **Search type support**: Could extend to support `searchType` parameter like main generate function
2. **Content validation**: Could add validation to ensure non-consulted sections have meaningful content
3. **Analytics**: Could track optimization effectiveness differently for consulted vs non-consulted sections

## Conclusion

This enhancement ensures that the optimize outline functionality respects user preferences for document consultation, making it consistent with the main report generation functionality and giving users full control over how their outline sections are processed during optimization.
