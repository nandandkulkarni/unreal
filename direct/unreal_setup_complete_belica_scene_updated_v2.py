"""
Pure Unreal Python Script - Complete Scene Setup (Modular Version)

This script runs INSIDE Unreal Engine's Python interpreter.
It creates a complete cinematic scene:
1. Deletes old Test* sequences, cameras, and mannequins
2. Creates a new sequence with timestamp
3. Creates a camera
4. Creates a mannequin
5. Adds both to the sequence

Usage: Open this file in VS Code and press Ctrl+Enter to run

Sub-modules are located in the current path and imported from there.
"""
import unreal
import sys
import importlib
import os

# Add module path - using local imports folder
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(script_dir, "imports")
if module_path not in sys.path:
    sys.path.insert(0, module_path)

# Reload modules to ensure we get the latest version
import logger
import cleanup
import sequence_setup
import track_setup
import camera_setup
import mannequin_setup
import hud_setup
import visual_aids
importlib.reload(logger)
importlib.reload(cleanup)
importlib.reload(sequence_setup)
importlib.reload(track_setup)
importlib.reload(camera_setup)
importlib.reload(mannequin_setup)
importlib.reload(hud_setup)
importlib.reload(visual_aids)

try:
    logger.log("=" * 60)
    logger.log("Complete Cinematic Scene Setup - MODULAR VERSION 2 - WITH CAMERA TRACKING")
    logger.log("=" * 60)

    # STEP 1: Cleanup old assets
    cleanup.cleanup_old_assets()

    # STEP 2: Create sequence
    sequence, sequence_name, next_num, fps, duration_frames = sequence_setup.create_sequence(fps=30, duration_seconds=60)
    
    camera_name = f"TestCamera_{sequence_name.replace('TestSequence_', '')}"
    mannequin_name = f"TestMannequin_{sequence_name.replace('TestSequence_', '')}"
    
    logger.log(f"  Camera: {camera_name}")
    logger.log(f"  Mannequin: {mannequin_name}")

    # STEP 3: Create camera
    camera_location = unreal.Vector(0, 0, 300)
    camera_rotation = unreal.Rotator(pitch=0.0, yaw=90.0, roll=0.0)
    camera = camera_setup.create_camera(camera_name, camera_location, camera_rotation)

    # STEP 4: Create mannequin
    mannequin_location = unreal.Vector(0, 0, 300)
    mannequin_rotation = unreal.Rotator(pitch=0.0, yaw=-90.0, roll=0.0)
    mannequin = mannequin_setup.create_mannequin(mannequin_name, mannequin_location, mannequin_rotation)

    # Create HUD
    hud_setup.create_hud(camera, mannequin)

    # Create visual aids (plus sign at origin)
    visual_aids.create_plus_sign_at_origin()

    # Position camera behind mannequin's movement direction (she moves along +X, so camera on -X)
    # Camera at (-500, 0, 400) looking at origin
    camera_behind_position = unreal.Vector(-500.0, 0.0, 400.0)
    camera_target_position = mannequin_location
    camera_rotation = unreal.MathLibrary.find_look_at_rotation(camera_behind_position, camera_target_position)
    camera.set_actor_location(camera_behind_position, False, False)
    camera.set_actor_rotation(camera_rotation, False)
    logger.log("✓ Camera positioned behind movement direction (-X) looking at mannequin")

    # STEP 5: Add camera to sequence
    camera_binding = track_setup.add_camera_to_sequence(sequence, camera, fps, duration_seconds=60)

    # STEP 6: Add mannequin to sequence
    mannequin_binding = track_setup.add_mannequin_to_sequence(
        sequence, mannequin, mannequin_location, mannequin_rotation, fps, duration_frames
    )

    # Add camera look-at constraint
    if camera and mannequin:
        track_setup.add_camera_look_at_constraint(camera, mannequin)

    # STEP 7: Finalize sequence
    track_setup.finalize_sequence(sequence, sequence_name)

    # ===== COMPLETE =====
    logger.log_header("✓ SCENE SETUP COMPLETE!")
    logger.log(f"Sequence: {sequence_name}")
    logger.log(f"Camera: {camera_name}")
    logger.log(f"Mannequin: {mannequin_name}")
    logger.log(f"Duration: 60s @ {fps}fps")
    logger.log("=" * 60)
    logger.log("\nCheck Sequencer to see your complete scene!")

except Exception as e:
    logger.log("\n" + "=" * 60)
    logger.log("✗ FATAL ERROR")
    logger.log("=" * 60)
    logger.log("Error type: " + type(e).__name__)
    logger.log("Error message: " + str(e))

    import traceback
    logger.log("\nFull traceback:")
    for line in traceback.format_exc().split('\n'):
        if line:
            logger.log("  " + line)
    logger.log("=" * 60)

print("\nDone!")