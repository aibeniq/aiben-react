#!/usr/bin/env python3
"""
Comprehensive test for ALL processing settings combinations.
Tests: search_mode, vision_analysis_enabled, pdf_parsing_preference

This will verify that each parameter produces different results.
"""
import requests
import time
import hashlib
from pathlib import Path
from itertools import product

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "david@aiben.io"
PASSWORD = "password123456"
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
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, execution_time

        result = response.json()

        # Extract evaluation
        results = result.get("results", {})
        evaluation = results.get("final_evaluation", "")

        # Create hash of evaluation for comparison
        eval_hash = hashlib.md5(evaluation.encode()).hexdigest()[:8]

        print(f"✅ Completed in {execution_time:.2f}s")
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
        print("✅ Search mode parameter IS working!")
    else:
        print("❌ Search mode parameter NOT working!")

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
        print("✅ Vision analysis parameter IS working!")
    else:
        print(
            "⚠️  Vision analysis parameter NOT making a difference (may be expected for this PDF)"
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
        print("✅ PDF parsing parameter IS working!")
    else:
        print(
            "⚠️  PDF parsing parameter NOT making a difference (may be expected for this simple PDF)"
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
        print("❌ ALL RESULTS IDENTICAL - Parameters not working!")
    elif len(unique_hashes) == len(all_results):
        print("✅ ALL RESULTS UNIQUE - All parameters working!")
    else:
        print("⚠️  SOME VARIATION - Some parameters working, some not")


def main():
    """Run comprehensive tests"""
    print("=" * 80)
    print("COMPREHENSIVE PROCESSING SETTINGS TEST")
    print("Testing ALL combinations of settings")
    print("=" * 80)
    print(f"Test file: {TEST_FILE}")
    print(f"Using KB: {KB_ID}")
    print(f"\nParameter space:")
    print(f"  - Search Modes: {SEARCH_MODES}")
    print(f"  - Vision Analysis: {VISION_ANALYSIS}")
    print(f"  - PDF Parsing: {PDF_PARSING}")
    print(
        f"  - Total combinations: {len(SEARCH_MODES) * len(VISION_ANALYSIS) * len(PDF_PARSING)}"
    )

    try:
        # Login
        session = login()

        # Test all combinations
        all_results = []
        test_count = 0
        total_tests = len(SEARCH_MODES) * len(VISION_ANALYSIS) * len(PDF_PARSING)

        for search_mode, vision, pdf_parsing in product(
            SEARCH_MODES, VISION_ANALYSIS, PDF_PARSING
        ):
            test_count += 1
            print(f"\n[Test {test_count}/{total_tests}]")

            result, exec_time = test_combination(
                session, search_mode, vision, pdf_parsing
            )

            if result:
                all_results.append(result)

            # Small delay between tests
            if test_count < total_tests:
                time.sleep(1)

        # Analyze results
        if all_results:
            analyze_results(all_results)

            # Summary
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)
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

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
