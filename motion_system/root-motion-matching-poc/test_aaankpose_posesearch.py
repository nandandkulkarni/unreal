"""
Test script for AAANKPose plugin with PoseSearch functions

This tests the PoseSearch database manipulation functions.
Run with: python run_remote.py test_aaankpose_posesearch.py
"""

import unreal

def test_posesearch_functions():
    """Test PoseSearch database functions in AAANKPose plugin"""
    print("=" * 80)
    print("TESTING AAANKPose PLUGIN - POSESEARCH FUNCTIONS")
    print("=" * 80)
    print()
    
    # Test 1: Load the library
    print("Test 1: Loading AAANKPose library...")
    try:
        lib = unreal.AAANKPoseLibrary()
        print("✓ Library loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load library: {e}")
        print("  Make sure plugin is enabled and editor was restarted")
        return
    
    print()
    
    # Test 2: Load database
    print("Test 2: Loading PoseSearch database...")
    try:
        database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
        if database:
            print(f"✓ Database loaded: {database.get_name()}")
        else:
            print("✗ Database not found at /Game/MotionMatching/MannyMotionDatabase")
            print("  Run 'python run_remote.py create_motion_database.py' first")
            return
    except Exception as e:
        print(f"✗ Error loading database: {e}")
        return
    
    print()
    
    # Test 3: Get initial animation count
    print("Test 3: Getting animation count...")
    try:
        count_before = lib.get_animation_count(database)
        print(f"✓ Animation count (before): {count_before}")
    except Exception as e:
        print(f"✗ Error getting count: {e}")
        count_before = 0
    
    print()
    
    # Test 4: Get database info
    print("Test 4: Getting database info...")
    try:
        info = lib.get_database_info(database)
        print(f"✓ Database info:")
        for line in info.split('\n'):
            print(f"  {line}")
    except Exception as e:
        print(f"✗ Error getting info: {e}")
    
    print()
    
    # Test 5: Load a test animation
    print("Test 5: Loading test animation...")
    try:
        # Try to load an Idle animation
        anim_paths = [
            "/Game/Characters/Mannequins/Animations/Manny/MM_Idle",
            "/Game/Characters/Mannequins/Animations/Unarmed/MM_Idle",
            "/Game/Characters/Mannequins/Animations/MM_Idle"
        ]
        
        anim = None
        for path in anim_paths:
            try:
                anim = unreal.load_object(None, path)
                if anim:
                    print(f"✓ Animation loaded: {anim.get_name()} from {path}")
                    break
            except:
                continue
        
        if not anim:
            print("⚠ Could not find test animation, skipping add test")
            print("  Tried paths:", anim_paths)
    except Exception as e:
        print(f"✗ Error loading animation: {e}")
        anim = None
    
    print()
    
    # Test 6: Add animation to database
    if anim:
        print("Test 6: Adding animation to database...")
        try:
            success = lib.add_animation_to_database(database, anim)
            if success:
                print(f"✓ Add animation: Success")
            else:
                print(f"⚠ Add animation: Failed (returned False)")
        except Exception as e:
            print(f"✗ Error adding animation: {e}")
        
        print()
        
        # Test 7: Get count after adding
        print("Test 7: Getting animation count after add...")
        try:
            count_after = lib.get_animation_count(database)
            print(f"✓ Animation count (after): {count_after}")
            if count_after > count_before:
                print(f"✓ Count increased by {count_after - count_before}")
        except Exception as e:
            print(f"✗ Error getting count: {e}")
        
        print()
    
    # Test 8: Build database
    print("Test 8: Building database...")
    try:
        success = lib.build_database(database)
        if success:
            print("✓ Build database: Success")
        else:
            print("⚠ Build database: Failed (returned False)")
    except Exception as e:
        print(f"✗ Error building database: {e}")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    
    # Summary
    print("Summary:")
    print("- If all tests passed, your plugin is working correctly!")
    print("- You can now use these functions to automate database population")
    print("- Next: Run the full automation script to add all 123 animations")
    print()

if __name__ == "__main__":
    test_posesearch_functions()
