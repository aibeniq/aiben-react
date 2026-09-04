#!/usr/bin/env python3
"""Apply fixes to test_all_processing_settings.py"""

import re

# Read the current file (already has some fixes)
with open("test_all_processing_settings.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix chatbot_doc to use "files" instead of "file" and correct param usage
# Replace the data dict with params for query parameters
content = re.sub(
    r"(def test_chatbot_doc\(session, search_mode, vision, pdf_parsing\):.*?"
    r'with open\(TEST_FILE, "rb"\) as f:\s+'
    r'files = \{"file": \(Path\(TEST_FILE\)\.name, f, "application/pdf"\)\}\s+'
    r"data = \{)"
    r"([^}]*)"
    r"(\}\s+"
    r"start_time = time\.time\(\)\s+"
    r"response = session\.post\(url, files=files, data=data\))",
    r"\1"
    r'\n            "query": "Summarize the key points about Swedish Fish",'
    r'\n            "search_mode": search_mode,'
    r'\n            "vision_analysis_override": vision,'
    r'\n            "pdf_parsing_override": pdf_parsing,'
    r"\n        }"
    r'\n\n        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}'
    r"\n\n        start_time = time.time()"
    r"\n        response = session.post(url, files=files, params=data)",
    content,
    flags=re.DOTALL,
)

# Fix chatbot KB to remove kb_id from params (it's already in URL)
content = re.sub(
    r'(url = f"\{BASE_URL\}/chatbot/knowledge-base/\{KB_ID\}"\s+'
    r"data = \{)\s+"
    r'"kb_id": KB_ID,\s+',
    r"\1\n        ",
    content,
    flags=re.DOTALL,
)

# Fix chatbot KB to use "query" instead of "message"
content = re.sub(
    r'(def test_chatbot_kb.*?data = \{[^}]*)"message": "What are the ingredients in Swedish Fish\?"',
    r'\1"query": "What are the ingredients in Swedish Fish?"',
    content,
    flags=re.DOTALL,
)

# Add description parameter to generate_questions
content = re.sub(
    r'(def test_generate_questions.*?url = f"\{BASE_URL\}/veradoc/generate-questions-with-files"\s+'
    r'with open\(TEST_FILE, "rb"\) as f:\s+'
    r'files = \{"file": \(Path\(TEST_FILE\)\.name, f, "application/pdf"\)\}\s+'
    r"data = \{)",
    r"\1" r'\n            "description": "Generate questions about this product",',
    content,
    flags=re.DOTALL,
)

# Add description parameter to generate_outline (and fix to JSON body, no files)
content = re.sub(
    r'(def test_generate_outline.*?url = f"\{BASE_URL\}/reportgenie/generate-outline-json")',
    r"\1\n\n    # This endpoint uses JSON body, not files\n    payload = {"
    r'\n        "report_name": "Product Analysis",'
    r'\n        "description": "Analyze product information",'
    r'\n        "search_mode": search_mode,'
    r'\n        "vision_analysis_override": vision,'
    r'\n        "pdf_parsing_override": pdf_parsing,'
    r"\n    }"
    r"\n\n    start_time = time.time()"
    r"\n    response = session.post(url, json=payload)"
    r"\n    exec_time = time.time() - start_time"
    r"\n\n    # Remove old file-based code by returning early",
    content,
    flags=re.DOTALL,
)

# Add description parameter to generate_fields
content = re.sub(
    r'(def test_generate_fields.*?url = f"\{BASE_URL\}/formconnect/generate-fields-with-files"\s+'
    r'with open\(TEST_FILE, "rb"\) as f:\s+'
    r'files = \{"file": \(Path\(TEST_FILE\)\.name, f, "application/pdf"\)\}\s+'
    r"data = \{)",
    r"\1" r'\n            "description": "Generate form fields for this product",',
    content,
    flags=re.DOTALL,
)

# Write the fixed content
with open("test_all_processing_settings.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Additional fixes applied successfully!")
print("- Fixed chatbot_doc to use 'files' and 'params'")
print("- Fixed chatbot_kb to use 'query' instead of 'message'")
print("- Removed duplicate kb_id from chatbot_kb params")
print("- Added 'description' to generate_questions")
print("- Fixed generate_outline to use JSON body")
print("- Added 'description' to generate_fields")
