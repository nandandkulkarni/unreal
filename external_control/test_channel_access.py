"""
Test different ways to access and add keyframes to transform channels
"""
import requests

BASE_URL = "http://localhost:30010/remote"

def call_function(object_path, function_name, parameters=None):
    """Call Unreal function via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name,
        "parameters": parameters or {}
    }
    
    response = requests.put(f"{BASE_URL}/object/call", json=payload)
    
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def main():
    print("=" * 70)
    print("TEST: Channel Access Methods")
    print("=" * 70)
    
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Open and get sequence
    print("\n[1] Opening sequence...")
    call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    success, seq_result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence",
        {}
    )
    sequence = seq_result.get('ReturnValue', '')
    print(f"    Sequence: {sequence}")
    
    # Get first binding
    print("\n[2] Getting first binding...")
    success, bindings_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": sequence}
    )
    bindings = bindings_result.get('ReturnValue', [])
    if not bindings:
        print("    [X] No bindings found")
        return
    
    first_binding = bindings[0]
    print(f"    Binding: {first_binding}")
    
    # Get tracks
    print("\n[3] Getting tracks...")
    success, tracks_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
        "GetTracks",
        {"Binding": first_binding}
    )
    tracks = tracks_result.get('ReturnValue', [])
    print(f"    Total tracks: {len(tracks)}")
    
    # Find transform track
    transform_track = None
    for track in tracks:
        if 'Transform' in str(track):
            transform_track = track
            print(f"    Found transform track: {track}")
            break
    
    if not transform_track:
        print("    [X] No transform track found")
        return
    
    # Get sections
    print("\n[4] Getting sections from track...")
    success, sections_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
        "GetSections",
        {"Track": transform_track}
    )
    sections = sections_result.get('ReturnValue', [])
    print(f"    Total sections: {len(sections)}")
    
    if not sections:
        print("    [X] No sections found")
        return
    
    section = sections[0]
    print(f"    First section: {section}")
    
    # Try different methods to get channels
    print("\n[5] Testing channel access methods...")
    
    # Method 1: GetAllChannels
    print("\n    Method 1: GetAllChannels")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "GetAllChannels",
        {"Section": section}
    )
    if success:
        channels = result.get('ReturnValue', [])
        print(f"      ✓ Got {len(channels)} channels")
        if channels:
            print(f"        First channel: {channels[0]}")
    else:
        print(f"      [X] Failed: {result}")
    
    # Method 2: FindChannelsByType with Integer enum value
    print("\n    Method 2: FindChannelsByType (enum as int)")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
        "FindChannelsByType",
        {"Section": section, "ChannelType": 1}  # Try 0, 1, 2, etc
    )
    if success:
        channels = result.get('ReturnValue', [])
        print(f"      ✓ Got {len(channels)} channels")
    else:
        print(f"      [X] Failed: {result}")
    
    # Method 3: Direct property access - get channel proxies
    print("\n    Method 3: Try getting channel proxies...")
    # This would require knowing the section's structure
    
    # Method 4: Use SequencerTools to add keys
    print("\n    Method 4: Try SequencerTools AddKey...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__SequencerTools",
        "GetBoundObjects",
        {"World": "/Game/Main.Main", "Binding": first_binding, "Range": {"Lower": {"Value": 0}, "Upper": {"Value": 300}}}
    )
    if success:
        print(f"      Result: {result}")
    else:
        print(f"      [X] Failed: {result}")

if __name__ == "__main__":
    main()
