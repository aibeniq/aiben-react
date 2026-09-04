#!/usr/bin/env python3
"""
Fix stuck progress task by manually completing the upload stage.
"""

import json
import redis

def fix_stuck_progress():
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    task_id = "280048d1-e880-44f4-bdf7-a827b2cdbfcb"
    key = f"progress:{task_id}"
    
    # Get current progress data
    progress_data = r.get(key)
    if not progress_data:
        print(f"❌ No progress data found for task {task_id}")
        return
    
    # Parse JSON
    progress = json.loads(progress_data)
    
    print("📊 Current progress status:")
    print(f"   Task ID: {task_id}")
    print(f"   Status: {progress['status']}")
    print(f"   Percentage: {progress['percentage']}")
    
    # Show current stage status
    print("\n📋 Stage Status:")
    for stage_name, stage_data in progress['stages'].items():
        status = "✅" if stage_data['completed'] else "❌"
        print(f"   {status} {stage_name}: {stage_data['current']}/{stage_data['total']} - {stage_data['message']}")
    
    # Fix the upload stage
    upload_stage = progress['stages']['upload']
    if not upload_stage['completed']:
        print(f"\n🔧 Fixing upload stage...")
        upload_stage['current'] = upload_stage['total']  # Mark as fully uploaded
        upload_stage['completed'] = True
        upload_stage['message'] = "Upload completed successfully"
        
        # Recalculate percentage
        total_weight = 0.0
        completed_weight = 0.0
        
        for stage in progress['stages'].values():
            total_weight += stage['weight']
            if stage['completed']:
                completed_weight += stage['weight']
            else:
                completed_weight += stage['weight'] * (stage['current'] / stage['total'] if stage['total'] > 0 else 0)
        
        new_percentage = (completed_weight / total_weight * 100) if total_weight > 0 else 0
        progress['percentage'] = new_percentage
        
        # Update overall status
        all_completed = all(stage['completed'] for stage in progress['stages'].values())
        progress['status'] = "completed" if all_completed else "in_progress"
        
        if all_completed:
            progress['message'] = f"{progress['operation']} completed successfully"
        
        # Save back to Redis
        r.set(key, json.dumps(progress))
        
        print(f"✅ Fixed! New percentage: {new_percentage}%")
        print(f"✅ New status: {progress['status']}")
        
        # Verify the fix
        print("\n🔍 Verification - Updated stage status:")
        for stage_name, stage_data in progress['stages'].items():
            status = "✅" if stage_data['completed'] else "❌"
            print(f"   {status} {stage_name}: {stage_data['current']}/{stage_data['total']} - {stage_data['message']}")
            
    else:
        print("✅ Upload stage is already completed.")

if __name__ == "__main__":
    fix_stuck_progress()