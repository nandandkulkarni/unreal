"""
Motion Command System - Translate high-level movement commands to keyframes

Supports commands like:
- "forward 500cm over 5 seconds" 
- "left 300cm" 
- Direction-based movement relative to character facing

This replaces manual keyframe calculation with intent-based motion planning.
"""
import unreal
from logger import log, log_header


def add_camera_to_sequence(sequence, camera, fps, duration_seconds):
    """Add camera to sequence with camera cut track"""
    log_header("STEP 5: Adding camera to sequence")

    camera_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, camera)

    if camera_binding:
        log(f"✓ Camera added to sequence: {str(camera_binding.get_display_name())}")

        # Add camera cut track
        camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
        camera_cut_section = camera_cut_track.add_section()
        
        camera_cut_duration_frames = int(fps * duration_seconds)
        camera_cut_section.set_range(0, camera_cut_duration_frames)
        log(f"  Camera cut duration: {duration_seconds}s ({camera_cut_duration_frames} frames)")

        # Set camera binding
        try:
            binding_id = unreal.MovieSceneObjectBindingID()
            binding_id.set_editor_property('guid', camera_binding.get_id())
            camera_cut_section.set_camera_binding_id(binding_id)
            log("✓ Camera cut track added with binding")
        except Exception as e:
            log(f"⚠ Warning: Could not set camera binding: {e}")

        return camera_binding
    else:
        log("⚠ Warning: Failed to add camera binding")
        return None


def add_camera_with_motion(sequence, camera, fps, duration_frames, keyframe_data):
    """Add camera to sequence with motion keyframes"""
    log_header("STEP 5: Adding camera with motion")
    
    camera_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, camera)
    
    if not camera_binding:
        log("⚠ Warning: Failed to add camera binding")
        return None
        
    log(f"✓ Camera added to sequence: {str(camera_binding.get_display_name())}")

    # Add camera cut track
    camera_cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    camera_cut_section = camera_cut_track.add_section()
    camera_cut_section.set_range(0, duration_frames)
    
    # Set camera binding
    try:
        binding_id = unreal.MovieSceneObjectBindingID()
        binding_id.set_editor_property('guid', camera_binding.get_id())
        camera_cut_section.set_camera_binding_id(binding_id)
        log("✓ Camera cut track added")
    except Exception as e:
        log(f"⚠ Warning: Could not set camera binding: {e}")

    # Apply Transform Keyframes
    if keyframe_data:
        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            camera_binding,
            unreal.MovieScene3DTransformTrack
        )
        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            
            # Use the existing keyframe applier logic (we can import it or duplicate simple logic here)
            # For simplicity, implementing basic applier here
            channels = section.get_all_channels()
            location_channels = channels[0:3]
            rotation_channels = channels[3:6]
            
            # Location
            for kf in keyframe_data["location"]:
                frame = unreal.FrameNumber(kf["frame"])
                location_channels[0].add_key(frame, float(kf["x"]))
                location_channels[1].add_key(frame, float(kf["y"]))
                location_channels[2].add_key(frame, float(kf["z"]))
                
            # Rotation
            for kf in keyframe_data["rotation"]:
                frame = unreal.FrameNumber(kf["frame"])
                rotation_channels[0].add_key(frame, float(kf["roll"]))
                rotation_channels[1].add_key(frame, float(kf["pitch"]))
                rotation_channels[2].add_key(frame, float(kf["yaw"]))
                
            log(f"✓ Applied {len(keyframe_data['location'])} camera transform keyframes")

    return camera_binding


def add_camera_look_at_constraint(camera_actor, mannequin_actor):
    """Add look-at constraint to make camera track the mannequin"""
    try:
        log("\nAdding camera look-at constraint...")
        log(f"  Camera actor: {camera_actor}")
        log(f"  Mannequin actor: {mannequin_actor}")
        
        # Create look-at tracking settings
        lookat_settings = unreal.CameraLookatTrackingSettings()
        lookat_settings.enable_look_at_tracking = True
        lookat_settings.actor_to_track = mannequin_actor
        lookat_settings.allow_roll = False
        lookat_settings.look_at_tracking_interp_speed = 0.0
        lookat_settings.relative_offset = unreal.Vector(0, 0, 0)
        
        # Set on camera actor (from api_reference.txt)
        camera_actor.set_editor_property('lookat_tracking_settings', lookat_settings)
        log("✓ Camera look-at tracking enabled on camera actor")
        return True
            
    except Exception as e:
        log(f"⚠ Look-at constraint failed: {e}")
        import traceback
        log(traceback.format_exc())
        return False


def calculate_position_from_motion(start_pos, start_rotation, direction, distance_cm):
    """
    Calculate world position based on relative direction and distance
    
    Args:
        start_pos: unreal.Vector starting position
        start_rotation: unreal.Rotator current facing direction
        direction: str - "forward", "backward", "left", "right"
        distance_cm: float - distance to move in cm
        
    Returns:
        unreal.Vector - new world position
    """
    # Get forward and right vectors from rotation
    forward = unreal.MathLibrary.get_forward_vector(start_rotation)
    right = unreal.MathLibrary.get_right_vector(start_rotation)
    
    # Calculate movement vector based on direction
    if direction == "forward":
        move_vec = forward
    elif direction == "backward":
        move_vec = unreal.Vector(-forward.x, -forward.y, -forward.z)
    elif direction == "left":
        move_vec = unreal.Vector(-right.x, -right.y, -right.z)
    elif direction == "right":
        move_vec = right
    else:
        log(f"⚠ Unknown direction: {direction}, using forward")
        move_vec = forward
    
    # Calculate new position
    new_pos = unreal.Vector(
        start_pos.x + move_vec.x * distance_cm,
        start_pos.y + move_vec.y * distance_cm,
        start_pos.z  # Keep Z constant (grounded)
    )
    
    return new_pos


def add_mannequin_with_motion(sequence, mannequin, mannequin_location, mannequin_rotation, fps, duration_frames, motion_plan):
    """
    Add mannequin to sequence with motion command-based keyframes
    
    Args:
        motion_plan: List of (time_seconds, animation, direction, distance_cm, description) tuples
    """
    log_header("STEP 6: Adding mannequin with motion commands")

    mannequin_binding = unreal.MovieSceneSequenceExtensions.add_possessable(sequence, mannequin)

    if mannequin_binding:
        log(f"✓ Mannequin added to sequence: {str(mannequin_binding.get_display_name())}")

        # Add transform track
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieScene3DTransformTrack
        )

        if transform_track:
            section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
            unreal.MovieSceneSectionExtensions.set_range(section, 0, duration_frames)
            log("✓ Transform track added")

        # Add skeletal animation track
        anim_track = unreal.MovieSceneBindingExtensions.add_track(
            mannequin_binding,
            unreal.MovieSceneSkeletalAnimationTrack
        )

        # Process motion plan and create keyframes
        add_motion_keyframes(transform_track, anim_track, mannequin_location, mannequin_rotation, fps, duration_frames, motion_plan)
        
        return mannequin_binding
    else:
        log("⚠ Warning: Failed to add mannequin binding")
        return None


def add_motion_keyframes(transform_track, anim_track, start_location, start_rotation, fps, duration_frames, motion_plan):
    """Create keyframes from motion command plan"""
    log("\nProcessing motion commands...")
    
    # Get transform channels
    transform_sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
    if not transform_sections:
        log("⚠ No transform section found")
        return
    
    transform_section = transform_sections[0]
    channels = transform_section.get_all_channels()
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    
    # Process each motion command
    current_pos = start_location
    prev_time = 0
    prev_anim = None
    
    for i, (time_sec, anim_name, direction, distance_cm, description) in enumerate(motion_plan):
        frame = int(time_sec * fps)
        
        # Calculate new position based on direction and distance
        new_pos = calculate_position_from_motion(current_pos, start_rotation, direction, distance_cm)
        
        # Add location keyframes
        location_channels[0].add_key(unreal.FrameNumber(frame), float(new_pos.x))
        location_channels[1].add_key(unreal.FrameNumber(frame), float(new_pos.y))
        location_channels[2].add_key(unreal.FrameNumber(frame), float(new_pos.z))
        
        # Add rotation keyframes (maintain spawn rotation)
        rotation_channels[0].add_key(unreal.FrameNumber(frame), float(start_rotation.roll))
        rotation_channels[1].add_key(unreal.FrameNumber(frame), float(start_rotation.pitch))
        rotation_channels[2].add_key(unreal.FrameNumber(frame), float(start_rotation.yaw))
        
        log(f"  [{time_sec}s] {description}: {direction} → ({new_pos.x:.1f}, {new_pos.y:.1f}, {new_pos.z:.1f})")
        
        # Add animation section if animation changed
        if anim_name and anim_name != prev_anim:
            add_animation_section(anim_track, anim_name, int(prev_time * fps), frame if i > 0 else duration_frames)
            prev_anim = anim_name
        
        current_pos = new_pos
        prev_time = time_sec
    
    log(f"✓ Motion keyframes added: {len(motion_plan)} waypoints")


def add_animation_section(anim_track, anim_name, start_frame, end_frame):
    """Add an animation section to the track"""
    anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
    unreal.MovieSceneSectionExtensions.set_range(anim_section, start_frame, end_frame)
    
    # Load animation
    anim_path = f"/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/{anim_name}.{anim_name}"
    anim = unreal.load_object(None, anim_path)
    
    if anim:
        params = anim_section.params
        params.animation = anim
        log(f"  ✓ Animation: {anim_name} ({start_frame}-{end_frame})")
    else:
        log(f"  ⚠ Animation not found: {anim_name}")


def finalize_sequence(sequence, sequence_name):
    """Save and open sequence, lock viewport to camera cuts"""
    log_header("STEP 7: Finalizing")

    # Save sequence
    saved = unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    if saved:
        log("✓ Sequence saved")

    try:
        # Open in Sequencer
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        log("✓ Sequence opened in Sequencer")
    except Exception as e:
        log(f"⚠ Warning: Could not open sequence: {e}")
        return

    try:
        # Lock viewport to camera cuts
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        log("✓ Viewport locked to camera cuts")
    except Exception as e:
        log(f"⚠ Warning: Could not lock viewport: {e}")

    # Wait for UI update
    import time
    time.sleep(2)

    try:
        # Refresh and play
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        log("✓ Sequence playing from frame 0")
    except Exception as e:
        log(f"⚠ Warning: Could not play sequence: {e}")
