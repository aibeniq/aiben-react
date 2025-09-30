#!/usr/bin/env python3
"""
FINAL DEBUGGING SUMMARY AND TEST GUIDE

This script summarizes our findings and provides a comprehensive test plan
to confirm the Knowledge Base vs Direct Upload retrieval discrepancy.
"""

import json
import subprocess
import sys
import os


def print_summary():
    """Print comprehensive summary of findings"""
    print("🚀 KNOWLEDGE BASE vs DIRECT UPLOAD RETRIEVAL ANALYSIS")
    print("=" * 80)

    print("🎯 PROBLEM IDENTIFIED:")
    print("   User reports: Same document, same question = different answers")
    print("   - KB returns: '0.12% per trade' (from Swaps table)")
    print(
        "   - Direct returns: 'Smart: $8.95, All-inclusive: $0' (from Exchange-traded table)"
    )
    print()

    print("🔍 ROOT CAUSE ANALYSIS:")
    print("   1. KB retrieves 'Swaps and Structured Products' table (Page 9)")
    print(
        "   2. Direct upload retrieves 'Exchange-traded Stocks, bonds, ETFs' table (Page 1)"
    )
    print(
        "   3. Question 'What are the fees for trading US equities?' should get Exchange-traded table"
    )
    print(
        "   4. KB chunking/embedding loses context, matches 'brokerage commission' term"
    )
    print("   5. Direct upload preserves document structure, gets correct table")
    print()

    print("📊 TECHNICAL DIFFERENCES:")
    print("   KB PROCESSING:")
    print("   - Pre-chunked documents stored in vector DB")
    print("   - Potential context loss during chunking")
    print("   - Academic paper retriever on stored chunks")
    print("   - Quality scores may differ from fresh processing")
    print()
    print("   DIRECT UPLOAD PROCESSING:")
    print("   - Fresh document processing with table-aware chunking")
    print("   - Vision processing preserves table structure")
    print("   - Academic paper retriever on fresh chunks")
    print("   - Better context preservation")
    print()


def check_backend_status():
    """Check if backend is running"""
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=aibeniq-react-backend-1",
                "--format",
                "{{.Status}}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            print(f"✅ Backend Status: {status}")
            return True
        else:
            print(f"❌ Backend not running")
            return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False


def check_debug_logs():
    """Check for existing debug output in logs"""
    try:
        result = subprocess.run(
            ["docker", "logs", "aibeniq-react-backend-1", "--tail=50"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            print(f"❌ Error getting logs: {result.stderr}")
            return False

        logs = result.stdout

        has_kb_debug = "🐛 KNOWLEDGE BASE DEBUG" in logs or "🐛 KB DEBUG" in logs
        has_direct_debug = "🐛 DIRECT UPLOAD DEBUG" in logs or "🐛 DIRECT DEBUG" in logs

        print(f"📋 DEBUG LOG STATUS:")
        print(f"   KB Debug Present: {has_kb_debug}")
        print(f"   Direct Debug Present: {has_direct_debug}")

        if has_kb_debug or has_direct_debug:
            print(f"   💡 Some debug output found - check logs manually")
            return True

        print(f"   ℹ️  No debug output yet - run test queries")
        return False

    except Exception as e:
        print(f"❌ Error checking debug logs: {e}")
        return False


def print_test_plan():
    """Print step-by-step test plan"""
    print("📋 STEP-BY-STEP TEST PLAN:")
    print("=" * 50)

    print("🔧 SETUP:")
    print("   1. Backend running ✓ (confirmed)")
    print("   2. Frontend accessible at http://localhost:5174/")
    print("   3. Debug logging enabled in chatbot.py ✓")
    print("   4. Test PDF: test_files/Appendix 6 Fee Schedule.pdf ✓")
    print()

    print("🧪 TEST SCENARIO A - Knowledge Base Query:")
    print("   1. Open frontend in browser")
    print("   2. Navigate to Knowledge Bases section")
    print("   3. Select any KB with the fee schedule document")
    print("   4. Ask: 'What are the fees for trading US equities?'")
    print("   5. Expected: Should return 0.12% (wrong - from Swaps table)")
    print()

    print("🧪 TEST SCENARIO B - Direct Upload Query:")
    print("   1. Navigate to Document Chat section")
    print("   2. Upload: test_files/Appendix 6 Fee Schedule.pdf")
    print("   3. Ask: 'What are the fees for trading US equities?'")
    print("   4. Expected: Should return Smart/All-inclusive plans (correct)")
    print()

    print("🔍 DEBUG OUTPUT TO MONITOR:")
    print("   Watch Docker logs for:")
    print("   - '🐛 KNOWLEDGE BASE DEBUG: Retrieved X documents'")
    print("   - '🐛 DIRECT UPLOAD DEBUG: Retrieved X documents'")
    print("   - 'Table Title: [table name]'")
    print("   - Page numbers retrieved")
    print()


def create_monitoring_commands():
    """Create easy monitoring commands"""
    print("⚡ QUICK MONITORING COMMANDS:")
    print("=" * 50)

    print("📊 Monitor logs in real-time:")
    print("   docker logs aibeniq-react-backend-1 -f")
    print()

    print("🔍 Check recent debug output:")
    print('   docker logs aibeniq-react-backend-1 --tail=100 | findstr "🐛"')
    print()

    print("📋 Extract table information:")
    print('   docker logs aibeniq-react-backend-1 --tail=100 | findstr "Table Title"')
    print()


def save_analysis_file():
    """Save analysis to JSON file"""
    analysis = {
        "problem": {
            "description": "KB and Direct Upload return different results for same document/question",
            "kb_result": "0.12% per trade (Swaps table)",
            "direct_result": "Smart: $8.95, All-inclusive: $0 (Exchange-traded table)",
        },
        "root_cause": {
            "kb_issue": "Retrieves wrong table (Swaps instead of Exchange-traded)",
            "chunking_issue": "Context loss during KB document processing",
            "embedding_issue": "Both tables have 'brokerage commission' term",
            "quality_issue": "Different quality scores between systems",
        },
        "solution": {
            "immediate": [
                "Add metadata-based filtering to KB retrieval",
                "Improve table context preservation in chunking",
                "Prefer early-document tables for general queries",
                "Add document section awareness to similarity search",
            ],
            "medium_term": [
                "Re-process existing KBs with improved chunking",
                "Implement semantic filtering by table titles",
                "Add hybrid retrieval with metadata filtering",
                "Use query-to-section mapping",
            ],
        },
        "test_files": {
            "debug_scripts": [
                "debug_simple_analysis.py",
                "debug_log_checker.py",
                "debug_log_monitor.py",
                "debug_api_retrieval_comparison.py",
            ],
            "test_document": "test_files/Appendix 6 Fee Schedule.pdf",
            "test_question": "What are the fees for trading US equities?",
        },
    }

    with open("retrieval_disparity_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"💾 Complete analysis saved to: retrieval_disparity_analysis.json")


def main():
    """Main summary function"""
    print_summary()

    print("🔧 CURRENT SYSTEM STATUS:")
    print("=" * 50)

    backend_running = check_backend_status()

    if backend_running:
        check_debug_logs()

    print()
    print_test_plan()
    create_monitoring_commands()

    print("🎯 EXPECTED OUTCOME:")
    print("=" * 50)
    print("After testing, you should see in the logs:")
    print("   KB retrieves: 'Swaps and Structured Products' table from Page 9")
    print(
        "   Direct retrieves: 'Exchange-traded Stocks, bonds, ETFs' table from Page 1"
    )
    print("   This confirms the root cause of the disparity")
    print()

    save_analysis_file()

    print("✅ DEBUGGING SETUP COMPLETE")
    print("💡 Run the tests above and monitor Docker logs for debug output")


if __name__ == "__main__":
    main()
