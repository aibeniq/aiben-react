# Quick Test Guide - Processing Settings

## Run Full Test Suite

```bash
python test_all_processing_settings.py
```

**Duration**: ~20-30 minutes  
**Total Tests**: 80 (10 functionalities × 8 combinations)

## Run Individual Functionality Tests

To test just one functionality, modify `main()` to comment out unwanted tests:

```python
# In main() function, comment out test suites you don't need:
test_suites = [
    ("1. Review (process-rag)", test_combination),
    # ("2. Generate Report", test_generate_report),
    # ("3. Match Form", test_match_form),
    # ... etc
]
```

## Test Individual Endpoints Manually

### 1. Review (VeraDoc)

```bash
curl -X POST http://localhost:8000/api/v1/veradoc/process-rag \
  -H "Cookie: session=..." \
  -F "file=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 2. Generate Report

```bash
curl -X POST http://localhost:8000/api/v1/reportgenie/generate-report \
  -H "Cookie: session=..." \
  -F "file=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "topic=Swedish Fish Analysis" \
  -F "search_mode=full_scan" \
  -F "vision_analysis_override=false" \
  -F "pdf_parsing_override=basic"
```

### 3. Match Form

```bash
curl -X POST http://localhost:8000/api/v1/formconnect/process \
  -H "Cookie: session=..." \
  -F "file=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 4. Chatbot Knowledge Base

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/query-knowledge-base \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json" \
  -d '{
    "kb_id": "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e",
    "message": "What are the ingredients?",
    "search_mode": "vector",
    "vision_analysis_override": true,
    "pdf_parsing_override": "enhanced"
  }'
```

### 5. Chatbot Document

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/query-document \
  -H "Cookie: session=..." \
  -F "file=@test_files/swedish fish.pdf" \
  -F "message=Summarize this document" \
  -F "search_mode=full_scan" \
  -F "vision_analysis_override=false" \
  -F "pdf_parsing_override=basic"
```

### 6. Generate Questions Modal

```bash
curl -X POST http://localhost:8000/api/v1/veradoc/generate-questions-with-files \
  -H "Cookie: session=..." \
  -F "files=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 7. Generate Outline Modal

```bash
curl -X POST http://localhost:8000/api/v1/reportgenie/generate-outline-json \
  -H "Cookie: session=..." \
  -F "files=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "topic=Swedish Fish" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 8. Generate Form Fields Modal

```bash
curl -X POST http://localhost:8000/api/v1/formconnect/generate-fields-with-files \
  -H "Cookie: session=..." \
  -F "files=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 9. Optimize Checklist Modal

```bash
curl -X POST http://localhost:8000/api/v1/veradoc/optimize-checklist \
  -H "Cookie: session=..." \
  -F "files=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "existing_questions=[...]" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

### 10. Optimize Outline Modal

```bash
curl -X POST http://localhost:8000/api/v1/reportgenie/optimize-outline \
  -H "Cookie: session=..." \
  -F "files=@test_files/swedish fish.pdf" \
  -F "kb_id=7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e" \
  -F "topic=Swedish Fish" \
  -F "current_outline=[...]" \
  -F "search_mode=vector" \
  -F "vision_analysis_override=true" \
  -F "pdf_parsing_override=enhanced"
```

## Parameter Combinations to Test

All 8 combinations (2×2×2):

| #   | Search Mode | Vision | PDF Parsing |
| --- | ----------- | ------ | ----------- |
| 1   | vector      | true   | enhanced    |
| 2   | vector      | true   | basic       |
| 3   | vector      | false  | enhanced    |
| 4   | vector      | false  | basic       |
| 5   | full_scan   | true   | enhanced    |
| 6   | full_scan   | true   | basic       |
| 7   | full_scan   | false  | enhanced    |
| 8   | full_scan   | false  | basic       |

## Expected Results

### ✅ Success Indicators

- Different results for different search modes
- Different results when vision analysis changes
- Different results for different PDF parsing modes
- 8/8 unique hashes (100% uniqueness)

### ⚠️ Warning Signs

- Same hash for all combinations (parameters not working)
- Same hash for specific parameter changes (that parameter not working)
- Low uniqueness ratio (<50%)

### ❌ Failure Indicators

- HTTP errors (500, 401, 404)
- Missing fields in response
- Crashes or timeouts

## Debugging Tips

### Check Backend Logs

```bash
docker-compose logs -f backend
```

### Check Parameter Passing

Add print statements in backend:

```python
print(f"Override received: vision={vision_analysis_override}, pdf={pdf_parsing_override}")
```

### Verify Processing

Check `document_utils.py`:

```python
print(f"Using vision: {user.vision_analysis_enabled}, pdf: {user.pdf_parsing_preference}")
```

### Compare Results

Save results to files:

```python
with open(f"result_{combo}.json", "w") as f:
    json.dump(result, f, indent=2)
```

Then diff them:

```bash
diff result_vector_true_enhanced.json result_vector_false_enhanced.json
```

## Quick Validation

Test one endpoint with two different settings to verify it works:

```python
import requests

session = requests.Session()
# Login first...

# Test 1: Vector + Vision
response1 = session.post("http://localhost:8000/api/v1/chatbot/query-knowledge-base", json={
    "kb_id": "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e",
    "message": "What are the ingredients?",
    "search_mode": "vector",
    "vision_analysis_override": True,
    "pdf_parsing_override": "enhanced"
})
answer1 = response1.json()["answer"]

# Test 2: Full scan + No vision
response2 = session.post("http://localhost:8000/api/v1/chatbot/query-knowledge-base", json={
    "kb_id": "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e",
    "message": "What are the ingredients?",
    "search_mode": "full_scan",
    "vision_analysis_override": False,
    "pdf_parsing_override": "basic"
})
answer2 = response2.json()["answer"]

# Compare
print(f"Same result: {answer1 == answer2}")
print(f"Answer 1: {answer1[:100]}...")
print(f"Answer 2: {answer2[:100]}...")
```

If answers are identical, parameters aren't working!
