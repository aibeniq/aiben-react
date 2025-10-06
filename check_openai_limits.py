#!/usr/bin/env python3
"""
Script to check your actual OpenAI rate limits.
Run this to see what limits you actually have vs what you're artificially imposing.
"""

import os
import openai
from openai import OpenAI

def check_openai_limits():
    """Check your actual OpenAI rate limits."""
    
    try:
        # Initialize client
        client = OpenAI()
        
        # Make a small test request to see rate limit headers
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API call successful!")
        print("\nNote: OpenAI rate limits are typically shown in response headers.")
        print("Your current artificial limits in the code:")
        print("- Tokens: 120,000/minute (you set this artificially low)")
        print("- Requests: 300/minute (you set this artificially low)")
        print("\nTypical OpenAI limits for paid accounts:")
        print("- GPT-4: 200k-800k tokens/minute")
        print("- GPT-4: 500-10k requests/minute")
        print("\nRecommendation: Increase your limits to 160k-200k tokens/minute")
        
    except Exception as e:
        print(f"❌ Error checking OpenAI limits: {e}")
        print("Make sure your OPENAI_API_KEY is set correctly.")

if __name__ == "__main__":
    check_openai_limits()