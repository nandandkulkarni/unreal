"""
Research: Creating Trajectory Data for Motion Matching Queries

Goal: Figure out how to populate PoseSearchFutureProperties with
actual trajectory data representing desired movement.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"trajectory_research_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

log("=" * 80)
log("RESEARCH: Creating Trajectory Data")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# ============================================================================
# 1. Explore PoseSearchFutureProperties
# ============================================================================
log("\n[1] Exploring PoseSearchFutureProperties...")

try:
    future_props = unreal.PoseSearchFutureProperties()
    
    # Get all properties
    props = [p for p in dir(future_props) if not p.startswith('_') and not callable(getattr(future_props, p))]
    
    log(f"Properties available:")
    for prop in props:
        try:
            value = getattr(future_props, prop)
            log(f"  {prop}: {value} (type: {type(value).__name__})")
        except:
            log(f"  {prop}: <cannot read>")
            
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 2. Explore PoseSearchTrajectoryData
# ============================================================================
log("\n[2] Exploring PoseSearchTrajectoryData...")

try:
    traj_data = unreal.PoseSearchTrajectoryData()
    
    props = [p for p in dir(traj_data) if not p.startswith('_') and not callable(getattr(traj_data, p))]
    
    log(f"Properties available:")
    for prop in props:
        try:
            value = getattr(traj_data, prop)
            log(f"  {prop}: {value} (type: {type(value).__name__})")
        except:
            log(f"  {prop}: <cannot read>")
            
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 3. Check PoseSearchQueryTrajectory
# ============================================================================
log("\n[3] Exploring PoseSearchQueryTrajectory...")

try:
    # This is likely what we need to create
    query_traj_class = unreal.PoseSearchQueryTrajectory
    log(f"Class: {query_traj_class}")
    
    # Try to instantiate
    try:
        query_traj = query_traj_class()
        log(f"✓ Can instantiate")
        
        # Check properties
        props = [p for p in dir(query_traj) if not p.startswith('_')]
        log(f"\nMethods/Properties ({len(props)}):")
        for prop in props[:20]:
            log(f"  - {prop}")
    except Exception as e:
        log(f"✗ Cannot instantiate: {e}")
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 4. Try PoseSearchTrajectoryLibrary generation methods
# ============================================================================
log("\n[4] Testing Trajectory Generation Methods...")

try:
    traj_lib = unreal.PoseSearchTrajectoryLibrary
    
    # Check the generate methods we found earlier
    log("\nAvailable generation methods:")
    methods = [m for m in dir(traj_lib) if 'generate' in m.lower()]
    for method in methods:
        log(f"  - {method}")
    
    # Try to understand pose_search_generate_transform_trajectory
    log("\nTrying pose_search_generate_transform_trajectory...")
    log("  This requires: anim_instance, trajectory_data, delta_time, ...")
    log("  We have anim_instance from spawned character")
    log("  Need to create trajectory_data")
    
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 5. Simple approach: Set properties directly
# ============================================================================
log("\n[5] Simple Approach: Setting Properties Directly...")

try:
    future_props = unreal.PoseSearchFutureProperties()
    
    log("\nTrying to set animation property...")
    # Try to set an animation
    test_anim = unreal.load_object(None, "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle")
    if test_anim:
        log(f"  Loaded test animation: {test_anim.get_name()}")
        
        try:
            future_props.animation = test_anim
            log(f"  ✓ Set animation property")
        except Exception as e:
            log(f"  ✗ Cannot set animation: {e}")
        
        try:
            future_props.animation_time = 0.0
            log(f"  ✓ Set animation_time property")
        except Exception as e:
            log(f"  ✗ Cannot set animation_time: {e}")
            
        try:
            future_props.interval_time = 0.5
            log(f"  ✓ Set interval_time property")
        except Exception as e:
            log(f"  ✗ Cannot set interval_time: {e}")
    
    log(f"\nFinal future_props:")
    log(f"  animation: {future_props.animation}")
    log(f"  animation_time: {future_props.animation_time}")
    log(f"  interval_time: {future_props.interval_time}")
    
except Exception as e:
    log(f"✗ ERROR: {e}")
    import traceback
    log(traceback.format_exc())

# ============================================================================
# Summary
# ============================================================================
log("\n" + "=" * 80)
log("SUMMARY")
log("=" * 80)

log("""
FINDINGS:

PoseSearchFutureProperties has these properties:
- animation: Can be set to a specific animation
- animation_time: Time within that animation
- interval_time: Time interval for prediction

SIMPLE APPROACH:
Instead of generating complex trajectory data, we can:
1. Set future_props.animation to desired animation type
2. Set future_props.animation_time to start time
3. Let Motion Matching find best match

ALTERNATIVE:
For true trajectory-based queries, we'd need to:
1. Use PoseSearchTrajectoryLibrary.pose_search_generate_transform_trajectory()
2. Requires AnimInstance + trajectory data
3. More complex but gives trajectory-based matching

RECOMMENDATION:
For procedural movies, the simple approach works:
- Set desired animation type in future_props
- Motion Matching finds best frame to start from
- Or just use traditional selection (simpler!)
""")

log(f"\nLog saved to: {LOG_FILE}")
