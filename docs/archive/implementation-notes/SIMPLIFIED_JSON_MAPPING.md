# Simplified JSON-Based Document Section Mapping

## Overview

Completely rewrote the document section mapping approach to use a simple JSON format with intelligent handling of "Consult Documents" settings, eliminating complex text parsing and confidence tracking that was causing mapping failures.

## Key Changes

### 1. Consult Documents Awareness

The mapping now distinguishes between two types of outline sections:

- **[TOPIC/CONCEPT] sections** (Consult Documents = ON): Section descriptions are conceptual/topical. The LLM maps ground-truth content that relates to the same topic/concept, even if wording differs.
- **[LITERAL TEXT] sections** (Consult Documents = OFF): Section descriptions are literal text snippets. The LLM maps ground-truth content that contains the same or very similar text/wording.

### 2. Enhanced Mapping Prompt

**Before**: Complex multi-part prompt with various response sections (DOCUMENT_SECTIONS_IDENTIFIED, SECTION_MAPPINGS, SECTIONS, REASONING, CONFIDENCE)

**After**: Clean, simple prompt requesting only JSON response:

```json
{
  "mappings": [
    {
      "section_text": "brief description of the document section found",
      "outline_section": 1
    }
  ]
}
```

### 2. Removed Complexity

- **No more confidence tracking**: Eliminated High/Medium/Low confidence levels
- **No more reasoning extraction**: Removed complex text parsing for explanations
- **No more multi-field parsing**: Single JSON structure instead of multiple delimited sections
- **Simplified context**: Reduced contextual information passed to LLM

### 3. JSON-Only Response Parsing

- Uses `json.loads()` for reliable parsing
- Clear error handling with fallback to positional mapping
- Records identified document sections as a simple list
- Maps each identified section to exactly one outline section

### 4. Enhanced Debugging

- Logs exact JSON prompt sent to LLM
- Logs raw JSON response received
- Clear success/failure indicators
- Simplified mapping statistics without confidence distribution

## Benefits

1. **Reliability**: JSON parsing is much more reliable than text parsing
2. **Simplicity**: Fewer moving parts mean fewer failure points
3. **Clarity**: LLM gets clear, simple instructions
4. **Debugging**: Easier to see exactly what's being sent and received
5. **Performance**: Faster processing without complex text analysis

## Example Workflow

1. **Chunk Analysis**: LLM receives document chunk and outline sections
2. **Section Identification**: LLM identifies discrete sections within the chunk
3. **JSON Response**: LLM responds with structured mappings in JSON format
4. **Parsing**: System reliably parses JSON and extracts mappings
5. **Fallback**: If JSON parsing fails, uses simple positional mapping
6. **Assignment**: Content from identified sections gets assigned to outline sections

## JSON Response Format

```json
{
  "mappings": [
    {
      "section_text": "Title: EMG-Based Monitoring Study",
      "outline_section": 1
    },
    {
      "section_text": "Invitation to Participate paragraph",
      "outline_section": 2
    },
    {
      "section_text": "Study description and methodology",
      "outline_section": 3
    }
  ]
}
```

## Error Handling

- **JSON Parse Error**: Falls back to keyword/positional mapping
- **Invalid Section Numbers**: Ignores mappings to non-existent outline sections
- **Empty Response**: Uses positional mapping based on chunk position
- **Malformed JSON**: Logs error and uses fallback logic

## Expected Results

This simplified approach should result in:

- More consistent section assignments
- Fewer "No specific content was mapped" errors
- Clearer mapping of document sections to outline sections
- Better reliability and debugging capability
- Actual content appearing in the ground-truth mapping instead of entire chunks or empty assignments

The goal is to properly identify and map individual document sections (like titles, headers, paragraphs) rather than mapping entire processing chunks, leading to much more accurate optimization suggestions.
