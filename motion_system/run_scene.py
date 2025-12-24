"""
Script to run motion scenes from JSON files.
This makes it easy to author sequences without writing Python code.
"""
import unreal
import json
import os
import sys

# Handle path for remote execution where __file__ might be missing
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system"

parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from motion_system import logger, cleanup, sequence_setup, camera_setup, mannequin_setup, motion_planner, keyframe_applier

def run_scene(json_path):
    """Load and run a scene from a JSON file"""
    
    # Robust reload for all motion_system modules
    import importlib
    import sys
    
    modules_to_reload = [
        "logger", "cleanup", "sequence_setup", "camera_setup", 
        "mannequin_setup", "motion_planner", "keyframe_applier", "debug_db"
    ]
    
    for mod_name in modules_to_reload:
        # Reload both top-level and package-level names if they exist
        for full_name in [mod_name, f"motion_system.{mod_name}"]:
            if full_name in sys.modules:
                try:
                    importlib.reload(sys.modules[full_name])
                except Exception as e:
                    print(f"Warning: Could not reload {full_name}: {e}")

    logger.log_header(f"RUNNING SCENE: {os.path.basename(json_path)}")
    
    if not os.path.exists(json_path):
        logger.log(f"✗ File not found: {json_path}")
        return

    try:
        with open(json_path, 'r') as f:
            scene_data = json.load(f)
    except Exception as e:
        logger.log(f"✗ Failed to parse JSON: {e}")
        return

    scene_name = scene_data.get("name", "Untitled_Scene")
    fps = scene_data.get("fps", 30)
    plan = scene_data.get("plan", [])
    
    logger.log(f"Scene: {scene_name}")
    logger.log(f"FPS: {fps}")
    logger.log(f"Commands: {len(plan)}")
    
    # Cleanup old actors only if requested or generic cleanup?
    # For movie making, maybe we want to keep previous stuff?
    # But current system relies on exclusive control.
    cleanup.close_open_sequences()
    cleanup.delete_old_actors() # This might be aggressive if user has set dressing?
    # Update cleanup to only delete Test* or Spawned* actors? We did that.
    
    # Create Sequence
    # sequence_setup.create_sequence signature: (fps=30, duration_seconds=60, test_name=None)
    # returns: (sequence, name, num, fps, frames)
    result = sequence_setup.create_sequence(fps=fps, test_name=scene_name)
    sequence = result[0]
    
    if not sequence:
        logger.log("✗ Failed to create sequence")
        return
        
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    
    # Initialize trackers
    actors_info = {}
    
    # 1. Plan Motion (Generate Keyframes)
    keyframe_data_all = motion_planner.plan_motion(plan, actors_info, fps, sequence=sequence)
    
    # 2. Apply Keyframes to Sequencer
    binding_map = {name: info["binding"] for name, info in actors_info.items()}
    
    # Calculate total duration
    total_frames = 0
    for actor_name, data in keyframe_data_all.items():
        keys = data["keyframes"]["location"]
        if keys:
            total_frames = max(total_frames, keys[-1]["frame"])
            
    # Add buffer
    total_frames += 30 
    
    # Set sequence playback range
    sequence.set_playback_end(total_frames)
    
    for actor_name, keyframe_data in keyframe_data_all.items():
        if actor_name in binding_map:
            actor = actors_info[actor_name]["actor"]
            keyframe_applier.apply_keyframes_to_actor(
                actor_name, 
                actor, 
                binding_map[actor_name], 
                keyframe_data, 
                fps, 
                total_frames
            )
            
    logger.log_header("SCENE GENERATION COMPLETE")

if __name__ == "__main__":
    # Check for environment variable passed from trigger
    json_path = os.environ.get("MOVIE_JSON_PATH")
    
    if not json_path:
        # Fallback to default
        json_path = os.path.join(script_dir, "movies", "scene_01.json")
        
    run_scene(json_path)
