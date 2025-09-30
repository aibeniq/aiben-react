#!/usr/bin/env python3
"""
Simple Backend Debug Output Checker

Periodically checks backend logs for debug output and displays key findings.
"""

import subprocess
import time
import re
import json


def check_recent_logs():
    """Check recent backend logs for debug output"""
    try:
        # Get recent logs
        result = subprocess.run(
            ["docker", "logs", "aibeniq-react-backend-1", "--tail=100"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            print(f"❌ Error getting logs: {result.stderr}")
            return

        logs = result.stdout.split("\n")

        # Look for debug output
        kb_debug_lines = []
        direct_debug_lines = []

        for line in logs:
            if "🐛 KNOWLEDGE BASE DEBUG" in line or "🐛 KB DEBUG" in line:
                kb_debug_lines.append(line.strip())
            elif "🐛 DIRECT UPLOAD DEBUG" in line or "🐛 DIRECT DEBUG" in line:
                direct_debug_lines.append(line.strip())
            elif ("Table Title:" in line or "Page" in line) and (
                "DEBUG" in line or "🐛" in line
            ):
                if kb_debug_lines:
                    kb_debug_lines.append(line.strip())
                elif direct_debug_lines:
                    direct_debug_lines.append(line.strip())

        return kb_debug_lines, direct_debug_lines

    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        return [], []


def extract_table_info(debug_lines):
    """Extract table information from debug lines"""
    tables = []
    pages = []
    doc_count = 0

    for line in debug_lines:
        # Extract document count
        if "Retrieved" in line and "documents" in line:
            match = re.search(r"Retrieved (\d+) documents", line)
            if match:
                doc_count = int(match.group(1))

        # Extract table titles
        if "Table Title:" in line:
            match = re.search(r"Table Title: (.+)", line)
            if match:
                table_title = match.group(1).strip()
                if table_title not in tables:
                    tables.append(table_title)

        # Extract pages
        page_matches = re.findall(r"Page (\d+)", line)
        for page in page_matches:
            if int(page) not in pages:
                pages.append(int(page))

    return {"doc_count": doc_count, "tables": tables, "pages": sorted(pages)}


def main():
    print("🔍 BACKEND DEBUG LOG CHECKER")
    print("=" * 50)
    print("📋 Checking for recent retrieval debug output...")
    print("💡 Run queries in the frontend to generate debug logs")
    print("")

    last_kb_count = 0
    last_direct_count = 0

    try:
        while True:
            kb_lines, direct_lines = check_recent_logs()

            if len(kb_lines) > last_kb_count:
                print(f"\n📥 NEW KB DEBUG OUTPUT:")
                kb_info = extract_table_info(kb_lines)
                print(f"   Documents: {kb_info['doc_count']}")
                print(f"   Tables: {kb_info['tables']}")
                print(f"   Pages: {kb_info['pages']}")
                last_kb_count = len(kb_lines)

            if len(direct_lines) > last_direct_count:
                print(f"\n📥 NEW DIRECT DEBUG OUTPUT:")
                direct_info = extract_table_info(direct_lines)
                print(f"   Documents: {direct_info['doc_count']}")
                print(f"   Tables: {direct_info['tables']}")
                print(f"   Pages: {direct_info['pages']}")
                last_direct_count = len(direct_lines)

            # Compare if we have both
            if kb_lines and direct_lines:
                kb_info = extract_table_info(kb_lines)
                direct_info = extract_table_info(direct_lines)

                print(f"\n🔬 COMPARISON:")
                print(f"   KB Tables: {kb_info['tables']}")
                print(f"   Direct Tables: {direct_info['tables']}")

                if kb_info["tables"] != direct_info["tables"]:
                    print(f"   🚨 DIFFERENCE DETECTED!")

                    # Check for the specific issue
                    kb_has_swaps = any("Swaps" in table for table in kb_info["tables"])
                    direct_has_exchange = any(
                        "Exchange-traded" in table for table in direct_info["tables"]
                    )

                    if kb_has_swaps and direct_has_exchange:
                        print(
                            f"   ✅ CONFIRMED: KB gets Swaps table, Direct gets Exchange-traded table"
                        )
                        print(f"   🎯 This matches the reported issue!")
                else:
                    print(f"   ✅ Both retrieved same tables")

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped")


if __name__ == "__main__":
    main()
