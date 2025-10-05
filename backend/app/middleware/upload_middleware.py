import logging
import time
import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class UploadProgressMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor file upload progress in real-time.
    Logs progress for knowledge base uploads as data is being received.
    Integrates with progress tracker service to update Redis-based progress.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.progress_tracker = None

    def _get_progress_tracker(self):
        """Lazy initialization of progress tracker to avoid import cycles"""
        if self.progress_tracker is None:
            from app.services.progress_tracker import progress_tracker
            self.progress_tracker = progress_tracker
        return self.progress_tracker

    def _extract_task_id(self, request: Request) -> str:
        """Extract task_id from request URL query parameters"""
        try:
            parsed_url = urlparse(str(request.url))
            query_params = parse_qs(parsed_url.query)
            task_id = query_params.get('task_id', [None])[0]
            logger.info(f"🔍 TASK ID EXTRACTION: Found task_id={task_id} in request URL")
            return task_id
        except Exception as e:
            logger.warning(f"⚠️ Could not extract task_id from URL: {e}")
            return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only monitor knowledge base uploads
        if (
            request.method == "POST" 
            and "knowledge-bases" in str(request.url)
            and request.headers.get("content-type", "").startswith("multipart/form-data")
        ):
            content_length = request.headers.get("content-length")
            task_id = self._extract_task_id(request)
            
            if content_length and int(content_length) > 1024:  # Log for uploads > 1KB (basically all uploads)
                size_mb = int(content_length) / 1024 / 1024
                start_time = time.time()
                
                logger.info(f"🚀 UPLOAD START: {size_mb:.2f}MB knowledge base upload beginning")
                logger.info(f"🚀 UPLOAD START: Client: {request.client.host}")
                logger.info(f"🚀 UPLOAD START: URL: {request.url}")
                if task_id:
                    logger.info(f"🚀 UPLOAD START: Task ID: {task_id}")
                
                # Monitor the upload by wrapping the request receive (restore detailed monitoring)
                request_with_monitoring = self._wrap_request_with_monitoring(
                    request, size_mb, start_time, task_id
                )
                
                # Process the request with monitoring
                response = await call_next(request_with_monitoring)
                
                duration = time.time() - start_time
                speed = size_mb / duration if duration > 0 else 0
                
                logger.info(f"🏁 UPLOAD COMPLETE: {size_mb:.2f}MB in {duration:.2f}s ({speed:.1f} MB/s)")
                
                return response
        
        # For non-upload requests, process normally
        return await call_next(request)
    
    def _wrap_request_with_monitoring(self, request: Request, total_size_mb: float, start_time: float, task_id: str = None):
        """Wrap the request to monitor upload progress"""
        
        original_receive = request.receive
        bytes_received = 0
        last_log_time = start_time
        last_log_bytes = 0
        
        async def monitored_receive():
            nonlocal bytes_received, last_log_time, last_log_bytes
            
            message = await original_receive()
            
            if message["type"] == "http.request":
                body = message.get("body", b"")
                bytes_received += len(body)
                
                current_time = time.time()
                
                # Log progress every 1MB or every 5 seconds, whichever comes first
                if (bytes_received - last_log_bytes >= 1 * 1024 * 1024 or 
                    current_time - last_log_time >= 5.0):
                    
                    elapsed = current_time - start_time
                    speed = (bytes_received / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    progress = (bytes_received / (total_size_mb * 1024 * 1024)) * 100
                    
                    logger.info(
                        f"📊 UPLOAD PROGRESS: {bytes_received/1024/1024:.1f}MB / "
                        f"{total_size_mb:.1f}MB ({progress:.1f}%) "
                        f"at {speed:.1f} MB/s"
                    )
                    
                    # Update progress tracker if task_id is available
                    if task_id:
                        try:
                            tracker = self._get_progress_tracker()
                            # Calculate progress within the upload stage
                            upload_progress_percentage = min(progress, 100.0)  # Cap at 100%
                            
                            # Create clean upload message
                            received_mb = bytes_received / 1024 / 1024
                            total_mb = total_size_mb
                            clean_message = f"Uploading {received_mb:.1f} of {total_mb:.1f}MB"
                            
                            # Convert percentage to current/total format (e.g., 50% -> 50/100)
                            current_value = int(upload_progress_percentage)
                            total_value = 100
                            
                            success = tracker.update_stage_progress(
                                task_id, 
                                "upload", 
                                current=current_value,
                                total=total_value,
                                message=clean_message
                            )
                            if success:
                                logger.info(f"📊 PROGRESS TRACKER UPDATED: {task_id} upload stage at {upload_progress_percentage:.1f}%")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to update progress tracker: {e}")
                    
                    last_log_time = current_time
                    last_log_bytes = bytes_received
                
                # Log when upload is complete (no more body data)
                if message.get("more_body", True) == False and bytes_received > 0:
                    elapsed = current_time - start_time
                    avg_speed = (bytes_received / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"📦 UPLOAD RECEIVED: {bytes_received/1024/1024:.2f}MB "
                        f"fully received in {elapsed:.2f}s (avg: {avg_speed:.1f} MB/s)"
                    )
                    
                    # Mark upload stage as complete in progress tracker
                    if task_id:
                        try:
                            tracker = self._get_progress_tracker()
                            success = tracker.complete_stage(task_id, "upload", "Upload completed successfully")
                            if success:
                                logger.info(f"✅ UPLOAD COMPLETE: Progress tracker updated for task {task_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to mark upload complete in progress tracker: {e}")
            
            return message
        
        # Replace the request's receive method
        request._receive = monitored_receive
        return request