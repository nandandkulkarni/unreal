"""
Keyframe Applier - Pass 2: Apply keyframe data to Unreal

Takes structured keyframe data and creates actual Unreal sequencer keyframes.
"""
import unreal
from logger import log


def apply_keyframes_to_actor(actor_name, actor, binding, keyframe_data, fps, duration_frames):
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
