#!/usr/bin/env python3

# Quick test script to validate the models
import sys

sys.path.append("./backend")

try:
    from app.models import (
        GenerateFormFieldsRequest,
        GenerateTopicsRequest,
        GenerateQuestionsRequest,
        GenerateOutlineRequest,
        ReportGenieRequest,
        OptimizeOutlineRequest,
    )

    # Test creating instances
    form_req = GenerateFormFieldsRequest(description="Test description for form fields")
    topics_req = GenerateTopicsRequest(description="Test description for topics")
    questions_req = GenerateQuestionsRequest(
        description="Test description for questions"
    )
    outline_req = GenerateOutlineRequest(description="Test description for outline")

    print("✅ All models imported and instantiated successfully!")
    print(f"form_req.search_mode: {form_req.search_mode}")
    print(f"topics_req.search_mode: {topics_req.search_mode}")
    print(f"questions_req.search_mode: {questions_req.search_mode}")
    print(f"outline_req.search_mode: {outline_req.search_mode}")

    # Test with different search mode
    form_req_full = GenerateFormFieldsRequest(
        description="Test description", search_mode="full_scan"
    )
    print(f"form_req_full.search_mode: {form_req_full.search_mode}")

    # Test invalid search mode (should raise validation error)
    try:
        invalid_req = GenerateFormFieldsRequest(
            description="Test description", search_mode="invalid_mode"
        )
        print("❌ ERROR: Invalid search mode was accepted!")
    except Exception as e:
        print(
            f"✅ Validation correctly rejected invalid search mode: {type(e).__name__}"
        )

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
