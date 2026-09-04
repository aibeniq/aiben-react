# Testing Checklist for PyMuPDF4LLM Optimization

## Prerequisites

- [ ] Backend environment is set up
- [ ] Dependencies are installed (PyMuPDF, PyMuPDF4LLM)
- [ ] Test PDFs available (with and without tables)

## Unit Tests

### 1. Fast Table Detection Function

- [ ] Test with PDF containing tables

  - Should return `(True, table_count)` where table_count > 0
  - Should complete in < 1 second

- [ ] Test with PDF without tables

  - Should return `(False, 0)`
  - Should complete in < 1 second

- [ ] Test with corrupted/invalid PDF
  - Should fail gracefully and return `(True, 0)` for safety

### 2. extract_pdf_with_pymupdf4llm()

- [ ] Test with `skip_table_check=False` (default) on PDF without tables

  - Should detect no tables
  - Should fall back to pypdf
  - Should return documents with `extraction_method: "pypdf_text"`

- [ ] Test with `skip_table_check=False` on PDF with tables

  - Should detect tables
  - Should use PyMuPDF4LLM
  - Should return documents with `extraction_method: "pymupdf4llm_markdown"`

- [ ] Test with `skip_table_check=True`
  - Should skip fast check
  - Should always use PyMuPDF4LLM

### 3. load_pdf_with_pypdf()

- [ ] Test with `use_enhanced_parsing=True` on PDF without tables

  - Should detect no tables
  - Should use pypdf extraction
  - Verify faster than PyMuPDF4LLM would be

- [ ] Test with `use_enhanced_parsing=True` on PDF with tables

  - Should detect tables
  - Should use PyMuPDF4LLM
  - Should extract table content properly

- [ ] Test with `use_enhanced_parsing=False`
  - Should always use pypdf
  - Should not run table detection

### 4. extract_text_from_pdf_bytes()

- [ ] Test with `use_enhanced_parsing=True` on PDF bytes without tables

  - Should detect no tables
  - Should use pypdf extraction

- [ ] Test with `use_enhanced_parsing=True` on PDF bytes with tables
  - Should detect tables
  - Should use PyMuPDF4LLM
  - Table content should be preserved

## Integration Tests

### 5. Knowledge Base Upload

- [ ] Upload PDF without tables

  - Check logs for "No tables detected"
  - Verify fast processing time

- [ ] Upload PDF with tables
  - Check logs for "Tables detected"
  - Verify table content is properly extracted and searchable

### 6. Document Processing Routes

- [ ] Test `/veradoc` endpoint with PDF without tables
- [ ] Test `/veradoc` endpoint with PDF with tables
- [ ] Test `/reportgenie` endpoint with various PDFs
- [ ] Test `/formconnect` endpoint with forms (likely have tables)
- [ ] Test `/chatbot` endpoint with knowledge base PDFs

### 7. Batch Processing

- [ ] Upload multiple PDFs (mix of with/without tables)
  - Verify appropriate method used for each
  - Compare total processing time vs. before optimization

## Performance Tests

### 8. Benchmark Tests

Run `test_fast_table_detection.py` with:

- [ ] Simple text PDF (no tables)

  - Record fast detection time
  - Record total processing time
  - Verify optimization was applied

- [ ] Data-heavy PDF (with tables)

  - Record fast detection time
  - Record total processing time
  - Verify PyMuPDF4LLM was used

- [ ] Large batch (50+ PDFs)
  - Record total time before optimization (if possible)
  - Record total time after optimization
  - Calculate speedup factor

## Edge Cases

### 9. Error Handling

- [ ] Test with empty PDF
- [ ] Test with password-protected PDF
- [ ] Test with scanned PDF (images only)
- [ ] Test with very large PDF (1000+ pages)
- [ ] Test with malformed PDF

### 10. Configuration

- [ ] Test with `USE_ENHANCED_PDF_PARSING=True` in config
  - Optimization should be active
- [ ] Test with `USE_ENHANCED_PDF_PARSING=False` in config
  - Should always use basic pypdf
  - Fast check should not run

### 11. PyMuPDF4LLM Unavailable

- [ ] Test when PyMuPDF4LLM is not installed
  - Should fall back to pypdf gracefully
  - No crashes or errors

## Logging Verification

### 12. Log Output

- [ ] Verify clear logging for table detection results

  - "Fast table detection: Found X table(s)"
  - "Fast table detection: No tables found"

- [ ] Verify clear logging for method selection

  - "Tables detected, using PyMuPDF4LLM"
  - "No tables detected, using fast pypdf extraction"

- [ ] Verify error logging is informative
  - "Error during fast table detection: ..."

## Regression Tests

### 13. Existing Functionality

- [ ] All existing unit tests still pass
- [ ] No breaking changes to API endpoints
- [ ] Document extraction quality unchanged
- [ ] Table extraction quality unchanged (when tables present)

## Documentation

### 14. Documentation Complete

- [ ] PYMUPDF4LLM_OPTIMIZATION.md created
- [ ] PYMUPDF4LLM_OPTIMIZATION_FLOW.md created
- [ ] Test script `test_fast_table_detection.py` created
- [ ] Inline code comments are clear

## Quick Test Commands

```bash
# Run the test script
python test_fast_table_detection.py path/to/test.pdf

# Run existing unit tests
cd backend
pytest test_pymupdf4llm_integration.py -v

# Run all tests
pytest -v

# Check for any import errors
python -c "from app.services.pdf_utils import has_tables_fast, load_pdf_with_pypdf; print('✓ Imports successful')"
```

## Expected Results Summary

| Test Type      | PDF Type              | Expected Behavior  | Expected Speed |
| -------------- | --------------------- | ------------------ | -------------- |
| Fast check     | No tables             | Returns (False, 0) | < 0.5s         |
| Fast check     | With tables           | Returns (True, n)  | < 0.5s         |
| Full process   | No tables             | Uses pypdf         | ~1s            |
| Full process   | With tables           | Uses PyMuPDF4LLM   | ~5-10s         |
| Batch 100 PDFs | 80 no tables, 20 with | Mixed methods      | ~150-250s      |

## Success Criteria

✅ **Performance**: 5-10x faster for PDFs without tables
✅ **Quality**: Same extraction quality as before
✅ **Reliability**: No crashes or errors
✅ **Logging**: Clear decision-making visible in logs
✅ **Compatibility**: All existing tests pass

## Notes

- The optimization is transparent to calling code
- Existing function signatures unchanged
- Backward compatible with all current usage
- Safe fallback on errors (assumes tables present)

---

**Test Date**: ******\_******
**Tester**: ******\_******
**Result**: ✅ PASS / ❌ FAIL
**Notes**: ******\_******
