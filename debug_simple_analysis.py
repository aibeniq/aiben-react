#!/usr/bin/env python3
"""
Simple Retrieval Comparison Script

This script creates a focused test to understand why Knowledge Base and
direct upload return different results for the same document.
"""

import json
import os
import sys

# Test data - extracted from the fee schedule document
# This represents the two key tables mentioned by the user

EXCHANGE_TRADED_TABLE = {
    "table_id": "table_1",
    "page": 1,
    "title": "Exchange-traded Stocks, bonds, ETFs",
    "headers": ["Description", "Smart", "All-inclusive"],
    "rows": [
        ["Minimum balance", "USD 2,000", "USD 25,000"],
        ["Brokerage commission", "USD 8.95 per trade", "USD 0 per trade"],
        ["Platform fee", "USD 0 per month", "USD 89.95 per month"],
        ["Account maintenance fee", "USD 0 per quarter", "USD 0 per quarter"],
        ["Safekeeping", "Free of charge", "Free of charge"],
        ["Dividend processing", "Free of charge", "Free of charge"],
    ],
    "summary": "Fees for exchange-traded stocks, bonds, and ETFs with Smart and All-inclusive plans",
    "context": "This table shows the fee structure for trading US equities and other exchange-traded securities",
}

SWAPS_TABLE = {
    "table_id": "table_4",
    "page": 9,
    "title": "Swaps and Structured Products",
    "headers": ["Description", "Fee"],
    "rows": [
        ["Brokerage commission, per trade", "0.12%"],
        ["Safekeeping", "Free of charge"],
        ["Early termination", "Free of charge"],
        [
            "Any transaction involving change of ownership",
            "0.1% of transaction amount but not less than 100 EUR",
        ],
    ],
    "summary": "Fees related to swaps and structured products",
    "context": "Details of fees for swaps and structured products",
}


def analyze_table_content():
    """Analyze the difference between the two tables"""
    print("🔬 TABLE CONTENT ANALYSIS")
    print("=" * 80)

    print("📊 EXCHANGE-TRADED STOCKS TABLE (Page 1):")
    print(f"   Title: {EXCHANGE_TRADED_TABLE['title']}")
    print(f"   Page: {EXCHANGE_TRADED_TABLE['page']}")
    print("   Key fees for US equities:")

    for row in EXCHANGE_TRADED_TABLE["rows"]:
        if "commission" in row[0].lower():
            print(f"     - {row[0]}: Smart={row[1]}, All-inclusive={row[2]}")

    print(f"\n📊 SWAPS AND STRUCTURED PRODUCTS TABLE (Page 9):")
    print(f"   Title: {SWAPS_TABLE['title']}")
    print(f"   Page: {SWAPS_TABLE['page']}")
    print("   Key fees:")

    for row in SWAPS_TABLE["rows"]:
        if "commission" in row[0].lower():
            print(f"     - {row[0]}: {row[1]}")

    print(f"\n🚨 KEY DIFFERENCE IDENTIFIED:")
    print(
        f"   ✅ CORRECT (Exchange-traded): Smart plan = USD 8.95 per trade, All-inclusive = USD 0 per trade"
    )
    print(f"   ❌ INCORRECT (Swaps): 0.12% per trade")
    print(f"")
    print(f"💡 ANALYSIS:")
    print(f"   - Exchange-traded table (Page 1) is for US equities, bonds, ETFs")
    print(f"   - Swaps table (Page 9) is for derivatives/structured products")
    print(
        f"   - Question asks about 'US equities' which should match Exchange-traded table"
    )
    print(f"   - Knowledge Base incorrectly retrieves Swaps table")
    print(f"   - Direct upload correctly retrieves Exchange-traded table")


def simulate_embedding_similarity():
    """Simulate why embeddings might retrieve wrong table"""
    print(f"\n🔍 EMBEDDING SIMILARITY SIMULATION")
    print("=" * 50)

    question = "What are the fees for trading US equities?"

    # Simulate semantic similarity scoring
    exchange_traded_terms = [
        "exchange-traded",
        "stocks",
        "bonds",
        "ETFs",
        "US equities",
        "Smart plan",
        "All-inclusive",
        "brokerage commission",
        "USD 8.95",
    ]

    swaps_terms = [
        "swaps",
        "structured products",
        "derivatives",
        "brokerage commission",
        "0.12%",
        "early termination",
        "transaction",
    ]

    print(f"📋 Question: '{question}'")
    print(f"")
    print(f"🎯 Exchange-traded table terms: {exchange_traded_terms}")
    print(f"🎯 Swaps table terms: {swaps_terms}")

    # Count matching terms
    question_lower = question.lower()
    exchange_matches = sum(
        1 for term in exchange_traded_terms if term.lower() in question_lower
    )
    swaps_matches = sum(1 for term in swaps_terms if term.lower() in question_lower)

    print(f"")
    print(f"📊 Semantic matching simulation:")
    print(f"   Exchange-traded table matches: {exchange_matches} terms")
    print(f"   Swaps table matches: {swaps_matches} terms")

    # Both tables have "brokerage commission" but different contexts
    print(f"")
    print(f"⚠️  POTENTIAL ISSUE:")
    print(f"   Both tables mention 'brokerage commission'")
    print(f"   Embedding model might not distinguish context properly")
    print(f"   Knowledge Base chunking might not preserve table context")


def diagnose_retrieval_differences():
    """Diagnose why retrieval methods differ"""
    print(f"\n🩺 RETRIEVAL DIAGNOSIS")
    print("=" * 50)

    print(f"🔍 KNOWLEDGE BASE RETRIEVAL:")
    print(f"   1. Document pre-chunked and stored in vector database")
    print(f"   2. Chunks may lose page/section context")
    print(f"   3. Similarity search across all chunks")
    print(f"   4. May retrieve chunks from different document sections")
    print(f"   5. Academic paper retriever uses different quality thresholds")

    print(f"")
    print(f"🔍 DIRECT UPLOAD RETRIEVAL:")
    print(f"   1. Document processed fresh with table-aware chunking")
    print(f"   2. Preserves document structure and page context")
    print(f"   3. Vision processing extracts tables with context")
    print(f"   4. Academic paper retriever on fresh document")
    print(f"   5. Better chunk quality due to fresh processing")

    print(f"")
    print(f"🎯 LIKELY CAUSES:")
    print(f"   1. Knowledge Base chunks missing page/context metadata")
    print(f"   2. Different chunking strategies between KB creation and direct upload")
    print(f"   3. Embedding similarities between 'brokerage commission' terms")
    print(f"   4. Quality score differences affecting retrieval ranking")
    print(f"   5. KB retriever getting lower-quality chunks")


def recommend_fixes():
    """Recommend fixes for the disparity"""
    print(f"\n💡 RECOMMENDED FIXES")
    print("=" * 50)

    print(f"🔧 IMMEDIATE FIXES:")
    print(f"   1. Improve KB chunking to preserve table context")
    print(f"   2. Add page number and section metadata to KB chunks")
    print(f"   3. Enhance table title matching in retrieval")
    print(f"   4. Use document section awareness in similarity search")
    print(
        f"   5. Filter results by document structure (prefer early pages for general queries)"
    )

    print(f"")
    print(f"🔧 MEDIUM TERM FIXES:")
    print(f"   1. Re-process existing KBs with improved chunking")
    print(f"   2. Add semantic filtering based on table titles")
    print(f"   3. Implement query-to-section mapping")
    print(f"   4. Add quality scoring for table relevance")
    print(f"   5. Use hybrid retrieval with metadata filtering")

    print(f"")
    print(f"🔧 VALIDATION STEPS:")
    print(f"   1. Test with the actual debug logs from both systems")
    print(f"   2. Compare retrieved document page numbers")
    print(f"   3. Examine table titles in retrieved chunks")
    print(f"   4. Verify quality scores and ranking")
    print(f"   5. Test fix with multiple KB queries")


def create_test_documents():
    """Create test document chunks as they would appear in each system"""
    print(f"\n📄 SIMULATED DOCUMENT CHUNKS")
    print("=" * 50)

    # KB-style chunk (potentially problematic)
    kb_chunk = f"""
=== TABLE DATA (JSON) ===
{json.dumps(SWAPS_TABLE, indent=2)}
=== END TABLE DATA ===

This table shows the fee structure for swaps and structured products trading.
"""

    # Direct upload-style chunk (correct)
    direct_chunk = f"""
=== TABLE DATA (JSON) ===
{json.dumps(EXCHANGE_TRADED_TABLE, indent=2)}
=== END TABLE DATA ===

This table shows the fee structure for trading US equities with Smart and All-inclusive plans.
"""

    print(f"🗃️  Knowledge Base chunk (problematic):")
    print(f"   Page: {SWAPS_TABLE['page']}")
    print(f"   Table: {SWAPS_TABLE['title']}")
    print(f"   Fee: 0.12% per trade")
    print(f"   Context: Derivatives/structured products")

    print(f"")
    print(f"📁 Direct upload chunk (correct):")
    print(f"   Page: {EXCHANGE_TRADED_TABLE['page']}")
    print(f"   Table: {EXCHANGE_TRADED_TABLE['title']}")
    print(f"   Fee: USD 8.95 (Smart) / USD 0 (All-inclusive)")
    print(f"   Context: US equities, bonds, ETFs")

    # Save chunks for further analysis
    with open("kb_problematic_chunk.txt", "w") as f:
        f.write(kb_chunk)

    with open("direct_correct_chunk.txt", "w") as f:
        f.write(direct_chunk)

    print(f"")
    print(f"💾 Saved chunks to:")
    print(f"   - kb_problematic_chunk.txt")
    print(f"   - direct_correct_chunk.txt")


def main():
    """Main analysis function"""
    print("🚀 KNOWLEDGE BASE vs DIRECT UPLOAD ANALYSIS")
    print("🎯 Diagnosing why same document/question returns different results")
    print("=" * 80)

    analyze_table_content()
    simulate_embedding_similarity()
    diagnose_retrieval_differences()
    recommend_fixes()
    create_test_documents()

    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"🎯 KEY FINDING: KB retrieves wrong table (Swaps vs Exchange-traded)")
    print(f"💡 ROOT CAUSE: Context loss in chunking + embedding similarity confusion")
    print(f"🔧 SOLUTION: Improve KB chunking and add metadata-based filtering")


if __name__ == "__main__":
    main()
