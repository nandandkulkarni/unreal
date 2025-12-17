"""
Add keyframes to transform track - Unreal Python script
This file is meant to be executed INSIDE Unreal Engine's Python interpreter
"""
import unreal

def add_animation_keyframes():
    """Add keyframes to a character's transform track in a sequence"""
    
    # Open the sequence
    sequence_path = '/Game/Sequences/TestSequence'
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(
        unreal.load_asset(sequence_path)
    )
    
    # Get the sequence
    sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    print(f"Sequence: {sequence.get_name()}")
    
    # Get bindings
    bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
    print(f"Found {len(bindings)} bindings")
    
    if len(bindings) == 0:
        print("ERROR: No bindings found in sequence!")
        return False
    
    # Use first binding
    binding = bindings[0]
    print(f"Using binding: {unreal.MovieSceneBindingExtensions.get_display_name(binding)}")
    
    # Get or create transform track
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    transform_track = None
    
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            transform_track = track
            print(f"Found existing transform track")
            break
    
    if not transform_track:
        print("Creating new transform track...")
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            binding,
            unreal.MovieScene3DTransformTrack
        )
    
    # Get or create section
    sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
    if len(sections) == 0:
        print("Creating new section...")
        section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
        unreal.MovieSceneSectionExtensions.set_range(section, 0, 300)
    else:
        section = sections[0]
        print(f"Using existing section")
    
    # Get channels - THIS WORKS in native Unreal Python!
    channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
    print(f"Got {len(channels)} channels")
    
    if len(channels) < 3:
        print(f"ERROR: Need at least 3 channels for X,Y,Z, got {len(channels)}")
        return False
    
    # Define waypoints for animation
    waypoints = [
        (0, 0, 100),
        (500, 0, 100),
        (500, 500, 100),
        (0, 500, 100),
        (0, 0, 100)
    ]
    
    frames_per_waypoint = 300 // (len(waypoints) - 1)
    keyframes_added = 0
    
    print(f"\nAdding {len(waypoints)} keyframes per channel...")
    
    # Add keyframes to Location X, Y, Z (first 3 channels)
    for wp_idx, (x, y, z) in enumerate(waypoints):
        frame = wp_idx * frames_per_waypoint
        frame_time = unreal.FrameNumber(frame)
        location = [x, y, z]
        
        for channel_idx in range(3):  # X, Y, Z only
            channel = channels[channel_idx]
            
            # THIS IS THE KEY: call add_key as an instance method on the channel
            key = channel.add_key(
                frame_time,
                location[channel_idx],
                0.0,  # sub_frame
                unreal.SequenceTimeUnit.DISPLAY_RATE,
                unreal.MovieSceneKeyInterpolation.LINEAR
            )
            
            if key:
                keyframes_added += 1
    
    print(f"\nSUCCESS! Added {keyframes_added} keyframes total!")
    print(f"  ({keyframes_added // 3} keyframes per channel)")
    return True

# Execute the function
if __name__ == '__main__':
    result = add_animation_keyframes()
    if result:
        print("\n" + "="*60)
        print("ANIMATION KEYFRAMES ADDED SUCCESSFULLY!")
        print("Open Sequencer to see the animated character")
        print("="*60)
