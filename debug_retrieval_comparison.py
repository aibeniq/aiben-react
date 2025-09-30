#!/usr/bin/env python3
"""
Knowledge Base vs Direct Upload Retrieval Comparison Debug Script

This script simulates both Knowledge Base and direct document upload retrieval
to identify why they return different results for the same document and question.
"""

import sys
import os
import asyncio
import uuid
import tempfile
import traceback
import json
from typing import List, Dict, Any

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

# Now import from the backend
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm
from app.services.enhanced_retrieval import SmartRetrieverFactory
from app.services.document_utils import (
    extract_documents_from_file_unified,
    ensure_documents_for_vector_search,
)
from app.services.smart_chunking import StructureAwareTextSplitter
from app.models import KnowledgeBase, EmbeddingModel
from app.core.database import engine
from sqlmodel import Session, select

# Test configuration
TEST_QUESTION = "What are the fees for trading US equities?"
TEST_PDF_PATH = "test_files/Appendix 6 Fee Schedule.pdf"  # Update this path as needed


class RetrievalDebugger:
    def __init__(self):
        self.session = None
        self.embedding_model = None
        self.llm = None
        self.TEST_QUESTION = TEST_QUESTION

    async def setup(self):
        """Initialize database session and models"""
        print("🔧 Setting up debug environment...")

        # Create database session
        self.session = Session(engine)

        # Get default embedding model
        try:
            # Get the first available embedding model
            embedding_models = self.session.exec(select(EmbeddingModel)).all()
            if not embedding_models:
                print("❌ No embedding models found in database")
                return False

            self.embedding_model = embedding_models[0]
            print(f"✅ Using embedding model: {self.embedding_model.model_name}")

            # Get default LLM
            self.llm = get_default_llm()
            print(f"✅ Using LLM: {self.llm}")

            return True

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            traceback.print_exc()
            return False

    def cleanup(self):
        """Clean up resources"""
        if self.session:
            self.session.close()

    async def simulate_kb_retrieval(self, kb_id: str, question: str) -> Dict[str, Any]:
        """Simulate Knowledge Base retrieval"""
        print(f"\n🔍 KB RETRIEVAL SIMULATION")
        print(f"📋 Question: {question}")
        print(f"🗃️  KB ID: {kb_id}")

        try:
            # Get the knowledge base
            kb = self.session.get(KnowledgeBase, kb_id)
            if not kb:
                return {"error": f"Knowledge base {kb_id} not found"}

            print(f"📚 KB Title: {kb.title}")
            print(f"📊 Sources: {kb.number_of_sources}")

            # Load embedding model
            embeddings = load_embeddings_model(self.embedding_model)

            # Create retriever using SmartRetrieverFactory (same as in chatbot.py)
            retriever_factory = SmartRetrieverFactory()
            retriever = retriever_factory.create_academic_paper_retriever(
                session=self.session, kb_id=kb_id, embeddings=embeddings, llm=self.llm
            )

            # Retrieve documents
            docs = retriever.get_relevant_documents(question)

            print(f"📄 Retrieved {len(docs)} documents")

            # Analyze retrieved documents
            results = []
            for i, doc in enumerate(docs):
                metadata = doc.metadata
                content_preview = (
                    doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content
                )

                # Extract table title if present
                table_title = "No table"
                if "=== TABLE DATA (JSON) ===" in doc.page_content:
                    try:
                        table_start = doc.page_content.find("{")
                        table_end = doc.page_content.rfind("}")
                        if table_start != -1 and table_end != -1:
                            table_json = doc.page_content[table_start : table_end + 1]
                            table_data = json.loads(table_json)
                            table_title = table_data.get("title", "Unknown table")
                    except:
                        table_title = "Table parse error"

                doc_info = {
                    "index": i,
                    "page": metadata.get("page", "Unknown"),
                    "source": metadata.get("source", "Unknown"),
                    "content_preview": content_preview,
                    "table_title": table_title,
                    "has_table": "=== TABLE DATA (JSON) ===" in doc.page_content,
                    "metadata": metadata,
                }
                results.append(doc_info)

                print(
                    f"  📄 Doc {i}: Page {doc_info['page']} - {doc_info['table_title']}"
                )
                print(f"      Content: {content_preview}")

            return {
                "success": True,
                "question": question,
                "kb_id": kb_id,
                "kb_title": kb.title,
                "retriever_type": "academic_paper_retriever",
                "document_count": len(docs),
                "documents": results,
            }

        except Exception as e:
            print(f"❌ KB retrieval failed: {e}")
            traceback.print_exc()
            return {"error": str(e)}

    async def simulate_direct_upload_retrieval(
        self, pdf_path: str, question: str
    ) -> Dict[str, Any]:
        """Simulate direct document upload retrieval"""
        print(f"\n🔍 DIRECT UPLOAD RETRIEVAL SIMULATION")
        print(f"📋 Question: {question}")
        print(f"📁 File: {pdf_path}")

        try:
            if not os.path.exists(pdf_path):
                return {"error": f"File {pdf_path} not found"}

            # Extract documents from file (same as in chatbot.py)
            with open(pdf_path, "rb") as f:
                file_bytes = f.read()

            print(f"📄 File size: {len(file_bytes)} bytes")

            # Process document with table extraction (same as direct upload)
            documents = extract_documents_from_file_unified(
                filename=os.path.basename(pdf_path),
                file_bytes=file_bytes,
                llm=self.llm,  # Use LLM for vision processing
            )

            print(f"📊 Extracted {len(documents)} raw documents")

            # Apply smart chunking
            text_splitter = StructureAwareTextSplitter(
                chunk_size=4000,
                chunk_overlap=200,
                separators=[
                    "\n\n=== TABLE DATA (JSON) ===\n",
                    "\n\n=== END TABLE DATA ===\n",
                    "\n\n",
                    "\n",
                    " ",
                    "",
                ],
            )

            split_docs = text_splitter.split_documents(documents)
            print(f"📋 Created {len(split_docs)} chunks after splitting")

            # Ensure documents for vector search
            docs = ensure_documents_for_vector_search(split_docs)
            print(f"🔍 Prepared {len(docs)} documents for vector search")

            # Load embedding model
            embeddings = load_embeddings_model(self.embedding_model)

            # Create retriever using SmartRetrieverFactory (same as in chatbot.py)
            retriever_factory = SmartRetrieverFactory()
            retriever = retriever_factory.create_academic_paper_retriever_from_docs(
                documents=docs, embeddings=embeddings, llm=self.llm
            )

            # Retrieve documents
            retrieved_docs = retriever.get_relevant_documents(question)

            print(f"📄 Retrieved {len(retrieved_docs)} documents")

            # Analyze retrieved documents
            results = []
            for i, doc in enumerate(retrieved_docs):
                metadata = doc.metadata
                content_preview = (
                    doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content
                )

                # Extract table title if present
                table_title = "No table"
                if "=== TABLE DATA (JSON) ===" in doc.page_content:
                    try:
                        table_start = doc.page_content.find("{")
                        table_end = doc.page_content.rfind("}")
                        if table_start != -1 and table_end != -1:
                            table_json = doc.page_content[table_start : table_end + 1]
                            table_data = json.loads(table_json)
                            table_title = table_data.get("title", "Unknown table")
                    except:
                        table_title = "Table parse error"

                doc_info = {
                    "index": i,
                    "page": metadata.get("page", "Unknown"),
                    "source": metadata.get("source", "Unknown"),
                    "content_preview": content_preview,
                    "table_title": table_title,
                    "has_table": "=== TABLE DATA (JSON) ===" in doc.page_content,
                    "metadata": metadata,
                }
                results.append(doc_info)

                print(
                    f"  📄 Doc {i}: Page {doc_info['page']} - {doc_info['table_title']}"
                )
                print(f"      Content: {content_preview}")

            return {
                "success": True,
                "question": question,
                "file_path": pdf_path,
                "retriever_type": "academic_paper_retriever",
                "total_documents": len(documents),
                "total_chunks": len(split_docs),
                "search_ready_docs": len(docs),
                "retrieved_count": len(retrieved_docs),
                "documents": results,
            }

        except Exception as e:
            print(f"❌ Direct upload retrieval failed: {e}")
            traceback.print_exc()
            return {"error": str(e)}

    def compare_results(self, kb_results: Dict, direct_results: Dict):
        """Compare and analyze the differences between KB and direct upload results"""
        print(f"\n🔬 COMPARISON ANALYSIS")
        print("=" * 80)

        if "error" in kb_results:
            print(f"❌ KB Error: {kb_results['error']}")
        if "error" in direct_results:
            print(f"❌ Direct Upload Error: {direct_results['error']}")

        if "error" in kb_results or "error" in direct_results:
            return

        # Basic counts
        kb_count = kb_results.get("document_count", 0)
        direct_count = direct_results.get("retrieved_count", 0)

        print(f"📊 Document Count Comparison:")
        print(f"   KB Retrieved: {kb_count}")
        print(f"   Direct Retrieved: {direct_count}")

        if kb_count != direct_count:
            print(f"⚠️  Document count mismatch!")

        # Compare table titles retrieved
        print(f"\n📋 Table Analysis:")

        kb_tables = [doc for doc in kb_results.get("documents", []) if doc["has_table"]]
        direct_tables = [
            doc for doc in direct_results.get("documents", []) if doc["has_table"]
        ]

        print(f"   KB Tables: {len(kb_tables)}")
        for doc in kb_tables:
            print(f"     - Page {doc['page']}: {doc['table_title']}")

        print(f"   Direct Tables: {len(direct_tables)}")
        for doc in direct_tables:
            print(f"     - Page {doc['page']}: {doc['table_title']}")

        # Identify unique tables
        kb_table_titles = {doc["table_title"] for doc in kb_tables}
        direct_table_titles = {doc["table_title"] for doc in direct_tables}

        only_kb = kb_table_titles - direct_table_titles
        only_direct = direct_table_titles - kb_table_titles
        common = kb_table_titles & direct_table_titles

        print(f"\n🎯 Table Title Comparison:")
        print(f"   Common tables: {common}")
        print(f"   Only in KB: {only_kb}")
        print(f"   Only in Direct: {only_direct}")

        if only_kb or only_direct:
            print(f"🚨 DISCREPANCY FOUND!")
            if only_kb:
                print(f"   KB has extra tables: {only_kb}")
            if only_direct:
                print(f"   Direct has extra tables: {only_direct}")
        else:
            print(f"✅ Both systems retrieve same table types")

        # Page analysis
        print(f"\n📄 Page Analysis:")
        kb_pages = {doc["page"] for doc in kb_results.get("documents", [])}
        direct_pages = {doc["page"] for doc in direct_results.get("documents", [])}

        print(f"   KB Pages: {sorted(kb_pages)}")
        print(f"   Direct Pages: {sorted(direct_pages)}")

        if kb_pages != direct_pages:
            print(f"⚠️  Page set mismatch!")
            print(f"     Only in KB: {sorted(kb_pages - direct_pages)}")
            print(f"     Only in Direct: {sorted(direct_pages - kb_pages)}")

    async def find_knowledge_bases(self):
        """Find available knowledge bases"""
        print(f"\n🗃️  Available Knowledge Bases:")

        try:
            kbs = self.session.exec(select(KnowledgeBase)).all()

            if not kbs:
                print("❌ No knowledge bases found")
                return []

            for kb in kbs:
                print(f"   📚 {kb.title} (ID: {kb.id})")
                print(f"      Sources: {kb.number_of_sources}, Pages: {kb.total_pages}")

            return kbs

        except Exception as e:
            print(f"❌ Failed to list knowledge bases: {e}")
            return []

    async def run_comparison(self, kb_id: str = None, pdf_path: str = None):
        """Run the full comparison analysis"""
        print("🚀 KNOWLEDGE BASE vs DIRECT UPLOAD RETRIEVAL COMPARISON")
        print("=" * 80)

        if not await self.setup():
            print("❌ Setup failed")
            return

        try:
            # Find available KBs if none specified
            if not kb_id:
                kbs = await self.find_knowledge_bases()
                if kbs:
                    # Use the first available KB
                    kb_id = str(kbs[0].id)
                    print(f"🎯 Using KB: {kbs[0].title} ({kb_id})")
                else:
                    print("❌ No knowledge bases available")
                    return

            # Check if PDF exists
            if not pdf_path:
                pdf_path = TEST_PDF_PATH

            if not os.path.exists(pdf_path):
                print(f"❌ PDF not found: {pdf_path}")
                print(
                    "💡 Please update TEST_PDF_PATH in the script or provide a valid path"
                )
                return

            # Run both retrieval simulations
            print(f"\n🎯 Testing Question: '{self.TEST_QUESTION}'")

            kb_results = await self.simulate_kb_retrieval(kb_id, self.TEST_QUESTION)
            direct_results = await self.simulate_direct_upload_retrieval(
                pdf_path, self.TEST_QUESTION
            )

            # Compare results
            self.compare_results(kb_results, direct_results)

            # Save results to file
            results = {
                "question": self.TEST_QUESTION,
                "kb_results": kb_results,
                "direct_results": direct_results,
                "timestamp": str(asyncio.get_event_loop().time()),
            }

            output_file = "retrieval_comparison_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            print(f"\n💾 Results saved to: {output_file}")

        finally:
            self.cleanup()


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Debug Knowledge Base vs Direct Upload retrieval"
    )
    parser.add_argument("--kb-id", help="Knowledge Base ID to test")
    parser.add_argument("--pdf-path", help="Path to PDF file for direct upload test")
    parser.add_argument("--question", help="Question to test", default=TEST_QUESTION)

    args = parser.parse_args()

    # Use the question from args (no need for global modification)
    test_question = args.question if args.question else TEST_QUESTION

    debugger = RetrievalDebugger()
    debugger.TEST_QUESTION = test_question  # Set the question for the debugger
    await debugger.run_comparison(args.kb_id, args.pdf_path)


if __name__ == "__main__":
    asyncio.run(main())
