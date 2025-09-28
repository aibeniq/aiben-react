"""
Vision Service Module - Centralized service for handling vision-enabled document processing.

This module provides reusable, modular code for vision capabilities across all app functionalities
including Chatbot, FormConnect, VeraDoc, TwinCheck, and any future features requiring image analysis.
"""

from typing import List, Dict, Optional, Tuple, Any
import base64
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """Centralized service for handling vision-enabled document processing"""

    @staticmethod
    def is_vision_enabled(llm) -> bool:
        """
        Check if the LLM supports multimodal/vision capabilities.

        Args:
            llm: The LLM instance to check

        Returns:
            bool: True if the LLM supports vision, False otherwise
        """
        if not llm:
            logger.debug("🔮 Vision check: No LLM provided")
            return False

        # Check if LLM model name is in vision-enabled models list
        model_name = getattr(llm, "model_name", "") or getattr(llm, "model", "")

        # Handle different LLM wrapper types
        if hasattr(llm, "__class__"):
            class_name = llm.__class__.__name__
            if "Replicate" in class_name:
                # For Replicate models, check the model attribute
                model_name = getattr(llm, "model", "")
            elif hasattr(llm, "_llm"):
                # For wrapped models, check the inner LLM
                inner_llm = getattr(llm, "_llm", None)
                if inner_llm:
                    model_name = getattr(inner_llm, "model_name", "") or getattr(
                        inner_llm, "model", ""
                    )

        logger.debug(
            f"🔮 Vision check: LLM model='{model_name}', class={type(llm).__name__}"
        )

        if not model_name:
            logger.debug("🔮 Vision check: No model name found")
            return False

        # Check against vision-enabled models list
        logger.debug(f"🔮 Vision enabled models: {settings.VISION_ENABLED_MODELS}")

        vision_supported = any(
            vision_model in model_name.lower()
            for vision_model in settings.VISION_ENABLED_MODELS
        )

        if vision_supported:
            logger.debug(f"🔮 Vision check: ✅ Model '{model_name}' supports vision")
        else:
            logger.debug(
                f"🔮 Vision check: ❌ Model '{model_name}' does not support vision"
            )

        return vision_supported

    @staticmethod
    def extract_images_from_files(files: List[Any]) -> List[Dict[str, Any]]:
        """
        Extract images from uploaded files with metadata.

        Args:
            files: List of uploaded file objects

        Returns:
            List of dictionaries containing image data and metadata
        """
        from app.services.document_utils import (
            extract_documents_and_images_from_file_unified,
        )

        extracted_images = []

        for file in files:
            try:
                if hasattr(file, "read"):
                    file_content = file.read()
                    filename = getattr(file, "filename", "unknown")
                    if hasattr(file, "seek"):
                        file.seek(0)  # Reset for other processing
                else:
                    file_content = file
                    filename = "unknown"

                # Extract images using unified function
                _, images = extract_documents_and_images_from_file_unified(
                    file_content, filename
                )

                for idx, image_b64 in enumerate(images):
                    extracted_images.append(
                        {
                            "image_data": image_b64,
                            "source_file": filename,
                            "image_index": idx,
                            "metadata": {
                                "file_size": len(file_content),
                                "extracted_from": filename,
                            },
                        }
                    )

            except Exception as e:
                logger.error(f"Error extracting images from {filename}: {e}")
                continue

        return extracted_images[: settings.MAX_IMAGES_PER_DOCUMENT]

    @staticmethod
    async def process_images_with_prompt(
        llm,
        images: List[Dict[str, Any]],
        prompt_template: str,
        variables: Dict[str, Any],
        context: str = "",
    ) -> str:
        """
        Process images with a given prompt template.

        Args:
            llm: The LLM instance to use
            images: List of image dictionaries with data and metadata
            prompt_template: The prompt template string
            variables: Variables to substitute in the template
            context: Additional context string

        Returns:
            str: The processed result from the vision-enabled LLM
        """
        from app.services.llms import invoke_llm_with_images

        if not VisionService.is_vision_enabled(llm):
            return "Vision analysis not available with current model"

        if not images:
            return "No images available for analysis"

        try:
            # Prepare image data for processing
            image_data_list = [img["image_data"] for img in images]

            # Add image metadata to variables
            variables.update(
                {
                    "image_count": len(images),
                    "source_files": list(set(img["source_file"] for img in images)),
                    "context": context,
                }
            )

            # Process with vision-enabled LLM
            result = invoke_llm_with_images(
                llm, prompt_template, variables, image_data_list
            )

            return result if result else "No analysis result returned"

        except Exception as e:
            logger.error(f"Vision processing error: {e}")
            return f"Vision analysis error: {str(e)}"

    @staticmethod
    def combine_text_and_vision_analysis(
        text_analysis: str,
        vision_analysis: str,
        combination_strategy: str = "comprehensive",
    ) -> str:
        """
        Combine text and vision analysis results.

        Args:
            text_analysis: The text-based analysis result
            vision_analysis: The vision-based analysis result
            combination_strategy: How to combine the results ("comprehensive", "integrated", "side-by-side")

        Returns:
            str: The combined analysis
        """

        if not vision_analysis or vision_analysis.startswith("Vision analysis"):
            return text_analysis

        if combination_strategy == "comprehensive":
            return f"""## Text Analysis
{text_analysis}

## Visual Analysis
{vision_analysis}

## Combined Insights
The analysis above integrates both textual content and visual elements to provide a comprehensive assessment."""

        elif combination_strategy == "integrated":
            return f"""## Comprehensive Analysis
{text_analysis}

### Visual Elements Detected:
{vision_analysis}"""

        else:  # side-by-side
            return f"""**Text Analysis:** {text_analysis}

**Visual Analysis:** {vision_analysis}"""

    @staticmethod
    def prepare_images_for_comparison(
        doc1_images: List[str],
        doc2_images: List[str],
        doc1_filename: str,
        doc2_filename: str,
    ) -> List[Dict[str, Any]]:
        """
        Prepare images from two documents for comparison analysis.

        Args:
            doc1_images: List of base64 images from document 1
            doc2_images: List of base64 images from document 2
            doc1_filename: Filename of document 1
            doc2_filename: Filename of document 2

        Returns:
            List of image dictionaries with document labels
        """
        combined_images = []

        for i, img in enumerate(doc1_images):
            combined_images.append(
                {
                    "image_data": img,
                    "source_file": doc1_filename,
                    "document": "doc1",
                    "image_index": i,
                    "metadata": {
                        "document_label": "Document 1",
                        "extracted_from": doc1_filename,
                    },
                }
            )

        for i, img in enumerate(doc2_images):
            combined_images.append(
                {
                    "image_data": img,
                    "source_file": doc2_filename,
                    "document": "doc2",
                    "image_index": i,
                    "metadata": {
                        "document_label": "Document 2",
                        "extracted_from": doc2_filename,
                    },
                }
            )

        return combined_images

    @staticmethod
    def safe_vision_analysis(
        llm,
        prompt_template: str,
        variables: Dict[str, Any],
        images: List[Dict[str, Any]],
    ) -> str:
        """
        Safely attempt vision analysis with fallback handling.

        Args:
            llm: The LLM instance
            prompt_template: The prompt template
            variables: Template variables
            images: List of image dictionaries

        Returns:
            str: Analysis result or error message
        """
        try:
            if not VisionService.is_vision_enabled(llm):
                return "Vision analysis not available with current model"

            if not images:
                return "No images found in documents"

            # Limit number of images to process
            limited_images = images[: settings.MAX_IMAGES_PER_DOCUMENT]

            from app.services.llms import invoke_llm_with_images

            return invoke_llm_with_images(
                llm,
                prompt_template,
                variables,
                [img["image_data"] for img in limited_images],
            )

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Vision analysis unavailable: {str(e)}"

    @staticmethod
    def extract_table_as_json(
        llm, page_images: List[str], page_numbers: List[int], filename: str
    ) -> Dict[str, Any]:
        """
        Extract table data from page images as structured JSON.
        Processes images in batches of 5 to avoid token limits.

        Args:
            llm: The LLM instance to use
            page_images: List of base64 encoded images containing tables
            page_numbers: List of corresponding page numbers
            filename: Source filename for context

        Returns:
            Dict containing extracted table data and metadata
        """

        if not VisionService.is_vision_enabled(llm):
            return {}

        if not page_images:
            return {}

        # Process in batches of 5 images to avoid token limits
        BATCH_SIZE = 5
        all_tables = []

        logger.info(
            f"🔄 Processing {len(page_images)} table pages in batches of {BATCH_SIZE}"
        )

        for batch_start in range(0, len(page_images), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(page_images))
            batch_images = page_images[batch_start:batch_end]
            batch_page_numbers = page_numbers[batch_start:batch_end]

            logger.info(
                f"📦 Processing batch {batch_start//BATCH_SIZE + 1}: pages {batch_page_numbers}"
            )

            vision_images = []
            for i, img_b64 in enumerate(batch_images):
                vision_images.append(
                    {
                        "image_data": img_b64,
                        "metadata": {
                            "source": filename,
                            "page": batch_page_numbers[i],
                            "content_type": "table",
                        },
                    }
                )

            table_extraction_prompt = """
Analyze the images and extract all table data as structured JSON.

For each table found, create a JSON object with:
1. "table_id": Unique identifier for the table (e.g., "table_1", "table_2")
2. "page": Page number where table appears
3. "title": Table title or caption if visible
4. "headers": List of column headers (empty list if no headers)
5. "rows": List of row data (each row as list of values)
6. "summary": Brief description of what the table contains
7. "context": Any surrounding text that provides table context
8. "metadata": Object with "row_count", "column_count", "table_type"

CRITICAL GUIDELINES FOR TABLE STRUCTURE:
- CAREFULLY identify all columns including unlabeled ones
- If the leftmost column has no header but contains row descriptions/labels, include it as a separate column
- Count ALL visible columns, not just the ones with headers
- For tables with unlabeled first columns containing descriptions (like "Monthly fee", "Minimum per order"), treat these as the first column data
- Be precise with data extraction - maintain exact values
- If a cell is empty, use null
- For merged cells, repeat the value across columns
- Include all visible text and numbers
- Preserve formatting information when possible

HEADER DETECTION:
- Look for column headers at the top of each column
- If a column has no visible header, use descriptive names like "Description", "Fee Type", "Category" etc.
- Pay special attention to tables where the first column may be unlabeled but contains row labels

Document: {filename}
Batch: Pages {batch_pages}
Expected content: Tables, charts, structured data

Return ONLY the JSON array wrapped in ```json``` code blocks.
Example format for a typical fee schedule table:
```json
[
  {{
    "table_id": "table_1", 
    "page": 1,
    "title": "Fee Schedule",
    "headers": ["Fee Type", "Smart Plan", "All-inclusive Plan"],
    "rows": [
      ["Monthly fee", "free of charge", "free of charge"],
      ["Minimum per order", null, "2 USD/2 EUR"],
      ["Amount per share", "0.02 USD/0.02 EUR", "0.02 USD/0.02 EUR"]
    ],
    "summary": "Comparison of fees between Smart and All-inclusive plans",
    "context": "Trading fee structure for different account types",
    "metadata": {{
      "row_count": 3,
      "column_count": 3,
      "table_type": "comparison"
    }}
  }}
]
```
            """

            batch_tables = VisionService._process_batch_for_tables(
                llm,
                table_extraction_prompt,
                filename,
                batch_page_numbers,
                vision_images,
            )

            # Add tables from this batch to the overall results
            all_tables.extend(batch_tables)

        # Return combined results from all batches
        logger.info(f"📊 Total tables extracted from {filename}: {len(all_tables)}")

        return {
            "tables": all_tables,
            "source": filename,
            "extraction_successful": len(all_tables) > 0,
            "page_count": len(page_images),
            "batches_processed": (len(page_images) + BATCH_SIZE - 1) // BATCH_SIZE,
        }

    @staticmethod
    def _process_batch_for_tables(
        llm,
        prompt_template: str,
        filename: str,
        page_numbers: List[int],
        vision_images: List[Dict],
    ) -> List[Dict]:
        """
        Process a single batch of images for table extraction.

        Args:
            llm: The LLM instance
            prompt_template: The table extraction prompt template
            filename: Source filename
            page_numbers: Page numbers for this batch
            vision_images: Vision images for this batch

        Returns:
            List of extracted table dictionaries
        """
        try:
            result = VisionService.safe_vision_analysis(
                llm=llm,
                prompt_template=prompt_template,
                variables={
                    "filename": filename,
                    "batch_pages": (
                        f"{page_numbers[0]}-{page_numbers[-1]}"
                        if len(page_numbers) > 1
                        else str(page_numbers[0])
                    ),
                },
                images=vision_images,
            )

            # 🐛 DEBUG: Print the raw LLM response for debugging table extraction
            logger.info("=" * 80)
            logger.info("🐛 DEBUG: RAW LLM RESPONSE FOR TABLE EXTRACTION (BATCH)")
            logger.info(f"📄 File: {filename}")
            logger.info(f"📊 Pages in batch: {page_numbers}")
            logger.info(f"📝 Response length: {len(result)} characters")
            logger.info("-" * 80)
            logger.info(f"RAW RESPONSE:\n{result}")
            logger.info("=" * 80)

            # Extract JSON from response
            import json
            import re

            json_match = re.search(
                r"```(?:json)?\s*\n?(\[.*?\])\s*\n?```",
                result,
                re.DOTALL | re.IGNORECASE,
            )

            if json_match:
                # 🐛 DEBUG: Show what JSON was extracted
                extracted_json = json_match.group(1)
                logger.info("🐛 DEBUG: EXTRACTED JSON FROM BATCH RESPONSE")
                logger.info(f"📝 JSON length: {len(extracted_json)} characters")
                logger.info(f"JSON content:\n{extracted_json}")
                logger.info("-" * 40)

                try:
                    tables_data = json.loads(extracted_json)
                    logger.info(
                        f"✅ Successfully parsed {len(tables_data)} tables from batch {page_numbers}"
                    )

                    # 🐛 DEBUG: Show summary of each table found in this batch
                    for i, table in enumerate(tables_data):
                        table_id = table.get("table_id", f"table_{i}")
                        page = table.get("page", "unknown")
                        title = table.get("title", "No title")
                        row_count = len(table.get("rows", []))
                        logger.info(
                            f"🐛 Batch Table {i+1}: {table_id} (Page {page}) - '{title}' ({row_count} rows)"
                        )
                    logger.info("-" * 40)
                    return tables_data
                except json.JSONDecodeError as e:
                    logger.error(
                        f"🐛 DEBUG: Failed to parse JSON from batch table extraction: {e}"
                    )
                    logger.error(f"🐛 Problematic JSON: {extracted_json[:500]}...")
                    return []
            else:
                logger.warning(
                    f"🐛 DEBUG: No JSON code blocks found in batch response for pages {page_numbers}"
                )

            # Fallback: try to extract any JSON-like content
            logger.info(
                f"🐛 DEBUG: Attempting fallback JSON extraction for batch {page_numbers}"
            )
            json_match = re.search(r"(\[.*?\])", result, re.DOTALL)

            if json_match:
                try:
                    tables_data = json.loads(json_match.group(1))
                    logger.info(
                        f"Successfully extracted {len(tables_data)} tables from batch {page_numbers} (fallback)"
                    )
                    return tables_data
                except json.JSONDecodeError as fallback_error:
                    logger.error(
                        f"🐛 DEBUG: Fallback JSON parsing also failed for batch {page_numbers}: {fallback_error}"
                    )

            logger.warning(f"⚠️ No valid table data extracted from batch {page_numbers}")
            return []

        except Exception as e:
            logger.error(f"Error processing table batch {page_numbers}: {e}")
            return []
