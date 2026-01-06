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
        "motion_includes.level_setup",
        "motion_includes.spline_setup",
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
    from motion_builder import CHARACTER_HEIGHT
    from motion_includes import cleanup
    from motion_includes import camera_setup
    from motion_includes import light_setup
    from motion_includes import mannequin_setup
    from motion_includes import sequence_setup
    from motion_includes import level_setup
    from motion_includes import keyframe_applier
    from motion_includes import attach_setup
    from motion_includes import spline_setup
    from motion_includes.assets import Shapes, Materials
    
    log(f"")
    log(f"{'='*60}")
    log(f"RUNNING TRACK-BASED SCENE: {os.path.basename(movie_folder)}")
    log(f"{'='*60}")
    
    # Setup explicit log file
    log_file_path = r"C:\Users\user\.gemini\antigravity\brain\ff952b7b-4239-4432-aaa1-ff80339214a1\execution.log"
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
    log("\n" + "="*60)
    log("CLEANUP PHASE")
    log("="*60)
    try:
        cleanup.close_open_sequences()
        log("[OK] Cleanup: close_open_sequences() completed")
    except Exception as e:
        log(f"✗ Cleanup: close_open_sequences() failed: {e}")
    
    try:
        cleanup.delete_old_actors()
        log("[OK] Cleanup: delete_old_actors() completed")
    except Exception as e:
        log(f"✗ Cleanup: delete_old_actors() failed: {e}")
    
    # 3. Process scene commands (atmosphere, fog, etc.)
    scene_commands_path = os.path.join(movie_folder, "scene.json")
    if os.path.exists(scene_commands_path):
        log("\n" + "="*60)
        log("SCENE COMMANDS PHASE")
        log("="*60)
        try:
            with open(scene_commands_path, 'r', encoding='utf-8') as f:
                scene_commands = json.load(f)
            
            for cmd in scene_commands:
                command_type = cmd.get("command")
                
                if command_type == "add_atmosphere":
                    log(f"  Processing add_atmosphere command")
                    try:
                        level_setup.apply_atmosphere_settings(cmd)
                        log(f"    [OK] Atmosphere settings applied")
                    except Exception as atmo_error:
                        log(f"    ✗ Atmosphere settings failed: {atmo_error}")
                        import traceback
                        traceback.print_exc()
                    
                elif command_type == "animate_fog":
                    log(f"  Processing animate_fog command (deferred until sequence creation)")
                    # Store for later processing after sequence is created
                    if not hasattr(run_scene, '_deferred_fog_animations'):
                        run_scene._deferred_fog_animations = []
                    run_scene._deferred_fog_animations.append(cmd)
                    
                elif command_type == "configure_light_shafts":
                    log(f"  Processing configure_light_shafts for {cmd.get('actor')}")
                    # Will be applied when light is created
                    
                else:
                    log(f"  [WARN] Unknown scene command: {command_type}")
        except Exception as e:
            log(f"  ✗ Failed to process scene commands: {e}")
            import traceback
            traceback.print_exc()
    
    # 4. Create level sequence
    log("\n" + "="*60)
    log("SEQUENCE CREATION PHASE")
    log("="*60)
    try:
        result = sequence_setup.create_sequence(fps=fps, duration_seconds=30, test_name=scene_name)
        sequence = result[0]
        
        if not sequence:
            log("✗ Failed to create sequence - returned None")
            return False
        log("✓ Sequence created successfully")
    except Exception as seq_error:
        log(f"✗ Sequence creation failed with error: {seq_error}")
        import traceback
        traceback.print_exc()
        return False
    
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    
    # 4. Plan motion - process track files
    log("\n" + "="*60)
    log("MOTION PLANNING PHASE")
    log("="*60)
    try:
        keyframe_data_all = motion_planner.plan_motion(movie_folder)
        log("✓ Motion planning completed")
    except Exception as plan_error:
        log(f"✗ Motion planning failed: {plan_error}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Create actors and cameras, apply keyframes
    actors_info = {}
    total_frames = 0
    
    for actor_name in actor_names:
        actor_folder = os.path.join(movie_folder, actor_name)
        if not os.path.exists(actor_folder):
            log(f"  [WARN] Folder not found for {actor_name}")
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
                log(f"  [WARN] Failed to load settings for {actor_name}: {e}")
        
        actor_obj = None
        binding = None
        
        # Logic for dispatching based on properties and type
        if actor_type == "camera" or "fov" in settings:
             log(f"  Creating camera: {actor_name}")
             fov = settings.get("fov", 90.0)
             debug_visible = settings.get("debug_visible", False)
             actor_obj = camera_setup.create_camera(actor_name, location=location, rotation=rotation, fov=fov, debug_visible=debug_visible)
             
        elif actor_type == "light" or "light_type" in settings:
             log(f"  Creating Light: {actor_name}")
             actor_obj = light_setup.create_light(actor_name, location, rotation, settings)
             
        elif actor_type == "marker":
             log(f"  Creating marker: {actor_name}")
             mesh_path = settings.get("mesh_path", Shapes.CYLINDER)
             mesh_scale = settings.get("mesh_scale", (0.1, 0.1, 0.1))
             
             actor_obj = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
             if actor_obj:
                 actor_obj.set_actor_label(actor_name)
                 actor_obj.tags.append("MotionSystemActor")
                 mesh_asset = unreal.load_object(None, mesh_path)
                 if mesh_asset:
                     actor_obj.static_mesh_component.set_static_mesh(mesh_asset)
                     actor_obj.set_actor_scale3d(unreal.Vector(*mesh_scale))
                     color_name = settings.get("color", "Blue")
                     mat_path = Materials.get_color(color_name)
                     mat = unreal.load_object(None, mat_path)
                     if mat:
                         actor_obj.static_mesh_component.set_material(0, mat)
                     log(f"    [OK] Marker created with {mesh_path}")
                     if mat:
                         actor_obj.static_mesh_component.set_material(0, mat)
                     log(f"    [OK] Marker created with {mesh_path}")
        
        elif actor_type == "spline":
             log(f"  Creating Spline: {actor_name}")
             # Get properties
             # Get properties (handle top-level or nested)
             props = settings.get("properties", {})
             points = settings.get("points") or props.get("points", [])
             closed = settings.get("closed") if "closed" in settings else props.get("closed", False)
             color = settings.get("color") or props.get("color", "Green")
             thickness = settings.get("thickness") or props.get("thickness", 5.0)
             show_debug = settings.get("show_debug") if "show_debug" in settings else props.get("show_debug", True)
             
             try:
                 actor_obj = spline_setup.create_spline_actor(
                     actor_name, 
                     points=points, 
                     closed=closed, 
                     color=color, 
                     thickness=thickness, 
                     show_debug=show_debug
                 )
                 log(f"    [OK] Spline created with {len(points)} points")
             except Exception as e:
                 log(f"    ❌ Failed to create spline {actor_name}: {e}")
                 import traceback
                 log(traceback.format_exc())



        else:
             # Default to mannequin for "actor" type or others
             log(f"  Creating actor: {actor_name}")
             
             # Extract from properties if nested
             props = settings.get("properties", {})
             mesh_path = props.get("mesh_path") or settings.get("mesh_path")
             
             try:
                 actor_obj = mannequin_setup.create_mannequin(actor_name, location, rotation, mesh_path=mesh_path)
             except Exception as e:
                 log(f"  ❌ Failed to create mannequin {actor_name}: {e}")
                 import traceback
                 try:
                     with open(log_file_path, 'a') as f:
                        traceback.print_exc(file=f)
                 except:
                    traceback.print_exc()

        if actor_obj:
            binding = sequence_setup.add_actor_to_sequence(sequence, actor_obj, actor_name)
            
            # CRITICAL: Enable LookAt tracking AFTER binding to sequence
            if "fov" in settings and ("look_at_timeline" in settings or "look_at_actor" in settings):
                log(f"    -> Enabling LookAt tracking (post-binding)...")
                try:
                    timeline = settings.get("look_at_timeline", [])
                    if timeline:
                        first_segment = timeline[0]
                        if first_segment.get("start_time", 0) <= 0:
                            target_name = first_segment.get("actor")
                            if target_name in actors_info:
                                target_actor = actors_info[target_name]["actor"]
                                cam_loc = actor_obj.get_actor_location()
                                target_loc = target_actor.get_actor_location()
                                
                                # Calculate and set LookAt rotation
                                look_at_rot = unreal.MathLibrary.find_look_at_rotation(cam_loc, target_loc)
                                actor_obj.set_actor_rotation(look_at_rot, False)
                                log(f"    [OK] Snapped initial rotation to {target_name} ({look_at_rot})")
                    
                    # Enable Tracking
                    tracking_settings = actor_obj.get_editor_property("lookat_tracking_settings")
                    tracking_settings.set_editor_property("enable_look_at_tracking", True)
                    
                    # Set interp speed
                    interp_speed = settings.get("look_at_interp_speed", 5.0)
                    tracking_settings.set_editor_property("look_at_tracking_interp_speed", interp_speed)
                    
                    actor_obj.set_editor_property("lookat_tracking_settings", tracking_settings)
                    log(f"    [OK] LookAt tracking enabled (interp_speed: {interp_speed})")
                except Exception as e:
                    log(f"    [WARN] Failed to enable LookAt tracking: {e}")
                    import traceback
                    log(traceback.format_exc())
            
            
            # Load attach.json if it exists
            attach_path = os.path.join(actor_folder, "attach.json")
            attachment_data = None
            if os.path.exists(attach_path):
                try:
                    with open(attach_path, 'r', encoding='utf-8') as f:
                        attach_sections = json.load(f)
                    if attach_sections:  # Non-empty list
                        attachment_data = attach_sections[0]  # First section
                        log(f"    -> Attachment to: {attachment_data.get('parent_actor')}")
                except Exception as e:
                    log(f"    [WARN] Failed to load attach.json: {e}")
            
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
    
    # POST-CREATION VALIDATION: Verify auto-tracking is enabled in Unreal sequence
    log(f"")
    log(f"{'='*60}")
    log(f"POST-CREATION VALIDATION")
    log(f"{'='*60}")
    for actor_name in actors_info:
        actor_folder = os.path.join(movie_folder, actor_name)
        settings_path = os.path.join(actor_folder, "settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Check if this is a camera with auto-tracking
                if "fov" in settings:
                    camera_obj = actors_info[actor_name]["actor"]
                    
                    # Validate LookAt tracking
                    if "look_at_timeline" in settings or "look_at_actor" in settings:
                        try:
                            tracking_settings = camera_obj.get_editor_property("lookat_tracking_settings")
                            is_enabled = tracking_settings.get_editor_property("enable_look_at_tracking")
                            
                            if is_enabled:
                                target = tracking_settings.get_editor_property("actor_to_track")
                                target_name = target.get_actor_label() if target else "None"
                                log(f"  [OK] Camera '{actor_name}': LookAt tracking ENABLED (target: {target_name})")
                            else:
                                log(f"  ❌ Camera '{actor_name}': LookAt tracking DISABLED (expected ENABLED)")
                                log(f"     WARNING: Auto-tracking may not work correctly!")
                        except Exception as e:
                            log(f"  [WARN] Camera '{actor_name}': Could not verify LookAt tracking: {e}")
                    
                    # Validate Focus tracking
                    if "focus_on_timeline" in settings:
                        try:
                            camera_component = camera_obj.get_cine_camera_component()
                            focus_settings = camera_component.focus_settings
                            focus_method = focus_settings.focus_method
                            
                            if focus_method == unreal.CameraFocusMethod.TRACKING:
                                log(f"  [OK] Camera '{actor_name}': Focus tracking ENABLED (method: TRACKING)")
                            else:
                                log(f"  [WARN] Camera '{actor_name}': Focus method is {focus_method} (expected TRACKING)")
                        except Exception as e:
                            log(f"  [WARN] Camera '{actor_name}': Could not verify Focus tracking: {e}")
            except Exception as e:
                log(f"  [WARN] Failed to validate {actor_name}: {e}")
    
    log(f"{'='*60}")
    log(f"")
    
    # Process attachments AFTER all actors are spawned
    log(f"")
    log(f"Processing attachments...")
    attach_setup.process_attachments(sequence, actors_info, fps)
    
    # 6. Apply keyframes to each actor
    for actor_name, data in keyframe_data_all.get("actors", {}).items():
        if actor_name in actors_info:
            actor_obj = actors_info[actor_name]["actor"]
            anim_binding = None
            if data.get("keyframes", {}).get("animations"):
                # For non-SkeletalMeshActors (e.g. Blueprints), we need to bind the SkeletalMeshComponent directly
                if actor_obj and not isinstance(actor_obj, unreal.SkeletalMeshActor):
                    # Iterate components to find SkeletalMeshComponent
                    comps = actor_obj.get_components_by_class(unreal.SkeletalMeshComponent)
                    if comps and len(comps) > 0:
                        skel_comp = comps[0]
                        log(f"    Binding component {skel_comp.get_name()} for animation...")
                        anim_binding = sequence.add_possessable(skel_comp)
                        if anim_binding:
                            # Parent it to the actor binding? Not strictly necessary for Possessables unless we want hierarchy
                            # Sequencer UI handles possessables at root usually fine
                            # But logical parenting helps organization
                            anim_binding.set_parent(actors_info[actor_name]["binding"])
                        else:
                            log(f"    ⚠ Failed to bind component, falling back")

            log(f"  Applying keyframes to: {actor_name}")
            keyframe_applier.apply_keyframes_to_actor(
                actor_name,
                actors_info[actor_name]["actor"],
                actors_info[actor_name]["binding"],
                data,
                fps,
                total_frames,
                sequence=sequence,
                anim_binding=anim_binding
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
                    
                    # CRITICAL: Adjust lens limits to prevent clamping of telephoto shots
                    max_kf_focal = max(kf["value"] for kf in focal_keyframes)
                    if max_kf_focal > 200.0: # Default max is often 120-200mm
                        log(f"    -> Adjusting lens limits (Max Focal Length: {max_kf_focal:.1f}mm)")
                        lens_settings = camera_component.lens_settings
                        lens_settings.max_focal_length = max_kf_focal + 100.0
                        camera_component.lens_settings = lens_settings
                    
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
                        log(f"    [OK] Applied {len(focal_keyframes)} focal length keyframes")
                    else:
                        log(f"    [WARN] Focal length track has no channels")
            except Exception as e:
                log(f"    [WARN] Failed to apply focal length: {e}")
        
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
                        
                        log(f"    [OK] Applied {len(settings['focus_on_timeline'])} Focus Tracking keyframes")
                    else:
                        log(f"    [WARN] Focus Tracking track has no channels")
                        
                    # Create Float Track for RelativeOffset.Z (Height Pct)
                    offset_track = comp_binding.add_track(unreal.MovieSceneFloatTrack)
                    offset_track.set_property_name_and_path("RelativeOffset.Z", "FocusSettings.TrackingFocusSettings.RelativeOffset.Z")
                    offset_section = offset_track.add_section()
                    offset_section.set_range(0, total_frames)
                    
                    channels = offset_section.get_all_channels()
                    if channels:
                        offset_channel = channels[0]
                        # Default offset (if no segments?) - maybe 0.
                        
                        for segment in settings["focus_on_timeline"]:
                            start_time = segment["start_time"]
                            height_pct = segment.get("height_pct", 0.7)
                            # Use standardized character height
                            offset_z = CHARACTER_HEIGHT * height_pct
                            
                            frame_number = unreal.FrameNumber(value=int(start_time * fps))
                            offset_channel.add_key(frame_number, offset_z)
                        
                        log(f"    [OK] Applied {len(settings['focus_on_timeline'])} Focus Offset keyframes")
            except Exception as e:
                log(f"    [WARN] Failed to apply Focus Tracking: {e}")
    
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
                        
                        log(f"    [OK] Applied {len(settings['look_at_timeline'])} LookAt target keyframes")
                    else:
                        log(f"    [WARN] LookAt track has no channels")
                        
                    # Create Float Track for RelativeOffset.Z (Height Pct)
                    # LookAt settings are on the Camera Component, but previous code used 'binding' (Actor).
                    # 'LookAtTrackingSettings' is likely exposed on Actor or we should use Component.
                    # To be safe, let's try 'binding' as before, but note it might need Component binding if Actor proxy fails.
                    # Actually, 'binding' corresponds to CineCameraActor. 
                    
                    offset_track = binding.add_track(unreal.MovieSceneFloatTrack)
                    offset_track.set_property_name_and_path("RelativeOffset.Z", "LookAtTrackingSettings.RelativeOffset.Z")
                    offset_section = offset_track.add_section()
                    offset_section.set_range(0, total_frames)
                    
                    channels = offset_section.get_all_channels()
                    if channels:
                        offset_channel = channels[0]
                        
                        for segment in settings["look_at_timeline"]:
                            start_time = segment["start_time"]
                            height_pct = segment.get("height_pct", 0.7)
                            offset_z = CHARACTER_HEIGHT * height_pct
                            
                            frame_number = unreal.FrameNumber(value=int(start_time * fps))
                            offset_channel.add_key(frame_number, offset_z)
                            
                        log(f"    [OK] Applied {len(settings['look_at_timeline'])} LookAt Offset keyframes")
            except Exception as e:
                log(f"    [WARN] Failed to apply LookAt tracking: {e}")
    
    
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
        log("[OK] Viewport locked to camera cuts")
    except Exception as e:
        log(f"[WARN] Warning: Could not lock viewport: {e}")
    
    import time
    time.sleep(0.5)
    
    try:
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        log("[OK] Sequence playing from frame 0")
    except Exception as e:
        log(f"[WARN] Warning: Could not play sequence: {e}")
    
    log(f"{'='*60}")
    log(f"SCENE EXECUTION COMPLETE")
    log(f"{'='*60}")
    
    return True


if __name__ == "__main__":
    # For testing outside Unreal
    folder = os.environ.get("MOVIE_FOLDER_PATH", "dist/test/")
    print(f"Would run scene from: {folder}")
