"""
Phase 1 Test: Manual 3D Spline Path

Tests the Motion Matching system with a manually defined 3D path
containing highs, lows, and turns.
"""

import unreal
import os
from datetime import datetime
import traceback

import sys
import importlib

# Ensure local modules can be imported
PROJECT_DIR = r"C:\UnrealProjects\coding\unreal\motion_system\root-motion-matching-poc"
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

# Setup logging first to capture import errors
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIR, f"phase1_test_{timestamp}.log")

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

try:
    import spline_terrain_system
    import terrain_aware_selector
    
    # FORCE RELOAD to ensure we are running latest code
    importlib.reload(spline_terrain_system)
    importlib.reload(terrain_aware_selector)
    
    from spline_terrain_system import SplinePathBuilder
    from terrain_aware_selector import TerrainAwareMotionMatchingSelector
except Exception as e:
    log(f"CRITICAL IMPORT ERROR: {e}")
    log(traceback.format_exc())
    raise

log("=" * 80)
log("PHASE 1 TEST: MANUAL 3D SPLINE PATH")
log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

def run_test():
    # 1. Setup Spline Builder
    log("\n[1] Building Spline Path...")
    builder = SplinePathBuilder()
    
    # Define points: (Highs, Lows, Turns)
    # Start (0,0,0)
    builder.add_point((0, 0, 0))
    
    # Simple Turn + slight elevation (100, 50, 10)
    builder.add_point((100, 50, 10))
    
    # "High" - Steep Climb to (200, 0, 100)
    # Distance approx 110m, Height gain 90m -> ~40 deg slope
    builder.add_point((200, 0, 100))
    
    # "Turn" - Ridge traverse to (300, 100, 110)
    # Gentle slope
    builder.add_point((300, 100, 110))
    
    # "Low" - Descent to (400, 0, 50)
    # Downhill
    builder.add_point((400, 0, 50))
    
    # Build in world
    spline_comp = builder.build_spline()
    total_length = builder.get_length()
    log(f"✓ Spline built. Total Length: {total_length:.2f} meters")
    
    # 2. Setup Motion Matching Selector
    log("\n[2] Initializing Motion Matching Selector...")
    selector = TerrainAwareMotionMatchingSelector()
    
    # 3. Walk the path
    log("\n[3] Walking the path...")
    
    current_dist = 0.0
    step_size = 50.0 # Sample every 50 meters
    
    while current_dist < total_length - 5: # Stop just before end
        # Sample current point
        pos_current, _ = builder.sample_spline(current_dist)
        
        # Sample next point (lookahead for slope calculation)
        next_dist = min(current_dist + step_size, total_length)
        pos_next, _ = builder.sample_spline(next_dist)
        
        # Calculate duration assuming constant speed for now to get Velocity
        # (In real system, speed might vary by slope, but let's test detection first)
        segment_dist_3d = pos_current.distance(pos_next)
        assumed_speed = 200.0 # Standard walk speed
        duration = segment_dist_3d / assumed_speed
        
        log(f"\n--- Segment: {current_dist:.0f}m to {next_dist:.0f}m ---")
        log(f"  Pos: {pos_current.x:.1f}, {pos_current.y:.1f}, {pos_current.z:.1f} -> {pos_next.x:.1f}, {pos_next.y:.1f}, {pos_next.z:.1f}")
        
        # Query Selector
        anim, start_time, metadata = selector.select_for_terrain_movement(
            start_pos=pos_current,
            end_pos=pos_next,
            duration=duration
        )
        
        # Output Results
        slope = metadata['slope_angle']
        terrain = metadata['terrain_type']
        
        log(f"  Slope: {slope:.1f} degrees")
        log(f"  Detected Terrain: {terrain}")
        
        if anim:
            log(f"  Selected Animation: {anim.get_name()}")
        else:
            log(f"  Selected Animation: None (using fallback/procedural)")
            
        current_dist += step_size

    # Cleanup
    log("\n[4] Cleanup...")
    selector.cleanup()
    builder.cleanup()
    log("✓ Cleanup complete")

try:
    run_test()
    log("\nTEST COMPLETED SUCCESSFULLY")
except Exception as e:
    log(f"\n✗ TEST FAILED: {e}")
    import traceback
    log(traceback.format_exc())
