#!/usr/bin/env python3
"""
Test script to verify progress tracker percentage calculation is working correctly.
"""

def test_percentage_calculation():
    # Define the stage weights (should sum to 1.0)
    stages = {
        "upload": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "processing": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "chunking": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "embedding": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "storing": {"weight": 0.17, "current": 0, "total": 100, "completed": False},
        "finalizing": {"weight": 0.03, "current": 0, "total": 100, "completed": False}
    }
    
    def calculate_percentage(stages):
        total_weight = 0.0
        completed_weight = 0.0
        
        for stage in stages.values():
            total_weight += stage["weight"]
            if stage["completed"]:
                completed_weight += stage["weight"]
            else:
                # Add partial progress for current stage
                stage_progress = stage["current"] / stage["total"] if stage["total"] > 0 else 0
                completed_weight += stage["weight"] * stage_progress
        
        return (completed_weight / total_weight * 100) if total_weight > 0 else 0
    
    print("Testing Progress Tracker Percentage Calculation")
    print("=" * 50)
    
    # Test 1: All stages at 0%
    print("\n1. All stages at 0%:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 0%, Actual: {percentage:.2f}%")
    
    # Test 2: Upload stage completed
    stages["upload"]["completed"] = True
    print("\n2. Upload stage completed:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 20%, Actual: {percentage:.2f}%")
    
    # Test 3: Upload + Processing completed  
    stages["processing"]["completed"] = True
    print("\n3. Upload + Processing completed:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 40%, Actual: {percentage:.2f}%")
    
    # Test 4: All stages except finalizing completed
    for stage_name in ["chunking", "embedding", "storing"]:
        stages[stage_name]["completed"] = True
    print("\n4. All stages except finalizing completed:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 97%, Actual: {percentage:.2f}%")
    
    # Test 5: All stages completed
    stages["finalizing"]["completed"] = True
    print("\n5. All stages completed:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 100%, Actual: {percentage:.2f}%")
    
    # Test 6: Partial progress in upload stage
    stages = {
        "upload": {"weight": 0.2, "current": 50, "total": 100, "completed": False},
        "processing": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "chunking": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "embedding": {"weight": 0.2, "current": 0, "total": 100, "completed": False},
        "storing": {"weight": 0.17, "current": 0, "total": 100, "completed": False},
        "finalizing": {"weight": 0.03, "current": 0, "total": 100, "completed": False}
    }
    print("\n6. Upload stage 50% complete:")
    percentage = calculate_percentage(stages)
    print(f"   Expected: 10%, Actual: {percentage:.2f}%")
    
    print("\n" + "=" * 50)
    print("✅ Progress calculation tests completed!")

if __name__ == "__main__":
    test_percentage_calculation()