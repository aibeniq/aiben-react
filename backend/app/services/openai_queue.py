"""
OpenAI Request Queue Manager

This module provides a queue-based system to manage OpenAI API requests,
working in conjunction with the global rate limiter to prevent overwhelming
the API with too many concurrent requests.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class OpenAIRequestQueue:
    """
    Queue manager for OpenAI API requests to prevent overwhelming the API.
    
    Works alongside the global rate limiter to provide both queue management
    and rate limiting for optimal API usage.
    """
    
    def __init__(self, max_concurrent_requests: int = 3, max_queue_size: int = 50):
        """
        Initialize the request queue.
        
        Args:
            max_concurrent_requests: Maximum number of concurrent requests
            max_queue_size: Maximum number of requests that can be queued
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.max_queue_size = max_queue_size
        
        # Queue management
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.queue_size = 0
        self.queue_lock = asyncio.Lock()
        
        # Statistics
        self.total_requests = 0
        self.completed_requests = 0
        self.failed_requests = 0
        self.queue_wait_times = []
        
        # Thread pool for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"🎯 OpenAI Request Queue initialized: max_concurrent={max_concurrent_requests}, max_queue={max_queue_size}")
    
    async def add_request(self, 
                         func: Callable, 
                         *args, 
                         request_type: str = "unknown",
                         estimated_tokens: int = 0,
                         **kwargs) -> Any:
        """
        Add a request to the queue and execute it when capacity is available.
        
        Args:
            func: The function to execute (should be an OpenAI API call)
            *args: Arguments to pass to the function
            request_type: Type of request for logging/monitoring
            estimated_tokens: Estimated tokens for this request
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If queue is full or request fails
        """
        start_time = time.time()
        
        # Check queue capacity
        async with self.queue_lock:
            if self.queue_size >= self.max_queue_size:
                raise Exception(f"OpenAI request queue is full ({self.queue_size}/{self.max_queue_size})")
            
            self.queue_size += 1
            self.total_requests += 1
            request_id = self.total_requests
        
        logger.info(f"🏃‍♂️ Request #{request_id} ({request_type}) added to queue (size: {self.queue_size}, tokens: {estimated_tokens})")
        
        try:
            # Wait for available slot
            async with self.semaphore:
                # Update queue size when we start processing
                async with self.queue_lock:
                    self.queue_size -= 1
                
                queue_wait_time = time.time() - start_time
                self.queue_wait_times.append(queue_wait_time)
                
                logger.info(f"⚡ Request #{request_id} ({request_type}) starting execution (waited {queue_wait_time:.2f}s)")
                
                # Add small delay between requests to be gentle on the API
                await asyncio.sleep(0.2)
                
                # Execute the function
                execution_start = time.time()
                
                # Check if this is a CPU-bound operation that should run in thread pool
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    # Run in thread pool to avoid blocking the event loop
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
                
                execution_time = time.time() - execution_start
                total_time = time.time() - start_time
                
                self.completed_requests += 1
                
                logger.info(f"✅ Request #{request_id} ({request_type}) completed successfully "
                           f"(execution: {execution_time:.2f}s, total: {total_time:.2f}s)")
                
                return result
                
        except Exception as e:
            self.failed_requests += 1
            
            # Update queue size on failure
            async with self.queue_lock:
                if self.queue_size > 0:
                    self.queue_size -= 1
            
            total_time = time.time() - start_time
            logger.error(f"❌ Request #{request_id} ({request_type}) failed after {total_time:.2f}s: {e}")
            raise e
    
    async def batch_process(self, 
                           requests: list, 
                           batch_name: str = "batch",
                           delay_between_batches: float = 1.0) -> list:
        """
        Process a batch of requests with intelligent spacing.
        
        Args:
            requests: List of (func, args, kwargs, request_type, estimated_tokens) tuples
            batch_name: Name for the batch (for logging)
            delay_between_batches: Delay between processing individual requests
            
        Returns:
            List of results in the same order as requests
        """
        logger.info(f"🔄 Starting batch '{batch_name}' with {len(requests)} requests")
        
        results = []
        
        for i, request_data in enumerate(requests):
            if len(request_data) == 5:
                func, args, kwargs, request_type, estimated_tokens = request_data
            elif len(request_data) == 4:
                func, args, kwargs, request_type = request_data
                estimated_tokens = 0
            else:
                func, args, kwargs = request_data
                request_type = f"{batch_name}_item_{i}"
                estimated_tokens = 0
            
            try:
                result = await self.add_request(
                    func, 
                    *args, 
                    request_type=f"{batch_name}_{request_type}_{i+1}",
                    estimated_tokens=estimated_tokens,
                    **kwargs
                )
                results.append(result)
                
                # Add delay between requests in the batch
                if i < len(requests) - 1:  # Don't delay after the last request
                    await asyncio.sleep(delay_between_batches)
                    
            except Exception as e:
                logger.error(f"Request {i+1} in batch '{batch_name}' failed: {e}")
                results.append(None)  # Add None for failed requests to maintain order
                
                # Continue with next request even if one fails
                continue
        
        successful_results = [r for r in results if r is not None]
        logger.info(f"🎯 Batch '{batch_name}' completed: {len(successful_results)}/{len(requests)} successful")
        
        return results
    
    def record_request(self, execution_time: float, success: bool) -> None:
        """
        Record the completion of a request for statistics tracking.
        
        Args:
            execution_time: Time taken to execute the request in seconds
            success: Whether the request was successful
        """
        if success:
            self.completed_requests += 1
        else:
            self.failed_requests += 1
        
        # Record execution time as a wait time for statistics
        self.queue_wait_times.append(execution_time)
        
        # Keep only the last 100 wait times to prevent memory growth
        if len(self.queue_wait_times) > 100:
            self.queue_wait_times = self.queue_wait_times[-100:]
        
        logger.debug(f"📊 Request recorded: {execution_time:.2f}s, success: {success}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        avg_wait_time = sum(self.queue_wait_times) / len(self.queue_wait_times) if self.queue_wait_times else 0
        
        return {
            "current_queue_size": self.queue_size,
            "max_queue_size": self.max_queue_size,
            "max_concurrent_requests": self.max_concurrent_requests,
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.completed_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "average_queue_wait_time": avg_wait_time,
            "recent_wait_times": self.queue_wait_times[-10:],  # Last 10 wait times
        }
    
    def __del__(self):
        """Cleanup thread pool on destruction."""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)


# Global instance - shared across all OpenAI requests
openai_request_queue = OpenAIRequestQueue(max_concurrent_requests=2, max_queue_size=20)