# FormConnect Filename Display Enhancement

## Problem

When using the Match/FormConnect functionality to compare multiple documents, the output tables displayed generic column headers like "Document 1", "Document 2", etc., instead of showing the actual filenames of the input documents.

## Solution Implemented

### Enhanced `compare_multiple_documents` Function

**File**: `backend/app/api/routes/formconnect.py`
**Function**: `compare_multiple_documents` (around line 572)

#### Key Changes:

1. **Filename Cleaning**: Removes suffixes like " (digitized)" and " (handwritten)" to show clean filenames
2. **Enhanced Document Representation**: Includes actual filenames in the document data structure
3. **Explicit Prompt Instructions**: Provides clear instructions to the LLM to use actual filenames
4. **Filename List**: Provides a separate list of filenames for reference

#### Implementation Details:

```python
# Clean filenames and create structured document representation
for i, (doc, name) in enumerate(zip(documents, file_names)):
    # Clean the filename (remove " (digitized)" or " (handwritten)" suffix)
    clean_filename = name.replace(" (digitized)", "").replace(" (handwritten)", "")
    clean_filenames.append(clean_filename)

    # Convert dict to string, escaping any curly braces for the formatter
    doc_str = str(doc).replace("{", "{{").replace("}", "}}")
    documents_str += f"Document: {clean_filename}\nExtracted Data: {doc_str}\n\n"
```

#### Enhanced Prompt Template:

```python
enhanced_prompt_template = """Compare the extracted fields across the following documents and provide a detailed analysis.

IMPORTANT: When referring to documents in your analysis and tables, use the actual document filenames provided below, NOT generic labels like "Document 1", "Document 2", etc.

Document Filenames:
{filename_list}

Documents to compare:
{documents_str}

Instructions:
1. Create a comparison table showing field values across all documents
2. Use the actual document filenames as column headers in any tables
3. Identify discrepancies and highlight the most likely correct values
4. Provide a summary of findings
5. If creating markdown tables, use the document filenames as column headers

Format your response in markdown with clear tables and analysis."""
```

## Expected Results

### Before Enhancement:

```markdown
| Field | Document 1 | Document 2 | Analysis  |
| ----- | ---------- | ---------- | --------- |
| Name  | John Doe   | John Smith | Different |
```

### After Enhancement:

```markdown
| Field | contract_v1.pdf | contract_v2.pdf | Analysis  |
| ----- | --------------- | --------------- | --------- |
| Name  | John Doe        | John Smith      | Different |
```

## Benefits

1. **Improved Traceability**: Users can immediately identify which document contains which values
2. **Better User Experience**: Clear, meaningful column headers instead of generic labels
3. **Professional Output**: More professional-looking comparison tables
4. **Easier Analysis**: Users can quickly understand which version of a document has specific values

## Testing

To test this enhancement:

1. Upload multiple documents with different filenames to FormConnect
2. Use the Match functionality to compare them
3. Verify that the output table shows actual filenames as column headers
4. Check that filenames are cleaned (no "(digitized)" or "(handwritten)" suffixes)

## Backward Compatibility

This enhancement is fully backward compatible:

- Existing functionality remains unchanged
- No breaking changes to API contracts
- Graceful handling of edge cases (missing filenames, etc.)

## Technical Notes

- Filenames are cleaned to remove processing type suffixes
- The prompt explicitly instructs the LLM to use actual filenames
- Filename list is provided separately for additional context
- Document structure includes both filename and extracted data clearly labeled

## Implementation Status: ✅ COMPLETE

The enhancement has been successfully implemented and is ready for testing. Users should now see actual document filenames in FormConnect comparison table headers instead of generic "Document 1", "Document 2" labels.
