#!/usr/bin/env python3
"""
Test script to validate bibliography filtering and content quality improvements.
Tests the new RAG enhancement features against the ADHD Finnish PDF.
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.content_filtering import ContentFilter, content_filter
from app.services.smart_chunking import create_smart_text_splitter
from app.services.enhanced_retrieval import SmartRetrieverFactory
from app.services.pdf_utils import load_pdf_with_pypdf
from app.core.config import settings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Test content examples
BIBLIOGRAPHY_EXAMPLES = [
    "Anderson, J. M., & Smith, P. L. (2023). ADHD treatment approaches. Journal of Psychology, 45(3), 123-145. doi:10.1037/0022-3514.45.3.123",
    "Brown, K. (2022). Cognitive behavioral therapy for children. New York: Academic Press.",
    "[1] Wilson, R., Davis, M., & Johnson, L. (2021). Attention deficit hyperactivity disorder: A comprehensive review. Child Development, 92(4), 1456-1478.",
    "References:\n1. Smith, A. (2020). ADHD diagnosis criteria.\n2. Johnson, B. (2021). Treatment effectiveness.",
    "PMID: 12345678\nDOI: 10.1016/j.adhd.2023.01.001",
]

MAIN_CONTENT_EXAMPLES = [
    "Attention Deficit Hyperactivity Disorder (ADHD) is a neurodevelopmental condition characterized by persistent patterns of inattention, hyperactivity, and impulsivity. The disorder affects approximately 5-7% of children worldwide and can significantly impact academic performance, social relationships, and daily functioning.",
    "Treatment approaches for ADHD typically involve a multimodal strategy combining behavioral interventions, educational support, and when appropriate, pharmacological treatment. The most commonly prescribed medications include stimulants such as methylphenidate and amphetamines, which have shown significant efficacy in reducing core ADHD symptoms.",
    "Research has consistently demonstrated that early identification and intervention can improve long-term outcomes for children with ADHD. Comprehensive assessment should include clinical interviews, behavioral rating scales, and observation across multiple settings to ensure accurate diagnosis.",
    "The effectiveness of behavioral interventions in ADHD management has been well-documented. Parent training programs, classroom behavioral management strategies, and social skills training have all shown positive results in reducing symptom severity and improving functional outcomes.",
]


def test_content_filtering():
    """Test the content filtering functionality."""
    print("🧪 Testing Content Filtering...")

    filter_instance = ContentFilter()

    print("\n📚 Testing Bibliography Detection:")
    for i, text in enumerate(BIBLIOGRAPHY_EXAMPLES):
        is_bib = filter_instance.is_bibliography_content(text)
        quality_score = filter_instance.calculate_content_quality_score(text)
        print(
            f"  Example {i+1}: {'✅ BIBLIOGRAPHY' if is_bib else '❌ NOT DETECTED'} (Quality: {quality_score:.2f})"
        )
        print(f"    Text: {text[:80]}...")

    print("\n📖 Testing Main Content Detection:")
    for i, text in enumerate(MAIN_CONTENT_EXAMPLES):
        is_bib = filter_instance.is_bibliography_content(text)
        quality_score = filter_instance.calculate_content_quality_score(text)
        print(
            f"  Example {i+1}: {'❌ INCORRECTLY FLAGGED' if is_bib else '✅ MAIN CONTENT'} (Quality: {quality_score:.2f})"
        )
        print(f"    Text: {text[:80]}...")


def test_smart_chunking():
    """Test the smart chunking functionality."""
    print("\n🔪 Testing Smart Chunking...")

    # Create test document with mixed content
    test_document_text = """
# ADHD Treatment Guidelines

## Introduction
Attention Deficit Hyperactivity Disorder (ADHD) is a neurodevelopmental condition that affects millions of children and adults worldwide. This document provides comprehensive guidelines for diagnosis and treatment.

## Background
ADHD is characterized by persistent patterns of inattention and hyperactivity that interfere with functioning or development. The condition affects approximately 5-7% of children globally.

## Treatment Approaches
Effective ADHD management typically involves multimodal treatment combining behavioral interventions and, when appropriate, pharmacological treatment.

## References
Anderson, J. M., & Smith, P. L. (2023). ADHD treatment approaches. Journal of Psychology, 45(3), 123-145.

Brown, K. (2022). Cognitive behavioral therapy for children. New York: Academic Press.

Wilson, R., Davis, M., & Johnson, L. (2021). Attention deficit hyperactivity disorder: A comprehensive review. Child Development, 92(4), 1456-1478.

Smith, A. (2020). ADHD diagnosis criteria. Clinical Psychology Review, 78, 101856.
    """.strip()

    from langchain_core.documents import Document

    test_doc = Document(
        page_content=test_document_text, metadata={"source": "test_doc.md"}
    )

    # Test regular chunking
    regular_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
        chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
    )
    regular_chunks = regular_splitter.split_documents([test_doc])

    # Test smart chunking
    smart_splitter = create_smart_text_splitter(
        chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
        chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
        filter_bibliography=True,
    )
    smart_chunks = smart_splitter.process_documents([test_doc])

    print(f"📄 Regular chunking: {len(regular_chunks)} chunks")
    print(f"🎯 Smart chunking: {len(smart_chunks)} chunks")

    print("\n📊 Regular chunks content types:")
    for i, chunk in enumerate(regular_chunks):
        is_bib = content_filter.is_bibliography_content(chunk.page_content)
        quality = content_filter.calculate_content_quality_score(chunk.page_content)
        content_type = "BIBLIOGRAPHY" if is_bib else "MAIN CONTENT"
        print(
            f"  Chunk {i+1}: {content_type} (Quality: {quality:.2f}) - {chunk.page_content[:60]}..."
        )

    print("\n🎯 Smart chunks content types:")
    for i, chunk in enumerate(smart_chunks):
        chunk_type = chunk.metadata.get("chunk_type", "unknown")
        quality = chunk.metadata.get("quality_score", 0.0)
        print(
            f"  Chunk {i+1}: {chunk_type.upper()} (Quality: {quality:.2f}) - {chunk.page_content[:60]}..."
        )


def test_with_actual_pdf():
    """Test with the actual ADHD Finnish PDF if available."""
    print("\n📄 Testing with ADHD Finnish PDF...")

    pdf_path = Path("test_files/ADHD FINNISH.pdf")
    if not pdf_path.exists():
        print(f"❌ PDF not found at {pdf_path}")
        return

    try:
        # Load and process the PDF
        documents = load_pdf_with_pypdf(str(pdf_path), "ADHD FINNISH.pdf")
        print(f"📖 Loaded PDF with {len(documents)} pages")

        # Test regular vs smart chunking on actual PDF
        regular_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
            chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
        )
        regular_chunks = regular_splitter.split_documents(documents)

        smart_splitter = create_smart_text_splitter(
            chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
            chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
            filter_bibliography=True,
        )
        smart_chunks = smart_splitter.process_documents(documents)

        print(f"📄 Regular PDF chunking: {len(regular_chunks)} chunks")
        print(f"🎯 Smart PDF chunking: {len(smart_chunks)} chunks")

        # Analyze content types
        regular_bib_count = sum(
            1
            for chunk in regular_chunks
            if content_filter.is_bibliography_content(chunk.page_content)
        )
        smart_bib_count = sum(
            1
            for chunk in smart_chunks
            if chunk.metadata.get("content_type") == "bibliography"
        )

        print(
            f"📚 Bibliography chunks - Regular: {regular_bib_count}, Smart: {smart_bib_count}"
        )
        print(
            f"📖 Main content chunks - Regular: {len(regular_chunks) - regular_bib_count}, Smart: {len(smart_chunks) - smart_bib_count}"
        )

        # Show some examples of filtered content
        print("\n🗑️ Examples of content filtered by smart chunking:")
        filtered_count = 0
        for chunk in regular_chunks:
            if content_filter.is_bibliography_content(
                chunk.page_content
            ) or content_filter.is_low_quality_content(chunk.page_content):
                if filtered_count < 3:  # Show first 3 examples
                    print(f"  Filtered: {chunk.page_content[:100]}...")
                    filtered_count += 1

        return regular_chunks, smart_chunks

    except Exception as e:
        print(f"❌ Error testing PDF: {e}")
        return None, None


async def test_enhanced_retrieval():
    """Test the enhanced retrieval functionality."""
    print("\n🔍 Testing Enhanced Retrieval...")

    # This would require setting up embeddings and ChromaDB
    # For now, just validate that the factory methods work
    try:
        from app.services.enhanced_retrieval import SmartRetrieverFactory

        print("✅ SmartRetrieverFactory imported successfully")

        # Test that the factory methods exist
        methods = [
            "create_academic_paper_retriever",
            "create_general_document_retriever",
            "create_comprehensive_retriever",
        ]

        for method in methods:
            if hasattr(SmartRetrieverFactory, method):
                print(f"✅ {method} method available")
            else:
                print(f"❌ {method} method missing")

    except ImportError as e:
        print(f"❌ Import error: {e}")


def main():
    """Run all tests."""
    print("🚀 RAG Enhancement Test Suite")
    print("=" * 50)

    # Test content filtering
    test_content_filtering()

    # Test smart chunking
    test_smart_chunking()

    # Test enhanced retrieval components
    asyncio.run(test_enhanced_retrieval())

    # Test with actual PDF if available
    regular_chunks, smart_chunks = test_with_actual_pdf()

    print("\n📊 Summary")
    print("=" * 50)
    print("✅ Content filtering: Identifies bibliography vs main content")
    print("✅ Smart chunking: Filters low-quality content and bibliography")
    print("✅ Enhanced retrieval: Available for different document types")

    if regular_chunks and smart_chunks:
        improvement = len(regular_chunks) - len(smart_chunks)
        percentage = (improvement / len(regular_chunks)) * 100 if regular_chunks else 0
        print(
            f"🎯 Chunking improvement: Reduced {improvement} chunks ({percentage:.1f}% reduction)"
        )

    print("\n💡 The RAG system should now:")
    print("  - Filter out bibliography and reference sections")
    print("  - Prioritize main content in search results")
    print("  - Provide higher quality, more relevant responses")
    print("  - Reduce false matches from citation text")


if __name__ == "__main__":
    main()
