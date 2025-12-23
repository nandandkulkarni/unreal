"""
Sequencer configuration - Add actors to sequence, add tracks and keyframes
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
        
        # Camera cut duration control
        camera_cut_use_seconds = True
        camera_cut_duration_seconds = 60
        camera_cut_duration_frames = int(fps * camera_cut_duration_seconds)

        # Determine camera cut end frame based on flag
        if camera_cut_use_seconds:
            camera_cut_end_frame = int(fps * camera_cut_duration_seconds)
            log(f"  Camera cut duration: {camera_cut_duration_seconds}s ({camera_cut_end_frame} frames) [seconds mode]")
        else:
            camera_cut_end_frame = camera_cut_duration_frames
            log(f"  Camera cut duration: {camera_cut_end_frame} frames [frames mode]")
        
        camera_cut_section.set_range(0, camera_cut_end_frame)

        # Set camera binding - using MovieSceneObjectBindingID with guid as editor property
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


def add_camera_look_at_constraint(camera_actor, mannequin_actor):
    """Add look-at constraint to make camera track the mannequin
    
    Sets the look-at tracking on the camera actor's lookat_tracking_settings property
    
    Args:
        camera_actor: The actual CineCameraActor instance
        mannequin_actor: The actual SkeletalMeshActor instance
    """
    try:
        log("\nAdding camera look-at constraint...")
        log(f"  Camera actor: {camera_actor}")
        log(f"  Mannequin actor: {mannequin_actor}")
        
        # Create look-at tracking settings
        lookat_settings = unreal.CameraLookatTrackingSettings()
        lookat_settings.enable_look_at_tracking = True
        lookat_settings.actor_to_track = mannequin_actor
        lookat_settings.allow_roll = False
        lookat_settings.look_at_tracking_interp_speed = 0.0  # Instant tracking
        lookat_settings.relative_offset = unreal.Vector(0, 0, 0)
        
        # Set the property on the camera actor (from api_reference.txt)
        try:
            camera_actor.set_editor_property('lookat_tracking_settings', lookat_settings)
            log("✓ Camera look-at tracking enabled on camera actor")
            return True
        except Exception as e:
            log(f"⚠ Could not set lookat_tracking_settings on camera actor: {e}")
            import traceback
            log(traceback.format_exc())
            return False
            
    except Exception as e:
        log(f"⚠ Look-at constraint failed: {e}")
        import traceback
        log(traceback.format_exc())
        return False
        
        # DISABLED: This causes Unreal to crash when opening the sequence
        # # Add a transform constraint track to the camera
        # constraint_track = unreal.MovieSceneBindingExtensions.add_track(
        #     camera_binding,
        #     unreal.MovieScene3DConstraintTrack
        # )
        # 
        # if constraint_track:
        #     # Add a constraint section
        #     constraint_section = unreal.MovieSceneTrackExtensions.add_section(constraint_track)
        #     constraint_section.set_range(0, duration_frames)
        #     
        #     # Set the constraint to point at the mannequin
        #     binding_id = unreal.MovieSceneObjectBindingID()
        #     binding_id.set_editor_property('guid', mannequin_binding.get_id())
        #     constraint_section.set_editor_property('constraint_binding_id', binding_id)
        #     
        #     log("✓ Camera look-at constraint added")
        #     return True
        # else:
        #     log("⚠ Failed to create constraint track")
        #     return False
            
    except Exception as e:
        log(f"⚠ Look-at constraint failed: {e}")
        log("  Attempting alternative method...")
        
        # Alternative: Add transform track with keyframes
        try:
            transform_track = unreal.MovieSceneBindingExtensions.add_track(
                camera_binding,
                unreal.MovieScene3DTransformTrack
            )
            if transform_track:
                log("✓ Camera transform track added for manual tracking")
                return True
        except Exception as e2:
            log(f"⚠ Alternative method also failed: {e2}")
        
        return False


def add_mannequin_to_sequence(sequence, mannequin, mannequin_location, mannequin_rotation, fps, duration_frames):
    """Add mannequin to sequence with transform and animation tracks"""
    log_header("STEP 6: Adding mannequin to sequence")

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

        if anim_track:
            anim_section = unreal.MovieSceneTrackExtensions.add_section(anim_track)
            unreal.MovieSceneSectionExtensions.set_range(anim_section, 0, duration_frames)

            # Load and set the jog_fwd animation
            jog_anim = unreal.load_object(None, "/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/Jog_Fwd.Jog_Fwd")
            if jog_anim:
                # Use the params property to set the animation sequence
                params = anim_section.params
                params.animation = jog_anim
                log("✓ Skeletal animation track added with jog_fwd animation")
            else:
                log("✓ Skeletal animation track added (jog_fwd animation not found)")
        else:
            log("⚠ Warning: Failed to add skeletal animation track")

        # Add movement keyframes
        add_movement_keyframes(transform_track, mannequin_location, mannequin_rotation)

        log("\n⚠ Camera look-at tracking not yet implemented")
        
        return mannequin_binding
    else:
        log("⚠ Warning: Failed to add mannequin binding")
        return None


def add_movement_keyframes(transform_track, mannequin_location, mannequin_rotation):
    """Add movement keyframes to transform track"""
    log("\nAdding movement keyframes...")
    transform_sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
    if transform_sections:
        transform_section = transform_sections[0]

        # Get the transform channels
        channels = transform_section.get_all_channels()
        location_channels = channels[0:3]  # X, Y, Z channels
        rotation_channels = channels[3:6]  # Rotation X (Roll), Y (Pitch), Z (Yaw) channels

        # Use fixed world-space movement vectors (independent of actor rotation)
        world_x = unreal.Vector(1.0, 0.0, 0.0)  # Red (+X)
        world_y = unreal.Vector(0.0, 1.0, 0.0)  # Green (+Y)
        start = mannequin_location

        # Choose movement direction: 'x' for Red or 'y' for Green
        movement_direction = 'x'  # change to 'y' for Green direction
        move_vec = world_x if movement_direction == 'x' else world_y

        # Distances along chosen direction at each keyframe (cm)
        # Spread keys over 0..300 frames (adjust if using 60s timeline)
        keys = [
            (0, 0.0),
            (100, 166.0),
            (200, 333.0),
            (300, 500.0),
        ]

        distance_scale = 3.0

        for frame, dist in keys:
            dist_scaled = dist * distance_scale
            pos_x = start.x + move_vec.x * dist_scaled
            pos_y = start.y + move_vec.y * dist_scaled
            pos_z = start.z  # grounded
            location_channels[0].add_key(unreal.FrameNumber(frame), float(pos_x))
            location_channels[1].add_key(unreal.FrameNumber(frame), float(pos_y))
            location_channels[2].add_key(unreal.FrameNumber(frame), float(pos_z))

            # Set rotation keyframes to maintain spawn rotation
            rotation_channels[0].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.roll))
            rotation_channels[1].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.pitch))
            rotation_channels[2].add_key(unreal.FrameNumber(frame), float(mannequin_rotation.yaw))

        log(f"✓ Movement keyframes added: {movement_direction} direction, Z grounded, distance x{distance_scale}")


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
        # Lock viewport to camera cuts - this makes the viewport show what the camera sees
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
        log("✓ Viewport locked to sequencer camera")
    except Exception as e:
        log(f"⚠ Warning: Could not lock viewport: {e}")

    # Wait 2 seconds to allow UI to update
    import time
    time.sleep(2)

    try:
        # Refresh the current sequence to update UI
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

        # Set playback position to frame 0
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)

        # Play the sequence
        unreal.LevelSequenceEditorBlueprintLibrary.play()
        log("✓ Sequence playing from frame 0")
    except Exception as e:
        log(f"⚠ Warning: Could not play sequence: {e}")
