"""
Test AddTrack to see if it works remotely after successful AddPossessable
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
        return True, response.json()
    else:
        return False, response.text

def test_add_track():
    """Test if AddTrack works with valid binding"""
    
    print("=" * 80)
    print("TEST: AddTrack after successful AddPossessable")
    print("=" * 80)
    
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Step 1: Open sequence and get reference
    print("\n[1] Opening sequence and getting reference...")
    success, result = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = current.get('ReturnValue', '')
    print(f"    ✓ Sequence: {current_seq}")
    
    # Step 2: Get character
    print("\n[2] Getting character...")
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    all_actors = result.get('ReturnValue', [])
    character = [a for a in all_actors if 'Character' in str(a)][0]
    print(f"    ✓ Character: {character}")
    
    # Step 3: AddPossessable
    print("\n[3] Adding possessable (known to work)...")
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {
            "Sequence": current_seq,
            "ObjectToPossess": character
        }
    )
    binding = result.get('ReturnValue', {})
    binding_id = binding.get('BindingID', {})
    print(f"    ✓ Binding ID: {binding_id}")
    
    if all(v == 0 for v in binding_id.values()):
        print("    [X] Binding ID is all zeros - cannot test AddTrack")
        return
    
    # Step 4: Try AddTrack (THIS IS WHERE IT CRASHES)
    print("\n[4] Attempting to add transform track...")
    print("    WARNING: This may crash Unreal...")
    print("    Calling AddTrack...")
    
    try:
        success, track_result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "AddTrack",
            {
                "InBinding": binding,
                "TrackType": {"objectPath": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"}
            }
        )
        
        if success:
            track = track_result.get('ReturnValue', {})
            print(f"    ✓ Track added: {track}")
        else:
            print(f"    [X] AddTrack failed: {track_result}")
            
    except Exception as e:
        print(f"    [X] EXCEPTION: {type(e).__name__}")
        print(f"    [X] Server likely crashed: {e}")
    
    print("\n" + "=" * 80)
    print("If you see this, AddTrack didn't crash!")
    print("Check Unreal Editor to see if it's still running")
    print("=" * 80)

if __name__ == "__main__":
    test_add_track()
