"""
Quick patch to add debug logging to identify the LLM model issue.
This will show us exactly what model is being used and why vision is disabled.
"""

# Add this to the chatbot route temporarily to debug the issue
import logging


def debug_llm_vision_capability(llm):
    """Debug function to identify why vision is not enabled"""

    logger = logging.getLogger(__name__)

    logger.info("🔍 DEBUGGING LLM VISION CAPABILITY")

    if not llm:
        logger.error("❌ LLM is None")
        return False

    # Get model information
    model_name = getattr(llm, "model_name", "") or getattr(llm, "model", "")
    class_name = type(llm).__name__

    logger.info(f"🤖 LLM Class: {class_name}")
    logger.info(f"🤖 LLM Model Name: '{model_name}'")

    # Check for wrapped models
    if hasattr(llm, "_llm"):
        inner_llm = getattr(llm, "_llm", None)
        if inner_llm:
            inner_model = getattr(inner_llm, "model_name", "") or getattr(
                inner_llm, "model", ""
            )
            inner_class = type(inner_llm).__name__
            logger.info(f"🤖 Inner LLM Class: {inner_class}")
            logger.info(f"🤖 Inner LLM Model: '{inner_model}'")

    # Mock vision-enabled models for testing
    vision_models = [
        "gpt-4-vision-preview",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
        "claude-3-5-sonnet",
    ]

    logger.info(f"🔮 Vision enabled models: {vision_models}")

    # Check if model matches
    for vision_model in vision_models:
        if vision_model in model_name.lower():
            logger.info(f"✅ MATCH FOUND: '{vision_model}' in '{model_name}'")
            return True
        else:
            logger.debug(f"❌ No match: '{vision_model}' not in '{model_name}'")

    logger.error(f"❌ NO VISION MATCH: Model '{model_name}' not in vision-enabled list")
    logger.error(f"💡 SOLUTION: Add your model to VISION_ENABLED_MODELS in settings")

    return False


# Example usage in chatbot route:
# Add this right before calling extract_documents_with_table_processing:


def patch_chatbot_for_vision_debug():
    """
    Add this code to your chatbot route around line 1300 right before:
    processed_documents, table_data = extract_documents_with_table_processing(...)
    """

    code_to_add = """
    # DEBUG: Check why vision is not enabled
    logger.info("🔍 DEBUGGING: Checking LLM vision capability before table processing")
    debug_result = debug_llm_vision_capability(llm)
    logger.info(f"🔍 DEBUG RESULT: Vision should be enabled: {debug_result}")
    """

    return code_to_add


if __name__ == "__main__":
    print("📋 DEBUG PATCH INSTRUCTIONS:")
    print("=" * 50)
    print("1. Add the debug_llm_vision_capability function to your chatbot route")
    print("2. Call it right before extract_documents_with_table_processing")
    print("3. Check the logs to see what model is being used")
    print("4. If needed, add your model to VISION_ENABLED_MODELS in settings")
    print("=" * 50)
