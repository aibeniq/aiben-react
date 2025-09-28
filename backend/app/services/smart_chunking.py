"""
Enhanced text splitting utilities that understand document structure.
Provides better chunking for academic papers, reports, and structured documents.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.content_filtering import content_filter

logger = logging.getLogger(__name__)


class TablePreservingTextSplitter:
    """
    Text splitter that preserves structured table data markers and prevents
    splitting within table JSON structures.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Base splitter for regular content
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def _extract_table_blocks(self, text: str):
        """
        Extract table blocks and their positions from text.

        Returns:
            List of dicts with 'start', 'end', 'content', and 'type' keys
        """
        blocks = []

        # Patterns for different table markers
        table_patterns = [
            # New JSON format (primary)
            (r"=== TABLE DATA \(JSON\) ===.*?=== END TABLE DATA ===", "json"),
            # Legacy formats (for backward compatibility)
            (
                r"=== STRUCTURED TABLE DATA ===.*?=== END STRUCTURED TABLE DATA ===",
                "structured",
            ),
            (
                r"=== STRUCTURED TABLE DATA \(FALLBACK\) ===.*?=== END STRUCTURED TABLE DATA ===",
                "fallback",
            ),
            (r"=== RAW TABLE CONTENT ===.*?=== END RAW TABLE CONTENT ===", "raw"),
            (r"=== SEARCHABLE SUMMARY ===.*?=== END SEARCHABLE SUMMARY ===", "summary"),
            (r"<TABLE_START>.*?<TABLE_END>", "test"),  # For testing
        ]

        for pattern, table_type in table_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                blocks.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "content": match.group(0),
                        "type": table_type,
                    }
                )

        # Sort by start position
        blocks.sort(key=lambda x: x["start"])
        return blocks

    def _create_table_aware_chunks(self, text: str):
        """
        Create chunks that preserve table structure.
        """
        table_blocks = self._extract_table_blocks(text)
        chunks = []
        last_end = 0

        for block in table_blocks:
            # Process text before this table block
            if block["start"] > last_end:
                pre_table_text = text[last_end : block["start"]].strip()
                if pre_table_text:
                    # Use base splitter for regular content
                    pre_chunks = self.base_splitter.split_text(pre_table_text)
                    chunks.extend(pre_chunks)

            # Handle the table block as a single unit - NEVER split JSON tables
            table_content = block["content"]
            table_type = block["type"]

            # JSON tables must ALWAYS remain atomic (never split or merged)
            if table_type == "json":
                logger.info(
                    f"📊 Preserving JSON table as atomic chunk ({len(table_content)} chars)"
                )
                chunks.append(table_content)
            elif len(table_content) > self.chunk_size * 2:
                logger.warning(
                    f"Large {table_type} table block ({len(table_content)} chars) may need special handling"
                )
                # For very large non-JSON tables, keep as single chunk to preserve structure
                chunks.append(table_content)
            else:
                # For non-JSON tables, we can try combining with previous chunk
                if chunks and len(chunks[-1]) + len(table_content) < self.chunk_size:
                    chunks[-1] += "\n\n" + table_content
                else:
                    chunks.append(table_content)

            last_end = block["end"]

        # Process remaining text after last table block
        if last_end < len(text):
            remaining_text = text[last_end:].strip()
            if remaining_text:
                remaining_chunks = self.base_splitter.split_text(remaining_text)
                chunks.extend(remaining_chunks)

        # If no table blocks found, use base splitter
        if not table_blocks:
            chunks = self.base_splitter.split_text(text)

        return chunks

    def split_text(self, text: str):
        """
        Split text while preserving table structure.
        """
        return self._create_table_aware_chunks(text)

    def split_documents(self, documents):
        """
        Split documents while preserving table structure.
        """
        result_documents = []

        for doc in documents:
            # Check if document has table data
            has_table_markers = any(
                marker in doc.page_content
                for marker in [
                    "=== TABLE DATA (JSON) ===",  # New JSON format
                    "=== STRUCTURED TABLE DATA ===",  # Legacy formats
                    "=== RAW TABLE CONTENT ===",
                    "=== SEARCHABLE SUMMARY ===",
                ]
            )

            if has_table_markers:
                logger.info(
                    f"📊 Processing document with table markers using table-aware splitting"
                )
                chunks = self._create_table_aware_chunks(doc.page_content)
            else:
                # Use regular splitting for non-table documents
                logger.info(
                    f"📋 Processing regular document: length={len(doc.page_content)}, has_tables=False"
                )
                chunks = self.base_splitter.split_text(doc.page_content)

            logger.info(f"📄 Document produced {len(chunks)} raw chunks")

            # Create new documents from chunks
            for i, chunk in enumerate(chunks):
                # Use very permissive minimum size threshold - just 10 characters to avoid empty content
                min_threshold = 10
                chunk_length = len(chunk.strip())
                logger.info(
                    f"🔍 Chunk {i}: {chunk_length} chars (min: {min_threshold}) - {'PASS' if chunk_length >= min_threshold else 'FAIL'}"
                )
                if chunk_length >= min_threshold:
                    chunk_doc = Document(
                        page_content=chunk,
                        metadata={
                            **doc.metadata,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "has_table_content": has_table_markers
                            and any(
                                marker in chunk
                                for marker in [
                                    "=== TABLE DATA (JSON) ===",  # New JSON format
                                    "=== STRUCTURED TABLE DATA ===",
                                    "=== RAW TABLE CONTENT ===",
                                ]
                            ),
                        },
                    )
                    result_documents.append(chunk_doc)

        # If no chunks were created (due to size filtering), create at least one chunk per document
        if len(result_documents) == 0 and len(documents) > 0:
            logger.warning(
                f"⚠️ No chunks met minimum size threshold, creating fallback chunks"
            )
            for doc in documents:
                if len(doc.page_content.strip()) > 0:
                    fallback_chunk = Document(
                        page_content=doc.page_content,
                        metadata={
                            **doc.metadata,
                            "chunk_index": 0,
                            "total_chunks": 1,
                            "has_table_content": False,
                            "fallback_chunk": True,  # Mark as fallback
                        },
                    )
                    result_documents.append(fallback_chunk)

        logger.info(
            f"📋 Split {len(documents)} documents into {len(result_documents)} table-aware chunks"
        )
        return result_documents


class StructureAwareTextSplitter:
    """
    Text splitter that understands document structure and creates better chunks
    for academic papers and structured documents.
    """

    # Section headers that indicate major document divisions
    MAJOR_SECTION_PATTERNS = [
        r"^\s*(?:abstract|introduction|background|literature\s+review)\s*$",
        r"^\s*(?:method|methodology|methods)\s*$",
        r"^\s*(?:results?|findings?)\s*$",
        r"^\s*(?:discussion|analysis)\s*$",
        r"^\s*(?:conclusion|summary)\s*$",
        r"^\s*(?:references?|bibliography|works?\s+cited)\s*$",
        r"^\s*(?:appendix|appendices)\s*$",
        r"^\s*\d+\.?\s+[A-Z][a-z]*.*$",  # Numbered sections like "1. Introduction"
    ]

    # Bibliography section identifiers
    BIBLIOGRAPHY_SECTION_PATTERNS = [
        r"^\s*(?:references?|bibliography|works?\s+cited|literature\s+cited)\s*$",
        r"^\s*(?:citation|bibliography)\s*$",
    ]

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        max_bibliography_chunks: int = 2,  # Limit bibliography chunks
        prioritize_main_content: bool = True,
    ):
        """
        Initialize the structure-aware text splitter.

        Args:
            chunk_size: Target size for text chunks
            chunk_overlap: Overlap between consecutive chunks
            min_chunk_size: Minimum size for a chunk to be included
            max_bibliography_chunks: Maximum number of bibliography chunks to include
            prioritize_main_content: Whether to prioritize main content over bibliography
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_bibliography_chunks = max_bibliography_chunks
        self.prioritize_main_content = prioritize_main_content

        # Compile regex patterns
        self.major_section_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.MAJOR_SECTION_PATTERNS
        ]
        self.bibliography_section_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.BIBLIOGRAPHY_SECTION_PATTERNS
        ]

        # Initialize base text splitter
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def identify_document_sections(self, text: str) -> Dict[str, Any]:
        """
        Identify major sections within a document.

        Args:
            text: Full document text

        Returns:
            Dictionary containing section information
        """
        sections = {
            "main_content_start": 0,
            "bibliography_start": None,
            "bibliography_end": None,
            "sections": [],
        }

        lines = text.split("\n")
        current_position = 0

        for i, line in enumerate(lines):
            # Check for bibliography section start
            if not sections["bibliography_start"]:
                for regex in self.bibliography_section_regex:
                    if regex.match(line.strip()):
                        sections["bibliography_start"] = current_position
                        logger.debug(
                            f"Found bibliography section at position {current_position}"
                        )
                        break

            # Update position
            current_position += len(line) + 1  # +1 for the newline

        # If we found a bibliography section, everything after it is bibliography
        if sections["bibliography_start"]:
            sections["bibliography_end"] = len(text)

        return sections

    def split_with_structure_awareness(
        self, text: str, metadata: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Split text while being aware of document structure.

        Args:
            text: Text to split
            metadata: Metadata to attach to chunks

        Returns:
            List of Document chunks with enhanced metadata
        """
        if not text or not text.strip():
            return []

        if metadata is None:
            metadata = {}

        # Identify document sections
        section_info = self.identify_document_sections(text)

        # Split main content and bibliography separately
        main_content_chunks = []
        bibliography_chunks = []

        # Extract main content (everything before bibliography)
        if section_info["bibliography_start"]:
            main_content = text[: section_info["bibliography_start"]].strip()
            bibliography_content = text[section_info["bibliography_start"] :].strip()
        else:
            main_content = text
            bibliography_content = ""

        # Process main content
        if main_content:
            main_chunks = self.base_splitter.split_text(main_content)
            for i, chunk_text in enumerate(main_chunks):
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update(
                        {
                            "chunk_type": "main_content",
                            "chunk_index": i,
                            "is_bibliography": False,
                        }
                    )

                    doc = Document(page_content=chunk_text, metadata=chunk_metadata)
                    main_content_chunks.append(doc)

        # Process bibliography content (limited)
        if bibliography_content and not self.prioritize_main_content:
            bib_chunks = self.base_splitter.split_text(bibliography_content)
            for i, chunk_text in enumerate(bib_chunks[: self.max_bibliography_chunks]):
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update(
                        {
                            "chunk_type": "bibliography",
                            "chunk_index": i,
                            "is_bibliography": True,
                        }
                    )

                    doc = Document(page_content=chunk_text, metadata=chunk_metadata)
                    bibliography_chunks.append(doc)

        # Combine chunks (main content first, then limited bibliography)
        all_chunks = main_content_chunks + bibliography_chunks

        # Enhance with content filtering metadata
        enhanced_chunks = content_filter.enhance_document_metadata(all_chunks)

        logger.info(
            f"Split document into {len(main_content_chunks)} main content chunks and {len(bibliography_chunks)} bibliography chunks"
        )

        return enhanced_chunks

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of documents using structure awareness.

        Args:
            documents: List of Document objects to split

        Returns:
            List of chunked Document objects
        """
        all_chunks = []

        for doc in documents:
            chunks = self.split_with_structure_awareness(doc.page_content, doc.metadata)
            all_chunks.extend(chunks)

        return all_chunks


class SmartDocumentProcessor:
    """
    Enhanced document processor that combines structure-aware splitting with content filtering.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        filter_bibliography: bool = True,
        max_bibliography_chunks: int = 2,
        min_quality_score: float = 0.3,
    ):
        """
        Initialize the smart document processor.

        Args:
            chunk_size: Target size for text chunks
            chunk_overlap: Overlap between consecutive chunks
            filter_bibliography: Whether to filter out bibliography content
            max_bibliography_chunks: Maximum bibliography chunks to include
            min_quality_score: Minimum quality score for chunks
        """
        self.filter_bibliography = filter_bibliography
        self.min_quality_score = min_quality_score

        self.splitter = StructureAwareTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_bibliography_chunks=max_bibliography_chunks,
            prioritize_main_content=filter_bibliography,
        )

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents with smart chunking and filtering.

        Args:
            documents: List of Document objects to process

        Returns:
            List of high-quality processed chunks
        """
        # Split documents with structure awareness
        chunks = self.splitter.split_documents(documents)

        if not chunks:
            return []

        # Filter and score chunks
        scored_chunks = content_filter.filter_and_score_documents(chunks)

        # Apply quality threshold and return documents only
        quality_chunks = [
            doc for doc, score in scored_chunks if score >= self.min_quality_score
        ]

        # If we have too few chunks after filtering, relax the criteria slightly
        if len(quality_chunks) < 3 and len(scored_chunks) > 0:
            logger.warning(
                f"Only {len(quality_chunks)} high-quality chunks found, including medium-quality chunks"
            )
            relaxed_threshold = self.min_quality_score * 0.7
            quality_chunks = [
                doc for doc, score in scored_chunks if score >= relaxed_threshold
            ][
                :10
            ]  # Limit to top 10

        logger.info(
            f"Smart processing: {len(documents)} documents -> {len(chunks)} chunks -> {len(quality_chunks)} quality chunks"
        )

        return quality_chunks


# Factory function for easy integration
def create_smart_text_splitter(
    chunk_size: int = 1000, chunk_overlap: int = 200, filter_bibliography: bool = True
) -> SmartDocumentProcessor:
    """
    Create a smart document processor with sensible defaults.

    Args:
        chunk_size: Target size for text chunks
        chunk_overlap: Overlap between consecutive chunks
        filter_bibliography: Whether to filter bibliography content

    Returns:
        Configured SmartDocumentProcessor instance
    """
    return SmartDocumentProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        filter_bibliography=filter_bibliography,
        max_bibliography_chunks=2 if not filter_bibliography else 0,
        min_quality_score=0.3,
    )
