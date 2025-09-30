#!/usr/bin/env python3
"""
Knowledge Base vs Direct Upload Retrieval Comparison Debug Script (API Version)

This script uses the API endpoints to compare retrieval results between
Knowledge Base queries and direct document uploads.
"""

import requests
import json
import os
import time
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
TEST_QUESTION = "What are the fees for trading US equities?"
TEST_PDF_PATH = "test_files/Appendix 6 Fee Schedule.pdf"


class APIRetrievalDebugger:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()

    def get_knowledge_bases(self) -> List[Dict]:
        """Get available knowledge bases"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/knowledge-bases/")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get knowledge bases: {response.status_code}")
                print(response.text)
                return []
        except Exception as e:
            print(f"❌ Error getting knowledge bases: {e}")
            return []

    def query_knowledge_base(self, kb_id: str, question: str) -> Dict[str, Any]:
        """Query a knowledge base"""
        try:
            params = {"question": question, "use_default_models": True}

            print(f"🔍 Querying KB {kb_id} with: {question}")
            response = self.session.get(
                f"{self.base_url}/api/v1/chat/knowledge-bases/{kb_id}", params=params
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ KB Query successful")
                print(f"📄 Answer length: {len(result.get('answer', ''))}")
                print(f"📋 Sources: {len(result.get('sources', []))}")

                # Analyze sources
                sources = result.get("sources", [])
                for i, source in enumerate(sources):
                    print(f"  Source {i+1}: Page {source.get('page', 'Unknown')}")
                    if "content" in source:
                        content = (
                            source["content"][:200] + "..."
                            if len(source["content"]) > 200
                            else source["content"]
                        )
                        print(f"    Content: {content}")

                return result
            else:
                print(f"❌ KB Query failed: {response.status_code}")
                print(response.text)
                return {"error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            print(f"❌ KB Query error: {e}")
            return {"error": str(e)}

    def query_direct_upload(self, pdf_path: str, question: str) -> Dict[str, Any]:
        """Query with direct document upload"""
        try:
            if not os.path.exists(pdf_path):
                return {"error": f"File not found: {pdf_path}"}

            # Upload and query document
            params = {"question": question, "use_default_models": True}

            with open(pdf_path, "rb") as f:
                files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}

                print(f"📁 Uploading {pdf_path} and querying: {question}")
                response = self.session.post(
                    f"{self.base_url}/api/v1/chat/document", files=files, params=params
                )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Direct upload query successful")
                print(f"📄 Answer length: {len(result.get('answer', ''))}")
                print(f"📋 Sources: {len(result.get('sources', []))}")

                # Analyze sources
                sources = result.get("sources", [])
                for i, source in enumerate(sources):
                    print(f"  Source {i+1}: Page {source.get('page', 'Unknown')}")
                    if "content" in source:
                        content = (
                            source["content"][:200] + "..."
                            if len(source["content"]) > 200
                            else source["content"]
                        )
                        print(f"    Content: {content}")

                return result
            else:
                print(f"❌ Direct upload query failed: {response.status_code}")
                print(response.text)
                return {"error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            print(f"❌ Direct upload error: {e}")
            return {"error": str(e)}

    def extract_table_info(self, content: str) -> str:
        """Extract table title from content"""
        if "=== TABLE DATA (JSON) ===" in content:
            try:
                table_start = content.find("{")
                table_end = content.rfind("}")
                if table_start != -1 and table_end != -1:
                    table_json = content[table_start : table_end + 1]
                    table_data = json.loads(table_json)
                    return table_data.get("title", "Unknown table")
            except:
                return "Table parse error"
        return "No table"

    def analyze_answer_content(self, answer: str) -> Dict[str, Any]:
        """Analyze the answer content for key information"""
        analysis = {
            "mentions_smart_plan": "smart" in answer.lower()
            and "plan" in answer.lower(),
            "mentions_all_inclusive": "all-inclusive" in answer.lower()
            or "all inclusive" in answer.lower(),
            "mentions_0_12_percent": "0.12%" in answer,
            "mentions_8_95": "8.95" in answer,
            "mentions_swaps": "swaps" in answer.lower(),
            "mentions_structured_products": "structured products" in answer.lower(),
            "mentions_exchange_traded": "exchange-traded" in answer.lower()
            or "exchange traded" in answer.lower(),
            "answer_length": len(answer),
        }

        # Extract fee mentions
        import re

        fee_patterns = [
            r"\$[\d,]+\.?\d*",  # Dollar amounts
            r"[\d,]+\.?\d*%",  # Percentages
            r"USD\s*[\d,]+\.?\d*",  # USD amounts
        ]

        fees_found = []
        for pattern in fee_patterns:
            fees_found.extend(re.findall(pattern, answer))

        analysis["fees_mentioned"] = list(set(fees_found))

        return analysis

    def compare_results(self, kb_result: Dict, direct_result: Dict, question: str):
        """Compare and analyze differences between KB and direct upload results"""
        print(f"\n🔬 DETAILED COMPARISON ANALYSIS")
        print("=" * 80)

        if "error" in kb_result:
            print(f"❌ KB Error: {kb_result['error']}")
        if "error" in direct_result:
            print(f"❌ Direct Upload Error: {direct_result['error']}")

        if "error" in kb_result or "error" in direct_result:
            return

        # Answer analysis
        kb_answer = kb_result.get("answer", "")
        direct_answer = direct_result.get("answer", "")

        print(f"📝 ANSWER COMPARISON:")
        print(f"   KB Answer length: {len(kb_answer)} chars")
        print(f"   Direct Answer length: {len(direct_answer)} chars")

        kb_analysis = self.analyze_answer_content(kb_answer)
        direct_analysis = self.analyze_answer_content(direct_answer)

        print(f"\n💰 FEE ANALYSIS:")
        print(f"   KB fees mentioned: {kb_analysis['fees_mentioned']}")
        print(f"   Direct fees mentioned: {direct_analysis['fees_mentioned']}")

        print(f"\n🔍 CONTENT ANALYSIS:")
        content_checks = [
            ("Smart plan mention", "mentions_smart_plan"),
            ("All-inclusive plan mention", "mentions_all_inclusive"),
            ("0.12% mention", "mentions_0_12_percent"),
            ("$8.95 mention", "mentions_8_95"),
            ("Swaps mention", "mentions_swaps"),
            ("Structured products mention", "mentions_structured_products"),
            ("Exchange-traded mention", "mentions_exchange_traded"),
        ]

        for check_name, check_key in content_checks:
            kb_has = kb_analysis[check_key]
            direct_has = direct_analysis[check_key]

            if kb_has != direct_has:
                print(f"   ⚠️  {check_name}: KB={kb_has}, Direct={direct_has}")
            else:
                print(f"   ✅ {check_name}: Both={kb_has}")

        # Source analysis
        kb_sources = kb_result.get("sources", [])
        direct_sources = direct_result.get("sources", [])

        print(f"\n📄 SOURCE ANALYSIS:")
        print(f"   KB sources: {len(kb_sources)}")
        print(f"   Direct sources: {len(direct_sources)}")

        # Analyze table content in sources
        kb_tables = []
        direct_tables = []

        for source in kb_sources:
            content = source.get("content", "")
            table_title = self.extract_table_info(content)
            if table_title != "No table":
                kb_tables.append({"page": source.get("page"), "title": table_title})

        for source in direct_sources:
            content = source.get("content", "")
            table_title = self.extract_table_info(content)
            if table_title != "No table":
                direct_tables.append({"page": source.get("page"), "title": table_title})

        print(f"\n📊 TABLE ANALYSIS:")
        print(f"   KB tables found: {len(kb_tables)}")
        for table in kb_tables:
            print(f"     - Page {table['page']}: {table['title']}")

        print(f"   Direct tables found: {len(direct_tables)}")
        for table in direct_tables:
            print(f"     - Page {table['page']}: {table['title']}")

        # Key difference identification
        kb_table_titles = {t["title"] for t in kb_tables}
        direct_table_titles = {t["title"] for t in direct_tables}

        if kb_table_titles != direct_table_titles:
            print(f"\n🚨 TABLE TITLE MISMATCH DETECTED!")
            print(f"   Only in KB: {kb_table_titles - direct_table_titles}")
            print(f"   Only in Direct: {direct_table_titles - kb_table_titles}")
            print(f"   Common: {kb_table_titles & direct_table_titles}")
        else:
            print(f"\n✅ Both systems retrieved same table types")

        # Print sample answers for manual inspection
        print(f"\n📋 SAMPLE ANSWERS (first 500 chars):")
        print(f"   KB Answer: {kb_answer[:500]}...")
        print(f"   Direct Answer: {direct_answer[:500]}...")

    def run_comparison(
        self, kb_id: str = None, pdf_path: str = None, question: str = None
    ):
        """Run the full comparison"""
        print("🚀 API-BASED RETRIEVAL COMPARISON")
        print("=" * 80)

        if not question:
            question = TEST_QUESTION

        if not pdf_path:
            pdf_path = TEST_PDF_PATH

        print(f"🎯 Testing Question: '{question}'")
        print(f"📁 PDF Path: {pdf_path}")

        # Get knowledge bases if no KB ID provided
        if not kb_id:
            print(f"\n🗃️  Finding Knowledge Bases...")
            kbs = self.get_knowledge_bases()

            if not kbs:
                print("❌ No knowledge bases found")
                return

            # Find a KB with the fee schedule document
            target_kb = None
            for kb in kbs:
                if any(
                    word in kb.get("title", "").lower()
                    for word in ["equity", "fee", "schedule"]
                ):
                    target_kb = kb
                    break

            if not target_kb:
                target_kb = kbs[0]  # Use first available

            kb_id = target_kb["id"]
            print(f"📚 Using KB: {target_kb['title']} (ID: {kb_id})")

        # Wait a moment for backend to be ready
        print(f"\n⏳ Waiting for backend...")
        time.sleep(2)

        # Run both queries
        print(f"\n" + "=" * 50)
        kb_result = self.query_knowledge_base(kb_id, question)

        print(f"\n" + "=" * 50)
        direct_result = self.query_direct_upload(pdf_path, question)

        # Compare results
        self.compare_results(kb_result, direct_result, question)

        # Save results
        results = {
            "question": question,
            "kb_id": kb_id,
            "pdf_path": pdf_path,
            "kb_result": kb_result,
            "direct_result": direct_result,
            "timestamp": time.time(),
        }

        output_file = "api_retrieval_comparison_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_file}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="API-based retrieval comparison")
    parser.add_argument("--kb-id", help="Knowledge Base ID to test")
    parser.add_argument("--pdf-path", help="Path to PDF file", default=TEST_PDF_PATH)
    parser.add_argument("--question", help="Question to test", default=TEST_QUESTION)
    parser.add_argument("--url", help="Base URL for API", default=BASE_URL)

    args = parser.parse_args()

    debugger = APIRetrievalDebugger()
    if args.url != BASE_URL:
        debugger.base_url = args.url

    debugger.run_comparison(args.kb_id, args.pdf_path, args.question)


if __name__ == "__main__":
    main()
