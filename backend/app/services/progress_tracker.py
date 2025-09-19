"""
Progress tracking service with Redis backend for knowledge base creation progress.
Allows frontend to poll for progress updates during long-running operations.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, asdict

from .session_manager import session_manager


@dataclass
class ProgressData:
    """Data structure for tracking progress of long-running operations"""
    task_id: str
    operation: str
    current: int
    total: int
    percentage: float
    status: str  # 'started', 'in_progress', 'completed', 'failed'
    message: str
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


class ProgressTracker:
    """
    Redis-backed progress tracker for long-running operations like knowledge base creation.
    """
    
    def __init__(self):
        # Use the existing session manager's Redis connection
        self.session_manager = session_manager
        self.prefix = "progress:"
        self.default_ttl = 3600  # 1 hour TTL for progress data
    
    def create_task(self, operation: str, total: int) -> str:
        """
        Create a new progress tracking task.
        
        Args:
            operation: Description of the operation (e.g., "Creating knowledge base")
            total: Total number of items to process
            
        Returns:
            task_id: Unique identifier for this task
        """
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        progress = ProgressData(
            task_id=task_id,
            operation=operation,
            current=0,
            total=total,
            percentage=0.0,
            status="started",
            message=f"Starting {operation.lower()}...",
            created_at=now,
            updated_at=now
        )
        
        self._save_progress(task_id, progress)
        return task_id
    
    def update_progress(self, task_id: str, current: int, message: str = "") -> bool:
        """
        Update progress for a task.
        
        Args:
            task_id: The task identifier
            current: Current number of items processed
            message: Optional status message
            
        Returns:
            Success status
        """
        progress = self._load_progress(task_id)
        if not progress:
            return False
        
        progress.current = current
        progress.percentage = (current / progress.total * 100) if progress.total > 0 else 0
        progress.status = "completed" if current >= progress.total else "in_progress"
        progress.updated_at = datetime.now().isoformat()
        
        if message:
            progress.message = message
        elif progress.status == "completed":
            progress.message = f"{progress.operation} completed successfully"
        else:
            progress.message = f"{progress.operation}: {current}/{progress.total} ({progress.percentage:.1f}%)"
        
        return self._save_progress(task_id, progress)
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: The task identifier
            error_message: Error description
            
        Returns:
            Success status
        """
        progress = self._load_progress(task_id)
        if not progress:
            return False
        
        progress.status = "failed"
        progress.error_message = error_message
        progress.message = f"{progress.operation} failed: {error_message}"
        progress.updated_at = datetime.now().isoformat()
        
        return self._save_progress(task_id, progress)
    
    def get_progress(self, task_id: str) -> Optional[Dict]:
        """
        Get current progress for a task.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Progress data as dictionary or None if not found
        """
        progress = self._load_progress(task_id)
        return asdict(progress) if progress else None
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete progress data for a task.
        
        Args:
            task_id: The task identifier
            
        Returns:
            Success status
        """
        if self.session_manager.use_redis:
            try:
                self.session_manager.redis_client.delete(f"{self.prefix}{task_id}")
                return True
            except Exception as e:
                print(f"ProgressTracker Redis delete error: {e}")
                return False
        else:
            # Use session manager's in-memory fallback
            return self.session_manager.delete_session(f"{self.prefix}{task_id}")
    
    def _save_progress(self, task_id: str, progress: ProgressData) -> bool:
        """Save progress data to storage"""
        if self.session_manager.use_redis:
            try:
                self.session_manager.redis_client.setex(
                    f"{self.prefix}{task_id}",
                    self.default_ttl,
                    json.dumps(asdict(progress))
                )
                return True
            except Exception as e:
                print(f"ProgressTracker Redis save error: {e}")
                return False
        else:
            # Use session manager's in-memory fallback
            return self.session_manager.set_session(f"{self.prefix}{task_id}", asdict(progress))
    
    def _load_progress(self, task_id: str) -> Optional[ProgressData]:
        """Load progress data from storage"""
        if self.session_manager.use_redis:
            try:
                data = self.session_manager.redis_client.get(f"{self.prefix}{task_id}")
                if data:
                    progress_dict = json.loads(data)
                    return ProgressData(**progress_dict)
                return None
            except Exception as e:
                print(f"ProgressTracker Redis load error: {e}")
                return None
        else:
            # Use session manager's in-memory fallback
            data = self.session_manager.get_session(f"{self.prefix}{task_id}")
            return ProgressData(**data) if data else None


# Global progress tracker instance
progress_tracker = ProgressTracker()