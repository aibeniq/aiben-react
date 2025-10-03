"""
Universal LLM Execution Wrapper

This module provides a universal wrapper for all LLM requests that ensures
they go through the global rate limiter, whether they are text-only or 
multimodal (vision) requests.
"""

import asyncio
from typing import Any, Optional, List, Dict, Union
import logging

logger = logging.getLogger(__name__)


async def execute_llm_request_safely(
    llm: Any,
    content: Union[str, List[Any]],
    images: Optional[List[str]] = None,
    model_name: Optional[str] = None,
    timeout: float = 120.0
) -> Any:
    """
    Universal wrapper for all LLM requests that ensures rate limiting compliance.
    
    Handles both text-only and multimodal (vision) requests through the global
    rate limiter and request queue.
    
    Args:
        llm: The LLM instance to invoke
        content: Text content or list of messages to send
        images: Optional list of base64 encoded images for vision requests
        model_name: Optional model name for better token estimation
        timeout: Maximum time to wait for the request
        
    Returns:
        LLM response
        
    Raises:
        Exception: If the request fails or times out
    """
    # Import here to avoid circular imports
    from app.services.global_rate_limiter import global_rate_limiter
    from app.services.openai_queue import openai_request_queue
    try:
        from langchain_core.messages import HumanMessage
    except ImportError:
        from langchain.schema import HumanMessage
    
    # Extract model name if not provided
    if not model_name:
        model_name = getattr(llm, 'model_name', 'gpt-4o')
    
    # Prepare content for token estimation
    if isinstance(content, str):
        text_content = content
        messages = [HumanMessage(content=content)]
    elif isinstance(content, list):
        # Extract text from messages for estimation
        text_parts = []
        for msg in content:
            if hasattr(msg, 'content'):
                if isinstance(msg.content, str):
                    text_parts.append(msg.content)
                elif isinstance(msg.content, list):
                    # Handle multimodal content
                    for part in msg.content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            text_parts.append(part.get('text', ''))
        text_content = ' '.join(text_parts)
        messages = content
    else:
        text_content = str(content)
        messages = [HumanMessage(content=text_content)]
    
    # Estimate token consumption
    if images:
        estimated_tokens = global_rate_limiter.estimate_multimodal_tokens(
            text_content, images, model_name
        )
        logger.info(f"🖼️ Vision request: {len(images)} images, ~{estimated_tokens} tokens, model: {model_name}")
    else:
        estimated_tokens = global_rate_limiter.estimate_multimodal_tokens(
            text_content, None, model_name
        )
        logger.debug(f"📝 Text request: ~{estimated_tokens} tokens, model: {model_name}")
    
    # Execute through rate limiter and queue
    async def _execute_request():
        # Wait for rate limiter approval
        can_proceed = global_rate_limiter.wait_for_capacity(estimated_tokens, max_wait_time=60.0)
        if not can_proceed:
            raise Exception("Rate limiter timeout - could not obtain capacity within 60 seconds")
        
        # Execute through request queue
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Acquire semaphore (limits concurrent requests)
            async with openai_request_queue.semaphore:
                logger.debug(f"🚀 Executing LLM request (queue position acquired)")
                
                # Execute the actual LLM call
                if asyncio.iscoroutinefunction(llm.invoke):
                    response = await llm.invoke(messages)
                else:
                    # Run synchronous invoke in thread pool
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, llm.invoke, messages
                    )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                # Try to get actual token usage from response
                actual_tokens = estimated_tokens  # Default fallback
                if hasattr(response, 'usage_metadata'):
                    if hasattr(response.usage_metadata, 'total_tokens'):
                        actual_tokens = response.usage_metadata.total_tokens
                elif hasattr(response, 'token_usage'):
                    actual_tokens = getattr(response.token_usage, 'total_tokens', estimated_tokens)
                
                # Update rate limiter with actual usage
                global_rate_limiter.record_actual_usage(actual_tokens, estimated_tokens)
                
                # Update queue statistics
                openai_request_queue.record_request(execution_time, True)
                
                logger.info(
                    f"✅ LLM request completed: {execution_time:.2f}s, "
                    f"tokens: {actual_tokens} (est: {estimated_tokens})"
                )
                
                return response
                
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            openai_request_queue.record_request(execution_time, False)
            logger.error(f"❌ LLM request failed after {execution_time:.2f}s: {e}")
            raise
    
    # Execute with timeout
    try:
        return await asyncio.wait_for(_execute_request(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"❌ LLM request timed out after {timeout}s")
        raise Exception(f"LLM request timed out after {timeout} seconds")


def execute_llm_request_safely_sync(
    llm: Any,
    content: Union[str, List[Any]],
    images: Optional[List[str]] = None,
    model_name: Optional[str] = None,
    timeout: float = 120.0
) -> Any:
    """
    Synchronous wrapper for execute_llm_request_safely.
    
    This function handles the async execution in a way that works
    with synchronous calling code.
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we need to use run_in_executor
            # to avoid "RuntimeError: cannot be called from a running event loop"
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(execute_llm_request_safely(
                        llm, content, images, model_name, timeout
                    ))
                )
                return future.result(timeout=timeout + 10)  # Extra buffer for timeout
        else:
            # No running loop, we can use asyncio.run directly
            return asyncio.run(execute_llm_request_safely(
                llm, content, images, model_name, timeout
            ))
    except RuntimeError as e:
        if "no running event loop" in str(e):
            # No event loop at all, create one
            return asyncio.run(execute_llm_request_safely(
                llm, content, images, model_name, timeout
            ))
        else:
            raise


def extract_images_from_messages(messages: List[Any]) -> List[str]:
    """
    Extract base64 image data from message content.
    
    Args:
        messages: List of LangChain messages
        
    Returns:
        List of base64 encoded image strings
    """
    images = []
    
    for message in messages:
        if hasattr(message, 'content') and isinstance(message.content, list):
            for part in message.content:
                if isinstance(part, dict) and part.get('type') == 'image_url':
                    image_url = part.get('image_url', {}).get('url', '')
                    if image_url.startswith('data:image/'):
                        # Extract base64 data from data URL
                        base64_data = image_url.split(',', 1)[-1]
                        images.append(base64_data)
    
    return images