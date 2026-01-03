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


import datetime

# Create timestamped log file
log_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = None

def log(message):
    """Log to console, Unreal, and local timestamped file"""
    global log_file_path
    
    # Initialize log file on first call
    if log_file_path is None:
        try:
            log_dir = os.path.join(script_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, f"run_scene_{log_timestamp}.log")
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            log_file_path = ""  # Disable file logging
    
    # Print to console and Unreal
    print(message)
    unreal.log(message)
    
    # Write to local log file
    if log_file_path:
        try:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")


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
             
             # Enable LookAt tracking if look_at timeline is present
             if actor_obj and "look_at_timeline" in settings:
                 try:
                     tracking_settings = actor_obj.get_editor_property("lookat_tracking_settings")
                     tracking_settings.set_editor_property("enable_look_at_tracking", True)
                     
                     # Set interp speed
                     interp_speed = settings.get("look_at_interp_speed", 5.0)
                     tracking_settings.set_editor_property("look_at_tracking_interp_speed", interp_speed)
                     
                     actor_obj.set_editor_property("lookat_tracking_settings", tracking_settings)
                     log(f"    ✓ LookAt tracking enabled (interp_speed: {interp_speed})")
                 except Exception as e:
                     log(f"    ⚠ Failed to enable LookAt tracking: {e}")
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
    
    # 7. Apply camera-specific keyframes (focal length, focus distance)
    for actor_name in actors_info:
        actor_folder = os.path.join(movie_folder, actor_name)
        
        # Check for focal_length.json
        focal_path = os.path.join(actor_folder, "focal_length.json")
        if os.path.exists(focal_path):
            try:
                with open(focal_path, 'r', encoding='utf-8') as f:
                    focal_keyframes = json.load(f)
                if focal_keyframes:
                    log(f"  Applying focal length keyframes to: {actor_name}")
                    camera_obj = actors_info[actor_name]["actor"]
                    binding = actors_info[actor_name]["binding"]
                    camera_component = camera_obj.get_cine_camera_component()
                    
                    # Create component binding (add component to sequence)
                    comp_binding = sequence.add_possessable(camera_component)
                    comp_binding.set_parent(binding)
                    
                    # Add focal length track to COMPONENT binding
                    focal_track = comp_binding.add_track(unreal.MovieSceneFloatTrack)
                    focal_track.set_property_name_and_path("CurrentFocalLength", "CurrentFocalLength")
                    focal_section = focal_track.add_section()
                    focal_section.set_range(0, total_frames)
                    
                    # Get channels and add keyframes
                    channels = focal_section.get_all_channels()
                    if channels:
                        focal_channel = channels[0]
                        for kf in focal_keyframes:
                            frame_number = unreal.FrameNumber(value=kf["frame"])
                            focal_channel.add_key(frame_number, kf["value"])
                        log(f"    ✓ Applied {len(focal_keyframes)} focal length keyframes")
                    else:
                        log(f"    ⚠ Focal length track has no channels")
            except Exception as e:
                log(f"    ⚠ Failed to apply focal length: {e}")
        
        # Check for focus_on timeline (use Tracking Focus mode, not manual distance)
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Check if focus_on timeline exists (stored in settings.json like look_at)
                if "focus_on_timeline" in settings:
                    log(f"  Applying Focus Tracking to: {actor_name}")
                    camera_obj = actors_info[actor_name]["actor"]
                    binding = actors_info[actor_name]["binding"]
                    camera_component = camera_obj.get_cine_camera_component()
                    
                    # Enable TRACKING focus mode (not MANUAL)
                    focus_settings = camera_component.focus_settings
                    focus_settings.focus_method = unreal.CameraFocusMethod.TRACKING
                    camera_component.focus_settings = focus_settings
                    
                    # Create component binding
                    comp_binding = sequence.add_possessable(camera_component)
                    comp_binding.set_parent(binding)
                    
                    # Create Object Property Track for ActorToTrack
                    focus_track = comp_binding.add_track(unreal.MovieSceneObjectPropertyTrack)
                    focus_track.set_property_name_and_path("ActorToTrack", "FocusSettings.TrackingFocusSettings.ActorToTrack")
                    focus_section = focus_track.add_section()
                    focus_section.set_range(0, total_frames)
                    
                    # Get channel and add keyframes
                    channels = focus_section.get_all_channels()
                    if channels:
                        focus_channel = channels[0]
                        
                        # Add keyframe for each timeline segment
                        for segment in settings["focus_on_timeline"]:
                            start_time = segment["start_time"]
                            target_actor_name = segment["actor"]
                            
                            if target_actor_name in actors_info:
                                frame_number = unreal.FrameNumber(value=int(start_time * fps))
                                target_actor = actors_info[target_actor_name]["actor"]
                                focus_channel.add_key(frame_number, target_actor)
                        
                        log(f"    ✓ Applied {len(settings['focus_on_timeline'])} Focus Tracking keyframes")
                    else:
                        log(f"    ⚠ Focus Tracking track has no channels")
            except Exception as e:
                log(f"    ⚠ Failed to apply Focus Tracking: {e}")
    
    # 8. Apply LookAt tracking timelines
    for actor_name in actors_info:
        actor_folder = os.path.join(movie_folder, actor_name)
        settings_path = os.path.join(actor_folder, "settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if "look_at_timeline" in settings:
                    log(f"  Applying LookAt tracking to: {actor_name}")
                    camera_obj = actors_info[actor_name]["actor"]
                    binding = actors_info[actor_name]["binding"]
                    
                    # Create Object Property Track for ActorToTrack
                    la_track = binding.add_track(unreal.MovieSceneObjectPropertyTrack)
                    la_track.set_property_name_and_path("ActorToTrack", "LookAtTrackingSettings.ActorToTrack")
                    la_section = la_track.add_section()
                    la_section.set_range(0, total_frames)
                    
                    # Get channel and add keyframes
                    channels = la_section.get_all_channels()
                    if channels:
                        la_channel = channels[0]
                        
                        # Add keyframe for each timeline segment
                        for segment in settings["look_at_timeline"]:
                            start_time = segment["start_time"]
                            target_actor_name = segment["actor"]
                            
                            if target_actor_name in actors_info:
                                frame_number = unreal.FrameNumber(value=int(start_time * fps))
                                target_actor = actors_info[target_actor_name]["actor"]
                                la_channel.add_key(frame_number, target_actor)
                        
                        log(f"    ✓ Applied {len(settings['look_at_timeline'])} LookAt target keyframes")
                    else:
                        log(f"    ⚠ LookAt track has no channels")
            except Exception as e:
                log(f"    ⚠ Failed to apply LookAt tracking: {e}")
    
    
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
