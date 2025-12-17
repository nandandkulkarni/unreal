"""
Add keyframes using Unreal Python executed IN Unreal
This bypasses the channel handle serialization issue
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote"

def execute_python_in_unreal(python_code):
    """Execute Python code inside Unreal Engine"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_code}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def main():
    print("=" * 70)
    print("ADD KEYFRAMES USING UNREAL PYTHON")
    print("=" * 70)
    
    # Python code to execute in Unreal - this will have access to real objects
    python_code = """
import unreal

# Open the sequence
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(
    unreal.load_asset('/Game/Sequences/TestSequence')
)

# Get the sequence
sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
print(f"Sequence: {sequence}")

# Get bindings
bindings = unreal.MovieSceneSequenceExtensions.get_bindings(sequence)
print(f"Bindings: {len(bindings)}")

if len(bindings) == 0:
    print("No bindings found!")
else:
    binding = bindings[0]
    print(f"Using binding: {binding}")
    
    # Get tracks
    tracks = unreal.MovieSceneBindingExtensions.get_tracks(binding)
    print(f"Tracks: {len(tracks)}")
    
    # Find or add transform track
    transform_track = None
    for track in tracks:
        if isinstance(track, unreal.MovieScene3DTransformTrack):
            transform_track = track
            break
    
    if not transform_track:
        print("Adding new transform track...")
        transform_track = unreal.MovieSceneBindingExtensions.add_track(
            binding,
            unreal.MovieScene3DTransformTrack
        )
    
    print(f"Transform track: {transform_track}")
    
    # Get or add section
    sections = unreal.MovieSceneTrackExtensions.get_sections(transform_track)
    if len(sections) == 0:
        print("Adding new section...")
        section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
        unreal.MovieSceneSectionExtensions.set_range(section, 0, 300)
    else:
        section = sections[0]
    
    print(f"Section: {section}")
    
    # Get channels - THIS WILL WORK because we're in Unreal Python
    channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
    print(f"Channels: {len(channels)}")
    
    # Add keyframes to Location X, Y, Z (first 3 channels)
    waypoints = [
        (0, 0, 100),
        (500, 0, 100),
        (500, 500, 100),
        (0, 500, 100),
        (0, 0, 100)
    ]
    
    frames_per_waypoint = 300 // (len(waypoints) - 1)
    keyframes_added = 0
    
    for wp_idx, (x, y, z) in enumerate(waypoints):
        frame_time = unreal.FrameNumber(wp_idx * frames_per_waypoint)
        location = [x, y, z]
        
        for channel_idx in range(3):  # X, Y, Z
            channel = channels[channel_idx]
            
            # Add the key - THIS WILL WORK with real channel objects
            key = unreal.MovieSceneScriptingFloatChannel.add_key(
                channel,
                frame_time,
                location[channel_idx],
                0.0  # SubFrame
            )
            
            if key:
                keyframes_added += 1
    
    print(f"Added {keyframes_added} keyframes!")
    print("SUCCESS!")
"""
    
    print("\n[1] Executing Python code in Unreal...")
    print("    (Adding keyframes using native Unreal Python API)")
    
    success, result = execute_python_in_unreal(python_code)
    
    if success:
        print("\n[2] Execution result:")
        print(result)
        print("\n" + "=" * 70)
        print("Check Unreal Output Log for detailed execution results!")
        print("=" * 70)
    else:
        print(f"\n[X] Failed to execute: {result}")

if __name__ == "__main__":
    main()
