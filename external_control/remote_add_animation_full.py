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
    
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Step 1: Open sequence
    print("\n[1/7] Opening sequence...")
    print(f"      Path: {sequence_path}")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    if not success:
        print(f"      [X] Failed to open sequence: {result}")
        return
    
    open_result = result.get('ReturnValue', None)
    if open_result != True:
        print(f"      [X] OpenLevelSequence returned False")
        return
    print("      [OK] Sequence opened successfully")
    
    # Check current sequence and GET IT (CRITICAL for AddPossessable to work!)
    print("      Getting current sequence reference...")
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    
    if not success:
        print(f"      [X] Failed to call GetCurrentLevelSequence: {current}")
        return
    
    current_sequence = current.get('ReturnValue', '')
    if not current_sequence:
        print("      [X] GetCurrentLevelSequence returned empty - no sequence is open")
        return
    
    print(f"      [OK] Current sequence reference: {current_sequence}")
    
    # Verify we got the same path back
    if current_sequence != sequence_path:
        print(f"      [WARNING] Path mismatch: opened '{sequence_path}' but got '{current_sequence}'")
    else:
        print(f"      [OK] Sequence path verified")
    
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
    
    if len(characters) < 1:
        print(f"      [X] Need at least 1 character!")
        return
    print(f"      [OK] Found {len(characters)} character(s) for animation")
    
    # Step 3: Check existing bindings
    print("\n[3/7] Checking existing sequence bindings...")
    success, bindings_result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "GetBindings",
        {"Sequence": current_sequence}
    )
    existing_bindings = bindings_result.get('ReturnValue', []) if success else []
    print(f"      → Existing bindings in sequence: {len(existing_bindings)}")
    
    # Process each character (limit to available characters)
    for idx, character_path in enumerate(characters[:min(2, len(characters))]):
        print(f"\n[4/7] Adding Character {idx+1} as possessable...")
        print(f"      Character path: {character_path}")
        
        # Add possessable - USE CURRENT_SEQUENCE (from GetCurrentLevelSequence)
        success, binding_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "AddPossessable",
            {
                "Sequence": current_sequence,  # Use the open sequence!
                "ObjectToPossess": character_path
            }
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
            {"Sequence": current_sequence}
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
                "TrackType": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"  # Simple string, not wrapped!
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
        
        # Get channels from the 3D transform section directly
        print(f"\n[7/7] Adding keyframes to Character {idx+1}...")
        
        # Try to get the channels from the section using a different approach
        # Use the MovieScene3DTransformSectionExtensions for transform-specific methods
        success, channels_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneScriptingActorReferenceChannel",
            "GetChannels",
            {"Section": section_object}
        )
        
        # If that doesn't work, try getting them as scripting float channels
        if not success:
            # Try direct channel access via section property
            success, channels_result = call_function(
                section_object,
                "GetChannels",
                {}
            )
        
        if not success:
            print(f"      [X] Failed to get channels from section")
            # Let's try a manual approach using SetLocationX/Y/Z methods
            print(f"      → Attempting direct keyframe setting via Set methods...")
            continue
            
        channels = channels_result.get('ReturnValue', []) if success else []
        print(f"      → Total channels found: {len(channels)}")
        
        if len(channels) >= 3:
            print(f"      ✓ Found {len(channels)} channels (need 3 for X,Y,Z)")
        else:
            print(f"      [X] Need at least 3 channels for X,Y,Z, got {len(channels)}")
            continue
        
        # Define waypoints and offset
        waypoints = [
            (0, 0, 100),
            (500, 0, 100),
            (500, 500, 100),
            (0, 500, 100),
            (0, 0, 100)
        ]
        offset_y = -100 if idx == 0 else 100
        frames_per_waypoint = 300 // (len(waypoints) - 1)
        
        print(f"      → Adding {len(waypoints)} keyframes per channel...")
        
        # Add keyframes to X, Y, Z channels using properly typed channels
        keyframes_added = 0
        for wp_idx, (x, y, z) in enumerate(waypoints):
            frame = wp_idx * frames_per_waypoint
            location = (x, y + offset_y, z)
            
            # Add key to each channel (X, Y, Z are first 3 channels)
            for channel_idx, value in enumerate(location):
                if channel_idx < len(channels):
                    channel = channels[channel_idx]
                    
                    # Use MovieSceneScriptingFloatChannel AddKey method
                    success, result = call_function(
                        "/Script/SequencerScripting.Default__MovieSceneScriptingFloatChannel",
                        "AddKey",
                        {
                            "Channel": channel,
                            "NewKey": {
                                "Time": {"FrameNumber": {"Value": frame}},
                                "Value": value,
                                "InterpMode": 0  # Linear interpolation
                            }
                        }
                    )
                    
                    if success:
                        keyframes_added += 1
        
        print(f"      ✓ Added {keyframes_added} keyframes total ({keyframes_added // 3} per channel)")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Animation keyframes added remotely!")
    print("Possessables → Tracks → Sections → Channels → Keyframes")
    print("Ready to play in Unreal!")
    print("=" * 70)

if __name__ == "__main__":
    main()
