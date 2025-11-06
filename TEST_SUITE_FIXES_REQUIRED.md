# Test Suite Fixes Required

## Current Test Results

- **Review (process-rag)**: ✅ **WORKING PERFECTLY** (8/8 tests passed, 100% uniqueness)
- All other 9 functionalities: ❌ Failed due to incorrect API signatures

## Required Fixes

### 1. Generate Report (`test_generate_report`)

**Current**: Uses `/reportgenie/generate-report` (doesn't exist)
**Fix**: Use `/reportgenie/generate`
**Required parameters**:

```python
data = {
    "knowledge_base_id": KB_ID,
    "sections": json.dumps([{"title": "...", "description": "..."}]),
    "outline_id": "test-outline-id",
    "search_mode": search_mode,
    "vision_analysis_override": str(vision).lower(),
    "pdf_parsing_override": pdf_parsing,
}
# No files needed - uses Form data
response = session.post(url, data=data)
```

### 2. Match Form (`test_match_form`)

**Current**: Missing required `fields` parameter
**Fix**: Add `fields` parameter
**Required parameters**:

```python
test_fields = [
    {"name": "product_name", "type": "text", "description": "..."},
    {"name": "ingredients", "type": "textarea", "description": "..."}
]

with open(TEST_FILE, "rb") as f:
    files = {"digitized_files": (filename, f, "application/pdf")}
    data = {
        "fields": json.dumps(test_fields),
        "search_mode": search_mode,
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }
```

### 3. Chatbot Knowledge Base (`test_chatbot_kb`)

**Current**: Uses `/chatbot/query-knowledge-base` (doesn't exist)
**Fix**: Use `/chatbot/knowledge-base/{KB_ID}`
**Required parameters**: Use query parameters, not JSON body

```python
url = f"{BASE_URL}/chatbot/knowledge-base/{KB_ID}"
params = {
    "question": "What are the ingredients in Swedish Fish?",
    "search_mode": search_mode,
    "vision_analysis_override": vision,  # Boolean, not string
    "pdf_parsing_override": pdf_parsing,
}
response = session.post(url, params=params)
```

### 4. Chatbot Document (`test_chatbot_doc`)

**Current**: Uses `/chatbot/query-document` (doesn't exist)
**Fix**: Use `/chatbot/document`
**Required parameters**: Use query parameters with files

```python
url = f"{BASE_URL}/chatbot/document"
with open(TEST_FILE, "rb") as f:
    files = {"files": (filename, f, "application/pdf")}
    params = {
        "question": "Summarize the key points...",
        "search_mode": search_mode,
        "vision_analysis_override": vision,
        "pdf_parsing_override": pdf_parsing,
    }
    response = session.post(url, files=files, params=params)
```

### 5. Generate Questions (`test_generate_questions`)

**Current**: Missing required `description` parameter
**Fix**: Add `description` parameter
**Required parameters**:

```python
with open(TEST_FILE, "rb") as f:
    files = {"files": (filename, f, "application/pdf")}
    data = {
        "description": "Generate questions about Swedish Fish product information",
        "checklist_type": "general",
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }
    response = session.post(url, files=files, data=data)
```

### 6. Generate Outline (`test_generate_outline`)

**Current**: Uses files parameter (not supported)
**Fix**: Use JSON body, no files
**Required parameters**:

```python
data = {
    "description": "Create an outline for a Swedish Fish product analysis report",
    "report_type": "general",
    "knowledge_base_id": KB_ID,
    "search_mode": search_mode,
    "vision_analysis_override": vision,  # Boolean, not string
    "pdf_parsing_override": pdf_parsing,
}
response = session.post(url, json=data)  # JSON, not form data
```

### 7. Generate Form Fields (`test_generate_fields`)

**Current**: Missing required `description` parameter
**Fix**: Add `description` parameter
**Required parameters**:

```python
with open(TEST_FILE, "rb") as f:
    files = {"files": (filename, f, "application/pdf")}
    data = {
        "description": "Generate form fields for Swedish Fish product information",
        "num_fields": 5,
        "search_mode": search_mode,
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }
    response = session.post(url, files=files, data=data)
```

### 8. Optimize Checklist (`test_optimize_checklist`)

**Current**: Tries to generate questions first (fails), then optimize
**Fix**: Use predefined test questions
**Required parameters**:

```python
test_questions = [
    {"question": "Does the document contain product information?", "answer_type": "yes_no"},
    {"question": "Are ingredients listed?", "answer_type": "yes_no"}
]

with open(TEST_FILE, "rb") as f:
    files = {"files": (filename, f, "application/pdf")}
    data = {
        "knowledge_base_id": KB_ID,
        "questions": json.dumps(test_questions),
        "search_mode": search_mode,
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }
    response = session.post(url, files=files, data=data)
```

### 9. Optimize Outline (`test_optimize_outline`)

**Current**: Tries to generate outline first (fails), then optimize
**Fix**: Use predefined test sections
**Required parameters**:

```python
test_sections = [
    {"title": "Product Overview", "description": "Overview of Swedish Fish"},
    {"title": "Ingredients", "description": "List of ingredients"}
]

with open(TEST_FILE, "rb") as f:
    files = {"files": (filename, f, "application/pdf")}
    data = {
        "knowledge_base_id": KB_ID,
        "outline_id": "test-outline-id",
        "sections": json.dumps(test_sections),
        "search_mode": search_mode,
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }
    response = session.post(url, files=files, data=data)
```

## Key Patterns

### Form Data vs JSON

- Most endpoints use **Form data** (multipart/form-data) when files are involved
- `generate-outline-json` uses **JSON body** (no files)
- Chatbot endpoints use **query parameters** (not body)

### Boolean vs String

- Form data: Use `str(vision).lower()` → `"true"` or `"false"`
- JSON body: Use boolean directly → `True` or `False`
- Query params: Use boolean directly → `True` or `False`

### File Parameter Names

- Review: `files`
- Generate: No files needed
- Match: `digitized_files` or `handwritten_files`
- Chatbot KB: No files
- Chatbot Doc: `files`
- Generate Questions: `files`
- Generate Outline: No files
- Generate Fields: `files`
- Optimize Checklist: `files`
- Optimize Outline: `files`

## Next Steps

1. Update the `test_all_processing_settings_fixed.py` file with these corrections
2. Remove emoji characters (✅❌⚠️) to avoid Windows encoding issues
3. Test one functionality at a time to validate fixes
4. Once all pass, replace the original `test_all_processing_settings.py`

## Quick Fix Script

Due to file encoding issues, the easiest approach is to manually edit `test_all_processing_settings_fixed.py`:

1. Find each function listed above
2. Apply the parameter fixes shown
3. Replace all ✅ with "OK", ❌ with "FAILED", ⚠️ with "WARNING"
4. Run the test
