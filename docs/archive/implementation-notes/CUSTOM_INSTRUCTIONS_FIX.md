# Custom Instructions Fix for Optimization

## Issue Identified

The custom instructions functionality in the ChecklistModal optimization section was incorrectly positioned as "optimization-specific" instructions, when it should be exactly the same as the review functionality's custom instructions.

## Root Cause

The original implementation had optimization-focused placeholder text and description:

- **Incorrect Placeholder**: "Enter any additional instructions for optimization analysis (e.g., 'Focus on pediatric study requirements'...)"
- **Incorrect Description**: "These instructions will be considered when analyzing questions."

This gave users the wrong impression that they should enter instructions specifically about how to optimize questions, rather than instructions for the actual review process.

## Correct Purpose

The custom instructions in optimization mode should:

- **Simulate realistic review conditions** during optimization analysis
- **Use the exact same instructions** that would be used during actual document reviews
- **Help determine how questions perform** under real review scenarios

## Fix Applied

### ChecklistModal.tsx

Updated the custom instructions section to match the Review page:

**Fixed Placeholder**:

```
"Enter any additional instructions that should be considered when answering the checklist questions..."
```

**Fixed Description**:

```
"These instructions will be used during optimization analysis to simulate realistic review conditions."
```

### Documentation Updates

Updated `CUSTOM_INSTRUCTIONS_FEATURE.md` to:

- Clarify that custom instructions are identical in both modes
- Explain that optimization mode simulates realistic review conditions
- Remove optimization-specific example instructions
- Add note about simulating realistic review conditions

## Result

Now users understand that:

1. ✅ Custom instructions should be the same for both Review and Optimization
2. ✅ The purpose is to simulate realistic review conditions during optimization
3. ✅ Instructions should focus on the document evaluation context, not optimization methodology
4. ✅ This ensures optimization analysis reflects real-world usage scenarios

## Example Correct Usage

**Good Custom Instructions** (same for both Review and Optimization):

- "Consider this is a pediatric study when evaluating age-related requirements"
- "This protocol is for a low-risk intervention, apply appropriate risk assessment criteria"
- "Focus on international regulatory requirements rather than US-specific guidelines"

**Bad Custom Instructions** (the previous optimization-focused approach):

- "Focus on pediatric study requirements" ❌ (too vague)
- "Ensure questions are suitable for regulatory compliance" ❌ (optimization-focused)
- "Focus on patient safety considerations in the optimization analysis" ❌ (meta-optimization)
