#!/usr/bin/env python3
"""
Backend Log Monitor Script

Monitors Docker logs in real-time to capture the debug output we added
to the chatbot.py file, showing exactly what documents are retrieved
by Knowledge Base vs Direct Upload.
"""

import subprocess
import time
import json
import re
from threading import Thread
import sys


class LogMonitor:
    def __init__(self):
        self.kb_logs = []
        self.direct_logs = []
        self.monitoring = False

    def monitor_logs(self):
        """Monitor backend logs for debug output"""
        print("🔍 Monitoring backend logs for retrieval debug output...")
        print("📋 Looking for '🐛 KNOWLEDGE BASE DEBUG' and '🐛 DIRECT UPLOAD DEBUG'")
        print("⏳ Waiting for queries... (Press Ctrl+C to stop)")

        try:
            # Start following Docker logs
            process = subprocess.Popen(
                ["docker", "logs", "aibeniq-react-backend-1", "-f"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding="utf-8",
                errors="ignore",
                bufsize=1,
            )

            self.monitoring = True
            current_kb_session = []
            current_direct_session = []
            in_kb_debug = False
            in_direct_debug = False

            while self.monitoring:
                line = process.stdout.readline()
                if not line:
                    break

                line = line.strip()

                # Check for KB debug start
                if "🐛 KNOWLEDGE BASE DEBUG:" in line:
                    in_kb_debug = True
                    current_kb_session = [line]
                    print(f"\n📥 KB DEBUG DETECTED:")
                    print(f"   {line}")
                    continue

                # Check for KB debug end
                if "🐛 KB DEBUG END" in line:
                    in_kb_debug = False
                    current_kb_session.append(line)
                    self.kb_logs.append(current_kb_session.copy())
                    print(f"   {line}")
                    print(
                        f"✅ KB debug session captured ({len(current_kb_session)} lines)"
                    )
                    continue

                # Check for Direct debug start
                if "🐛 DIRECT UPLOAD DEBUG:" in line:
                    in_direct_debug = True
                    current_direct_session = [line]
                    print(f"\n📥 DIRECT DEBUG DETECTED:")
                    print(f"   {line}")
                    continue

                # Check for Direct debug end
                if "🐛 DIRECT UPLOAD DEBUG END" in line:
                    in_direct_debug = False
                    current_direct_session.append(line)
                    self.direct_logs.append(current_direct_session.copy())
                    print(f"   {line}")
                    print(
                        f"✅ Direct debug session captured ({len(current_direct_session)} lines)"
                    )

                    # Analyze if we have both KB and Direct logs
                    if self.kb_logs and self.direct_logs:
                        self.analyze_latest_comparison()
                    continue

                # Collect lines within debug sessions
                if in_kb_debug:
                    current_kb_session.append(line)
                    if "Table Title:" in line or "Page" in line:
                        print(f"   {line}")

                if in_direct_debug:
                    current_direct_session.append(line)
                    if "Table Title:" in line or "Page" in line:
                        print(f"   {line}")

        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
            self.monitoring = False
        except Exception as e:
            print(f"\n❌ Error monitoring logs: {e}")
            self.monitoring = False
        finally:
            if "process" in locals():
                process.terminate()

    def analyze_latest_comparison(self):
        """Analyze the latest KB vs Direct comparison"""
        if not self.kb_logs or not self.direct_logs:
            return

        latest_kb = self.kb_logs[-1]
        latest_direct = self.direct_logs[-1]

        print(f"\n🔬 ANALYZING LATEST RETRIEVAL COMPARISON")
        print("=" * 60)

        # Extract key information from logs
        kb_info = self.extract_retrieval_info(latest_kb, "KB")
        direct_info = self.extract_retrieval_info(latest_direct, "Direct")

        print(f"📊 RETRIEVAL SUMMARY:")
        print(f"   KB Retrieved: {kb_info.get('doc_count', 'Unknown')} documents")
        print(
            f"   Direct Retrieved: {direct_info.get('doc_count', 'Unknown')} documents"
        )

        # Compare table titles
        kb_tables = kb_info.get("table_titles", [])
        direct_tables = direct_info.get("table_titles", [])

        print(f"\n📋 TABLE COMPARISON:")
        print(f"   KB Tables: {kb_tables}")
        print(f"   Direct Tables: {direct_tables}")

        # Identify differences
        if kb_tables != direct_tables:
            print(f"\n🚨 DIFFERENCE DETECTED!")
            only_kb = set(kb_tables) - set(direct_tables)
            only_direct = set(direct_tables) - set(kb_tables)

            if only_kb:
                print(f"   ❌ Only in KB: {list(only_kb)}")
            if only_direct:
                print(f"   ✅ Only in Direct: {list(only_direct)}")

            # Check for the specific issue we identified
            if (
                "Swaps and Structured Products" in kb_tables
                and "Exchange-traded Stocks, bonds, ETFs" in direct_tables
            ):
                print(f"\n🎯 CONFIRMED: This matches the user's reported issue!")
                print(f"   KB incorrectly retrieved: Swaps table (0.12% fee)")
                print(
                    f"   Direct correctly retrieved: Exchange-traded table (Smart/All-inclusive plans)"
                )
        else:
            print(f"\n✅ Both systems retrieved same tables")

        # Compare pages
        kb_pages = kb_info.get("pages", [])
        direct_pages = direct_info.get("pages", [])

        print(f"\n📄 PAGE COMPARISON:")
        print(f"   KB Pages: {sorted(set(kb_pages))}")
        print(f"   Direct Pages: {sorted(set(direct_pages))}")

        if set(kb_pages) != set(direct_pages):
            print(f"   ⚠️  Different pages retrieved!")

        # Save detailed analysis
        analysis = {
            "timestamp": time.time(),
            "kb_info": kb_info,
            "direct_info": direct_info,
            "kb_logs": latest_kb,
            "direct_logs": latest_direct,
        }

        with open("retrieval_comparison_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"\n💾 Detailed analysis saved to: retrieval_comparison_analysis.json")

    def extract_retrieval_info(self, logs, system_name):
        """Extract key information from debug logs"""
        info = {
            "system": system_name,
            "doc_count": 0,
            "table_titles": [],
            "pages": [],
            "question": "",
        }

        for line in logs:
            # Extract document count
            if "Retrieved" in line and "documents for question" in line:
                match = re.search(r"Retrieved (\d+) documents", line)
                if match:
                    info["doc_count"] = int(match.group(1))

            # Extract question
            if "for question:" in line:
                match = re.search(r"for question: '([^']+)'", line)
                if match:
                    info["question"] = match.group(1)

            # Extract table titles
            if "Table Title:" in line:
                match = re.search(r"Table Title: (.+)", line)
                if match:
                    title = match.group(1).strip()
                    if title not in info["table_titles"]:
                        info["table_titles"].append(title)

            # Extract page numbers
            if "Page" in line:
                matches = re.findall(r"Page (\d+)", line)
                for match in matches:
                    page_num = int(match)
                    if page_num not in info["pages"]:
                        info["pages"].append(page_num)

        return info

    def print_instructions(self):
        """Print instructions for testing"""
        print("🚀 BACKEND LOG MONITOR FOR RETRIEVAL COMPARISON")
        print("=" * 60)
        print("📋 INSTRUCTIONS:")
        print("   1. This script monitors Docker logs for debug output")
        print("   2. Open the frontend in your browser")
        print("   3. First, ask a Knowledge Base about US equity fees")
        print("   4. Then, upload the same PDF and ask the same question")
        print("   5. The script will capture and compare both debug sessions")
        print("")
        print("🎯 EXPECTED BEHAVIOR:")
        print("   - KB should retrieve 'Swaps and Structured Products' (wrong)")
        print("   - Direct upload should retrieve 'Exchange-traded Stocks' (correct)")
        print("")
        print("💡 QUESTION TO TEST:")
        print("   'What are the fees for trading US equities?'")
        print("")


def main():
    monitor = LogMonitor()
    monitor.print_instructions()

    try:
        monitor.monitor_logs()
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped")

    # Print summary if we captured anything
    if monitor.kb_logs or monitor.direct_logs:
        print(f"\n📊 MONITORING SUMMARY:")
        print(f"   KB debug sessions captured: {len(monitor.kb_logs)}")
        print(f"   Direct upload debug sessions captured: {len(monitor.direct_logs)}")

        if monitor.kb_logs and monitor.direct_logs:
            print(f"   ✅ Can perform comparison analysis")
        else:
            print(f"   ⚠️  Need both KB and Direct queries for comparison")


if __name__ == "__main__":
    main()
