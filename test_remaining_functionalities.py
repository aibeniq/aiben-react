#!/usr/bin/env python3
"""
Test remaining functionalities: Generate Report and Chatbot Knowledge Base
"""
import sys
import time

# Import all the test functions and utilities from the main test file
from test_all_processing_settings import (
    login,
    run_test_suite,
    test_generate_report,
    test_chatbot_kb,
    test_optimize_outline,
)


def main():
    """Run tests for remaining functionalities only"""
    print("=" * 80)
    print("TESTING REMAINING FUNCTIONALITIES")
    print("=" * 80)
    print("\nFunctionalities to test:")
    print("  2. Generate Report (ReportGenie)")
    print("  4. Chatbot Knowledge Base")
    print("  10. Optimize Outline Modal")

    try:
        # Login
        session = login()

        # Define test suites for remaining functionalities
        test_suites = [
            ("2. Generate Report", test_generate_report),
            ("4. Chatbot Knowledge Base", test_chatbot_kb),
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
        print("REMAINING FUNCTIONALITIES TEST SUMMARY")
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
        print(f"  Total tests across remaining functionalities: {total_tests}")
        print(f"  Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        if total_tests > 0:
            print(f"  Average time per test: {total_time/total_tests:.2f}s")

        print("\n" + "=" * 80)
        print("REMAINING TESTS COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
