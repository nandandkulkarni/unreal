"""
Add Animation Keyframes REMOTELY via MovieSceneSequenceExtensions API
This should work based on successful AddPossessable test
"""
import requests
import json

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
        result = response.json()
        return True, result
    else:
        return False, response.text

def add_animation_remote():
    """Add animation keyframes to sequence remotely"""
    
    print("=" * 80)
    print("REMOTE ANIMATION ADDITION")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/CharacterWalkSequence"
    
    # Step 1: Open sequence
    print("\n[1/7] Opening sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": {"objectPath": sequence_path}}
    )
    
    if not success:
        print(f"      [X] Failed to open sequence: {result}")
        return
    print("      [OK] Sequence opened")
    
    # Step 2: Get all characters
    print("\n[2/7] Getting characters...")
    success, actors_result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    
    characters = [a for a in actors_result.get('ReturnValue', []) if 'Character' in str(a)]
    print(f"      [OK] Found {len(characters)} characters")
    
    if len(characters) < 2:
        print("      [X] Need at least 2 characters!")
        return
    
    # Step 3-7: Add possessables and animate
    for idx, character_path in enumerate(characters[:2]):
        print(f"\n[3/7] Adding character {idx+1} to sequence...")
        
        # Add possessable
        success, binding_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "AddPossessable",
            {
                "Sequence": sequence_path,
                "ObjectToAdd": character_path
            }
        )
        
        if not success:
            print(f"      [X] Failed to add possessable: {binding_result}")
            continue
            
        print(f"      [OK] Character {idx+1} added to sequence")
        print(f"      Binding: {binding_result}")
        
        # Step 4: Add transform track
        print(f"\n[4/7] Adding transform track to character {idx+1}...")
        
        binding_id = binding_result.get('ReturnValue', {}).get('BindingID')
        
        success, track_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
            "AddTrack",
            {
                "Sequence": sequence_path,
                "TrackType": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"
            }
        )
        
        print(f"      Track result: {track_result}")
    
    print("\n" + "=" * 80)
    print("[5/7] Next: Add sections to tracks")
    print("[6/7] Next: Get channels from sections")
    print("[7/7] Next: Add keyframes to channels")
    print("\nCheck MovieSceneTrackExtensions and MovieSceneSectionExtensions")
    print("=" * 80)

if __name__ == "__main__":
    add_animation_remote()
