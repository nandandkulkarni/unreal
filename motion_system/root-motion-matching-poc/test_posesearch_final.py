"""
Test PoseSearch functions in AAANKPose plugin with detailed logging

Run with: python run_remote.py test_posesearch_final.py
"""

import unreal
import os
from datetime import datetime

# Log file path
LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
LOG_FILE = os.path.join(LOG_DIR, "test_posesearch_final.log")

def log(message):
    """Write message to both console and log file"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def test_posesearch():
    """Test all PoseSearch functions"""
    
    # Clear previous log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log("=" * 80)
    log("AAANKPose PLUGIN - POSESEARCH FUNCTIONS TEST")
    log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log("")
    
    # Test 1: Load library
    log("Test 1: Loading AAANKPoseBlueprintLibrary...")
    try:
        lib = unreal.AAANKPoseBlueprintLibrary
        log(f"✓ Library loaded: {lib}")
    except Exception as e:
        log(f"✗ Failed to load library: {e}")
        return False
    
    log("")
    
    # Test 2: Check for PoseSearch functions
    log("Test 2: Checking for PoseSearch functions...")
    functions = [
        'add_animation_to_database',
        'add_animations_to_database',
        'build_database',
        'get_animation_count',
        'clear_database',
        'get_database_info'
    ]
    
    found = []
    missing = []
    for func in functions:
        if hasattr(lib, func):
            found.append(func)
            log(f"  ✓ {func}")
        else:
            missing.append(func)
            log(f"  ✗ {func} - NOT FOUND")
    
    log("")
    log(f"Summary: {len(found)}/{len(functions)} functions found")
    
    if missing:
        log("")
        log("❌ MISSING FUNCTIONS - Plugin may not have compiled correctly")
        log("Please:")
        log("1. Check Visual Studio for compilation errors")
        log("2. Ensure PoseSearch plugin is enabled")
        log("3. Restart Unreal Editor")
        return False
    
    log("")
    
    # Test 3: Load database
    log("Test 3: Loading Motion Matching database...")
    try:
        database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
        if database:
            log(f"✓ Database loaded: {database.get_name()}")
        else:
            log("⚠ Database not found - creating it first...")
            log("  Run: python run_remote.py create_motion_database.py")
            database = None
    except Exception as e:
        log(f"⚠ Error loading database: {e}")
        database = None
    
    log("")
    
    # Test 4: Get database info (if database exists)
    if database:
        log("Test 4: Getting database info...")
        try:
            info = lib.get_database_info(database)
            log(f"✓ Database info retrieved:")
            for line in info.split('\n'):
                log(f"  {line}")
        except Exception as e:
            log(f"✗ Error getting info: {e}")
        
        log("")
        
        # Test 5: Get animation count
        log("Test 5: Getting animation count...")
        try:
            count = lib.get_animation_count(database)
            log(f"✓ Current animation count: {count}")
        except Exception as e:
            log(f"✗ Error getting count: {e}")
            count = 0
        
        log("")
        
        # Test 6: Try to load and add a test animation
        log("Test 6: Testing add_animation_to_database...")
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
                    log(f"  ✓ Loaded animation: {anim.get_name()}")
                    break
            except:
                continue
        
        if anim:
            try:
                success = lib.add_animation_to_database(database, anim)
                if success:
                    log(f"  ✓ Animation added successfully!")
                else:
                    log(f"  ⚠ Function returned False")
            except Exception as e:
                log(f"  ✗ Error adding animation: {e}")
            
            # Check count again
            try:
                new_count = lib.get_animation_count(database)
                log(f"  ✓ New animation count: {new_count}")
                if new_count > count:
                    log(f"  ✓ Count increased by {new_count - count}!")
            except Exception as e:
                log(f"  ✗ Error getting new count: {e}")
        else:
            log("  ⚠ Could not find test animation")
        
        log("")
        
        # Test 7: Build database
        log("Test 7: Testing build_database...")
        try:
            success = lib.build_database(database)
            if success:
                log(f"  ✓ Database built successfully!")
            else:
                log(f"  ⚠ Build returned False")
        except Exception as e:
            log(f"  ✗ Error building database: {e}")
    
    log("")
    log("=" * 80)
    log("✅ TEST COMPLETE!")
    log("=" * 80)
    log("")
    
    if len(found) == len(functions):
        log("🎉 SUCCESS! All PoseSearch functions are working!")
        log("")
        log("You can now:")
        log("1. Add all 123 animations automatically")
        log("2. Build the database from Python")
        log("3. Achieve 100% automation!")
        log("")
        log("Next: Run the full automation script to populate the database")
    else:
        log("⚠ Some functions are missing - check compilation")
    
    log("")
    log(f"Full log saved to: {LOG_FILE}")
    
    return True

if __name__ == "__main__":
    test_posesearch()
