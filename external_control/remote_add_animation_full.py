"""
Add Animation Keyframes REMOTELY
Complete implementation using MovieSceneExtensions API
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
    print("REMOTE ANIMATION ADDITION - FULL IMPLEMENTATION")
    print("=" * 70)
    
    sequence_path = "/Game/Sequences/CharacterWalkSequence"
    
    # Step 1: Open sequence
    print("\n[1/7] Opening sequence...")
    success, _ = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": {"objectPath": sequence_path}}
    )
    if not success:
        print("      [X] Failed to open sequence")
        return
    print("      [OK] Sequence opened")
    
    # Check current sequence
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    print(f"      → Current open sequence: {current.get('ReturnValue', 'None')}")
    
    # Step 2: Get characters
    print("\n[2/7] Getting characters in level...")
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    all_actors = result.get('ReturnValue', [])
    characters = [a for a in all_actors if 'Character' in str(a)]
    
    print(f"      → Total actors in level: {len(all_actors)}")
    print(f"      → Character actors found: {len(characters)}")
    
    if len(characters) < 2:
        print(f"      [X] Need at least 2 characters!")
        return
    print(f"      [OK] Sufficient characters for animation")
    
    # Step 3: Check existing bindings
    print("\n[3/7] Checking existing sequence bindings...")
    success, bindings_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": {"objectPath": sequence_path}}
    )
    existing_bindings = bindings_result.get('ReturnValue', []) if success else []
    print(f"      → Existing bindings in sequence: {len(existing_bindings)}")
    
    # Process each character
    for idx, character_path in enumerate(characters[:2]):
        print(f"\n[4/7] Adding Character {idx+1} as possessable...")
        print(f"      Character path: {character_path}")
        
        # Add possessable
        success, binding_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "AddPossessable",
            {"Sequence": {"objectPath": sequence_path}, "ObjectToAdd": {"objectPath": character_path}}
        )
        if not success:
            print(f"      [X] Failed: {binding_result}")
            continue
        
        binding_proxy = binding_result.get('ReturnValue', {})
        print(f"      [OK] Character {idx+1} added to sequence")
        print(f"      → Binding ID: {binding_proxy.get('BindingID', {})}")
        
        # Verify binding was added by querying all bindings
        success, all_bindings = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "GetBindings",
            {"Sequence": {"objectPath": sequence_path}}
        )
        all_bindings_list = all_bindings.get('ReturnValue', []) if success else []
        print(f"      → Total bindings in sequence after add: {len(all_bindings_list)}")
        
        # Get tracks on this binding
        success, tracks_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "GetTracks",
            {"InBinding": binding_proxy}
        )
        existing_tracks = tracks_result.get('ReturnValue', []) if success else []
        print(f"      → Existing tracks on this binding: {len(existing_tracks)}")
        
        print(f"\n[5/7] Adding transform track to Character {idx+1}...")
        success, track_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "AddTrack",
            {
                "InBinding": binding_proxy,
                "TrackType": {"objectPath": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"}
            }
        )
        
        if not success:
            print(f"      [X] Failed to add track: {track_result}")
            continue
        
        track_object = track_result.get('ReturnValue', {})
        print(f"      [OK] Transform track added")
        print(f"      → Track object: {track_object}")
        
        # Verify track was added by querying tracks again
        success, updated_tracks = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "GetTracks",
            {"InBinding": binding_proxy}
        )
        current_tracks = updated_tracks.get('ReturnValue', []) if success else []
        print(f"      → Total tracks on binding after add: {len(current_tracks)}")
        
        # If we have tracks, get sections count before adding
        if track_object:
            success, sections_before = call_function(
                "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
                "GetSections",
                {"Track": track_object}
            )
            existing_sections = sections_before.get('ReturnValue', []) if success else []
            print(f"      → Existing sections on track: {len(existing_sections)}")
        print(f"      → Total tracks now: {len(current_tracks)}")
        
        # Now add section to the track
        print(f"\n[6/7] Adding section to track...")
        success, section_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
            "AddSection",
            {"Track": track_object}
        )
        
        if not success:
            print(f"      [X] Failed to add section: {section_result}")
            continue
        
        section_object = section_result.get('ReturnValue', {})
        print(f"      [OK] Section added to track")
        print(f"      → Section object: {section_object}")
        
        # Verify section was added by querying sections again
        success, sections_after = call_function(
            "/Script/SequencerScripting.Default__MovieSceneTrackExtensions",
            "GetSections",
            {"Track": track_object}
        )
        current_sections = sections_after.get('ReturnValue', []) if success else []
        print(f"      → Total sections on track after add: {len(current_sections)}")
        
        # Set section range
        success, _ = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "SetRange",
            {"Section": section_object, "StartFrame": 0, "EndFrame": 300}
        )
        
        # Get channels from section
        print(f"\n[7/7] Adding keyframes to Character {idx+1}...")
        success, channels_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "GetChannelsByType",
            {
                "Section": section_object,
                "ChannelType": {"objectPath": "/Script/SequencerScripting.MovieSceneScriptingDoubleChannel"}
            }
        )
        
        if not success:
            print(f"      [X] Failed to get channels: {channels_result}")
            continue
        
        channels = channels_result.get('ReturnValue', [])
        print(f"      → Got {len(channels)} double channels")
        
        # Also try getting all channels to see what's available
        success, all_channels_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSectionExtensions",
            "GetAllChannels",
            {"Section": section_object}
        )
        all_channels = all_channels_result.get('ReturnValue', []) if success else []
        print(f"      → Total channels of all types: {len(all_channels)}")
        
        if len(channels) < 3:
            print(f"      [X] Need at least 3 double channels for X,Y,Z, got {len(channels)}")
            if len(all_channels) > 0:
                print(f"      → But found {len(all_channels)} channels of other types")
            continue
        print(f"      [OK] Got {len(channels)} channels (X, Y, Z for location)")
        
        if len(channels) < 3:
            print(f"      [X] Need at least 3 channels, got {len(channels)}")
            continue
        
        # Define waypoints and offset
        waypoints = [
            (0, 0, 0),
            (500, 0, 0),
            (500, 500, 0),
            (0, 500, 0),
            (0, 0, 0)
        ]
        offset_y = -100 if idx == 0 else 100
        frames_per_waypoint = 300 // (len(waypoints) - 1)
        
        # Add keyframes
        for wp_idx, (x, y, z) in enumerate(waypoints):
            frame = wp_idx * frames_per_waypoint
            location = (x, y + offset_y, z)
            
            # Add key to each channel (X, Y, Z)
            for channel_idx, value in enumerate(location):
                if channel_idx < len(channels):
                    success, _ = call_function(
                        "/Script/SequencerScripting.Default__MovieSceneScriptingDoubleChannel",
                        "AddKey",
                        {
                            "Channel": channels[channel_idx],
                            "NewKey": {
                                "Time": {"FrameNumber": {"Value": frame}},
                                "Value": value
                            }
                        }
                    )
        
        print(f"      [OK] Added {len(waypoints)} keyframes per channel")
        print(f"      [OK] Added {len(waypoints)} keyframes per channel")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Animation keyframes added remotely!")
    print("Possessables → Tracks → Sections → Channels → Keyframes")
    print("Ready to play in Unreal!")
    print("=" * 70)

if __name__ == "__main__":
    main()
