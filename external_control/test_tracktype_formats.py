"""
Test different formats for passing TrackType to AddTrack
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

def setup_binding():
    """Get a valid binding"""
    sequence_path = "/Game/Sequences/TestSequence.TestSequence"
    
    # Open and get sequence
    call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "OpenLevelSequence",
        {"LevelSequence": sequence_path}
    )
    
    success, current = call_function(
        "/Script/LevelSequenceEditor.Default__LevelSequenceEditorBlueprintLibrary",
        "GetCurrentLevelSequence"
    )
    current_seq = current.get('ReturnValue', '')
    
    # Get character
    success, result = call_function(
        "/Script/UnrealEd.Default__EditorActorSubsystem",
        "GetAllLevelActors"
    )
    all_actors = result.get('ReturnValue', [])
    character = [a for a in all_actors if 'Character' in str(a)][0]
    
    # AddPossessable
    success, result = call_function(
        "/Script/SequencerScripting.Default__MovieSceneSequenceExtensions",
        "AddPossessable",
        {"Sequence": current_seq, "ObjectToPossess": character}
    )
    return result.get('ReturnValue', {})

def test_addtrack_formats():
    """Test different parameter formats for AddTrack"""
    
    print("=" * 80)
    print("TEST: Different TrackType formats for AddTrack")
    print("=" * 80)
    
    binding = setup_binding()
    binding_id = binding.get('BindingID', {})
    print(f"\n✓ Setup complete - Binding ID: {binding_id}")
    
    # Test 1: Simple string (like SpawnActorFromClass)
    print("\n[Test 1] TrackType as simple string...")
    print("    Format: 'TrackType': '/Script/MovieSceneTracks.MovieScene3DTransformTrack'")
    try:
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "AddTrack",
            {
                "InBinding": binding,
                "TrackType": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"
            }
        )
        print(f"    ✓ Success! Result: {result}")
    except Exception as e:
        print(f"    [X] Failed: {type(e).__name__}")
    
    # Test 2: Wrapped in objectPath dict (current approach)
    print("\n[Test 2] TrackType wrapped in objectPath dict...")
    print("    Format: 'TrackType': {'objectPath': '...'}")
    try:
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "AddTrack",
            {
                "InBinding": binding,
                "TrackType": {"objectPath": "/Script/MovieSceneTracks.MovieScene3DTransformTrack"}
            }
        )
        print(f"    ✓ Success! Result: {result}")
    except Exception as e:
        print(f"    [X] Failed: {type(e).__name__}")
    
    # Test 3: Using Class path format
    print("\n[Test 3] TrackType with Class_ prefix...")
    print("    Format: 'TrackType': '/Script/MovieSceneTracks.Class_MovieScene3DTransformTrack'")
    try:
        success, result = call_function(
            "/Script/SequencerScripting.Default__MovieSceneBindingExtensions",
            "AddTrack",
            {
                "InBinding": binding,
                "TrackType": "/Script/MovieSceneTracks.Class_MovieScene3DTransformTrack"
            }
        )
        print(f"    ✓ Success! Result: {result}")
    except Exception as e:
        print(f"    [X] Failed: {type(e).__name__}")
    
    print("\n" + "=" * 80)
    print("Test complete - check which format worked (if any)")
    print("=" * 80)

if __name__ == "__main__":
    test_addtrack_formats()
