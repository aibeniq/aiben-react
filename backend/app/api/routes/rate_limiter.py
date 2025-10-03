"""
Rate Limiter Monitoring Endpoint

This module provides endpoints for monitoring the global OpenAI rate limiter
status and usage statistics.
"""

from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser
from app.services.global_rate_limiter import get_rate_limiter_stats
from app.services.openai_queue import openai_request_queue
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"])


@router.get("/rate-limiter/status")
async def get_rate_limiter_status(current_user: CurrentUser):
    """
    Get current rate limiter status and usage statistics.
    
    Returns:
        Dictionary with current rate limiter usage and capacity information
    """
    try:
        # Get rate limiter stats
        rate_stats = get_rate_limiter_stats()
        
        # Get queue stats
        queue_stats = openai_request_queue.get_statistics()
        
        # Add some calculated fields for easier monitoring
        token_utilization = (rate_stats["tokens_used"] / rate_stats["tokens_limit"]) * 100
        request_utilization = (rate_stats["requests_made"] / rate_stats["requests_limit"]) * 100
        queue_utilization = (queue_stats["current_queue_size"] / queue_stats["max_queue_size"]) * 100
        
        # Determine overall system status
        if token_utilization < 80 and request_utilization < 80 and queue_utilization < 70:
            status = "healthy"
        elif token_utilization < 95 and request_utilization < 95 and queue_utilization < 90:
            status = "warning"
        else:
            status = "critical"
        
        response = {
            "rate_limiter": {
                **rate_stats,
                "token_utilization_percent": round(token_utilization, 1),
                "request_utilization_percent": round(request_utilization, 1),
            },
            "request_queue": {
                **queue_stats,
                "queue_utilization_percent": round(queue_utilization, 1),
            },
            "overall_status": status,
            "recommendations": []
        }
        
        # Add recommendations based on status
        if token_utilization > 90:
            response["recommendations"].append("High token usage - consider reducing request frequency")
        if request_utilization > 90:
            response["recommendations"].append("High request rate - consider implementing delays")
        if queue_utilization > 80:
            response["recommendations"].append("High queue utilization - requests may be delayed")
        if queue_stats["failed_requests"] > 0:
            failure_rate = (queue_stats["failed_requests"] / queue_stats["total_requests"]) * 100
            if failure_rate > 10:
                response["recommendations"].append(f"High failure rate ({failure_rate:.1f}%) - check error logs")
        
        logger.info(f"Rate limiter status requested by user {current_user.id}: {status}")
        
        return {
            "status": "success",
            "data": response
        }
        
    except Exception as e:
        logger.error(f"Error getting rate limiter status: {e}")
        return {
            "status": "error",
            "message": f"Failed to get rate limiter status: {str(e)}"
        }


@router.post("/rate-limiter/reset")
async def reset_rate_limiter(current_user: CurrentUser):
    """
    Reset the rate limiter counters (admin function).
    
    Note: This should only be used in development or emergency situations.
    """
    try:
        from app.services.global_rate_limiter import global_rate_limiter
        
        # Reset the counters
        with global_rate_limiter.lock:
            global_rate_limiter.tokens_used = 0
            global_rate_limiter.requests_made = 0
            global_rate_limiter.token_window_start = global_rate_limiter.request_window_start = __import__('time').time()
        
        logger.warning(f"Rate limiter reset by user {current_user.id}")
        
        return {
            "status": "success",
            "message": "Rate limiter counters have been reset"
        }
        
    except Exception as e:
        logger.error(f"Error resetting rate limiter: {e}")
        return {
            "status": "error",
            "message": f"Failed to reset rate limiter: {str(e)}"
        }