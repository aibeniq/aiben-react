"""
Content filtering utilities for RAG to improve retrieval quality.
Filters out bibliography, references, and other non-main content from retrieval results.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ContentFilter:
    """
    Filter and score document content to improve RAG retrieval quality.
    Identifies and de-prioritizes bibliography, references, and low-quality content.
    """

    # Patterns that indicate bibliography/reference sections
    BIBLIOGRAPHY_PATTERNS = [
        r"\b(?:references?|bibliography|works? cited|literature cited)\b",
        r"\b(?:citation|cite|cited)\b",
        r"[A-Z][a-z]+,?\s+[A-Z]\.?(?:\s+[A-Z]\.?)*\s*\([12]\d{3}\)",  # Author, A. (2023) - more flexible
        r"[A-Z][a-z]+,?\s+[A-Z]\.?.*?&.*?[A-Z][a-z]+,?\s+[A-Z]\.?.*?\([12]\d{3}\)",  # Author, A. & Author, B. (2023)
        r"^\s*\[[0-9]+\]\s+",  # [1] Citation format
        r"doi:\s*10\.\d+",  # DOI patterns
        r"https?://(?:dx\.)?doi\.org/",  # DOI URLs
        r"PubMed ID:|PMID:\s*\d+",  # PubMed identifiers - improved
        r"ISBN:?\s*[\d-]+",  # ISBN numbers - improved
        r"pp?\.\s*\d+[-–]\d+",  # Page ranges (common in citations)
        r"vol\.\s*\d+",  # Volume numbers
        r"no\.\s*\d+",  # Issue numbers
        r"et\s+al\.",  # Et al. indicator (common in citations)
        r"Journal\s+of\s+\w+",  # Journal names
        r"Proceedings\s+of\s+the",  # Conference proceedings
    ]

    # Patterns that indicate low-quality or non-content sections
    LOW_QUALITY_PATTERNS = [
        r"^\s*page\s+\d+\s*$",  # Page numbers
        r"^\s*\d+\s*$",  # Standalone numbers
        r"^\s*figure\s+\d+",  # Figure captions
        r"^\s*table\s+\d+",  # Table captions
        r"^\s*appendix\s+[a-z]?\s*$",  # Appendix headers
        r"^\s*\w{1,3}\s*$",  # Very short fragments
        r"^\s*copyright\s+",  # Copyright notices
        r"^\s*all rights reserved",  # Rights statements
        r"^\s*\(c\)\s*\d{4}",  # Copyright symbols
    ]

    # Patterns that indicate main content
    MAIN_CONTENT_INDICATORS = [
        r"\b(?:background|introduction|method|methodology|results?|discussion|conclusion|abstract|summary)\b",
        r"\b(?:objective|aim|purpose|goal)\b",
        r"\b(?:study|research|analysis|investigation|examination)\b",
        r"\b(?:finding|evidence|data|observation)\b",
        r"\b(?:treatment|therapy|intervention|approach)\b",
        r"\b(?:patient|participant|subject|individual)\b",
        r"\b(?:significant|important|critical|key|major)\b",
        r"\b(?:however|therefore|thus|consequently|furthermore|moreover)\b",  # Discourse markers
    ]

    def __init__(self):
        # Compile regex patterns for efficiency
        self.bibliography_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.BIBLIOGRAPHY_PATTERNS
        ]
        self.low_quality_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.LOW_QUALITY_PATTERNS
        ]
        self.main_content_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.MAIN_CONTENT_INDICATORS
        ]

    def is_bibliography_content(self, text: str) -> bool:
        """
        Check if text appears to be from a bibliography or references section.

        Args:
            text: Text to analyze

        Returns:
            True if text appears to be bibliography content
        """
        if not text or len(text.strip()) < 10:
            return False

        # Check for bibliography patterns
        bibliography_matches = sum(
            1 for regex in self.bibliography_regex if regex.search(text)
        )

        # If multiple bibliography indicators, likely a reference
        if bibliography_matches >= 2:
            return True

        # Check for single strong indicators
        text_lines = text.strip().split("\n")
        for line in text_lines[:3]:  # Check first few lines
            # Strong patterns that almost certainly indicate citations
            if re.search(r"[A-Z][a-z]+,?\s+[A-Z]\..*\([12]\d{3}\)", line):
                return True
            if re.search(r"et\s+al\..*\([12]\d{3}\)", line, re.IGNORECASE):
                return True
            if re.search(
                r"doi:\s*10\.\d+|https?://(?:dx\.)?doi\.org/", line, re.IGNORECASE
            ):
                return True
            if re.search(r"PMID:\s*\d+", line, re.IGNORECASE):
                return True
            # Check for journal-style formatting
            if re.search(r"Journal\s+of\s+\w+.*\d+\(\d+\)", line, re.IGNORECASE):
                return True

        return False

    def is_low_quality_content(self, text: str) -> bool:
        """
        Check if text is low-quality content (headers, page numbers, etc.).

        Args:
            text: Text to analyze

        Returns:
            True if text is low-quality content
        """
        if not text or len(text.strip()) < 5:
            return True

        # Check for low-quality patterns
        for regex in self.low_quality_regex:
            if regex.search(text):
                return True

        # Check if text is too short and repetitive
        words = text.split()
        if len(words) < 5:
            return True

        # Check if text has very low information density
        unique_words = set(word.lower() for word in words if word.isalpha())
        if len(words) > 0 and len(unique_words) / len(words) < 0.3:
            return True

        return False

    def calculate_content_quality_score(self, text: str) -> float:
        """
        Calculate a quality score for text content.
        Higher scores indicate better, more substantial content.

        Args:
            text: Text to score

        Returns:
            Quality score between 0.0 and 1.0
        """
        if not text:
            return 0.0

        score = 0.5  # Base score

        # Length factor (prefer medium-length chunks)
        length = len(text)
        if 100 <= length <= 2000:
            score += 0.2
        elif 50 <= length < 100 or 2000 < length <= 4000:
            score += 0.1
        elif length < 50:
            score -= 0.3

        # Main content indicators
        main_content_matches = sum(
            1 for regex in self.main_content_regex if regex.search(text)
        )
        score += min(main_content_matches * 0.1, 0.3)

        # Bibliography penalty
        if self.is_bibliography_content(text):
            score -= 0.5

        # Low quality penalty
        if self.is_low_quality_content(text):
            score -= 0.4

        # Sentence structure bonus
        sentences = re.split(r"[.!?]+", text)
        complete_sentences = sum(1 for s in sentences if len(s.strip().split()) >= 4)
        if complete_sentences >= 2:
            score += 0.2

        # Information density bonus
        words = text.split()
        if words:
            unique_words = set(word.lower() for word in words if word.isalpha())
            if len(unique_words) / len(words) > 0.7:
                score += 0.1

        return max(0.0, min(1.0, score))

    def filter_and_score_documents(
        self, documents: List[Document]
    ) -> List[Tuple[Document, float]]:
        """
        Filter and score a list of documents for RAG quality.

        Args:
            documents: List of Document objects to filter and score

        Returns:
            List of (document, quality_score) tuples, sorted by quality (highest first)
        """
        scored_docs = []

        for doc in documents:
            # Skip obvious bibliography content
            if self.is_bibliography_content(doc.page_content):
                logger.debug(
                    f"Filtered out bibliography content: {doc.page_content[:100]}..."
                )
                continue

            # Skip low-quality content
            if self.is_low_quality_content(doc.page_content):
                logger.debug(
                    f"Filtered out low-quality content: {doc.page_content[:100]}..."
                )
                continue

            # Calculate quality score
            quality_score = self.calculate_content_quality_score(doc.page_content)

            # Only include documents with reasonable quality
            if quality_score >= 0.3:
                scored_docs.append((doc, quality_score))
            else:
                logger.debug(
                    f"Filtered out low-scoring content (score: {quality_score:.2f}): {doc.page_content[:100]}..."
                )

        # Sort by quality score (highest first)
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        logger.info(
            f"Filtered documents: {len(documents)} -> {len(scored_docs)} (removed {len(documents) - len(scored_docs)} low-quality chunks)"
        )

        return scored_docs

    def enhance_document_metadata(self, documents: List[Document]) -> List[Document]:
        """
        Enhance document metadata with content type and quality information.

        Args:
            documents: List of Document objects to enhance

        Returns:
            List of Document objects with enhanced metadata
        """
        enhanced_docs = []

        for doc in documents:
            # Create a copy to avoid modifying original
            new_doc = Document(
                page_content=doc.page_content,
                metadata=doc.metadata.copy() if doc.metadata else {},
            )

            # Add content type classification
            if self.is_bibliography_content(doc.page_content):
                new_doc.metadata["content_type"] = "bibliography"
            elif self.is_low_quality_content(doc.page_content):
                new_doc.metadata["content_type"] = "low_quality"
            else:
                new_doc.metadata["content_type"] = "main_content"

            # Add quality score
            new_doc.metadata["quality_score"] = self.calculate_content_quality_score(
                doc.page_content
            )

            enhanced_docs.append(new_doc)

        return enhanced_docs


# Global instance for easy access
content_filter = ContentFilter()
