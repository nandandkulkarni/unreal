"""
Create a Level Sequence with Character Walking Animation
Run this inside Unreal Engine using Tools > Execute Python Script

This creates a cinematic sequence where the character walks through waypoints
with proper walking animations.
"""

import unreal
import time

def create_walking_sequence():
    """Create a Level Sequence with walking character animation"""
    
    # Find the character actor
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    character = unreal.load_object(None, actor_path)
    
    if not character:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        for a in actors:
            if 'ThirdPersonCharacter' in a.get_name():
                character = a
                break
    
    if not character:
        unreal.log_error("Could not find ThirdPersonCharacter!")
        return
    
    unreal.log(f"Found character: {character.get_name()}")
    
    # Create a new Level Sequence
    sequence_path = '/Game/Sequences'
    sequence_name = 'CharacterWalkSequence'
    full_path = f'{sequence_path}/{sequence_name}'
    
    # Make sure the Sequences folder exists
    if not unreal.EditorAssetLibrary.does_directory_exist(sequence_path):
        unreal.EditorAssetLibrary.make_directory(sequence_path)
    
    # Delete existing sequence if it exists
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        unreal.log("Deleting existing sequence...")
        unreal.EditorAssetLibrary.delete_asset(full_path)
    
    # Create the Level Sequence
    sequence_factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    sequence = asset_tools.create_asset(
        sequence_name,
        sequence_path,
        unreal.LevelSequence,
        sequence_factory
    )
    
    if not sequence:
        unreal.log_error("Failed to create Level Sequence")
        return
    
    unreal.log(f"Created sequence: {sequence.get_name()}")
    
    # Get the sequence's movie scene
    movie_scene = sequence.get_movie_scene()
    
    if not movie_scene:
        unreal.log_error("Failed to get movie scene from sequence")
        return
    
    # Set sequence duration (10 seconds at 24fps)
    frame_rate = unreal.FrameRate(24, 1)
    sequence.set_display_rate(frame_rate)
    sequence.set_tick_resolution_directly(unreal.FrameRate(24000, 1))
    
    # Set playback range: 0 to 10 seconds (240 frames at 24fps)
    start_frame = 0
    end_frame = 240  # 10 seconds * 24fps
    sequence.set_playback_start(start_frame)
    sequence.set_playback_end(end_frame)
    
    # Add the character as a possessable
    binding = sequence.add_possessable(character)
    unreal.log(f"Added character binding: {binding.get_display_name()}")
    
    # Add animation track for walking animation
    anim_track = binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.set_range(start_frame, end_frame)
    
    # Set the walking animation
    # Find the walking animation asset
    walk_anim_path = '/Game/Characters/Mannequins/Animations/Manny/MM_Walk_Fwd.MM_Walk_Fwd'
    walk_anim = unreal.load_object(None, walk_anim_path)
    
    if walk_anim:
        anim_section.params.animation = walk_anim
        unreal.log(f"Added walking animation: {walk_anim.get_name()}")
    else:
        unreal.log_warning(f"Could not find walking animation at {walk_anim_path}")
    
    # Add a Transform track to animate position
    transform_track = binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(0)
    transform_section.set_end_frame_bounded(0)
    transform_section.set_range(start_frame, end_frame)
    
    # Get the transform channels
    channels = transform_section.get_all_channels()
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    
    # Define waypoints (with timestamps in seconds and rotation yaw)
    # Rotation: 0=East, 90=North, 180=West, 270=South
    waypoints = [
        (0.0, 0, 0, 100, 0),         # Time 0s: start position, facing East
        (2.5, 300, 0, 100, 90),      # Time 2.5s: facing North
        (5.0, 300, 300, 100, 180),   # Time 5s: facing West
        (7.5, 0, 300, 100, 270),     # Time 7.5s: facing South
        (10.0, 0, 0, 100, 0)         # Time 10s: back to start, facing East
    ]
    
    # Add keyframes for each waypoint (24fps frame rate)
    fps = 24
    
    for time_sec, x, y, z, yaw in waypoints:
        frame_number = int(time_sec * fps)
        
        # Set location keyframes
        location_channels[0].add_key(unreal.FrameNumber(frame_number), x)  # X
        location_channels[1].add_key(unreal.FrameNumber(frame_number), y)  # Y
        location_channels[2].add_key(unreal.FrameNumber(frame_number), z)  # Z
        
        # Set rotation keyframe (Yaw only, to face direction of movement)
        rotation_channels[2].add_key(unreal.FrameNumber(frame_number), yaw)  # Yaw
        
        unreal.log(f"Added keyframe at frame {frame_number} ({time_sec}s): pos({x}, {y}, {z}) rot({yaw}°)")
    
    # Save the sequence
    unreal.EditorAssetLibrary.save_asset(sequence.get_path_name())
    
    unreal.log("✓ Sequence created successfully!")
    unreal.log("To view: Content Browser > Sequences > CharacterWalkSequence (double-click)")
    unreal.log("Click the Play button in Sequencer to see the character walk!")
    
    # Open the sequence in Sequencer
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)

# Run it
create_walking_sequence()
