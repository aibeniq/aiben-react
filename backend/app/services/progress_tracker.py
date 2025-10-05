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
class ProgressStage:
    """Individual stage of a multi-stage operation"""
    name: str
    weight: float  # Relative weight (0.0 to 1.0) of this stage in overall progress
    current: int = 0
    total: int = 1
    message: str = ""
    completed: bool = False

    @property
    def percentage(self) -> float:
        return (self.current / self.total * 100) if self.total > 0 else 0


@dataclass
class ProgressData:
    """Data structure for tracking progress of multi-stage operations"""
    task_id: str
    operation: str
    stages: Dict[str, ProgressStage]
    current_stage: str
    percentage: float
    status: str  # 'started', 'in_progress', 'completed', 'failed'
    message: str
    created_at: str
    updated_at: str
    error_message: Optional[str] = None

    def calculate_overall_percentage(self) -> float:
        """Calculate overall percentage based on weighted stages"""
        total_weight = 0.0
        completed_weight = 0.0
        
        for stage in self.stages.values():
            total_weight += stage.weight
            if stage.completed:
                completed_weight += stage.weight
            else:
                # Add partial progress for current stage
                completed_weight += stage.weight * (stage.current / stage.total if stage.total > 0 else 0)
        
        return (completed_weight / total_weight * 100) if total_weight > 0 else 0


class ProgressTracker:
    """
    Redis-backed progress tracker for long-running operations like knowledge base creation.
    """
    
    def __init__(self):
        # Use the existing session manager's Redis connection
        self.session_manager = session_manager
        self.prefix = "progress:"
        self.default_ttl = 3600  # 1 hour TTL for progress data
    
    def create_task(self, operation: str, stages: Dict[str, float]) -> str:
        """
        Create a new multi-stage progress tracking task.
        
        Args:
            operation: Description of the operation (e.g., "Creating knowledge base")
            stages: Dictionary mapping stage names to their relative weights
                   e.g., {"upload": 0.1, "processing": 0.3, "chunking": 0.2, "embedding": 0.3, "storing": 0.1}
            
        Returns:
            task_id: Unique identifier for this task
        """
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create ProgressStage objects for each stage
        progress_stages = {}
        for stage_name, weight in stages.items():
            progress_stages[stage_name] = ProgressStage(
                name=stage_name,
                weight=weight,
                message=f"Waiting to start {stage_name}..."
            )
        
        first_stage = list(stages.keys())[0] if stages else "unknown"
        
        progress = ProgressData(
            task_id=task_id,
            operation=operation,
            stages=progress_stages,
            current_stage=first_stage,
            percentage=0.0,
            status="started",
            message=f"Starting {operation.lower()}...",
            created_at=now,
            updated_at=now
        )
        
        self._save_progress(task_id, progress)
        return task_id
    
    def update_stage_progress(self, task_id: str, stage_name: str, current: int, total: int = None, message: str = "") -> bool:
        """
        Update progress for a specific stage of a task.
        
        Args:
            task_id: The task identifier
            stage_name: Name of the stage to update
            current: Current number of items processed in this stage
            total: Total number of items in this stage (if different from current)
            message: Optional status message for this stage
            
        Returns:
            Success status
        """
        progress = self._load_progress(task_id)
        if not progress:
            return False
        
        if stage_name not in progress.stages:
            return False
        
        stage = progress.stages[stage_name]
        stage.current = current
        if total is not None:
            stage.total = total
        
        if message:
            stage.message = message
        
        # Mark stage as completed if current >= total
        stage.completed = stage.current >= stage.total
        
        # Update current stage
        progress.current_stage = stage_name
        
        # Recalculate overall percentage
        progress.percentage = progress.calculate_overall_percentage()
        
        # Update overall status
        all_completed = all(stage.completed for stage in progress.stages.values())
        progress.status = "completed" if all_completed else "in_progress"
        
        # Update overall message
        if message:
            progress.message = message
        elif all_completed:
            progress.message = f"{progress.operation} completed successfully"
        else:
            # Use the stage's custom message if available, otherwise show clean progress
            current_stage_obj = progress.stages.get(stage_name)
            if current_stage_obj and current_stage_obj.message:
                progress.message = current_stage_obj.message
            else:
                stage_percentage = (current_stage_obj.current / current_stage_obj.total * 100) if current_stage_obj and current_stage_obj.total > 0 else 0
                progress.message = f"{stage_name}: {stage_percentage:.1f}% complete"
        
        progress.updated_at = datetime.now().isoformat()
        
        return self._save_progress(task_id, progress)

    def complete_stage(self, task_id: str, stage_name: str, message: str = "") -> bool:
        """
        Mark a stage as completed.
        
        Args:
            task_id: The task identifier
            stage_name: Name of the stage to complete
            message: Optional completion message
            
        Returns:
            Success status
        """
        progress = self._load_progress(task_id)
        if not progress or stage_name not in progress.stages:
            return False
        
        stage = progress.stages[stage_name]
        stage.current = stage.total
        stage.completed = True
        if message:
            stage.message = message
        else:
            stage.message = f"{stage_name.title()} completed"
        
        # Update overall progress
        progress.percentage = progress.calculate_overall_percentage()
        all_completed = all(stage.completed for stage in progress.stages.values())
        progress.status = "completed" if all_completed else "in_progress"
        
        # Debug logging for completion status
        if all_completed:
            print(f"🎉 All stages completed for task {task_id}! Setting status to 'completed'")
            progress.message = f"{progress.operation} completed successfully"
        else:
            incomplete_stages = [name for name, stage in progress.stages.items() if not stage.completed]
            print(f"📊 Task {task_id}: Completed stage '{stage_name}', but still incomplete: {incomplete_stages}")
            progress.message = stage.message
        
        progress.updated_at = datetime.now().isoformat()
        
        return self._save_progress(task_id, progress)

    def update_progress(self, task_id: str, current: int, message: str = "") -> bool:
        """
        Legacy method for backwards compatibility.
        Updates the current stage's progress.
        """
        progress = self._load_progress(task_id)
        if not progress:
            return False
        
        current_stage = progress.current_stage
        if current_stage in progress.stages:
            return self.update_stage_progress(task_id, current_stage, current, message=message)
        
        return False
    
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
        if not progress:
            return None
        
        # Convert to dictionary with proper serialization
        result = asdict(progress)
        result["stages"] = {
            name: asdict(stage) for name, stage in progress.stages.items()
        }
        return result
    
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
                # Custom serialization to handle ProgressStage objects
                progress_dict = asdict(progress)
                # Convert ProgressStage objects to dicts manually since they contain nested dataclasses
                progress_dict["stages"] = {
                    name: asdict(stage) for name, stage in progress.stages.items()
                }
                
                self.session_manager.redis_client.setex(
                    f"{self.prefix}{task_id}",
                    self.default_ttl,
                    json.dumps(progress_dict)
                )
                return True
            except Exception as e:
                print(f"ProgressTracker Redis save error: {e}")
                return False
        else:
            # Use session manager's in-memory fallback
            progress_dict = asdict(progress)
            progress_dict["stages"] = {
                name: asdict(stage) for name, stage in progress.stages.items()
            }
            return self.session_manager.set_session(f"{self.prefix}{task_id}", progress_dict)
    
    def _load_progress(self, task_id: str) -> Optional[ProgressData]:
        """Load progress data from storage"""
        if self.session_manager.use_redis:
            try:
                data = self.session_manager.redis_client.get(f"{self.prefix}{task_id}")
                if data:
                    progress_dict = json.loads(data)
                    # Reconstruct ProgressStage objects from dicts
                    stages = {}
                    for name, stage_dict in progress_dict.get("stages", {}).items():
                        stages[name] = ProgressStage(**stage_dict)
                    progress_dict["stages"] = stages
                    return ProgressData(**progress_dict)
                return None
            except Exception as e:
                print(f"ProgressTracker Redis load error: {e}")
                return None
        else:
            # Use session manager's in-memory fallback
            data = self.session_manager.get_session(f"{self.prefix}{task_id}")
            if data:
                # Reconstruct ProgressStage objects from dicts
                stages = {}
                for name, stage_dict in data.get("stages", {}).items():
                    stages[name] = ProgressStage(**stage_dict)
                data["stages"] = stages
                return ProgressData(**data)
            return None


# Global progress tracker instance
progress_tracker = ProgressTracker()