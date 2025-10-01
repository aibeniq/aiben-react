#!/usr/bin/env python3
"""
Test the enhanced vision question detection.
"""

import re

def is_vision_related_question(question: str) -> bool:
    """
    Detect if a user's question is asking about visual content that would require vision analysis.
    
    Args:
        question: The user's question
        
    Returns:
        bool: True if the question appears to be asking about visual content
    """
    if not question:
        return False
    
    question_lower = question.lower()
    
    # Visual element keywords
    visual_keywords = [
        "logo", "image", "picture", "photo", "graphic", "icon", "symbol",
        "diagram", "chart", "graph", "figure", "illustration", "drawing",
        "visual", "color", "shape", "design", "layout", "appearance",
        "banner", "header", "footer", "watermark", "signature",
        "screenshot", "snapshot", "capture", "shoe", "shoes", "product",
        "item", "clothing", "footwear", "object", "thing", "brand"
    ]
    
    # Question patterns that suggest visual analysis
    visual_patterns = [
        r"what.*(?:looks|appears|shows|displays|shown)",
        r"what.*(?:look like|appear like|shown)",
        r"(?:can you see|do you see|is there).*(?:in the|on the)",
        r"(?:describe|identify|recognize).*(?:the|any)",
        r"what.*(?:at the top|at the bottom|in the corner|on the side)",
        r"what.*(?:color|size|style|format)",
        r"(?:show|display|contain|include).*(?:image|picture|logo)",
        r"(?:what|how).*(?:does|do).*(?:look|appear)",
        r"what.*(?:shoe|product|item|object).*(?:look|appear|shown)"
    ]
    
    print(f"Testing question: '{question}'")
    print(f"Lowercase: '{question_lower}'")
    
    # Check for visual keywords
    for keyword in visual_keywords:
        if keyword in question_lower:
            print(f"  ✅ Matched keyword: '{keyword}'")
            return True
    
    # Check for visual question patterns
    for pattern in visual_patterns:
        if re.search(pattern, question_lower):
            print(f"  ✅ Matched pattern: '{pattern}'")
            return True
    
    print("  ❌ No vision-related content detected")
    return False

def main():
    # Test the problematic question
    test_questions = [
        "What does the shoe shown in this document look like?",
        "What is the logo at the top of the letter?",
        "Can you see any products in the image?",
        "Describe the shoe in the picture",
        "What color is the footwear?",
        "How does the item appear?",
        "What shoe is displayed?",
        "What table data is available?",  # Should NOT trigger vision
    ]
    
    print("🧪 Testing Enhanced Vision Question Detection")
    print("=" * 60)
    
    for question in test_questions:
        result = is_vision_related_question(question)
        status = "✅ VISION" if result else "❌ TEXT"
        print(f"\n{status}: {question}")
        print("-" * 40)

if __name__ == "__main__":
    main()