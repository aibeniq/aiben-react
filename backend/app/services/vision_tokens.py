"""
Vision Token Calculator

This module provides utilities for calculating token consumption
when processing images with vision-enabled models like GPT-4V.
"""

import base64
import math
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def calculate_image_tokens(
    image_base64: str, 
    model: str = "gpt-4o", 
    detail: str = "auto"
) -> int:
    """
    Calculate token consumption for image processing based on OpenAI's pricing model.
    
    Args:
        image_base64: Base64 encoded image data
        model: The model being used (gpt-4o, gpt-4o-mini, gpt-4-vision-preview)
        detail: Image detail level ("low", "high", "auto")
    
    Returns:
        Estimated token consumption for the image
    """
    try:
        # Decode base64 to get image size estimation
        image_data = base64.b64decode(image_base64)
        image_size_kb = len(image_data) / 1024
        
        # OpenAI's token calculation for images:
        # - Low detail: 85 tokens regardless of size
        # - High detail: 85 + (tiles * 170) tokens
        # - Auto detail: depends on image size
        
        if detail == "low":
            return 85
        
        # For high detail or auto, estimate based on image size
        # OpenAI divides images into 512x512 tiles for processing
        
        # Rough estimation: assume square images for simplicity
        # More accurate calculation would require actual image dimensions
        estimated_pixels = image_size_kb * 1000  # Very rough estimation
        estimated_dimension = math.sqrt(estimated_pixels)
        
        # Calculate number of 512x512 tiles needed
        tiles_per_dimension = math.ceil(estimated_dimension / 512)
        total_tiles = tiles_per_dimension * tiles_per_dimension
        
        # Apply OpenAI's formula: 85 base + (tiles * 170)
        tokens = 85 + (total_tiles * 170)
        
        # Cap at reasonable maximum (OpenAI's current max is around 2000 tokens per image)
        tokens = min(tokens, 2000)
        
        # Model-specific adjustments
        if model == "gpt-4o-mini":
            # GPT-4o-mini typically uses fewer tokens for vision
            tokens = int(tokens * 0.7)
        elif model == "gpt-4-vision-preview":
            # Legacy model, might use more tokens
            tokens = int(tokens * 1.2)
        
        logger.debug(f"Calculated {tokens} tokens for image (size: {image_size_kb:.1f}KB, model: {model})")
        return max(tokens, 85)  # Minimum 85 tokens
        
    except Exception as e:
        logger.warning(f"Error calculating image tokens: {e}, using conservative estimate")
        # Conservative fallback: assume high token usage
        return 1000


def calculate_multimodal_tokens(
    text_content: str,
    images: List[str],
    model: str = "gpt-4o"
) -> Dict[str, int]:
    """
    Calculate total token consumption for multimodal requests.
    
    Args:
        text_content: The text portion of the request
        images: List of base64 encoded images
        model: The model being used
    
    Returns:
        Dictionary with breakdown of token usage
    """
    # Rough text token estimation (4 chars ≈ 1 token)
    text_tokens = len(text_content) // 4
    
    # Calculate image tokens
    image_tokens = sum(
        calculate_image_tokens(img, model) for img in images
    )
    
    total_tokens = text_tokens + image_tokens
    
    return {
        "text_tokens": text_tokens,
        "image_tokens": image_tokens,
        "total_tokens": total_tokens,
        "image_count": len(images)
    }


def get_vision_model_multiplier(model: str) -> float:
    """
    Get the rate limit multiplier for vision models.
    Vision models typically have different rate limits than text-only models.
    
    Args:
        model: The model name
    
    Returns:
        Multiplier to apply to standard rate limits
    """
    vision_multipliers = {
        "gpt-4o": 1.5,  # Higher token consumption
        "gpt-4o-mini": 1.2,  # Moderate increase
        "gpt-4-vision-preview": 2.0,  # Legacy model, more expensive
        "claude-3-opus": 1.8,
        "claude-3-sonnet": 1.4,
    }
    
    return vision_multipliers.get(model, 1.0)