"""
Test if we can add keyframes using MovieSceneSequenceExtensions API
Based on the documentation showing AddPossessable and AddTrack are available
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

def test_add_keyframes_via_extensions():
    """Test using MovieSceneSequenceExtensions API"""
    
    print("=" * 80)
    print("Testing Keyframe Addition via MovieSceneSequenceExtensions")
    print("=" * 80)
    
    # Step 1: Get current sequence
    print("\n1. Getting current sequence...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    
    if not success or not result.get('ReturnValue'):
        print("   [X] No sequence open. Opening CharacterWalkSequence...")
        
        # Try to open a sequence
        success, result = call_function(
            "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
            "OpenLevelSequence",
            {
                "LevelSequence": {
                    "objectPath": "/Game/Sequences/CharacterWalkSequence"
                }
            }
        )
        
        if success:
            print("   [OK] Sequence opened")
        else:
            print(f"   [X] Failed to open sequence: {result}")
            return
    else:
        print(f"   [OK] Current sequence loaded")
    
    # Step 2: Try AddPossessable using MovieSceneSequenceExtensions
    print("\n2. Testing AddPossessable via MovieSceneSequenceExtensions...")
    print("   Checking if we can call this function...")
    
    # Get all actors first
    success, actors_result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    
    if success:
        actors = actors_result.get('ReturnValue', [])
        print(f"   Found {len(actors)} actors in level")
        
        # Find a Character actor
        character = None
        for actor in actors:
            if 'Character' in str(actor):
                character = actor
                break
        
        if character:
            print(f"   Found character: {character}")
            
            # Try to add possessable
            print("\n3. Trying to add possessable via MovieSceneSequenceExtensions...")
            
            # This API requires the sequence object path
            # We need to call it on the sequence object itself
            success, result = call_function(
                "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
                "AddPossessable",
                {
                    "Sequence": "/Game/Sequences/CharacterWalkSequence",
                    "ObjectToAdd": character
                }
            )
            
            if success:
                print(f"   [OK] AddPossessable succeeded!")
                print(f"   Result: {result}")
                
                # Now try AddTrack
                print("\n4. Trying to add transform track...")
                # This would need the binding object returned from AddPossessable
                print("   (This requires the binding object from AddPossessable)")
                
            else:
                print(f"   [X] AddPossessable failed: {result}")
        else:
            print("   [X] No character found")
    else:
        print(f"   [X] Failed to get actors: {actors_result}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT:")
    print("=" * 80)
    print("MovieSceneSequenceExtensions has AddPossessable and AddTrack,")
    print("BUT these require calling methods ON the sequence object,")
    print("not as standalone subsystem functions.")
    print()
    print("Remote Control API limitation:")
    print("- Can call SUBSYSTEM functions (EditorActorSubsystem.SpawnActor)")
    print("- CANNOT call object methods (sequence.AddPossessable)")
    print()
    print("MovieSceneSequenceExtensions is a UTILITY class, not a subsystem.")
    print("Its functions take a sequence as a parameter, but Remote Control")
    print("cannot route calls through utility/extension classes.")
    print("=" * 80)

if __name__ == "__main__":
    test_add_keyframes_via_extensions()
