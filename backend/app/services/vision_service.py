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

        if not model_name:
            return False

        # Check against vision-enabled models list
        return any(
            vision_model in model_name.lower()
            for vision_model in settings.VISION_ENABLED_MODELS
        )

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
