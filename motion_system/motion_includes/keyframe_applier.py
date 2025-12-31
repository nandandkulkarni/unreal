"""
Keyframe Applier - Pass 2: Apply keyframe data to Unreal

Takes structured keyframe data and creates actual Unreal sequencer keyframes.
"""
import unreal
import logger
from logger import log


def apply_keyframes_to_actor(actor_name, actor, binding, keyframe_data, fps, duration_frames, sequence=None):
    """
    Apply keyframe data to an actor in the sequence
    
    Args:
        actor_name: Name of the actor
        actor: The Unreal actor object
        binding: MovieSceneBindingProxy
        keyframe_data: Dict with "keyframes" and "waypoints"
        fps: Frames per second
        duration_frames: Total sequence duration in frames
    """
    # Setup file logging
    import os
    log_file_path = os.path.join(r"C:\UnrealProjects\Coding\unreal\motion_system\dist", "motion_application.log")
    
    def file_log(message):
        try:
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
        except:
            pass
            
    # Clear log on first call for a scene (heuristic)
    # Actually just append, we can check timestamps or just new entries
    file_log(f"\n=== Keyframe Application Start ===")
    

    
    log(f"\n{'='*60}")
    log(f"APPLYING KEYFRAMES: {actor_name}")
    log(f"{'='*60}")
    file_log(f"Processing actor: {actor_name}") # Added this line based on the spirit of the request
    
    keyframes = keyframe_data["keyframes"]
    loc_keys = keyframes.get("location", [])
    rot_keys = keyframes.get("rotation", [])
    
    file_log(f"  Location keys: {len(loc_keys)}, Rotation keys: {len(rot_keys)}") # Added this line
    
    # Only click create transform track if we have keys to apply
    # Otherwise, an empty track might reset the actor to 0,0,0
    # Location/Rotation track
    if loc_keys or rot_keys:
        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            binding,
            unreal.MovieScene3DTransformTrack
        )
        
        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            log(f"✓ Transform track created")
            
            # Apply location and rotation keyframes
            apply_transform_keyframes(section, keyframes, actor_name)
    else:
        log(f"  (Skipping transform track: no keyframes for {actor_name})")
    
    # Focal Length Track (Smart Zoom)
    focal_keys = keyframes.get("current_focal_length", [])
    if focal_keys and isinstance(actor, unreal.CineCameraActor) and sequence:
        log(f"  Applying {len(focal_keys)} Focal Length keyframes (Component Property Binding)...")
        
        try:
            # 1. Get the component
            component = actor.get_cine_camera_component()
            
            # 2. Add component to sequence (possessable)
            # Use MovieSceneSequenceExtensions for better stability in 5.7
            comp_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, component)
            if comp_binding:
                comp_binding.set_parent(binding)
                
                # 3. Use FloatPropertyTrack specifically for properties
                # This class is often more stable for "CurrentFocalLength"
                track_class = unreal.MovieSceneFloatTrack
                if hasattr(unreal, "MovieSceneFloatPropertyTrack"):
                    track_class = unreal.MovieSceneFloatPropertyTrack
                
                fl_track = unreal.MovieSceneBindingExtensions.add_track(comp_binding, track_class)
                
                if fl_track:
                    # On the component, the path is just the property name
                    fl_track.set_property_name_and_path("CurrentFocalLength", "CurrentFocalLength")
                    
                    section = unreal.MovieSceneTrackExtensions.add_section(fl_track)
                    unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
                    
                    channels = section.get_all_channels()
                    if channels:
                        fl_channel = channels[0]
                        for key in focal_keys:
                            frame = unreal.FrameNumber(key["frame"])
                            key_obj = fl_channel.add_key(frame, float(key["value"]))
                            
                            # Use simple interpolation for now
                            if key_obj and hasattr(key_obj, 'set_interpolation'):
                                try:
                                    key_obj.set_interpolation(unreal.MovieSceneKeyInterpolation.USER)
                                except:
                                    pass
                        
                        log(f"  ✓ Applied {len(focal_keys)} keyframes to Focal Length track on component")
                    else:
                        log(f"  ⚠ Track section has no channels")
                else:
                    log(f"  ✗ Failed to create {track_class.__name__} on component")
            else:
                log(f"  ✗ Failed to bind CameraComponent to sequence")
        except Exception as e:
            log(f"  ⚠ Failed to apply Focal Length track: {e}")
            import traceback
            log(traceback.format_exc())
        
        channels = section.get_all_channels()
        fl_channel = channels[0]
        
        for key in focal_keys:
            frame = unreal.FrameNumber(key["frame"])
            val = float(key["value"])
            key_obj = fl_channel.add_key(frame, val)
            if hasattr(key_obj, 'set_interpolation'):
                 key_obj.set_interpolation(unreal.MovieSceneKeyInterpolation.CUBIC)
        
        log(f"  ✓ Focal Length track applied to {actor_name}'s CameraComponent")

    # Focus Distance Track (Manual Focus)
    focus_keys = keyframes.get("current_focus_distance", [])
    if focus_keys and isinstance(actor, unreal.CineCameraActor) and sequence:
        file_log(f"  Focus Distance keys: {len(focus_keys)}")
        log(f"  Applying {len(focus_keys)} Focus Distance keyframes...")
        
        try:
            component = actor.get_cine_camera_component()
            
            # Ensure Manual Focus Method is set
            focus_settings = component.get_editor_property("focus_settings")
            focus_settings.set_editor_property("focus_method", unreal.CameraFocusMethod.MANUAL)
            component.set_editor_property("focus_settings", focus_settings)
            
            # Add component binding if not already exists (reuse comp_binding idea)
            comp_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, component)
            if comp_binding:
                comp_binding.set_parent(binding)
                
                track_class = unreal.MovieSceneFloatTrack
                if hasattr(unreal, "MovieSceneFloatPropertyTrack"):
                    track_class = unreal.MovieSceneFloatPropertyTrack
                
                fd_track = unreal.MovieSceneBindingExtensions.add_track(comp_binding, track_class)
                
                if fd_track:
                    # The property path for Manual Focus Distance is nested in the struct
                    # FocusSettings.ManualFocusDistance
                    fd_track.set_property_name_and_path("ManualFocusDistance", "FocusSettings.ManualFocusDistance")
                    
                    section = unreal.MovieSceneTrackExtensions.add_section(fd_track)
                    unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
                    
                    channels = section.get_all_channels()
                    if channels:
                        fd_channel = channels[0]
                        for key in focus_keys:
                            frame = unreal.FrameNumber(key["frame"])
                            # Add keyframe
                            key_obj = fd_channel.add_key(frame, float(key["value"]))
                            
                            # Use cubic interpolation for smooth focus pulls
                            if hasattr(key_obj, 'set_interpolation'):
                                try:
                                    key_obj.set_interpolation(unreal.MovieSceneKeyInterpolation.CUBIC)
                                except:
                                    pass
                        
                        log(f"  ✓ Applied {len(focus_keys)} keyframes to Manual Focus Distance")
                        file_log(f"  ✓ Applied {len(focus_keys)} Focus keys")
                    else:
                        log(f"  ⚠ Focus Track section has no channels")
                else:
                    log(f"  ✗ Failed to create Focus Distance track")
        except Exception as e:
            log(f"  ⚠ Failed to apply Focus Distance track: {e}")
            import traceback
            log(traceback.format_exc())
    
    # Build Actor Map for resolving references (only once)
    actor_map = {}
    if "look_at_target" in keyframes or "focus_target" in keyframes:
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in all_actors:
            actor_map[a.get_actor_label()] = a
            
    # Look-At Target Track (Auto Tracking)
    look_at_keys = keyframes.get("look_at_target", [])
    if look_at_keys and isinstance(actor, unreal.CineCameraActor):
        log(f"  Applying {len(look_at_keys)} Look-At Target keyframes...")
        
        try:
            # Enable LookAt Tracking globally on the actor first
            tracking_settings = actor.get_editor_property("lookat_tracking_settings")
            tracking_settings.set_editor_property("enable_look_at_tracking", True)
            # Set default to first target to ensure it works immediately
            if look_at_keys and look_at_keys[0]["value"] in actor_map:
                tracking_settings.set_editor_property("actor_to_track", actor_map[look_at_keys[0]["value"]])
            actor.set_editor_property("lookat_tracking_settings", tracking_settings)
            
            # Create Object Property Track
            track_class = unreal.MovieSceneObjectPropertyTrack
            la_track = unreal.MovieSceneBindingExtensions.add_track(binding, track_class)
            
            if la_track:
                # Property path on CineCameraActor
                la_track.set_property_name_and_path("ActorToTrack", "LookAtTrackingSettings.ActorToTrack")
                
                section = unreal.MovieSceneTrackExtensions.add_section(la_track)
                unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
                
                channels = section.get_all_channels()
                if channels:
                    la_channel = channels[0] # Object channels
                    
                    for key in look_at_keys:
                        frame = unreal.FrameNumber(key["frame"])
                        target_name = key["value"]
                        target_actor = actor_map.get(target_name)
                        
                        if target_actor:
                            # Note: Object channel add_key takes (frame, object)
                            key_obj = la_channel.add_key(frame, target_actor)
                        else:
                            log(f"    ⚠ Could not find actor '{target_name}' for LookAt key")
                    
                    log(f"  ✓ Applied {len(look_at_keys)} Look-At Target keys")
                    file_log(f"  ✓ Applied {len(look_at_keys)} Look-At keys")
                else:
                    log(f"  ⚠ LookAt Track section has no channels")
        except Exception as e:
            log(f"  ⚠ Failed to apply Look-At keys: {e}")
            import traceback
            log(traceback.format_exc())

    # Focus Target Track (Auto Focus)
    focus_target_keys = keyframes.get("focus_target", [])
    if focus_target_keys and isinstance(actor, unreal.CineCameraActor) and sequence:
        log(f"  Applying {len(focus_target_keys)} Focus Target keyframes...")
        
        try:
            component = actor.get_cine_camera_component()
            
            # Ensure Tracking Focus Method is set
            focus_settings = component.get_editor_property("focus_settings")
            focus_settings.set_editor_property("focus_method", unreal.CameraFocusMethod.TRACKING)
            component.set_editor_property("focus_settings", focus_settings)
            
            # Add component binding
            comp_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, component)
            if comp_binding:
                comp_binding.set_parent(binding)
                
                track_class = unreal.MovieSceneObjectPropertyTrack
                ft_track = unreal.MovieSceneBindingExtensions.add_track(comp_binding, track_class)
                
                if ft_track:
                    # Nested property path
                    ft_track.set_property_name_and_path("ActorToTrack", "FocusSettings.TrackingFocusSettings.ActorToTrack")
                    
                    section = unreal.MovieSceneTrackExtensions.add_section(ft_track)
                    unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
                    
                    channels = section.get_all_channels()
                    if channels:
                        ft_channel = channels[0]
                        for key in focus_target_keys:
                            frame = unreal.FrameNumber(key["frame"])
                            target_name = key["value"]
                            target_actor = actor_map.get(target_name)
                            
                            if target_actor:
                                ft_channel.add_key(frame, target_actor)
                            else:
                                log(f"    ⚠ Could not find actor '{target_name}' for Focus key")
                        
                        log(f"  ✓ Applied {len(focus_target_keys)} Focus Target keys")
                        file_log(f"  ✓ Applied {len(focus_target_keys)} Focus keys")
                    else:
                        log(f"  ⚠ Focus Target Track section has no channels")
        except Exception as e:
            log(f"  ⚠ Failed to apply Focus Target keys: {e}")
            import traceback
            log(traceback.format_exc())

    # Apply animation keyframes (only for skeletal mesh actors)
    if hasattr(actor, 'skeletal_mesh_component') or isinstance(actor, unreal.SkeletalMeshActor):
        apply_animation_keyframes(binding, keyframes, duration_frames, actor_name)


def apply_transform_keyframes(section, keyframes, actor_name):
    """Apply location and rotation keyframes to transform section with smooth interpolation"""
    channels = section.get_all_channels()
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    
    # helper for adding smooth keys
    def add_smooth_key(channel, frame, value):
        key = channel.add_key(frame, float(value))
        if hasattr(key, 'set_interpolation'):
            key.set_interpolation(unreal.MovieSceneKeyInterpolation.CUBIC)
            if hasattr(key, 'set_tangent_mode'):
                key.set_tangent_mode(unreal.MovieSceneKeyTangentMode.AUTO)

    # Location keyframes
    loc_keys = keyframes.get("location", [])
    for key in loc_keys:
        frame = unreal.FrameNumber(key["frame"])
        add_smooth_key(location_channels[0], frame, key["x"])
        add_smooth_key(location_channels[1], frame, key["y"])
        add_smooth_key(location_channels[2], frame, key["z"])
    
    log(f"  ✓ Added {len(loc_keys)} location keyframes (Smooth/Cubic)")
    
    # Rotation keyframes
    rot_keys = keyframes.get("rotation", [])
    for key in rot_keys:
        frame = unreal.FrameNumber(key["frame"])
        add_smooth_key(rotation_channels[0], frame, key["roll"])
        add_smooth_key(rotation_channels[1], frame, key["pitch"])
        add_smooth_key(rotation_channels[2], frame, key["yaw"])
    
    log(f"  ✓ Added {len(rot_keys)} rotation keyframes (Smooth/Cubic)")


def apply_animation_keyframes(binding, keyframes, duration_frames, actor_name):
    """Apply animation sections to skeletal mesh"""
    anim_list = keyframes.get("animations", [])
    if not anim_list:
        return
    
    # Add skeletal animation track
    anim_track = unreal.MovieSceneBindingExtensions.add_track(
        binding,
        unreal.MovieSceneSkeletalAnimationTrack
    )
    
    if not anim_track:
        log(f"  ⚠ Could not create animation track for {actor_name}")
        return
    
    for anim_data in anim_list:
        anim_name = anim_data["name"]
        start_frame = anim_data["start_frame"]
        end_frame = anim_data.get("end_frame", duration_frames)
        
        # Create animation section
        anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
        unreal.MovieSceneSectionExtensions.set_range(anim_section, start_frame, end_frame)
        
        # Load animation
        # anim_path = f"/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/{anim_name}.{anim_name}"
        # TEMPORARY: Force Jog_Fwd as requested
        anim_path = "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/Jog_Fwd.Jog_Fwd"
        anim = unreal.load_object(None, anim_path)
        
        if anim:
            params = anim_section.params
            params.animation = anim
            log(f"  ✓ Animation '{anim_name}' [{start_frame}-{end_frame}]")
        else:
            log(f"  ⚠ Animation '{anim_name}' not found at {anim_path}")
    
    log(f"  ✓ Added {len(anim_list)} animation sections")
