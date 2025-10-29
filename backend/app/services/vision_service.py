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
    def is_vision_enabled(llm, current_user=None) -> bool:
        """
        Check if vision analysis should be performed.

        Args:
            llm: The LLM instance to check
            current_user: Current user object (optional for backward compatibility)

        Returns:
            bool: True if BOTH model supports vision AND user has enabled it
        """
        if not llm:
            return False

        # Check 1: Does the model support vision?
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
        model_supports_vision = any(
            vision_model in model_name.lower()
            for vision_model in settings.VISION_ENABLED_MODELS
        )

        if not model_supports_vision:
            return False

        # Check 2: Has the user enabled vision analysis?
        if current_user is not None:
            user_enabled_vision = getattr(
                current_user, "vision_analysis_enabled", False
            )
            if not user_enabled_vision:
                logger.info(
                    f"Vision analysis disabled by user preference (user_id: {getattr(current_user, 'id', 'unknown')})"
                )
                return False

        return True

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

            # Support batching: split images into batches configured by settings.VISION_IMAGES_BATCH_SIZE
            batch_size = max(1, int(getattr(settings, "VISION_IMAGES_BATCH_SIZE", 10)))
            partial_results: List[str] = []

            for i in range(0, len(image_data_list), batch_size):
                batch = image_data_list[i : i + batch_size]
                try:
                    part = invoke_llm_with_images(
                        llm, prompt_template, variables, batch
                    )

                    # Log each raw batch response
                    try:
                        logger.debug(
                            f"Raw vision batch response (process_images_with_prompt) [{i // batch_size}]: {repr(part)}"
                        )
                        print(
                            f"RAW_VISION_BATCH_RESPONSE(process_images_with_prompt)[{i // batch_size}]: {repr(part)[:4000]}"
                        )
                    except Exception:
                        pass

                    if part:
                        partial_results.append(str(part))
                except Exception as e:
                    logger.error(f"Vision batch {i // batch_size} failed: {e}")
                    # continue to next batch
                    continue

            # Combine partial results
            result = "\n\n".join(partial_results).strip()

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

        # If there's no vision analysis, return text-only
        if not vision_analysis or vision_analysis.startswith("Vision analysis"):
            return text_analysis

        # Wrap the vision analysis in explicit markers so downstream QA prompts can treat it as evidence
        visual_block = (
            "\n\n---VISUAL_ANALYSIS_START---\n"
            + vision_analysis.strip()
            + "\n---VISUAL_ANALYSIS_END---\n\n"
        )

        if combination_strategy == "comprehensive":
            return f"""## Text Analysis
{text_analysis}

## Visual Analysis
{visual_block}

## Combined Insights
The analysis above integrates both textual content and visual elements to provide a comprehensive assessment."""

        elif combination_strategy == "integrated":
            return f"""## Comprehensive Analysis
{text_analysis}

### Visual Elements Detected:
{visual_block}"""

        else:  # side-by-side
            return f"""**Text Analysis:** {text_analysis}

**Visual Analysis:** {visual_block}"""

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

            # Batch images according to config
            image_payloads = [img["image_data"] for img in limited_images]
            batch_size = max(1, int(getattr(settings, "VISION_IMAGES_BATCH_SIZE", 10)))
            partial_results: List[str] = []

            for i in range(0, len(image_payloads), batch_size):
                batch = image_payloads[i : i + batch_size]
                try:
                    part = invoke_llm_with_images(
                        llm, prompt_template, variables, batch
                    )

                    try:
                        logger.debug(
                            f"Raw vision batch response (safe_vision_analysis) [{i // batch_size}]: {repr(part)}"
                        )
                        print(
                            f"RAW_VISION_BATCH_RESPONSE(safe_vision_analysis)[{i // batch_size}]: {repr(part)[:4000]}"
                        )
                    except Exception:
                        pass

                    if part:
                        partial_results.append(str(part))
                except Exception as e:
                    logger.error(f"Vision batch {i // batch_size} failed: {e}")
                    continue

            combined_result = "\n\n".join(partial_results).strip()

            # If we have multiple batches, summarize them using LLM
            if len(partial_results) > 1:
                try:
                    from app.services.llms import invoke_llm

                    # Create numbered results for better summarization
                    numbered_results = []
                    for i, result in enumerate(partial_results, 1):
                        numbered_results.append(f"Batch {i} Analysis:\n{result}")
                    vision_results_text = "\n\n".join(numbered_results)

                    # Use LLM to summarize all the vision results
                    print(
                        f"DEBUG: vision summarization language_instruction = '{variables.get('language_instruction', '')}'"
                    )
                    summary_result = invoke_llm(
                        llm,
                        settings.VISION_SUMMARIZATION_PROMPT_TEMPLATE,
                        {
                            "batch_count": len(partial_results),
                            "question": variables.get(
                                "question", "Analyze the visual content"
                            ),
                            "vision_results": vision_results_text,
                            "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                            "language_instruction": variables.get(
                                "language_instruction", ""
                            ),
                        },
                    )

                    # Use the summarized result
                    combined_result = summary_result.strip()

                except Exception as summary_error:
                    logger.warning(
                        f"Vision summarization failed, using combined results: {summary_error}"
                    )
                    # Fall back to combined results if summarization fails

            # Sanitize/normalize the vision output: prefer compact JSON with keys observations, summary, confidence
            normalized = combined_result
            try:
                import json

                # Try to parse if the model already returned JSON
                parsed = json.loads(combined_result)
                # If parsed is a dict and contains expected keys, accept as-is
                if isinstance(parsed, dict) and (
                    "observations" in parsed or "summary" in parsed
                ):
                    normalized = json.dumps(parsed)
                else:
                    # Not in expected shape -> wrap as summary
                    normalized = json.dumps(
                        {
                            "observations": [],
                            "summary": str(combined_result),
                            "confidence": "medium",
                        }
                    )
            except Exception:
                # If the model returned a refusal or prose, normalize to a compact JSON fallback
                low_conf_summary = combined_result.strip()
                # Heuristic: if the response contains phrases like "unable to" or "cannot analyze", mark low confidence
                lc = low_conf_summary.lower()
                conf = (
                    "low"
                    if any(
                        p in lc
                        for p in ["unable to", "cannot", "refuse", "can't", "don't"]
                    )
                    else "medium"
                )
                try:
                    import json

                    normalized = json.dumps(
                        {
                            "observations": [],
                            "summary": low_conf_summary,
                            "confidence": conf,
                        }
                    )
                except Exception:
                    normalized = combined_result

            # Return the normalized JSON string (or fallback to raw combined_result)
            return normalized

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Vision analysis unavailable: {str(e)}"
