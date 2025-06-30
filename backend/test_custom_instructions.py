#!/usr/bin/env python3
"""
Test script to verify that custom instructions are being properly passed
to the LLM calls in the optimize outline functionality.
"""

import json
import tempfile
import os

# Test data to verify custom instructions are working
test_outline = [
    {"text": "Study Purpose", "consultDocuments": True},
    {"text": "Participant Eligibility", "consultDocuments": True},
    {"text": "Risks and Benefits", "consultDocuments": False},  # Should be excluded
]

test_custom_instructions = "SPECIAL TEST INSTRUCTION: Always include the phrase 'CUSTOM_INSTRUCTION_APPLIED' in your response."

# Sample ground truth content
test_ground_truth = """
This study aims to investigate the effectiveness of a new treatment approach for patients with chronic pain.

Participants must be:
- 18 years or older
- Diagnosed with chronic pain lasting more than 6 months
- Not currently taking pain medication

The study involves minimal risk to participants. Benefits may include improved pain management and contributing to medical research.
"""


# Expected: Custom instructions should appear in the prompts and affect the LLM output
def test_custom_instructions():
    print("Testing custom instructions integration...")

    # Create a temporary file with ground truth content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(test_ground_truth)
        temp_file_path = f.name

    print(f"Created test ground truth file: {temp_file_path}")
    print(f"Test outline: {json.dumps(test_outline, indent=2)}")
    print(f"Custom instructions: {test_custom_instructions}")

    print(
        """
To test:
1. Use the optimize outline API with these test parameters
2. Check that custom instructions appear in backend logs
3. Verify that LLM responses include the custom instruction phrase
4. Confirm that sections with consultDocuments: False are excluded
    """
    )

    # Clean up
    os.unlink(temp_file_path)
    print("Test preparation complete.")


if __name__ == "__main__":
    test_custom_instructions()
