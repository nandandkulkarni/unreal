"""
Builder Test Script - Runs INSIDE Unreal Engine
Uses MovieBuilder to define a sequence and executes it using the motion system.
"""
import unreal
import sys
import os
import importlib

# Ensure we can import sibling modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
# Also add parent dir for 'direct' imports if needed (though motion_system seems self-contained now?)
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import Motion System parts
import logger
import cleanup
import sequence_setup
import camera_setup
import mannequin_setup
import hud_setup
import visual_aids
import motion_planner
import keyframe_applier
from motion_builder import MovieBuilder

# Reload for iteration
importlib.reload(logger)
importlib.reload(cleanup)
importlib.reload(sequence_setup)
importlib.reload(camera_setup)
importlib.reload(mannequin_setup)
importlib.reload(hud_setup)
importlib.reload(visual_aids)
importlib.reload(motion_planner)
importlib.reload(keyframe_applier)
# importlib.reload(motion_builder) # Will fail if module not imported as module variable

def add_camera_cut_track(sequence, camera_binding, fps, duration_seconds):
    """Add camera cut track to sequence"""
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_section = camera_cut_track.add_section()
    
    camera_cut_duration_frames = int(fps * duration_seconds)
    camera_cut_section.set_range(0, camera_cut_duration_frames)
    
    try:
        binding_id = unreal.MovieSceneObjectBindingID()
        binding_id.set_editor_property('guid', camera_binding.get_id())
        camera_cut_section.set_camera_binding_id(binding_id)
        logger.log(f"✓ Camera cut track added ({duration_seconds}s)")
    except Exception as e:
        logger.log(f"Warning: Could not set camera binding: {e}")

def add_camera_look_at_constraint(camera_actor, mannequin_actor):
    """Add look-at constraint to camera"""
    try:
        logger.log("\n✓ Adding camera look-at tracking...")
        lookat_settings = unreal.CameraLookatTrackingSettings()
        lookat_settings.enable_look_at_tracking = True
        lookat_settings.actor_to_track = mannequin_actor
        lookat_settings.allow_roll = False
        lookat_settings.look_at_tracking_interp_speed = 0.0
        lookat_settings.relative_offset = unreal.Vector(0, 0, 0)
        
        camera_actor.set_editor_property('lookat_tracking_settings', lookat_settings)
        logger.log("  ✓ Camera look-at tracking enabled")
        return True
    except Exception as e:
        logger.log(f"  Look-at failed: {e}")
        return False

def finalize_sequence(sequence, sequence_name):
    """Save and open sequence"""
    logger.log_header("STEP 7: Finalizing")
    
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    logger.log("✓ Sequence saved")
    
    try:
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        logger.log("✓ Sequence opened and viewport locked")
    except Exception as e:
        logger.log(f"Could not open sequence: {e}")
        return
    
    import time
    time.sleep(1)
    
    try:
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        logger.log("✓ Playing from frame 0")
    except Exception as e:
        logger.log(f"Could not play: {e}")


def run_test():
    try:
        logger.log("=" * 60)
        logger.log("BUILDER TEST - SCENE SETUP")
        logger.log("=" * 60)

        # STEP 1: Cleanup
        cleanup.cleanup_old_assets()

        # STEP 2: Create sequence
        sequence, sequence_name, next_num, fps, duration_frames = sequence_setup.create_sequence(fps=30, duration_seconds=60)
        
        camera_name = f"BuilderCam_{next_num}"
        mannequin_name = f"BuilderMan_{next_num}"
        
        logger.log(f"  Camera: {camera_name}")
        logger.log(f"  Mannequin: {mannequin_name}")

        # STEP 3: Create camera
        camera_location = unreal.Vector(-500.0, 0.0, 400.0)
        camera_rotation = unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0)
        camera = camera_setup.create_camera(camera_name, camera_location, camera_rotation)

        # STEP 4: Create mannequin
        mannequin_location = unreal.Vector(0, 0, 6.882729)
        mannequin_rotation = unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0)
        mannequin = mannequin_setup.create_mannequin(mannequin_name, mannequin_location, mannequin_rotation)

        # Create Visual Aids
        hud_setup.create_hud(camera, mannequin)
        visual_aids.create_plus_sign_at_origin()

        # Position camera
        camera_target_position = mannequin_location
        camera_rotation_aimed = unreal.MathLibrary.find_look_at_rotation(camera_location, camera_target_position)
        camera.set_actor_rotation(camera_rotation_aimed, False)

        # STEP 5: Add actors to sequence
        camera_binding = sequence_setup.add_actor_to_sequence(sequence, camera, camera_name)
        mannequin_binding = sequence_setup.add_actor_to_sequence(sequence, mannequin, mannequin_name)
        add_camera_cut_track(sequence, camera_binding, fps, 60)

        # STEP 6: USE BUILDER TO DEFINE MOTION
        logger.log_header("STEP 6: Defining Motion using Builder")
        
        builder = MovieBuilder("BuilderSequence")
        # We must align the builder's start state with actual spawn state
        builder.add_actor(mannequin_name, (mannequin_location.x, mannequin_location.y, mannequin_location.z))
        
        with builder.for_actor(mannequin_name) as b:
            b.animation("Jog_Fwd")
            b.move_by_distance(meters=5, direction="forward", speed_mph=3, waypoint_name="point_A")
            b.wait(1)
            b.animation("Jog_Left_Start")
            b.move_and_turn(direction="left", meters=3, turn_degrees=90, speed_mph=2, turn_speed_deg_per_sec=45)
            b.animation("Jog_Fwd")
            b.move_for_seconds(direction="forward", seconds=3, speed_mph=2)

        motion_plan = builder.build()["plan"]
        
        # Prepare actors info
        actors_info = {
            mannequin_name: {
                "location": mannequin_location,
                "rotation": mannequin_rotation,
                "actor": mannequin,
                "binding": mannequin_binding
            }
        }
        
        # EXECUTE PLANNER
        keyframe_data_all = motion_planner.plan_motion(motion_plan, actors_info, fps)
        
        # APPLY KEYFRAMES
        logger.log("\nAPPLYING KEYFRAMES...")
        for actor_name, actor_info in actors_info.items():
            if actor_name in keyframe_data_all:
                keyframe_applier.apply_keyframes_to_actor(
                    actor_name,
                    actor_info["actor"],
                    actor_info["binding"],
                    keyframe_data_all[actor_name],
                    fps,
                    duration_frames
                )

        # Camera tracking
        if camera and mannequin:
            add_camera_look_at_constraint(camera, mannequin)

        # Finalize
        finalize_sequence(sequence, sequence_name)
        logger.log_header("✓ BUILDER TEST COMPLETE")
        
    except Exception as e:
        logger.log("\nFATAL ERROR: " + str(e))
        import traceback
        logger.log(traceback.format_exc())

if __name__ == "__main__":
    run_test()
