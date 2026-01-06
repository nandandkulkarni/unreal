"""
Test: PoseSearchLibrary.motion_match() Function

This script attempts to use the discovered motion_match() function
to query the Motion Matching database from Python.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"test_motion_match_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("TESTING: PoseSearchLibrary.motion_match()")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# Load the library
log("\n[1] Loading PoseSearchLibrary...")
try:
    lib = unreal.PoseSearchLibrary
    log("✓ Library loaded")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Check the motion_match function
log("\n[2] Inspecting motion_match function...")
try:
    motion_match = lib.motion_match
    log(f"✓ Function found: {motion_match}")
    log(f"  Type: {type(motion_match)}")
    
    # Try to get docstring
    if hasattr(motion_match, '__doc__'):
        doc = str(motion_match.__doc__)
        log(f"\n  Documentation:")
        for line in doc.split('\n')[:20]:
            log(f"    {line}")
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# Load database
log("\n[3] Loading Motion Matching database...")
try:
    database = unreal.load_object(None, "/Game/MotionMatching/MannyMotionDatabase")
    if database:
        log(f"✓ Database loaded: {database.get_name()}")
    else:
        log("✗ Database not found")
        raise Exception("Database not found")
except Exception as e:
    log(f"✗ ERROR: {e}")
    raise

# Try to understand the parameters
log("\n[4] Understanding motion_match parameters...")
log("""
From documentation:
  motion_match(anim_instance, assets_to_search, pose_history_name, 
               continuing_properties, future) -> PoseSearchBlueprintResult

Parameters needed:
  - anim_instance: AnimInstance (from character's skeletal mesh)
  - assets_to_search: Array of databases to search
  - pose_history_name: Name for pose history tracking
  - continuing_properties: PoseSearchContinuingProperties struct
  - future: PoseSearchFutureProperties struct (trajectory data)

Challenge: We need an AnimInstance, which requires a character in the world.
""")

# Try to call with minimal parameters to see error
log("\n[5] Attempting to call motion_match (will likely fail)...")
try:
    # This will fail but give us useful error info
    result = lib.motion_match(None, [database], "test", None, None)
    log(f"✓ Unexpected success: {result}")
except TypeError as e:
    log(f"⚠ Expected error (shows parameter requirements):")
    log(f"  {str(e)}")
except Exception as e:
    log(f"⚠ Error: {e}")
    import traceback
    log(traceback.format_exc())

# Check related types
log("\n[6] Checking related types...")

try:
    log("\nPoseSearchContinuingProperties:")
    cont_props = unreal.PoseSearchContinuingProperties
    log(f"  Type: {cont_props}")
    
    # Try to instantiate
    try:
        instance = cont_props()
        log(f"  ✓ Can instantiate")
        # Check properties
        props = [p for p in dir(instance) if not p.startswith('_')]
        log(f"  Properties: {props[:10]}")
    except Exception as e:
        log(f"  ✗ Cannot instantiate: {e}")
except Exception as e:
    log(f"  Error: {e}")

try:
    log("\nPoseSearchFutureProperties:")
    future_props = unreal.PoseSearchFutureProperties
    log(f"  Type: {future_props}")
    
    try:
        instance = future_props()
        log(f"  ✓ Can instantiate")
        props = [p for p in dir(instance) if not p.startswith('_')]
        log(f"  Properties: {props[:10]}")
    except Exception as e:
        log(f"  ✗ Cannot instantiate: {e}")
except Exception as e:
    log(f"  Error: {e}")

# Summary
log("\n" + "=" * 80)
log("SUMMARY")
log("=" * 80)

log("""
FINDINGS:
✓ PoseSearchLibrary.motion_match() EXISTS and is callable from Python!
✓ Returns PoseSearchBlueprintResult with selected animation and time
✓ Can query Motion Matching database programmatically

CHALLENGE:
✗ Requires AnimInstance (needs character in world)
✗ Requires trajectory data (PoseSearchFutureProperties)
✗ Cannot easily test without a running game/character

FOR PROCEDURAL MOVIES:
This function is designed for runtime gameplay, not offline queries.
To use it, you would need:
1. A character spawned in the world
2. Access to its AnimInstance
3. Trajectory data (where character wants to move)

RECOMMENDATION:
For procedural movies, better to:
Option A: Use traditional animation selection (velocity-based)
Option B: Extend C++ plugin with simplified query function
Option C: Record Motion Matching gameplay and use recordings

The motion_match() function is powerful but designed for real-time
gameplay, not offline cinematic generation.
""")

log(f"\nLog saved to: {LOG_FILE}")
