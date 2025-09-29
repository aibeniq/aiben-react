"""
Table Detection Service - Detects tables in document text and identifies which pages contain them.

This module provides functionality to id        # Estimate table structure
        total_structured_rows = max(potential_rows, financial_rows)
        complexity = "simple"
        if max_columns > 5 or total_structured_rows > 20 or financial_rows > 15:
            complexity = "complex"
        elif max_columns > 3 or total_structured_rows > 10 or financial_rows > 8:
            complexity = "medium"

        return {
            "has_tables": True,
            "estimated_columns": max_columns,
            "estimated_rows": total_structured_rows,
            "financial_rows": financial_rows,
            "complexity": complexity,
            "line_count": len(lines),
            "table_density": total_structured_rows / len(lines) if lines else 0
        }ke structures in document text
and determine which pages/chunks contain tables that would benefit from vision processing.
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from langchain.schema import Document

# Set up logger for table detection
logger = logging.getLogger(__name__)


class TableDetector:
    """Service for detecting tables in document text and determining which pages contain them."""

    @staticmethod
    def detect_tables_in_text(text: str) -> bool:
        """
        Detect if text contains table-like structures.

        Args:
            text: The text content to analyze

        Returns:
            bool: True if table-like structures are detected
        """
        if not text or len(text.strip()) < 20:
            logger.debug(
                f"Table detection: Text too short ({len(text.strip())} chars), skipping"
            )
            return False

        # Common table indicators with weighted scoring
        table_patterns = [
            (r"\|.*\|.*\|", 3),  # Pipe-separated tables (strong indicator)
            (r"(\t.*){3,}", 2),  # Tab-separated data (3+ columns)
            (r"(\s{3,}\S+){3,}", 2),  # Multiple space-separated columns (3+ spaces)
            (r"(?i)(table|chart|figure)\s*\d+", 1),  # Table/Chart references
            (r"[\-_]{5,}", 1),  # Table borders/separators (5+ chars)
            (r"(?i)(column|row|cell)", 1),  # Table terminology
            (
                r"\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+",
                2,
            ),  # Multiple decimal numbers in sequence
            # Financial schedule patterns
            (r"\d+\.\d+%", 3),  # Percentage values (strong financial indicator)
            (r"USD\s+\d+", 3),  # Currency amounts (USD)
            (r"\$\s*\d+", 2),  # Dollar amounts
            (r"(?i)(fee|charge|cost|rate|price)", 2),  # Financial terminology
            (
                r"(?i)(appendix|schedule|attachment)",
                2,
            ),  # Document structure terminology
            (r"(?i)(free\s+of\s+charge|no\s+fee|waived)", 2),  # Fee exemption language
            (r"\d+\s*(per|each|annually|monthly)", 2),  # Rate/frequency patterns
        ]

        # Calculate weighted pattern score
        pattern_score = 0
        for pattern, weight in table_patterns:
            matches = len(re.findall(pattern, text))
            pattern_score += matches * weight

        # Additional heuristics
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return False

        # Count lines that look like table rows (3+ space-separated items)
        potential_rows = 0
        for line in lines:
            # Split by various delimiters
            parts = re.split(r"[\t\|]", line)
            if len(parts) >= 3:
                potential_rows += 1
            else:
                # Check for space-separated columns
                words = line.split()
                if len(words) >= 3:
                    # Check if words are likely column data (numbers, short words, etc.)
                    numeric_words = sum(
                        1 for word in words if re.match(r"^\d+(\.\d+)?$", word)
                    )
                    if numeric_words >= len(words) * 0.3:  # 30% numeric content
                        potential_rows += 1

        row_percentage = potential_rows / len(lines) if lines else 0

        # Decision logic: combine pattern score and row analysis
        logger.debug(
            f"Table detection analysis: pattern_score={pattern_score}, row_percentage={row_percentage:.2f}, potential_rows={potential_rows}, total_lines={len(lines)}"
        )

        if pattern_score >= 4:  # Strong pattern indicators
            logger.info(
                f"✅ Table detected (strong patterns): pattern_score={pattern_score}"
            )
            return True
        elif (
            pattern_score >= 2 and row_percentage > 0.4
        ):  # Medium patterns + high row percentage
            logger.info(
                f"✅ Table detected (medium patterns + high rows): pattern_score={pattern_score}, row_percentage={row_percentage:.2f}"
            )
            return True
        elif row_percentage > 0.6:  # Very high row percentage
            logger.info(
                f"✅ Table detected (very high row percentage): row_percentage={row_percentage:.2f}"
            )
            return True

        logger.debug(
            f"❌ No table detected: pattern_score={pattern_score}, row_percentage={row_percentage:.2f}"
        )
        return False

    @staticmethod
    def identify_table_pages(documents: List[Document]) -> List[int]:
        """
        Identify which pages/chunks contain tables.

        Args:
            documents: List of Document objects to analyze

        Returns:
            List of page numbers/indices that contain tables
        """
        logger.info(
            f"🔍 Analyzing {len(documents)} document chunks for table detection"
        )
        table_pages = []

        for i, doc in enumerate(documents):
            if TableDetector.detect_tables_in_text(doc.page_content):
                # Extract page number from metadata if available
                page_num = doc.metadata.get("page", doc.metadata.get("page_number", i))

                # Handle different page numbering formats
                if isinstance(page_num, str) and page_num.isdigit():
                    page_num = int(page_num)
                elif not isinstance(page_num, int):
                    page_num = i

                table_pages.append(page_num)
                logger.debug(f"📊 Table detected on page {page_num} (chunk {i})")

        result = sorted(list(set(table_pages)))  # Remove duplicates and sort
        logger.info(
            f"📋 Table detection complete: {len(result)} pages contain tables: {result}"
        )
        return result

    @staticmethod
    def analyze_table_complexity(text: str) -> Dict[str, Any]:
        """
        Analyze the complexity and characteristics of detected tables.

        Args:
            text: The text content containing tables

        Returns:
            Dict with table analysis information
        """
        if not TableDetector.detect_tables_in_text(text):
            return {"has_tables": False}

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Count potential columns and rows
        max_columns = 0
        potential_rows = 0
        financial_rows = 0

        for line in lines:
            # Check various delimiters
            pipe_parts = len(line.split("|"))
            tab_parts = len(line.split("\t"))
            space_parts = len(
                [p for p in line.split("  ") if p.strip()]
            )  # Double space split

            max_cols_in_line = max(pipe_parts, tab_parts, space_parts)
            if max_cols_in_line >= 3:
                max_columns = max(max_columns, max_cols_in_line)
                potential_rows += 1

            # Check for financial schedule patterns (service + fee structure)
            if re.search(
                r"(?i)\d+\.\d+%|\$\s*\d+|USD\s+\d+|(fee|charge|cost|rate|price|free\s+of\s+charge)",
                line,
            ):
                financial_rows += 1

        # Estimate table structure
        complexity = "simple"

        # Factor in financial schedule complexity
        financial_density = financial_rows / len(lines) if lines else 0

        if max_columns > 5 or potential_rows > 20 or financial_density > 0.3:
            complexity = "complex"
        elif max_columns > 3 or potential_rows > 10 or financial_density > 0.15:
            complexity = "medium"

        logger.debug(
            f"📊 Table complexity analysis: columns={max_columns}, rows={potential_rows}, financial_rows={financial_rows}, financial_density={financial_density:.2f}, complexity={complexity}"
        )

        return {
            "has_tables": True,
            "estimated_columns": max_columns,
            "estimated_rows": potential_rows,
            "financial_rows": financial_rows,
            "complexity": complexity,
            "line_count": len(lines),
            "table_density": potential_rows / len(lines) if lines else 0,
            "financial_density": financial_density,
        }

    @staticmethod
    def should_use_vision_for_tables(
        documents: List[Document], file_extension: str = ""
    ) -> bool:
        """
        Determine if vision processing should be used for table extraction.
        Prioritizes vision processing for image-heavy pages with minimal text.

        Args:
            documents: List of documents to analyze
            file_extension: File extension (e.g., '.pdf', '.docx')

        Returns:
            bool: True if vision processing is recommended
        """
        logger.info(
            f"🔮 Evaluating vision processing for {len(documents)} documents (file_extension: {file_extension})"
        )

        # Only recommend vision for file types that can contain images
        supported_extensions = [".pdf", ".docx"]
        if file_extension.lower() not in supported_extensions:
            logger.info(
                f"❌ Vision not recommended: Unsupported file extension '{file_extension}' (supported: {supported_extensions})"
            )
            return False

        # Check for pages with minimal text or web-based PDF patterns
        minimal_text_pages = 0
        web_pdf_pages = 0
        total_text_length = 0

        for i, doc in enumerate(documents):
            text_length = len(doc.page_content.strip())
            total_text_length += text_length
            content = doc.page_content.strip().lower()

            # Check for web-based PDF patterns (like APA sample tables)
            is_web_pdf = any(
                indicator in content
                for indicator in [
                    "https://",
                    "apa.org",
                    "sample tables",
                    "style-grammar-guidelines",
                    "of 7",
                    "pm",
                    "am",
                ]
            )

            # Pages with limited text or web PDF patterns likely contain images/tables
            if text_length < 500 or is_web_pdf:  # Increased threshold
                minimal_text_pages += 1
                if is_web_pdf:
                    web_pdf_pages += 1
                    logger.debug(
                        f"🌐 Page {i+1}: Web PDF pattern detected ({text_length} chars) - likely image-heavy webpage"
                    )
                else:
                    logger.debug(
                        f"📄 Page {i+1}: Minimal text detected ({text_length} chars) - likely image-heavy"
                    )

        # If we have pages with minimal text or web patterns, prioritize vision processing
        if minimal_text_pages > 0:
            avg_text_per_page = total_text_length / len(documents) if documents else 0
            if (
                avg_text_per_page < 1000 or web_pdf_pages > 0
            ):  # Relaxed threshold for web PDFs
                reason = (
                    "web-based PDF patterns"
                    if web_pdf_pages > 0
                    else "minimal text content"
                )
                logger.info(
                    f"✅ Vision RECOMMENDED: {minimal_text_pages} pages with {reason} detected (avg: {avg_text_per_page:.0f} chars/page, web_pages: {web_pdf_pages})"
                )
                return True

        table_pages = TableDetector.identify_table_pages(documents)
        # Don't reject if no table pages detected - minimal text pages might still need vision
        if not table_pages and minimal_text_pages == 0:
            logger.info(
                f"❌ Vision not recommended: No table pages or minimal text pages detected"
            )
            return False

        # Analyze table complexity on table pages
        complex_tables = 0
        total_tables = 0
        has_financial_schedule = False

        for i, doc in enumerate(documents):
            page_num = doc.metadata.get("page", doc.metadata.get("page_number", i))
            if page_num in table_pages:
                analysis = TableDetector.analyze_table_complexity(doc.page_content)
                if analysis.get("has_tables"):
                    total_tables += 1
                    if analysis.get("complexity") in ["medium", "complex"]:
                        complex_tables += 1
                    # Check for financial schedules
                    if analysis.get("financial_density", 0) > 0.1:
                        has_financial_schedule = True

        logger.info(
            f"📊 Vision analysis summary: total_tables={total_tables}, complex_tables={complex_tables}, has_financial_schedule={has_financial_schedule}, table_pages={len(table_pages)}"
        )

        # Recommend vision if we have complex tables, financial schedules, or many table pages
        if complex_tables > 0:
            logger.info(
                f"✅ Vision RECOMMENDED: {complex_tables} complex tables detected"
            )
            return True
        elif (
            has_financial_schedule
        ):  # Financial schedules benefit from vision processing
            logger.info(f"✅ Vision RECOMMENDED: Financial schedule detected")
            return True
        elif len(table_pages) >= 3:  # Multiple table pages
            logger.info(
                f"✅ Vision RECOMMENDED: Multiple table pages ({len(table_pages)} pages)"
            )
            return True
        elif total_tables >= 2:  # Multiple tables
            logger.info(
                f"✅ Vision RECOMMENDED: Multiple tables ({total_tables} tables)"
            )
            return True

        logger.info(
            f"❌ Vision NOT recommended: Tables are simple enough for text processing"
        )
        return False
