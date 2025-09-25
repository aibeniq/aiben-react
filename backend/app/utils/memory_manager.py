"""
Memory management utilities for handling large data operations.
"""
import os
import gc
import tempfile
import zipfile
import psutil
import logging
from fastapi import HTTPException
from typing import Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """Utility class for managing memory during intensive operations."""
    
    @staticmethod
    def get_memory_info():
        """Get comprehensive memory information."""
        process = psutil.Process()
        system_memory = psutil.virtual_memory()
        
        return {
            'process_memory_mb': process.memory_info().rss / 1024 / 1024,
            'system_memory_percent': system_memory.percent,
            'system_available_mb': system_memory.available / 1024 / 1024,
            'system_total_mb': system_memory.total / 1024 / 1024
        }
    
    @staticmethod
    def log_memory_usage(stage: str, force_gc: bool = False):
        """Log memory usage at different stages with optional cleanup."""
        memory_info = MemoryManager.get_memory_info()
        
        logger.info(
            f"Memory usage at {stage}: "
            f"{memory_info['process_memory_mb']:.1f}MB process, "
            f"{memory_info['system_memory_percent']:.1f}% system "
            f"({memory_info['system_available_mb']:.0f}MB available)"
        )
        
        if force_gc or memory_info['system_memory_percent'] > 75:
            if memory_info['system_memory_percent'] > 75:
                logger.warning("High memory usage detected, forcing garbage collection...")
            gc.collect()
            
        return memory_info
    
    @staticmethod
    def check_memory_availability(min_available_mb: int = 500, max_usage_percent: float = 85):
        """Check if sufficient memory is available for operations."""
        memory_info = MemoryManager.get_memory_info()
        
        if (memory_info['system_memory_percent'] > max_usage_percent or 
            memory_info['system_available_mb'] < min_available_mb):
            raise HTTPException(
                status_code=507,
                detail=(
                    f"Insufficient memory available: "
                    f"{memory_info['system_memory_percent']:.1f}% used "
                    f"({memory_info['system_available_mb']:.0f}MB available). "
                    f"Please try again later or upgrade your instance."
                )
            )
        return memory_info
    
    @staticmethod
    def create_streaming_zip_from_directory(source_dir: str, output_path: Optional[str] = None, compression_level: int = 6):
        """Create ZIP file using streaming to avoid loading entire ZIP into memory."""
        if output_path is None:
            temp_fd, output_path = tempfile.mkstemp(suffix=".zip")
            os.close(temp_fd)
        
        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zip_file:
                for root, _, filenames in os.walk(source_dir):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.relpath(file_path, source_dir)
                        zip_file.write(file_path, arcname)
            
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            logger.info(f"Created streaming ZIP file: {output_path} ({size_mb:.1f}MB)")
            
            return output_path, size_mb
            
        except Exception as e:
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up ZIP file on error: {cleanup_error}")
            raise e

    @staticmethod
    def cleanup_temp_file(file_path: str, log_success: bool = True):
        """Safely clean up a temporary file."""
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
                if log_success:
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up temporary file {file_path}: {e}")

    @staticmethod
    def store_large_file(temp_file_path: str, kb_id: str, storage_base_path: str) -> str:
        """
        Move a temporary file to persistent storage for a knowledge base.
        
        Args:
            temp_file_path: Path to the temporary file
            kb_id: Knowledge base ID for organizing storage
            storage_base_path: Base directory for file storage
            
        Returns:
            Path to the stored file
        """
        # Ensure storage directory exists
        os.makedirs(storage_base_path, exist_ok=True)
        
        # Create a subdirectory for this knowledge base
        kb_storage_dir = os.path.join(storage_base_path, kb_id)
        os.makedirs(kb_storage_dir, exist_ok=True)
        
        # Generate the final file path
        file_extension = os.path.splitext(temp_file_path)[1] or '.zip'
        stored_file_path = os.path.join(kb_storage_dir, f"data{file_extension}")
        
        try:
            # Move the file to persistent storage
            import shutil
            shutil.move(temp_file_path, stored_file_path)
            
            file_size_mb = os.path.getsize(stored_file_path) / 1024 / 1024
            logger.info(f"Stored large file for KB {kb_id}: {stored_file_path} ({file_size_mb:.1f}MB)")
            
            return stored_file_path
            
        except Exception as e:
            logger.error(f"Failed to store large file for KB {kb_id}: {e}")
            # Clean up the temp file if it still exists
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
            raise e

    @staticmethod
    def cleanup_stored_file(file_path: str):
        """
        Clean up a stored file and its directory if empty.
        
        Args:
            file_path: Path to the stored file to clean up
        """
        if not file_path or not os.path.exists(file_path):
            return
            
        try:
            # Remove the file
            os.unlink(file_path)
            logger.info(f"Cleaned up stored file: {file_path}")
            
            # Try to remove the parent directory if it's empty
            parent_dir = os.path.dirname(file_path)
            try:
                os.rmdir(parent_dir)
                logger.info(f"Removed empty storage directory: {parent_dir}")
            except OSError:
                # Directory not empty or other OS error, that's fine
                pass
                
        except Exception as e:
            logger.warning(f"Could not clean up stored file {file_path}: {e}")

# Convenience functions for backward compatibility
def log_memory_usage(stage: str, force_gc: bool = False):
    """Convenience function for logging memory usage."""
    return MemoryManager.log_memory_usage(stage, force_gc)

def check_memory_availability(min_available_mb: int = 500, max_usage_percent: float = 85):
    """Convenience function for checking memory availability."""
    return MemoryManager.check_memory_availability(min_available_mb, max_usage_percent)

def create_streaming_zip_from_directory(source_dir: str, output_path: Optional[str] = None):
    """Convenience function for creating streaming ZIP files."""
    return MemoryManager.create_streaming_zip_from_directory(source_dir, output_path)

def store_large_file(temp_file_path: str, kb_id: str, storage_base_path: str) -> str:
    """Convenience function for storing large files."""
    return MemoryManager.store_large_file(temp_file_path, kb_id, storage_base_path)

def cleanup_stored_file(file_path: str):
    """Convenience function for cleaning up stored files."""
    return MemoryManager.cleanup_stored_file(file_path)
