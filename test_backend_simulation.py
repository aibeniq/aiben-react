#!/usr/bin/env python3
"""
Test to simulate the exact backend conditions and see the enhanced logging.
"""

import sys
import os
import logging

# Configure logging to match backend format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

sys.path.append(os.path.join(os.getcwd(), "backend"))


def simulate_backend_processing():
    """Simulate the exact processing that happens in your backend"""

    print("🔄 SIMULATING BACKEND TABLE PROCESSING")
    print("=" * 60)

    # Mock different LLM types that might be used
    class MockChatOpenAI:
        """Simulate ChatOpenAI with different model names"""

        def __init__(self, model_name):
            self.model_name = model_name
            self.model = model_name

    class MockReplicateLLM:
        """Simulate Replicate LLM"""

        def __init__(self, model_name):
            self.model = model_name

    class MockWrappedLLM:
        """Simulate a wrapped LLM (like with rate limiting)"""

        def __init__(self, inner_llm):
            self._llm = inner_llm

    # Test different LLM configurations
    test_llms = [
        ("GPT-4o (should work)", MockChatOpenAI("gpt-4o")),
        ("GPT-4 Vision (should work)", MockChatOpenAI("gpt-4-vision-preview")),
        ("GPT-3.5 (should NOT work)", MockChatOpenAI("gpt-3.5-turbo")),
        ("Claude-3.5 (should work)", MockChatOpenAI("claude-3-5-sonnet-20241022")),
        ("Wrapped GPT-4o (should work)", MockWrappedLLM(MockChatOpenAI("gpt-4o"))),
    ]

    # Mock settings
    class MockSettings:
        VISION_ENABLED_MODELS = [
            "gpt-4-vision-preview",
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "claude-3-5-sonnet",
        ]

    # Load file
    file_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        file_content = f.read()

    # Import and patch settings
    import backend.app.core.config as config_module

    original_settings = getattr(config_module, "settings", None)
    config_module.settings = MockSettings()

    try:
        from backend.app.services.document_utils import (
            extract_documents_with_table_processing,
        )

        for llm_name, llm in test_llms:
            print(f"\n🤖 Testing: {llm_name}")
            print("-" * 40)

            try:
                # This will trigger our enhanced logging
                processed_docs, table_data = extract_documents_with_table_processing(
                    file_content, "Appendix 6 Fee Schedule.pdf", llm
                )

                vision_used = len(table_data.get("tables", [])) > 0
                print(
                    f"📊 Result: {'✅ Vision used' if vision_used else '❌ Vision NOT used'}"
                )

            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Failed to import: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Restore settings
        if original_settings:
            config_module.settings = original_settings


if __name__ == "__main__":
    simulate_backend_processing()

    print("\n" + "=" * 60)
    print("🎯 ANALYSIS:")
    print("1. Check which LLM types work vs don't work")
    print("2. Look for 'VISION DISABLED' messages to see the reason")
    print("3. The model name must contain one of the vision-enabled patterns")
    print("=" * 60)
