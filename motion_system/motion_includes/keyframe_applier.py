"""
Keyframe Applier - Pass 2: Apply keyframe data to Unreal

Takes structured keyframe data and creates actual Unreal sequencer keyframes.
"""
import unreal
from ..logger import log


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
    log(f"\n{'='*60}")
    log(f"APPLYING KEYFRAMES: {actor_name}")
    log(f"{'='*60}")
    
    keyframes = keyframe_data["keyframes"]
    loc_keys = keyframes.get("location", [])
    rot_keys = keyframes.get("rotation", [])
    
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
        anim_path = f"/Game/ParagonLtBelica/Characters/Heroes/Belica/Animations/{anim_name}.{anim_name}"
        anim = unreal.load_object(None, anim_path)
        
        if anim:
            params = anim_section.params
            params.animation = anim
            log(f"  ✓ Animation '{anim_name}' [{start_frame}-{end_frame}]")
        else:
            log(f"  ⚠ Animation '{anim_name}' not found at {anim_path}")
    
    log(f"  ✓ Added {len(anim_list)} animation sections")
