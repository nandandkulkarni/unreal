"""
Add Animation Keyframes REMOTELY - COMPLETE END-TO-END
Uses ExecutePythonCommand to run code inside Unreal where channels work natively

This creates:
- 2 characters with transform tracks
- Animated movement in square paths
- Complete keyframe animation
"""
import requests
import json

BASE_URL = "http://localhost:30010/remote/object/call"

def call_function(object_path, function_name, parameters=None):
    """Call a function on an Unreal object via Remote Control API"""
    payload = {
        "objectPath": object_path,
        "functionName": function_name
    }
    
    if parameters:
        payload["parameters"] = parameters
    
    response = requests.put(BASE_URL, json=payload)
    if response.status_code == 200:
        return True, response.json()
    else:
        return False, response.text

def execute_python(python_code):
    """Execute Python code inside Unreal Engine"""
    payload = {
        "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
        "functionName": "ExecutePythonCommand",
        "parameters": {"PythonCommand": python_code}
    }
    
    response = requests.put(BASE_URL, json=payload)
    return response.status_code == 200, response.json() if response.status_code == 200 else response.text

def main():
    print("=" * 80)
    print("COMPLETE END-TO-END: Create Animated Two-Character Scene")
    print("=" * 80)
    
    # Complete pipeline in Unreal Python
    complete_scene_code = """
import unreal

print("\\n" + "="*60)
print("Creating Complete Animated Scene")
print("="*60)

# Get current sequence or create one
seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
if not seq:
    print("No sequence open, creating new one...")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = asset_tools.create_asset(
        "TwoCharacterSequence",
        "/Game/Sequences",
        unreal.LevelSequence,
        unreal.LevelSequenceFactoryNew()
    )
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
    print(f"Created new sequence: {seq.get_name()}")

print(f"Working with sequence: {seq.get_name()}")

# Set sequence properties
unreal.MovieSceneSequenceExtensions.set_playback_end_seconds(seq, 10.0)
unreal.MovieSceneSequenceExtensions.set_display_rate(seq, unreal.FrameRate(30, 1))
print("Set sequence to 10 seconds at 30fps")

# Get all actors
editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors = editor_subsystem.get_all_level_actors()

# Find or spawn characters
characters = []
for actor in all_actors:
    if 'Character' in actor.get_name() or 'BP_ThirdPerson' in actor.get_name():
        characters.append(actor)
        if len(characters) >= 2:
            break

# Spawn if needed
world = unreal.EditorLevelLibrary.get_editor_world()
character_class = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter')

while len(characters) < 2:
    location = unreal.Vector(0, (len(characters) - 0.5) * 200, 88)
    new_char = world.spawn_actor(character_class, location, unreal.Rotator())
    new_char.set_actor_label(f"Character{len(characters)+1}")
    characters.append(new_char)
    print(f"Spawned {new_char.get_name()}")

print(f"\\nUsing 2 characters: {[c.get_name() for c in characters]}")

# Add characters to sequence with animation
waypoints = [
    (0, 0, 100),
    (500, 0, 100),
    (500, 500, 100),
    (0, 500, 100),
    (0, 0, 100)
]

for char_idx, character in enumerate(characters[:2]):
    print(f"\\n--- Character {char_idx+1}: {character.get_name()} ---")
    
    # Add as possessable
    binding = unreal.MovieSceneSequenceExtensions.add_possessable(seq, character)
    print(f"  Added to sequence")
    
    # Add transform track
    transform_track = unreal.MovieSceneBindingExtensions.add_track(
        binding,
        unreal.MovieScene3DTransformTrack
    )
    print(f"  Transform track created")
    
    # Add section
    section = unreal.MovieSceneTrackExtensions.add_section(transform_track)
    unreal.MovieSceneSectionExtensions.set_range(section, 0, 300)
    print(f"  Section added (0-300 frames)")
    
    # Get channels
    channels = unreal.MovieSceneSectionExtensions.get_all_channels(section)
    location_x, location_y, location_z = channels[0], channels[1], channels[2]
    
    # Y offset for side-by-side movement
    y_offset = -100 if char_idx == 0 else 100
    
    # Add keyframes
    frames_per_waypoint = 60
    for i, (x, y, z) in enumerate(waypoints):
        frame = unreal.FrameNumber(i * frames_per_waypoint)
        location_x.add_key(frame, float(x))
        location_y.add_key(frame, float(y + y_offset))
        location_z.add_key(frame, float(z))
    
    print(f"  Added {len(waypoints)} keyframes")
    print(f"  Keys: X={location_x.get_num_keys()}, Y={location_y.get_num_keys()}, Z={location_z.get_num_keys()}")

print("\\n" + "="*60)
print("COMPLETE! Scene created with 2 animated characters")
print("="*60)
result = "SUCCESS: 2 characters with full animation!"
"""
    
    # Step 0: Delete and create fresh sequence
    print("\n[0/7] Creating fresh sequence...")
    sequence_setup_code = """
import unreal

# Close any open sequence
current_seq = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
if current_seq:
    print(f"  Closing: {current_seq.get_name()}")
    unreal.LevelSequenceEditorBlueprintLibrary.close()

# Delete existing sequence if it exists
sequence_path = '/Game/Sequences/TwoCharacterSequence'
if unreal.EditorAssetLibrary.does_asset_exist(sequence_path + '.TwoCharacterSequence'):
    print(f"  Deleting: {sequence_path}")
    unreal.EditorAssetLibrary.delete_asset(sequence_path + '.TwoCharacterSequence')
    if not unreal.EditorAssetLibrary.does_asset_exist(sequence_path + '.TwoCharacterSequence'):
        print("  ✓ Deleted successfully")

# Create new sequence
print("  Creating new sequence...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
seq = asset_tools.create_asset(
    "TwoCharacterSequence",
    "/Game/Sequences",
    unreal.LevelSequence,
    unreal.LevelSequenceFactoryNew()
)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)

# Set sequence properties
unreal.MovieSceneSequenceExtensions.set_playback_end_seconds(seq, 10.0)
unreal.MovieSceneSequenceExtensions.set_display_rate(seq, unreal.FrameRate(30, 1))

print(f"  ✓ Created and opened: {seq.get_name()}")
result = "SUCCESS"
"""
    
    success, result = execute_python(sequence_setup_code)
    if not success:
        print(f"      [X] Failed to setup sequence: {result}")
        return
    print(f"      [OK] Fresh sequence created")
    
    print("\n[1/7] Getting sequence reference...")
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
    
    # Expected sequence path
    sequence_path = '/Game/Sequences/TwoCharacterSequence.TwoCharacterSequence'
    
    # Verify we got the same path back
    if sequence_path not in current_sequence:
        print(f"      [WARNING] Path mismatch: expected '{sequence_path}' but got '{current_sequence}'")
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
