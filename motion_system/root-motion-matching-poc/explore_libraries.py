"""
Deep Exploration: PoseSearchLibrary and PoseSearchTrajectoryLibrary

This script explores all methods in these libraries to find query capabilities
that could be used for procedural movie animation selection.
"""

import unreal
import os
from datetime import datetime

LOG_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc\logs"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"library_exploration_{timestamp}.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

def explore_method(obj, method_name):
    """Try to get detailed info about a method"""
    try:
        method = getattr(obj, method_name)
        log(f"\n  {method_name}:")
        log(f"    Type: {type(method)}")
        
        # Try to get docstring
        if hasattr(method, '__doc__') and method.__doc__:
            doc = str(method.__doc__).strip()
            if doc and doc != 'None':
                log(f"    Doc: {doc[:200]}")
        
        # Try to call with no args to see signature error
        try:
            method()
        except TypeError as e:
            # Error message often contains signature info
            error_msg = str(e)
            if 'argument' in error_msg.lower() or 'parameter' in error_msg.lower():
                log(f"    Signature hint: {error_msg[:150]}")
        except:
            pass
            
    except Exception as e:
        log(f"  {method_name}: Error - {e}")

log("=" * 80)
log("DEEP EXPLORATION: PoseSearch Libraries")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# ============================================================================
# 1. PoseSearchLibrary
# ============================================================================
log("\n" + "=" * 80)
log("[1] PoseSearchLibrary - Detailed Method Exploration")
log("=" * 80)

try:
    lib = unreal.PoseSearchLibrary
    methods = [m for m in dir(lib) if not m.startswith('_')]
    
    log(f"\nTotal methods: {len(methods)}")
    log("\nExploring each method:")
    
    for method_name in sorted(methods):
        explore_method(lib, method_name)
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 2. PoseSearchTrajectoryLibrary
# ============================================================================
log("\n" + "=" * 80)
log("[2] PoseSearchTrajectoryLibrary - Detailed Method Exploration")
log("=" * 80)

try:
    traj_lib = unreal.PoseSearchTrajectoryLibrary
    methods = [m for m in dir(traj_lib) if not m.startswith('_')]
    
    log(f"\nTotal methods: {len(methods)}")
    log("\nExploring each method:")
    
    for method_name in sorted(methods):
        explore_method(traj_lib, method_name)
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 3. PoseSearchBlueprintResult
# ============================================================================
log("\n" + "=" * 80)
log("[3] PoseSearchBlueprintResult - Query Result Type")
log("=" * 80)

try:
    result_class = unreal.PoseSearchBlueprintResult
    methods = [m for m in dir(result_class) if not m.startswith('_')]
    
    log(f"\nTotal methods: {len(methods)}")
    log("\nExploring each method:")
    
    for method_name in sorted(methods):
        explore_method(result_class, method_name)
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 4. PoseSearchQueryTrajectory
# ============================================================================
log("\n" + "=" * 80)
log("[4] PoseSearchQueryTrajectory - Trajectory Query Type")
log("=" * 80)

try:
    query_traj = unreal.PoseSearchQueryTrajectory
    methods = [m for m in dir(query_traj) if not m.startswith('_')]
    
    log(f"\nTotal methods: {len(methods)}")
    
    # Check properties
    log("\nProperties:")
    try:
        instance = query_traj()
        props = [p for p in dir(instance) if not p.startswith('_') and not callable(getattr(instance, p))]
        for prop in props[:20]:
            log(f"  - {prop}")
    except Exception as e:
        log(f"  Could not instantiate: {e}")
        
except Exception as e:
    log(f"✗ ERROR: {e}")

# ============================================================================
# 5. Try to find actual query/search methods
# ============================================================================
log("\n" + "=" * 80)
log("[5] Searching for Query/Search Methods Across All Classes")
log("=" * 80)

all_pose_classes = [attr for attr in dir(unreal) if 'pose' in attr.lower() and 'search' in attr.lower()]

log(f"\nSearching {len(all_pose_classes)} PoseSearch classes for query methods...")

found_query_methods = []

for class_name in all_pose_classes:
    try:
        cls = getattr(unreal, class_name)
        methods = [m for m in dir(cls) if not m.startswith('_')]
        
        # Look for promising method names
        query_keywords = ['query', 'search', 'find', 'match', 'select', 'choose', 'pick']
        
        for method in methods:
            if any(keyword in method.lower() for keyword in query_keywords):
                found_query_methods.append({
                    'class': class_name,
                    'method': method
                })
    except:
        pass

if found_query_methods:
    log(f"\n✓ Found {len(found_query_methods)} potential query methods:")
    for item in found_query_methods:
        log(f"  {item['class']}.{item['method']}")
else:
    log("\n⚠ No query methods found")

# ============================================================================
# Summary and Recommendations
# ============================================================================
log("\n" + "=" * 80)
log("SUMMARY & RECOMMENDATIONS")
log("=" * 80)

log("""
Based on this exploration:

FINDINGS:
1. PoseSearchLibrary exists but has limited Python exposure
2. PoseSearchTrajectoryLibrary can generate trajectory data
3. PoseSearchBlueprintResult is the result type from queries
4. BUT: No direct query function exposed to Python

TRAJECTORY GENERATION:
- pose_search_generate_trajectory() methods exist
- Can create trajectory data in Python
- Trajectory represents desired future movement

MISSING PIECE:
- No Python function to query database with trajectory
- Query happens in C++ AnimGraph nodes
- Result type (PoseSearchBlueprintResult) exists but can't be created from Python

RECOMMENDATION FOR PROCEDURAL MOVIES:
Option A: Extend C++ Plugin (Best for Motion Matching)
  - Add QueryDatabase() function to AAANKPose plugin
  - Takes trajectory, current pose as input
  - Returns best matching animation + frame
  - Enables true Motion Matching in procedural movies

Option B: Traditional Selection (Simpler)
  - Use velocity/direction to pick animations
  - Manual logic: if speed > 400: use jog, else: use walk
  - No Motion Matching, but deterministic
  - Works with existing procedural movie system

Option C: Hybrid
  - Use Motion Matching for gameplay
  - Use traditional selection for cinematics
  - Best of both worlds
""")

log(f"\nLog saved to: {LOG_FILE}")
