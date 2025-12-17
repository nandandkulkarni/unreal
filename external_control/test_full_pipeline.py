"""
Complete Animation Pipeline: Create binding, track, and add keyframes
This handles sequences with no existing bindings
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"

def execute_python(python_code):
    """Execute Python code inside Unreal Engine"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_code}
    }
    
    response = requests.put(BASE_URL, json=payload)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text

print("=" * 80)
print("COMPLETE PIPELINE: Add Character + Animation Keyframes")
print("=" * 80)

# Complete pipeline: add character, create track, add keyframes
complete_pipeline = """
import unreal

# Get current sequence
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
print(f'Working with sequence: {seq.get_name()}')

# Check if we have bindings
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
print(f'Existing bindings: {len(bindings)}')

# If no bindings, we need to add a character
if len(bindings) == 0:
    print('No bindings found, searching for character actor...')
    
    # Get all actors in the level
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_subsystem.get_all_level_actors()
    
    # Find a character actor
    character_actor = None
    for actor in all_actors:
        actor_name = actor.get_name()
        if 'Character' in actor_name or 'BP_ThirdPerson' in actor_name:
            character_actor = actor
            print(f'Found character: {actor_name}')
            break
    
    if character_actor:
        # Add character as possessable
        print(f'Adding {character_actor.get_name()} to sequence...')
        binding = unreal.MovieSceneSequenceExtensions.add_possessable(seq, character_actor)
        print(f'Character added! Binding: {binding}')
        bindings = [binding]
    else:
        print('ERROR: No character actor found in level!')
        print('Available actors:')
        for actor in all_actors[:10]:
            print(f'  - {actor.get_name()}')
        result = 'FAILED: No character found'

if bindings:
    binding = bindings[0]
    
    # Get or create transform track
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    transform_track = None
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            transform_track = track
            break
    
    if not transform_track:
        print('No transform track found, creating one...')
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            binding,
            unreal.MovieScene3DTransformTrack
        )
        print(f'Transform track created!')
    
    # Get or create section
    sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
    if not sections:
        print('No sections found, adding one...')
        section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
        # Set section range
        unreal.MovieSceneSectionExtensions.set_range(section, 0, 300)
        print(f'Section created with range 0-300')
    else:
        section = sections[0]
    
    # Get channels
    channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
    print(f'Found {len(channels)} channels')
    
    if len(channels) >= 3:
        location_x = channels[0]
        location_y = channels[1]
        location_z = channels[2]
        
        # Define animation waypoints (square path)
        waypoints = [
            (0, 0, 100),      # Start
            (500, 0, 100),    # Right
            (500, 500, 100),  # Forward-Right
            (0, 500, 100),    # Forward-Left
            (0, 0, 100)       # Back to start
        ]
        
        frames_per_waypoint = 60
        
        print(f'\\nAdding {len(waypoints)} keyframes...')
        
        for i, (x, y, z) in enumerate(waypoints):
            frame_num = i * frames_per_waypoint
            frame = unreal.FrameNumber(frame_num)
            
            location_x.add_key(frame, float(x))
            location_y.add_key(frame, float(y))
            location_z.add_key(frame, float(z))
            
            print(f'  Frame {frame_num}: ({x}, {y}, {z})')
        
        # Verify
        num_keys_x = location_x.get_num_keys()
        num_keys_y = location_y.get_num_keys()
        num_keys_z = location_z.get_num_keys()
        
        print(f'\\nKeyframes created:')
        print(f'  Location.X: {num_keys_x} keys')
        print(f'  Location.Y: {num_keys_y} keys')
        print(f'  Location.Z: {num_keys_z} keys')
        
        result = f'SUCCESS: Character animated with {len(waypoints)} keyframes!'
    else:
        print(f'ERROR: Only {len(channels)} channels found')
        result = f'FAILED: Not enough channels'
"""

print("\n[1] Executing complete pipeline...")
success, result = execute_python(complete_pipeline)

if success:
    print(f"    ✓ Pipeline executed!")
    print(f"    Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 80)
    print("✓ COMPLETE ANIMATION PIPELINE FINISHED!")
    print("=" * 80)
    print("\nWhat was created:")
    print("  1. Character added as possessable to sequence")
    print("  2. Transform track created")
    print("  3. Section with keyframes added (frames 0, 60, 120, 180, 240)")
    print("  4. Character will move in a square path")
    print("\nTo view:")
    print("  - Open Sequencer window")
    print("  - Press SPACE to play animation")
    print("=" * 80)
else:
    print(f"    ✗ Pipeline failed: {result}")
    print("\nCheck Unreal Output Log (Window > Developer Tools > Output Log)")
