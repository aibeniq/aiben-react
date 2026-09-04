# Comprehensive Processing Settings Test Suite

## Overview

This document describes the comprehensive test suite for validating processing settings across ALL LLM-powered functionalities in the application.

**Test File**: `test_all_processing_settings.py`

## Purpose

Validates that the three processing settings parameters work correctly across all functionalities:

- **Search Mode**: `vector` vs `full_scan`
- **Vision Analysis**: `true` vs `false`
- **PDF Parsing**: `enhanced` vs `basic`

Each functionality is tested with all 8 combinations (2×2×2) of these parameters.

## Tested Functionalities

The test suite covers **10 LLM-powered functionalities**:

### 1. Review (VeraDoc)

- **Endpoint**: `/api/v1/veradoc/process-rag`
- **Test Function**: `test_combination()`
- **Description**: Tests the Review page's document processing with RAG
- **Result Hash**: Based on questions and suggested sections

### 2. Generate Report (ReportGenie)

- **Endpoint**: `/api/v1/reportgenie/generate-report`
- **Test Function**: `test_generate_report()`
- **Description**: Tests report generation from knowledge base
- **Result Hash**: Based on generated report content

### 3. Match Form (FormConnect)

- **Endpoint**: `/api/v1/formconnect/process`
- **Test Function**: `test_match_form()`
- **Description**: Tests form field matching and filling
- **Result Hash**: Based on filled_fields dictionary

### 4. Chatbot Knowledge Base

- **Endpoint**: `/api/v1/chatbot/query-knowledge-base`
- **Test Function**: `test_chatbot_kb()`
- **Description**: Tests chatbot queries against a knowledge base
- **Result Hash**: Based on chatbot answer text

### 5. Chatbot Document

- **Endpoint**: `/api/v1/chatbot/query-document`
- **Test Function**: `test_chatbot_doc()`
- **Description**: Tests chatbot queries against a specific document
- **Result Hash**: Based on chatbot answer text

### 6. Generate Questions Modal (VeraDoc)

- **Endpoint**: `/api/v1/veradoc/generate-questions-with-files`
- **Test Function**: `test_generate_questions()`
- **Description**: Tests checklist question generation from files
- **Result Hash**: Based on generated questions array

### 7. Generate Outline Modal (ReportGenie)

- **Endpoint**: `/api/v1/reportgenie/generate-outline-json`
- **Test Function**: `test_generate_outline()`
- **Description**: Tests outline generation from files
- **Result Hash**: Based on outline structure array

### 8. Generate Form Fields Modal (FormConnect)

- **Endpoint**: `/api/v1/formconnect/generate-fields-with-files`
- **Test Function**: `test_generate_fields()`
- **Description**: Tests form field generation from files
- **Result Hash**: Based on generated fields array

### 9. Optimize Checklist Modal (VeraDoc)

- **Endpoint**: `/api/v1/veradoc/optimize-checklist`
- **Test Function**: `test_optimize_checklist()`
- **Description**: Tests checklist optimization with existing questions
- **Result Hash**: Based on optimized questions array
- **Note**: First generates initial questions, then optimizes them

### 10. Optimize Outline Modal (ReportGenie)

- **Endpoint**: `/api/v1/reportgenie/optimize-outline`
- **Test Function**: `test_optimize_outline()`
- **Description**: Tests outline optimization with existing outline
- **Result Hash**: Based on optimized outline array
- **Note**: First generates initial outline, then optimizes it

## Test Configuration

```python
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "david@aiben.io"
PASSWORD = "password123456"
TEST_FILE = "test_files/swedish fish.pdf"
KB_ID = "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e"

# Parameter combinations
SEARCH_MODES = ["vector", "full_scan"]
VISION_ANALYSIS = [True, False]
PDF_PARSING = ["enhanced", "basic"]
```

## Test Execution

### Running the Tests

```bash
python test_all_processing_settings.py
```

### Test Flow

1. **Login** - Authenticates with session-based auth
2. **For Each Functionality**:
   - Run 8 tests (all parameter combinations)
   - Collect results with MD5 hash of output
   - Analyze parameter impact
   - Display summary
3. **Overall Summary** - Aggregate results across all functionalities

### Expected Duration

- **Per test**: ~2-10 seconds (varies by functionality)
- **Per functionality**: ~8-80 seconds (8 tests + delays)
- **Total suite**: ~20-30 minutes (10 functionalities × 8 tests + delays)

## Analysis Metrics

For each functionality, the test analyzes:

### 1. Search Mode Impact

- Compares results between `vector` and `full_scan`
- Groups by vision_analysis and pdf_parsing
- Reports how many combinations show differences

### 2. Vision Analysis Impact

- Compares results between `true` and `false`
- Groups by search_mode and pdf_parsing
- Reports how many combinations show differences

### 3. PDF Parsing Impact

- Compares results between `enhanced` and `basic`
- Groups by search_mode and vision_analysis
- Reports how many combinations show differences

### 4. Overall Uniqueness

- Counts unique result hashes
- Calculates uniqueness ratio
- Ideal: 8/8 unique (100%)

## Success Criteria

### Per Functionality

- ✅ All 8 tests complete successfully
- ✅ Parameters produce different results
- ✅ No duplicate hashes (100% unique)

### Overall

- ✅ All 10 functionalities tested
- ✅ Total: 80 tests (10 × 8)
- ✅ Each functionality validates parameter impact

## Output Example

```
================================================================================
COMPREHENSIVE PROCESSING SETTINGS TEST - ALL FUNCTIONALITIES
================================================================================
Test file: test_files/swedish fish.pdf
Using KB: 7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e

Functionalities to test:
  1. Review (VeraDoc process-rag)
  2. Generate Report (ReportGenie)
  3. Match Form (FormConnect)
  ...

[Test 1/8] 1. Review (process-rag)
Parameters: vector+vision_True+pdf_enhanced
  ✅ SUCCESS (hash: a1b2c3d4, time: 5.23s, length: 2341)

...

================================================================================
ANALYSIS: PARAMETER IMPACT
================================================================================

1. SEARCH MODE IMPACT (vector vs full_scan)
--------------------------------------------------------------------------------
  Vision=True, PDF=enhanced: DIFFERENT (vector=a1b2c3d4, full_scan=e5f6g7h8)
  Vision=True, PDF=basic: DIFFERENT (vector=i9j0k1l2, full_scan=m3n4o5p6)
  ...

Result: 4/4 combinations show difference
✅ Search mode parameter IS working!

...

4. OVERALL UNIQUENESS
--------------------------------------------------------------------------------
Total tests run: 8
Unique results: 8
Uniqueness ratio: 8/8 = 100.0%
✅ ALL RESULTS UNIQUE - All parameters working!

...

================================================================================
OVERALL TEST SUMMARY - ALL FUNCTIONALITIES
================================================================================

1. Review (process-rag):
  Tests: 8
  Time: 42.35s
  Uniqueness: 8/8 unique

2. Generate Report:
  Tests: 8
  Time: 58.12s
  Uniqueness: 8/8 unique

...

================================================================================
GRAND TOTAL:
  Total tests across all functionalities: 80
  Total time: 1234.56s (20.6 minutes)
  Average time per test: 15.43s
================================================================================
ALL TESTS COMPLETE
================================================================================
```

## Troubleshooting

### Common Issues

1. **Login Failed**

   - Verify credentials in configuration
   - Check backend is running on localhost:8000

2. **Test File Not Found**

   - Ensure `test_files/swedish fish.pdf` exists
   - Check file path is relative to script location

3. **Knowledge Base Not Found**

   - Verify KB_ID exists in database
   - Ensure KB contains the test file

4. **Endpoint Errors**

   - Check all backend services are running
   - Verify API routes match current backend

5. **Parameter Not Working**
   - Review backend implementation
   - Check parameter is passed through all layers
   - Verify core processing functions use the parameter

## File Structure

```python
test_all_processing_settings.py
├── Configuration (BASE_URL, credentials, parameters)
├── login() - Authentication
├── Test Functions (one per functionality)
│   ├── test_combination() - Review
│   ├── test_generate_report() - Generate
│   ├── test_match_form() - Match
│   ├── test_chatbot_kb() - Chatbot KB
│   ├── test_chatbot_doc() - Chatbot Doc
│   ├── test_generate_questions() - Questions Modal
│   ├── test_generate_outline() - Outline Modal
│   ├── test_generate_fields() - Fields Modal
│   ├── test_optimize_checklist() - Optimize Checklist
│   └── test_optimize_outline() - Optimize Outline
├── analyze_results() - Parameter impact analysis
├── run_test_suite() - Execute one functionality
└── main() - Orchestrate all tests
```

## Related Documentation

- **Implementation Guide**: `PROCESSING_SETTINGS_TEST_GUIDE.md`
- **Backend Updates**: See conversation summary for endpoint changes
- **Frontend Components**: All use `ProcessingSettingsPopup`

## Maintenance

When adding new LLM-powered functionality:

1. Create a new test function following the pattern
2. Add endpoint URL and test logic
3. Hash the appropriate result field
4. Add to `test_suites` list in `main()`
5. Update this documentation
6. Run full test suite to verify

## Validation Checklist

Before considering the feature complete:

- [ ] All 10 functionalities have test functions
- [ ] Each test function follows the standard pattern
- [ ] All tests use the same parameter names
- [ ] Hash calculation is consistent
- [ ] Error handling is present
- [ ] Full test suite runs successfully
- [ ] All functionalities show parameter impact
- [ ] Documentation is updated
- [ ] Frontend components use ProcessingSettingsPopup
- [ ] Backend endpoints accept override parameters
- [ ] Core processing functions respect overrides
