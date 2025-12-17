"""
Complete Animation Test: Add full animation path with multiple keyframes
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
print("COMPLETE ANIMATION: Add Multiple Keyframes for Character Movement")
print("=" * 80)

# Create a complete animation path
animation_code = """
import unreal

# Get current sequence
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
print(f'Working with sequence: {seq.get_name()}')

# Get first character binding
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
if not bindings:
    print('ERROR: No bindings found!')
    result = 'FAILED: No bindings'
else:
    binding = bindings[0]
    print(f'Using binding: {binding}')
    
    # Get transform track
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    transform_track = None
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            transform_track = track
            break
    
    if not transform_track:
        print('ERROR: No transform track found!')
        result = 'FAILED: No transform track'
    else:
        # Get section
        sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
        if not sections:
            print('ERROR: No sections found!')
            result = 'FAILED: No sections'
        else:
            section = sections[0]
            
            # Get all channels
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
                
                frames_per_waypoint = 60  # 60 frames between each waypoint
                
                print(f'Adding {len(waypoints)} waypoints...')
                
                for i, (x, y, z) in enumerate(waypoints):
                    frame_num = i * frames_per_waypoint
                    frame = unreal.FrameNumber(frame_num)
                    
                    key_x = location_x.add_key(frame, float(x))
                    key_y = location_y.add_key(frame, float(y))
                    key_z = location_z.add_key(frame, float(z))
                    
                    print(f'  Frame {frame_num}: ({x}, {y}, {z})')
                
                # Verify keyframes were added
                num_keys_x = location_x.get_num_keys()
                num_keys_y = location_y.get_num_keys()
                num_keys_z = location_z.get_num_keys()
                
                print(f'\\nVerification:')
                print(f'  Location.X: {num_keys_x} keys')
                print(f'  Location.Y: {num_keys_y} keys')
                print(f'  Location.Z: {num_keys_z} keys')
                
                result = f'SUCCESS: Added {len(waypoints)} keyframes to each channel!'
            else:
                print(f'ERROR: Only {len(channels)} channels found, need at least 3')
                result = f'FAILED: Only {len(channels)} channels'
"""

print("\n[1] Executing animation script in Unreal...")
success, result = execute_python(animation_code)

if success:
    print(f"    ✓ Execution succeeded!")
    print(f"    Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 80)
    print("✓ COMPLETE ANIMATION ADDED!")
    print("=" * 80)
    print("\nTo see the animation:")
    print("  1. Open Sequencer in Unreal Editor")
    print("  2. Click on the character's transform track")
    print("  3. You should see 5 keyframes creating a square path")
    print("  4. Press SPACE to play the animation")
    print("=" * 80)
else:
    print(f"    ✗ Execution failed: {result}")

# Now verify by reading the keyframe count
print("\n[2] Verifying keyframes were created...")
verify_code = """
import unreal

seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
binding = bindings[0]
tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
transform_track = next(t for t in tracks if isinstance(t, unreal.MovieScene3DTransformTrack))
sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
section = sections[0]
channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)

result = f"X:{channels[0].get_num_keys()} Y:{channels[1].get_num_keys()} Z:{channels[2].get_num_keys()}"
"""

success, result = execute_python(verify_code)
if success:
    print(f"    Keyframe counts: {result}")
