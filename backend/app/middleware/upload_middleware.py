import logging
import time
import asyncio
from fastapi import Request, Response
from starlette.types import ASGIApp, Scope, Receive, Send
from typing import Callable
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class UploadProgressMiddleware:
    """
    ASGI Middleware to monitor file upload progress in real-time.
    Logs progress for knowledge base uploads as data is being received.
    Integrates with progress tracker service to update Redis-based progress.
    """
    
    def __init__(self, app: ASGIApp):
        print("UPLOAD MIDDLEWARE INIT", flush=True)
        self.app = app
        self.progress_tracker = None

    def _get_progress_tracker(self):
        """Lazy initialization of progress tracker to avoid import cycles"""
        if self.progress_tracker is None:
            from app.services.progress_tracker import progress_tracker
            self.progress_tracker = progress_tracker
        return self.progress_tracker

    def _extract_task_id_from_query(self, query_string: str) -> str:
        """Extract task_id from query string"""
        try:
            query_params = parse_qs(query_string)
            task_id = query_params.get('task_id', [None])[0]
            logger.info(f"🔍 TASK ID EXTRACTION: Found task_id={task_id} in query string")
            return task_id
        except Exception as e:
            logger.warning(f"⚠️ Could not extract task_id from query string: {e}")
            return None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        import sys
        # Reduced logging - don't log every request dispatch
        # print("DISPATCH START", flush=True)
        # sys.stdout.flush()
        
        # Only handle HTTP requests
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Extract request details from scope
        method = scope.get("method", "")
        path = scope.get("path", "")
        headers = dict(scope.get("headers", []))
        content_type = headers.get(b"content-type", b"").decode("latin-1", errors="ignore")
        query_string = scope.get("query_string", b"").decode("latin-1", errors="ignore")
        
        # Reduced logging - don't log every request
        # print(f"🔍 REQUEST: {method} {path}", flush=True)
        # print(f"🔍 CONTENT-TYPE: '{content_type}'", flush=True)
        
        # Check individual conditions
        is_post = method == "POST"
        has_kb_in_url = "knowledge-bases" in path
        is_multipart = content_type.startswith("multipart/form-data")
        
        # Reduced logging - don't log conditions for every request
        # print(f"🔍 CONDITIONS: POST={is_post}, KB_URL={has_kb_in_url}, MULTIPART={is_multipart}", flush=True)
        
        # Only monitor knowledge base uploads - skip all other requests immediately
        if not (is_post and has_kb_in_url and is_multipart):
            # Reduced logging - don't log every skipped request
            # print(f"⏭️ SKIPPING MIDDLEWARE: Not a KB upload request", flush=True)
            return await self.app(scope, receive, send)
        
        # Only log and process for actual upload requests
        # Reduced logging - only log activation once, not duplicate messages
        # print(f"✅ MIDDLEWARE ACTIVATED: Processing knowledge base upload", flush=True)
        # logger.error("MIDDLEWARE CALLED")
        # logger.error(f"🔍 MIDDLEWARE CHECK: {method} {path}")
        # logger.error(f"🔍 Content-Type: '{content_type}'")
        
        # print(f"✅ MIDDLEWARE ACTIVATED: Processing knowledge base upload", flush=True)
        logger.info(f"✅ MIDDLEWARE ACTIVATED: Processing knowledge base upload")
        
        # Get content length
        content_length_header = headers.get(b"content-length", b"")
        content_length = int(content_length_header) if content_length_header else None
        
        task_id = self._extract_task_id_from_query(query_string)
        
        if content_length and content_length > 1024:  # Log for uploads > 1KB (basically all uploads)
            size_mb = content_length / 1024 / 1024
            start_time = time.time()
            
            logger.info(f"🚀 UPLOAD START: {size_mb:.2f}MB knowledge base upload beginning")
            logger.info(f"🚀 UPLOAD START: Path: {path}")
            if task_id:
                logger.info(f"🚀 UPLOAD START: Task ID: {task_id}")
                try:
                    tracker = self._get_progress_tracker()
                    
                    # Don't translate server-side, let frontend handle translation
                    # Just store the key and parameters for frontend translation
                    success = tracker.update_stage_progress(
                        task_id, 
                        "upload", 
                        current=0,
                        total=100,
                        message_key="knowledgeBases.progress.uploading",
                        message_params={"current": "0.00", "total": f"{size_mb:.2f}"},
                        message=f"Uploading 0.00 MB of {size_mb:.2f} MB..."  # Fallback for old clients
                    )
                    if success:
                        logger.info(f"📊 PROGRESS TRACKER INITIAL UPDATE: {task_id} upload started")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send initial progress update: {e}")
            else:
                logger.warning(f"⚠️ UPLOAD START: No task_id found in query: {query_string}")
            
            # Wrap the receive callable for monitoring
            monitored_receive = self._create_monitored_receive(
                receive, size_mb, start_time, task_id, content_length
            )
            
            # Process the request with monitoring
            return await self.app(scope, monitored_receive, send)
        elif content_length is None and path.startswith("/api/v1/knowledge-bases/") and "multipart" in content_type:
            # Fallback for chunked uploads (no Content-Length)
            logger.warning("⚠️ CHUNKED UPLOAD DETECTED: No Content-Length, enabling basic progress tracking")
            start_time = time.time()
            # Set a placeholder total (will be updated as bytes are received)
            if task_id:
                try:
                    tracker = self._get_progress_tracker()
                    success = tracker.update_stage_progress(
                        task_id, 
                        "upload", 
                        current=0,
                        total=100,  # Use percentage-based tracking
                        message_key="knowledgeBases.progress.uploading",
                        message_params={"current": "0.00", "total": "Unknown"},
                        message="Uploading (chunked transfer)..."
                    )
                    if success:
                        logger.info(f"📊 PROGRESS TRACKER INITIAL UPDATE: {task_id} chunked upload started")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send initial progress update for chunked upload: {e}")
            else:
                logger.warning(f"⚠️ CHUNKED UPLOAD: No task_id found in query: {query_string}")
            
            # Wrap receive for basic tracking
            monitored_receive = self._create_monitored_receive(
                receive, 0, start_time, task_id, None  # Pass None for total_size_bytes
            )
            return await self.app(scope, monitored_receive, send)
        else:
            logger.info(f"ℹ️ SMALL UPLOAD: {content_length or 0} bytes, skipping monitoring")
        
        # For non-upload requests, process normally
        return await self.app(scope, receive, send)
    
    def _create_monitored_receive(self, original_receive: Receive, total_size_mb: float, start_time: float, task_id: str = None, total_size_bytes: int = None):
        """Create a monitored receive callable that wraps the original receive"""
        
        logger.info(f"🔧 SETTING UP MONITORING: task_id={task_id}, total_size_mb={total_size_mb}, total_size_bytes={total_size_bytes}")
        
        bytes_received = 0
        last_log_time = start_time
        last_log_bytes = 0
        is_chunked = total_size_bytes is None
        
        async def monitored_receive():
            nonlocal bytes_received, last_log_time, last_log_bytes
            
            # Reduced logging - don't log every receive call
            # logger.info(f"📡 MONITOR RECEIVE CALLED: bytes_received={bytes_received}")
            
            message = await original_receive()
            
            if message["type"] == "http.request":
                body = message.get("body", b"")
                bytes_received += len(body)
                
                current_time = time.time()
                
                # Log progress every 1MB or every 5 seconds, whichever comes first
                if (bytes_received - last_log_bytes >= 1 * 1024 * 1024 or 
                    current_time - last_log_time >= 5.0 or
                    (not message.get("more_body", True) and bytes_received > 0)):  # Always log at completion
                    
                    elapsed = current_time - start_time
                    speed = (bytes_received / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    
                    if is_chunked:
                        # For chunked uploads, show received bytes without total
                        received_mb = bytes_received / 1024 / 1024
                        # Reduced logging - don't log every progress update for chunked uploads
                        # logger.debug(
                        #     f"📊 CHUNKED UPLOAD PROGRESS: {received_mb:.1f}MB received "
                        #     f"at {speed:.1f} MB/s"
                        # )
                        
                        # Update progress tracker if task_id is available
                        if task_id:
                            try:
                                # Reduced logging - don't log every progress update attempt
                                # logger.debug(f"📊 ATTEMPTING PROGRESS UPDATE: task_id={task_id}, received={received_mb:.1f}MB")
                                tracker = self._get_progress_tracker()
                                
                                # For chunked uploads, we can't calculate percentage, so use a placeholder
                                success = tracker.update_stage_progress(
                                    task_id, 
                                    "upload", 
                                    current=int(received_mb),  # Use MB received as current
                                    total=1000,  # Arbitrary large number
                                    message_key="knowledgeBases.progress.uploading",
                                    message_params={"current": f"{received_mb:.2f}", "total": "Unknown"},
                                    message=f"Uploading {received_mb:.2f} MB..."  # Fallback for old clients
                                )
                                # Reduced logging - don't log every successful update
                                # if success:
                                #     logger.debug(f"📊 PROGRESS TRACKER UPDATED: {task_id} chunked upload at {received_mb:.1f}MB")
                                # else:
                                #     logger.warning(f"⚠️ PROGRESS TRACKER UPDATE FAILED: {task_id}")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to update progress tracker: {e}")
                        # else:
                        #     logger.warning(f"⚠️ NO TASK_ID FOR PROGRESS UPDATE: task_id is None")
                    else:
                        # Original logic for uploads with known size
                        progress = (bytes_received / total_size_bytes * 100) if total_size_bytes > 0 else 0
                        
                        # Reduced logging - don't log every progress update
                        # logger.debug(
                        #     f"📊 UPLOAD PROGRESS: {bytes_received/1024/1024:.1f}MB / "
                        #     f"{total_size_mb:.1f}MB ({progress:.1f}%) "
                        #     f"at {speed:.1f} MB/s"
                        # )
                        
                        # Update progress tracker if task_id is available
                        if task_id:
                            try:
                                # Reduced logging - don't log every progress update attempt
                                # logger.debug(f"📊 ATTEMPTING PROGRESS UPDATE: task_id={task_id}, progress={progress:.1f}%")
                                tracker = self._get_progress_tracker()
                                
                                # Calculate progress within the upload stage
                                upload_progress_percentage = min(progress, 100.0)  # Cap at 100%
                                
                                # Create clean upload message with parameters for frontend translation
                                received_mb = bytes_received / 1024 / 1024
                                total_mb = total_size_mb
                                
                                # Convert percentage to current/total format (e.g., 50% -> 50/100)
                                current_value = int(upload_progress_percentage)
                                total_value = 100
                                
                                # Reduced logging - don't log progress update details
                                # logger.debug(f"📊 UPDATING PROGRESS: current={current_value}, total={total_value}, params=current:{received_mb:.2f}MB, total:{total_mb:.2f}MB")
                                
                                success = tracker.update_stage_progress(
                                    task_id, 
                                    "upload", 
                                    current=current_value,
                                    total=total_value,
                                    message_key="knowledgeBases.progress.uploading",
                                    message_params={"current": f"{received_mb:.2f}", "total": f"{total_mb:.2f}"},
                                    message=f"Uploading {received_mb:.2f} MB of {total_mb:.2f} MB..."  # Fallback for old clients
                                )
                                # Reduced logging - don't log every successful update
                                # if success:
                                #     logger.debug(f"📊 PROGRESS TRACKER UPDATED: {task_id} upload stage at {upload_progress_percentage:.1f}%")
                                # else:
                                #     logger.warning(f"⚠️ PROGRESS TRACKER UPDATE FAILED: {task_id}")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to update progress tracker: {e}")
                        # else:
                        #     logger.warning(f"⚠️ NO TASK_ID FOR PROGRESS UPDATE: task_id is None")
                    
                    last_log_time = current_time
                    last_log_bytes = bytes_received
                
                # Log when upload is complete (no more body data)
                if message.get("more_body", True) == False and bytes_received > 0:
                    elapsed = current_time - start_time
                    avg_speed = (bytes_received / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    if is_chunked:
                        logger.info(
                            f"📦 CHUNKED UPLOAD RECEIVED: {bytes_received/1024/1024:.2f}MB "
                            f"fully received in {elapsed:.2f}s (avg: {avg_speed:.1f} MB/s)"
                        )
                    else:
                        logger.info(
                            f"📦 UPLOAD RECEIVED: {bytes_received/1024/1024:.2f}MB "
                            f"fully received in {elapsed:.2f}s (avg: {avg_speed:.1f} MB/s)"
                        )
                    
                    # Mark upload stage as complete in progress tracker
                    if task_id:
                        try:
                            tracker = self._get_progress_tracker()
                            
                            if is_chunked:
                                received_mb = bytes_received / 1024 / 1024
                                success = tracker.complete_stage(
                                    task_id, 
                                    "upload", 
                                    message_key="knowledgeBases.progress.uploading",
                                    message_params={"current": f"{received_mb:.2f}", "total": f"{received_mb:.2f}"},
                                    message=f"Uploading {received_mb:.2f} MB of {received_mb:.2f} MB..."  # Fallback for old clients
                                )
                            else:
                                success = tracker.complete_stage(
                                    task_id, 
                                    "upload", 
                                    message_key="knowledgeBases.progress.uploading",
                                    message_params={"current": f"{total_size_mb:.2f}", "total": f"{total_size_mb:.2f}"},
                                    message=f"Uploading {total_size_mb:.2f} MB of {total_size_mb:.2f} MB..."  # Fallback for old clients
                                )
                            if success:
                                logger.info(f"✅ UPLOAD COMPLETE: Progress tracker updated for task {task_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to mark upload complete in progress tracker: {e}")
            
            return message
        
        # Reduced logging - don't log every time monitoring is set up
        # logger.info(f"✅ RECEIVE WRAPPED: task_id={task_id}, monitoring active, chunked={is_chunked}")
        return monitored_receive