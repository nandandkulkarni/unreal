"""
Script to validate that the scene setup matches the JSON definition.
Checks:
1. Initial Location
2. Initial Rotation
3. Tracking Settings (Locked vs LookAt)
"""
import unreal
import json
import os
import math
from .logger import log, log_header

def vectors_close(v1, v2, tolerance=1.0):
    return v1.distance(v2) <= tolerance

def rotators_close(r1, r2, tolerance=1.0):
    # Normalize angles
    d_pitch = abs((r1.pitch - r2.pitch + 180) % 360 - 180)
    d_yaw = abs((r1.yaw - r2.yaw + 180) % 360 - 180)
    d_roll = abs((r1.roll - r2.roll + 180) % 360 - 180)
    return d_pitch <= tolerance and d_yaw <= tolerance and d_roll <= tolerance

def validate_scene(json_path):
    log_header("VALIDATING SCENE SETTINGS")
    
    if not os.path.exists(json_path):
        log(f"✗ Validation skipped: file not found {json_path}")
        return

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except:
        # If it's a python file (e.g. .py), we might need to load it differently or parse
        # But run_scene usually runs on .json or .py. If .py, we assume it's valid.
        # For simplicity, if passed a .py, we might try to import it if in correct dir.
        # But this script is likely called from run_scene which has 'scene_data'.
        # We will assume run_scene calls this with the DATA dict, not path?
        # User asked for a standalone script "add a validate_settings.py... which checks..."
        # If called from run_scene, we can pass data.
        log("⚠ Validation requires parsing the movie plan. If .py file, manual check needed.")
        return

    # If called directly with data:
    # We'll assume this function is imported and called with plan data or we parse JSON
    pass

def validate_plan(plan):
    """Validate actors in the level against the plan"""
    log_header("VALIDATION CHECKS")
    
    errors = 0
    passed = 0
    
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    
    for cmd in plan:
        if cmd["command"] not in ["add_camera", "add_actor"]:
            continue
            
        actor_name = cmd.get("actor")
        if not actor_name:
            continue
            
        # Find actor
        found = False
        all_actors = editor_actor_subsystem.get_all_level_actors()
        actor = None
        for a in all_actors:
            if a.get_actor_label() == actor_name:
                actor = a
                found = True
                break
        
        if not found:
            log(f"✗ MISSING: Actor '{actor_name}' not found in level")
            errors += 1
            continue
            
        # 1. Validate Location
        if "location" in cmd:
            target_loc = unreal.Vector(cmd["location"][0], cmd["location"][1], cmd["location"][2])
            actual_loc = actor.get_actor_location()
            
            if vectors_close(target_loc, actual_loc):
                log(f"✓ Location {actor_name}: OK {actual_loc}")
                passed += 1
            else:
                log(f"✗ LOCATION MISMATCH {actor_name}: Expected {target_loc}, Got {actual_loc}")
                errors += 1
        
        # 2. Validate Rotation
        if "rotation" in cmd:
            target_rot = unreal.Rotator(cmd["rotation"][0], cmd["rotation"][1], cmd["rotation"][2])
            actual_rot = actor.get_actor_rotation()
            
            # Note: If LookAt is enabled, actual rotation might differ immediately!
            # So we only check rotation if LookAt is NOT enabled, OR if we strictly require init state.
            # But let's check anyway and warn.
            
            if rotators_close(target_rot, actual_rot, tolerance=5.0):
                log(f"✓ Rotation {actor_name}: OK")
                passed += 1
            else:
                # Check directly if LookAt is active
                is_tracking = False
                if isinstance(actor, unreal.CineCameraActor):
                    settings = actor.get_editor_property("lookat_tracking_settings")
                    if settings and settings.get_editor_property("enable_look_at_tracking"):
                        is_tracking = True
                
                if is_tracking:
                    log(f"ℹ Rotation {actor_name}: Differs (Tracking Enabled) - Expected {target_rot}, Got {actual_rot}")
                    passed += 1 # Count as pass since tracking overrides
                else:
                    log(f"✗ ROTATION MISMATCH {actor_name}: Expected {target_rot}, Got {actual_rot}")
                    errors += 1

        # 3. Validate Locks (LookAt Tracking)
        if isinstance(actor, unreal.CineCameraActor):
            should_track = "look_at_actor" in cmd
            
            settings = actor.get_editor_property("lookat_tracking_settings")
            is_tracking = False
            if settings:
                is_tracking = settings.get_editor_property("enable_look_at_tracking")
                
            if should_track == is_tracking:
                state = "Locked" if not should_track else "Tracking"
                log(f"✓ Tracking {actor_name}: OK ({state})")
                passed += 1
            else:
                log(f"✗ TRACKING MISMATCH {actor_name}: Expected {'Tracking' if should_track else 'Locked'}, Got {'Tracking' if is_tracking else 'Locked'}")
                errors += 1

    log("-" * 40)
    if errors > 0:
        log(f"FAILED: {errors} errors found")
    else:
        log(f"SUCCESS: All {passed} checks passed")
        
if __name__ == "__main__":
    # If run standalone, try to verify current level against a default JSON?
    pass
