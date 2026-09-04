# Custom Instructions Implementation - Optimize Outline

## Overview

Custom instructions are now properly integrated into the Optimize Outline backend functionality. This ensures that user-provided custom instructions affect both content generation and optimization analysis.

## Implementation Details

### Changes Made

#### Backend Files Modified:

1. **`backend/app/api/routes/reportgenie.py`**

   - Updated content generation LLM call (line ~1143-1156)
   - Updated optimization analysis LLM call (line ~1705-1718)
   - Enhanced debug logging to show when custom instructions are applied

2. **`backend/app/core/config.py`**
   - Updated `REPORT_GENIE_PROMPT_TEMPLATE` to include `{custom_instructions}` placeholder
   - Updated `REPORTGENIE_OPTIMIZE_OUTLINE_PROMPT_TEMPLATE` to include `{custom_instructions}` placeholder

### How Custom Instructions Are Applied

#### Content Generation (Section Generation)

- Custom instructions are added to the template variables with the format:
  ```
  ADDITIONAL CUSTOM INSTRUCTIONS:
  {user_custom_instructions}
  ```
- They appear in the prompt between the standard instructions and the format requirements
- Debug log: "✓ Applying custom instructions to content generation for section: {section_name}..."

#### Optimization Analysis

- Custom instructions are added to the template variables with the format:
  ```
  ADDITIONAL CUSTOM INSTRUCTIONS FOR OPTIMIZATION:
  {user_custom_instructions}
  ```
- They appear in the prompt after the ground-truth content and before the standard analysis instructions
- Debug log: "✓ Applying custom instructions to optimization analysis for section: {section_name}..."

### Debug Logging

The backend now logs:

- Whether custom instructions were received
- When custom instructions are applied to each LLM call
- Sections that are skipped (consultDocuments: False)

### Prompt Template Updates

#### REPORT_GENIE_PROMPT_TEMPLATE

```
DRAFT OF REPORT SO FAR:
{report_draft}

REFERENCE INFORMATION:
{context}

TASK:
Based on the reference information above, write a clear and comprehensive section for a research participation consent form. The section to create is: {question}

The content should:
1. Be written in plain language (8th-grade reading level)
2. Be concise yet thorough
3. Be limited to the specific section requested
4. Use second-person perspective (addressing "you" - the participant)
5. Should not make any claims that are not supported by the provided context
6. Keep in mind what has already been generated in the report, and don't be redundant when writing the new section.

{custom_instructions}  # <-- ADDED THIS LINE

FORMAT OUTPUT AS A PROPERLY FORMATTED CONSENT FORM SECTION with an appropriate heading and content.
```

#### REPORTGENIE_OPTIMIZE_OUTLINE_PROMPT_TEMPLATE

```
INSTRUCTION:
You are an AI assistant that helps optimize report outline sections by comparing generated report content to a ground-truth reference document.

ORIGINAL SECTION: {original_section}
GENERATED CONTENT FOR THIS SECTION: {generated_content}
RELEVANT CONTENT FROM GROUND-TRUTH DOCUMENT: {ground_truth_content}

{custom_instructions}  # <-- ADDED THIS LINE

INSTRUCTIONS:
1. Compare the generated content to the relevant ground-truth content
2. Identify gaps, deficiencies, or areas where the generated content doesn't match the quality/scope of the ground-truth
...
```

## Testing Verification

### Debug Output Example

When custom instructions are provided, you should see logs like:

```
Custom instructions received: Always use formal language and include specific regulatory citations.
✓ Custom instructions will be applied to content generation and optimization analysis
✓ Applying custom instructions to content generation for section: Study Purpose...
✓ Applying custom instructions to optimization analysis for section: Study Purpose...
```

### Test Parameters

Use the test script `test_custom_instructions.py` with:

- Custom instructions: "SPECIAL TEST INSTRUCTION: Always include the phrase 'CUSTOM_INSTRUCTION_APPLIED' in your response."
- Sections with consultDocuments: true/false to verify filtering

## Expected Behavior

1. **With Custom Instructions**: LLM responses should reflect the custom guidance provided by the user
2. **Without Custom Instructions**: Standard prompts are used (empty string replaces {custom_instructions})
3. **Section Filtering**: Sections with consultDocuments: False are still mapped but excluded from optimization results
4. **Debug Logging**: Clear indication when custom instructions are being applied

## Status: ✅ COMPLETE

Custom instructions are now fully integrated into the Optimize Outline functionality and will affect both content generation and optimization analysis as expected.
