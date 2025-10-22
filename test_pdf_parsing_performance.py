"""
Performance comparison test for PDF parsing modes: auto, enhanced, and basic.

This script tests the three parsing modes available in the system:
1. Basic: Uses only pypdf (fast, no table detection)
2. Enhanced: Uses PyMuPDF4LLM (slower, better table handling)
3. Auto: Intelligent hybrid (fast detection, then chooses optimal method)
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.pdf_utils import (
    load_pdf_with_pypdf,
    extract_pdf_with_pymupdf4llm,
    has_tables_fast,
    PYMUPDF4LLM_AVAILABLE,
)


def format_time(seconds: float) -> str:
    """Format time in a human-readable way."""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


def test_basic_mode(pdf_path: str, filename: str) -> Tuple[float, int, Dict]:
    """Test basic mode (pypdf only)."""
    print(f"\n{'='*60}")
    print("Testing BASIC mode (pypdf only)")
    print(f"{'='*60}")

    start_time = time.time()
    documents = load_pdf_with_pypdf(pdf_path, filename, use_enhanced_parsing=False)
    end_time = time.time()

    elapsed = end_time - start_time

    # Analyze results
    total_chars = sum(len(doc.page_content) for doc in documents)
    has_markdown_tables = any("|" in doc.page_content for doc in documents)

    result = {
        "mode": "basic",
        "time_seconds": elapsed,
        "num_documents": len(documents),
        "total_characters": total_chars,
        "has_markdown_tables": has_markdown_tables,
        "extraction_method": (
            documents[0].metadata.get("extraction_method") if documents else "unknown"
        ),
    }

    print(f"✓ Completed in: {format_time(elapsed)}")
    print(f"  - Documents extracted: {len(documents)}")
    print(f"  - Total characters: {total_chars:,}")
    print(f"  - Extraction method: {result['extraction_method']}")
    print(f"  - Contains markdown tables: {has_markdown_tables}")

    return elapsed, len(documents), result


def test_enhanced_mode(pdf_path: str, filename: str) -> Tuple[float, int, Dict]:
    """Test enhanced mode (PyMuPDF4LLM forced)."""
    print(f"\n{'='*60}")
    print("Testing ENHANCED mode (PyMuPDF4LLM forced)")
    print(f"{'='*60}")

    if not PYMUPDF4LLM_AVAILABLE:
        print("⚠ PyMuPDF4LLM not available - skipping enhanced mode test")
        return 0, 0, {"mode": "enhanced", "skipped": True}

    start_time = time.time()
    documents = extract_pdf_with_pymupdf4llm(pdf_path, filename, skip_table_check=True)
    end_time = time.time()

    elapsed = end_time - start_time

    # Analyze results
    total_chars = sum(len(doc.page_content) for doc in documents)
    has_markdown_tables = any("|" in doc.page_content for doc in documents)

    result = {
        "mode": "enhanced",
        "time_seconds": elapsed,
        "num_documents": len(documents),
        "total_characters": total_chars,
        "has_markdown_tables": has_markdown_tables,
        "extraction_method": (
            documents[0].metadata.get("extraction_method") if documents else "unknown"
        ),
    }

    print(f"✓ Completed in: {format_time(elapsed)}")
    print(f"  - Documents extracted: {len(documents)}")
    print(f"  - Total characters: {total_chars:,}")
    print(f"  - Extraction method: {result['extraction_method']}")
    print(f"  - Contains markdown tables: {has_markdown_tables}")

    return elapsed, len(documents), result


def test_auto_mode(pdf_path: str, filename: str) -> Tuple[float, int, Dict]:
    """Test auto mode (intelligent detection)."""
    print(f"\n{'='*60}")
    print("Testing AUTO mode (intelligent hybrid)")
    print(f"{'='*60}")

    # First, do table detection
    detection_start = time.time()
    has_tables, table_count = has_tables_fast(pdf_path)
    detection_time = time.time() - detection_start

    print(f"  Table detection: {format_time(detection_time)}")
    print(f"  - Tables found: {table_count}")
    print(f"  - Will use: {'enhanced' if has_tables else 'basic'} mode")

    # Now do the actual parsing
    parse_start = time.time()
    documents = load_pdf_with_pypdf(pdf_path, filename, use_enhanced_parsing=True)
    parse_end = time.time()

    parse_time = parse_end - parse_start
    total_time = parse_time + detection_time

    # Analyze results
    total_chars = sum(len(doc.page_content) for doc in documents)
    has_markdown_tables = any("|" in doc.page_content for doc in documents)

    result = {
        "mode": "auto",
        "time_seconds": total_time,
        "detection_time": detection_time,
        "parse_time": parse_time,
        "tables_detected": table_count,
        "chose_method": "enhanced" if has_tables else "basic",
        "num_documents": len(documents),
        "total_characters": total_chars,
        "has_markdown_tables": has_markdown_tables,
        "extraction_method": (
            documents[0].metadata.get("extraction_method") if documents else "unknown"
        ),
    }

    print(f"✓ Completed in: {format_time(total_time)}")
    print(f"  - Parsing time: {format_time(parse_time)}")
    print(f"  - Documents extracted: {len(documents)}")
    print(f"  - Total characters: {total_chars:,}")
    print(f"  - Extraction method: {result['extraction_method']}")
    print(f"  - Contains markdown tables: {has_markdown_tables}")

    return total_time, len(documents), result


def print_summary(results: List[Dict], pdf_filename: str):
    """Print a summary comparison of all modes."""
    print(f"\n{'='*60}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    print(f"PDF File: {pdf_filename}\n")

    # Filter out skipped tests
    valid_results = [r for r in results if not r.get("skipped", False)]

    if not valid_results:
        print("No valid test results to compare.")
        return

    # Find fastest
    fastest = min(valid_results, key=lambda x: x["time_seconds"])

    # Print comparison table
    print(
        f"{'Mode':<12} {'Time':<12} {'Documents':<12} {'Characters':<15} {'Method':<20}"
    )
    print(f"{'-'*12} {'-'*12} {'-'*12} {'-'*15} {'-'*20}")

    for result in valid_results:
        mode = result["mode"].upper()
        time_str = format_time(result["time_seconds"])
        is_fastest = result == fastest
        marker = "⚡" if is_fastest else "  "

        print(
            f"{marker}{mode:<10} {time_str:<12} {result['num_documents']:<12} "
            f"{result['total_characters']:<15,} {result['extraction_method']:<20}"
        )

    # Speed comparison
    print(f"\n{'='*60}")
    print("SPEED COMPARISON (relative to fastest)")
    print(f"{'='*60}")

    fastest_time = fastest["time_seconds"]
    for result in valid_results:
        mode = result["mode"].upper()
        if result == fastest:
            print(f"{mode:<12} ⚡ FASTEST (baseline)")
        else:
            ratio = result["time_seconds"] / fastest_time
            slower_by = result["time_seconds"] - fastest_time
            print(f"{mode:<12} {ratio:.2f}x slower (+{format_time(slower_by)})")

    # Additional insights for auto mode
    auto_result = next((r for r in valid_results if r["mode"] == "auto"), None)
    if auto_result and "chose_method" in auto_result:
        print(f"\n{'='*60}")
        print("AUTO MODE INSIGHTS")
        print(f"{'='*60}")
        print(f"Tables detected: {auto_result['tables_detected']}")
        print(f"Method chosen: {auto_result['chose_method'].upper()}")
        print(
            f"Detection overhead: {format_time(auto_result.get('detection_time', 0))}"
        )
        print(f"Parsing time: {format_time(auto_result.get('parse_time', 0))}")

        # Compare auto to the method it chose
        chosen_method_result = next(
            (r for r in valid_results if r["mode"] == auto_result["chose_method"]), None
        )
        if chosen_method_result:
            overhead = (
                auto_result["time_seconds"] - chosen_method_result["time_seconds"]
            )
            print(
                f"Auto mode overhead vs {auto_result['chose_method']}: {format_time(overhead)}"
            )

    # Content quality comparison
    print(f"\n{'='*60}")
    print("CONTENT QUALITY")
    print(f"{'='*60}")
    for result in valid_results:
        mode = result["mode"].upper()
        has_tables = "Yes" if result.get("has_markdown_tables", False) else "No"
        print(f"{mode:<12} Markdown tables preserved: {has_tables}")


def main():
    """Main test function."""
    # Test file path
    test_file = Path("test_files/New York City wikipedia-1.pdf")

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        print("\nAvailable PDF files in test_files/:")
        test_dir = Path("test_files")
        if test_dir.exists():
            pdf_files = list(test_dir.glob("*.pdf"))
            if pdf_files:
                for pdf in pdf_files:
                    print(f"  - {pdf.name}")
            else:
                print("  (no PDF files found)")
        return

    print("=" * 60)
    print("PDF PARSING PERFORMANCE COMPARISON TEST")
    print("=" * 60)
    print(f"Test file: {test_file.name}")
    print(f"File size: {test_file.stat().st_size / 1024:.2f} KB")
    print(f"PyMuPDF4LLM available: {PYMUPDF4LLM_AVAILABLE}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    results = []

    try:
        # Test 1: Basic mode
        time_basic, docs_basic, result_basic = test_basic_mode(
            str(test_file), test_file.name
        )
        results.append(result_basic)

        # Test 2: Enhanced mode
        time_enhanced, docs_enhanced, result_enhanced = test_enhanced_mode(
            str(test_file), test_file.name
        )
        results.append(result_enhanced)

        # Test 3: Auto mode
        time_auto, docs_auto, result_auto = test_auto_mode(
            str(test_file), test_file.name
        )
        results.append(result_auto)

        # Print summary
        print_summary(results, test_file.name)

        # Save results to file
        log_file = (
            f"pdf_parsing_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        with open(log_file, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("PDF PARSING PERFORMANCE COMPARISON TEST\n")
            f.write("=" * 60 + "\n")
            f.write(f"Test file: {test_file.name}\n")
            f.write(f"File size: {test_file.stat().st_size / 1024:.2f} KB\n")
            f.write(f"Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"PyMuPDF4LLM available: {PYMUPDF4LLM_AVAILABLE}\n\n")

            for result in results:
                f.write(f"\n{result['mode'].upper()} MODE:\n")
                f.write("-" * 40 + "\n")
                for key, value in result.items():
                    if key == "time_seconds":
                        f.write(f"  {key}: {format_time(value)}\n")
                    else:
                        f.write(f"  {key}: {value}\n")

        print(f"\n✓ Results saved to: {log_file}")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
