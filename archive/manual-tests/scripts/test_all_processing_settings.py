#!/usr/bin/env python3
"""
Comprehensive test for ALL processing settings combinations.
Tests: search_mode, vision_analysis_enabled, pdf_parsing_preference

This will verify that each parameter produces different results.
"""
import requests
import time
import hashlib
import json
import uuid
from pathlib import Path
from itertools import product

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "david@aiben.io"
PASSWORD = "password123456"
# Use Swedish Fish PDF - matches the existing KB
TEST_FILE = "test_files/swedish fish.pdf"
KB_ID = "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e"

TEST_QUESTIONS = """What are the ingredients?
What is the nutritional information?
Are there any allergens mentioned?"""

# All parameter combinations
SEARCH_MODES = ["vector", "full_scan"]
VISION_ANALYSIS = [True, False]
PDF_PARSING = ["enhanced", "basic"]


def login():
    """Login and return authenticated session"""
    print("\n" + "=" * 80)
    print("LOGGING IN")
    print("=" * 80)

    session = requests.Session()
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = session.post(f"{BASE_URL}/login/access-token", data=login_data)

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

    print("Login successful!")
    return session


def test_combination(session, search_mode, vision_enabled, pdf_parsing):
    """Test a specific combination of settings"""
    combo_name = f"{search_mode}+vision_{vision_enabled}+pdf_{pdf_parsing}"

    print(f"\n" + "=" * 80)
    print(f"TESTING: {combo_name}")
    print("=" * 80)

    # Create task
    response = session.post(f"{BASE_URL}/veradoc/review/task")
    if response.status_code != 200:
        raise Exception(f"Failed to create task: {response.text}")
    task_id = response.json()["task_id"]
    print(f"Task ID: {task_id}")

    # Prepare the request
    if not Path(TEST_FILE).exists():
        raise Exception(f"Test file not found: {TEST_FILE}")

    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "questions": TEST_QUESTIONS,
            "knowledge_base_id": KB_ID,
            "search_mode": search_mode,
            "vision_analysis_enabled": str(vision_enabled).lower(),
            "pdf_parsing_preference": pdf_parsing,
            "task_id": task_id,
        }

        print(f"Parameters:")
        print(f"  - Search Mode: {search_mode}")
        print(f"  - Vision Analysis: {vision_enabled}")
        print(f"  - PDF Parsing: {pdf_parsing}")

        start_time = time.time()

        response = session.post(
            f"{BASE_URL}/veradoc/process-rag", files=files, data=data
        )

        execution_time = time.time() - start_time

        if response.status_code != 200:
            print(f"[FAIL] Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, execution_time

        result = response.json()

        # Extract evaluation
        results = result.get("results", {})
        evaluation = results.get("final_evaluation", "")

        # Create hash of evaluation for comparison
        eval_hash = hashlib.md5(evaluation.encode()).hexdigest()[:8]

        print(f"[OK] Completed in {execution_time:.2f}s")
        print(f"Evaluation length: {len(evaluation)} chars")
        print(f"Hash: {eval_hash}")
        print(f"Preview: {evaluation[:150]}...")

        return {
            "combo": combo_name,
            "search_mode": search_mode,
            "vision": vision_enabled,
            "pdf_parsing": pdf_parsing,
            "evaluation": evaluation,
            "hash": eval_hash,
            "time": execution_time,
            "length": len(evaluation),
        }, execution_time


def test_generate_report(session, search_mode, vision, pdf_parsing):
    """Test Generate: generate-report endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/reportgenie/generate"

    # Generate report requires knowledge_base_id, sections, and outline_id
    sections_data = [
        {"text": "Product Overview", "consultDocuments": True},
        {"text": "Ingredients Analysis", "consultDocuments": True},
        {"text": "Nutritional Information", "consultDocuments": True},
    ]

    data = {
        "knowledge_base_id": KB_ID,
        "sections": json.dumps(sections_data),
        "outline_id": str(uuid.uuid4()),  # Use a real UUID
        "search_mode": search_mode,
        "vision_analysis_override": str(vision).lower(),
        "pdf_parsing_override": pdf_parsing,
    }

    start_time = time.time()
    response = session.post(url, data=data)
    exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    # Report is nested in results.full_report
    report_content = result_data.get("results", {}).get("full_report", "")
    result_hash = hashlib.md5(report_content.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, length: {len(report_content)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(report_content),
    }, exec_time


def test_match_form(session, search_mode, vision, pdf_parsing):
    """Test Match: process form endpoint with TWO files for comparison"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/formconnect/process"

    # Use TWO files for better comparison testing
    file1 = "test_files/swedish fish.pdf"
    file2 = "test_files/karelian pasties.pdf"

    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        files = [
            ("digitized_files", (Path(file1).name, f1, "application/pdf")),
            ("digitized_files", (Path(file2).name, f2, "application/pdf")),
        ]

        data = {
            "fields": "Product Name\nIngredients\nNutritional Information",
            "search_mode": search_mode,
            "vision_analysis_override": str(vision).lower(),
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, data=data)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    # Match Form returns: results.extracted_data
    extracted_data = result_data.get("results", {}).get("extracted_data", {})
    hash_input = json.dumps(extracted_data, sort_keys=True)
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, fields: {len(extracted_data)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(hash_input),
    }, exec_time


def test_chatbot_kb(session, search_mode, vision, pdf_parsing):
    """Test Chatbot: query-knowledge-base endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/chat/knowledge-base/{KB_ID}"

    # Map full_scan to full_text for chatbot endpoints
    chatbot_search_mode = "full_text" if search_mode == "full_scan" else search_mode

    params = {
        "question": "What are the ingredients in Swedish Fish?",
        "search_mode": chatbot_search_mode,
        "vision_analysis_override": vision,
        "pdf_parsing_override": pdf_parsing,
    }

    start_time = time.time()
    response = session.post(url, params=params)
    exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    answer = result_data.get("answer", "")
    result_hash = hashlib.md5(answer.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, length: {len(answer)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(answer),
    }, exec_time


def test_chatbot_doc(session, search_mode, vision, pdf_parsing):
    """Test Chatbot: query-document endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/chat/document"

    # Map full_scan to full_text for chatbot endpoints
    chatbot_search_mode = "full_text" if search_mode == "full_scan" else search_mode

    with open(TEST_FILE, "rb") as f:
        files = {"file": (Path(TEST_FILE).name, f, "application/pdf")}

        params = {
            "question": "What are the main ingredients?",
            "search_mode": chatbot_search_mode,
            "vision_analysis_override": vision,
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, params=params)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    answer = result_data.get("answer", "")
    result_hash = hashlib.md5(answer.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, length: {len(answer)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(answer),
    }, exec_time


def test_generate_questions(session, search_mode, vision, pdf_parsing):
    """Test VeraDoc Modal: generate-questions-with-files endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/veradoc/generate-questions-with-files"

    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "description": "Generate questions about this product",
            "vision_analysis_override": str(vision).lower(),
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, data=data)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    questions = result_data.get("questions", [])
    hash_input = json.dumps(questions, sort_keys=True)
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, questions: {len(questions)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(questions),
    }, exec_time


def test_generate_outline(session, search_mode, vision, pdf_parsing):
    """Test ReportGenie Modal: generate-outline-json endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/reportgenie/generate-outline-json"

    payload = {
        "report_name": "Swedish Fish Analysis",
        "description": "Generate an outline for product analysis",
        "search_mode": search_mode,
        "vision_analysis_override": vision,
        "pdf_parsing_override": pdf_parsing,
    }

    start_time = time.time()
    response = session.post(url, json=payload)
    exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    sections = result_data.get("sections", [])
    hash_input = json.dumps(sections, sort_keys=True)
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, sections: {len(sections)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(sections),
    }, exec_time


def test_generate_fields(session, search_mode, vision, pdf_parsing):
    """Test FormConnect Modal: generate-fields-with-files endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/formconnect/generate-fields-with-files"

    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "description": "Generate form fields for this product",
            "vision_analysis_override": str(vision).lower(),
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, data=data)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    fields = result_data.get("fields", [])
    hash_input = json.dumps(fields, sort_keys=True)
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, fields: {len(fields)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(fields),
    }, exec_time


def test_optimize_checklist(session, search_mode, vision, pdf_parsing):
    """Test VeraDoc Modal: optimize-checklist endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/veradoc/optimize-checklist"

    # First generate some questions to optimize
    gen_url = f"{BASE_URL}/veradoc/generate-questions-with-files"
    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}
        data = {"description": "Product analysis questions"}
        gen_response = session.post(gen_url, files=files, data=data)

    if gen_response.status_code != 200:
        print(
            f"  [FAIL] FAILED to generate initial questions: {gen_response.status_code}"
        )
        return None, 0

    initial_questions = gen_response.json().get("questions", [])[:3]  # Use first 3

    # Now optimize
    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "knowledge_base_id": KB_ID,
            "questions": json.dumps(initial_questions),
            "vision_analysis_override": str(vision).lower(),
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, data=data)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    optimized_questions = result_data.get("optimized_questions", [])
    hash_input = json.dumps(optimized_questions, sort_keys=True)
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, questions: {len(optimized_questions)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(optimized_questions),
    }, exec_time


def test_optimize_outline(session, search_mode, vision, pdf_parsing):
    """Test ReportGenie Modal: optimize-outline endpoint"""
    combo_name = f"{search_mode}+vision_{vision}+pdf_{pdf_parsing}"
    print(f"Parameters: {combo_name}")

    url = f"{BASE_URL}/reportgenie/optimize-outline"

    # First generate an outline to optimize
    gen_url = f"{BASE_URL}/reportgenie/generate-outline-json"
    payload = {
        "report_name": "Swedish Fish Analysis",
        "description": "Product analysis outline",
    }
    gen_response = session.post(gen_url, json=payload)

    if gen_response.status_code != 200:
        print(
            f"  [FAIL] FAILED to generate initial outline: {gen_response.status_code}"
        )
        return None, 0

    initial_sections = gen_response.json().get("sections", [])

    if not initial_sections:
        print(f"  [FAIL] Generated outline has no sections")
        return None, 0

    # Convert string sections to objects with required structure for optimize-outline
    sections_objects = [
        {"text": section, "consultDocuments": True} for section in initial_sections
    ]

    # Now optimize
    with open(TEST_FILE, "rb") as f:
        files = {"files": (Path(TEST_FILE).name, f, "application/pdf")}

        data = {
            "knowledge_base_id": KB_ID,
            "outline_id": "test-outline-id",
            "sections": json.dumps(sections_objects),
            "vision_analysis_override": str(vision).lower(),
            "pdf_parsing_override": pdf_parsing,
        }

        start_time = time.time()
        response = session.post(url, files=files, data=data)
        exec_time = time.time() - start_time

    if response.status_code != 200:
        print(f"  [FAIL] FAILED: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return None, exec_time

    result_data = response.json()
    # Use suggestions for hashing as they contain the actual analysis
    suggestions = result_data.get("suggestions", [])
    optimized_sections = result_data.get("optimized_sections", [])

    # Hash both suggestions and optimized sections to capture variations
    hash_input = json.dumps(
        {"suggestions": suggestions, "optimized_sections": optimized_sections},
        sort_keys=True,
    )
    result_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]

    print(
        f"  [OK] SUCCESS (hash: {result_hash}, time: {exec_time:.2f}s, sections: {len(optimized_sections)})"
    )

    return {
        "search_mode": search_mode,
        "vision": vision,
        "pdf_parsing": pdf_parsing,
        "combo": combo_name,
        "hash": result_hash,
        "time": exec_time,
        "length": len(optimized_sections),
    }, exec_time


def analyze_results(all_results):
    """Analyze results to see which parameters make a difference"""
    print("\n" + "=" * 80)
    print("ANALYSIS: PARAMETER IMPACT")
    print("=" * 80)

    # Group by search_mode
    print("\n1. SEARCH MODE IMPACT (vector vs full_scan)")
    print("-" * 80)
    search_groups = {}
    for r in all_results:
        key = (r["vision"], r["pdf_parsing"])
        if key not in search_groups:
            search_groups[key] = {}
        search_groups[key][r["search_mode"]] = r["hash"]

    search_diff_count = 0
    for key, modes in search_groups.items():
        if len(modes) == 2:
            if modes["vector"] != modes["full_scan"]:
                search_diff_count += 1
                print(
                    f"  Vision={key[0]}, PDF={key[1]}: DIFFERENT (vector={modes['vector']}, full_scan={modes['full_scan']})"
                )
            else:
                print(f"  Vision={key[0]}, PDF={key[1]}: IDENTICAL")

    print(
        f"\nResult: {search_diff_count}/{len(search_groups)} combinations show difference"
    )
    if search_diff_count > 0:
        print("[OK] Search mode parameter IS working!")
    else:
        print("[FAIL] Search mode parameter NOT working!")

    # Group by vision_analysis
    print("\n2. VISION ANALYSIS IMPACT (True vs False)")
    print("-" * 80)
    vision_groups = {}
    for r in all_results:
        key = (r["search_mode"], r["pdf_parsing"])
        if key not in vision_groups:
            vision_groups[key] = {}
        vision_groups[key][r["vision"]] = r["hash"]

    vision_diff_count = 0
    for key, visions in vision_groups.items():
        if len(visions) == 2:
            if visions[True] != visions[False]:
                vision_diff_count += 1
                print(
                    f"  Search={key[0]}, PDF={key[1]}: DIFFERENT (on={visions[True]}, off={visions[False]})"
                )
            else:
                print(f"  Search={key[0]}, PDF={key[1]}: IDENTICAL")

    print(
        f"\nResult: {vision_diff_count}/{len(vision_groups)} combinations show difference"
    )
    if vision_diff_count > 0:
        print("[OK] Vision analysis parameter IS working!")
    else:
        print(
            "[WARN]  Vision analysis parameter NOT making a difference (may be expected for this PDF)"
        )

    # Group by pdf_parsing
    print("\n3. PDF PARSING IMPACT (enhanced vs basic)")
    print("-" * 80)
    pdf_groups = {}
    for r in all_results:
        key = (r["search_mode"], r["vision"])
        if key not in pdf_groups:
            pdf_groups[key] = {}
        pdf_groups[key][r["pdf_parsing"]] = r["hash"]

    pdf_diff_count = 0
    for key, parsings in pdf_groups.items():
        if len(parsings) == 2:
            if parsings["enhanced"] != parsings["basic"]:
                pdf_diff_count += 1
                print(
                    f"  Search={key[0]}, Vision={key[1]}: DIFFERENT (enhanced={parsings['enhanced']}, basic={parsings['basic']})"
                )
            else:
                print(f"  Search={key[0]}, Vision={key[1]}: IDENTICAL")

    print(f"\nResult: {pdf_diff_count}/{len(pdf_groups)} combinations show difference")
    if pdf_diff_count > 0:
        print("[OK] PDF parsing parameter IS working!")
    else:
        print(
            "[WARN]  PDF parsing parameter NOT making a difference (may be expected for this simple PDF)"
        )

    # Overall unique results
    print("\n4. OVERALL UNIQUENESS")
    print("-" * 80)
    unique_hashes = set(r["hash"] for r in all_results)
    print(f"Total tests run: {len(all_results)}")
    print(f"Unique results: {len(unique_hashes)}")
    print(
        f"Uniqueness ratio: {len(unique_hashes)}/{len(all_results)} = {len(unique_hashes)/len(all_results)*100:.1f}%"
    )

    if len(unique_hashes) == 1:
        print("[FAIL] ALL RESULTS IDENTICAL - Parameters not working!")
    elif len(unique_hashes) == len(all_results):
        print("[OK] ALL RESULTS UNIQUE - All parameters working!")
    else:
        print("[WARN]  SOME VARIATION - Some parameters working, some not")


def run_test_suite(session, test_name, test_func):
    """Run a complete test suite for one functionality"""
    print("\n" + "=" * 80)
    print(f"TESTING: {test_name}")
    print("=" * 80)

    all_results = []
    test_count = 0
    total_tests = len(SEARCH_MODES) * len(VISION_ANALYSIS) * len(PDF_PARSING)

    for search_mode, vision, pdf_parsing in product(
        SEARCH_MODES, VISION_ANALYSIS, PDF_PARSING
    ):
        test_count += 1
        print(f"\n[Test {test_count}/{total_tests}] {test_name}")

        result, exec_time = test_func(session, search_mode, vision, pdf_parsing)

        if result:
            all_results.append(result)

        # Small delay between tests
        if test_count < total_tests:
            time.sleep(1)

    # Analyze results
    if all_results:
        analyze_results(all_results)

        # Summary
        print("\n" + "-" * 80)
        print(f"{test_name} SUMMARY")
        print("-" * 80)
        print(f"Total tests: {len(all_results)}")
        print(f"Total time: {sum(r['time'] for r in all_results):.2f}s")
        print(
            f"Average time: {sum(r['time'] for r in all_results)/len(all_results):.2f}s"
        )

        # Show hash distribution
        print("\nHash distribution:")
        hash_counts = {}
        for r in all_results:
            hash_counts[r["hash"]] = hash_counts.get(r["hash"], 0) + 1

        for hash_val, count in sorted(hash_counts.items(), key=lambda x: -x[1]):
            combos = [r["combo"] for r in all_results if r["hash"] == hash_val]
            print(f"  {hash_val}: {count} occurrences")
            for combo in combos[:3]:  # Show first 3
                print(f"    - {combo}")
            if len(combos) > 3:
                print(f"    ... and {len(combos)-3} more")

    return all_results


def main():
    """Run comprehensive tests for ALL functionalities"""
    print("=" * 80)
    print("COMPREHENSIVE PROCESSING SETTINGS TEST - ALL FUNCTIONALITIES")
    print("=" * 80)
    print(f"Test file: {TEST_FILE}")
    print(f"Using KB: {KB_ID}")
    print(f"\nParameter space:")
    print(f"  - Search Modes: {SEARCH_MODES}")
    print(f"  - Vision Analysis: {VISION_ANALYSIS}")
    print(f"  - PDF Parsing: {PDF_PARSING}")
    print(
        f"  - Total combinations per test: {len(SEARCH_MODES) * len(VISION_ANALYSIS) * len(PDF_PARSING)}"
    )
    print(f"\nFunctionalities to test:")
    print(f"  1. Review (VeraDoc process-rag)")
    print(f"  2. Generate Report (ReportGenie)")
    print(f"  3. Match Form (FormConnect)")
    print(f"  4. Chatbot Knowledge Base")
    print(f"  5. Chatbot Document")
    print(f"  6. Generate Questions Modal")
    print(f"  7. Generate Outline Modal")
    print(f"  8. Generate Form Fields Modal")
    print(f"  9. Optimize Checklist Modal")
    print(f"  10. Optimize Outline Modal")

    try:
        # Login
        session = login()

        # Define all test suites
        test_suites = [
            ("1. Review (process-rag)", test_combination),
            ("2. Generate Report", test_generate_report),
            ("3. Match Form", test_match_form),
            ("4. Chatbot Knowledge Base", test_chatbot_kb),
            ("5. Chatbot Document", test_chatbot_doc),
            ("6. Generate Questions Modal", test_generate_questions),
            ("7. Generate Outline Modal", test_generate_outline),
            ("8. Generate Form Fields Modal", test_generate_fields),
            ("9. Optimize Checklist Modal", test_optimize_checklist),
            ("10. Optimize Outline Modal", test_optimize_outline),
        ]

        # Run each test suite
        all_suite_results = {}
        for test_name, test_func in test_suites:
            results = run_test_suite(session, test_name, test_func)
            all_suite_results[test_name] = results
            print(f"\n[OK] Completed {test_name}")
            time.sleep(2)  # Delay between test suites

        # Overall summary
        print("\n\n" + "=" * 80)
        print("OVERALL TEST SUMMARY - ALL FUNCTIONALITIES")
        print("=" * 80)

        total_tests = 0
        total_time = 0
        for test_name, results in all_suite_results.items():
            test_count = len(results)
            suite_time = sum(r["time"] for r in results) if results else 0
            total_tests += test_count
            total_time += suite_time

            unique_hashes = len(set(r["hash"] for r in results)) if results else 0
            uniqueness = (
                f"{unique_hashes}/{test_count} unique"
                if test_count > 0
                else "no results"
            )

            print(f"\n{test_name}:")
            print(f"  Tests: {test_count}")
            print(f"  Time: {suite_time:.2f}s")
            print(f"  Uniqueness: {uniqueness}")

        print(f"\n{'='*80}")
        print(f"GRAND TOTAL:")
        print(f"  Total tests across all functionalities: {total_tests}")
        print(f"  Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        print(f"  Average time per test: {total_time/total_tests:.2f}s")

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
