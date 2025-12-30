"""
Tandem Square Runner - Runs INSIDE Unreal Engine
Imports the movie definition from movies/json_tandem_run_square.py and executes it.
"""
import unreal
import sys
import os
import importlib

# Setup paths
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for remote execution where __file__ is undefined
    script_dir = "c:/UnrealProjects/coding/unreal/motion_system"
if script_dir not in sys.path:
    sys.path.append(script_dir)
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import dependencies
import logger
from motion_includes import cleanup
from motion_includes import sequence_setup
from motion_includes import camera_setup
from motion_includes import mannequin_setup
from motion_includes import hud_setup
from motion_includes import visual_aids
from motion_includes import keyframe_applier
import motion_planner

# Import the movie definition
# We need to make sure we can import from movies.
# Since script_dir is motion_system/, movies should be importable as movies.json_tandem_run_square
# IF motion_system is a package.
# Alternatively, we append movies/ to path.
movies_dir = os.path.join(script_dir, "movies")
if movies_dir not in sys.path:
    sys.path.append(movies_dir)

import json_tandem_run_square

# Reload all modules for iteration (clears Python cache in Unreal)
modules_to_reload = [
    'logger', 'motion_planner', 'motion_builder', 'motion_math',
    'json_tandem_run_square'
]

for mod_name in modules_to_reload:
    if mod_name in sys.modules:
        try:
            importlib.reload(sys.modules[mod_name])
        except Exception as e:
            logger.log(f"Warning: Could not reload {mod_name}: {e}")

# Also reload motion_includes modules
motion_includes_modules = [
    'cleanup', 'sequence_setup', 'camera_setup', 'mannequin_setup',
    'keyframe_applier', 'light_setup', 'level_setup', 'hud_setup',
    'visual_aids', 'axis_markers'
]

for mod_name in motion_includes_modules:
    full_name = f'motion_includes.{mod_name}'
    if full_name in sys.modules:
        try:
            importlib.reload(sys.modules[full_name])
        except Exception as e:
            logger.log(f"Warning: Could not reload {full_name}: {e}")

def run_tandem_square():
    try:
        logger.log("=" * 60)
        logger.log("RUNNING TANDEM SQUARE SCENE")
        logger.log("=" * 60)

        # 1. Get the plan
        # json_tandem_run_square.define_movie() returns the movie_data dict
        movie_data = json_tandem_run_square.define_movie()
        plan = movie_data["plan"]
        fps = movie_data.get("fps", 30)
        scene_name = movie_data.get("name", "TandemSquare")
        
        # 2. Setup Environment
        cleanup.cleanup_old_assets()
        
        # 3. Create Sequence
        sequence, sequence_name, next_num, fps, duration_frames = sequence_setup.create_sequence(fps=fps, duration_seconds=20, test_name=scene_name)
        
        # 4. Execute Plan
        logger.log_header("Executing Motion Plan")
        
        # Initialize trackers
        actors_info = {}
        
        # Motion planner will handle all setup commands (add_actor, add_camera, etc)
        # and populate actors_info automatically
        keyframe_data_all, camera_cuts = motion_planner.plan_motion(plan, actors_info, fps, sequence=sequence)
        
        # 6. Apply Keyframes
        # ... (standard apply loop) ... 
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
        
        # 5. Apply Camera Cuts
        if camera_cuts:
            logger.log_header("Applying Camera Cuts")
            sequence_setup.apply_camera_cuts(sequence, camera_cuts, actors_info, fps)
        
        # 6. Finalize
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        logger.log("✓ Sequence Playing")

    except Exception as e:
        logger.log(f"FATAL ERROR: {e}")
        import traceback
        logger.log(traceback.format_exc())

def add_camera_look_at_constraint(camera_actor, target_actor):
    # Simplified version of the helper
    settings = unreal.CameraLookatTrackingSettings()
    settings.enable_look_at_tracking = True
    settings.actor_to_track = target_actor
    camera_actor.set_editor_property('lookat_tracking_settings', settings)

if __name__ == "__main__":
    run_tandem_square()
