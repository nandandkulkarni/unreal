"""
Manny Walk/Jog Test (POC)

Verifies that the Motion Matching system returns appropriate animations
(Walk vs Jog vs Run) based on speed inputs.
"""

from motion_cmds.pose_search_selector import PoseSearchSelector
import sys

def run_test():
    print("--- Manny Walk/Jog/Run POC Test ---")
    
    # 1. Initialize Selector
    db_path = "/Game/MotionMatching/MannyMotionDatabase"
    selector = PoseSearchSelector(db_path)
    print(f"Database: {db_path}")

    # 2. Define Test Cases
    # Structure: (Test Name, Speed cm/s, Context Hint, Expected Substring)
    # Note: 1 m/s = 100 cm/s
    tests = [
        ("Walk Test", 150.0, None, "Walk"),
        ("Jog Test",  350.0, None, "Jog"),
        ("Run Test",  600.0, "/Game/Characters/Mannequins/Anims/Unarmed/Run/MF_Unarmed_Run_Fwd", "Run") 
    ]
    
    # Why context hint for run? 
    # Because starting from valid (0,0,0) with just speed might be ambiguous 
    # without a trajectory history. But we'll try pure speed first for Walk/Jog.
    
    results = []
    
    for title, speed, hint, expected in tests:
        print(f"\nRunning {title}...")
        print(f"  Input Speed: {speed} cm/s")
        print(f"  Context: {hint}")
        
        anim, start_time = selector.select(speed, direction=(1,0,0), context_hint=hint)
        
        if anim:
            anim_name = anim.get_path_name()
            print(f"  Result: {anim_name}")
            
            if expected.lower() in anim_name.lower():
                print("  [PASS] Correct animation type found.")
                results.append((title, True))
            else:
                print(f"  [FAIL] Expected '{expected}' in name, got '{anim_name}'")
                results.append((title, False))
        else:
            print("  [FAIL] No animation returned.")
            results.append((title, False))

    # 3. Cleanup
    selector.cleanup()
    
    # 4. Summary
    print("\n--- Summary ---")
    all_passed = True
    for title, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{title}: {status}")
        if not passed: all_passed = False
        
    if all_passed:
        print("\nSUCCESS: All motion matching tests passed.")
    else:
        print("\nFAILURE: Some tests failed.")

if __name__ == "__main__":
    run_test()
