#!/usr/bin/env python3
"""
Test script to verify that the Knowledge Base progress tracking fix works correctly.
This simulates the stages of Knowledge Base creation to ensure 100% completion.
"""

import sys
import os
sys.path.append('/home/ec2-user/aiben-react/backend')

from app.services.progress_tracker import progress_tracker

def test_progress_stages():
    """Test that progress tracking works correctly through all stages."""
    print("🧪 Testing Knowledge Base progress tracking fix...")
    
    # Create a test task with the same weights as the real KB creation
    stages = {
        "upload": 0.20,      # 20% - File upload and validation
        "processing": 0.20,  # 20% - File processing and text extraction
        "chunking": 0.20,    # 20% - Document splitting and chunking
        "embedding": 0.20,   # 20% - Creating embeddings
        "storing": 0.17,     # 17% - Compressing and storing in database
        "finalizing": 0.03   # 3% - Creating source entries and cleanup
    }
    
    task_id = progress_tracker.create_task("Test Knowledge Base Creation", stages)
    print(f"✅ Created test task: {task_id}")
    
    # Simulate progress through each stage
    file_count = 3
    
    # 1. Upload stage with progress
    print("\n📤 Testing upload stage...")
    for i in range(file_count):
        progress_tracker.update_stage_progress(
            task_id, "upload", i, file_count, 
            f"Reading file {i + 1}/{file_count}"
        )
    progress_tracker.complete_stage(task_id, "upload", f"All {file_count} files uploaded successfully")
    
    # Check progress after upload
    progress = progress_tracker.get_progress(task_id)
    print(f"After upload: {progress['percentage']:.1f}% - Status: {progress['status']}")
    
    # 2. Processing stage
    print("\n⚙️ Testing processing stage...")
    progress_tracker.update_stage_progress(task_id, "processing", 0, file_count * 2, "Starting file processing...")
    for i in range(file_count * 2):
        progress_tracker.update_stage_progress(
            task_id, "processing", i + 1, file_count * 2, 
            f"Processing step {i + 1}/{file_count * 2}"
        )
    progress_tracker.complete_stage(task_id, "processing", "File processing completed successfully")
    
    progress = progress_tracker.get_progress(task_id)
    print(f"After processing: {progress['percentage']:.1f}% - Status: {progress['status']}")
    
    # 3. Chunking stage
    print("\n✂️ Testing chunking stage...")
    progress_tracker.update_stage_progress(task_id, "chunking", 0, 1, "Starting document chunking...")
    progress_tracker.complete_stage(task_id, "chunking", "Document chunking completed: 150 chunks created")
    
    progress = progress_tracker.get_progress(task_id)
    print(f"After chunking: {progress['percentage']:.1f}% - Status: {progress['status']}")
    
    # 4. Embedding stage
    print("\n🧠 Testing embedding stage...")
    chunk_count = 5
    progress_tracker.update_stage_progress(task_id, "embedding", 0, chunk_count, "Starting embedding creation...")
    for i in range(chunk_count):
        progress_tracker.update_stage_progress(
            task_id, "embedding", i + 1, chunk_count, 
            f"Creating embeddings for chunk {i + 1}/{chunk_count}"
        )
    progress_tracker.complete_stage(task_id, "embedding", "Vector database created successfully")
    
    progress = progress_tracker.get_progress(task_id)
    print(f"After embedding: {progress['percentage']:.1f}% - Status: {progress['status']}")
    
    # 5. Storing stage
    print("\n💾 Testing storing stage...")
    storing_steps = 3
    for i in range(storing_steps):
        progress_tracker.update_stage_progress(
            task_id, "storing", i, storing_steps, 
            f"Storing step {i + 1}/{storing_steps}"
        )
    progress_tracker.complete_stage(task_id, "storing", "Database stored successfully")
    
    progress = progress_tracker.get_progress(task_id)
    print(f"After storing: {progress['percentage']:.1f}% - Status: {progress['status']}")
    
    # 6. Finalizing stage (this should complete the entire task)
    print("\n🏁 Testing finalizing stage...")
    for i in range(file_count):
        progress_tracker.update_stage_progress(
            task_id, "finalizing", i, file_count, 
            f"Creating source entry {i + 1}/{file_count}"
        )
    print("⏳ Completing finalizing stage...")
    progress_tracker.complete_stage(task_id, "finalizing", "Knowledge base created successfully")
    
    # Final check
    final_progress = progress_tracker.get_progress(task_id)
    print(f"\n🎯 FINAL RESULT:")
    print(f"   Percentage: {final_progress['percentage']:.1f}%")
    print(f"   Status: {final_progress['status']}")
    print(f"   Message: {final_progress['message']}")
    
    # Verify all stages are completed
    all_completed = all(stage['completed'] for stage in final_progress['stages'].values())
    print(f"   All stages completed: {all_completed}")
    
    if final_progress['status'] == 'completed' and final_progress['percentage'] == 100.0:
        print("✅ SUCCESS: Progress tracking works correctly!")
        return True
    else:
        print("❌ FAILURE: Progress tracking still has issues")
        print("Stage details:")
        for name, stage in final_progress['stages'].items():
            print(f"  {name}: {stage['completed']} ({stage['current']}/{stage['total']})")
        return False

if __name__ == "__main__":
    success = test_progress_stages()
    sys.exit(0 if success else 1)
