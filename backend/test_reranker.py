"""
Test script for Cross-Encoder Reranker implementation.

This script demonstrates how to use the new cross-encoder reranking functionality.
Run this after installing sentence-transformers:
    uv pip install sentence-transformers
"""

import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from langchain_core.documents import Document
from app.services.reranker import CrossEncoderReranker, rerank_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_reranking():
    """Test basic reranking functionality."""
    print("\n" + "="*60)
    print("TEST 1: Basic Reranking")
    print("="*60)
    
    # Sample query
    query = "What are the symptoms of diabetes?"
    
    # Sample documents (simulating retrieval results)
    documents = [
        Document(
            page_content="Diabetes is a metabolic disease affecting blood sugar levels.",
            metadata={"source": "doc1.pdf", "quality_score": 0.7}
        ),
        Document(
            page_content="Common symptoms of diabetes include increased thirst, frequent urination, extreme hunger, and fatigue.",
            metadata={"source": "doc2.pdf", "quality_score": 0.9}
        ),
        Document(
            page_content="The history of diabetes treatment dates back centuries.",
            metadata={"source": "doc3.pdf", "quality_score": 0.6}
        ),
        Document(
            page_content="Type 1 and Type 2 diabetes have different causes but similar symptoms like blurred vision and slow healing.",
            metadata={"source": "doc4.pdf", "quality_score": 0.8}
        ),
    ]
    
    print(f"\nQuery: {query}")
    print(f"Number of documents: {len(documents)}")
    
    # Initialize reranker
    print("\nInitializing cross-encoder reranker...")
    reranker = CrossEncoderReranker()
    
    # Rerank documents
    print("\nReranking documents...")
    ranked_results = reranker.rerank(query, documents)
    
    # Display results
    print("\n" + "-"*60)
    print("Reranked Results:")
    print("-"*60)
    for i, (doc, score) in enumerate(ranked_results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   Content: {doc.page_content[:80]}...")
        print(f"   Source: {doc.metadata.get('source', 'unknown')}")
    
    return ranked_results


def test_quality_fusion():
    """Test reranking with quality score fusion."""
    print("\n" + "="*60)
    print("TEST 2: Quality Fusion Reranking")
    print("="*60)
    
    query = "machine learning algorithms"
    
    documents = [
        Document(
            page_content="Machine learning uses statistical algorithms to learn from data.",
            metadata={"source": "ml_intro.pdf", "quality_score": 0.9, "content_type": "main_content"}
        ),
        Document(
            page_content="References: Smith et al. (2020), Jones (2019), ML Conference 2021.",
            metadata={"source": "ml_intro.pdf", "quality_score": 0.3, "content_type": "bibliography"}
        ),
        Document(
            page_content="Popular ML algorithms include decision trees, neural networks, and support vector machines.",
            metadata={"source": "algorithms.pdf", "quality_score": 0.85, "content_type": "main_content"}
        ),
    ]
    
    print(f"\nQuery: {query}")
    print(f"Number of documents: {len(documents)}")
    
    # Initialize reranker
    reranker = CrossEncoderReranker()
    
    # Rerank with quality fusion
    print("\nReranking with quality fusion (70% cross-encoder, 30% quality)...")
    reranked_docs = reranker.rerank_with_quality_fusion(
        query, documents, quality_weight=0.3
    )
    
    # Display results
    print("\n" + "-"*60)
    print("Fused Reranked Results:")
    print("-"*60)
    for i, doc in enumerate(reranked_docs, 1):
        print(f"\n{i}. Content: {doc.page_content[:80]}...")
        print(f"   Quality Score: {doc.metadata.get('quality_score', 'N/A')}")
        print(f"   Content Type: {doc.metadata.get('content_type', 'unknown')}")
        print(f"   Source: {doc.metadata.get('source', 'unknown')}")
    
    return reranked_docs


def test_convenience_function():
    """Test the convenience rerank_documents function."""
    print("\n" + "="*60)
    print("TEST 3: Convenience Function")
    print("="*60)
    
    query = "treatment for hypertension"
    
    documents = [
        Document(page_content="Hypertension treatment includes lifestyle changes and medication."),
        Document(page_content="High blood pressure affects millions of people worldwide."),
        Document(page_content="ACE inhibitors and beta blockers are common hypertension medications."),
    ]
    
    print(f"\nQuery: {query}")
    print("\nUsing convenience function rerank_documents()...")
    
    # Use convenience function
    reranked = rerank_documents(query, documents, top_k=2)
    
    print("\n" + "-"*60)
    print("Top 2 Results:")
    print("-"*60)
    for i, doc in enumerate(reranked, 1):
        print(f"\n{i}. {doc.page_content}")
    
    return reranked


def test_different_models():
    """Compare different cross-encoder models."""
    print("\n" + "="*60)
    print("TEST 4: Different Models Comparison")
    print("="*60)
    
    query = "climate change effects"
    
    documents = [
        Document(page_content="Climate change leads to rising sea levels and extreme weather."),
        Document(page_content="The Paris Agreement aims to limit global warming."),
        Document(page_content="Greenhouse gas emissions are the primary driver of climate change."),
    ]
    
    models = [
        "cross-encoder/ms-marco-MiniLM-L-6-v2",  # Fast
        # "cross-encoder/ms-marco-MiniLM-L-12-v2",  # More accurate (uncomment if needed)
    ]
    
    for model_name in models:
        print(f"\n\nTesting model: {model_name}")
        print("-" * 60)
        
        try:
            reranker = CrossEncoderReranker(model_name=model_name)
            results = reranker.rerank(query, documents, top_k=2)
            
            for i, (doc, score) in enumerate(results, 1):
                print(f"{i}. Score: {score:.4f} | {doc.page_content[:60]}...")
        except Exception as e:
            print(f"Error with model {model_name}: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CROSS-ENCODER RERANKER TESTS")
    print("="*60)
    
    try:
        # Test 1: Basic reranking
        test_basic_reranking()
        
        # Test 2: Quality fusion
        test_quality_fusion()
        
        # Test 3: Convenience function
        test_convenience_function()
        
        # Test 4: Different models
        test_different_models()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Enable in config: RAG_USE_RERANKER=True")
        print("2. Choose model: RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("3. Restart backend to apply changes")
        print("4. Test with your actual knowledge base queries")
        
    except ImportError as e:
        print("\n" + "="*60)
        print("ERROR: sentence-transformers not installed")
        print("="*60)
        print("\nPlease install it with:")
        print("  uv pip install sentence-transformers")
        print("\nOr add to pyproject.toml optional dependencies:")
        print("  [project.optional-dependencies]")
        print("  reranker = [\"sentence-transformers>=2.2.0,<4.0.0\"]")
        print("\nThen run: uv sync --extra reranker")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
