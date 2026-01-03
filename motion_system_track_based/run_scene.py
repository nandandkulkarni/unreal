"""
Run Scene - Unreal-side execution script (Track-Based)

This script is executed inside Unreal Engine via Remote Control.
It orchestrates the motion planning and sequence creation from track files.

Environment:
    MOVIE_FOLDER_PATH: Path to movie folder (set by trigger_movie.py)
"""

import unreal
import json
import os
import sys
import importlib

# Add motion_system_track_based to path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = r"C:\UnrealProjects\Coding\unreal\motion_system_track_based"

# Insert at beginning to override any other logger modules
if script_dir in sys.path:
    sys.path.remove(script_dir)
sys.path.insert(0, script_dir)


def log(message):
    """Log to both console and Unreal"""
    print(message)
    unreal.log(message)


def reload_modules():
    """Reload all motion system modules to pick up changes"""
    # First, ensure our logger is imported
    import logger as motion_logger
    sys.modules['logger'] = motion_logger
    
    modules_to_reload = [
        "motion_math",
        "motion_planner",
        "motion_includes.cleanup",
        "motion_includes.sequence_setup",
        "motion_includes.camera_setup",
        "motion_includes.mannequin_setup",
        "motion_includes.keyframe_applier",
        "motion_includes.light_setup",
        "motion_includes.attach_setup",
    ]
    
    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            try:
                importlib.reload(sys.modules[mod_name])
            except Exception as e:
                print(f"Warning: Could not reload {mod_name}: {e}")


def run_scene(movie_folder: str):
    """
    Main entry point for Unreal-side execution.
    
    Args:
        movie_folder: Absolute path to movie folder
    
    Process:
        1. Load meta.json for fps and duration
        2. Cleanup old actors
        3. Create level sequence
        4. Call motion_planner.plan_motion(movie_folder)
        5. Create actors and apply keyframes
        6. Add camera cuts
        7. Play sequence
    """
    reload_modules()
    
    import motion_planner
    from motion_includes import cleanup, sequence_setup, camera_setup, mannequin_setup, keyframe_applier, light_setup, attach_setup
    
    log(f"")
    log(f"{'='*60}")
    log(f"RUNNING TRACK-BASED SCENE: {os.path.basename(movie_folder)}")
    log(f"{'='*60}")
    
    # 1. Load meta.json
    meta_path = os.path.join(movie_folder, "meta.json")
    if not os.path.exists(meta_path):
        log(f"✗ meta.json not found in {movie_folder}")
        return False
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    scene_name = meta.get("name", "Untitled_Scene")
    fps = meta.get("fps", 60)
    actor_names = meta.get("actors", [])
    
    log(f"Scene: {scene_name}")
    log(f"FPS: {fps}")
    log(f"Actors: {actor_names}")
    
    # 2. Cleanup old state
    cleanup.close_open_sequences()
    cleanup.delete_old_actors()
    
    # 3. Create level sequence
    result = sequence_setup.create_sequence(fps=fps, duration_seconds=30, test_name=scene_name)
    sequence = result[0]
    
    if not sequence:
        log("✗ Failed to create sequence")
        return False
    
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    
    # 4. Plan motion - process track files
    keyframe_data_all = motion_planner.plan_motion(movie_folder)
    
    # 5. Create actors and cameras, apply keyframes
    actors_info = {}
    total_frames = 0
    
    for actor_name in actor_names:
        actor_folder = os.path.join(movie_folder, actor_name)
        if not os.path.exists(actor_folder):
            log(f"  ⚠ Folder not found for {actor_name}")
            continue
        
        # Load initial state from transform track
        transform_path = os.path.join(actor_folder, "transform.json")
        location = unreal.Vector(0, 0, 0)
        rotation = unreal.Rotator(0, 0, 0)
        
        if os.path.exists(transform_path):
            with open(transform_path, 'r', encoding='utf-8') as f:
                transform_data = json.load(f)
            
            if transform_data:
                first_kf = transform_data[0]
                location = unreal.Vector(first_kf.get("x", 0), first_kf.get("y", 0), first_kf.get("z", 0))
                rotation = unreal.Rotator(
                    pitch=first_kf.get("pitch", 0),
                    yaw=first_kf.get("yaw", 0),
                    roll=first_kf.get("roll", 0)
                )
                
                # Track max frames
                for kf in transform_data:
                    total_frames = max(total_frames, kf.get("frame", 0))

        # Check for settings to determine type
        settings_path = os.path.join(actor_folder, "settings.json")
        actor_type = "mannequin" # default
        settings = {}
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    actor_type = settings.get("actor_type", "camera") # Assume camera if settings exists but no type
            except Exception as e:
                log(f"  ⚠ Failed to load settings for {actor_name}: {e}")
        
        actor_obj = None
        binding = None
        
        if actor_type == "camera":
            # Create camera
            log(f"  Creating camera: {actor_name}")
            actor_obj = camera_setup.create_camera(actor_name, location=location, rotation=rotation)
            
        elif actor_type == "light":
            # Create light
            # Light properties are in 'properties' key of settings usually? 
            # ActorTrackSet puts type in top level or properties?
            # Let's check LightBuilder again. 
            # track_set.initial_state["properties"] has the details.
            # But settings.json usually contains the 'properties' dict.
            # Wait, ActorTrackSet.to_dict(): 'settings.json' = self.initial_state["properties"]
            # But 'actor_type' is passed to ActorTrackSet init. 
            # ActorTrackSet.to_dict puts actor_type in meta.json? No, meta just lists names.
            # ActorTrackSet writes type WHERE?
            # Im motion_builder.py, ActorTrackSet doesn't seem to write type explicitly to settings unless in properties!
            # LightBuilder puts 'light_type' in properties.
            # So settings.json will have "light_type".
            # But how do we distinguish from Camera (which has "fov")?
            
            # Update: I will check 'light_type' key in settings.
            if "light_type" in settings:
                log(f"  Creating Light: {actor_name}")
                actor_obj = light_setup.create_light(actor_name, location, rotation, settings)
            else:
                # Fallback logic
                pass
                
        elif actor_type == "mannequin":
            # Create mannequin actor
            log(f"  Creating actor: {actor_name}")
            actor_obj = mannequin_setup.create_mannequin(actor_name, location, rotation)

        # Logic for dispatching based on properties
        if "light_type" in settings:
             actor_obj = light_setup.create_light(actor_name, location, rotation, settings)
        elif "fov" in settings or actor_type=="camera":
             fov = settings.get("fov", 90.0)
             debug_visible = settings.get("debug_visible", False)
             actor_obj = camera_setup.create_camera(actor_name, location=location, rotation=rotation, fov=fov, debug_visible=debug_visible)
        else:
             actor_obj = mannequin_setup.create_mannequin(actor_name, location, rotation)

        if actor_obj:
            binding = sequence_setup.add_actor_to_sequence(sequence, actor_obj, actor_name)
            
            # Load attach.json if it exists
            attach_path = os.path.join(actor_folder, "attach.json")
            attachment_data = None
            if os.path.exists(attach_path):
                try:
                    with open(attach_path, 'r', encoding='utf-8') as f:
                        attach_sections = json.load(f)
                    if attach_sections:  # Non-empty list
                        attachment_data = attach_sections[0]  # First section
                        log(f"    → Attachment to: {attachment_data.get('parent_actor')}")
                except Exception as e:
                    log(f"    ⚠ Failed to load attach.json: {e}")
            
            actors_info[actor_name] = {
                "actor": actor_obj,
                "binding": binding,
                "location": location,
                "rotation": rotation,
                "attachment": attachment_data
            }
    # Add buffer frames
    total_frames += 60
    sequence.set_playback_end(total_frames)
    
    # Process attachments AFTER all actors are spawned
    log(f"")
    log(f"Processing attachments...")
    attach_setup.process_attachments(sequence, actors_info, fps)
    
    # 6. Apply keyframes to each actor
    for actor_name, data in keyframe_data_all.get("actors", {}).items():
        if actor_name in actors_info:
            log(f"  Applying keyframes to: {actor_name}")
            keyframe_applier.apply_keyframes_to_actor(
                actor_name,
                actors_info[actor_name]["actor"],
                actors_info[actor_name]["binding"],
                data,
                fps,
                total_frames,
                sequence=sequence
            )
    
    # 7. Apply camera cuts
    camera_cuts = keyframe_data_all.get("camera_cuts", [])
    if camera_cuts:
        log(f"  Applying {len(camera_cuts)} camera cut(s)")
        # Convert time-based cuts to frame-based
        frame_cuts = []
        for cut in camera_cuts:
            frame_cuts.append({
                "frame": int(cut["time"] * fps),
                "camera": cut["camera"]
            })
        sequence_setup.apply_camera_cuts(sequence, frame_cuts, actors_info, fps)
    
    # 8. Save and play
    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    
    try:
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        log("✓ Viewport locked to camera cuts")
    except Exception as e:
        log(f"⚠ Warning: Could not lock viewport: {e}")
    
    import time
    time.sleep(0.5)
    
    try:
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        log("✓ Sequence playing from frame 0")
    except Exception as e:
        log(f"⚠ Warning: Could not play sequence: {e}")
    
    log(f"{'='*60}")
    log(f"SCENE EXECUTION COMPLETE")
    log(f"{'='*60}")
    
    return True


if __name__ == "__main__":
    # For testing outside Unreal
    folder = os.environ.get("MOVIE_FOLDER_PATH", "dist/test/")
    print(f"Would run scene from: {folder}")
