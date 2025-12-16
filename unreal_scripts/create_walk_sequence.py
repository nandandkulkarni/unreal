"""
Create a Level Sequence with Character Walking Animation
Run this inside Unreal Engine using Tools > Execute Python Script

This creates a cinematic sequence where the character walks through waypoints
with proper walking animations.
"""

import unreal
import time
from datetime import datetime
import os

# Setup logging
LOG_FILE = r"C:\U\CinematicPipeline_Scripts\logs\create_walk_sequence.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_message(message, level="INFO"):
    """Log to both Unreal and a file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    
    # Log to Unreal
    if level == "ERROR":
        unreal.log_error(message)
    elif level == "WARNING":
        unreal.log_warning(message)
    else:
        unreal.log(message)
    
    # Log to file
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted_msg + '\n')
    except Exception as e:
        unreal.log_error(f"Failed to write to log file: {e}")

def create_walking_sequence():
    """Create a Level Sequence with walking character animation"""
    
    log_message("=" * 80)
    log_message("Starting Level Sequence creation script")
    log_message("=" * 80)
    
    # Find the character actor
    actor_path = '/Game/Main.Main:PersistentLevel.BP_ThirdPersonCharacter_C_1'
    log_message(f"Searching for character at: {actor_path}")
    character = unreal.load_object(None, actor_path)
    
    if not character:
        log_message("Character not found at default path, searching all level actors...", "WARNING")
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        log_message(f"Found {len(actors)} total actors in level")
        
        for a in actors:
            if 'ThirdPersonCharacter' in a.get_name():
                character = a
                log_message(f"Found character by name search: {a.get_name()}")
                break
    
    if not character:
        log_message("Could not find ThirdPersonCharacter!", "ERROR")
        return
    
    log_message(f"✓ Character found: {character.get_name()}")
    log_message(f"  - Full path: {character.get_path_name()}")
    log_message(f"  - Class: {character.get_class().get_name()}")
    
    # Create a new Level Sequence
    sequence_path = '/Game/Sequences'
    sequence_name = 'CharacterWalkSequence'
    full_path = f'{sequence_path}/{sequence_name}'
    
    log_message(f"Creating Level Sequence at: {full_path}")
    
    # Make sure the Sequences folder exists
    if not unreal.EditorAssetLibrary.does_directory_exist(sequence_path):
        log_message(f"Creating directory: {sequence_path}")
        unreal.EditorAssetLibrary.make_directory(sequence_path)
        log_message("✓ Directory created")
    else:
        log_message(f"✓ Directory exists: {sequence_path}")
    
    # Delete existing sequence if it exists
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        log_message("Existing sequence found, deleting...", "WARNING")
        unreal.EditorAssetLibrary.delete_asset(full_path)
        log_message("✓ Old sequence deleted")
    
    # Create the Level Sequence
    log_message("Creating new Level Sequence...")
    sequence_factory = unreal.LevelSequenceFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    
    sequence = asset_tools.create_asset(
        sequence_name,
        sequence_path,
        unreal.LevelSequence,
        sequence_factory
    )
    
    if not sequence:
        log_message("Failed to create Level Sequence", "ERROR")
        return
    
    log_message(f"✓ Sequence created: {sequence.get_name()}")
    log_message(f"  - Asset path: {sequence.get_path_name()}")
    
    # Get the sequence's movie scene
    log_message("Getting MovieScene from sequence...")
    movie_scene = sequence.get_movie_scene()
    
    if not movie_scene:
        log_message("Failed to get movie scene from sequence", "ERROR")
        return
    
    log_message("✓ MovieScene obtained")
    
    # Set sequence duration (10 seconds at 24fps)
    log_message("Setting sequence parameters...")
    frame_rate = unreal.FrameRate(24, 1)
    sequence.set_display_rate(frame_rate)
    log_message(f"  - Display rate: 24fps")
    
    sequence.set_tick_resolution_directly(unreal.FrameRate(24000, 1))
    log_message(f"  - Tick resolution: 24000")
    
    # Set playback range: 0 to 10 seconds (240 frames at 24fps)
    start_frame = 0
    end_frame = 240  # 10 seconds * 24fps
    sequence.set_playback_start(start_frame)
    sequence.set_playback_end(end_frame)
    log_message(f"  - Playback range: {start_frame} to {end_frame} frames (10 seconds)")
    log_message("✓ Sequence parameters set")
    
    # Add the character as a possessable
    log_message("Adding character as possessable to sequence...")
    binding = sequence.add_possessable(character)
    log_message(f"✓ Character binding created: {binding.get_display_name()}")
    log_message(f"  - Binding ID: {binding.get_id()}")
    
    # Add animation track for walking animation
    log_message("Adding skeletal animation track...")
    anim_track = binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
    anim_section = anim_track.add_section()
    anim_section.set_range(start_frame, end_frame)
    log_message(f"✓ Animation track created")
    log_message(f"  - Track type: {anim_track.get_class().get_name()}")
    log_message(f"  - Section range: {start_frame} to {end_frame}")
    
    # Set the walking animation
    # Find the walking animation asset
    walk_anim_path = '/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.MF_Unarmed_Walk_Fwd'
    log_message(f"Loading walking animation from: {walk_anim_path}")
    walk_anim = unreal.load_object(None, walk_anim_path)
    
    if walk_anim:
        anim_section.params.animation = walk_anim
        log_message(f"✓ Walking animation assigned: {walk_anim.get_name()}")
        log_message(f"  - Animation class: {walk_anim.get_class().get_name()}")
    else:
        log_message(f"Could not find walking animation at {walk_anim_path}", "WARNING")
        log_message("Character will glide instead of walking", "WARNING")
    
    # Add a Transform track to animate position
    log_message("Adding 3D transform track...")
    transform_track = binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_start_frame_bounded(0)
    transform_section.set_end_frame_bounded(0)
    transform_section.set_range(start_frame, end_frame)
    log_message(f"✓ Transform track created")
    log_message(f"  - Track type: {transform_track.get_class().get_name()}")
    
    # Get the transform channels
    log_message("Getting transform channels for keyframe animation...")
    channels = transform_section.get_all_channels()
    log_message(f"  - Total channels: {len(channels)}")
    location_channels = channels[0:3]  # X, Y, Z
    rotation_channels = channels[3:6]  # Roll, Pitch, Yaw
    log_message(f"  - Location channels: {len(location_channels)}")
    log_message(f"  - Rotation channels: {len(rotation_channels)}")
    
    # Define waypoints (with timestamps in seconds and rotation yaw)
    # Rotation: 0=East, 90=North, 180=West, 270=South
    waypoints = [
        (0.0, 0, 0, 100, 0),         # Time 0s: start position, facing East
        (2.5, 300, 0, 100, 90),      # Time 2.5s: facing North
        (5.0, 300, 300, 100, 180),   # Time 5s: facing West
        (7.5, 0, 300, 100, 270),     # Time 7.5s: facing South
        (10.0, 0, 0, 100, 0)         # Time 10s: back to start, facing East
    ]
    
    log_message(f"Adding {len(waypoints)} keyframes to animation...")
    
    # Add keyframes for each waypoint (24fps frame rate)
    fps = 24
    
    for i, (time_sec, x, y, z, yaw) in enumerate(waypoints, 1):
        frame_number = int(time_sec * fps)
        
        log_message(f"Keyframe {i}/{len(waypoints)}: Frame {frame_number} (t={time_sec}s)")
        
        # Set location keyframes
        location_channels[0].add_key(unreal.FrameNumber(frame_number), x)  # X
        location_channels[1].add_key(unreal.FrameNumber(frame_number), y)  # Y
        location_channels[2].add_key(unreal.FrameNumber(frame_number), z)  # Z
        log_message(f"  - Location: ({x}, {y}, {z})")
        
        # Set rotation keyframe (Yaw only, to face direction of movement)
        rotation_channels[2].add_key(unreal.FrameNumber(frame_number), yaw)  # Yaw
        log_message(f"  - Rotation: Yaw={yaw}°")
    
    log_message(f"✓ All {len(waypoints)} keyframes added successfully")
    
    # Save the sequence
    log_message("Saving Level Sequence asset...")
    save_result = unreal.EditorAssetLibrary.save_asset(sequence.get_path_name())
    if save_result:
        log_message("✓ Sequence saved successfully")
    else:
        log_message("Failed to save sequence", "WARNING")
    
    log_message("=" * 80)
    log_message("✓✓✓ SEQUENCE CREATED SUCCESSFULLY! ✓✓✓")
    log_message("=" * 80)
    log_message(f"Sequence path: {sequence.get_path_name()}")
    log_message("To view: Content Browser > Sequences > CharacterWalkSequence (double-click)")
    log_message("Click the Play button in Sequencer to see the character walk!")
    log_message(f"Log file location: {LOG_FILE}")
    log_message("=" * 80)
    
    # Open the sequence in Sequencer
    log_message("Opening sequence in Sequencer...")
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    log_message("✓ Sequencer opened")

# Run it
log_message("\n" + "=" * 80)
log_message("SCRIPT EXECUTION STARTED")
log_message("=" * 80)
create_walking_sequence()
log_message("=" * 80)
log_message("SCRIPT EXECUTION COMPLETED")
log_message("=" * 80 + "\n")
