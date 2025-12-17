"""
Test ExecutePythonCommand now that developer mode is enabled
This runs Python code INSIDE Unreal where channel objects work natively
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"

def execute_python(python_code):
    """Execute Python code inside Unreal Engine"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {
            "PythonCommand": python_code
        },
        "generateTransaction": False
    }
    
    response = requests.put(BASE_URL, json=payload)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text

print("=" * 80)
print("TEST: ExecutePythonCommand for Adding Keyframes")
print("=" * 80)

# Step 1: Simple test - just print
print("\n[1] Testing basic Python execution...")
success, result = execute_python("print('Hello from Unreal!')")
print(f"    Success: {success}")
print(f"    Result: {json.dumps(result, indent=2)}")

# Step 2: Test importing unreal module
print("\n[2] Testing unreal module import...")
test_code = """
import unreal
print(f'Unreal module loaded: {unreal}')
result = 'SUCCESS'
"""
success, result = execute_python(test_code)
print(f"    Success: {success}")
if success:
    print(f"    Result: {json.dumps(result, indent=2)}")
else:
    print(f"    Error: {result}")

# Step 3: Test getting sequence and channels
print("\n[3] Testing channel access inside Unreal...")
test_code = """
import unreal

# Get current sequence
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
print(f'Sequence: {seq.get_name()}')

# Get bindings
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)
print(f'Bindings: {len(bindings)}')

if bindings:
    binding = bindings[0]
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    print(f'Tracks: {len(tracks)}')
    
    if tracks:
        # Find transform track
        transform_track = None
        for track in tracks:
            if isinstance(track, unreal.MovieScene3DTransformTrack):
                transform_track = track
                break
        
        if transform_track:
            sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
            print(f'Sections: {len(sections)}')
            
            if sections:
                section = sections[0]
                channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
                print(f'Channels: {len(channels)}')
                print(f'Channel types: {[type(c).__name__ for c in channels[:3]]}')

result = 'Channel access test complete'
"""
success, result = execute_python(test_code)
print(f"    Success: {success}")
if success:
    print(f"    Result: {json.dumps(result, indent=2)}")
else:
    print(f"    Error: {result[:300]}")

# Step 4: Actually add a keyframe!
print("\n[4] ADDING ACTUAL KEYFRAME...")
add_key_code = """
import unreal

# Get current sequence
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(seq)

if bindings:
    binding = bindings[0]
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    
    # Find transform track
    transform_track = None
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            transform_track = track
            break
    
    if transform_track:
        sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
        
        if sections:
            section = sections[0]
            channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
            
            # Add keyframe to Location.X channel
            if len(channels) >= 3:
                location_x = channels[0]
                location_y = channels[1]
                location_z = channels[2]
                
                # Add keyframes at frame 100
                frame = unreal.FrameNumber(100)
                key_x = location_x.add_key(frame, 500.0)
                key_y = location_y.add_key(frame, 300.0)
                key_z = location_z.add_key(frame, 150.0)
                
                print(f'Added 3 keyframes at frame 100')
                print(f'X={key_x.get_value()}, Y={key_y.get_value()}, Z={key_z.get_value()}')
                
                result = 'SUCCESS: Keyframes added!'
            else:
                result = f'ERROR: Only {len(channels)} channels found'
        else:
            result = 'ERROR: No sections found'
    else:
        result = 'ERROR: No transform track found'
else:
    result = 'ERROR: No bindings found'
"""

success, result = execute_python(add_key_code)
print(f"    Success: {success}")
if success:
    print(f"    Result: {json.dumps(result, indent=2)}")
    print("\n" + "=" * 80)
    print("✓ SUCCESS! Keyframe added through ExecutePythonCommand!")
    print("  Open Sequencer in Unreal to see the keyframe at frame 100")
    print("=" * 80)
else:
    print(f"    Error: {result[:500]}")

print("\nCheck Unreal Output Log for Python execution details!")
